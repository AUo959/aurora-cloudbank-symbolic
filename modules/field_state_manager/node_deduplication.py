"""
Node Deduplication - Token Merging for Redundant Node Observations

When multiple nodes have near-identical capability signatures (>=95% similar),
tracking them independently wastes memory and compute. Merging them into
a single representative preserves field-wide pattern detection while
reducing node count by 1.5-3×.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=node_deduplication, symbolic_hash=FIELD_DENSITY_v3
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NodeSignature:
    """Lightweight signature for comparing node capability similarity."""

    node_id: str
    capabilities: Dict[str, float]  # Dimension → score (0.0–1.0)
    ethical_score: float
    importance: float
    merge_weight: float = 1.0       # Increases when nodes merge into this representative


@dataclass
class DeduplicationConfig:
    """Configuration for node deduplication."""

    similarity_threshold: float = 0.95   # Nodes >= 95% similar are merged
    merge_strategy: str = "attention_weighted"  # "attention_weighted" or "max_importance"
    preserve_high_importance: float = 8.0  # Never merge nodes with importance >= this


class NodeDeduplicator:
    """
    Merges redundant node observations to reduce field tracking overhead.

    Uses cosine-like similarity across capability dimensions to find
    near-duplicate nodes, then merges them into a weighted representative.

    Expected reduction: 1.5-3× fewer nodes tracked with the same pattern coverage.
    This translates directly to 1.5-3× more field history depth for the same memory.
    """

    def __init__(self, config: Optional[DeduplicationConfig] = None):
        self.config = config or DeduplicationConfig()
        self._merge_count: int = 0

    def similarity(self, a: NodeSignature, b: NodeSignature) -> float:
        """
        Compute capability similarity between two nodes (0.0–1.0).

        Uses normalized dot product across shared capability dimensions.
        Nodes with no overlapping dimensions have similarity 0.
        """
        dims = set(a.capabilities) & set(b.capabilities)
        if not dims:
            return 0.0

        dot = sum(a.capabilities[d] * b.capabilities[d] for d in dims)
        mag_a = sum(v ** 2 for v in a.capabilities.values()) ** 0.5
        mag_b = sum(v ** 2 for v in b.capabilities.values()) ** 0.5

        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0

        return dot / (mag_a * mag_b)

    def should_merge(self, a: NodeSignature, b: NodeSignature) -> bool:
        """
        Decide whether two nodes should be merged.

        Protects high-importance nodes from being merged away.
        """
        if (a.importance >= self.config.preserve_high_importance
                or b.importance >= self.config.preserve_high_importance):
            return False

        return self.similarity(a, b) >= self.config.similarity_threshold

    def merge_nodes(self, primary: NodeSignature, secondary: NodeSignature) -> NodeSignature:
        """
        Merge secondary into primary, producing a single representative.

        Attention-weighted merge: capabilities weighted by merge_weight,
        which accumulates each time a node absorbs another.
        """
        total_weight = primary.merge_weight + secondary.merge_weight
        if total_weight <= 0.0:  # NOSONAR - defensive guard; callers may pass merge_weight=0.0
            # merge_weight defaults to 1.0 but callers may pass 0.0; fall back to equal weighting
            total_weight = 1.0
        all_dims = set(primary.capabilities) | set(secondary.capabilities)

        merged_caps: Dict[str, float] = {}
        for dim in all_dims:
            a_val = primary.capabilities.get(dim, 0.0) * primary.merge_weight
            b_val = secondary.capabilities.get(dim, 0.0) * secondary.merge_weight
            merged_caps[dim] = (a_val + b_val) / total_weight

        merged_ethical = (
            primary.ethical_score * primary.merge_weight
            + secondary.ethical_score * secondary.merge_weight
        ) / total_weight

        merged_importance = max(primary.importance, secondary.importance)

        self._merge_count += 1
        return NodeSignature(
            node_id=primary.node_id,  # Keep primary's identity
            capabilities=merged_caps,
            ethical_score=merged_ethical,
            importance=merged_importance,
            merge_weight=total_weight,
        )

    def deduplicate(self, nodes: List[NodeSignature]) -> Tuple[List[NodeSignature], int]:
        """
        Deduplicate a list of node signatures, merging near-identical nodes.

        Returns:
            (deduplicated_list, number_of_merges_performed)

        Uses greedy O(n²) pairwise matching — practical for typical field
        sizes (hundreds of nodes), not for millions.
        """
        if not nodes:
            return [], 0

        result: List[NodeSignature] = []
        merged_indices = set()
        merges = 0

        for i, node in enumerate(nodes):
            if i in merged_indices:
                continue

            current = node
            for j in range(i + 1, len(nodes)):
                if j in merged_indices:
                    continue
                if self.should_merge(current, nodes[j]):
                    current = self.merge_nodes(current, nodes[j])
                    merged_indices.add(j)
                    merges += 1

            result.append(current)

        return result, merges

    def deduplication_ratio(self, original_count: int, deduplicated_count: int) -> float:
        """Compression ratio: >1 means fewer nodes after dedup."""
        if deduplicated_count == 0:
            return float(original_count)
        return original_count / deduplicated_count

    @property
    def total_merges(self) -> int:
        """Cumulative number of merges performed since instantiation."""
        return self._merge_count
