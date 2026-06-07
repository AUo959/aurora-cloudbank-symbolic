"""Tests for src/middleware/csrf_middleware — issue #784.

Verifies that GlobalCsrfMiddleware:
  - passes safe (GET/HEAD) methods without a token
  - blocks unsafe methods (POST/PUT/PATCH/DELETE) when no token is supplied
  - allows requests on the path allowlist even without a token
  - degrades gracefully when no CSRF_SECRET_KEY is configured
  - accepts a well-formed, in-date HMAC token
  - rejects an invalid / tampered HMAC token
"""
import hashlib
import hmac
import time

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from src.middleware.csrf_middleware import (
    GlobalCsrfMiddleware,
    _is_exempt,
    _validate_csrf_token,
)

_SECRET = "test-csrf-secret-key"


# ---------------------------------------------------------------------------
# Helper: generate a valid token
# ---------------------------------------------------------------------------

def _make_token(secret: str = _SECRET, session_id: str = "sess-abc", offset: int = 0) -> str:
    """Build a well-formed HMAC-SHA256 CSRF token."""
    timestamp = str(int(time.time()) + offset)
    message = f"{session_id}.{timestamp}"
    sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"{session_id}.{timestamp}.{sig}"


# ---------------------------------------------------------------------------
# Unit tests — _is_exempt
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_is_exempt_known_allowlist_paths():
    assert _is_exempt("/health")
    assert _is_exempt("/metrics")
    assert _is_exempt("/docs")
    assert _is_exempt("/openapi.json")
    assert _is_exempt("/redoc")
    assert _is_exempt("/api/auth/token")
    assert _is_exempt("/api/auth/refresh")
    assert _is_exempt("/api/csrf-token")
    assert _is_exempt("/csrf-token")


@pytest.mark.unit
def test_is_exempt_prefix_matches():
    assert _is_exempt("/api/webhooks/github")
    assert _is_exempt("/api/webhooks/stripe")
    assert _is_exempt("/docs/swagger")
    assert _is_exempt("/openapi/v3")
    assert _is_exempt("/redoc/v2")


@pytest.mark.unit
def test_is_exempt_non_allowlisted_paths():
    assert not _is_exempt("/api/memory/store")
    assert not _is_exempt("/api/quantum/simulate")
    assert not _is_exempt("/api/monitoring/status")
    assert not _is_exempt("/data")


# ---------------------------------------------------------------------------
# Unit tests — _validate_csrf_token
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_validate_csrf_token_valid():
    token = _make_token()
    assert _validate_csrf_token(token, _SECRET) is True


@pytest.mark.unit
def test_validate_csrf_token_wrong_secret():
    token = _make_token(secret=_SECRET)
    assert _validate_csrf_token(token, "wrong-secret") is False


@pytest.mark.unit
def test_validate_csrf_token_tampered_signature():
    token = _make_token()
    parts = token.rsplit(".", 1)
    tampered = parts[0] + ".deadbeefdeadbeef"
    assert _validate_csrf_token(tampered, _SECRET) is False


@pytest.mark.unit
def test_validate_csrf_token_expired():
    # Create token 400 seconds in the past (beyond 300 s TTL + 30 s grace)
    token = _make_token(offset=-400)
    assert _validate_csrf_token(token, _SECRET) is False


@pytest.mark.unit
def test_validate_csrf_token_future_skew():
    # Slightly future token within grace period should be accepted
    token = _make_token(offset=20)
    assert _validate_csrf_token(token, _SECRET) is True


@pytest.mark.unit
def test_validate_csrf_token_too_far_future():
    # Token with timestamp > 30 s in future is rejected
    token = _make_token(offset=60)
    assert _validate_csrf_token(token, _SECRET) is False


@pytest.mark.unit
def test_validate_csrf_token_wrong_format():
    assert _validate_csrf_token("not-a-valid-token", _SECRET) is False
    assert _validate_csrf_token("", _SECRET) is False
    assert _validate_csrf_token("a.b", _SECRET) is False


