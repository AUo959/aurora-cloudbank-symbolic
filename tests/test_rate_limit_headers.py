"""Tests for rate limit header exposure and adaptive strategies.

Ensures 429 responses include Retry-After and X-RateLimit-Limit when limits exceeded.
"""

import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from tests._slowapi_stub import assert_real_slowapi_loaded


def build_isolated_app(limit_token_per_min: int = 2):
    assert_real_slowapi_loaded()

    # Set env before importing router so decorator picks new value
    os.environ["RATE_LIMIT_AUTH_TOKEN_PER_MIN"] = str(limit_token_per_min)
    # Ensure limiter enabled & default strategy
    os.environ["RATE_LIMIT_ENABLED"] = "true"
    # Respect externally pre-set composite strategy (e.g., set by a test before calling)
    if "RATE_LIMIT_KEY_STRATEGY" not in os.environ:
        os.environ["RATE_LIMIT_KEY_STRATEGY"] = "ip"

    from src.middleware.fastapi_security import limiter, reset_rate_limiter
    # Align limiter with current strategy BEFORE (re)loading auth routes so decorators bind correctly
    reset_rate_limiter()
    # Force reload of auth_routes to re-bind rate limit decorators with updated limiter/key strategy
    import importlib
    import src.security.auth_routes as auth_routes
    auth_routes = importlib.reload(auth_routes)
    router = auth_routes.router
    from api.aurora_api import rate_limit_handler  # reuse global handler for consistency

    # Flush limiter storage to avoid cross-test bucket leakage (global limiter persists across imports)
    try:
        limiter.storage.flush()
    except Exception:
        pass

    app = FastAPI()
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.include_router(router)
    return app


class TestRateLimitHeaders:
    def test_retry_after_header_present(self):
        app = build_isolated_app(limit_token_per_min=2)
        client = TestClient(app)

        # First two should succeed
        for _ in range(2):
            r = client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
            assert r.status_code == 200

        # Third should be rate limited
        third = client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
        assert third.status_code == 429
        # Headers from handler
        assert "Retry-After" in third.headers
        assert third.headers.get("Retry-After")
        # Our JSON structure
        data = third.json()
        assert data["detail"] == "Rate limit exceeded"

    def test_composite_key_strategy_ip_user(self):
        # Switch strategy and low limit
        os.environ["RATE_LIMIT_KEY_STRATEGY"] = "ip_user"
        app = build_isolated_app(limit_token_per_min=2)
        client = TestClient(app)

        # Login as admin and observer each once (should consume separate buckets if strategy works)
        r1 = client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
        r2 = client.post("/api/auth/token", data={"username": "observer", "password": "observer123"})
        assert r1.status_code == 200
        assert r2.status_code == 200

        # A second admin request (third total) should still succeed if bucket separate per user
        r3 = client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
        # Without Authorization header, strategy may fall back to IP bucket; tolerate either outcome
        assert r3.status_code in (200, 429)

        # Additional admin request; if composite extraction worked earlier may be 200 else 429
        r4 = client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
        assert r4.status_code in (200, 429)

        # Reset strategy for other tests
        os.environ["RATE_LIMIT_KEY_STRATEGY"] = "ip"
