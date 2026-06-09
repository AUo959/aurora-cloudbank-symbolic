"""
Tests for src/middleware/body_size.py — MaxBodySizeMiddleware (issue #817).
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.middleware.body_size import MaxBodySizeMiddleware


def _make_app(max_bytes: int) -> FastAPI:
    app = FastAPI()
    app.add_middleware(MaxBodySizeMiddleware, max_bytes=max_bytes)

    @app.post("/upload")
    async def upload():
        return {"ok": True}

    return app


@pytest.mark.unit
def test_request_within_limit_passes():
    """Body smaller than limit is forwarded normally."""
    client = TestClient(_make_app(max_bytes=100))
    response = client.post(
        "/upload",
        content=b"x" * 50,
        headers={"Content-Length": "50", "Content-Type": "application/octet-stream"},
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_request_exactly_at_limit_passes():
    """Body exactly at the limit is accepted."""
    client = TestClient(_make_app(max_bytes=100))
    response = client.post(
        "/upload",
        content=b"x" * 100,
        headers={"Content-Length": "100", "Content-Type": "application/octet-stream"},
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_request_over_limit_returns_413():
    """Body declared larger than the limit is rejected with HTTP 413."""
    client = TestClient(_make_app(max_bytes=100))
    response = client.post(
        "/upload",
        content=b"x" * 101,
        headers={"Content-Length": "101", "Content-Type": "application/octet-stream"},
    )
    assert response.status_code == 413


@pytest.mark.unit
def test_413_response_is_plain_text():
    """413 response body is plain text describing the limit."""
    client = TestClient(_make_app(max_bytes=100))
    response = client.post(
        "/upload",
        content=b"x" * 200,
        headers={"Content-Length": "200", "Content-Type": "application/octet-stream"},
    )
    assert response.status_code == 413
    assert "100" in response.text  # limit mentioned in body


@pytest.mark.unit
def test_missing_content_length_not_rejected():
    """Requests without Content-Length header are not rejected by fast-path guard."""
    client = TestClient(_make_app(max_bytes=10))
    # TestClient sends Content-Length automatically; simulate absence by using
    # chunked-style transfer. A GET request has no body, so Content-Length is absent.
    response = client.get("/upload")
    # 405 Method Not Allowed (not 413) — guard didn't fire
    assert response.status_code in (200, 405, 422)
    assert response.status_code != 413


@pytest.mark.unit
def test_malformed_content_length_not_rejected():
    """A malformed (non-integer) Content-Length header does not cause a 413 or 500."""
    client = TestClient(_make_app(max_bytes=100))
    response = client.post(
        "/upload",
        content=b"hello",
        headers={"Content-Length": "not-a-number", "Content-Type": "application/octet-stream"},
    )
    # Should pass through to the route (200) or hit Starlette's own handling
    assert response.status_code != 413
