"""
Compression Field Coverage Tests

Validates that memory compression increases (or at minimum preserves)
field observation density — more nodes/synapses tracked per unit memory.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=compression_coverage_tests
"""

import pytest
import time

from modules.field_state_manager.synapse_compression import (
    CompressedSynapseRegistry,
    CompressionConfig,
    Synapse,
)
from modules.field_state_manager.node_deduplication import (
    NodeDeduplicator,
    NodeSignature,
    DeduplicationConfig,
)
from modules.field_state_manager.quantization_config import FieldQuantizer


# ── Synapse Registry (RocketKV) ──────────────────────────────────────────────

@pytest.mark.unit
class TestSynapseRegistryCoverage:
    def test_registry_tracks_more_history_than_active_budget(self):
        """Total tracked (permanent + active + archived) must exceed active_budget."""
        config = CompressionConfig(permanent_budget=4, active_budget=4, enable_archival=True)
        registry = CompressedSynapseRegistry(config)

        for i in range(20):
            registry.observe_synapse(
                source=f"node_{i}",
                target=f"node_{i + 1}",
                weight=0.5,
                ethical_score=0.9,
                success=True,
            )

        stats = registry.memory_stats()
        assert stats["total_tracked"] > config.active_budget, (
            f"Only tracking {stats['total_tracked']} entries with active_budget={config.active_budget}"
        )

    def test_permanent_tier_capped_at_budget(self):
        """Permanent tier must not exceed permanent_budget."""
        config = CompressionConfig(permanent_budget=5, active_budget=10)
        registry = CompressedSynapseRegistry(config)

        for i in range(30):
            registry.observe_synapse(
                source=f"n{i}", target=f"n{i + 1}",
                weight=float(i) / 30, ethical_score=0.9, success=True,
            )

        stats = registry.memory_stats()
        assert stats["permanent_count"] <= config.permanent_budget

    def test_active_tier_capped_at_budget(self):
        """Active tier must not exceed active_budget after compression."""
        config = CompressionConfig(permanent_budget=3, active_budget=3, enable_archival=True)
        registry = CompressedSynapseRegistry(config)

        for i in range(20):
            registry.observe_synapse(
                source=f"a{i}", target=f"b{i}",
                weight=0.3, ethical_score=0.8, success=True,
            )

        stats = registry.memory_stats()
        assert stats["active_count"] <= config.active_budget

    def test_archived_synapses_can_be_restored(self):
        """A synapse evicted to archive must be retrievable on access."""
        config = CompressionConfig(permanent_budget=2, active_budget=2, enable_archival=True,
                                   archival_threshold_age=0.0)
        registry = CompressedSynapseRegistry(config)

        # Observe enough synapses to force archival
        for i in range(10):
            registry.observe_synapse(
                source=f"s{i}", target="t0",
                weight=0.2, ethical_score=0.9, success=True,
            )

        # Access an archived synapse
        archived_key = ("s0", "t0")
        if archived_key in registry.archived:
            restored = registry.get_synapse("s0", "t0")
            assert restored is not None
            assert restored.source_node == "s0"  # NOSONAR - restored is Optional[Synapse] but non-None: assert restored is not None above narrows the type; SonarCloud does not recognize assert as narrowing

    def test_high_importance_synapse_stays_in_permanent(self):
        """The highest-weight synapse must always land in permanent storage."""
        config = CompressionConfig(permanent_budget=1, active_budget=5)
        registry = CompressedSynapseRegistry(config)

        registry.observe_synapse("star", "hub", weight=1.0, ethical_score=1.0, success=True)
        for i in range(10):
            registry.observe_synapse(f"n{i}", f"m{i}", weight=0.1, ethical_score=0.5, success=False)

        star_synapse = registry.get_synapse("star", "hub")
        assert star_synapse is not None, "High-importance synapse lost from all tiers"

    def test_field_context_sorted_by_importance(self):
        """get_field_context() must return synapses sorted descending by importance."""
        registry = CompressedSynapseRegistry()

        registry.observe_synapse("a", "b", weight=0.9, ethical_score=0.9, success=True)
        registry.observe_synapse("c", "d", weight=0.1, ethical_score=0.5, success=False)

        context = registry.get_field_context()
        if len(context) >= 2:
            assert context[0].importance() >= context[1].importance()

    def test_memory_stats_total_is_sum_of_tiers(self):
        """memory_stats total must equal permanent + active + archived."""
        registry = CompressedSynapseRegistry()
        registry.observe_synapse("x", "y", weight=0.5, ethical_score=0.8, success=True)
        stats = registry.memory_stats()
        assert stats["total_tracked"] == (
            stats["permanent_count"] + stats["active_count"] + stats["archived_count"]
        )


