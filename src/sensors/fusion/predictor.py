"""
Fusion Predictor — anomaly forecasting via precursor patterns and trajectory
extrapolation. No ML: known patterns + statistical projection.

RQ-2 (v0.3.0): patterns are canon-like artifacts. Live patterns come from the
post-incident pipeline (extract T-minus window -> stage -> backtest precision
>= 0.7 across >= 10 occurrences -> promote). ``stage_pattern`` and
``promote_pattern`` implement that lifecycle; ad-hoc additions to the live
library are not supported by design.

AFS coupling (v0.3.0): forecasts carry ``resolution_criteria`` and
``confidence_interval`` so the AFS harness (PK-04 C5/C6) can Brier-score them.
AFS consumes sensor data; the predictor never consumes AFS forecasts
(no forecast feedback loops — one-way observation).
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, List, Optional

from src.sensors import constants as C
from src.sensors.core.reading_types import AnomalyForecast, PrecursorPattern
from src.sensors.core.sensor_base import RollingWindow, utcnow

logger = logging.getLogger(__name__)


def _pattern_hash(pattern_id: str, signals: List[str]) -> str:
    return hashlib.sha256(
        (pattern_id + "|" + "|".join(sorted(signals))).encode()
    ).hexdigest()[:16]


def default_pattern_library() -> List[PrecursorPattern]:
    """Seed library (spec §Fusion Predictor). Live by definition: these ship
    with the spec and are subject to RQ-2 demotion like any other pattern."""
    seeds = [
        PrecursorPattern(
            pattern_id="drift_velocity_spike", anomaly_type="drift",
            signals=["drift_velocity > 0.0005", "anchor_stability < 0.95"],
            confidence=0.8, typical_eta_seconds=1800),
        PrecursorPattern(
            pattern_id="relay_divergence_cascade", anomaly_type="drift",
            signals=["cross_relay_divergence > 0.001", "divergence_increasing"],
            confidence=0.75, typical_eta_seconds=3600),
        PrecursorPattern(
            pattern_id="ethical_risk_acceleration", anomaly_type="ethics",
            signals=["risk_trend == 'accelerating'", "boundary_testing > 0.5"],
            confidence=0.7, typical_eta_seconds=900),
        PrecursorPattern(
            pattern_id="metaphor_bleed_emerging", anomaly_type="resonance",
            signals=["bleed_risk > 0.3", "l1_l2_resonance_increasing"],
            confidence=0.65, typical_eta_seconds=7200),
        PrecursorPattern(
            pattern_id="containment_stress", anomaly_type="containment",
            signals=["grid_integrity < 0.999", "bleed_events > 0"],
            confidence=0.9, typical_eta_seconds=300),
    ]
    for p in seeds:
        p.pattern_hash = _pattern_hash(p.pattern_id, p.signals)
        p.provenance = {"source": "sensor_array_specification_v3", "seed": "true"}
    return seeds


# Signal predicates are evaluated against a flat current-state dict.
_PREDICATES = {
    "drift_velocity > 0.0005": lambda s: s.get("drift_velocity", 0) > 0.0005,
    "anchor_stability < 0.95": lambda s: s.get("anchor_hash_stability", 1.0) < 0.95,
    "cross_relay_divergence > 0.001": lambda s: s.get("cross_relay_divergence", 0) > 0.001,
    "divergence_increasing": lambda s: s.get("divergence_velocity", 0) > 0,
    "risk_trend == 'accelerating'": lambda s: s.get("risk_trend") == "accelerating",
    "boundary_testing > 0.5": lambda s: s.get("boundary_testing", 0) > 0.5,
    "bleed_risk > 0.3": lambda s: s.get("bleed_risk", 0) > 0.3,
    "l1_l2_resonance_increasing": lambda s: s.get("l1_l2_resonance_velocity", 0) > 0,
    "grid_integrity < 0.999": lambda s: s.get("grid_integrity", 1.0) < 0.999,
    "bleed_events > 0": lambda s: s.get("bleed_events", 0) > 0,
}

_INTERVENTIONS = {
    "drift": "TRIGGER_ANCHOR_RESYNC",
    "ethics": "REQUIRE_HUMAN_APPROVAL",
    "resonance": "QUARANTINE_CONCEPT",
    "containment": "REINFORCE_BOUNDARY",
    "structural": "INITIATE_HEALTH_CHECK",
}


class FusionPredictor:
    """Pattern matching + trajectory extrapolation over the sensor stream."""

    def __init__(self, lookback_seconds: int = 3600,
                 pattern_library: Optional[List[PrecursorPattern]] = None):
        self.lookback = lookback_seconds
        self.history = RollingWindow(lookback_seconds)
        self.pattern_library = (
            pattern_library if pattern_library is not None
            else default_pattern_library()
        )
        self.staged_patterns: List[PrecursorPattern] = []

    # -- RQ-2 lifecycle ---------------------------------------------------------

    def stage_pattern(self, pattern: PrecursorPattern,
                      incident_id: str, author: str) -> PrecursorPattern:
        pattern.status = "staged"
        pattern.pattern_hash = _pattern_hash(pattern.pattern_id, pattern.signals)
        pattern.provenance = {
            "incident_id": incident_id, "author": author,
            "date": utcnow().isoformat(),
        }
        self.staged_patterns.append(pattern)
        return pattern

    def promote_pattern(self, pattern_id: str, backtest_precision: float,
                        occurrences: int) -> PrecursorPattern:
        """Promote a staged pattern carrying its backtest evidence."""
        pattern = next(p for p in self.staged_patterns
                       if p.pattern_id == pattern_id)
        if backtest_precision < C.PATTERN_PROMOTE_PRECISION:
            raise ValueError(
                f"precision {backtest_precision:.2f} < "
                f"{C.PATTERN_PROMOTE_PRECISION} — promotion denied")
        pattern.backtest_precision = backtest_precision
        pattern.low_n = occurrences < C.PATTERN_PROMOTE_MIN_N
        pattern.status = "live"
        self.staged_patterns.remove(pattern)
        self.pattern_library.append(pattern)
        return pattern

    def demote_pattern(self, pattern_id: str, reason: str = "fp_rate") -> None:
        """Auto-demotion path: rolling FP rate > 30% over 30 days."""
        pattern = next(p for p in self.pattern_library
                       if p.pattern_id == pattern_id)
        pattern.status = "staged"
        self.pattern_library.remove(pattern)
        self.staged_patterns.append(pattern)
        logger.warning("Pattern %s demoted to staged (%s)", pattern_id, reason)

    # -- forecasting ----------------------------------------------------------------

    def ingest(self, state: Dict[str, Any]) -> None:
        self.history.append({"state": dict(state)})

    def _current_state(self) -> Dict[str, Any]:
        items = self.history.items()
        return items[-1]["state"] if items else {}

    def forecast(self, horizon_seconds: int = 3600) -> List[AnomalyForecast]:
        forecasts: List[AnomalyForecast] = []
        state = self._current_state()
        now = utcnow()

        for pattern in self.pattern_library:
            if pattern.status != "live":
                continue
            matched = [s for s in pattern.signals
                       if _PREDICATES.get(s, lambda _: False)(state)]
            if len(matched) != len(pattern.signals):
                continue
            strength = len(matched) / max(len(pattern.signals), 1)
            prob = pattern.confidence * strength
            forecasts.append(AnomalyForecast(
                forecast_id=f"forecast_{pattern.pattern_id}_{now.timestamp()}",
                timestamp=now,
                anomaly_type=pattern.anomaly_type,
                probability=prob,
                predicted_eta_seconds=pattern.typical_eta_seconds,
                confidence=pattern.confidence,
                contributing_signals=pattern.signals,
                pattern_matched=pattern.pattern_id,
                trajectory=self._assess_trajectory(pattern.anomaly_type),
                recommended_intervention=_INTERVENTIONS.get(
                    pattern.anomaly_type, "LOG_AND_MONITOR"),
                intervention_urgency=self._assess_urgency(pattern),
                resolution_criteria=(
                    f"{pattern.anomaly_type} anomaly reaches threshold within "
                    f"{int(pattern.typical_eta_seconds * 2)}s of forecast"),
                confidence_interval=(max(prob - 0.15, 0.0), min(prob + 0.15, 1.0)),
            ))

        drift_forecast = self._extrapolate_drift(horizon_seconds)
        if drift_forecast:
            forecasts.append(drift_forecast)
        return sorted(forecasts, key=lambda f: f.probability, reverse=True)

    def _extrapolate_drift(self, horizon: int) -> Optional[AnomalyForecast]:
        state = self._current_state()
        velocity = state.get("drift_velocity", 0.0)      # Δ/hour
        current = state.get("current_drift_delta", 0.0)
        threshold = state.get("drift_threshold", C.DRIFT_THRESHOLD_DELTA)
        if velocity <= 0:
            return None
        eta_hours = (threshold - current) / velocity
        if eta_hours * 3600 > horizon:
            return None
        now = utcnow()
        prob = min(0.95, 0.5 + (1.0 - eta_hours * 3600 / horizon) * 0.45)
        return AnomalyForecast(
            forecast_id=f"forecast_drift_extrapolation_{now.timestamp()}",
            timestamp=now,
            anomaly_type="drift",
            probability=prob,
            predicted_eta_seconds=eta_hours * 3600,
            confidence=0.6,
            contributing_signals=["drift_velocity", "current_drift_delta"],
            pattern_matched=None,
            trajectory="linear",
            recommended_intervention="TRIGGER_ANCHOR_RESYNC",
            intervention_urgency=(
                "immediate" if eta_hours * 3600 < 600
                else "soon" if eta_hours * 3600 < 3600 else "monitor"),
            resolution_criteria=(
                f"drift Δ reaches {threshold} within "
                f"{int(eta_hours * 7200)}s [unit: drift_delta]"),
            confidence_interval=(max(prob - 0.2, 0.0), min(prob + 0.2, 1.0)),
        )

    def _assess_trajectory(self, anomaly_type: str) -> str:
        items = self.history.items()
        if len(items) < 3:
            return "linear"
        key = {"drift": "drift_velocity", "ethics": "risk_score",
               "resonance": "bleed_risk"}.get(anomaly_type)
        if not key:
            return "linear"
        vals = [i["state"].get(key, 0.0) for i in items[-3:]]
        if vals[2] - vals[1] > vals[1] - vals[0]:
            return "accelerating"
        if vals[2] - vals[1] < vals[1] - vals[0]:
            return "decelerating"
        return "linear"

    def _assess_urgency(self, pattern: PrecursorPattern) -> str:
        if pattern.typical_eta_seconds < 600:
            return "immediate"
        if pattern.typical_eta_seconds < 3600:
            return "soon"
        return "monitor"
