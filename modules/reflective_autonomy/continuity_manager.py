"""Continuity manager backed by the Aurora memory optimizer."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from src.aurora_fusion.memory import AuroraMemoryOptimizer, MemoryStatus
from src.core.native_symbolic_anchor import NativeSymbolicCPUAnchor


class ContinuityManager:
    """Thin continuity facade over the doctrine-aware memory optimizer."""

    def __init__(
        self,
        anchor: Optional[NativeSymbolicCPUAnchor] = None,
        symbolic_dim: int = 512,
    ):
        self.memory_optimizer = AuroraMemoryOptimizer(anchor=anchor, symbolic_dim=symbolic_dim)

    def record_event(
        self,
        owner: str,
        content: str,
        *,
        importance: float = 5.0,
        layer: str = "L2",
        source: str = "continuity.event",
        tags: Optional[Sequence[str]] = None,
        anchor_ids: Optional[Sequence[str]] = None,
        truth_confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store an event in continuity memory."""
        record = self.memory_optimizer.remember(
            owner=owner,
            content=content,
            importance=importance,
            layer=layer,
            source=source,
            tags=tags,
            anchor_ids=anchor_ids,
            truth_confidence=truth_confidence,
            metadata=metadata,
        )
        return record.to_dict()

    def retrieve_context(self, owner: str, query: str, *, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return ranked continuity context for an owner."""
        return [hit.to_dict() for hit in self.memory_optimizer.retrieve_context(owner, query, top_k=top_k)]

    def run_maintenance(self, owner: Optional[str] = None) -> Dict[str, Any]:
        """Apply decay, compression, and archival policy."""
        return self.memory_optimizer.run_maintenance(owner)

    def lock_memory(self, owner: str, anchor_id: Optional[str] = None) -> int:
        """Freeze an owner or anchor lineage."""
        return self.memory_optimizer.lock_memory(owner, anchor_id=anchor_id, locked=True)

    def unlock_memory(self, owner: str, anchor_id: Optional[str] = None) -> int:
        """Release a previously locked owner or anchor lineage."""
        return self.memory_optimizer.lock_memory(owner, anchor_id=anchor_id, locked=False)

    def queue_anchor(self, owner: str, anchor_id: str, reason: str) -> Dict[str, Any]:
        """Register a queue anchor marker."""
        return self.memory_optimizer.queue_anchor(owner, anchor_id, reason).to_dict()

    def build_report(self, owner: Optional[str] = None) -> Dict[str, Any]:
        """Return a sealed continuity report."""
        return self.memory_optimizer.build_continuity_snapshot(owner)

    @property
    def doctrine(self) -> Dict[str, Any]:
        """Expose active continuity doctrine."""
        return self.memory_optimizer.doctrine.to_dict()


__all__ = ["ContinuityManager", "MemoryStatus"]
