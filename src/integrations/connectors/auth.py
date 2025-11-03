"""
Authentication Framework for External Tool Connectors

Provides flexible authentication patterns including OAuth, API keys,
and custom authentication with secure credential management.
"""

import hashlib
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AuthType(Enum):
    """Supported authentication types"""
    API_KEY = "api_key"
    OAUTH = "oauth"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"


@dataclass
class AuthConfig:
    """Configuration for authentication"""
    auth_type: AuthType
    credentials: Dict[str, Any] = field(default_factory=dict)
    # Secure credential storage options
    use_vault: bool = False
    vault_path: Optional[str] = None
    # Token refresh settings
    auto_refresh: bool = True
    refresh_threshold_seconds: int = 300
    # Aurora DLP tracking
    context_tag: str = field(default_factory=lambda: f"auth_{hashlib.sha256(os.urandom(16)).hexdigest()[:8]}")


class AuthProvider(ABC):
    """
    Abstract base class for authentication providers.

    Implements secure credential management following Aurora's
    ethical governance and DLP tracking protocols.
    """

    def __init__(self, config: AuthConfig):
        self.config = config
        self._authenticated = False
        self._auth_timestamp: Optional[str] = None
        self._token_expiry: Optional[str] = None

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Perform authentication.

        Returns:
            bool: True if authentication successful
        """
        pass

    @abstractmethod
    async def refresh(self) -> bool:
        """
        Refresh authentication credentials.

        Returns:
            bool: True if refresh successful
        """
        pass

    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for authenticated requests.

        Returns:
            Dict of HTTP headers
        """
        pass

    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self._authenticated

    def needs_refresh(self) -> bool:
        """
        Check if authentication needs refresh.

        Returns:
            bool: True if refresh needed
        """
        if not self._authenticated or not self._token_expiry:
            return False

        # Simplified check - in production, compare with current time
        return False

    def get_auth_metadata(self) -> Dict[str, Any]:
        """
        Get authentication metadata for DLP tracking.

        Returns:
            Dict containing auth metadata (without sensitive credentials)
        """
        return {
            "context_tag": self.config.context_tag,
            "auth_type": self.config.auth_type.value,
            "authenticated": self._authenticated,
            "auth_timestamp": self._auth_timestamp,
            "token_expiry": self._token_expiry,
            "auto_refresh": self.config.auto_refresh,
            "use_vault": self.config.use_vault,
            "dlp_level": "DLP_L1_OK",
        }


class APIKeyAuth(AuthProvider):
    """API Key authentication provider"""

    def __init__(self, config: AuthConfig):
        super().__init__(config)
        self._api_key = config.credentials.get("api_key")
        self._header_name = config.credentials.get("header_name", "X-API-Key")

    async def authenticate(self) -> bool:
        """Validate API key availability"""
        if not self._api_key:
            return False

        self._authenticated = True
        self._auth_timestamp = datetime.utcnow().isoformat()
        return True

    async def refresh(self) -> bool:
        """API keys typically don't need refresh"""
        return self._authenticated

    def get_auth_headers(self) -> Dict[str, str]:
        """Get API key headers"""
        if not self._authenticated:
            return {}
        return {self._header_name: self._api_key}


class OAuthAuth(AuthProvider):
    """OAuth 2.0 authentication provider"""

    def __init__(self, config: AuthConfig):
        super().__init__(config)
        self._client_id = config.credentials.get("client_id")
        self._client_secret = config.credentials.get("client_secret")
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

    async def authenticate(self) -> bool:
        """
        Perform OAuth authentication flow.

        Note: This is a simplified implementation. Production code should
        implement full OAuth flow with PKCE, state validation, etc.
        """
        if not self._client_id or not self._client_secret:
            return False

        # Placeholder for OAuth flow
        # In production: redirect to auth URL, handle callback, exchange code for token
        self._authenticated = True
        self._auth_timestamp = datetime.utcnow().isoformat()
        return True

    async def refresh(self) -> bool:
        """Refresh OAuth access token"""
        if not self._refresh_token:
            return False

        # Placeholder for token refresh
        # In production: POST to token endpoint with refresh_token grant
        return True

    def get_auth_headers(self) -> Dict[str, str]:
        """Get OAuth bearer token headers"""
        if not self._authenticated or not self._access_token:
            return {}
        return {"Authorization": f"Bearer {self._access_token}"}


class BearerTokenAuth(AuthProvider):
    """Bearer token authentication provider"""

    def __init__(self, config: AuthConfig):
        super().__init__(config)
        self._token = config.credentials.get("token")

    async def authenticate(self) -> bool:
        """Validate bearer token"""
        if not self._token:
            return False

        self._authenticated = True
        self._auth_timestamp = datetime.utcnow().isoformat()
        return True

    async def refresh(self) -> bool:
        """Bearer tokens typically don't auto-refresh"""
        return self._authenticated

    def get_auth_headers(self) -> Dict[str, str]:
        """Get bearer token headers"""
        if not self._authenticated:
            return {}
        return {"Authorization": f"Bearer {self._token}"}


class BasicAuth(AuthProvider):
    """Basic HTTP authentication provider"""

    def __init__(self, config: AuthConfig):
        super().__init__(config)
        self._username = config.credentials.get("username")
        self._password = config.credentials.get("password")

    async def authenticate(self) -> bool:
        """Validate basic auth credentials"""
        if not self._username or not self._password:
            return False

        self._authenticated = True
        self._auth_timestamp = datetime.utcnow().isoformat()
        return True

    async def refresh(self) -> bool:
        """Basic auth doesn't need refresh"""
        return self._authenticated

    def get_auth_headers(self) -> Dict[str, str]:
        """Get basic auth headers"""
        if not self._authenticated:
            return {}

        import base64
        credentials = f"{self._username}:{self._password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}


def create_auth_provider(auth_type: AuthType, credentials: Dict[str, Any]) -> AuthProvider:
    """
    Factory function to create appropriate auth provider.

    Args:
        auth_type: Type of authentication
        credentials: Authentication credentials

    Returns:
        AuthProvider instance
    """
    config = AuthConfig(auth_type=auth_type, credentials=credentials)

    if auth_type == AuthType.API_KEY:
        return APIKeyAuth(config)
    elif auth_type == AuthType.OAUTH:
        return OAuthAuth(config)
    elif auth_type == AuthType.BEARER_TOKEN:
        return BearerTokenAuth(config)
    elif auth_type == AuthType.BASIC_AUTH:
        return BasicAuth(config)
    else:
        raise ValueError(f"Unsupported auth type: {auth_type}")