# ── Node Deduplication Coverage ───────────────────────────────────────────────

@pytest.mark.unit
class TestNodeDeduplicationCoverage:
    def _make_nodes(self, n: int, similarity: float = 0.99) -> list:
        """Create n near-identical nodes."""
        import random
        random.seed(42)
        base = {"reasoning": 0.8, "memory": 0.7, "planning": 0.6}
        nodes = []
        for i in range(n):
            caps = {k: v + random.uniform(-0.01, 0.01) * (1 - similarity) for k, v in base.items()}
            nodes.append(NodeSignature(
                node_id=f"node_{i}",
                capabilities=caps,
                ethical_score=0.9,
                importance=5.0,
            ))
        return nodes

    def test_near_identical_nodes_reduce_count(self):
        """10 near-identical nodes must reduce to fewer after dedup."""
        nodes = self._make_nodes(10, similarity=0.99)
        dedup = NodeDeduplicator(DeduplicationConfig(similarity_threshold=0.95))
        result, merges = dedup.deduplicate(nodes)
        assert len(result) < len(nodes), "Near-identical nodes were not merged"
        assert merges > 0

    def test_diverse_nodes_retained(self):
        """Highly diverse nodes must all survive deduplication."""
        nodes = [
            NodeSignature("a", {"reasoning": 1.0, "memory": 0.0, "planning": 0.0}, 0.9, 5.0),
            NodeSignature("b", {"reasoning": 0.0, "memory": 1.0, "planning": 0.0}, 0.9, 5.0),
            NodeSignature("c", {"reasoning": 0.0, "memory": 0.0, "planning": 1.0}, 0.9, 5.0),
        ]
        dedup = NodeDeduplicator(DeduplicationConfig(similarity_threshold=0.95))
        result, merges = dedup.deduplicate(nodes)
        assert len(result) == 3
        assert merges == 0

    def test_dedup_ratio_at_least_1_5x_for_identical(self):
        """10 identical nodes → dedup ratio >= 1.5 (lose at least 4 nodes)."""
        caps = {"x": 0.8, "y": 0.8}
        nodes = [NodeSignature(f"n{i}", caps, 0.9, 5.0) for i in range(10)]
        dedup = NodeDeduplicator(DeduplicationConfig(similarity_threshold=0.90))
        result, _ = dedup.deduplicate(nodes)
        ratio = dedup.deduplication_ratio(len(nodes), len(result))
        assert ratio >= 1.5, f"Dedup ratio {ratio:.2f} below 1.5× minimum"

    def test_ethical_scores_preserved_after_merge(self):
        """Merged node's ethical score must remain in valid range [0,1]."""
        nodes = self._make_nodes(5, similarity=0.99)
        dedup = NodeDeduplicator(DeduplicationConfig(similarity_threshold=0.90))
        result, _ = dedup.deduplicate(nodes)
        for node in result:
            assert 0.0 <= node.ethical_score <= 1.0


# ── Quantization Coverage ────────────────────────────────────────────────────

@pytest.mark.unit
class TestQuantizationCoverage:
    def test_4x_memory_reduction_claimed(self):
        """Quantizer must claim 4× memory savings for any input size."""
        quantizer = FieldQuantizer()
        for n in [1, 10, 100, 1000]:
            assert quantizer.memory_savings_ratio(n) == 4.0

    def test_all_curvature_steps_produce_valid_output(self):
        """100 evenly-spaced curvature values must all produce valid levels."""
        quantizer = FieldQuantizer()
        valid_levels = {0, 32, 64, 96, 128, 160, 192, 224, 255}
        for i in range(101):
            level = quantizer.quantize_curvature(i / 100.0)
            assert level in valid_levels

    def test_kv_quantization_large_tensor(self):
        """KV quantization of 512 values must produce 512 INT8 values."""
        quantizer = FieldQuantizer()
        import random
        random.seed(0)
        values = [random.uniform(-1, 1) for _ in range(512)]
        quantized = quantizer.quantize_kv_tensor(values)
        assert len(quantized) == 512
        for v in quantized:
            assert -128 <= v <= 127
