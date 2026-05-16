"""Reflective autonomy loop receipt generation."""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

try:
    from .autonomic_correction_engine import AutonomicCorrectionEngine, CorrectionAction
    from .capsule_linter import CapsuleLinter, CapsuleLintResult
except ImportError:  # pragma: no cover - direct script execution fallback
    from autonomic_correction_engine import AutonomicCorrectionEngine, CorrectionAction
    from capsule_linter import CapsuleLinter, CapsuleLintResult


@dataclass
class AutonomyCycleReceipt:
    """Machine-readable result of one reflective autonomy cycle."""

    timestamp: str
    status: str
    checked_capsules: int
    findings: List[Dict[str, Optional[str]]] = field(default_factory=list)
    corrections: List[Dict[str, Optional[str]]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "status": self.status,
            "checked_capsules": self.checked_capsules,
            "findings": self.findings,
            "corrections": self.corrections,
        }


class ReflectiveAutonomyLoop:
    """Run deterministic lint and correction-planning cycles."""

    def __init__(
        self,
        linter: Optional[CapsuleLinter] = None,
        correction_engine: Optional[AutonomicCorrectionEngine] = None,
        audit_log_path: Optional[Path] = None,
    ) -> None:
        self.linter = linter or CapsuleLinter()
        self.correction_engine = correction_engine or AutonomicCorrectionEngine(self.linter)
        self.audit_log_path = Path(audit_log_path) if audit_log_path else None

    def run_cycle(
        self,
        capsules: Optional[Iterable[Mapping[str, Any]]] = None,
        payload_files: Optional[Iterable[Path]] = None,
        registry: Optional[Mapping[str, Mapping[str, Any]]] = None,
    ) -> AutonomyCycleReceipt:
        """Run a cycle over supplied capsules, payload files, or registry entries."""
        lint_result = CapsuleLintResult()

        if capsules:
            for index, capsule in enumerate(capsules):
                lint_result.extend(self.linter.lint_capsule(capsule, capsule_id=f"capsule:{index}"))
        if payload_files:
            for payload_path in payload_files:
                lint_result.extend(self.linter.lint_payload_file(Path(payload_path)))
        if registry:
            lint_result.extend(self.linter.lint_registry_entries(registry))
        if not any((capsules, payload_files, registry)):
            lint_result.extend(self.linter.lint_registered_payloads())

        report = self.correction_engine.plan_corrections(lint_result)
        receipt = self._build_receipt(lint_result, report.actions)
        if self.audit_log_path:
            self.write_audit_log(receipt)
        return receipt

    def write_audit_log(self, receipt: AutonomyCycleReceipt) -> None:
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_log_path, "a", encoding="utf-8") as handle:
            handle.write(f"Autonomy Cycle: {receipt.timestamp}\n")
            handle.write(f" - status: {receipt.status}\n")
            handle.write(f" - checked_capsules: {receipt.checked_capsules}\n")
            for correction in receipt.corrections:
                handle.write(f" - planned: {correction['action']} {correction.get('target')}\n")
            handle.write("\n")

    @staticmethod
    def _build_receipt(
        lint_result: CapsuleLintResult,
        actions: Iterable[CorrectionAction],
    ) -> AutonomyCycleReceipt:
        correction_dicts = [action.to_dict() for action in actions]
        status = "passed" if lint_result.valid and not correction_dicts else "attention_required"
        return AutonomyCycleReceipt(
            timestamp=_dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
            status=status,
            checked_capsules=lint_result.checked_capsules,
            findings=[finding.to_dict() for finding in lint_result.findings],
            corrections=correction_dicts,
        )


__all__ = ["AutonomyCycleReceipt", "ReflectiveAutonomyLoop"]
