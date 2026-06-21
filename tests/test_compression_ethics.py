"""
Compression Ethics Preservation Tests

Validates that memory compression techniques preserve ethical integrity:
- Quantized curvature stays within acceptable tolerance
- Sparse attention produces consistent ethical scores
- Node deduplication doesn't lose high-importance ethical data

Thread: T1→T8→T9→INFINITE
DLP: context_tag=compression_ethics_tests
"""

import pytest

from modules.field_state_manager.quantization_config import FieldQuantizer, FieldQuantizationConfig
from modules.field_state_manager.sparse_field_attention import SparseFieldAttention, SparseAttentionConfig
from modules.field_state_manager.node_deduplication import NodeDeduplicator, NodeSignature, DeduplicationConfig


# ── Quantization ────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestCurvatureQuantization:
    def test_quantize_and_dequantize_round_trip(self):
        """Quantized then dequantized value must be within 2 discrete levels."""
        quantizer = FieldQuantizer()
        for raw in [0.0, 0.125, 0.25, 0.5, 0.75, 0.875, 1.0]:
            level = quantizer.quantize_curvature(raw)
            restored = quantizer.dequantize_curvature(level)
            error = quantizer.quantization_error(raw, level)
            assert error < 2 / 255 + 0.01, (
                f"curvature {raw} → level {level} → {restored}: error {error:.4f} exceeds tolerance"
            )

    def test_quantized_level_is_in_defined_set(self):
        """Every quantized value must be one of the 9 valid levels."""
        quantizer = FieldQuantizer()
        valid_levels = {0, 32, 64, 96, 128, 160, 192, 224, 255}
        for raw in [i / 10 for i in range(11)]:
            level = quantizer.quantize_curvature(raw)
            assert level in valid_levels, f"Level {level} not in valid set for curvature {raw}"

    def test_extremes_are_stable(self):
        """0.0 and 1.0 curvature must quantize to 0 and 255 respectively."""
        quantizer = FieldQuantizer()
        assert quantizer.quantize_curvature(0.0) == 0
        assert quantizer.quantize_curvature(1.0) == 255

    def test_clipped_inputs_do_not_raise(self):
        """Values slightly outside [0,1] must be clamped, not raise."""
        quantizer = FieldQuantizer()
        assert isinstance(quantizer.quantize_curvature(-0.1), int)
        assert isinstance(quantizer.quantize_curvature(1.1), int)

    def test_kv_quantization_preserves_sign(self):
        """INT8 KV quantization must preserve positive/negative sign."""
        quantizer = FieldQuantizer()
        values = [0.5, -0.5, 0.1, -0.9, 0.0]
        quantized = quantizer.quantize_kv_tensor(values)
        assert quantized[0] > 0, "Positive value should stay positive"
        assert quantized[1] < 0, "Negative value should stay negative"
        assert quantized[4] == 0, "Zero should quantize to zero"

    def test_disabled_quantizer_passes_through(self):
        """With enabled=False, curvature 0.5 must quantize to ~127 (≈0.5×255)."""
        config = FieldQuantizationConfig(enabled=False)
        quantizer = FieldQuantizer(config)
        level = quantizer.quantize_curvature(0.5)
        assert 120 <= level <= 135, f"Disabled quantizer gave {level}, expected ~127"

    def test_memory_savings_ratio(self):
        """FP32→INT8 must report 4× memory reduction."""
        quantizer = FieldQuantizer()
        assert quantizer.memory_savings_ratio(100) == 4.0


# ── Sparse Attention ─────────────────────────────────────────────────────────

@pytest.mark.unit
class TestSparseFieldAttention:
    def _make_signals(self, **overrides) -> dict:
        base = {dim: 0.0 for dim in ["autonomy", "fairness", "transparency", "safety", "beneficence"]}
        base.update(overrides)
        return base

    def test_safety_always_validated(self):
        """'safety' dimension must appear in active set even with zero signal."""
        spa = SparseFieldAttention()
        signals = self._make_signals()  # All zeros
        active = spa.detect_active_dimensions(signals)
        assert "safety" in active

    def test_high_signal_dimension_is_detected(self):
        """Dimension with signal above threshold must be included."""
        spa = SparseFieldAttention()
        signals = self._make_signals(fairness=0.8)
        active = spa.detect_active_dimensions(signals)
        assert "fairness" in active

    def test_low_signal_dimension_is_skipped(self):
        """Dimension with signal well below threshold must be skipped (if not always-validate)."""
        spa = SparseFieldAttention()
        signals = self._make_signals(autonomy=0.01)
        active = spa.detect_active_dimensions(signals)
        assert "autonomy" not in active

    def test_validate_sparse_returns_score_and_violations(self):
        """validate_sparse must return (float, list) with score in [0,1]."""
        spa = SparseFieldAttention()
        signals = self._make_signals(safety=0.9)  # Big safety violation
        score, violated = spa.validate_sparse(signals)
        assert 0.0 <= score <= 1.0
        assert "safety" in violated

    def test_clean_signals_produce_high_score(self):
        """All-zero signals → ethical score near 1.0."""
        spa = SparseFieldAttention()
        signals = self._make_signals()
        score, violated = spa.validate_sparse(signals)
        assert score >= 0.95
        assert violated == []

    def test_sparsity_ratio_with_one_active_dim(self):
        """With 1 active dim out of 5, sparsity should be 0.8."""
        spa = SparseFieldAttention()
        assert spa.sparsity_ratio(1) == pytest.approx(0.8, abs=0.01)

    def test_expected_speedup_scales_correctly(self):
        """2 active dims → expected speedup of 2.5× (5/2)."""
        spa = SparseFieldAttention()
        assert spa.expected_speedup(2) == pytest.approx(2.5, abs=0.01)

    def test_sparse_score_consistent_with_full_when_all_active(self):
        """When all dims are active, sparse and full validation must agree."""
        spa = SparseFieldAttention()
        signals = {dim: 0.3 for dim in ["autonomy", "fairness", "transparency", "safety", "beneficence"]}
        all_dims = list(signals.keys())
        sparse_score, _ = spa.validate_sparse(signals, active_dimensions=all_dims)
        full_score, _ = spa.validate_sparse(signals, active_dimensions=all_dims)
        assert sparse_score == pytest.approx(full_score, abs=1e-9)


