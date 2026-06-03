"""Tests for RequestIDMiddleware (Issue #818)."""

import os
import re
import uuid

# fastapi_security refuses to import without these secrets; set safe test values
# before any src.middleware import so the module-level guard doesn't raise.
os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-key-32chars-min!")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-auth-secret-32chars-min!")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-32chars-min!")

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from src.middleware.request_id import (
    REQUEST_ID_HEADER,
    RequestIDMiddleware,
    current_request_id,
)


def _make_app() -> TestClient:
    """Minimal Starlette app with RequestIDMiddleware for testing."""

    async def echo(request: Request) -> PlainTextResponse:
        rid = getattr(request.state, "request_id", "MISSING")
        ctx = current_request_id.get()
        return PlainTextResponse(f"{rid}|{ctx}")

    app = Starlette(routes=[Route("/", echo)])
    app.add_middleware(RequestIDMiddleware)
    return TestClient(app, raise_server_exceptions=True)


@pytest.mark.unit
class TestRequestIDMiddleware:
    """RequestIDMiddleware generates, validates, and propagates request IDs."""

    def test_generates_uuid_when_no_header(self):
        client = _make_app()
        resp = client.get("/")
        rid = resp.headers.get(REQUEST_ID_HEADER, "")
        assert rid, "Response must include X-Request-ID"
        # UUID4 pattern
        assert re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", rid), (
            f"Expected UUID4, got {rid!r}"
        )

    def test_forwards_valid_caller_id(self):
        client = _make_app()
        caller_id = str(uuid.uuid4())
        resp = client.get("/", headers={REQUEST_ID_HEADER: caller_id})
        assert resp.headers[REQUEST_ID_HEADER] == caller_id

    def test_replaces_invalid_caller_id_with_uuid(self):
        client = _make_app()
        resp = client.get("/", headers={REQUEST_ID_HEADER: "bad\ninject"})
        rid = resp.headers[REQUEST_ID_HEADER]
        # Must NOT echo the injected value
        assert "inject" not in rid
        assert re.match(r"^[0-9a-f-]{36}$", rid), f"Expected UUID4 fallback, got {rid!r}"

    def test_replaces_oversized_caller_id(self):
        client = _make_app()
        resp = client.get("/", headers={REQUEST_ID_HEADER: "a" * 200})
        rid = resp.headers[REQUEST_ID_HEADER]
        assert len(rid) <= 36

    def test_request_state_contains_id(self):
        client = _make_app()
        resp = client.get("/")
        state_id, _ = resp.text.split("|")
        assert state_id == resp.headers[REQUEST_ID_HEADER]

    def test_contextvar_set_during_request(self):
        client = _make_app()
        resp = client.get("/")
        _, ctx_id = resp.text.split("|")
        assert ctx_id == resp.headers[REQUEST_ID_HEADER]

    def test_contextvar_cleared_after_request(self):
        # After the request completes the ContextVar should reset to default "".
        assert current_request_id.get() == ""

    def test_unique_id_per_request(self):
        client = _make_app()
        ids = {client.get("/").headers[REQUEST_ID_HEADER] for _ in range(5)}
        assert len(ids) == 5, "Each request should get a unique ID"
