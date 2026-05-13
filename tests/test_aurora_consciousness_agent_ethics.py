import unittest

from src.agents.aurora_consciousness_agent import AuroraConsciousnessAgent


def test_think_marks_safe_thought_ethics_verified():
    checks = unittest.TestCase()
    agent = AuroraConsciousnessAgent()

    thought = agent.think({"type": "strategic_planning", "focus": "maintenance"})

    checks.assertIs(thought.ethical_verified, True)
    checks.assertEqual(agent.stats["ethical_verifications"], 1)
    checks.assertEqual(agent.ethics_engine.violations, [])


def test_think_blocks_critical_thought_without_human_approval():
    checks = unittest.TestCase()
    agent = AuroraConsciousnessAgent()

    thought = agent.think(
        {
            "type": "strategic_planning",
            "critical_decision": True,
            "no_human_approval": True,
        }
    )

    checks.assertIs(thought.ethical_verified, False)
    checks.assertEqual(agent.stats["ethical_verifications"], 1)
    checks.assertTrue(
        any(violation.rule_id == "AI_001" for violation in agent.ethics_engine.violations)
    )