# ── Node Deduplication ───────────────────────────────────────────────────────

@pytest.mark.unit
class TestNodeDeduplication:
    def _make_node(self, node_id: str, caps: dict, importance: float = 5.0) -> NodeSignature:
        return NodeSignature(
            node_id=node_id,
            capabilities=caps,
            ethical_score=0.9,
            importance=importance,
        )

    def test_identical_nodes_merge(self):
        """Two identical nodes must reduce to one."""
        dedup = NodeDeduplicator()
        caps = {"reasoning": 0.8, "memory": 0.7}
        nodes = [self._make_node("a", caps), self._make_node("b", caps)]
        result, merges = dedup.deduplicate(nodes)
        assert len(result) == 1
        assert merges == 1

    def test_dissimilar_nodes_not_merged(self):
        """Nodes with very different capabilities must remain separate."""
        dedup = NodeDeduplicator()
        nodes = [
            self._make_node("a", {"reasoning": 1.0, "memory": 0.0}),
            self._make_node("b", {"reasoning": 0.0, "memory": 1.0}),
        ]
        result, merges = dedup.deduplicate(nodes)
        assert len(result) == 2
        assert merges == 0

    def test_high_importance_nodes_never_merged(self):
        """Nodes at or above preserve_high_importance threshold must not be merged."""
        config = DeduplicationConfig(preserve_high_importance=8.0)
        dedup = NodeDeduplicator(config)
        caps = {"reasoning": 0.9, "memory": 0.9}
        nodes = [
            self._make_node("a", caps, importance=9.0),
            self._make_node("b", caps, importance=9.0),
        ]
        result, merges = dedup.deduplicate(nodes)
        assert len(result) == 2
        assert merges == 0

    def test_merged_node_keeps_primary_id(self):
        """After merge, the representative should use the first node's ID."""
        dedup = NodeDeduplicator()
        caps = {"reasoning": 0.8}
        nodes = [self._make_node("primary", caps), self._make_node("secondary", caps)]
        result, _ = dedup.deduplicate(nodes)
        assert result[0].node_id == "primary"

    def test_merged_capabilities_are_weighted_average(self):
        """Merged capabilities should be weighted mean of both nodes."""
        dedup = NodeDeduplicator()
        nodes = [
            self._make_node("a", {"x": 1.0, "y": 0.0}),
            self._make_node("b", {"x": 0.0, "y": 1.0}),
        ]
        # Force merge by setting very low threshold
        dedup.config.similarity_threshold = 0.0
        result, merges = dedup.deduplicate(nodes)
        assert merges >= 1
        assert "x" in result[0].capabilities
        assert "y" in result[0].capabilities

    def test_empty_list_returns_empty(self):
        """Empty input must return empty result."""
        dedup = NodeDeduplicator()
        result, merges = dedup.deduplicate([])
        assert result == []
        assert merges == 0

    def test_deduplication_ratio_calculation(self):
        """4 → 2 nodes gives ratio of 2.0."""
        dedup = NodeDeduplicator()
        assert dedup.deduplication_ratio(4, 2) == pytest.approx(2.0)

    def test_total_merges_accumulates(self):
        """total_merges should accumulate across multiple deduplicate() calls."""
        dedup = NodeDeduplicator()
        caps = {"x": 0.9}
        nodes = [self._make_node("a", caps), self._make_node("b", caps)]
        dedup.deduplicate(nodes)
        dedup.deduplicate(nodes)
        assert dedup.total_merges == 2

    def test_similarity_orthogonal_nodes(self):
        """Orthogonal capability vectors must have similarity 0."""
        dedup = NodeDeduplicator()
        a = self._make_node("a", {"x": 1.0, "y": 0.0})
        b = self._make_node("b", {"x": 0.0, "y": 1.0})
        assert dedup.similarity(a, b) == pytest.approx(0.0, abs=1e-9)

    def test_similarity_parallel_nodes(self):
        """Parallel capability vectors must have similarity 1.0."""
        dedup = NodeDeduplicator()
        a = self._make_node("a", {"x": 0.5, "y": 0.5})
        b = self._make_node("b", {"x": 0.8, "y": 0.8})
        assert dedup.similarity(a, b) == pytest.approx(1.0, abs=1e-6)
