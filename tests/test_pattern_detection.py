"""
Test Pattern Detection in Field State Manager

Validates that PatternDetector integration works correctly:
- Pattern detection methods callable
- Field coherence calculation works
- Recommendations generated properly
- Pattern recording integrated

Thread: T1→T8→T9→INFINITE
DLP: context_tag=test_pattern_detection, symbolic_hash=PATTERN_INTELLIGENCE_TEST_v1
"""

import pytest

from modules.field_state_manager.field_state_manager import FieldStateManager
from modules.field_state_manager.pattern_detector import FieldCoherence, Pattern


@pytest.mark.unit
@pytest.mark.aurora
class TestPatternDetection:
    """Test pattern detection integration in FieldStateManager."""

    def test_pattern_detection_enabled_by_default(self):
        """Pattern detection should be enabled by default."""
        fsm = FieldStateManager(use_compressed_registry=False)
        assert fsm.enable_pattern_detection is True
        assert fsm.pattern_detector is not None

    def test_pattern_detection_can_be_disabled(self):
        """Pattern detection can be explicitly disabled."""
        fsm = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False
        )
        assert fsm.enable_pattern_detection is False
        assert fsm.pattern_detector is None

    def test_detect_patterns_with_empty_field(self):
        """Detect patterns should return empty results for new field."""
        fsm = FieldStateManager(use_compressed_registry=False)
        patterns = fsm.detect_patterns()
        
        assert "collaboration" in patterns
        assert "bottleneck" in patterns
        assert "cascade" in patterns
        assert "coalition" in patterns
        
        # Should be empty for new field
        assert len(patterns["collaboration"]) == 0
        assert len(patterns["bottleneck"]) == 0
        assert len(patterns["cascade"]) == 0
        assert len(patterns["coalition"]) == 0

    def test_detect_patterns_when_disabled(self):
        """Detect patterns should return empty dict when disabled."""
        fsm = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False
        )
        patterns = fsm.detect_patterns()
        
        # Should have empty lists for all types
        assert all(len(p) == 0 for p in patterns.values())

    def test_get_field_coherence_with_empty_field(self):
        """Field coherence should work for empty field."""
        fsm = FieldStateManager(use_compressed_registry=False)
        coherence = fsm.get_field_coherence()
        
        assert coherence is not None
        assert isinstance(coherence, FieldCoherence)
        assert 0.0 <= coherence.overall_score <= 1.0

    def test_get_field_coherence_when_disabled(self):
        """Field coherence should return None when disabled."""
        fsm = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False
        )
        coherence = fsm.get_field_coherence()
        assert coherence is None

    def test_get_pattern_recommendations_with_empty_field(self):
        """Pattern recommendations should work for empty field."""
        fsm = FieldStateManager(use_compressed_registry=False)
        recommendations = fsm.get_pattern_recommendations()
        
        assert isinstance(recommendations, list)
        # May or may not have recommendations for empty field

    def test_get_pattern_recommendations_when_disabled(self):
        """Pattern recommendations should return empty list when disabled."""
        fsm = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False
        )
        recommendations = fsm.get_pattern_recommendations()
        assert recommendations == []

    def test_pattern_recording_integration(self):
        """Test that synapse usage is recorded for pattern detection."""
        fsm = FieldStateManager(use_compressed_registry=False)
        
        # Register two nodes
        fsm.register_node("node_a", ["capability_x"])
        fsm.register_node("node_b", ["capability_y"])
        
        # Form a synapse
        synapse_id = fsm.form_synapse(
            source_node_id="node_a",
            target_node_id="node_b",
            purpose="test_collaboration",
            initial_weight=0.5,
            ethical_score=0.9,
            skip_ethics_check=True
        )
        
        assert synapse_id is not None
        
        # Record successful usage
        fsm.record_synapse_usage("node_a", "node_b", success=True)
        
        # Pattern detector should have recorded this
        assert len(fsm.pattern_detector.synapse_activations) > 0
        
        # Check recording
        last_activation = fsm.pattern_detector.synapse_activations[-1]
        assert last_activation[0] == "node_a"  # source_id
        assert last_activation[1] == "node_b"  # target_id
        assert last_activation[3] is True  # success

    def test_collaboration_pattern_detection(self):
        """Test that repeated successful collaborations are detected."""
        fsm = FieldStateManager(use_compressed_registry=False)
        
        # Register two nodes
        fsm.register_node("node_a", ["capability_x"])
        fsm.register_node("node_b", ["capability_y"])
        
        # Form synapse
        fsm.form_synapse(
            source_node_id="node_a",
            target_node_id="node_b",
            purpose="test_collaboration",
            initial_weight=0.5,
            ethical_score=0.9,
            skip_ethics_check=True
        )
        
        # Record multiple successful collaborations
        for _ in range(5):
            fsm.record_synapse_usage("node_a", "node_b", success=True)
        
        # Detect patterns
        patterns = fsm.detect_patterns()
        
        # Should detect collaboration pattern
        assert len(patterns["collaboration"]) > 0
        
        collab_pattern = patterns["collaboration"][0]
        assert isinstance(collab_pattern, Pattern)
        assert collab_pattern.pattern_type == "collaboration"
        assert "node_a" in collab_pattern.involved_nodes
        assert "node_b" in collab_pattern.involved_nodes

    def test_field_coherence_calculation(self):
        """Test field coherence calculation with active nodes."""
        fsm = FieldStateManager(use_compressed_registry=False)
        
        # Register multiple nodes
        fsm.register_node("node_a", ["capability_x"])
        fsm.register_node("node_b", ["capability_y"])
        fsm.register_node("node_c", ["capability_z"])
        
        # Form some synapses
        fsm.form_synapse("node_a", "node_b", "test1", 0.5, 0.9, skip_ethics_check=True)
        fsm.form_synapse("node_b", "node_c", "test2", 0.5, 0.9, skip_ethics_check=True)
        
        # Record some activity
        fsm.record_synapse_usage("node_a", "node_b", success=True)
        fsm.record_synapse_usage("node_b", "node_c", success=True)
        
        # Calculate coherence
        coherence = fsm.get_field_coherence()
        
        assert coherence is not None
        assert 0.0 <= coherence.overall_score <= 1.0
        assert 0.0 <= coherence.synapse_efficiency <= 1.0
        assert 0.0 <= coherence.load_balance <= 1.0
        assert 0.0 <= coherence.pattern_diversity <= 1.0
        assert 0.0 <= coherence.organic_formation <= 1.0


