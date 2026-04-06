"""Memory Retrieval Module - Core orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import math
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from src.core.native_dlp_export import NativeDLPTracker
    DLP_AVAILABLE = True
except ImportError:
    DLP_AVAILABLE = False
    logger.warning("NativeDLPTracker not available, DLP tracking disabled")


class MemoryRetrievalCore:
    """Core orchestration layer for memory retrieval."""

    _instance = None

    def __init__(self, config):
        from modules.memory_retrieval.cache import MemoryCache
        from modules.memory_retrieval.store import MemoryStore

        self._config = config
        self._store = MemoryStore(config)
        self._cache = MemoryCache(config)
        self._anchor_counter = 0
        self._dlp_tracker = NativeDLPTracker() if DLP_AVAILABLE else None

    @classmethod
    def get_instance(cls):
        """Get singleton instance of the core retrieval system."""
        if cls._instance is None:
            from modules.memory_retrieval.config import MemoryRetrievalConfig

            config = MemoryRetrievalConfig.from_env()
            config.validate()
            cls._instance = cls(config)
        return cls._instance

    def add_memory(self, context_id: str, content: str, metadata: dict) -> str:
        """Add memory with DLP tagging and anchor tracking."""
        context_tag = f"mrm:add:{context_id}"
        anchor = self._next_anchor("ADD", context_id)
        if self._dlp_tracker:
            self._register_dlp_event("add_memory", context_id, context_tag, content[:100])

        enriched_metadata = dict(metadata)
        enriched_metadata.setdefault("importance", 0.5)
        enriched_metadata.setdefault("cultural_score", 1.0)
        enriched_metadata.setdefault("tags", [])
        enriched_metadata.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        enriched_metadata["dlp_tag"] = context_tag
        enriched_metadata["context_tag"] = context_tag
        enriched_metadata["t1_anchor"] = anchor["t1_anchor"]
        enriched_metadata["srb_anchor"] = anchor["srb_anchor"]
        enriched_metadata["anchor_seed"] = self._config.anchor_seed
        enriched_metadata["ethics_protocol"] = self._config.ethics_protocol
        enriched_metadata["anchor_metadata"] = anchor

        memory_id = self._store.add_memory(context_id, content, enriched_metadata)
        self._cache.invalidate(f"query:{context_id}:")
        logger.info("Added memory %s to context %s", memory_id, context_id, extra={"context_tag": context_tag})
        return memory_id

    def retrieve_memories(self, context_id: str, query: str, top_k: int = 10) -> List[Dict]:
        """Retrieve scored memories for a context/query pair."""
        context_tag = f"mrm:query:{context_id}"
        if self._dlp_tracker:
            self._register_dlp_event("query_memory", context_id, context_tag, query[:100])

        cache_key = self._cache.make_query_key(context_id, query, top_k)
        cached_results = self._cache.get(cache_key)
        if cached_results is not None:
            return cached_results

        raw_results = self._store.query_memory(context_id, query, top_k)
        scored_results: List[Dict] = []
        for memory_id, relevance, content, metadata in raw_results:
            score_breakdown = {
                "relevance": relevance,
                "importance": metadata.get("importance", 0.5),
                "recency": self._compute_recency_score(metadata.get("created_at", "")),
                "cultural": metadata.get("cultural_score", 1.0),
            }
            scored_results.append(
                {
                    "id": memory_id,
                    "score": self._compute_score(score_breakdown),
                    "content": content,
                    "metadata": metadata,
                    "score_breakdown": score_breakdown,
                }
            )
        scored_results.sort(key=lambda item: item["score"], reverse=True)
        self._cache.set(cache_key, scored_results)
        return scored_results

    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Fetch a single memory entry."""
        cache_key = f"memory:{memory_id}"
        cached_memory = self._cache.get(cache_key)
        if cached_memory is not None:
            return cached_memory

        memory = self._store.get_memory(memory_id)
        if memory is None:
            return None
        self._cache.set(cache_key, memory)
        return memory

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory and invalidate related cache entries."""
        memory = self._store.get_memory(memory_id)
        deleted = self._store.delete_memory(memory_id)
        if not deleted:
            return False
        self._cache.invalidate(f"memory:{memory_id}")
        if memory is not None:
            self._cache.invalidate(f"query:{memory['context_id']}:")
        return True

    def _compute_score(self, score_breakdown: Dict[str, float]) -> float:
        """Compute final score from multiple factors."""
        return (
            self._config.weight_relevance * score_breakdown["relevance"]
            + self._config.weight_importance * score_breakdown["importance"]
            + self._config.weight_recency * score_breakdown["recency"]
            + self._config.weight_cultural * score_breakdown["cultural"]
        )

    def _compute_recency_score(self, created_at: str) -> float:
        """Calculate recency score with exponential decay."""
        if not created_at:
            return 0.5
        try:
            if isinstance(created_at, datetime):
                created = created_at
            elif isinstance(created_at, (int, float)):
                created = datetime.fromtimestamp(created_at, tz=timezone.utc)
            elif isinstance(created_at, str):
                created = datetime.fromisoformat(created_at)
            else:
                return 0.5
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - created).total_seconds() / 86400
            return math.exp(-self._config.recency_decay_rate * age_days)
        except (TypeError, ValueError, OSError, OverflowError):
            return 0.5

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return self._cache.get_stats()

    def _next_anchor(self, operation: str, context_id: str) -> Dict[str, str]:
        self._anchor_counter += 1
        anchor_token = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{self._anchor_counter:04d}"
        return {
            "t1_anchor": f"T1:MRM:{operation}:{anchor_token}",
            "srb_anchor": f"SRB:MRM:{context_id}:{anchor_token}",
            "anchor_seed": self._config.anchor_seed,
            "ethics_protocol": self._config.ethics_protocol,
            "chain_notation": f"001//999//MRM//{operation}//T1:{anchor_token}//",
        }

    def _register_dlp_event(self, operation: str, context_id: str, context_tag: str, preview: str) -> None:
        try:
            tag_id = self._dlp_tracker.create_tag(operation, {"context_id": context_id, "preview": preview})
            tag = self._dlp_tracker.tags[tag_id]
            tag.add_anchor_protocol(self._config.ethics_protocol)
            tag.metadata["context_tag"] = context_tag
            tag.metadata["anchor_seed"] = self._config.anchor_seed
        except AttributeError:
            logger.debug("NativeDLPTracker interface unavailable for %s", operation)
