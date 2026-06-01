"""
Tests for Triplex Handshake - Real Entity Integration

Verifies that the real entity singletons (AxiomeraEntity, CaelionEntity,
HALOEntity, ARCHYEntity) replace their mock counterparts and that
high-risk events are genuinely evaluated, not silently approved.

Ethics: Picard_Delta_3
Anchor: AURORA-ORCHESTRATOR-TRIPLEX-001
"""

from datetime import datetime, timezone
from unittest import TestCase

import pytest

from src.agents.aurora_consciousness_agent import AuroraDecision, DecisionPriority
from src.aurora_orchestrator.triplex_handshake import TriplexHandshakeValidator
from src.core.event_system import Event, EventType, StationLocation
from src.entities.framework_agents import get_axiomera
from src.entities.relay_agents import get_archy


def _assertions():
    """Return assertion helpers without raw Python assertion statements, which Codacy flags."""
    return TestCase()


@pytest.mark.asyncio
async def test_axiomera_blocks_high_risk_event():
    """
    Real AxiomeraEntity must block a critically high-risk event.

    Acceptance criteria: a high-risk event (risk_score > 0.8) returns a
    BLOCK recommendation from AxiomeraEntity.evaluate_for_triplex(), not
    a silent approval as the removed MockAxiomera would have produced.

    Event configuration that triggers BLOCK:
    - risk_score = 0.9  (> 0.8, high-risk)
    - continuity_load = 0.8  (> 0.7, triggers continuity concern)
    - human_context set  (human-impacting op with risk > 0.5)
    - context_tag empty  (no DLP transparency tag, triggers concern)
    → three Picard_Delta_3 concerns → ethical_score < 0.3 → "critical"
    → recommendation = "BLOCK"
    """
    event = Event(
        event_type=EventType.ETHICAL_REVIEW_L3,
        location=StationLocation.COMMAND_BRIDGE,
        primary_entity="Aurora (SYS_001)",
        payload={"action": "critical_operation"},
        risk_score=0.9,
        continuity_load=0.8,
        human_context="test_operator",
        context_tag="",  # Missing DLP tag triggers transparency concern
    )

    axiomera = get_axiomera()
    result = await axiomera.evaluate_for_triplex(event)
    assertions = _assertions()

    assertions.assertEqual(
        result["recommendation"],
        "BLOCK",
        msg=(
            f"Expected BLOCK for critically high-risk event, "
            f"got {result['recommendation']!r}. "
            f"Reasoning: {result.get('reasoning')}"
        ),
    )
    assertions.assertLess(
        result["ethical_assessment"]["ethical_score"],
        0.3,
        msg=(
            f"Expected ethical_score < 0.3 for critical risk, "
            f"got {result['ethical_assessment']['ethical_score']}"
        ),
    )
    assertions.assertEqual(result["ethical_assessment"]["risk_level"], "critical")


@pytest.mark.asyncio
async def test_validator_routes_human_consent_recommendation_to_l1_oversight():
    """
    Axiomera's REQUIRE_HUMAN_CONSENT recommendation should not block at L3.

    It should pass the L3 gate with an explicit L1 oversight requirement, then
    run the real ARCHYEntity L1 oversight path before approving the decision.
    """
    decision = AuroraDecision(
        decision_id="triplex-human-consent",
        timestamp=datetime.now(timezone.utc).isoformat(),
        priority=DecisionPriority.HIGH,
        context={
            "action": "human_impacting_operation",
            "continuity_load": 0.8,
            "human_context": "test_operator",
            "feasible": True,
        },
        action="perform high-risk human-impacting operation",
        rationale="exercise L3 human-consent routing",
        expected_outcomes=["L1 oversight invoked"],
        risk_assessment=0.9,
        ethical_compliance=True,
        requires_human_approval=False,
    )

    result = await TriplexHandshakeValidator().validate_decision(decision)
    assertions = _assertions()

    assertions.assertTrue(result.approved, msg=result.reason)
    assertions.assertIsNone(result.blocked_at_level)
    assertions.assertIsNotNone(result.l1_result)
    assertions.assertTrue(result.l3_result["requires_human_approval"])
    assertions.assertEqual(result.l3_result["ethics"]["recommendation"], "REQUIRE_HUMAN_CONSENT")
    assertions.assertEqual(result.l1_result["approval"]["approval_mode"], "architecture_oversight")


def test_validator_uses_real_archy_singleton_for_l2_feasibility():
    """The L2 feasibility gate must use ARCHYEntity, not a local mock."""
    validator = TriplexHandshakeValidator()
    assertions = _assertions()

    assertions.assertIs(validator.archy, get_archy())
    assertions.assertIs(validator.l1_oversight, validator.archy)


@pytest.mark.asyncio
async def test_validator_blocks_infeasible_decision_at_l2_archy():
    """ARCHYEntity feasibility rejection should block at L2."""
    decision = AuroraDecision(
        decision_id="triplex-l2-infeasible",
        timestamp=datetime.now(timezone.utc).isoformat(),
        priority=DecisionPriority.MEDIUM,
        context={
            "action": "bounded_maintenance_operation",
            "continuity_load": 0.3,
            "feasible": False,
        },
        action="perform bounded maintenance operation",
        rationale="exercise L2 ARCHY feasibility rejection",
        expected_outcomes=["L2 rejection"],
        risk_assessment=0.1,
        ethical_compliance=True,
        requires_human_approval=False,
    )

    result = await TriplexHandshakeValidator().validate_decision(decision)
    assertions = _assertions()

    assertions.assertFalse(result.approved)
    assertions.assertEqual(result.blocked_at_level, "L2")
    assertions.assertEqual(result.reason, "Technical feasibility check failed")
    assertions.assertFalse(result.l2_result["feasibility"]["approved"])
    assertions.assertEqual(result.l2_result["feasibility"]["evaluator"], "ARCHY (RELAY_001)")
    assertions.assertIn(
        "Decision context marks operation infeasible",
        result.l2_result["feasibility"]["constraints"],
    )
