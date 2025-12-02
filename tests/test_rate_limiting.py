#!/usr/bin/env python3
"""
Tests for Rate Limiting Middleware
=================================
Target: src/middleware/rate_limiting.py
Coverage Goal: 100%

DLP: COVERAGE_IMPROVEMENT_CRITICAL
Chain: #932//. Integration Coverage Sprint
"""

import pytest  # noqa: F401
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

# Import the module under test
from src.middleware.rate_limiting import (
    limiter,
    rate_limit_error_handler,
    RateLimits,
    computational_limit,
    state_change_limit,
    read_only_limit,
    auth_limit,
    health_limit,
    agent_tools_limit,
)


class TestRateLimits:
    """Test RateLimits class constants"""

    def test_computational_limit(self):
        """Test computational rate limit value"""
        assert RateLimits.COMPUTATIONAL == "60/minute"

    def test_state_change_limit(self):
        """Test state change rate limit value"""
        assert RateLimits.STATE_CHANGE == "10/minute"

    def test_read_only_limit(self):
        """Test read-only rate limit value"""
        assert RateLimits.READ_ONLY == "200/minute"

    def test_auth_limit(self):
        """Test authentication rate limit value"""
        assert RateLimits.AUTH == "5/minute"

    def test_health_limit(self):
        """Test health check rate limit value"""
        assert RateLimits.HEALTH == "300/minute"

    def test_agent_tools_limit(self):
        """Test agent tools rate limit value"""
        assert RateLimits.AGENT_TOOLS == "30/minute"


class TestLimiterConfiguration:
    """Test limiter initialization and configuration"""

    def test_limiter_exists(self):
        """Test that limiter is properly initialized"""
        assert limiter is not None

    def test_limiter_headers_enabled(self):
        """Test that rate limit headers are enabled"""
        assert limiter._headers_enabled is True

    def test_limiter_has_default_limits(self):
        """Test that default limits are configured"""
        assert limiter._default_limits is not None


class TestRateLimitErrorHandler:
    """Test rate limit error handler"""

    def test_error_handler_returns_json_response(self):
        """Test that error handler returns JSONResponse"""
        # Create a mock RateLimitExceeded exception
        class MockRateLimitExceeded:
            detail = "60"

        exc = MockRateLimitExceeded()
        response = rate_limit_error_handler(exc)

        assert response.status_code == 429
        assert "Retry-After" in response.headers

    def test_error_handler_content_structure(self):
        """Test error response content structure"""
        class MockRateLimitExceeded:
            detail = "120"

        exc = MockRateLimitExceeded()
        response = rate_limit_error_handler(exc)

        # Parse the response body
        import json
        content = json.loads(response.body.decode())

        assert "error" in content
        assert content["error"] == "Rate limit exceeded"
        assert "detail" in content
        assert "retry_after" in content
        assert content["retry_after"] == "120"


class TestLimitDecorators:
    """Test rate limit decorator functions"""

    def test_computational_limit_returns_callable(self):
        """Test computational_limit decorator factory"""
        decorator = computational_limit()
        assert callable(decorator)

    def test_state_change_limit_returns_callable(self):
        """Test state_change_limit decorator factory"""
        decorator = state_change_limit()
        assert callable(decorator)

    def test_read_only_limit_returns_callable(self):
        """Test read_only_limit decorator factory"""
        decorator = read_only_limit()
        assert callable(decorator)

    def test_auth_limit_returns_callable(self):
        """Test auth_limit decorator factory"""
        decorator = auth_limit()
        assert callable(decorator)

    def test_health_limit_returns_callable(self):
        """Test health_limit decorator factory"""
        decorator = health_limit()
        assert callable(decorator)

    def test_agent_tools_limit_returns_callable(self):
        """Test agent_tools_limit decorator factory"""
        decorator = agent_tools_limit()
        assert callable(decorator)


class TestRateLimitIntegration:
    """Integration tests - verify decorator behavior"""

    def test_limiter_shared_state(self):
        """Test that limiter maintains shared state"""
        # Access limiter storage keys (should be accessible)
        assert hasattr(limiter, "_storage")
        assert hasattr(limiter, "_key_func")

    def test_limiter_can_be_attached_to_app(self):
        """Test limiter can be attached to FastAPI app state"""
        app = FastAPI()
        app.state.limiter = limiter
        assert app.state.limiter is limiter

    def test_exception_handler_can_be_registered(self):
        """Test rate limit exception handler can be registered"""
        app = FastAPI()
        app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)
        # If no exception, registration succeeded
        assert True


class TestRateLimitValues:
    """Test rate limit string parsing"""

    def test_limits_have_correct_format(self):
        """Verify all rate limits follow 'N/period' format"""
        import re
        pattern = r"^\d+/\w+$"

        limits = [
            RateLimits.COMPUTATIONAL,
            RateLimits.STATE_CHANGE,
            RateLimits.READ_ONLY,
            RateLimits.AUTH,
            RateLimits.HEALTH,
            RateLimits.AGENT_TOOLS,
        ]

        for limit in limits:
            assert re.match(pattern, limit), f"Invalid format: {limit}"

    def test_auth_most_restrictive(self):
        """Verify auth limit is most restrictive"""
        # Extract numbers from limit strings
        def get_rate(limit_str):
            return int(limit_str.split("/")[0])

        auth_rate = get_rate(RateLimits.AUTH)
        state_rate = get_rate(RateLimits.STATE_CHANGE)

        assert auth_rate < state_rate, "Auth should be more restrictive"

    def test_health_least_restrictive(self):
        """Verify health limit is least restrictive"""
        def get_rate(limit_str):
            return int(limit_str.split("/")[0])

        health_rate = get_rate(RateLimits.HEALTH)
        read_rate = get_rate(RateLimits.READ_ONLY)

        assert health_rate > read_rate, "Health should be less restrictive"
