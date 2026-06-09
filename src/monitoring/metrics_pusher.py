"""Pushes live request metrics to DriftDetector for behavioral drift detection.

Collects per-request observations from the MetricsMiddleware and periodically
pushes aggregated window statistics (avg latency, p95 latency, error rate,
request count) into the DriftDetector via its ``detect_drift`` method.

Baseline bootstrapping: the first ``_MIN_BASELINE_SAMPLES`` observations are
used to establish an initial baseline so the detector has reference data before
it starts emitting drift alerts.
"""
from __future__ import annotations

import collections
import logging
import threading
import time
from typing import Deque, Dict, Optional

logger = logging.getLogger(__name__)

_WINDOW_SECONDS = 60  # rolling aggregation window
_MIN_BASELINE_SAMPLES = 20  # samples required before handing off to detector
_AGENT_ID = "aurora-api"  # logical agent identifier used in drift keys


class MetricsPusher:
    """Collects per-request stats and pushes aggregated metrics to DriftDetector.

    Thread-safe. Designed to be called from FastAPI middleware on every request.

    Usage::

        pusher = get_pusher()
        pusher.record(duration_ms=42.3, status_code=200)

    A background daemon thread calls :meth:`push_to_detector` on a regular
    interval via :func:`start_background_pusher`.
    """

    def __init__(self, window_seconds: int = _WINDOW_SECONDS) -> None:
        self._window = window_seconds
        self._lock = threading.Lock()
        # Each entry: (monotonic_timestamp, duration_ms, status_code)
        self._samples: Deque[tuple] = collections.deque()
        # Warm-up buffer: accumulate until we have enough for a baseline
        self._warmup: list[tuple[str, float]] = []  # (metric_name, value)
        self._detector = None
        self._baseline_established: set[str] = set()

    # ------------------------------------------------------------------
    # Internal: DriftDetector access
    # ------------------------------------------------------------------

    def _get_detector(self):
        """Lazy-init DriftDetector; returns None when unavailable."""
        if self._detector is None:
            try:
                from src.monitoring.drift_detector import DriftDetector
                self._detector = DriftDetector()
                logger.info("DriftDetector initialised for MetricsPusher")
            except Exception as exc:
                logger.warning("DriftDetector unavailable: %s", exc)
        return self._detector

    # ------------------------------------------------------------------
    # Public: observation recording
    # ------------------------------------------------------------------

    def record(self, duration_ms: float, status_code: int) -> None:
        """Record a single request observation (called from middleware).

        Args:
            duration_ms: End-to-end request duration in milliseconds.
            status_code: HTTP response status code.
        """
        now = time.monotonic()
        with self._lock:
            self._samples.append((now, duration_ms, status_code))
            # Evict samples outside the rolling window
            cutoff = now - self._window
            while self._samples and self._samples[0][0] < cutoff:
                self._samples.popleft()

    # ------------------------------------------------------------------
    # Public: aggregation
    # ------------------------------------------------------------------

    def get_metrics(self) -> Dict[str, float]:
        """Return aggregated metrics for the current rolling window.

        Returns an empty dict when no samples are present.

        Keys:
            ``request_count``, ``avg_latency_ms``, ``p95_latency_ms``,
            ``error_rate``
        """
        with self._lock:
            if not self._samples:
                return {}
            now = time.monotonic()
            cutoff = now - self._window
            recent = [(d, s) for ts, d, s in self._samples if ts >= cutoff]

        if not recent:
            return {}

        durations = [d for d, _ in recent]
        error_count = sum(1 for _, s in recent if s >= 500)
        sorted_durations = sorted(durations)
        p95_idx = max(0, int(len(sorted_durations) * 0.95) - 1)

        return {
            "request_count": float(len(recent)),
            "avg_latency_ms": sum(durations) / len(durations),
            "p95_latency_ms": sorted_durations[p95_idx],
            "error_rate": error_count / len(recent),
        }

    # ------------------------------------------------------------------
    # Public: push to detector
    # ------------------------------------------------------------------

    def push_to_detector(self) -> None:
        """Push current aggregated metrics to DriftDetector.

        On the first ``_MIN_BASELINE_SAMPLES`` pushes the values are used to
        establish the detector baseline; subsequent pushes call
        ``detect_drift`` for each metric so the detector can issue alerts.
        """
        detector = self._get_detector()
        if detector is None:
            return

        metrics = self.get_metrics()
        if not metrics:
            logger.debug("MetricsPusher: no samples yet, skipping push")
            return

        for metric_name, value in metrics.items():
            key = f"{_AGENT_ID}:{metric_name}"
            if key not in self._baseline_established:
                # Accumulate warm-up values for this metric
                self._warmup.append((metric_name, value))
                warmup_values = [v for n, v in self._warmup if n == metric_name]
                if len(warmup_values) >= _MIN_BASELINE_SAMPLES:
                    try:
                        detector.establish_baseline(
                            agent_id=_AGENT_ID,
                            metric_name=metric_name,
                            values=warmup_values,
                        )
                        self._baseline_established.add(key)
                        logger.info(
                            "Baseline established for %s:%s from %d samples",
                            _AGENT_ID, metric_name, len(warmup_values),
                        )
                    except Exception as exc:
                        logger.warning(
                            "Failed to establish baseline for %s:%s: %s",
                            _AGENT_ID, metric_name, exc,
                        )
            else:
                try:
                    alert = detector.detect_drift(
                        agent_id=_AGENT_ID,
                        metric_name=metric_name,
                        current_value=value,
                        context_tag=f"metrics_pusher_{metric_name}_{int(time.time())}",
                    )
                    if alert:
                        logger.warning(
                            "Drift alert [%s] %s=%s (baseline=%.3f)",
                            alert.level.value, metric_name, value, alert.baseline_value,
                        )
                except Exception as exc:
                    logger.warning(
                        "Failed to push metric %s to DriftDetector: %s",
                        metric_name, exc,
                    )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_pusher: Optional[MetricsPusher] = None
_pusher_lock = threading.Lock()


def get_pusher() -> MetricsPusher:
    """Return the process-wide MetricsPusher singleton."""
    global _pusher
    if _pusher is None:
        with _pusher_lock:
            if _pusher is None:
                _pusher = MetricsPusher()
    return _pusher


# ---------------------------------------------------------------------------
# Background flush thread
# ---------------------------------------------------------------------------

_bg_thread: Optional[threading.Thread] = None
_bg_lock = threading.Lock()


def start_background_pusher(interval_seconds: int = 30) -> None:
    """Start a daemon thread that calls ``push_to_detector`` every *interval_seconds*.

    Safe to call multiple times; only one background thread is ever started.

    Args:
        interval_seconds: How often (in seconds) to push aggregated metrics.
    """
    global _bg_thread

    with _bg_lock:
        if _bg_thread is not None and _bg_thread.is_alive():
            logger.debug("Background metrics pusher already running")
            return

        def _loop() -> None:
            logger.info(
                "Background metrics pusher started (interval=%ds)", interval_seconds
            )
            while True:
                time.sleep(interval_seconds)
                try:
                    get_pusher().push_to_detector()
                except Exception as exc:  # pragma: no cover - safety net
                    logger.error("Background metrics pusher error: %s", exc)

        _bg_thread = threading.Thread(
            target=_loop,
            name="metrics-pusher-bg",
            daemon=True,
        )
        _bg_thread.start()
        logger.info("Background metrics pusher thread started")
