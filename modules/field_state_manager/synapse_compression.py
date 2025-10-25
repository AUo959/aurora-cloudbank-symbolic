"""
Synapse Registry Compression - RocketKV-inspired

The field remembers synapses across time. But memory is finite.
RocketKV's two-stage compression mirrors how natural memory works:
permanent storage for important connections, sparse attention for recent context.

This isn't just caching - it's how the field organizes its own memory.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=synapse_compression, symbolic_hash=MEMORY_ARCHITECTURE_v1
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Synapse:
    """
    A connection between nodes in the field.
    
    Synapses have weight (how strong), usage (how often), and ethical
    validation (whether the connection respects field geometry).
    """
    source_node: str
    target_node: str
    weight: float  # 0.0 → 1.0
    usage_count: int
    last_used: float  # timestamp
    ethical_score: float  # From geometric ethics validation
    success_rate: float  # How often this synapse leads to useful outcomes
    
    def importance(self) -> float:
        """
        Calculate synapse importance for compression decisions.
        
        Importance = weight × usage × ethical_score × success_rate × recency_boost
        
        Strong, frequently-used, ethical, successful synapses that were used
        recently are most important to keep.
        """
        recency_boost = 1.0 + (1.0 / (1.0 + time.time() - self.last_used))
        return (
            self.weight *
            (1.0 + self.usage_count) *
            self.ethical_score *
            self.success_rate *
            recency_boost
        )


@dataclass
class CompressionConfig:
    """Configuration for synapse registry compression."""
    
    # RocketKV-inspired two-stage budgets
    permanent_budget: int = 256  # Always keep top-256 synapses
    active_budget: int = 512     # Sparse attention on recent context
    
    # Eviction strategy
    eviction_strategy: str = "importance"  # "importance", "lru", "lfu"
    recomputation_on_access: bool = True   # Recompute archived when accessed
    
    # Archival compression
    enable_archival: bool = True
    archival_threshold_age: float = 3600.0  # 1 hour (seconds)


class CompressedSynapseRegistry:
    """
    Two-stage synapse registry with RocketKV-inspired compression.
    
    Stage 1: Permanent storage for high-importance synapses (top-k)
    Stage 2: Sparse attention for recent context
    Archive: Compressed historical patterns
    
    The field remembers more by organizing memory hierarchically,
    not by storing everything equally.
    """
    
    def __init__(self, config: Optional[CompressionConfig] = None):
        self.config = config or CompressionConfig()
        
        # Three-tier memory structure
        self.permanent: Dict[Tuple[str, str], Synapse] = {}  # Always in memory
        self.active: Dict[Tuple[str, str], Synapse] = {}     # Recent context
        self.archived: Dict[Tuple[str, str], dict] = {}      # Compressed patterns
        
        # Importance heap for permanent storage
        self._importance_heap: List[Tuple[float, Tuple[str, str]]] = []
        
    def observe_synapse(
        self,
        source: str,
        target: str,
        weight: float,
        ethical_score: float,
        success: bool = True
    ) -> None:
        """
        Observe a synapse activation in the field.
        
        Not "add to registry" - the field *observes* a connection forming.
        This updates importance, triggers compression decisions.
        """
        key = (source, target)
        now = time.time()
        
        # Update or create synapse
        if key in self.permanent:
            synapse = self.permanent[key]
            synapse.weight = (synapse.weight + weight) / 2  # Running average
            synapse.usage_count += 1
            synapse.last_used = now
            synapse.success_rate = (
                (synapse.success_rate * synapse.usage_count + (1.0 if success else 0.0))
                / (synapse.usage_count + 1)
            )
        elif key in self.active:
            synapse = self.active[key]
            synapse.weight = (synapse.weight + weight) / 2
            synapse.usage_count += 1
            synapse.last_used = now
            synapse.success_rate = (
                (synapse.success_rate * synapse.usage_count + (1.0 if success else 0.0))
                / (synapse.usage_count + 1)
            )
        else:
            # New synapse - starts in active memory
            synapse = Synapse(
                source_node=source,
                target_node=target,
                weight=weight,
                usage_count=1,
                last_used=now,
                ethical_score=ethical_score,
                success_rate=1.0 if success else 0.0
            )
            self.active[key] = synapse
        
        # Trigger compression if needed
        self._maybe_compress()
    
    def get_synapse(
        self,
        source: str,
        target: str
    ) -> Optional[Synapse]:
        """
        Retrieve synapse from memory (any tier).
        
        If in archive and recomputation enabled, bring back to active memory.
        """
        key = (source, target)
        
        # Check permanent first
        if key in self.permanent:
            synapse = self.permanent[key]
            synapse.last_used = time.time()
            synapse.usage_count += 1
            return synapse
        
        # Check active
        if key in self.active:
            synapse = self.active[key]
            synapse.last_used = time.time()
            synapse.usage_count += 1
            return synapse
        
        # Check archive
        if key in self.archived:
            if self.config.recomputation_on_access:
                # Recompute from compressed representation
                synapse = self._restore_from_archive(key)
                self.active[key] = synapse
                del self.archived[key]
                return synapse
            else:
                # Return compressed metadata (limited info)
                return None
        
        return None
    
    def get_field_context(
        self,
        max_synapses: Optional[int] = None
    ) -> List[Synapse]:
        """
        Get current field context (active synapses for attention).
        
        Returns permanent + active synapses, sorted by importance.
        This is what the field "sees" when making decisions.
        """
        all_active = list(self.permanent.values()) + list(self.active.values())
        all_active.sort(key=lambda s: s.importance(), reverse=True)
        
        if max_synapses is not None:
            return all_active[:max_synapses]
        return all_active
    
    def _maybe_compress(self) -> None:
        """
        Check if compression is needed and execute two-stage compression.
        
        Stage 1: Promote important synapses to permanent
        Stage 2: Evict low-importance from active
        Archive: Move old synapses to compressed storage
        """
        # Stage 1: Update permanent storage
        self._update_permanent()
        
        # Stage 2: Compress active memory
        if len(self.active) > self.config.active_budget:
            self._compress_active()
        
        # Archive: Move old synapses to compressed storage
        if self.config.enable_archival:
            self._archive_old_synapses()
    
    def _update_permanent(self) -> None:
        """
        Update permanent storage with top-k most important synapses.
        
        Permanent synapses are always in memory, never evicted.
        This is the field's "long-term memory" - core patterns that persist.
        """
        # Collect all synapses and their importance
        all_synapses = list(self.permanent.items()) + list(self.active.items())
        
        # Sort by importance
        all_synapses.sort(key=lambda item: item[1].importance(), reverse=True)
        
        # Keep top-k in permanent
        new_permanent = {}
        moved_to_active = []
        
        for i, (key, synapse) in enumerate(all_synapses):
            if i < self.config.permanent_budget:
                new_permanent[key] = synapse
            else:
                if key in self.permanent:
                    # Was permanent, now demoted to active
                    moved_to_active.append((key, synapse))
        
        # Update permanent storage
        self.permanent = new_permanent
        
        # Move demoted synapses to active
        for key, synapse in moved_to_active:
            if key not in self.active:
                self.active[key] = synapse
    
    def _compress_active(self) -> None:
        """
        Compress active memory by evicting low-importance synapses.
        
        Keep most recent and most important up to active_budget.
        Evicted synapses go to archive (if enabled) or are forgotten.
        """
        # Sort active by importance
        active_items = list(self.active.items())
        active_items.sort(key=lambda item: item[1].importance(), reverse=True)
        
        # Keep top active_budget, evict rest
        new_active = {}
        to_archive = []
        
        for i, (key, synapse) in enumerate(active_items):
            if i < self.config.active_budget:
                new_active[key] = synapse
            else:
                to_archive.append((key, synapse))
        
        self.active = new_active
        
        # Archive evicted synapses
        if self.config.enable_archival:
            for key, synapse in to_archive:
                self._archive_synapse(key, synapse)
    
    def _archive_old_synapses(self) -> None:
        """
        Move old, inactive synapses to compressed archive.
        
        Synapses that haven't been used recently and aren't important
        enough for permanent/active storage get compressed.
        """
        now = time.time()
        to_archive = []
        
        for key, synapse in list(self.active.items()):
            age = now - synapse.last_used
            if age > self.config.archival_threshold_age:
                # Old enough to archive
                to_archive.append((key, synapse))
        
        for key, synapse in to_archive:
            self._archive_synapse(key, synapse)
            del self.active[key]
    
    def _archive_synapse(self, key: Tuple[str, str], synapse: Synapse) -> None:
        """
        Archive a synapse with semantic compression.
        
        Store only essential pattern information, discard detailed history.
        Can be restored if accessed again.
        """
        self.archived[key] = {
            "source": synapse.source_node,
            "target": synapse.target_node,
            "avg_weight": synapse.weight,
            "total_usage": synapse.usage_count,
            "ethical_score": synapse.ethical_score,
            "success_rate": synapse.success_rate,
            "last_seen": synapse.last_used
        }
    
    def _restore_from_archive(self, key: Tuple[str, str]) -> Synapse:
        """
        Restore synapse from compressed archive.
        
        Recreates synapse from pattern metadata. Some detail is lost
        (exact history) but core pattern is preserved.
        """
        archived = self.archived[key]
        
        return Synapse(
            source_node=archived["source"],
            target_node=archived["target"],
            weight=archived["avg_weight"],
            usage_count=archived["total_usage"],
            last_used=time.time(),  # Reactivation time
            ethical_score=archived["ethical_score"],
            success_rate=archived["success_rate"]
        )
    
    def memory_stats(self) -> Dict[str, int]:
        """Get current memory usage statistics."""
        return {
            "permanent_count": len(self.permanent),
            "active_count": len(self.active),
            "archived_count": len(self.archived),
            "total_tracked": len(self.permanent) + len(self.active) + len(self.archived),
            "compression_ratio": (
                (len(self.permanent) + len(self.active) + len(self.archived))
                / max(len(self.permanent) + len(self.active), 1)
            )
        }
