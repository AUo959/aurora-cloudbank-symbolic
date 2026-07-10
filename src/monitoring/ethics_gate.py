"""Ethics gate: evaluates whether an operation is permitted before execution."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from modules.superposition_gate import Verdict, VerdictSeverity, collapse

logger = logging.getLogger(__name__)

LOW_RISK_IMPACT_LEVELS = {"low", "informational", "read_only", "read-only"}

# Maps EthicsEngine's ViolationSeverity to a (VerdictSeverity, score) pair for
# non-blocking violations. Deliberately caps below BLOCK/HARD_VETO: whether
# this gate raises is governed solely by `hard_veto` (== any violation with
# auto_block=True), not by nominal severity -- a HIGH-severity violation that
# isn't auto_block must not itself trigger a block, matching the original
# check_should_block() semantics exactly.
_NON_BLOCKING_SEVERITY_MAP = {
    "low": (VerdictSeverity.WARN, 0.7),
    "medium": (VerdictSeverity.WARN, 0.5),
    "high": (VerdictSeverity.THROTTLE, 0.3),
    "critical": (VerdictSeverity.THROTTLE, 0.1),
}


def _non_blocking_severity(violation: Any) -> tuple:
    """Map a violation's severity to (VerdictSeverity, score), defensively.

    Falls back to (WARN, 0.5) for anything that isn't one of EthicsEngine's
    four known ViolationSeverity values -- including test doubles/mocks that
    don't set `.severity` to a real enum. This lookup only ever affects
    informational severity/score for *non-blocking* violations; it can never
    change whether check_ethics() raises, since that's keyed on `hard_veto`
    (== violation.blocked) alone.
    """
    value = getattr(getattr(violation, "severity", None), "value", None)
    return _NON_BLOCKING_SEVERITY_MAP.get(value, (VerdictSeverity.WARN, 0.5))


def _violations_to_verdict(violations: List[Any], context_tag: Optional[str]) -> Verdict:
    """Normalize EthicsEngine's violation list into one Verdict for collapse().

    This is the first of the three existing ethics/safety evaluators wired
    into modules.superposition_gate.collapse() -- see that module's README
    for why the other two (the Ethics Field's dimension evaluators,
    EthicsAwareQuantumGate) are left as separate, later integrations rather
    than bolted on here.
    """
    if not violations:
        return Verdict(source="ethics_engine", severity=VerdictSeverity.ALLOW, score=1.0, context_tag=context_tag)

    hard_veto = any(v.blocked for v in violations)
    worst = min(violations, key=lambda v: _non_blocking_severity(v)[1])
    severity, score = _non_blocking_severity(worst)
    if hard_veto:
        severity = VerdictSeverity.HARD_VETO

    worst_name = getattr(worst, "rule_name", None) or "unknown_rule"
    return Verdict(
        source="ethics_engine",
        severity=severity,
        score=score,
        hard_veto=hard_veto,
        reason=f"{len(violations)} violation(s); worst={worst_name}",
        context_tag=context_tag,
    )


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
    EthicsViolation objects, which are normalized into a single Verdict and passed
    through modules.superposition_gate.collapse() to make the raise decision. With
    only one evaluator wired in, this is behavior-preserving today (still raises iff
    any violation has auto_block=True); the point is to make this call site ready
    to take a second/third evaluator's Verdict without changing again.

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

        verdict = _violations_to_verdict(violations, context_tag or None)
        collapsed = collapse([verdict])

        # Keyed on `final == HARD_VETO` specifically, not the broader `.blocked`
        # property: raising must depend only on hard_veto (== any violation with
        # auto_block=True), matching the original check_should_block() semantics
        # exactly regardless of how non-blocking violations map onto severity.
        if collapsed.final == VerdictSeverity.HARD_VETO:
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
