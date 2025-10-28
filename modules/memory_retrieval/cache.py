"""
Memory Retrieval Module - Cache

TTL-based caching with genealogy tracking for query results.
"""

from typing import Optional, Any, Dict
import time
import hashlib


class MemoryCache:
    """
    TTL-based cache with hit/miss tracking.
    
    Caches query results to improve performance and tracks statistics
    for monitoring and optimization.
    """
    
    def __init__(self, config):
        """
        Initialize cache.
        
        Args:
            config: MemoryRetrievalConfig instance
        """
        self._config = config
        self._cache: Dict[str, dict] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }
    
    def get(self, cache_key: str) -> Optional[Any]:
        """
        Retrieve cached value if not expired.
        
        Args:
            cache_key: Cache key string
        
        Returns:
            Cached value or None if not found/expired
        """
        if cache_key not in self._cache:
            self._stats["misses"] += 1
            return None
        
        entry = self._cache[cache_key]
        
        # Check TTL expiration
        if time.time() > entry["expires_at"]:
            del self._cache[cache_key]
            self._stats["misses"] += 1
            self._stats["evictions"] += 1
            return None
        
        # Cache hit
        self._stats["hits"] += 1
        entry["hits"] += 1
        entry["last_accessed"] = time.time()
        
        return entry["value"]
    
    def set(self, cache_key: str, value: Any, ttl: Optional[int] = None):
        """
        Store value in cache with TTL.
        
        Args:
            cache_key: Cache key string
            value: Value to cache
            ttl: Time to live in seconds (uses config default if None)
        """
        if ttl is None:
            ttl = self._config.cache_ttl_seconds
        
        entry = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "last_accessed": time.time(),
            "hits": 0,
        }
        
        self._cache[cache_key] = entry
    
    def invalidate(self, pattern: str):
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match (simple prefix matching)
        """
        keys_to_delete = []
        for key in self._cache:
            if key.startswith(pattern):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._cache[key]
            self._stats["evictions"] += 1
    
    def get_stats(self) -> dict:
        """
        Return cache statistics.
        
        Returns:
            Dict with hits, misses, hit_rate, size, evictions
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0.0
        
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate,
            "size": len(self._cache),
        }
    
    def make_query_key(self, context_id: str, query: str, top_k: int) -> str:
        """
        Generate cache key for query.
        
        Args:
            context_id: Context identifier
            query: Query string
            top_k: Number of results
        
        Returns:
            Cache key string
        """
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:8]
        return f"query:{context_id}:{query_hash}:{top_k}"
