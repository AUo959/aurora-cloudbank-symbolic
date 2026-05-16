"""Autonomic correction planning for reflective autonomy lint findings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

try:
    from .capsule_linter import CapsuleLinter, CapsuleLintFinding, CapsuleLintResult
except ImportError:  # pragma: no cover - direct script execution fallback
    from capsule_linter import CapsuleLinter, CapsuleLintFinding, CapsuleLintResult


@dataclass(frozen=True)
class CorrectionAction:
    """A non-destructive correction intent."""

    action: str
    target: Optional[str]
    reason: str
    field: Optional[str] = None
    status: str = "planned"

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "action": self.action,
            "target": self.target,
            "field": self.field,
            "reason": self.reason,
            "status": self.status,
        }


@dataclass
class CorrectionReport:
    """Correction-planning receipt for one autonomy check."""

    lint_result: CapsuleLintResult
    actions: List[CorrectionAction] = field(default_factory=list)

    @property
    def approved(self) -> bool:
        return self.lint_result.valid and not self.actions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved": self.approved,
            "lint": self.lint_result.to_dict(),
            "actions": [action.to_dict() for action in self.actions],
        }


class AutonomicCorrectionEngine:
    """Plan corrections from capsule lint findings without silent mutation."""

    def __init__(self, linter: Optional[CapsuleLinter] = None) -> None:
        self.linter = linter or CapsuleLinter()

    def evaluate_capsule(
        self,
        capsule: Mapping[str, Any],
        capsule_id: Optional[str] = None,
    ) -> CorrectionReport:
        lint_result = self.linter.lint_capsule(capsule, capsule_id=capsule_id)
        return self.plan_corrections(lint_result)

    def evaluate_payload_file(self, payload_path: str) -> CorrectionReport:
        lint_result = self.linter.lint_payload_file(self.linter.repo_root / payload_path)
        return self.plan_corrections(lint_result)

    def evaluate_registered_payloads(self) -> CorrectionReport:
        lint_result = self.linter.lint_registered_payloads()
        return self.plan_corrections(lint_result)

    def plan_corrections(self, lint_result: CapsuleLintResult) -> CorrectionReport:
        actions = [self._action_for(finding) for finding in lint_result.findings]
        return CorrectionReport(lint_result=lint_result, actions=actions)

    @staticmethod
    def _action_for(finding: CapsuleLintFinding) -> CorrectionAction:
        action_map = {
            "missing_required_field": "populate_field",
            "invalid_anchor_seed": "restore_governance_value",
            "invalid_ethics_protocol": "restore_governance_value",
            "invalid_threadcore_directives": "repair_directives",
            "symbolic_drift_high": "review_drift",
            "payload_file_missing": "recover_payload_file",
            "payload_file_unreadable": "repair_payload_file",
            "registry_payload_path_missing": "link_registry_payload",
            "registry_entry_invalid": "repair_registry_entry",
            "capsule_unsealed": "seal_capsule",
        }
        return CorrectionAction(
            action=action_map.get(finding.code, "review_finding"),
            target=finding.capsule_id,
            field=finding.field,
            reason=finding.message,
            status="planned",
        )


__all__ = ["AutonomicCorrectionEngine", "CorrectionAction", "CorrectionReport"]
