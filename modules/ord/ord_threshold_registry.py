"""Governance-backed ORD threshold registry.

This module isolates threshold values and escalation rules from the policy
engines so operational posture can be reviewed as configuration rather than
smuggled in as quiet code assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class EscalationRule:
    rule_id: str
    when: str
    action: str
    rationale: str


@dataclass(frozen=True)
class ThresholdRegistry:
    registry_id: str = "ORD_THRESHOLD_REGISTRY"
    version: str = "0.5.0"
    reconnaissance_threshold: float = 0.40
    inspection_threshold: float = 0.40
    secure_transport_threshold: float = 0.40
    drift_threshold: float = 0.005
    quarantine_violation_count: int = 3
    quantum_seal_threshold: float = 0.60
    human_review_drift_plus_ethics: bool = True
    sensitivity_keywords: Dict[str, str] = field(default_factory=lambda: {
        "secret": "RESTRICTED",
        "token": "RESTRICTED",
        "auth": "RESTRICTED",
        "credential": "RESTRICTED",
        "key": "RESTRICTED",
    })
    escalation_rules: List[EscalationRule] = field(default_factory=lambda: [
        EscalationRule(
            rule_id="ER-001",
            when="drift_score >= drift_threshold",
            action="require_human_review",
            rationale="semantic drift can silently break provenance",
        ),
        EscalationRule(
            rule_id="ER-002",
            when="ethics_violation_count > 0 and drift_score >= drift_threshold",
            action="force_quarantine",
            rationale="compound ethics and drift failure should not auto-integrate",
        ),
        EscalationRule(
            rule_id="ER-003",
            when="risk_level >= secure_transport_threshold or restricted sensitivity",
            action="require_secure_transport",
            rationale="sensitive payloads need stable packaging guarantees",
        ),
    ])

    def sensitivity_for_value(self, value: Any) -> Optional[str]:
        for token in self._iter_sensitivity_tokens(value):
            label = self.sensitivity_keywords.get(token)
            if label is not None:
                return label
        return None

    def sensitivity_for_blob(self, parameter_blob: str) -> Optional[str]:
        return self.sensitivity_for_value(parameter_blob)

    @staticmethod
    def _iter_sensitivity_tokens(value: Any) -> List[str]:
        if isinstance(value, dict):
            tokens: List[str] = []
            for key in sorted(value):
                tokens.extend(ThresholdRegistry._split_tokens(str(key)))
                tokens.extend(ThresholdRegistry._iter_sensitivity_tokens(value[key]))
            return tokens
        if isinstance(value, (list, tuple, set)):
            tokens: List[str] = []
            for item in value:
                tokens.extend(ThresholdRegistry._iter_sensitivity_tokens(item))
            return tokens
        return ThresholdRegistry._split_tokens(str(value))

    @staticmethod
    def _split_tokens(text: str) -> List[str]:
        return re.findall(r"[a-z0-9]+", text.lower())


def load_default_registry() -> ThresholdRegistry:
    return ThresholdRegistry()


__all__ = ["EscalationRule", "ThresholdRegistry", "load_default_registry"]
