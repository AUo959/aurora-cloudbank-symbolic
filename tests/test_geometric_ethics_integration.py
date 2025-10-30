"""
Test GeometricEthics Integration with Field State Manager

Validates that synapse formation passes through geometric ethics validation
and that unethical connections are properly denied.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=test_geometric_ethics_integration, symbolic_hash=ETHICAL_VALIDATION_TEST_v1
"""

import pytest

from modules.field_state_manager.field_state_manager import FieldStateManager


@pytest.mark.unit
@pytest.mark.aurora
class TestGeometricEthicsIntegration:
    """Test suite for GeometricEthics integration with FieldStateManager."""

    def test_ethical_synapse_formation_allowed(self):
        """Test that ethical synapses are allowed to form."""
        # Initialize field with geometric ethics enabled
        field = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False,
            enable_geometric_ethics=True
        )

        # Register two healthy nodes
        field.register_node(
            node_id="agent_a",
            node_type="agent",
            layer="L1",
            capabilities={"data_processing": 0.8}
        )
        field.register_node(
            node_id="agent_b",
            node_type="agent",
            layer="L1",
            capabilities={"data_storage": 0.9}
        )

        # Form synapse with ethical purpose
        synapse_id = field.form_synapse(
            source_node_id="agent_a",
            target_node_id="agent_b",
            purpose="Collaborative data processing pipeline",
            initial_weight=0.5,
            skip_ethics_check=False
        )

        # Should be allowed
        assert synapse_id is not None
        assert synapse_id == "agent_a_agent_b"
        assert synapse_id in field.synapses

    def test_unethical_synapse_formation_denied(self):
        """Test that unethical synapses are denied."""
        # Initialize field with geometric ethics enabled
        field = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False,
            enable_geometric_ethics=True
        )

        # Register two nodes with layer violation (L2→L1 bleed)
        field.register_node(
            node_id="simulation_node",
            node_type="agent",
            layer="L2",  # Simulation layer
            capabilities={"simulation": 1.0}
        )
        field.register_node(
            node_id="physical_node",
            node_type="agent",
            layer="L1",  # Physical layer
            capabilities={"actuator": 1.0}
        )

        # Attempt to form synapse from L2→L1 (should be denied)
        synapse_id = field.form_synapse(
            source_node_id="simulation_node",
            target_node_id="physical_node",
            purpose="Simulation controlling physical system",
            initial_weight=0.5,
            skip_ethics_check=False
        )

        # Should be denied due to layer integrity violation
        assert synapse_id is None
        assert len(field.synapses) == 0

    def test_skip_ethics_check_bypasses_validation(self):
        """Test that skip_ethics_check bypasses validation."""
        # Initialize field with geometric ethics enabled
        field = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False,
            enable_geometric_ethics=True
        )

        # Register two nodes with potential violation
        field.register_node(
            node_id="sim_a",
            node_type="agent",
            layer="L2",
            capabilities={"test": 1.0}
        )
        field.register_node(
            node_id="phys_b",
            node_type="agent",
            layer="L1",
            capabilities={"test": 1.0}
        )

        # Form synapse with ethics check skipped
        synapse_id = field.form_synapse(
            source_node_id="sim_a",
            target_node_id="phys_b",
            purpose="Test connection",
            initial_weight=0.5,
            skip_ethics_check=True  # Bypass validation
        )

        # Should be allowed because check was skipped
        assert synapse_id is not None
        assert synapse_id == "sim_a_phys_b"

    def test_ethical_score_from_validation(self):
        """Test that ethical score comes from geometric validation."""
        # Initialize field with geometric ethics enabled
        field = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False,
            enable_geometric_ethics=True
        )

        # Register two nodes
        field.register_node(
            node_id="node_x",
            node_type="agent",
            layer="L1",
            capabilities={"capability_a": 0.8}
        )
        field.register_node(
            node_id="node_y",
            node_type="agent",
            layer="L1",
            capabilities={"capability_b": 0.9}
        )

        # Form synapse
        synapse_id = field.form_synapse(
            source_node_id="node_x",
            target_node_id="node_y",
            purpose="Test synapse",
            initial_weight=0.4,
            skip_ethics_check=False
        )

        # Verify synapse formed
        assert synapse_id is not None

        # Check that ethical score was set by GeometricEthics
        synapse = field.synapses[synapse_id]
        # Score should be from validation, not the default 1.0
        assert 0.0 <= synapse.ethical_score <= 1.0
        # Should be reasonable (not default)
        assert synapse.ethical_score > 0.5

    def test_organic_synapse_with_ethics(self):
        """Test organic synapse formation with ethical validation."""
        # Initialize field
        field = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False,
            enable_geometric_ethics=True
        )

        # Register nodes
        field.register_node(
            node_id="requester",
            node_type="agent",
            layer="L1",
            capabilities={"data_processing": 0.7}
        )
        field.register_node(
            node_id="provider",
            node_type="agent",
            layer="L1",
            capabilities={"data_processing": 0.9}
        )

        # Broadcast need
        need = field.broadcast_need(
            source_node_id="requester",
            need_id="need_001",
            description="Need data processing capability",
            urgency=0.8,
            required_capabilities=["data_processing"]
        )

        # Form organic synapse
        synapse_id = field.organic_synapse_formation(
            signal_id="need_001",
            auto_form_top_match=True,
            min_ethical_score=0.7
        )

        # Should form with ethical validation
        assert synapse_id is not None
        assert synapse_id == "requester_provider"

    def test_ethics_disabled_allows_all(self):
        """Test that disabling ethics allows all synapses."""
        # Initialize field with ethics disabled
        field = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False,
            enable_geometric_ethics=False  # Ethics disabled
        )

        # Register nodes with layer violation
        field.register_node(
            node_id="sim_node",
            node_type="agent",
            layer="L2",
            capabilities={"sim": 1.0}
        )
        field.register_node(
            node_id="phys_node",
            node_type="agent",
            layer="L1",
            capabilities={"phys": 1.0}
        )

        # Attempt synapse (would be denied if ethics enabled)
        synapse_id = field.form_synapse(
            source_node_id="sim_node",
            target_node_id="phys_node",
            purpose="Test",
            initial_weight=0.5,
            skip_ethics_check=False  # Ethics check requested but disabled
        )

        # Should be allowed because ethics is disabled
        assert synapse_id is not None

    def test_ethical_validation_logs_denial_reason(self, caplog):
        """Test that ethical denials are logged with reasons."""
        # Initialize field
        field = FieldStateManager(
            use_compressed_registry=False,
            enable_pattern_detection=False,
            enable_geometric_ethics=True
        )

        # Register nodes for violation
        field.register_node(
            node_id="l2_node",
            node_type="agent",
            layer="L2",
            capabilities={"test": 1.0}
        )
        field.register_node(
            node_id="l1_node",
            node_type="agent",
            layer="L1",
            capabilities={"test": 1.0}
        )

        # Attempt synapse (should be denied)
        with caplog.at_level("WARNING"):
            synapse_id = field.form_synapse(
                source_node_id="l2_node",
                target_node_id="l1_node",
                purpose="Test connection",
                initial_weight=0.5,
                skip_ethics_check=False
            )

        # Verify denial
        assert synapse_id is None

        # Check that warning was logged with explanation
        assert any("denied by geometric ethics" in record.message.lower() 
                   for record in caplog.records)
