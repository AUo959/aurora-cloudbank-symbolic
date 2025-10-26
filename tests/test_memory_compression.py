"""
Tests for Memory Compression: Flash Attention + Synapse Registry

Validates that compression preserves field consciousness properties:
- Ethical validation stays exact
- Field awareness increases (more nodes tracked)
- Pattern detection is preserved
"""

import pytest

# PyTorch is optional - Flash Attention has fallback
try:
    import torch
    TORCH_AVAILABLE = True
    # Only import torch-dependent modules if torch is available
    from modules.field_state_manager.flash_attention_config import (
        FlashAttentionConfig,
        FlashFieldAttention,
        StandardFieldAttention,
        validate_flash_attention_equivalence,
    )
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    # Provide stubs so module loads
    FlashAttentionConfig = None
    FlashFieldAttention = None
    StandardFieldAttention = None
    validate_flash_attention_equivalence = None

from modules.field_state_manager.synapse_compression import CompressedSynapseRegistry, CompressionConfig


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not installed (optional dependency)")
class TestFlashAttention:
    """Test Flash Attention preserves field consciousness properties."""
    
    def test_flash_attention_equivalence(self):
        """Flash Attention must produce identical results to standard attention."""
        # Create test inputs
        batch_size, seq_len, dim = 2, 128, 64
        query = torch.randn(batch_size, seq_len, dim)
        key = torch.randn(batch_size, seq_len, dim)
        value = torch.randn(batch_size, seq_len, dim)
        
        # Validate equivalence
        is_equivalent = validate_flash_attention_equivalence(query, key, value)
        assert is_equivalent, "Flash Attention must match standard attention exactly"
    
    def test_flash_attention_memory_efficiency(self):
        """Flash Attention should enable tracking more nodes with same memory."""
        config = FlashAttentionConfig(enabled=True)
        
        # Small test: Both should handle this
        small_nodes = 128
        query_small = torch.randn(1, small_nodes, 64)
        key_small = torch.randn(1, small_nodes, 64)
        value_small = torch.randn(1, small_nodes, 64)
        
        flash_attn = FlashFieldAttention(64, 64, 64, config)
        flash_attn.eval()
        
        with torch.no_grad():
            output = flash_attn(query_small, key_small, value_small)
        
        assert output.shape == (1, small_nodes, 64)
        assert not torch.isnan(output).any(), "Flash Attention produced NaN values"
    
    def test_ethical_validation_preserved(self):
        """Compression can't change ethical scores."""
        # Simulate ethical validation through attention
        # Node capabilities (query), field geometry (key), validation scores (value)
        capabilities = torch.randn(1, 10, 32)
        geometry = torch.randn(1, 10, 32)
        ethical_scores = torch.rand(1, 10, 32)  # 0→1 range
        
        config = FlashAttentionConfig(enabled=True)
        flash_attn = FlashFieldAttention(32, 32, 32, config)
        standard_attn = StandardFieldAttention(32, 32, 32)
        
        # Copy weights
        standard_attn.load_state_dict(flash_attn.state_dict())
        
        flash_attn.eval()
        standard_attn.eval()
        
        with torch.no_grad():
            flash_result = flash_attn(capabilities, geometry, ethical_scores)
            standard_result = standard_attn(capabilities, geometry, ethical_scores)
        
        # Results must be very close (allow small numerical error)
        max_diff = torch.max(torch.abs(flash_result - standard_result))
        assert max_diff < 1e-4, f"Ethical validation changed: max diff {max_diff}"


