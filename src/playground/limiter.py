"""Per-IP rate limiting using Redis with graceful in-memory fallback."""
from __future__ import annotations

import logging
import time
from typing import Dict

from fastapi import HTTPException

from .storage import SessionStore

logger = logging.getLogger(__name__)


class RateLimiter:
    """Per-IP execution limiter (default 100/hour)."""

    def __init__(self, store: SessionStore, limit: int = 100, window_seconds: int = 3600):
        self.store = store
        self.limit = limit
        self.window_seconds = window_seconds
        self._memory_counts: Dict[str, Dict[str, int]] = {}

    def _memory_increment(self, key: str) -> int:
        now = int(time.time())
        bucket = now // self.window_seconds
        bucket_key = f"{key}:{bucket}"
        bucket_map = self._memory_counts.setdefault(bucket_key, {"count": 0})
        bucket_map["count"] += 1
        return bucket_map["count"]

    def increment(self, ip_address: str) -> int:
        key = f"playground:rate:{ip_address}"
        if self.store.redis:
            current = self.store.redis.incr(key)
            if current == 1:
                self.store.redis.expire(key, self.window_seconds)
            return int(current)
        return self._memory_increment(key)

    def enforce(self, ip_address: str):
        current = self.increment(ip_address)
        if current > self.limit:
            logger.warning("Rate limit exceeded for %s", ip_address)
            raise HTTPException(status_code=429, detail="Execution rate limit exceeded")


def get_rate_limiter(store: SessionStore, limit: int = 100) -> RateLimiter:
    return RateLimiter(store=store, limit=limit)
