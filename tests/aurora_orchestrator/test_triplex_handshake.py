"""
Tests for Triplex Handshake - Real Entity Integration

Verifies that the real entity singletons (AxiomeraEntity, CaelionEntity,
HALOEntity, ARCHYEntity) replace their mock counterparts and that
high-risk events are genuinely evaluated, not silently approved.

Ethics: Picard_Delta_3
Anchor: AURORA-ORCHESTRATOR-TRIPLEX-001
"""

from unittest import TestCase

import pytest

from src.core.event_system import Event, EventType, StationLocation
from src.entities.framework_agents import get_axiomera


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
    assertions = TestCase()

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
