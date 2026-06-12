"""
Oscillation Health Monitor — is the correction system itself pathological?

Detects hunting (high alternation), limit cycles, and divergence (corrections
amplifying drift).

v0.3.0 Convergence Regulator coupling: the regulator emits
intentional-perturbation markers (tick, target, magnitude) on the data bus
topic ``regulator.intentional_perturbation``. Marker-matched corrections are
EXCLUDED from alternation/hunting calculations, and ``regulator_share``
reports the regulator-intentional fraction of observed variation —
``regulator_share > 0.8`` with rising drift is itself an advisory (the
regulator may be masking genuine instability).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.sensors import constants as C
from src.sensors.core.data_bus import TOPIC_REGULATOR_MARKER, SensorDataBus
from src.sensors.core.reading_types import OscillationHealthReading
from src.sensors.core.sensor_base import RollingWindow, utcnow

logger = logging.getLogger(__name__)


class RegulatorMarkerConsumer:
    """Consumes Convergence Regulator intentional-perturbation markers.

    Marker schema (open question #2 — provisional until agreed with the
    GUMAS engine owner): {"tick": int, "target": str, "magnitude": float}.
    """

    def __init__(self, bus: Optional[SensorDataBus] = None):
        self.markers = RollingWindow(C.DEFAULT_OBSERVATION_WINDOW_SECONDS)
        if bus is not None:
            bus.subscribe(TOPIC_REGULATOR_MARKER, self._on_marker)

    def _on_marker(self, topic: str, payload: Dict[str, Any]) -> None:
        self.markers.append(dict(payload))

    def matches(self, correction: Dict[str, Any]) -> bool:
        """A correction matches a marker when targets coincide and magnitudes
        agree within 25% inside the same window."""
        for m in self.markers.items():
            if m.get("target") and m["target"] != correction.get("target"):
                continue
            mag = m.get("magnitude", 0.0)
            if mag and abs(correction["magnitude"] - mag) <= 0.25 * mag:
                return True
        return False


class OscillationHealthMonitor:
    """Monitor correction patterns for pathological oscillation."""

    def __init__(self, marker_consumer: Optional[RegulatorMarkerConsumer] = None):
        self.corrections = RollingWindow(C.DEFAULT_OBSERVATION_WINDOW_SECONDS)
        self.marker_consumer = marker_consumer

    def record_correction(
        self,
        correction_type: str,
        direction: str,                    # "positive" | "negative"
        magnitude: float,
        drift_before: float,
        drift_after: float,
        target: Optional[str] = None,
    ) -> None:
        self.corrections.append({
            "type": correction_type,
            "direction": direction,
            "magnitude": magnitude,
            "drift_before": drift_before,
            "drift_after": drift_after,
            "effective": drift_after < drift_before,
            "target": target,
        })

    def analyze(self) -> OscillationHealthReading:
        all_corrections = self.corrections.items()
        if len(all_corrections) < 2:
            return self._healthy_baseline()

        # v0.3.0: exclude regulator-intentional perturbations from
        # alternation/hunting math; report their share.
        if self.marker_consumer is not None:
            intentional = [c for c in all_corrections
                           if self.marker_consumer.matches(c)]
            organic = [c for c in all_corrections
                       if not self.marker_consumer.matches(c)]
        else:
            intentional, organic = [], all_corrections
        regulator_share = len(intentional) / len(all_corrections)

        if len(organic) < 2:
            # All variation is regulator-intentional (or nearly): there is no
            # organic correction signal to diagnose. Hunting/limit-cycle math
            # on intentional perturbations would be a false alarm by
            # construction (success criterion 12).
            baseline = self._healthy_baseline()
            baseline.regulator_share = regulator_share
            baseline.diagnosis = (
                "No organic correction signal; "
                f"regulator_share={regulator_share:.2f}")
            return baseline

        corrections = organic

        hours = (corrections[-1]["timestamp"] -
                 corrections[0]["timestamp"]).total_seconds() / 3600
        freq = len(corrections) / max(hours, 0.1)

        magnitudes = [c["magnitude"] for c in corrections]
        magnitude_trend = self._assess_trend(magnitudes)

        directions = [c["direction"] for c in corrections]
        alternation = self._alternation_rate(directions)
        streak = self._same_direction_streak(directions)

        effective = sum(1 for c in corrections if c["effective"])
        success = effective / len(corrections)
        avg_after = sum(c["drift_after"] for c in corrections) / len(corrections)

        healthy, risk, diagnosis = self._diagnose(
            freq, magnitude_trend, alternation, success)

        # Regulator-masking advisory
        if regulator_share > 0.8 and avg_after > 0:
            drift_rising = (all_corrections[-1]["drift_after"] >
                            all_corrections[0]["drift_after"])
            if drift_rising:
                diagnosis += (" | ADVISORY: regulator_share "
                              f"{regulator_share:.2f} with rising drift — "
                              "regulator may be masking genuine instability")
                risk = "medium" if risk in ("none", "low") else risk
                healthy = False

        return OscillationHealthReading(
            timestamp=utcnow(),
            observation_window_seconds=C.DEFAULT_OBSERVATION_WINDOW_SECONDS,
            corrections_per_hour=freq,
            correction_frequency_trend=self._freq_trend(corrections),
            avg_correction_magnitude=sum(magnitudes) / len(magnitudes),
            magnitude_trend=magnitude_trend,
            same_direction_streak=streak,
            direction_alternation_rate=alternation,
            drift_after_correction=avg_after,
            correction_success_rate=success,
            oscillation_healthy=healthy,
            oscillation_risk=risk,
            diagnosis=diagnosis,
            regulator_share=regulator_share,
        )

    # -- diagnostics ----------------------------------------------------------------

    def _diagnose(self, freq: float, mag_trend: str, alt_rate: float,
                  success: float) -> Tuple[bool, str, str]:
        if freq < C.OSC_HEALTHY_FREQ and mag_trend == "shrinking" \
                and success > C.OSC_HEALTHY_SUCCESS:
            return True, "none", "System converging normally"
        if alt_rate > C.OSC_ALTERNATION_ALERT and mag_trend == "stable":
            return False, "high", "Hunting behavior: system fighting itself"
        if freq > C.OSC_MAX_CORRECTIONS_PER_HOUR and mag_trend == "stable" \
                and alt_rate > 0.5:
            return False, "medium", "Limit cycle: locked in oscillation pattern"
        if mag_trend == "growing":
            return False, "high", "Diverging: corrections amplifying drift"
        if success < 0.5:
            return False, "medium", "Low effectiveness: corrections not reducing drift"
        return True, "low", "Minor oscillation within acceptable bounds"

    def _healthy_baseline(self) -> OscillationHealthReading:
        return OscillationHealthReading(
            timestamp=utcnow(),
            observation_window_seconds=C.DEFAULT_OBSERVATION_WINDOW_SECONDS,
            corrections_per_hour=0.0,
            correction_frequency_trend="stable",
            avg_correction_magnitude=0.0,
            magnitude_trend="stable",
            same_direction_streak=0,
            direction_alternation_rate=0.0,
            drift_after_correction=0.0,
            correction_success_rate=1.0,
            oscillation_healthy=True,
            oscillation_risk="none",
            diagnosis="Insufficient corrections to assess; baseline healthy",
            regulator_share=0.0,
        )

    @staticmethod
    def _assess_trend(values: List[float]) -> str:
        if len(values) < 2:
            return "stable"
        half = len(values) // 2
        first = sum(values[:half]) / max(half, 1)
        second = sum(values[half:]) / max(len(values) - half, 1)
        if second < first * 0.8:
            return "shrinking"
        if second > first * 1.2:
            return "growing"
        return "stable"

    @staticmethod
    def _alternation_rate(directions: List[str]) -> float:
        if len(directions) < 2:
            return 0.0
        flips = sum(1 for a, b in zip(directions, directions[1:], strict=False)
                    if a != b)
        return flips / (len(directions) - 1)

    @staticmethod
    def _same_direction_streak(directions: List[str]) -> int:
        streak = best = 1
        for a, b in zip(directions, directions[1:], strict=False):
            streak = streak + 1 if a == b else 1
            best = max(best, streak)
        return best if directions else 0

    def _freq_trend(self, corrections: List[dict]) -> str:
        if len(corrections) < 4:
            return "stable"
        mid = corrections[len(corrections) // 2]["timestamp"]
        first = sum(1 for c in corrections if c["timestamp"] <= mid)
        second = len(corrections) - first
        if second > first * 1.5:
            return "increasing"
        if second < first * 0.67:
            return "decreasing"
        return "stable"
