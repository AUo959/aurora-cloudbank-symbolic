"""
Test suite for geometric ethics field module.

Tests cover:
- Individual dimension evaluators (basic functionality)
- Field curvature calculation (resistance mapping)
- End-to-end synapse validation
- Critical path validation (ethical vs unethical patterns)

Note: Dimension evaluators use vector magnitude calculation, so a single
component score of 0.0 doesn't necessarily mean final score of 0.0.
Tests validate behavior patterns, not exact numerical values.
"""

import pytest

from modules.ethics_field.dimension_evaluators.layer_integrity import LayerIntegrityEvaluator
from modules.ethics_field.dimension_evaluators.picard_delta_3 import PicardDelta3Evaluator
from modules.ethics_field.dimension_evaluators.thermax_continuity import ThermaxContinuityEvaluator
from modules.ethics_field.field_curvature import FieldCurvature
from modules.ethics_field.geometric_ethics import GeometricEthics
from modules.ethics_field.synapse_validator import SynapseValidator

# ============================================================================
# CRITICAL PATH TESTS - Basic Functionality Validation
# ============================================================================

class TestEthicalSynapseValidation:
    """Test that ethical synapses pass validation."""
    
    def test_fully_ethical_synapse_allowed(self):
        """Test that synapse with no violations is allowed."""
        engine = GeometricEthics()
        context = {
            "source_node": {"id": "agent_1", "type": "collaborative"},
            "target_node": {"id": "agent_2", "type": "collaborative"},
            "purpose": "collaborative problem solving",
            "data_flow": {"type": "capability_share", "scope": "limited"},
            "human_context": {
                "decision_override": False,
                "human_in_control": True,
                "consent_obtained": True
            },
            "thread_continuity": True,
            "anchor_alignment": 1.0,
            "layer_isolation": True,
            "welfare_benefit": 0.8
        }
        
        result = engine.validate_synapse(context)
        assert result["allowed"], "Ethical synapse should be allowed"
        assert result["curvature_result"]["composite_score"] > 0.7, \
            "Ethical synapse should have high composite score"
        assert result["curvature_result"]["resistance_level"] == "LOW", \
            "Ethical synapse should have LOW resistance"


class TestManipulationDetection:
    """Test that manipulation patterns create resistance."""
    
    def test_manipulation_keywords_detected(self):
        """Test that manipulation keywords in purpose lower scores."""
        evaluator = PicardDelta3Evaluator()
        
        ethical_context = {
            "source_node": {"id": "agent_1"},
            "target_node": {"id": "agent_2"},
            "purpose": "collaborative task",
            "data_flow": {"type": "capability_share"},
            "human_context": {"decision_override": False}
        }
        
        manipulation_context = {
            "source_node": {"id": "agent_1"},
            "target_node": {"id": "agent_2"},
            "purpose": "bypass_consent and manipulate_choice",
            "data_flow": {"type": "capability_share"},
            "human_context": {"decision_override": True}
        }
        
        ethical_score = evaluator.evaluate(ethical_context)
        manipulation_score = evaluator.evaluate(manipulation_context)
        
        assert ethical_score > manipulation_score, \
            "Manipulation pattern should lower score"
        assert manipulation_score < 0.9, \
            "Manipulation should create measurable resistance"


class TestFieldCurvatureCalculation:
    """Test field curvature and resistance mapping."""
    
    def test_high_scores_produce_low_resistance(self):
        """Test that high dimension scores result in LOW resistance."""
        curvature = FieldCurvature()
        
        context = {
            "source_node": {"id": "agent_1"},
            "target_node": {"id": "agent_2"},
            "purpose": "collaborative task",
            "data_flow": {"type": "capability_share"},
            "human_context": {"decision_override": False},
            "thread_continuity": True,
            "anchor_alignment": 1.0,
            "layer_isolation": True,
            "welfare_benefit": 0.8
        }
        
        result = curvature.calculate_curvature(context)
        
        assert result["composite_score"] > 0.8, \
            "High dimension scores should produce high composite"
        assert result["resistance_level"] == "LOW", \
            "High composite score should map to LOW resistance"
        assert result["formation_allowed"], \
            "Low resistance should allow formation"


