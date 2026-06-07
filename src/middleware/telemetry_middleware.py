"""Telemetry Middleware

Records per-request latency and HTTP status code into the MetricsPusher so
that live production traffic feeds the DriftDetector for behavioral drift
detection (see src/monitoring/metrics_pusher.py).

The middleware measures wall-clock time between request receipt and response
completion, then calls ``get_pusher().record(duration_ms, status_code)``.

Design notes:
- Uses Starlette BaseHTTPMiddleware for consistency with RequestIDMiddleware.
- Falls back gracefully if MetricsPusher is unavailable (import error, etc.).
- Only HTTP requests are instrumented; WebSocket connections are skipped.
"""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

try:
    from src.monitoring.metrics_pusher import get_pusher as _get_pusher
    _PUSHER_AVAILABLE = True
except Exception as _import_exc:  # pragma: no cover - graceful degradation
    logger.warning("MetricsPusher unavailable: %s", _import_exc)
    _PUSHER_AVAILABLE = False
    _get_pusher = None  # type: ignore[assignment]


class MetricsMiddleware(BaseHTTPMiddleware):
    """Capture per-request duration and status code for drift detection."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000.0

        if _PUSHER_AVAILABLE:
            try:
                _get_pusher().record(
                    duration_ms=duration_ms,
                    status_code=response.status_code,
                )
            except Exception as exc:  # pragma: no cover - safety net
                logger.debug("MetricsMiddleware: record error: %s", exc)

        return response
