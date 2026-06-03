"""
Request-ID Middleware

Generates or forwards an X-Request-ID header for every HTTP request and
propagates it through the response and log context so all log lines for a
single request share the same identifier.

Design:
  - If the client sends X-Request-ID, validate it via sanitize_request_id;
    discard silently if it fails validation and generate a fresh UUID instead.
  - Store the resolved ID in request.state.request_id so route handlers and
    other middleware can reference it without re-reading the header.
  - Echo the ID in the X-Request-ID response header.
  - Bind the ID to a contextvars.ContextVar so logging formatters can include
    it via a LogRecord filter without threading.local boilerplate.
"""

import logging
import uuid
from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

try:
    from src.middleware.fastapi_security import sanitize_request_id
except ImportError:  # pragma: no cover
    def sanitize_request_id(request_id: Optional[str]) -> Optional[str]:  # type: ignore[misc]
        return None

logger = logging.getLogger(__name__)

# Module-level ContextVar so any log formatter can read the current request ID.
current_request_id: ContextVar[str] = ContextVar("request_id", default="")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique X-Request-ID to every request/response pair."""

    def __init__(self, app: ASGIApp, header_name: str = REQUEST_ID_HEADER) -> None:
        super().__init__(app)
        self._header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get(self._header_name)
        request_id = sanitize_request_id(incoming) or str(uuid.uuid4())

        # Make ID available to route handlers and other middleware.
        request.state.request_id = request_id

        # Bind to context so log filters can pick it up without touching handlers.
        token = current_request_id.set(request_id)
        try:
            response = await call_next(request)
        finally:
            current_request_id.reset(token)

        response.headers[self._header_name] = request_id
        return response


class RequestIDLogFilter(logging.Filter):
    """Inject the current request_id into every LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = current_request_id.get()
        return True