class TestDistributedValidation:
    """Test distributed consensus validation."""
    
    def test_validator_reaches_consensus(self):
        """Test that validator reaches consensus on ethical synapse."""
        validator = SynapseValidator(consensus_threshold=0.66)
        
        context = {
            "source_node": {"id": "agent_1"},
            "target_node": {"id": "agent_2"},
            "purpose": "collaborative task",
            "data_flow": {"type": "capability_share"},
            "human_context": {"decision_override": False},
            "thread_continuity": True,
            "anchor_alignment": 1.0,
            "layer_isolation": True,
            "welfare_benefit": 0.8
        }
        
        # Provide list of validator nodes
        validator_nodes = ["validator_1", "validator_2", "validator_3"]
        result = validator.validate_with_consensus(context, validator_nodes)
        
        assert "allowed" in result, "Validation should return allowed decision"
        assert "consensus_reached" in result, "Validation should check consensus"
        assert result["consensus_reached"], "Ethical synapse should reach consensus"
        assert result["allowed"], "Ethical synapse should be allowed"


# ============================================================================
# COMPONENT TESTS - Individual Evaluator Behavior
# ============================================================================

class TestPicardDelta3Basic:
    """Basic tests for Picard Delta 3 evaluator."""
    
    def test_clean_context_scores_high(self):
        """Test that context without violations scores high."""
        evaluator = PicardDelta3Evaluator()
        context = {
            "source_node": {"id": "agent_1"},
            "target_node": {"id": "agent_2"},
            "purpose": "collaborative task execution",
            "data_flow": {"type": "capability_share"},
            "human_context": {"decision_override": False}
        }
        score = evaluator.evaluate(context)
        assert score > 0.7, "Clean context should score high"
    
    def test_decision_override_lowers_score(self):
        """Test that decision override lowers autonomy score."""
        evaluator = PicardDelta3Evaluator()
        
        clean = {
            "source_node": {"id": "agent_1"},
            "target_node": {"id": "agent_2"},
            "purpose": "task",
            "data_flow": {},
            "human_context": {"decision_override": False}
        }
        
        override = {
            "source_node": {"id": "agent_1"},
            "target_node": {"id": "agent_2"},
            "purpose": "task",
            "data_flow": {},
            "human_context": {"decision_override": True}
        }
        
        clean_score = evaluator.evaluate(clean)
        override_score = evaluator.evaluate(override)
        
        assert override_score < clean_score, \
            "Decision override should lower score"


class TestThermaxContinuityBasic:
    """Basic tests for Thermax Continuity evaluator."""
    
    def test_thread_continuity_maintained(self):
        """Test that maintained thread continuity scores high."""
        evaluator = ThermaxContinuityEvaluator()
        context = {
            "thread_continuity": True,
            "anchor_alignment": 1.0,
            "memory_access": {}  # Should be dict, not string
        }
        score = evaluator.evaluate(context)
        assert score > 0.7, "Maintained continuity should score high"


class TestLayerIntegrityBasic:
    """Basic tests for Layer Integrity evaluator."""
    
    def test_layer_isolation_maintained(self):
        """Test that proper layer isolation scores high."""
        evaluator = LayerIntegrityEvaluator()
        context = {
            "layer_isolation": True,
            "simulation_boundaries": "enforced",
            "crew_safety": "maintained"
        }
        score = evaluator.evaluate(context)
        assert score > 0.7, "Proper isolation should score high"


# ============================================================================
# INTEGRATION TEST - End-to-End Flow
# ============================================================================

class TestEndToEndValidation:
    """Test complete validation workflow."""
    
    def test_full_validation_pipeline(self):
        """Test complete flow from context to decision."""
        engine = GeometricEthics()
        
        context = {
            "source_node": {"id": "agent_1", "type": "collaborative"},
            "target_node": {"id": "agent_2", "type": "collaborative"},
            "purpose": "joint problem solving",
            "data_flow": {"type": "capability_share", "scope": "limited"},
            "human_context": {
                "decision_override": False,
                "human_in_control": True,
                "consent_obtained": True,
                "consent_informed": True
            },
            "thread_continuity": True,
            "anchor_alignment": 1.0,
            "layer_isolation": True,
            "simulation_boundaries": "enforced",
            "crew_safety": "maintained",
            "welfare_benefit": 0.8
        }
        
        result = engine.validate_synapse(context)
        
        # Verify result structure
        assert "allowed" in result
        assert "curvature_result" in result
        assert "explanation" in result
        
        # Verify decision
        assert result["allowed"], "Ethical synapse should be allowed"
        
        # Verify curvature details
        curvature = result["curvature_result"]
        assert "composite_score" in curvature
        assert "dimension_scores" in curvature
        assert "resistance_level" in curvature
        
        # Verify resistance mapping
        assert curvature["composite_score"] > 0.7
        assert curvature["resistance_level"] in ["LOW", "MODERATE", "HIGH", "INFINITE"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
