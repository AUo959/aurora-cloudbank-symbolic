"""
Integration tests for authentication API routes.

Tests OAuth2 endpoints and authentication flow.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.security.auth_routes import router, USERS_DB
from src.security.oauth2 import OAuth2Handler
from src.security.roles import Role


@pytest.fixture
def app():
    """Create a test FastAPI application."""
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestLoginEndpoint:
    """Test the /api/auth/token endpoint."""
    
    def test_login_success_admin(self, client):
        """Test successful login with admin credentials."""
        response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
    
    def test_login_success_operator(self, client):
        """Test successful login with operator credentials."""
        response = client.post(
            "/api/auth/token",
            data={"username": "operator", "password": "operator123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_success_observer(self, client):
        """Test successful login with observer credentials."""
        response = client.post(
            "/api/auth/token",
            data={"username": "observer", "password": "observer123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "wrong_password"}
        )
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/auth/token",
            data={"username": "nonexistent", "password": "password"}
        )
        
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
        login_response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Get user info
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
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
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestPermissionsEndpoint:
    """Test the /api/auth/me/permissions endpoint."""
    
    def test_get_permissions_admin(self, client):
        """Test getting permissions for admin user."""
        # Login as admin
        login_response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Get permissions
        response = client.get(
            "/api/auth/me/permissions",
            headers={"Authorization": f"Bearer {token}"}
        )
        
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
        login_response = client.post(
            "/api/auth/token",
            data={"username": "observer", "password": "observer123"}
        )
        token = login_response.json()["access_token"]
        
        # Get permissions
        response = client.get(
            "/api/auth/me/permissions",
            headers={"Authorization": f"Bearer {token}"}
        )
        
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
        login_response = client.post(
            "/api/auth/token",
            data={"username": "operator", "password": "operator123"}
        )
        token = login_response.json()["access_token"]
        
        # Get permissions
        response = client.get(
            "/api/auth/me/permissions",
            headers={"Authorization": f"Bearer {token}"}
        )
        
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
        login_response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh the token
        response = client.post(
            "/api/auth/refresh",
            params={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client):
        """Test refreshing with invalid token."""
        response = client.post(
            "/api/auth/refresh",
            params={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_refresh_with_access_token(self, client):
        """Test that access token cannot be used for refresh."""
        # Login first
        login_response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        access_token = login_response.json()["access_token"]
        
        # Try to use access token for refresh (should fail)
        response = client.post(
            "/api/auth/refresh",
            params={"refresh_token": access_token}
        )
        
        assert response.status_code == 401
        assert "Invalid token type" in response.json()["detail"]


class TestLogoutEndpoint:
    """Test the /api/auth/logout endpoint."""
    
    def test_logout_success(self, client):
        """Test successful logout."""
        # Login first
        login_response = client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
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
        login_response = client.post(
            "/api/auth/token",
            data={"username": "operator", "password": "operator123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 2: Access protected resource (user info)
        user_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert user_response.status_code == 200
        assert user_response.json()["username"] == "operator"
        
        # Step 3: Get permissions
        perms_response = client.get(
            "/api/auth/me/permissions",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert perms_response.status_code == 200
        
        # Step 4: Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_response.status_code == 200
