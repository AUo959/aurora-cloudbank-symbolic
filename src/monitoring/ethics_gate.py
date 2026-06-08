"""Ethics gate: evaluates whether an operation is permitted before execution."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class EthicsViolationError(Exception):
    """Raised when an ethics check fails."""

    def __init__(self, message: str, violations: List[Any]):
        super().__init__(message)
        self.violations = violations


def check_ethics(
    action_type: str,
    parameters: Dict[str, Any],
    *,
    agent_id: str = "api",
    context_tag: str = "",
) -> None:
    """Run the EthicsEngine check. Raises EthicsViolationError if not permitted.

    Uses EthicsEngine.evaluate_action(ActionContext) — the engine returns a list of
    EthicsViolation objects; if any have auto_block=True the gate raises.

    No-op (passes silently) if EthicsEngine is unavailable.

    Args:
        action_type: Type/name of the action being evaluated (e.g. "quantum_simulate").
        parameters: Free-form dict describing the action's parameters.
        agent_id: Identifier of the calling agent/service.
        context_tag: DLP context tag for audit trail.

    Raises:
        EthicsViolationError: If the engine is available and determines the action
            should be blocked.
    """
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
        logger.debug("EthicsEngine unavailable, allowing action '%s': %s", action_type, exc)
