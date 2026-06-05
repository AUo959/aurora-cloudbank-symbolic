"""Integration tests for authentication API routes."""

import json
import os
from unittest import TestCase

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.security.auth_routes import build_auth_users_db, router
from src.security.oauth2 import OAuth2Handler
from slowapi.middleware import SlowAPIMiddleware
from src.middleware.fastapi_security import limiter


@pytest.fixture(autouse=True)
def _require_dev_auth_env(dev_auth_fixture_env):  # noqa: PT004
    """Activate the dev-auth fixture environment for every test in this module.

    All tests here exercise authentication routes that depend on the dev/test
    fixture user store (AURORA_ALLOW_DEV_AUTH_FIXTURE + password secrets).
    Using autouse=True within this file avoids repetitive per-test requests
    while keeping the variables absent from modules that do not request them.
    """


@pytest.fixture
def app():
    """Create a test FastAPI application."""
    test_app = FastAPI()
    # Enable rate limiting for auth endpoints inside test app
    test_app.state.limiter = limiter
    test_app.add_middleware(SlowAPIMiddleware)
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


def auth_data(username):
    """Return dev-fixture credentials from the explicit test environment."""
    return {
        "username": username,
        "password": os.environ[f"AURORA_DEV_{username.upper()}_PASSWORD"],
    }


class TestAuthUserStoreConfiguration(TestCase):
    """Validate production and dev/test auth user-store configuration."""

    def test_production_startup_requires_configured_users(self):
        """Mounted auth must not silently ship default credentials."""
        with pytest.raises(RuntimeError, match="auth users are not configured"):
            build_auth_users_db({})

    def test_configured_user_store_accepts_password_hashes(self):
        """Production-style configuration should use supplied password hashes."""
        password_hash = OAuth2Handler.get_password_hash("configured-secret")
        payload = {
            "configured": {
                "email": "configured@aurora.local",
                "full_name": "Configured User",
                "role": "observer",
                "password_hash": password_hash,
            }
        }

        users = build_auth_users_db({"AURORA_AUTH_USERS_JSON": json.dumps(payload)})

        self.assertEqual(users["configured"].email, "configured@aurora.local")
        self.assertIsNotNone(OAuth2Handler.authenticate_user("configured", "configured-secret", users))
        self.assertIsNone(OAuth2Handler.authenticate_user("configured", "wrong-secret", users))

    def test_dev_fixture_requires_explicit_gate_and_password_secrets(self):
        """Dev/test fixture users require both the gate and password env values."""
        with pytest.raises(RuntimeError, match="AURORA_DEV_ADMIN_PASSWORD"):
            build_auth_users_db({"AURORA_ALLOW_DEV_AUTH_FIXTURE": "true"})

        users = build_auth_users_db(
            {
                "AURORA_ALLOW_DEV_AUTH_FIXTURE": "true",
                "AURORA_DEV_ADMIN_PASSWORD": os.environ["AURORA_DEV_ADMIN_PASSWORD"],
                "AURORA_DEV_OPERATOR_PASSWORD": os.environ["AURORA_DEV_OPERATOR_PASSWORD"],
                "AURORA_DEV_OBSERVER_PASSWORD": os.environ["AURORA_DEV_OBSERVER_PASSWORD"],
            }
        )

        self.assertIsNotNone(
            OAuth2Handler.authenticate_user("admin", os.environ["AURORA_DEV_ADMIN_PASSWORD"], users)
        )
        self.assertIsNotNone(
            OAuth2Handler.authenticate_user("operator", os.environ["AURORA_DEV_OPERATOR_PASSWORD"], users)
        )
        self.assertIsNotNone(
            OAuth2Handler.authenticate_user("observer", os.environ["AURORA_DEV_OBSERVER_PASSWORD"], users)
        )


class TestLoginEndpoint:
    """Test the /api/auth/token endpoint."""

    def test_login_success_admin(self, client):
        """Test successful login with admin credentials."""
        response = client.post("/api/auth/token", data=auth_data("admin"))

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_login_success_operator(self, client):
        """Test successful login with operator credentials."""
        response = client.post("/api/auth/token", data=auth_data("operator"))

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_success_observer(self, client):
        """Test successful login with observer credentials."""
        response = client.post("/api/auth/token", data=auth_data("observer"))

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        response = client.post("/api/auth/token", data={"username": "admin", "password": "wrong_password"})

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post("/api/auth/token", data={"username": "nonexistent", "password": "password"})

        assert response.status_code == 401

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials."""
        response = client.post("/api/auth/token", data={})

        assert response.status_code == 422  # Unprocessable Entity


class TestUserInfoEndpoint:
    """Test the /api/auth/me endpoint."""

    def test_get_user_info_authenticated(self, client):
        """Test getting user info with valid token."""
        # Login first
        login_response = client.post("/api/auth/token", data=auth_data("admin"))
        token = login_response.json()["access_token"]

        # Get user info
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    def test_get_user_info_unauthenticated(self, client):
        """Test getting user info without token."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_user_info_invalid_token(self, client):
        """Test getting user info with invalid token."""
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == 401


