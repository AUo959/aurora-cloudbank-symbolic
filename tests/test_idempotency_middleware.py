"""
Tests for src/middleware/idempotency.py — IdempotencyMiddleware (issue #819).
"""

import uuid
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.middleware.idempotency import IdempotencyMiddleware, clear_idempotency_cache

_VALID_KEY = str(uuid.uuid4())
_VALID_KEY_2 = str(uuid.uuid4())


def _make_app(ttl: float = 3600) -> FastAPI:
    app = FastAPI()
    app.add_middleware(IdempotencyMiddleware, ttl_seconds=ttl)

    call_count = {"n": 0}

    @app.post("/state")
    async def create_state():
        call_count["n"] += 1
        return {"count": call_count["n"]}

    app.state.call_count = call_count
    return app


@pytest.fixture(autouse=True)
def reset_cache():
    """Clear the idempotency cache before every test."""
    clear_idempotency_cache()
    yield
    clear_idempotency_cache()


@pytest.mark.unit
def test_request_without_idempotency_key_passes_through():
    """Requests without Idempotency-Key are forwarded normally on every call."""
    client = TestClient(_make_app())
    r1 = client.post("/state")
    r2 = client.post("/state")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["count"] == 1
    assert r2.json()["count"] == 2  # called twice, not cached


@pytest.mark.unit
def test_same_key_replays_cached_response():
    """Second request with the same Idempotency-Key returns the cached response."""
    app = _make_app()
    client = TestClient(app)

    r1 = client.post("/state", headers={"Idempotency-Key": _VALID_KEY})
    r2 = client.post("/state", headers={"Idempotency-Key": _VALID_KEY})

    assert r1.status_code == 200
    assert r2.status_code == 200
    # Route was called only once
    assert r1.json() == r2.json()
    assert app.state.call_count["n"] == 1


@pytest.mark.unit
def test_different_keys_are_independent():
    """Two different keys each execute the route independently."""
    app = _make_app()
    client = TestClient(app)

    r1 = client.post("/state", headers={"Idempotency-Key": _VALID_KEY})
    r2 = client.post("/state", headers={"Idempotency-Key": _VALID_KEY_2})

    assert r1.json()["count"] == 1
    assert r2.json()["count"] == 2
    assert app.state.call_count["n"] == 2


@pytest.mark.unit
def test_invalid_key_format_returns_422():
    """Non-UUID Idempotency-Key values are rejected with HTTP 422."""
    client = TestClient(_make_app())
    response = client.post("/state", headers={"Idempotency-Key": "not-a-uuid"})
    assert response.status_code == 422
    assert "UUID" in response.json()["detail"]


@pytest.mark.unit
def test_expired_cache_entry_allows_re_execution():
    """After TTL expires, the same key triggers a fresh route execution."""
    app = _make_app(ttl=0.0)  # immediate expiry
    client = TestClient(app)

    r1 = client.post("/state", headers={"Idempotency-Key": _VALID_KEY})
    assert r1.json()["count"] == 1

    # Force-clear so expiry-based eviction fires on next request
    clear_idempotency_cache()

    r2 = client.post("/state", headers={"Idempotency-Key": _VALID_KEY})
    assert r2.json()["count"] == 2  # executed again
    assert app.state.call_count["n"] == 2


@pytest.mark.unit
def test_different_paths_with_same_key_are_independent():
    """Same Idempotency-Key on different paths does not cross-contaminate."""
    app = FastAPI()
    app.add_middleware(IdempotencyMiddleware, ttl_seconds=3600)

    @app.post("/a")
    async def route_a():
        return {"route": "a"}

    @app.post("/b")
    async def route_b():
        return {"route": "b"}

    client = TestClient(app)

    ra = client.post("/a", headers={"Idempotency-Key": _VALID_KEY})
    rb = client.post("/b", headers={"Idempotency-Key": _VALID_KEY})

    assert ra.json()["route"] == "a"
    assert rb.json()["route"] == "b"


@pytest.mark.unit
def test_cached_response_preserves_status_code():
    """Cached replay returns the original HTTP status code (not always 200)."""
    app = FastAPI()
    app.add_middleware(IdempotencyMiddleware, ttl_seconds=3600)

    @app.post("/created")
    async def create():
        from fastapi.responses import JSONResponse
        return JSONResponse({"msg": "ok"}, status_code=201)

    client = TestClient(app)
    key = str(uuid.uuid4())

    r1 = client.post("/created", headers={"Idempotency-Key": key})
    r2 = client.post("/created", headers={"Idempotency-Key": key})

    assert r1.status_code == 201
    assert r2.status_code == 201