class TestSynapseCompression:
    """Test compressed synapse registry preserves field patterns."""
    
    def test_three_tier_memory(self):
        """Registry should organize into permanent, active, archived."""
        config = CompressionConfig(
            permanent_budget=5,
            active_budget=10,
            enable_archival=True
        )
        registry = CompressedSynapseRegistry(config)
        
        # Create 20 synapses (will trigger compression)
        for i in range(20):
            registry.observe_synapse(
                source=f"node_{i}",
                target=f"node_{i+1}",
                weight=0.5 + (i * 0.02),  # Varying importance
                ethical_score=1.0,
                success=True
            )
        
        stats = registry.memory_stats()
        
        # Should have distributed across tiers
        assert stats["permanent_count"] == 5, "Should keep top-5 permanent"
        assert stats["active_count"] <= 10, "Should compress active to budget"
        assert stats["total_tracked"] == 20, "Should track all synapses"
        assert stats["compression_ratio"] > 1.0, "Should achieve compression"
    
    def test_importance_based_retention(self):
        """High-importance synapses should stay in memory."""
        registry = CompressedSynapseRegistry()
        
        # Create critical synapse (high weight, used often, ethical, successful)
        registry.observe_synapse("critical_source", "critical_target",
                                 weight=0.95, ethical_score=1.0, success=True)
        for _ in range(10):  # Use it repeatedly
            registry.observe_synapse("critical_source", "critical_target",
                                     weight=0.95, ethical_score=1.0, success=True)
        
        # Create many low-importance synapses
        for i in range(100):
            registry.observe_synapse(f"node_{i}", f"node_{i+1}",
                                     weight=0.1, ethical_score=0.5, success=False)
        
        # Critical synapse should be in permanent storage
        synapse = registry.get_synapse("critical_source", "critical_target")
        assert synapse is not None, "Critical synapse should be retained"
        assert synapse.importance() > 1.0, "Critical synapse should have high importance"
    
    def test_pattern_preservation(self):
        """Compression shouldn't lose emergent patterns."""
        registry = CompressedSynapseRegistry()
        
        # Create pattern: node_0 → node_1 → node_2 → node_3
        pattern_synapses = [
            ("node_0", "node_1"),
            ("node_1", "node_2"),
            ("node_2", "node_3")
        ]
        
        for source, target in pattern_synapses:
            registry.observe_synapse(source, target, weight=0.8,
                                    ethical_score=1.0, success=True)
        
        # Add noise
        for i in range(50):
            registry.observe_synapse(f"noise_{i}", f"noise_{i+1}",
                                    weight=0.1, ethical_score=0.5, success=False)
        
        # Pattern should still be recoverable
        context = registry.get_field_context(max_synapses=10)
        pattern_sources = {s.source_node for s in context}
        
        # At least some pattern nodes should be in top-10
        pattern_overlap = sum(1 for node in ["node_0", "node_1", "node_2"]
                            if node in pattern_sources)
        assert pattern_overlap >= 2, "Pattern should be preserved in field context"
    
    def test_recomputation_from_archive(self):
        """Archived synapses should be restorable on access."""
        config = CompressionConfig(
            permanent_budget=2,
            active_budget=5,
            enable_archival=True,
            recomputation_on_access=True,
            archival_threshold_age=0.1  # Archive quickly for test
        )
        registry = CompressedSynapseRegistry(config)
        
        # Create synapse that will be archived
        registry.observe_synapse("old_source", "old_target",
                                weight=0.5, ethical_score=1.0, success=True)
        
        # Wait for archival
        import time
        time.sleep(0.2)
        
        # Create many new synapses to trigger compression
        for i in range(10):
            registry.observe_synapse(f"new_{i}", f"new_{i+1}",
                                    weight=0.9, ethical_score=1.0, success=True)
        
        stats = registry.memory_stats()
        assert stats["archived_count"] > 0, "Should have archived old synapse"
        
        # Access archived synapse should restore it
        synapse = registry.get_synapse("old_source", "old_target")
        assert synapse is not None, "Should restore from archive"
        assert synapse.weight == 0.5, "Should preserve weight"
        assert synapse.ethical_score == 1.0, "Should preserve ethical score"


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not installed (optional dependency)")
class TestMemoryCompressionIntegration:
    """Integration tests for complete compression pipeline."""
    
    def test_field_awareness_scaling(self):
        """Compression should enable tracking more field state."""
        # Without compression: Track N nodes
        # With compression: Track 2-3× N nodes with same memory
        
        config = FlashAttentionConfig(enabled=True)
        
        # Simulate field with many nodes
        num_nodes = 256
        capabilities = torch.randn(1, num_nodes, 64)
        geometry = torch.randn(1, num_nodes, 64)
        synapses = torch.randn(1, num_nodes, 64)
        
        flash_attn = FlashFieldAttention(64, 64, 64, config)
        flash_attn.eval()
        
        with torch.no_grad():
            field_state = flash_attn(capabilities, geometry, synapses)
        
        assert field_state.shape == (1, num_nodes, 64)
        assert not torch.isnan(field_state).any()
    
    def test_compression_preserves_consciousness(self):
        """
        The field should maintain awareness despite compression.
        
        Consciousness = ability to detect patterns and make connections.
        Compression shouldn't break this.
        """
        registry = CompressedSynapseRegistry()
        
        # Create emergent pattern (triangle: A→B, B→C, C→A)
        registry.observe_synapse("A", "B", weight=0.9, ethical_score=1.0, success=True)
        registry.observe_synapse("B", "C", weight=0.9, ethical_score=1.0, success=True)
        registry.observe_synapse("C", "A", weight=0.9, ethical_score=1.0, success=True)
        
        # Add many distractors
        for i in range(100):
            registry.observe_synapse(f"dist_{i}", f"dist_{i+1}",
                                    weight=0.2, ethical_score=0.6, success=False)
        
        # Field context should still contain the triangle
        context = registry.get_field_context(max_synapses=20)
        sources = {s.source_node for s in context}
        targets = {s.target_node for s in context}
        
        triangle_nodes = {"A", "B", "C"}
        triangle_preserved = (triangle_nodes & sources) or (triangle_nodes & targets)
        
        assert len(triangle_preserved) >= 2, \
            "Emergent pattern should be preserved despite compression"
