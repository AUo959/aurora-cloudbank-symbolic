"""Reflective decision checks for the Sonnet 4 autonomy surface."""

from typing import Any, Dict, Optional

try:
    from .autonomic_correction_engine import AutonomicCorrectionEngine
except ImportError:  # pragma: no cover - direct script execution fallback
    from autonomic_correction_engine import AutonomicCorrectionEngine


class ReflectiveEngine:
    """Reflective autonomy engine for decision and context checks."""

    def __init__(self, correction_engine: Optional[AutonomicCorrectionEngine] = None) -> None:
        self.correction_engine = correction_engine or AutonomicCorrectionEngine()

    def reflect_on_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Return a governance receipt for a decision payload."""
        required_fields = ("decision_id", "rationale", "expected_outcomes")
        missing = [field for field in required_fields if not decision.get(field)]
        approved = not missing and decision.get("ethical_verified") is not False
        return {
            "reflection": "processed",
            "approved": approved,
            "missing_fields": missing,
            "decision": decision,
        }

    def autonomous_adjustment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan capsule corrections from a context payload without mutating it."""
        capsule = context.get("capsule") if isinstance(context, dict) else None
        if isinstance(capsule, dict):
            report = self.correction_engine.evaluate_capsule(capsule)
            return {
                "adjustment": "planned",
                "approved": report.approved,
                "corrections": [action.to_dict() for action in report.actions],
            }
        return {
            "adjustment": "none",
            "approved": False,
            "reason": "No capsule payload supplied",
        }