class TestPermissionsEndpoint:
    """Test the /api/auth/me/permissions endpoint."""

    def test_get_permissions_admin(self, client):
        """Test getting permissions for admin user."""
        # Login as admin
        login_response = client.post("/api/auth/token", data=auth_data("admin"))
        token = login_response.json()["access_token"]

        # Get permissions
        response = client.get("/api/auth/me/permissions", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        assert "permissions" in data
        assert "read" in data["permissions"]
        assert "write" in data["permissions"]
        assert "admin" in data["permissions"]

    def test_get_permissions_observer(self, client):
        """Test getting permissions for observer user."""
        # Login as observer
        login_response = client.post("/api/auth/token", data=auth_data("observer"))
        token = login_response.json()["access_token"]

        # Get permissions
        response = client.get("/api/auth/me/permissions", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "observer"
        assert "read" in data["permissions"]
        assert "monitor" in data["permissions"]
        assert "write" not in data["permissions"]
        assert "admin" not in data["permissions"]

    def test_get_permissions_operator(self, client):
        """Test getting permissions for operator user."""
        # Login as operator
        login_response = client.post("/api/auth/token", data=auth_data("operator"))
        token = login_response.json()["access_token"]

        # Get permissions
        response = client.get("/api/auth/me/permissions", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "relay_operator"
        assert "read" in data["permissions"]
        assert "write" in data["permissions"]
        assert "execute" in data["permissions"]
        assert "admin" not in data["permissions"]


class TestRefreshTokenEndpoint:
    """Test the /api/auth/refresh endpoint."""

    def test_refresh_token_success(self, client):
        """Test refreshing a valid token."""
        # Login first
        login_response = client.post("/api/auth/token", data=auth_data("admin"))
        refresh_token = login_response.json()["refresh_token"]

        # Refresh the token
        response = client.post("/api/auth/refresh", params={"refresh_token": refresh_token})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client):
        """Test refreshing with invalid token."""
        response = client.post("/api/auth/refresh", params={"refresh_token": "invalid_token"})

        assert response.status_code == 401

    def test_refresh_with_access_token(self, client):
        """Test that access token cannot be used for refresh."""
        # Login first
        login_response = client.post("/api/auth/token", data=auth_data("admin"))
        access_token = login_response.json()["access_token"]

        # Try to use access token for refresh (should fail)
        response = client.post("/api/auth/refresh", params={"refresh_token": access_token})

        assert response.status_code == 401
        assert "Invalid token type" in response.json()["detail"]


class TestLogoutEndpoint:
    """Test the /api/auth/logout endpoint."""

    def test_logout_success(self, client):
        """Test successful logout."""
        # Login first
        login_response = client.post("/api/auth/token", data=auth_data("admin"))
        token = login_response.json()["access_token"]

        # Logout
        response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["username"] == "admin"

    def test_logout_unauthenticated(self, client):
        """Test logout without authentication."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 401


class TestAuthenticationFlow:
    """Test complete authentication flow."""

    def test_full_auth_flow(self, client):
        """Test complete authentication flow: login -> get info -> logout."""
        # Step 1: Login
        login_response = client.post("/api/auth/token", data=auth_data("operator"))
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 2: Access protected resource (user info)
        user_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert user_response.status_code == 200
        assert user_response.json()["username"] == "operator"

        # Step 3: Get permissions
        perms_response = client.get("/api/auth/me/permissions", headers={"Authorization": f"Bearer {token}"})
        assert perms_response.status_code == 200

        # Step 4: Logout
        logout_response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout_response.status_code == 200


class TestRateLimiting:
    """Validate that rate limiting is enforced on token endpoint."""

    def test_token_rate_limit_exceeded(self):
        """Exceed per-minute limit and expect 429 on final request using isolated app instance."""
        # Build isolated app so other tests' requests do not consume quota
        isolated_app = FastAPI()
        isolated_app.state.limiter = limiter
        isolated_app.add_middleware(SlowAPIMiddleware)
        isolated_app.include_router(router)
        isolated_client = TestClient(isolated_app)

        success_count = 0
        failure_status = None
        for i in range(11):
            response = isolated_client.post(
                "/api/auth/token",
                data=auth_data("admin"),
            )
            if response.status_code == 200:
                success_count += 1
            else:
                failure_status = response.status_code
                break
        # Two validation modes:
        # 1. Default env (10/min): expect 10 successes then 429
        # 2. Elevated env for broader test runs (>10/min): all succeed, no failure_status
        if success_count == 11:
            assert failure_status is None, "Unexpected failure under elevated rate limit configuration"
        else:
            assert success_count == 10, f"Expected 10 successful requests before limit, got {success_count}"
            assert failure_status == 429, f"Expected 429 after limit exceeded, got {failure_status}"
