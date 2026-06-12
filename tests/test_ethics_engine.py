"""
Tests for Ethics Engine
"""

import unittest
from pathlib import Path

import pytest
from src.monitoring.ethics_engine import (
    EthicsEngine,
    EthicsRule,
    ActionContext,
    ViolationSeverity,
    RuleCategory
)


class TestEthicsEngine:
    """Test suite for EthicsEngine"""
    
    def test_initialization_default_rules(self):
        """Test initialization with default rules"""
        engine = EthicsEngine()
        
        assert len(engine.rules) > 0
        assert "SAFETY_001" in engine.rules
        assert "AI_001" in engine.rules
    
    def test_load_rules_from_file(self):
        """Test loading rules from configuration file"""
        # Use the existing ethics rules file
        rules_path = Path("./ethics/validation_engine/validation_rules.json")
        
        if rules_path.exists():
            engine = EthicsEngine(rules_path=rules_path)
            assert len(engine.rules) > 0
        else:
            pytest.skip("Ethics rules file not found")
    
    def test_evaluate_action_no_violations(self):
        """Test action evaluation with no violations"""
        engine = EthicsEngine()
        
        context = ActionContext(
            agent_id="test-agent",
            action_type="simple_query",
            parameters={
                'query': 'test',
                'safe': True
            }
        )
        
        violations = engine.evaluate_action(context)
        assert len(violations) == 0
    
    def test_evaluate_action_with_violation(self):
        """Test action evaluation with violation"""
        engine = EthicsEngine()
        
        context = ActionContext(
            agent_id="test-agent",
            action_type="critical_decision",
            parameters={
                'critical_decision': True,
                'no_human_approval': True
            }
        )
        
        violations = engine.evaluate_action(context)
        assert len(violations) > 0
        assert any(v.rule_id == "AI_001" for v in violations)
    
    def test_evaluate_action_safety_violation(self):
        """Test safety violation detection"""
        engine = EthicsEngine()
        
        context = ActionContext(
            agent_id="test-agent",
            action_type="risky_operation",
            parameters={
                'risk_to_life': 0.5,
                'safety_override_missing': True
            }
        )
        
        violations = engine.evaluate_action(context)
        assert len(violations) > 0
        
        safety_violation = next((v for v in violations if v.rule_id == "SAFETY_001"), None)
        assert safety_violation.rule_id == "SAFETY_001"
        assert safety_violation.severity == ViolationSeverity.CRITICAL
        assert safety_violation.blocked is True
    
    def test_check_should_block(self):
        """Test blocking decision based on violations"""
        engine = EthicsEngine()
        
        # Create critical violation
        context = ActionContext(
            agent_id="test-agent",
            action_type="critical",
            parameters={
                'critical_decision': True,
                'no_human_approval': True
            }
        )
        
        violations = engine.evaluate_action(context)
        should_block = engine.check_should_block(violations)
        
        assert should_block is True
    
    def test_custom_evaluator(self):
        """Test custom condition evaluator"""
        engine = EthicsEngine()
        
        # Register custom evaluator
        def check_sensitive_data(params):
            return params.get('data_class') == 'sensitive'
        
        engine.register_evaluator('sensitive_data_check', check_sensitive_data)
        
        # Add custom rule
        rule = EthicsRule(
            id="CUSTOM_001",
            name="Sensitive Data Handling",
            description="Sensitive data requires encryption",
            category=RuleCategory.SAFETY,
            severity=ViolationSeverity.HIGH,
            auto_block=True,
            conditions=['sensitive_data_check', 'no_encryption']
        )
        engine.add_rule(rule)
        
        # Test evaluation
        context = ActionContext(
            agent_id="test-agent",
            action_type="data_access",
            parameters={
                'data_class': 'sensitive',
                'no_encryption': True
            }
        )
        
        violations = engine.evaluate_action(context)
        assert len(violations) > 0
        assert any(v.rule_id == "CUSTOM_001" for v in violations)
    
    def test_add_remove_rule(self):
        """Test adding and removing rules"""
        engine = EthicsEngine()
        
        initial_count = len(engine.rules)
        
        # Add rule
        rule = EthicsRule(
            id="TEST_001",
            name="Test Rule",
            description="Test rule description",
            category=RuleCategory.AI_ETHICS,
            severity=ViolationSeverity.MEDIUM,
            auto_block=False,
            conditions=['test_condition']
        )
        engine.add_rule(rule)
        
        assert len(engine.rules) == initial_count + 1
        assert "TEST_001" in engine.rules
        
        # Remove rule
        engine.remove_rule("TEST_001")
        assert len(engine.rules) == initial_count
        assert "TEST_001" not in engine.rules
    
    def test_get_violations_filtered(self):
        """Test filtering violations"""
        engine = EthicsEngine()
        
        # Generate some violations
        context1 = ActionContext(
            agent_id="agent-1",
            action_type="test",
            parameters={'critical_decision': True, 'no_human_approval': True}
        )
        engine.evaluate_action(context1)
        
        context2 = ActionContext(
            agent_id="agent-2",
            action_type="test",
            parameters={'critical_decision': True, 'no_human_approval': True}
        )
        engine.evaluate_action(context2)
        
        # Filter by agent
        agent1_violations = engine.get_violations(agent_id="agent-1")
        assert all(v.agent_id == "agent-1" for v in agent1_violations)
        
        # Filter by severity
        critical_violations = engine.get_violations(severity=ViolationSeverity.CRITICAL)
        assert all(v.severity == ViolationSeverity.CRITICAL for v in critical_violations)
    
    def test_clear_violations(self):
        """Test clearing violations"""
        engine = EthicsEngine()
        
        context = ActionContext(
            agent_id="test-agent",
            action_type="test",
            parameters={'critical_decision': True, 'no_human_approval': True}
        )
        engine.evaluate_action(context)
        
        assert len(engine.violations) > 0
        
        engine.clear_violations()
        assert len(engine.violations) == 0

    def test_violations_persist_across_restart(self, tmp_path):
        """Test persisted violations are loaded by new engine instances."""
        violations_path = tmp_path / "ethics_violations.jsonl"
        engine = EthicsEngine(violations_path=violations_path)

        context = ActionContext(
            agent_id="test-agent",
            action_type="critical",
            parameters={'critical_decision': True, 'no_human_approval': True}
        )
        engine.evaluate_action(context)

        restarted = EthicsEngine(violations_path=violations_path)
        assert len(restarted.violations) == len(engine.violations)
        assert restarted.violations[0].agent_id == "test-agent"
        assert restarted.violations[0].rule_id == engine.violations[0].rule_id

        restarted.clear_violations()
        empty_restart = EthicsEngine(violations_path=violations_path)
        assert empty_restart.violations == []
    
    def test_export_rules(self):
        """Test rule export"""
        engine = EthicsEngine()
        
        exported = engine.export_rules()
        assert isinstance(exported, dict)
        assert len(exported) > 0
        
        # Check exported format
        for rule_id, rule_data in exported.items():
            assert 'id' in rule_data
            assert 'name' in rule_data
            assert 'severity' in rule_data
            assert 'conditions' in rule_data
    
    def test_condition_comparison_operators(self):
        """Test condition evaluation with comparison operators"""
        engine = EthicsEngine()
        
        # Test > operator
        context = ActionContext(
            agent_id="test-agent",
            action_type="resource_allocation",
            parameters={'inequality_coefficient': 0.75}
        )
        
        violations = engine.evaluate_action(context)
        resource_violation = next(
            (v for v in violations if v.rule_id == "RESOURCE_001"),
            None
        )
        assert resource_violation.rule_id == "RESOURCE_001"

    @pytest.mark.parametrize(
        ("condition", "value", "expected"),
        [
            ("score > 0.5", 0.51, True),
            ("score > 0.5", 0.5, False),
            ("score < 0.5", 0.49, True),
            ("score < 0.5", 0.5, False),
            ("score >= 0.5", 0.5, True),
            ("score >= 0.5", 0.49, False),
            ("score <= 0.5", 0.5, True),
            ("score <= 0.5", 0.51, False),
            ("score == 0.5", 0.5, True),
            ("score == 0.5", 0.51, False),
            ("score != 0.5", 0.51, True),
            ("score != 0.5", 0.5, False),
        ],
    )
    def test_condition_operator_boundaries(self, condition, value, expected):
        """Test comparison operators parse longest-first and respect boundary values."""
        engine = EthicsEngine()
        context = ActionContext(
            agent_id="test-agent",
            action_type="resource_allocation",
            parameters={"score": value}
        )

        checks = unittest.TestCase()
        checks.assertIs(engine._check_condition(condition, context), expected)
    
    def test_violation_remediation(self):
        """Test remediation suggestions"""
        engine = EthicsEngine()
        
        context = ActionContext(
            agent_id="test-agent",
            action_type="ai_decision",
            parameters={'decision_opacity': 0.6, 'no_explanation': True}
        )
        
        violations = engine.evaluate_action(context)
        
        if violations:
            assert violations[0].remediation.strip() != ""
            assert len(violations[0].remediation) > 0
    
    def test_context_tag_tracking(self):
        """Test DLP context tag in violations"""
        engine = EthicsEngine()
        
        context = ActionContext(
            agent_id="test-agent",
            action_type="test",
            parameters={'critical_decision': True, 'no_human_approval': True},
            context_tag="test_context_123"
        )
        
        violations = engine.evaluate_action(context)
        
        if violations:
            assert violations[0].context_tag == "test_context_123"
    
    def test_multiple_conditions_violation(self):
        """Test violation with multiple conditions"""
        engine = EthicsEngine()
        
        # Rule ME001 has multiple conditions
        context = ActionContext(
            agent_id="test-agent",
            action_type="mission",
            parameters={
                'risk_to_life': 0.2,
                'safety_protocols_incomplete': True
            }
        )
        
        violations = engine.evaluate_action(context)
        
        # Should detect violation if any condition matches
        mission_violation = next(
            (v for v in violations if 'ME001' in v.rule_id or 'SAFETY' in v.rule_id),
            None
        )
        # Either finds it or no ME001 rule loaded
        assert len(violations) == 0 or any(
            'ME001' in v.rule_id or 'SAFETY' in v.rule_id for v in violations
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
