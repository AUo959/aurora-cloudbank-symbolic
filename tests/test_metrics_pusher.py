"""Tests for src/monitoring/metrics_pusher.py

Covers:
- record() adds samples to the rolling window
- Old samples outside the window are evicted
- get_metrics() returns correct avg_latency_ms, p95_latency_ms, error_rate,
  and request_count
- push_to_detector() calls DriftDetector.detect_drift for each metric
- push_to_detector() is a no-op when DriftDetector is unavailable
- Empty window returns empty dict from get_metrics()
- start_background_pusher() starts exactly one daemon thread
- get_pusher() returns a consistent singleton
"""
from __future__ import annotations

import threading
import time
import types
from unittest.mock import MagicMock, patch

import pytest

from src.monitoring.metrics_pusher import MetricsPusher, get_pusher, start_background_pusher


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pusher_with_samples(*status_duration_pairs) -> MetricsPusher:
    """Return a MetricsPusher pre-loaded with (status_code, duration_ms) samples."""
    pusher = MetricsPusher(window_seconds=60)
    for status_code, duration_ms in status_duration_pairs:
        pusher.record(duration_ms=duration_ms, status_code=status_code)
    return pusher


# ---------------------------------------------------------------------------
# Tests: record() and rolling window
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_record_adds_samples():
    """record() should add a sample that get_metrics() can see."""
    pusher = MetricsPusher(window_seconds=60)
    assert pusher.get_metrics() == {}

    pusher.record(duration_ms=100.0, status_code=200)
    metrics = pusher.get_metrics()

    assert metrics["request_count"] == 1.0
    assert metrics["avg_latency_ms"] == pytest.approx(100.0)


@pytest.mark.unit
def test_record_multiple_samples():
    """record() for multiple requests accumulates correctly."""
    pusher = _pusher_with_samples(
        (200, 50.0),
        (200, 150.0),
        (200, 100.0),
    )
    metrics = pusher.get_metrics()

    assert metrics["request_count"] == 3.0
    assert metrics["avg_latency_ms"] == pytest.approx(100.0)


@pytest.mark.unit
def test_old_samples_evicted_from_window():
    """Samples older than window_seconds are evicted on the next record()."""
    pusher = MetricsPusher(window_seconds=1)  # 1-second window for speed

    # Inject an old sample by manipulating the internal deque directly
    old_ts = time.monotonic() - 10  # 10 seconds ago — well outside window
    with pusher._lock:
        pusher._samples.append((old_ts, 999.0, 200))

    # Record a fresh sample; this triggers eviction
    pusher.record(duration_ms=10.0, status_code=200)
    metrics = pusher.get_metrics()

    # Only the fresh sample should survive
    assert metrics["request_count"] == 1.0
    assert metrics["avg_latency_ms"] == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Tests: get_metrics() aggregation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_metrics_empty_window():
    """get_metrics() returns empty dict when no samples exist."""
    pusher = MetricsPusher(window_seconds=60)
    assert pusher.get_metrics() == {}


@pytest.mark.unit
def test_get_metrics_avg_latency():
    """avg_latency_ms is the mean of recorded durations."""
    pusher = _pusher_with_samples(
        (200, 20.0),
        (200, 40.0),
        (200, 60.0),
    )
    metrics = pusher.get_metrics()
    assert metrics["avg_latency_ms"] == pytest.approx(40.0)


@pytest.mark.unit
def test_get_metrics_p95_latency():
    """p95_latency_ms is the 95th-percentile duration in the window."""
    # 20 samples: 19 at 10 ms, 1 at 1000 ms
    samples = [(200, 10.0)] * 19 + [(200, 1000.0)]
    pusher = _pusher_with_samples(*samples)
    metrics = pusher.get_metrics()

    # p95 index = int(20 * 0.95) - 1 = 18 → sorted[18] = 10.0
    # The spike lands at index 19, above the p95 cut
    assert metrics["p95_latency_ms"] == pytest.approx(10.0)


