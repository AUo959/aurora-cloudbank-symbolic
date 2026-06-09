"""Integration test: verify rate-limited endpoints return HTTP 429 (Issue #785)."""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


@pytest.mark.unit
def test_rate_limited_endpoint_returns_429():
    """A route decorated with @limiter.limit returns 429 after the threshold."""
    limiter = Limiter(key_func=get_remote_address, default_limits=[])
    app = FastAPI()
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    @app.get("/test-endpoint")
    @limiter.limit("2/minute")
    async def _test_endpoint(request: Request):
        return {"ok": True}

    client = TestClient(app, raise_server_exceptions=False)

    # First two requests should succeed
    r1 = client.get("/test-endpoint")
    r2 = client.get("/test-endpoint")
    assert r1.status_code == 200
    assert r2.status_code == 200

    # Third request must be rate-limited
    r3 = client.get("/test-endpoint")
    assert r3.status_code == 429, f"Expected 429, got {r3.status_code}"
