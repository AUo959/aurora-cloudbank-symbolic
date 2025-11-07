"""
Test Security Middleware Module

Validates centralized security configuration for Aurora CloudBank.
"""

import pytest
import time
import hmac
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials

from src.middleware.fastapi_security import (
    security,
    limiter,
    get_rate_limiter,
    setup_cors_middleware,
    verify_csrf_token,
    generate_csrf_token,
    require_auth,
    secure_compare,
    CSRF_SECRET_KEY,
    CSRF_TOKEN_EXPIRY_SECONDS,
    CSRF_CLOCK_SKEW_GRACE_SECONDS,
)


class TestSecurityMiddleware:
    """Test suite for security middleware components"""

    @staticmethod
    def _create_mock_token(token_string: str):
        """Helper method to create a mock token object"""
        class MockToken:
            credentials = token_string
        return MockToken()

    @staticmethod
    def _generate_test_csrf_token(session_id: str, timestamp: int) -> str:
        """Helper method to generate a test CSRF token with specific timestamp"""
        message = f"{session_id}.{timestamp}"
        signature = hmac.new(
            CSRF_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{session_id}.{timestamp}.{signature}"

    def test_rate_limiter_creation(self):
        """Test rate limiter instance creation"""
        rate_limiter = get_rate_limiter()
        assert rate_limiter is not None
        # Limiter object exists and is callable
        assert callable(rate_limiter.limit)

    def test_global_limiter_instance(self):
        """Test global limiter instance exists"""
        assert limiter is not None
        # Limiter object exists and is callable
        assert callable(limiter.limit)

    def test_security_instance(self):
        """Test HTTPBearer security instance"""
        assert security is not None
        assert hasattr(security, 'scheme_name')

    def test_secure_compare_equal_strings(self):
        """Test secure_compare with equal strings"""
        assert secure_compare("test_token", "test_token") is True

    def test_secure_compare_different_strings(self):
        """Test secure_compare with different strings"""
        assert secure_compare("test_token", "wrong_token") is False

    def test_secure_compare_empty_strings(self):
        """Test secure_compare with empty strings"""
        assert secure_compare("", "") is True

    def test_verify_csrf_token_valid(self):
        """Test CSRF token verification with valid token"""
        # Generate a valid token using the actual generation function
        session_id = "test_session"
        token_string = generate_csrf_token(session_id)
        token = self._create_mock_token(token_string)

        # Should not raise exception
        verify_csrf_token(token, session_id=session_id)

    def test_verify_csrf_token_invalid_format(self):
        """Test CSRF token verification with invalid format"""
        # Token without proper format (missing parts)
        token = self._create_mock_token("invalid_token_format")

        with pytest.raises(HTTPException) as exc_info:
            verify_csrf_token(token)
        assert exc_info.value.status_code == 403
        assert "Invalid CSRF token" in str(exc_info.value.detail)

    def test_verify_csrf_token_none(self):
        """Test CSRF token verification with None token"""
        with pytest.raises(HTTPException) as exc_info:
            verify_csrf_token(None)
        assert exc_info.value.status_code == 403

    def test_verify_csrf_token_clock_skew_valid(self):
        """Test CSRF token verification with clock skew within grace period"""
        # Generate a token with timestamp 310 seconds in the past
        # This is past the 300-second expiry but within the 30-second grace period
        session_id = "test_session"
        old_timestamp = int(time.time()) - 310
        token_string = self._generate_test_csrf_token(session_id, old_timestamp)
        token = self._create_mock_token(token_string)

        # Should not raise exception because token is within grace period
        verify_csrf_token(token, session_id=session_id)

    def test_verify_csrf_token_clock_skew_expired(self):
        """Test CSRF token verification beyond clock skew grace period"""
        # Generate a token with timestamp 340 seconds in the past
        # This is past both the 300-second expiry and 30-second grace period
        session_id = "test_session"
        old_timestamp = int(time.time()) - 340
        token_string = self._generate_test_csrf_token(session_id, old_timestamp)
        token = self._create_mock_token(token_string)

        # Should raise exception because token is beyond grace period
        with pytest.raises(HTTPException) as exc_info:
            verify_csrf_token(token, session_id=session_id)
        assert exc_info.value.status_code == 403
        assert "expired" in str(exc_info.value.detail).lower()

    def test_verify_csrf_token_at_expiry_boundary(self):
        """Test CSRF token verification at exact expiry boundary"""
        # Generate a token with timestamp exactly 300 seconds in the past
        session_id = "test_session"
        old_timestamp = int(time.time()) - CSRF_TOKEN_EXPIRY_SECONDS
        token_string = self._generate_test_csrf_token(session_id, old_timestamp)
        token = self._create_mock_token(token_string)

        # Should not raise exception because token is at exact boundary (not exceeded)
        verify_csrf_token(token, session_id=session_id)

    def test_verify_csrf_token_fresh(self):
        """Test CSRF token verification with freshly generated token"""
        # Generate a fresh token using the actual generation function
        session_id = "test_session"
        token_string = generate_csrf_token(session_id)
        token = self._create_mock_token(token_string)

        # Should not raise exception
        verify_csrf_token(token, session_id=session_id)

    def test_setup_cors_middleware_default(self):
        """Test CORS middleware setup with default settings"""
        app = FastAPI()
        setup_cors_middleware(app)
        # Verify middleware was added
        assert len(app.user_middleware) > 0

    def test_setup_cors_middleware_custom(self):
        """Test CORS middleware setup with custom settings"""
        app = FastAPI()
        setup_cors_middleware(
            app,
            allow_origins=["https://example.com"],
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"]
        )
        assert len(app.user_middleware) > 0

    @pytest.mark.asyncio
    async def test_require_auth_decorator(self):
        """Test require_auth decorator"""
        @require_auth(roles=["admin"])
        async def test_function():
            return "success"

        result = await test_function()
        assert result == "success"

    def test_cors_middleware_integration(self):
        """Test CORS middleware integration with FastAPI app"""
        app = FastAPI()
        setup_cors_middleware(app)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test", headers={"Origin": "https://example.com"})
        assert response.status_code == 200
        # Check CORS headers are present
        assert "access-control-allow-origin" in response.headers


class TestSecurityIntegration:
    """Integration tests for security middleware with FastAPI"""

    def test_full_security_stack(self):
        """Test full security stack integration"""
        from fastapi import Depends
        app = FastAPI()
        setup_cors_middleware(app)

        @app.post("/secure")
        async def secure_endpoint(token: HTTPAuthorizationCredentials = Depends(security)):
            verify_csrf_token(token)
            return {"status": "secure"}

        client = TestClient(app)

        # Test without token - should fail
        response = client.post("/secure")
        assert response.status_code == 403  # Forbidden (no auth header)

        # Test with valid token
        response = client.post(
            "/secure",
            headers={"Authorization": "Bearer valid_token_123456"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "secure"

    def test_timing_attack_resistance(self):
        """Test secure_compare timing attack resistance"""
        import time

        token1 = "a" * 100
        token2_same = "a" * 100
        token2_diff = "b" * 100

        # Test with same strings
        start = time.perf_counter()
        result1 = secure_compare(token1, token2_same)
        time1 = time.perf_counter() - start

        # Test with different strings
        start = time.perf_counter()
        result2 = secure_compare(token1, token2_diff)
        time2 = time.perf_counter() - start

        # Results should be correct
        assert result1 is True
        assert result2 is False

        # Timing should be similar (within reasonable variance)
        # Note: This is a basic check, real timing attacks are more sophisticated
        time_ratio = max(time1, time2) / min(time1, time2)
        assert time_ratio < 10  # Allow 10x variance due to system noise
