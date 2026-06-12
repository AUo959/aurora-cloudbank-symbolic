"""Deterministic ORD inspection and quarantine policy.

Status: draft_policy_library
Anchor: EOS_SEED_ORION
Ethics: Picard_Delta_3

This module converts normalized inspection findings into quarantine,
sanitization, and escalation decisions without relying on external services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from modules.ord.ord_threshold_registry import ThresholdRegistry, load_default_registry


class QuarantineDecision(Enum):
    INTEGRATE = "integrate"
    SANITIZE = "sanitize"
    QUARANTINE = "quarantine"
    REJECT = "reject"


class SanitizationAction(Enum):
    STRIP_MALICIOUS = "strip_malicious_code"
    REDACT_PII = "redact_pii"
    FIX_STRUCTURE = "fix_malformed_structure"
    APPLY_ETHICS_PATCH = "apply_ethics_patch"
    NORMALIZE_ENCODING = "normalize_encoding"


@dataclass(frozen=True)
class InspectionInput:
    mission_id: str
    structure_valid: bool
    contamination_detected: bool
    contamination_type: Optional[str] = None
    drift_score: float = 0.001
    drift_threshold: Optional[float] = None
    ethics_violations: List[str] = field(default_factory=list)
    pii_detected: bool = False
    encoding_anomaly: bool = False


@dataclass(frozen=True)
class InspectionReport:
    mission_id: str
    decision: QuarantineDecision
    structure_valid: bool
    contamination_detected: bool
    contamination_type: Optional[str]
    drift_score: float
    ethics_compliant: bool
    ethics_violations: List[str]
    requires_sanitization: List[SanitizationAction]
    human_review_required: bool
    reason: str


class OrdInspectionPolicy:
    def __init__(self, threshold_registry: Optional[ThresholdRegistry] = None) -> None:
        self.registry = threshold_registry or load_default_registry()

    def inspect(self, inspection_input: InspectionInput) -> InspectionReport:
        sanitization_needed: List[SanitizationAction] = []
        violations: List[str] = []
        effective_drift_threshold = (
            inspection_input.drift_threshold
            if inspection_input.drift_threshold is not None
            else self.registry.drift_threshold
        )

        if not inspection_input.structure_valid:
            sanitization_needed.append(SanitizationAction.FIX_STRUCTURE)
            violations.append("structure_invalid")

        if inspection_input.contamination_detected:
            sanitization_needed.append(SanitizationAction.STRIP_MALICIOUS)
            violations.append(f"contamination:{inspection_input.contamination_type or 'unknown'}")

        drift_exceeded = inspection_input.drift_score >= effective_drift_threshold
        if drift_exceeded:
            violations.append(
                f"drift_exceeded:{inspection_input.drift_score:.6f}>={effective_drift_threshold:.6f}"
            )

        ethics_compliant = len(inspection_input.ethics_violations) == 0
        if not ethics_compliant:
            sanitization_needed.append(SanitizationAction.APPLY_ETHICS_PATCH)
            violations.extend([f"ethics:{item}" for item in inspection_input.ethics_violations])

        if inspection_input.pii_detected:
            sanitization_needed.append(SanitizationAction.REDACT_PII)
            violations.append("pii_detected")

        if inspection_input.encoding_anomaly:
            sanitization_needed.append(SanitizationAction.NORMALIZE_ENCODING)
            violations.append("encoding_anomaly")

        sanitization_needed = self._stable_unique_actions(sanitization_needed)
        decision, reason, human_review = self._determine_decision(
            contamination=inspection_input.contamination_detected,
            drift_exceeded=drift_exceeded,
            ethics_compliant=ethics_compliant,
            violations=violations,
            sanitization_needed=sanitization_needed,
        )

        return InspectionReport(
            mission_id=inspection_input.mission_id,
            decision=decision,
            structure_valid=inspection_input.structure_valid,
            contamination_detected=inspection_input.contamination_detected,
            contamination_type=inspection_input.contamination_type,
            drift_score=inspection_input.drift_score,
            ethics_compliant=ethics_compliant,
            ethics_violations=list(inspection_input.ethics_violations),
            requires_sanitization=sanitization_needed,
            human_review_required=human_review,
            reason=reason,
        )

    def _determine_decision(
        self,
        contamination: bool,
        drift_exceeded: bool,
        ethics_compliant: bool,
        violations: List[str],
        sanitization_needed: List[SanitizationAction],
    ) -> tuple[QuarantineDecision, str, bool]:
        if contamination and SanitizationAction.STRIP_MALICIOUS not in sanitization_needed:
            return (
                QuarantineDecision.REJECT,
                "Critical contamination detected, cannot sanitize",
                False,
            )

        if len(violations) >= self.registry.quarantine_violation_count or (
            drift_exceeded and not ethics_compliant and self.registry.human_review_drift_plus_ethics
        ):
            return (
                QuarantineDecision.QUARANTINE,
                f"Multiple violations require human review: {', '.join(violations[:3])}",
                True,
            )

        if drift_exceeded:
            return (
                QuarantineDecision.QUARANTINE,
                "Semantic drift exceeds threshold, requires human validation",
                True,
            )

        if sanitization_needed:
            actions = ", ".join(action.value for action in sanitization_needed)
            return (
                QuarantineDecision.SANITIZE,
                f"Sanitization required: {actions}",
                False,
            )

        return (
            QuarantineDecision.INTEGRATE,
            "All validation checks passed",
            False,
        )

    @staticmethod
    def _stable_unique_actions(actions: List[SanitizationAction]) -> List[SanitizationAction]:
        order = {action: idx for idx, action in enumerate(SanitizationAction)}
        deduped = []
        seen = set()
        for action in actions:
            if action not in seen:
                seen.add(action)
                deduped.append(action)
        deduped.sort(key=lambda item: order[item])
        return deduped


__all__ = [
    "InspectionInput",
    "InspectionReport",
    "OrdInspectionPolicy",
    "QuarantineDecision",
    "SanitizationAction",
]