# ---------------------------------------------------------------------------
# Middleware integration tests via Starlette test app
# ---------------------------------------------------------------------------

def _make_app(secret: str = _SECRET) -> Starlette:
    async def view(request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    routes = [
        Route("/data", view, methods=["GET", "POST", "PUT", "PATCH", "DELETE"]),
        Route("/health", view, methods=["POST"]),
        Route("/api/auth/token", view, methods=["POST"]),
        Route("/api/webhooks/gh", view, methods=["POST"]),
    ]
    app = Starlette(routes=routes)
    app.add_middleware(GlobalCsrfMiddleware, secret_key=secret)
    return app


@pytest.mark.unit
def test_get_request_bypasses_csrf():
    client = TestClient(_make_app(), raise_server_exceptions=True)
    assert client.get("/data").status_code == 200


@pytest.mark.unit
def test_post_without_token_is_403():
    client = TestClient(_make_app(), raise_server_exceptions=False)
    resp = client.post("/data", json={})
    assert resp.status_code == 403
    assert "CSRF token missing" in resp.json()["detail"]


@pytest.mark.unit
def test_put_without_token_is_403():
    client = TestClient(_make_app(), raise_server_exceptions=False)
    assert client.put("/data", json={}).status_code == 403


@pytest.mark.unit
def test_patch_without_token_is_403():
    client = TestClient(_make_app(), raise_server_exceptions=False)
    assert client.patch("/data", json={}).status_code == 403


@pytest.mark.unit
def test_delete_without_token_is_403():
    client = TestClient(_make_app(), raise_server_exceptions=False)
    assert client.delete("/data").status_code == 403


@pytest.mark.unit
def test_post_with_valid_token_succeeds():
    client = TestClient(_make_app(), raise_server_exceptions=True)
    token = _make_token()
    resp = client.post("/data", json={}, headers={"X-CSRF-Token": token})
    assert resp.status_code == 200


@pytest.mark.unit
def test_post_with_invalid_token_is_403():
    client = TestClient(_make_app(), raise_server_exceptions=False)
    resp = client.post("/data", json={}, headers={"X-CSRF-Token": "bad.token.value"})
    assert resp.status_code == 403
    assert "invalid" in resp.json()["detail"].lower()


@pytest.mark.unit
def test_post_on_health_allowlisted_path_succeeds():
    client = TestClient(_make_app(), raise_server_exceptions=True)
    assert client.post("/health", json={}).status_code == 200


@pytest.mark.unit
def test_post_on_auth_token_allowlisted_path_succeeds():
    client = TestClient(_make_app(), raise_server_exceptions=True)
    assert client.post("/api/auth/token", json={}).status_code == 200


@pytest.mark.unit
def test_post_on_webhook_prefix_succeeds():
    client = TestClient(_make_app(), raise_server_exceptions=True)
    assert client.post("/api/webhooks/gh", json={}).status_code == 200


@pytest.mark.unit
def test_no_secret_key_degrades_gracefully(monkeypatch):
    """When CSRF_SECRET_KEY is absent the middleware allows all requests.

    The middleware constructor falls back to os.getenv("CSRF_SECRET_KEY").
    We must ensure that env var is absent for this test so the middleware
    truly enters graceful-degradation mode.
    """
    monkeypatch.delenv("CSRF_SECRET_KEY", raising=False)

    async def view(request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    from starlette.applications import Starlette as _Starlette
    from starlette.routing import Route as _Route

    app = _Starlette(routes=[_Route("/data", view, methods=["POST"])])
    app.add_middleware(GlobalCsrfMiddleware, secret_key="")
    client = TestClient(app, raise_server_exceptions=True)
    resp = client.post("/data", json={})
    assert resp.status_code == 200


@pytest.mark.unit
def test_csrf_token_accepted_via_lowercase_header():
    """X-Csrf-Token header variant should also be accepted."""
    client = TestClient(_make_app(), raise_server_exceptions=True)
    token = _make_token()
    resp = client.post("/data", json={}, headers={"X-Csrf-Token": token})
    assert resp.status_code == 200
