"""
Ethical Signal Sentinel — pre-violation ethics monitoring.

Detects escalating patterns (tone escalation, boundary testing, deviation
accumulation) BEFORE explicit Picard_Delta_3 rules break, enabling proactive
intervention while risk is low.

Repo-reality integration (reconciler 2026-06-11): binds to
``src.monitoring.ethics_engine.EthicsEngine`` (``evaluate_action(ActionContext)
-> List[EthicsViolation]``, severities LOW/MEDIUM/HIGH/CRITICAL). The
BLOCK/REVIEW/THROTTLE/SUSPEND/RESET action vocabulary belongs to
``MonitoringSystem`` — the sentinel only RECOMMENDS; MonitoringSystem and L3
governance own actions (one-way observation, RQ-4).

RQ-4 sentinel-risk mapping: <0.4 log; 0.4-0.7 alert/REVIEW queue; >0.7 or
accelerating => CRITICAL path with REQUIRE_HUMAN_APPROVAL recommendation.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Dict, List, Optional

from src.sensors import constants as C
from src.sensors.core.reading_types import (
    EthicalSignalReading,
    EthicalWarning,
    Layer,
    SensorReading,
)
from src.sensors.core.sensor_base import Sensor, utcnow

logger = logging.getLogger(__name__)

# Severity weights for near-boundary scoring (LOW/MEDIUM are near-boundary
# evidence; HIGH/CRITICAL are actual violations handled by the engine itself).
_SEVERITY_WEIGHT = {"low": 0.25, "medium": 0.5, "high": 0.85, "critical": 1.0}


@dataclass
class Action:
    """Action view consumed by the sentinel (mirrors spec; engine-agnostic)."""
    action_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    allowed: bool = True
    intensity: float = 0.0          # optional, feeds tone escalation


class EthicalSignalSentinel(Sensor):
    """Rule-based pre-violation pattern detection. No ML required."""

    budget_key = "ethical_signal"

    def __init__(self, ethics_engine: Optional[Any] = None):
        super().__init__("observatory.symbolic.ethical_signal",
                         Layer.L3, "ethical_signal")
        self.ethics_engine = ethics_engine    # src.monitoring.EthicsEngine
        self.action_history: Dict[str, List[dict]] = defaultdict(list)
        self.risk_scores: Dict[str, float] = defaultdict(float)
        self.critical = True                  # never decimated

    # -- evaluation -------------------------------------------------------------

    def evaluate_action(self, entity_id: str, action: Action) -> EthicalSignalReading:
        """Evaluate an action for pre-violation signals. Observation only:
        the engine's verdict (if any) is recorded, never altered."""
        violations = self._engine_violations(entity_id, action)
        now = utcnow()

        self.action_history[entity_id].append({
            "action": action,
            "violations": violations,
            "blocked": any(v.get("blocked") for v in violations),
            "max_severity": max(
                (_SEVERITY_WEIGHT.get(v.get("severity", "low"), 0.25)
                 for v in violations), default=0.0),
            "timestamp": now,
        })
        cutoff = now - timedelta(hours=1)
        self.action_history[entity_id] = [
            a for a in self.action_history[entity_id] if a["timestamp"] > cutoff
        ]
        history = self.action_history[entity_id]

        tone = self._detect_tone_escalation(history)
        boundary = self._detect_boundary_testing(history)
        accumulation = self._detect_accumulation(history)

        w = C.SENTINEL_WEIGHTS
        risk = tone * w["tone"] + boundary * w["boundary"] + \
            accumulation * w["accumulation"]

        prev = self.risk_scores[entity_id]
        self.risk_scores[entity_id] = risk
        velocity = risk - prev
        if velocity > C.SENTINEL_ACCEL_VELOCITY:
            trend = "accelerating"
        elif velocity > C.SENTINEL_INCREASING_VELOCITY:
            trend = "increasing"
        elif velocity < -C.SENTINEL_INCREASING_VELOCITY:
            trend = "decreasing"
        else:
            trend = "stable"

        warnings = self._generate_warnings(
            entity_id, tone, boundary, accumulation, trend)

        return EthicalSignalReading(
            timestamp=now,
            observation_window_seconds=C.DEFAULT_OBSERVATION_WINDOW_SECONDS,
            entity_id=entity_id,
            risk_score=risk,
            risk_trend=trend,
            risk_velocity=velocity,
            tone_escalation=tone,
            boundary_testing=boundary,
            rule_deviation_accumulation=accumulation,
            warnings=warnings,
            intervention_recommended=(
                risk > C.SENTINEL_RISK_INTERVENTION or trend == "accelerating"),
            recommended_action=self._recommend_action(risk, trend),
        )

    def _engine_violations(self, entity_id: str, action: Action) -> List[dict]:
        """Standard ethics check via the existing EthicsEngine, if wired."""
        if self.ethics_engine is None:
            return []
        try:
            from src.monitoring.ethics_engine import ActionContext
            results = self.ethics_engine.evaluate_action(ActionContext(
                agent_id=entity_id,
                action_type=action.action_type,
                parameters=action.params,
            ))
            return [
                {"severity": v.severity.value, "blocked": v.blocked,
                 "rule_id": v.rule_id}
                for v in results
            ]
        except Exception:  # noqa: BLE001 — sentinel must never break the path
            logger.exception("EthicsEngine evaluation failed (observed only)")
            return []

    # -- signal components ----------------------------------------------------------

    def _detect_tone_escalation(self, history: List[dict]) -> float:
        """Rising action intensity across the window."""
        if len(history) < 2:
            return 0.0
        intensities = [h["action"].intensity for h in history]
        first, second = intensities[: len(intensities) // 2], \
            intensities[len(intensities) // 2:]
        if not first or not second:
            return 0.0
        delta = (sum(second) / len(second)) - (sum(first) / len(first))
        return max(0.0, min(delta, 1.0))

    def _detect_boundary_testing(self, history: List[dict]) -> float:
        """Frequency of near-boundary actions (LOW/MEDIUM severity hits,
        i.e. margin < SENTINEL_NEAR_BOUNDARY_MARGIN of a violation)."""
        if not history:
            return 0.0
        near = sum(
            1 for h in history
            if 0.0 < h["max_severity"] < 1.0 - C.SENTINEL_NEAR_BOUNDARY_MARGIN
            or (h["violations"] and not h["blocked"])
        )
        return min(near / len(history), 1.0)

    def _detect_accumulation(self, history: List[dict]) -> float:
        """Minor deviations accumulating; 10 soft hits normalizes to 1.0."""
        if not history:
            return 0.0
        minor = sum(1 for h in history if h["violations"] and not h["blocked"])
        return min(minor / 10, 1.0)

    # -- outputs ------------------------------------------------------------------------

    def _generate_warnings(self, entity_id, tone, boundary, accumulation,
                           trend) -> List[EthicalWarning]:
        out: List[EthicalWarning] = []
        now = utcnow().timestamp()

        def warn(wtype, severity, desc, evidence, response):
            out.append(EthicalWarning(
                warning_id=f"ethw_{wtype}_{entity_id}_{now}",
                warning_type=wtype, severity=severity, description=desc,
                evidence=evidence, suggested_response=response))

        if tone > 0.5:
            warn("tone", "caution", "Action intensity escalating",
                 [f"tone_escalation={tone:.2f}"], "INCREASE_AUDIT_FREQUENCY")
        if boundary > 0.5:
            warn("boundary", "warning", "Repeated near-boundary actions",
                 [f"boundary_testing={boundary:.2f}"], "INCREASE_AUDIT_FREQUENCY")
        if accumulation > 0.5:
            warn("accumulation", "warning", "Minor deviations accumulating",
                 [f"accumulation={accumulation:.2f}"], "LOG_AND_MONITOR")
        if trend == "accelerating":
            warn("pattern", "critical", "Risk accelerating",
                 [f"trend={trend}"], "REQUIRE_HUMAN_APPROVAL")
        return out

    def _recommend_action(self, risk: float, trend: str) -> Optional[str]:
        """Recommendation only (RQ-4): >0.8 or accelerating is a Picard_Delta_3
        boundary case — never automated. 0.4-0.7 maps to WARNING/REVIEW queue."""
        if risk > C.SENTINEL_RISK_HUMAN_APPROVAL or trend == "accelerating":
            return "REQUIRE_HUMAN_APPROVAL"
        if risk > C.SENTINEL_RISK_AUDIT:
            return "INCREASE_AUDIT_FREQUENCY"
        if risk > C.SENTINEL_RISK_MONITOR:
            return "LOG_AND_MONITOR"
        return None

    # -- Sensor interface ----------------------------------------------------------------

    def ingest(self, source: str, payload: Dict[str, Any]) -> None:
        self.evaluate_action(
            payload.get("entity_id", payload.get("faction_id", "unknown")),
            Action(
                action_type=payload.get("action_type", source),
                params=payload.get("params", {}),
                allowed=payload.get("allowed", True),
                intensity=payload.get("intensity", 0.0),
            ),
        )

    def read(self) -> SensorReading:
        risks = dict(self.risk_scores)
        worst = max(risks.values(), default=0.0)
        alerts = [
            f"sentinel risk {r:.2f} for {e}"
            for e, r in risks.items() if r > C.SENTINEL_RISK_INTERVENTION
        ]
        return self._reading(
            {"max_risk_score": worst,
             "entities_monitored": float(len(risks))},
            alerts=alerts,
            metadata={"risk_scores": risks},
        )
