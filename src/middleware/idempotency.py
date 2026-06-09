"""
Idempotency-Key Middleware
===========================
Prevents duplicate execution of state-changing requests by caching
responses keyed on the client-supplied Idempotency-Key header.

Behaviour:
  - No header → pass through unchanged (key is optional by default).
  - Header present, UUID-invalid → HTTP 422.
  - Header present, first request → execute route, cache response, return it.
  - Header present, same key in-flight → HTTP 409 (retry later).
  - Header present, same key already done → replay cached response, no route call.

Cache is in-process (dict); TTL defaults to 24 h via AURORA_IDEMPOTENCY_TTL_SECONDS.
For multi-process deployments, replace _IdempotencyStore with a Redis backend.

Key uniqueness scope: (HTTP method, URL path, Idempotency-Key value).
This prevents a single key value from accidentally de-duplicating requests
to different endpoints.
"""

import logging
import os
import re
import time
from typing import Dict, Optional, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

_DEFAULT_TTL = 86_400  # 24 hours


def _ttl() -> float:
    try:
        return float(os.getenv("AURORA_IDEMPOTENCY_TTL_SECONDS", str(_DEFAULT_TTL)))
    except ValueError:
        return _DEFAULT_TTL


# ---------------------------------------------------------------------------
# In-process cache (swap this class for a Redis-backed one in production)
# ---------------------------------------------------------------------------

class _CacheRecord:
    __slots__ = ("status", "status_code", "body", "media_type", "headers", "expires_at")

    def __init__(
        self,
        *,
        status: str,
        status_code: int = 0,
        body: bytes = b"",
        media_type: Optional[str] = None,
        headers: Optional[dict] = None,
        expires_at: float = 0.0,
    ) -> None:
        self.status = status          # "in_flight" | "done"
        self.status_code = status_code
        self.body = body
        self.media_type = media_type
        self.headers = headers or {}
        self.expires_at = expires_at


_CacheKey = Tuple[str, str, str]  # (method, path, idempotency_key)

_store: Dict[_CacheKey, _CacheRecord] = {}


def _purge_expired() -> None:
    now = time.monotonic()
    expired = [k for k, v in _store.items() if v.expires_at < now]
    for k in expired:
        del _store[k]


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Cache and replay responses for requests carrying an Idempotency-Key header."""

    def __init__(self, app: ASGIApp, ttl_seconds: Optional[float] = None) -> None:
        super().__init__(app)
        self._ttl = ttl_seconds if ttl_seconds is not None else _ttl()

    async def dispatch(self, request: Request, call_next) -> Response:
        raw_key = request.headers.get("Idempotency-Key")
        if not raw_key:
            return await call_next(request)

        # Validate UUID format
        if not _UUID_RE.match(raw_key.strip()):
            return JSONResponse(
                {"detail": "Idempotency-Key must be a UUID (e.g. xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)."},
                status_code=422,
            )

        key = raw_key.strip().lower()
        cache_key: _CacheKey = (request.method, request.url.path, key)

        # Periodically evict expired entries (simple O(n) scan is fine at low volume)
        _purge_expired()

        record = _store.get(cache_key)

        if record is not None:
            if record.status == "in_flight":
                logger.info("Idempotency: key %s in-flight for %s %s", key, request.method, request.url.path)
                return JSONResponse(
                    {"detail": "A request with this Idempotency-Key is already in progress. Retry after it completes."},
                    status_code=409,
                    headers={"Retry-After": "5"},
                )

            if record.status == "done" and record.expires_at > time.monotonic():
                logger.debug("Idempotency: replaying cached response for key %s", key)
                # Strip hop-by-hop headers that must not be forwarded
                headers = {k: v for k, v in record.headers.items() if k.lower() not in ("content-length",)}
                return Response(
                    content=record.body,
                    status_code=record.status_code,
                    headers=headers,
                    media_type=record.media_type,
                )

        # First request with this key — mark in-flight
        _store[cache_key] = _CacheRecord(
            status="in_flight",
            expires_at=time.monotonic() + self._ttl,
        )

        try:
            response = await call_next(request)
        except Exception:
            # Route raised — remove in-flight marker so client can retry
            _store.pop(cache_key, None)
            raise

        # Buffer the response body so we can both cache and return it
        body_chunks = []
        async for chunk in response.body_iterator:
            body_chunks.append(chunk if isinstance(chunk, bytes) else chunk.encode())
        body = b"".join(body_chunks)

        _store[cache_key] = _CacheRecord(
            status="done",
            status_code=response.status_code,
            body=body,
            media_type=response.media_type,
            headers=dict(response.headers),
            expires_at=time.monotonic() + self._ttl,
        )

        logger.info(
            "Idempotency: stored response (status=%d) for key %s on %s %s",
            response.status_code, key, request.method, request.url.path,
        )

        return Response(
            content=body,
            status_code=response.status_code,
            headers={k: v for k, v in response.headers.items() if k.lower() != "content-length"},
            media_type=response.media_type,
        )


def clear_idempotency_cache() -> None:
    """Remove all entries from the in-process cache (useful in tests)."""
    _store.clear()
