"""
Memory Retrieval Module - Core Orchestration

Orchestrates retrieval operations combining store, cache, and scoring.
Integrates with DLP tracking and AuMemManager.
"""

from typing import List, Dict
import math
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MemoryRetrievalCore:
    """
    Core orchestration layer for memory retrieval.
    
    Combines storage, caching, and multi-factor scoring to provide
    intelligent memory retrieval with DLP compliance.
    """
    
    _instance = None
    
    def __init__(self, config):
        """
        Initialize core retrieval system.
        
        Args:
            config: MemoryRetrievalConfig instance
        """
        from modules.memory_retrieval.config import MemoryRetrievalConfig
        from modules.memory_retrieval.store import MemoryStore
        from modules.memory_retrieval.cache import MemoryCache
        
        self._config = config
        self._store = MemoryStore(config)
        self._cache = MemoryCache(config)
    
    @classmethod
    def get_instance(cls):
        """
        Get singleton instance of core retrieval system.
        
        Returns:
            MemoryRetrievalCore instance
        """
        if cls._instance is None:
            from modules.memory_retrieval.config import MemoryRetrievalConfig
            config = MemoryRetrievalConfig.from_env()
            config.validate()
            cls._instance = cls(config)
        return cls._instance
    
    def add_memory(self, context_id: str, content: str, metadata: dict) -> str:
        """
        Add memory with DLP tagging and anchor tracking.
        
        Args:
            context_id: Context isolation identifier
            content: Memory content
            metadata: Additional metadata
        
        Returns:
            Generated memory_id
        """
        # TODO: Add DLP tracking
        # context_tag = f"mrm:add:{context_id}"
        # tracker = NativeDLPTracker(context_tag=context_tag)
        
        # Ensure metadata has required fields
        if "importance" not in metadata:
            metadata["importance"] = 0.5
        if "created_at" not in metadata:
            metadata["created_at"] = datetime.now().isoformat()
        
        memory_id = self._store.add_memory(context_id, content, metadata)
        
        # Invalidate cache for this context
        self._cache.invalidate(f"query:{context_id}:")
        
        logger.info(f"Added memory {memory_id} to context {context_id}")
        return memory_id
    
    def retrieve_memories(self, context_id: str, query: str, top_k: int = 10) -> List[Dict]:
        """
        Main retrieval method combining cache, store, and scoring.
        
        Args:
            context_id: Context to search within
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of scored and ranked memory results
        """
        # Check cache first
        cache_key = self._cache.make_query_key(context_id, query, top_k)
        cached_results = self._cache.get(cache_key)
        
        if cached_results is not None:
            logger.debug(f"Cache hit for query: {query[:50]}")
            return cached_results
        
        # Cache miss - query store
        logger.debug(f"Cache miss for query: {query[:50]}")
        raw_results = self._store.query_memory(context_id, query, top_k)
        
        # Compute multi-factor scores
        scored_results = []
        for memory_id, relevance, content, metadata in raw_results:
            final_score = self._compute_score(relevance, metadata)
            
            result = {
                "id": memory_id,
                "score": final_score,
                "content": content,
                "metadata": metadata,
                "score_breakdown": {
                    "relevance": relevance,
                    "importance": metadata.get("importance", 0.5),
                    "recency": self._compute_recency_score(metadata.get("created_at", "")),
                    "cultural": metadata.get("cultural_score", 1.0),
                }
            }
            scored_results.append(result)
        
        # Re-sort by final score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Cache results
        self._cache.set(cache_key, scored_results)
        
        return scored_results
    
    def _compute_score(self, relevance: float, metadata: dict) -> float:
        """
        Compute final score from multiple factors.
        
        Args:
            relevance: Vector similarity score
            metadata: Memory metadata
        
        Returns:
            Final combined score
        """
        importance = metadata.get("importance", 0.5)
        recency = self._compute_recency_score(metadata.get("created_at", ""))
        cultural = metadata.get("cultural_score", 1.0)
        
        final_score = (
            self._config.weight_relevance * relevance +
            self._config.weight_importance * importance +
            self._config.weight_recency * recency +
            self._config.weight_cultural * cultural
        )
        
        return final_score
    
    def _compute_recency_score(self, created_at: str) -> float:
        """
        Calculate recency score with exponential decay.
        
        Args:
            created_at: ISO 8601 timestamp
        
        Returns:
            Recency score (0-1)
        """
        if not created_at:
            return 0.5
        
        try:
            created = datetime.fromisoformat(created_at)
            age_days = (datetime.now() - created).total_seconds() / 86400
            decay_rate = 0.1  # Configurable
            return math.exp(-decay_rate * age_days)
        except Exception:
            return 0.5
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics dict
        """
        return self._cache.get_stats()
