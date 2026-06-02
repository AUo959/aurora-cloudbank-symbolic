"""
Memory Retrieval Module - Cache

TTL-based caching with genealogy tracking for query results.

Bounded by a configurable ``max_size`` with LRU eviction so that long-running
processes and high-cardinality query inputs cannot grow the cache without
bound. Cold entries that expire without ever being read back are reclaimed by
a periodic ``clear_expired`` sweep triggered every N ``set`` operations.
"""

from collections import OrderedDict
from typing import Optional, Any
import time
import hashlib


class MemoryCache:
    """
    Bounded TTL-based cache with LRU eviction and hit/miss tracking.

    Caches query results to improve performance and tracks statistics
    for monitoring and optimization. The cache is capped at ``max_size``
    entries; when full, the least-recently-used entry is evicted on insert.
    """

    # Run a cold-expired sweep every this many set() calls so that entries
    # which expire but are never read back do not linger until overflow.
    _SWEEP_INTERVAL = 256

    def __init__(self, config):
        """
        Initialize cache.

        Args:
            config: MemoryRetrievalConfig instance
        """
        self._config = config
        self._max_size = max(1, int(getattr(config, "cache_max_size", 10_000)))
        # OrderedDict preserves insertion order and supports O(1) move_to_end /
        # popitem(last=False), giving us LRU semantics cheaply.
        self._cache: "OrderedDict[str, dict]" = OrderedDict()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }
        self._sets_since_sweep = 0

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

        # Cache hit - mark as most-recently-used for LRU ordering
        self._stats["hits"] += 1
        entry["hits"] += 1
        entry["last_accessed"] = time.time()
        self._cache.move_to_end(cache_key)

        return entry["value"]

    def set(self, cache_key: str, value: Any, ttl: Optional[int] = None):
        """
        Store value in cache with TTL, evicting the LRU entry if over capacity.

        Args:
            cache_key: Cache key string
            value: Value to cache
            ttl: Time to live in seconds (uses config default if None)
        """
        if ttl is None:
            ttl = self._config.cache_ttl_seconds

        now = time.time()
        entry = {
            "value": value,
            "created_at": now,
            "expires_at": now + ttl,
            "last_accessed": now,
            "hits": 0,
        }

        # Overwrite (and refresh recency) or insert as most-recently-used.
        self._cache[cache_key] = entry
        self._cache.move_to_end(cache_key)

        # Periodically reclaim cold-expired entries that are never read back.
        self._sets_since_sweep += 1
        if self._sets_since_sweep >= self._SWEEP_INTERVAL:
            self.clear_expired()
            self._sets_since_sweep = 0

        self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        """Evict least-recently-used entries until the cache is within cap."""
        while len(self._cache) > self._max_size:
            # popitem(last=False) removes the oldest (LRU) entry.
            self._cache.popitem(last=False)
            self._stats["evictions"] += 1

    def clear_expired(self) -> int:
        """
        Remove all expired entries regardless of access.

        Returns:
            Number of entries reclaimed.
        """
        now = time.time()
        expired_keys = [key for key, entry in self._cache.items() if now > entry["expires_at"]]
        for key in expired_keys:
            del self._cache[key]
            self._stats["evictions"] += 1
        return len(expired_keys)

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
            Dict with hits, misses, hit_rate, size, evictions, max_size, utilization
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0.0
        size = len(self._cache)

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate,
            "size": size,
            "max_size": self._max_size,
            "utilization": size / self._max_size if self._max_size else 0.0,
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
