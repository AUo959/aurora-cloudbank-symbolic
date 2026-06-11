"""Ethics gate: evaluates whether an operation is permitted before execution."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

LOW_RISK_IMPACT_LEVELS = {"low", "informational", "read_only", "read-only"}


class EthicsViolationError(Exception):
    """Raised when an ethics check fails."""

    def __init__(self, message: str, violations: List[Any]):
        super().__init__(message)
        self.violations = violations


def _gate_unavailable_violation(
    action_type: str,
    agent_id: str,
    context_tag: str,
    impact_level: str,
    exc: Exception,
) -> Dict[str, Any]:
    return {
        "rule_id": "ETHICS_GATE_UNAVAILABLE",
        "rule_name": "Ethics Gate Availability",
        "severity": "critical",
        "blocked": True,
        "description": "EthicsEngine could not evaluate the action.",
        "action_type": action_type,
        "agent_id": agent_id,
        "context_tag": context_tag or None,
        "impact_level": impact_level,
        "error_type": type(exc).__name__,
        "error": str(exc),
    }


def check_ethics(
    action_type: str,
    parameters: Dict[str, Any],
    *,
    agent_id: str = "api",
    context_tag: str = "",
    impact_level: str = "high",
    allow_degraded: bool = False,
) -> None:
    """Run the EthicsEngine check. Raises EthicsViolationError if not permitted.

    Uses EthicsEngine.evaluate_action(ActionContext) — the engine returns a list of
    EthicsViolation objects; if any have auto_block=True the gate raises.

    The gate fails closed by default when EthicsEngine is unavailable or errors.
    Low-risk callers may explicitly opt into degraded allow behavior by passing
    ``impact_level="low"`` and ``allow_degraded=True``; this path emits a
    warning so the degraded decision is visible in logs.

    Args:
        action_type: Type/name of the action being evaluated (e.g. "quantum_simulate").
        parameters: Free-form dict describing the action's parameters.
        agent_id: Identifier of the calling agent/service.
        context_tag: DLP context tag for audit trail.
        impact_level: Risk/impact level for gate-unavailable fallback decisions.
        allow_degraded: Allow explicit low-risk degraded operation if the engine
            cannot evaluate the action.

    Raises:
        EthicsViolationError: If the engine determines the action should be
            blocked, or if the engine cannot evaluate a non-degraded operation.
    """
    normalized_impact = str(impact_level or "high").strip().lower()
    try:
        from src.monitoring.ethics_engine import ActionContext, EthicsEngine

        engine = EthicsEngine()

        context = ActionContext(
            agent_id=agent_id,
            action_type=action_type,
            parameters=parameters,
            context_tag=context_tag or None,
        )

        violations = engine.evaluate_action(context)

        if violations and engine.check_should_block(violations):
            serialized = [v.to_dict() for v in violations if v.blocked]
            raise EthicsViolationError(
                f"Ethics check failed for {action_type}: "
                f"{len(serialized)} blocking violation(s)",
                violations=serialized,
            )

    except EthicsViolationError:
        raise
    except Exception as exc:
        violation = _gate_unavailable_violation(
            action_type=action_type,
            agent_id=agent_id,
            context_tag=context_tag,
            impact_level=normalized_impact,
            exc=exc,
        )
        if allow_degraded and normalized_impact in LOW_RISK_IMPACT_LEVELS:
            logger.warning(
                "EthicsEngine unavailable; allowing low-risk degraded action '%s': %s",
                action_type,
                exc,
            )
            return

        logger.error(
            "EthicsEngine unavailable; blocking action '%s' at impact level '%s': %s",
            action_type,
            normalized_impact,
            exc,
        )
        raise EthicsViolationError(
            f"Ethics gate unavailable for {action_type}; failing closed",
            violations=[violation],
        )