@pytest.mark.unit
def test_get_metrics_error_rate():
    """error_rate counts HTTP 5xx responses divided by total requests."""
    pusher = _pusher_with_samples(
        (200, 10.0),
        (200, 10.0),
        (200, 10.0),
        (500, 10.0),  # one error
    )
    metrics = pusher.get_metrics()
    assert metrics["error_rate"] == pytest.approx(0.25)  # 1/4


@pytest.mark.unit
def test_get_metrics_no_errors():
    """error_rate is 0.0 when all requests succeed."""
    pusher = _pusher_with_samples((200, 10.0), (201, 10.0), (204, 10.0))
    metrics = pusher.get_metrics()
    assert metrics["error_rate"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Tests: push_to_detector()
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_push_to_detector_calls_detect_drift():
    """push_to_detector() calls DriftDetector.detect_drift once per metric
    after the baseline warm-up period (_MIN_BASELINE_SAMPLES pushes) completes."""
    import src.monitoring.metrics_pusher as mp_module

    min_samples = mp_module._MIN_BASELINE_SAMPLES  # typically 20

    pusher = MetricsPusher(window_seconds=60)
    pusher.record(duration_ms=50.0, status_code=200)  # ensure window is non-empty

    mock_detector = MagicMock()
    mock_detector.establish_baseline = MagicMock()
    mock_detector.detect_drift = MagicMock(return_value=None)

    with patch.object(pusher, "_get_detector", return_value=mock_detector):
        # Push min_samples times to build up warm-up values per metric
        for _ in range(min_samples):
            pusher.push_to_detector()

        # One more push should now trigger detect_drift (baseline is established)
        pusher.push_to_detector()

    # detect_drift should have been called at least once (one call per metric)
    assert mock_detector.detect_drift.called
    called_metric_names = {call.kwargs["metric_name"] for call in mock_detector.detect_drift.call_args_list}
    expected_metrics = {"request_count", "avg_latency_ms", "p95_latency_ms", "error_rate"}
    assert called_metric_names == expected_metrics


@pytest.mark.unit
def test_push_to_detector_noop_when_detector_unavailable():
    """push_to_detector() is a no-op when DriftDetector cannot be imported."""
    pusher = MetricsPusher(window_seconds=60)
    pusher.record(duration_ms=10.0, status_code=200)

    with patch.object(pusher, "_get_detector", return_value=None):
        # Should not raise
        pusher.push_to_detector()


@pytest.mark.unit
def test_push_to_detector_noop_when_no_samples():
    """push_to_detector() is a no-op when the window is empty."""
    pusher = MetricsPusher(window_seconds=60)
    mock_detector = MagicMock()

    with patch.object(pusher, "_get_detector", return_value=mock_detector):
        pusher.push_to_detector()

    mock_detector.detect_drift.assert_not_called()
    mock_detector.establish_baseline.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: singleton and background thread
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_pusher_returns_singleton():
    """get_pusher() should return the same instance on repeated calls."""
    p1 = get_pusher()
    p2 = get_pusher()
    assert p1 is p2


@pytest.mark.unit
def test_start_background_pusher_starts_daemon_thread():
    """start_background_pusher() should start exactly one daemon thread."""
    import src.monitoring.metrics_pusher as mp_module

    # Reset background thread state for isolation
    original_thread = mp_module._bg_thread
    mp_module._bg_thread = None

    try:
        start_background_pusher(interval_seconds=60)
        thread = mp_module._bg_thread
        assert thread is not None
        assert thread.is_alive()
        assert thread.daemon is True

        # Calling again should NOT start a second thread
        start_background_pusher(interval_seconds=60)
        assert mp_module._bg_thread is thread  # same object
    finally:
        # Restore original state (the thread is daemon so it will die with the process)
        mp_module._bg_thread = original_thread
