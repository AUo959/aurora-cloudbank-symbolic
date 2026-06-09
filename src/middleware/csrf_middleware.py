"""Global CSRF enforcement middleware.

Enforces CSRF token validation on all state-changing HTTP methods
(POST, PUT, PATCH, DELETE) except for paths in the allowlist.

The token must be present as the X-CSRF-Token (or X-Csrf-Token) request header.
Token format mirrors src/middleware/fastapi_security.py:
    session_id.timestamp.signature  (HMAC-SHA256, 5-minute TTL)

Pair with: src/middleware/fastapi_security.py generate_csrf_token /
           verify_csrf_token for per-endpoint use; this middleware enforces
           the same rule globally so individual routes need not repeat it.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import FrozenSet, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# HTTP methods that mutate state — CSRF applies to these
_UNSAFE_METHODS: FrozenSet[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})

# Paths exempt from CSRF (machine-to-machine, read-only, or own-auth flows)
_CSRF_ALLOWLIST: FrozenSet[str] = frozenset({
    "/health",
    "/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/auth/token",      # OAuth token endpoint — has its own auth
    "/api/auth/refresh",
    "/api/csrf-token",      # Token issuance endpoint itself
    "/csrf-token",
    "/api/webhooks/",       # Webhook callbacks verified by their own signature
})

# Token freshness window — must match fastapi_security.py CSRF_TOKEN_EXPIRY_SECONDS
_TOKEN_EXPIRY_SECONDS: int = 300
_CLOCK_SKEW_GRACE_SECONDS: int = 30


def _is_exempt(path: str) -> bool:
    """Return True if *path* is on the CSRF allowlist."""
    if path in _CSRF_ALLOWLIST:
        return True
    # Prefix match for path families (docs, redoc, openapi, webhooks)
    for prefix in ("/api/webhooks/", "/docs", "/redoc", "/openapi"):
        if path.startswith(prefix):
            return True
    return False


def _validate_csrf_token(token: str, secret: str) -> bool:
    """Validate a CSRF token using inline HMAC-SHA256 with timestamp check.

    Expected token format: ``session_id.timestamp.signature``
    This matches the format produced by
    ``src.middleware.fastapi_security.generate_csrf_token``.

    Args:
        token:  Raw token string from the X-CSRF-Token header.
        secret: CSRF secret key (CSRF_SECRET_KEY env var).

    Returns:
        True if signature is valid and token has not expired.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return False

        session_id, timestamp_str, signature = parts

        # Verify timestamp freshness with clock-skew grace period
        token_time = int(timestamp_str)
        current_time = int(time.time())
        age = current_time - token_time
        if age < -_CLOCK_SKEW_GRACE_SECONDS:
            # Token timestamp is too far in the future
            return False
        if age > _TOKEN_EXPIRY_SECONDS + _CLOCK_SKEW_GRACE_SECONDS:
            # Token has expired
            return False

        # Recompute expected HMAC signature
        message = f"{session_id}.{timestamp_str}"
        expected_sig = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected_sig)

    except Exception:
        return False


class GlobalCsrfMiddleware(BaseHTTPMiddleware):
    """Enforce CSRF token on all unsafe (non-idempotent) routes.

    Reads the CSRF secret from the CSRF_SECRET_KEY env var at init time.
    When no secret is configured the middleware degrades gracefully: it logs
    a warning and passes requests through so the application can still start
    in development environments where the env var is absent.

    Args:
        app:        The ASGI application to wrap.
        secret_key: Override CSRF secret (defaults to CSRF_SECRET_KEY env var).
    """

    def __init__(self, app: ASGIApp, *, secret_key: str = "") -> None:
        super().__init__(app)
        self._secret_key: str = secret_key or os.getenv("CSRF_SECRET_KEY", "")
        if not self._secret_key:
            logger.warning(
                "GlobalCsrfMiddleware: CSRF_SECRET_KEY not set — CSRF enforcement disabled"
            )

    async def dispatch(self, request: Request, call_next) -> Response:
        # Safe / idempotent methods don't need CSRF protection
        if request.method not in _UNSAFE_METHODS:
            return await call_next(request)

        # Allowlisted paths bypass the check
        if _is_exempt(request.url.path):
            return await call_next(request)

        # No secret configured — degrade gracefully
        if not self._secret_key:
            logger.debug(
                "CSRF check skipped (no secret configured) for %s %s",
                request.method,
                request.url.path,
            )
            return await call_next(request)

        # Extract token from header (case-insensitive common variants)
        token: Optional[str] = (
            request.headers.get("X-CSRF-Token")
            or request.headers.get("X-Csrf-Token")
            or request.query_params.get("csrf_token")
        )

        if not token:
            logger.warning(
                "CSRF token missing: %s %s", request.method, request.url.path
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token missing. Include X-CSRF-Token header."},
            )

        if not _validate_csrf_token(token, self._secret_key):
            logger.warning(
                "CSRF token invalid: %s %s", request.method, request.url.path
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token invalid or expired."},
            )

        return await call_next(request)