@pytest.mark.integration
@pytest.mark.aurora
class TestPatternDetectionIntegration:
    """Integration tests for pattern detection in field dynamics."""

    def test_organic_synapse_formation_with_patterns(self):
        """Test that organic synapse formation integrates with pattern detection."""
        fsm = FieldStateManager(use_compressed_registry=False)
        
        # Register nodes with matching capabilities
        fsm.register_node("node_a", ["capability_x", "capability_y"])
        fsm.register_node("node_b", ["capability_y", "capability_z"])
        
        # Broadcast a need
        need = fsm.broadcast_need(
            source_node_id="node_a",
            need_id="test_need_001",
            required_capabilities=["capability_y"],
            description="Need help with capability_y",
            urgency=0.8
        )
        
        # Organic formation should happen
        synapse_id = fsm.organic_synapse_formation(
            signal_id=need.need_id,
            auto_form_top_match=True
        )
        
        if synapse_id:
            # Record usage
            fsm.record_synapse_usage("node_a", "node_b", success=True)
            
            # Pattern detector should have recorded
            assert len(fsm.pattern_detector.synapse_activations) > 0

    def test_pattern_recommendations_reflect_field_state(self):
        """Test that recommendations are generated based on field state."""
        fsm = FieldStateManager(use_compressed_registry=False)
        
        # Create a field with some activity
        fsm.register_node("node_a", ["capability_x"])
        fsm.register_node("node_b", ["capability_y"])
        fsm.register_node("node_c", ["capability_z"])
        
        # Form synapses and record activity
        fsm.form_synapse("node_a", "node_b", "test1", 0.5, 0.9, skip_ethics_check=True)
        fsm.form_synapse("node_b", "node_c", "test2", 0.5, 0.9, skip_ethics_check=True)
        
        for _ in range(3):
            fsm.record_synapse_usage("node_a", "node_b", success=True)
            fsm.record_synapse_usage("node_b", "node_c", success=True)
        
        # Get recommendations
        recommendations = fsm.get_pattern_recommendations()
        
        # Should have some recommendations (content varies based on coherence)
        assert isinstance(recommendations, list)
