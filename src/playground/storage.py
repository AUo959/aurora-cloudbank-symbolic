"""Redis-backed session storage with safe in-memory fallback."""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Optional

try:
    from redis import Redis
    from redis.asyncio import Redis as AsyncRedis
except Exception:  # pragma: no cover - optional dependency
    Redis = None
    AsyncRedis = None

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = int(os.getenv("PLAYGROUND_SESSION_TTL", "900"))
REDIS_URL = os.getenv("PLAYGROUND_REDIS_URL", "redis://localhost:6379/0")


class SessionStore:
    """Wrapper around Redis with in-memory fallback for robustness."""

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._memory: Dict[str, Any] = {}
        self._memory_expiry: Dict[str, float] = {}
        self.redis: Optional[Redis] = None
        self.async_redis: Optional[AsyncRedis] = None
        if Redis:
            try:
                self.redis = Redis.from_url(REDIS_URL, decode_responses=True)
                self.redis.ping()
                logger.info("✅ Playground Redis connected")
            except Exception as exc:  # pragma: no cover - environment fallback
                logger.warning("⚠️ Redis unavailable, using in-memory store: %s", exc)
                self.redis = None
        if AsyncRedis:
            try:
                self.async_redis = AsyncRedis.from_url(REDIS_URL, decode_responses=True)
            except Exception:
                self.async_redis = None

    def _now(self) -> float:
        return time.time()

    def _set_memory(self, key: str, value: Any):
        self._memory[key] = value
        self._memory_expiry[key] = self._now() + self.ttl_seconds

    def _get_memory(self, key: str) -> Optional[Any]:
        expires = self._memory_expiry.get(key)
        if expires and expires < self._now():
            self._memory.pop(key, None)
            self._memory_expiry.pop(key, None)
            return None
        return self._memory.get(key)

    def create_session(self, session_id: str, payload: Dict[str, Any]):
        payload["created_at"] = self._now()
        payload["expires_at"] = payload["created_at"] + self.ttl_seconds
        if self.redis:
            self.redis.setex(f"playground:session:{session_id}", self.ttl_seconds, json.dumps(payload))
        else:
            self._set_memory(f"session:{session_id}", payload)
        return payload

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        key = f"playground:session:{session_id}"
        if self.redis:
            raw = self.redis.get(key)
            return json.loads(raw) if raw else None
        return self._get_memory(f"session:{session_id}")

    def save_result(self, session_id: str, result: Dict[str, Any]):
        key = f"playground:result:{session_id}"
        if self.redis:
            self.redis.setex(key, self.ttl_seconds, json.dumps(result))
        else:
            self._set_memory(key, result)

    def get_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        key = f"playground:result:{session_id}"
        if self.redis:
            raw = self.redis.get(key)
            return json.loads(raw) if raw else None
        return self._get_memory(key)

    def set_share_code(self, short_code: str, payload: Dict[str, Any]):
        key = f"playground:share:{short_code}"
        if self.redis:
            self.redis.setex(key, self.ttl_seconds, json.dumps(payload))
        else:
            self._set_memory(key, payload)

    def get_share_code(self, short_code: str) -> Optional[Dict[str, Any]]:
        key = f"playground:share:{short_code}"
        if self.redis:
            raw = self.redis.get(key)
            return json.loads(raw) if raw else None
        return self._get_memory(key)

    async def publish_event(self, session_id: str, payload: Dict[str, Any]):
        """Publish a streaming payload on the session channel."""
        if self.async_redis:
            await self.async_redis.publish(f"playground:stream:{session_id}", json.dumps(payload))
        else:
            # In-memory fallback: store last event for polling
            self._set_memory(f"stream:{session_id}", payload)

    async def stream_events(self, session_id: str):
        """Async generator yielding events via Redis pubsub or in-memory store."""
        if self.async_redis:
            pubsub = self.async_redis.pubsub()
            channel = f"playground:stream:{session_id}"
            await pubsub.subscribe(channel)
            try:
                async for message in pubsub.listen():
                    if message.get("type") == "message":
                        data = json.loads(message["data"])
                        yield data
            finally:
                try:
                    await pubsub.unsubscribe(channel)
                except Exception:
                    pass
                try:
                    await pubsub.close()
                except Exception:
                    pass
        else:
            # Polling fallback
            last_payload = None
            while True:
                payload = self._get_memory(f"stream:{session_id}")
                if payload and payload != last_payload:
                    last_payload = payload
                    yield payload
                await _sleep_for_stream()


async def _sleep_for_stream():  # pragma: no cover - small async helper
    import asyncio

    await asyncio.sleep(0.5)
