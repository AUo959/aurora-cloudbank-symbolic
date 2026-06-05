"""
Max Body Size Middleware
========================
Rejects HTTP requests whose body exceeds a configurable byte limit.

Fast-path: checks the Content-Length header before the body is read.
Any request where Content-Length is declared and exceeds the limit is
rejected immediately with HTTP 413, without touching the body.

Default limit: 10 MiB (AURORA_MAX_BODY_BYTES env var overrides).
"""

import logging
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

_10_MIB = 10 * 1024 * 1024


def _default_max_bytes() -> int:
    try:
        return int(os.getenv("AURORA_MAX_BODY_BYTES", str(_10_MIB)))
    except ValueError:
        return _10_MIB


class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Reject requests whose declared Content-Length exceeds *max_bytes*."""

    def __init__(self, app: ASGIApp, max_bytes: int = _10_MIB) -> None:
        super().__init__(app)
        self._max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length_header = request.headers.get("Content-Length")
        if content_length_header is not None:
            try:
                content_length = int(content_length_header)
            except ValueError:
                content_length = None

            if content_length is not None and content_length > self._max_bytes:
                logger.warning(
                    "Rejected oversized request: Content-Length=%d limit=%d path=%s",
                    content_length,
                    self._max_bytes,
                    request.url.path,
                )
                return Response(
                    content=f"Request body too large (limit {self._max_bytes} bytes).",
                    status_code=413,
                    media_type="text/plain",
                )

        return await call_next(request)
