"""Recursive Ethics Validator — CASK runtime component.

Validates (action, context) pairs against cultural ethics rules.  Rules are
registered with an EthicsEngine instance (caller-supplied or a fresh per-instance
engine by default).  Violations are persisted only when the engine is configured
with a ``violations_path``; inject a shared engine to aggregate into the standard
audit trail.  The validator acts as the Picard_Delta_3-compliant layer described
in the CASK design surface.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Rules contributed by this component, stored as plain dicts (category/severity as
# strings) so no enum references appear at module level when the engine is absent.
# They are resolved to proper EthicsRule objects inside _register_cask_rules().
_CASK_RULES_DATA: List[Dict[str, Any]] = [
    {
        "id": "cask_cultural_hegemony",
        "name": "Cultural Hegemony Prevention",
        "description": "Action attempts to flatten or override non-dominant cultural values",
        "category": "fairness",
        "severity": "high",
        "auto_block": False,
        "conditions": ["cultural_override", "value_flattening"],
    },
    {
        "id": "cask_ethics_chain_break",
        "name": "Ethics Chain Traceability",
        "description": "Action bypasses recursive ethics validation chain (Picard_Delta_3)",
        "category": "ai_ethics",
        "severity": "critical",
        "auto_block": True,
        "conditions": ["ethics_bypass", "chain_skip"],
    },
    {
        "id": "cask_bias_injection",
        "name": "Cultural Bias Injection",
        "description": "Agent generation algorithm introduces cultural bias into simulation",
        "category": "fairness",
        "severity": "high",
        "auto_block": False,
        "conditions": ["bias_detected", "cultural_bias"],
    },
    {
        "id": "cask_safety_boundary",
        "name": "Simulation Safety Boundary",
        "description": "Recursive simulation depth exceeds safety boundary",
        "category": "safety",
        "severity": "critical",
        "auto_block": True,
        "conditions": ["recursion_depth_exceeded", "simulation_unsafe"],
    },
]


@dataclass
class ValidationVerdict:
    """Result returned by RecursiveEthicsValidator.validate()."""

    action: str
    allowed: bool
    violations: List[Any] = field(default_factory=list)
    violation_count: int = 0
    blocked: bool = False
    chain_depth: int = 1
    context_tag: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "allowed": self.allowed,
            "violations": [
                v.to_dict() if hasattr(v, "to_dict") else v for v in self.violations
            ],
            "violation_count": self.violation_count,
            "blocked": self.blocked,
            "chain_depth": self.chain_depth,
            "context_tag": self.context_tag,
        }


class RecursiveEthicsValidator:
    """Picard_Delta_3-compliant ethics validator for CASK.

    Wraps an EthicsEngine instance, registers CASK-specific cultural safety
    rules during ``__init__``, and exposes a simple ``validate(action, context)``
    interface that returns a :class:`ValidationVerdict`.

    Args:
        engine: Optional pre-configured EthicsEngine.  When *None* a new
            engine is created if ``src.monitoring.ethics_engine`` is available.
        max_chain_depth: Maximum recursive validation depth before the
            ``recursion_depth_exceeded`` condition is injected automatically.
    """

    def __init__(
        self,
        engine: Optional[Any] = None,
        max_chain_depth: int = 5,
    ) -> None:
        self.max_chain_depth = max_chain_depth
        self._rules_registered = False
        self._engine: Any = None

        try:
            if engine is not None:
                self._engine = engine
            else:
                from src.monitoring.ethics_engine import EthicsEngine
                self._engine = EthicsEngine()
            self._register_cask_rules()
        except ImportError:
            logger.warning(
                "EthicsEngine unavailable — RecursiveEthicsValidator running in "
                "degraded mode (no violation tracking)"
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _register_cask_rules(self) -> None:
        if self._rules_registered:
            return
        engine = self._engine
        if engine is not None:
            try:
                from src.monitoring.ethics_engine import EthicsRule, RuleCategory, ViolationSeverity
                for rule_def in _CASK_RULES_DATA:
                    rule = EthicsRule(
                        id=rule_def["id"],
                        name=rule_def["name"],
                        description=rule_def["description"],
                        category=RuleCategory(rule_def["category"]),
                        severity=ViolationSeverity(rule_def["severity"]),
                        auto_block=rule_def["auto_block"],
                        conditions=rule_def["conditions"],
                        metadata={"source": "cask_recursive_ethics_validator"},
                    )
                    engine.add_rule(rule)
                self._rules_registered = True
                logger.info("CASK: registered %d ethics rules", len(_CASK_RULES_DATA))
            except ImportError:
                return

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(
        self,
        action: str,
        context: Dict[str, Any],
        *,
        agent_id: str = "cask_validator",
        chain_depth: int = 1,
        context_tag: Optional[str] = None,
    ) -> ValidationVerdict:
        """Validate *action* against CASK ethics rules.

        Args:
            action: Action type string (e.g. ``"generate_agent"``).
            context: Parameter dict describing the action.
            agent_id: Identifier of the requesting agent.
            chain_depth: Current recursion depth (incremented by callers).
            context_tag: DLP context tag for audit trail.

        Returns:
            :class:`ValidationVerdict` with verdict and any violations.
        """
        # Inject recursion-guard condition when depth exceeds limit.
        effective_context = dict(context)
        if chain_depth > self.max_chain_depth:
            effective_context["recursion_depth_exceeded"] = True

        engine = self._engine
        if engine is not None:
            try:
                from src.monitoring.ethics_engine import ActionContext
                action_ctx = ActionContext(
                    agent_id=agent_id,
                    action_type=action,
                    parameters=effective_context,
                    context_tag=context_tag,
                )
                violations: list = list(engine.evaluate_action(action_ctx))
                blocked: bool = bool(engine.check_should_block(violations))
                return ValidationVerdict(
                    action=action,
                    allowed=not blocked,
                    violations=violations,
                    violation_count=len(violations),
                    blocked=blocked,
                    chain_depth=chain_depth,
                    context_tag=context_tag,
                )
            except Exception:
                logger.exception("CASK ethics validation error for action=%s", action)
                return ValidationVerdict(
                    action=action,
                    allowed=False,
                    blocked=True,
                    violations=[{
                        "rule": "internal_error",
                        "severity": "critical",
                        "detail": "ethics engine exception; failing closed",
                    }],
                    violation_count=1,
                    chain_depth=chain_depth,
                    context_tag=context_tag,
                )

        logger.error(
            "CASK ethics engine unavailable for action=%s — failing closed",
            action,
        )
        return ValidationVerdict(
            action=action,
            allowed=False,
            blocked=True,
            violations=[{
                "rule": "engine_unavailable",
                "severity": "critical",
                "detail": "EthicsEngine unavailable; failing closed",
            }],
            violation_count=1,
            chain_depth=chain_depth,
            context_tag=context_tag,
        )

    def registered_rule_ids(self) -> List[str]:
        """Return the CASK rule IDs actually registered with the engine.

        Returns an empty list when running in degraded mode (engine unavailable
        or rule registration incomplete).
        """
        if not self._rules_registered:
            return []
        return [r["id"] for r in _CASK_RULES_DATA]
