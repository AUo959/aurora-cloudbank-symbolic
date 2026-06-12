"""
Drift Pre-signature Monitor — correction at Δ0.001 instead of rollback at Δ0.002.

Tracks minor continuity deviations (anchor hash instability, cross-relay
divergence, snapshot drift) that precede major drift events.

v0.3.0: every pre-signature is weighted by Symbol Integration Index depth and
classified rupture / drift / peripheral_noise. Rupture bypasses trend
analysis and escalates CRITICAL immediately (never decimated).

Unit discipline: all deltas here are on the DRIFT_DELTA scale (threshold
0.002) — never the 0.2/0.5/0.8 deviation-fraction scale.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.sensors import constants as C
from src.sensors.core.reading_types import (
    DriftPreSignatureReading,
    Layer,
    PreSignature,
    SensorReading,
    WeightedPreSignature,
)
from src.sensors.core.sensor_base import RollingWindow, Sensor, utcnow

logger = logging.getLogger(__name__)


class DriftPreSignatureMonitor(Sensor):
    """Statistical pre-signature analysis over drift samples and anchor hashes.

    ``drift_detector`` (src.monitoring.drift_detector.DriftDetector) may be
    attached for provenance, but the monitor consumes recorded samples only —
    it never drives detector state (one-way observation).
    """

    budget_key = "drift_presig"

    def __init__(
        self,
        drift_detector: Optional[Any] = None,
        threshold: float = C.DRIFT_THRESHOLD_DELTA,
        sii: Optional[Any] = None,
    ):
        super().__init__("observatory.symbolic.drift_presignature",
                         Layer.L3, "drift_presignature")
        self.drift_detector = drift_detector
        self.threshold = threshold
        self.presig_threshold = threshold * C.DRIFT_PRESIG_RATIO
        self.sii = sii                              # SymbolIntegrationIndex
        self.drift_history = RollingWindow(3600)
        self.anchor_hashes = RollingWindow(3600, maxlen=100)
        self.snapshot_diffs = RollingWindow(3600)
        self.correction_log: List[dict] = []
        self.critical = True                        # rupture path: never decimated

    # -- recording ----------------------------------------------------------------

    def record_drift_sample(self, drift_delta: float, relay_id: str) -> None:
        self.drift_history.append({"delta": drift_delta, "relay_id": relay_id})

    def record_anchor_hash(self, anchor_id: str, hash_value: str) -> None:
        self.anchor_hashes.append({"anchor_id": anchor_id, "hash": hash_value})

    def record_snapshot_diff(self, magnitude: float, location: str = "thread_snapshots") -> None:
        self.snapshot_diffs.append({"magnitude": magnitude, "location": location})

    def record_correction(self, correction_type: str, magnitude: float) -> None:
        self.correction_log.append({
            "type": correction_type,
            "magnitude": magnitude,
            "timestamp": utcnow(),
            "drift_before": self._current_drift_delta(),
        })

    # -- analysis -------------------------------------------------------------------

    def analyze(self) -> DriftPreSignatureReading:
        current = self._current_drift_delta()
        headroom = self.threshold - current
        velocity = self._calculate_velocity()
        time_to_threshold = headroom / velocity if velocity > 0 else None
        trend = self._classify_trend(current, velocity)

        pre_signatures: List[PreSignature] = []
        now = utcnow()

        anchor_stability = self._anchor_hash_stability()
        if anchor_stability < 0.95:
            pre_signatures.append(self._weight(PreSignature(
                signature_id=f"presig_anchor_{now.timestamp()}",
                signature_type="hash_instability",
                magnitude=1.0 - anchor_stability,
                location="anchor_chain",
                first_detected=now,
                predicted_impact="Anchor drift may cause state divergence",
            ), symbol_id=self._dominant_anchor(),
                loss_rate=1.0 - anchor_stability))

        relay_divergence = self._cross_relay_divergence()
        if relay_divergence > 0.001:
            pre_signatures.append(self._weight(PreSignature(
                signature_id=f"presig_relay_{now.timestamp()}",
                signature_type="state_divergence",
                magnitude=relay_divergence,
                location="relay_constellation",
                first_detected=now,
                predicted_impact="Relay desynchronization may compound",
            )))

        snapshot_magnitude = self._snapshot_diff_magnitude()
        if snapshot_magnitude > 0.05:
            pre_signatures.append(self._weight(PreSignature(
                signature_id=f"presig_snapshot_{now.timestamp()}",
                signature_type="snapshot_drift",
                magnitude=snapshot_magnitude,
                location="thread_snapshots",
                first_detected=now,
                predicted_impact="State changes accelerating beyond normal",
            )))

        return DriftPreSignatureReading(
            timestamp=now,
            current_drift_delta=current,
            drift_threshold=self.threshold,
            headroom=headroom,
            drift_velocity=velocity,
            time_to_threshold_hours=time_to_threshold,
            trend=trend,
            pre_signatures=pre_signatures,
            anchor_hash_stability=anchor_stability,
            snapshot_diff_magnitude=snapshot_magnitude,
            cross_relay_divergence=relay_divergence,
            micro_corrections_1h=self._count_recent_corrections(),
            correction_effectiveness=self._correction_effectiveness(),
        )

    def _weight(self, presig: PreSignature, symbol_id: Optional[str] = None,
                loss_rate: float = 0.0) -> PreSignature:
        """v0.3.0 SII weighting; falls back to unweighted when SII not wired."""
        if self.sii is None:
            return presig
        periphery_count = 1 + sum(
            1 for _ in self.drift_history.items()
        ) // 10  # crude correlation proxy until calibration (RQ-3)
        return self.sii.weight_presignature(
            presig, symbol_id=symbol_id,
            connection_loss_rate_per_hour=loss_rate,
            correlated_periphery_count=periphery_count,
        )

    # -- internals -----------------------------------------------------------------------

    def _current_drift_delta(self) -> float:
        items = self.drift_history.items()
        return items[-1]["delta"] if items else 0.0

    def _calculate_velocity(self) -> float:
        """Δ change per hour via first/last sample over the window."""
        items = self.drift_history.items()
        if len(items) < 2:
            return 0.0
        span = (items[-1]["timestamp"] - items[0]["timestamp"]).total_seconds()
        if span <= 0:
            return 0.0
        return (items[-1]["delta"] - items[0]["delta"]) / (span / 3600.0)

    def _classify_trend(self, current: float, velocity: float) -> str:
        if current > self.threshold * 0.8:
            return "critical"
        if velocity > C.DRIFT_VELOCITY_ALERT:
            return "diverging"
        if velocity < C.DRIFT_VELOCITY_CONVERGING:
            return "converging"
        return "stable"

    def _anchor_hash_stability(self) -> float:
        items = self.anchor_hashes.items()
        if len(items) < 2:
            return 1.0
        by_anchor: Dict[str, List[str]] = {}
        for i in items:
            by_anchor.setdefault(i["anchor_id"], []).append(i["hash"])
        stable = sum(1 for hashes in by_anchor.values()
                     if len(set(hashes)) == 1)
        return stable / len(by_anchor)

    def _dominant_anchor(self) -> Optional[str]:
        items = self.anchor_hashes.items()
        if not items:
            return None
        unstable = [i["anchor_id"] for i in items]
        return max(set(unstable), key=unstable.count)

    def _cross_relay_divergence(self) -> float:
        items = self.drift_history.items()
        by_relay: Dict[str, float] = {}
        for i in items:
            by_relay[i["relay_id"]] = i["delta"]
        if len(by_relay) < 2:
            return 0.0
        vals = list(by_relay.values())
        return max(vals) - min(vals)

    def _snapshot_diff_magnitude(self) -> float:
        items = self.snapshot_diffs.items()
        if not items:
            return 0.0
        return sum(i["magnitude"] for i in items) / len(items)

    def _count_recent_corrections(self) -> int:
        cutoff = utcnow().timestamp() - 3600
        return sum(1 for c in self.correction_log
                   if c["timestamp"].timestamp() > cutoff)

    def _correction_effectiveness(self) -> float:
        if not self.correction_log:
            return 1.0
        current = self._current_drift_delta()
        effective = sum(1 for c in self.correction_log
                        if current <= c["drift_before"])
        return effective / len(self.correction_log)

    # -- Sensor interface ---------------------------------------------------------------------

    def ingest(self, source: str, payload: Dict[str, Any]) -> None:
        if "drift_delta" in payload:
            self.record_drift_sample(payload["drift_delta"],
                                     payload.get("relay_id", source))
        if "anchor_hash" in payload:
            self.record_anchor_hash(payload.get("anchor_id", "unknown"),
                                    payload["anchor_hash"])

    def read(self) -> SensorReading:
        r = self.analyze()
        alerts: List[str] = []
        for p in r.pre_signatures:
            if isinstance(p, WeightedPreSignature) and p.classification == "rupture":
                alerts.append(
                    f"RUPTURE {p.signature_type}@{p.location} "
                    f"priority={p.priority:.3f}")
            elif not isinstance(p, WeightedPreSignature) or \
                    p.classification == "drift":
                alerts.append(f"presig {p.signature_type}@{p.location}")
            # peripheral_noise: advisory log only — no alert
        if r.current_drift_delta > self.presig_threshold:
            alerts.append(
                f"drift Δ {r.current_drift_delta:.4f} > presig "
                f"{self.presig_threshold:.4f} [unit: drift_delta]")
        return self._reading(
            {"current_drift_delta": r.current_drift_delta,
             "drift_velocity": r.drift_velocity,
             "headroom": r.headroom,
             "anchor_hash_stability": r.anchor_hash_stability,
             "cross_relay_divergence": r.cross_relay_divergence},
            alerts=alerts,
            metadata={"reading": r},
        )
