"""
Tests for OAuth2 authentication functionality.

Tests JWT token creation, validation, and OAuth2 flow.

Note: Test credentials and secrets are intentionally hardcoded for testing purposes only.
These are not production credentials and are safe for test environments.
SonarCloud security hotspots are acknowledged and accepted.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from src.security.oauth2 import OAuth2Handler, Token, TokenData, User, UserInDB, get_current_user, SECRET_KEY, ALGORITHM
from src.security.roles import Role


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpass123"
        hashed = OAuth2Handler.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash prefix

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpass123"
        hashed = OAuth2Handler.get_password_hash(password)

        assert OAuth2Handler.verify_password(password, hashed)

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpass123"
        hashed = OAuth2Handler.get_password_hash(password)

        assert not OAuth2Handler.verify_password("wrongpass", hashed)


class TestTokenCreation:
    """Test JWT token creation."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "testuser", "role": "admin"}
        token = OAuth2Handler.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_expiry(self):
        """Test creating an access token with custom expiry."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = OAuth2Handler.create_access_token(data, expires_delta)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])

        # Check expiry is approximately 15 minutes from issued time
        time_diff = (exp_time - iat_time).total_seconds()
        assert 14 * 60 < time_diff < 16 * 60  # Allow 1 minute tolerance

    def test_create_refresh_token(self):
        """Test creating a refresh token."""
        data = {"sub": "testuser", "role": "observer"}
        token = OAuth2Handler.create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["role"] == "observer"
        assert payload["type"] == "refresh"
        assert "exp" in payload


class TestTokenDecoding:
    """Test JWT token decoding and validation."""

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "testuser", "role": "admin"}
        token = OAuth2Handler.create_access_token(data)

        payload = OAuth2Handler.decode_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    def test_decode_expired_token(self):
        """Test decoding an expired token."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = OAuth2Handler.create_access_token(data, expires_delta)

        with pytest.raises(Exception):  # Should raise HTTPException
            OAuth2Handler.decode_token(token)

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"

        with pytest.raises(Exception):  # Should raise HTTPException
            OAuth2Handler.decode_token(invalid_token)


class TestUserAuthentication:
    """Test user authentication logic."""

    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        password = "testpass"
        hashed = OAuth2Handler.get_password_hash(password)

        user_db = {
            "testuser": UserInDB(
                username="testuser", email="test@example.com", role=Role.ADMIN, hashed_password=hashed, disabled=False
            )
        }

        user = OAuth2Handler.authenticate_user("testuser", password, user_db)
        assert user is not None
        assert user.username == "testuser"
        assert user.role == Role.ADMIN

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        password = "testpass"
        hashed = OAuth2Handler.get_password_hash(password)

        user_db = {
            "testuser": UserInDB(
                username="testuser", email="test@example.com", role=Role.ADMIN, hashed_password=hashed, disabled=False
            )
        }

        user = OAuth2Handler.authenticate_user("testuser", "wrongpass", user_db)
        assert user is None

    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user."""
        user_db = {}

        user = OAuth2Handler.authenticate_user("nonexistent", "password", user_db)
        assert user is None


class TestTokenModels:
    """Test Pydantic models for tokens."""

    def test_token_model(self):
        """Test Token model creation."""
        token = Token(access_token="test_token", token_type="bearer", expires_in=1800)

        assert token.access_token == "test_token"
        assert token.token_type == "bearer"
        assert token.expires_in == 1800
        assert token.refresh_token is None

    def test_token_with_refresh(self):
        """Test Token model with refresh token."""
        token = Token(access_token="access_token", refresh_token="refresh_token")

        assert token.refresh_token == "refresh_token"

    def test_token_data_model(self):
        """Test TokenData model creation."""
        token_data = TokenData(username="testuser", role="admin", exp=datetime.utcnow())

        assert token_data.username == "testuser"
        assert token_data.role == "admin"
        assert isinstance(token_data.exp, datetime)


class TestUserModels:
    """Test user-related Pydantic models."""

    def test_user_model(self):
        """Test User model creation."""
        user = User(
            username="testuser", email="test@example.com", full_name="Test User", role=Role.OBSERVER, disabled=False
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == Role.OBSERVER
        assert not user.disabled

    def test_user_model_defaults(self):
        """Test User model with default values."""
        user = User(username="testuser")

        assert user.username == "testuser"
        assert user.role == Role.OBSERVER
        assert not user.disabled
        assert user.email is None

    def test_user_in_db_model(self):
        """Test UserInDB model creation."""
        user = UserInDB(
            username="testuser",
            email="test@example.com",
            role=Role.ADMIN,
            hashed_password="$2b$12$hash",
            disabled=False,
        )

        assert user.username == "testuser"
        assert user.hashed_password == "$2b$12$hash"
        assert user.role == Role.ADMIN


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Test get_current_user dependency."""

    async def test_get_current_user_valid_token(self):
        """Test getting current user with valid token."""
        data = {"sub": "testuser", "role": "admin"}
        token = OAuth2Handler.create_access_token(data)

        user = await get_current_user(token)

        assert user.username == "testuser"
        assert user.role == Role.ADMIN

    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        with pytest.raises(Exception):  # Should raise HTTPException
            await get_current_user("invalid_token")

    async def test_get_current_user_missing_subject(self):
        """Test getting current user with token missing subject."""
        # Create token without 'sub' claim
        token = jwt.encode(
            {"role": "admin", "exp": datetime.utcnow() + timedelta(minutes=15)}, SECRET_KEY, algorithm=ALGORITHM
        )

        with pytest.raises(Exception):  # Should raise HTTPException
            await get_current_user(token)
