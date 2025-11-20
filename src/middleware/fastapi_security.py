"""
FastAPI Security Middleware Module

Centralized security configuration for Aurora CloudBank Symbolic API.
Provides rate limiting, CSRF protection, CORS middleware, and authentication utilities.

Usage:
    from src.middleware.fastapi_security import security, limiter, setup_cors_middleware

Design follows defense-in-depth principles with:
- Rate limiting via slowapi
- CSRF token validation via HTTPBearer
- CORS configuration for cross-origin requests
- Secure comparison utilities for timing-attack resistance
"""

from functools import wraps
from typing import Optional, List
import hmac
import hashlib
import os
import time
import re

from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Callable


# ================================
# Rate Limiting Configuration
# ================================

def _composite_key_factory(strategy: str) -> Callable:
    """Return a key function based on strategy.

    Strategies:
        ip       -> client IP only (default)
        ip_user  -> client IP + authenticated user (JWT sub) when available
    """
    def key_func(request):  # pragma: no cover - simple deterministic key builder
        base_ip = get_remote_address(request)
        if strategy != "ip_user":
            return base_ip
        user_part = "anonymous"
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
            try:  # decode token for subject
                from src.security.oauth2 import OAuth2Handler  # local import to avoid circular during startup
                payload = OAuth2Handler.decode_token(token)
                sub = payload.get("sub")
                if sub:
                    user_part = sub
            except Exception:
                pass
        return f"{base_ip}:{user_part}"
    return key_func


def get_rate_limiter() -> Limiter | object:
    """Create and configure rate limiter for API endpoints.

    Environment Variables:
        RATE_LIMIT_ENABLED (default: true) -> disable limiter entirely if false
        RATE_LIMIT_KEY_STRATEGY (ip|ip_user) -> key function selection
        REDIS_URL -> optional Redis backend (e.g., redis://localhost:6379)
    """
    enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    if not enabled:
        class NoOpLimiter:  # pragma: no cover - trivial passthrough
            def limit(self, *args, **kwargs):
                def decorator(func):
                    return func
                return decorator
        return NoOpLimiter()

    strategy = os.getenv("RATE_LIMIT_KEY_STRATEGY", "ip")
    redis_url = os.getenv("REDIS_URL")
    key_func = _composite_key_factory(strategy)

    # Attempt Redis-backed limiter if URL provided; fall back to in-memory
    try:
        if redis_url:
            return Limiter(key_func=key_func, storage_uri=redis_url)
    except Exception:  # pragma: no cover - graceful fallback
        pass
    return Limiter(key_func=key_func)


# Global rate limiter instance (may be NoOpLimiter)
limiter = get_rate_limiter()


# ================================
# CSRF Protection
# ================================

# HTTPBearer security scheme for CSRF token validation
security = HTTPBearer()

# Get CSRF secret from environment
CSRF_SECRET_KEY = os.getenv("CSRF_SECRET_KEY")
if not CSRF_SECRET_KEY:
    raise RuntimeError(
        "CSRF_SECRET_KEY environment variable must be set to a strong, unpredictable value. "
        "Refusing to start with default or missing secret."
    )
CSRF_TOKEN_EXPIRY_SECONDS = 300  # 5 minutes
CSRF_CLOCK_SKEW_GRACE_SECONDS = 30  # Grace period for clock skew between client and server


def generate_csrf_token(session_id: str) -> str:
    """
    Generate a cryptographically secure CSRF token.

    Token format: session_id.timestamp.signature

    Args:
        session_id: Unique session identifier

    Returns:
        CSRF token string
    """
    timestamp = str(int(time.time()))
    message = f"{session_id}.{timestamp}"
    signature = hmac.new(
        CSRF_SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{session_id}.{timestamp}.{signature}"


def verify_csrf_token(token: HTTPAuthorizationCredentials, session_id: Optional[str] = None) -> None:
    """
    Verify CSRF token with cryptographic validation.

    SECURITY FIX: Replaces length-only check with HMAC verification.

    Args:
        token: HTTPAuthorizationCredentials from request
        session_id: Optional session ID for binding validation

    Raises:
        HTTPException: If token is missing, expired, or invalid (403)
    """
    if not token:
        raise HTTPException(status_code=403, detail='Missing CSRF token')

    try:
        # Parse token format: session_id.timestamp.signature
        parts = token.credentials.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        token_session_id, timestamp, signature = parts

        # Verify session ID matches if provided
        if session_id and token_session_id != session_id:
            raise HTTPException(status_code=403, detail='Token session mismatch')

        # Check expiration (5 minutes) with grace period for clock skew
        # Grace period allows for minor time synchronization differences between client and server
        token_time = int(timestamp)
        current_time = int(time.time())
        age = current_time - token_time
        if age < -CSRF_CLOCK_SKEW_GRACE_SECONDS:
            raise HTTPException(status_code=403, detail='CSRF token timestamp invalid')
        if age > CSRF_TOKEN_EXPIRY_SECONDS + CSRF_CLOCK_SKEW_GRACE_SECONDS:
            raise HTTPException(status_code=403, detail='CSRF token expired')

        # Verify HMAC signature
        expected_message = f"{token_session_id}.{timestamp}"
        expected_signature = hmac.new(
            CSRF_SECRET_KEY.encode(),
            expected_message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=403, detail='Invalid CSRF token signature')

    except ValueError:
        raise HTTPException(status_code=403, detail='Invalid CSRF token format')
    except HTTPException:
        raise
    except Exception:
        # Log error securely without exposing details to client
        raise HTTPException(status_code=403, detail='CSRF token validation failed')


# ================================
# WebSocket Authentication
# ================================

# Get WebSocket auth secret from environment
WS_AUTH_SECRET = os.getenv("WS_AUTH_SECRET")
if not WS_AUTH_SECRET or WS_AUTH_SECRET == "default-ws-secret-change-in-production":
    raise RuntimeError(
        "WS_AUTH_SECRET environment variable must be set to a secure random value. "
        "Do not use the default or leave it unset. Refusing to start."
    )
WS_TOKEN_EXPIRY_SECONDS = 3600  # 1 hour

# Maximum length for request_id to prevent DoS attacks
MAX_REQUEST_ID_LENGTH = 128

# Compiled regex for request_id validation (performance optimization)
REQUEST_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

# Whitelist of allowed tool names for WebSocket execution.
# Each entry maps a tool name to a description and rationale for why it is allowed.
ALLOWED_WS_TOOLS = {
    "session_management": (
        "Allows clients to manage their session state (e.g., start/end session). "
        "Required for secure session lifecycle management."
    ),
    "get_status": (
        "Returns the current status of the WebSocket connection or server. "
        "Permitted for health checks and client diagnostics."
    ),
    "list_tools": (
        "Lists all available tools that the client can invoke. "
        "Necessary for client-side tool discovery; does not execute any tool."
    ),
    "echo": (
        "Echoes back the received message. "
        "Used for connectivity testing and debugging; no side effects."
    ),
    "ping": (
        "Responds with a pong to verify connection liveness. "
        "Standard for WebSocket keepalive and latency measurement."
    ),
}

# Set of allowed tool names for quick membership checks
ALLOWED_WS_TOOL_NAMES = set(ALLOWED_WS_TOOLS.keys())

def generate_ws_token(client_id: str) -> str:
    """
    Generate a cryptographically secure WebSocket authentication token.

    Token format: client_id.timestamp.signature

    Args:
        client_id: Unique client identifier

    Returns:
        WebSocket token string
    """
    timestamp = str(int(time.time()))
    message = f"{client_id}.{timestamp}"
    signature = hmac.new(
        WS_AUTH_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{client_id}.{timestamp}.{signature}"


def verify_ws_token(token: str) -> Optional[str]:
    """
    Verify WebSocket authentication token.

    Args:
        token: WebSocket token string

    Returns:
        Client ID if valid, None otherwise
    """
    if not token:
        return None

    try:
        # Parse token format: client_id.timestamp.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None

        client_id, timestamp, signature = parts

        # Check expiration
        token_time = int(timestamp)
        current_time = int(time.time())
        if current_time - token_time > WS_TOKEN_EXPIRY_SECONDS:
            return None

        # Verify HMAC signature
        expected_message = f"{client_id}.{timestamp}"
        expected_signature = hmac.new(
            WS_AUTH_SECRET.encode(),
            expected_message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison
        if not hmac.compare_digest(signature, expected_signature):
            return None

        return client_id

    except Exception:
        return None


def validate_ws_tool(tool_name: str) -> bool:
    """
    Validate if a tool is allowed for WebSocket execution.

    Args:
        tool_name: Name of the tool to validate

    Returns:
        True if tool is allowed, False otherwise
    """
    return tool_name in ALLOWED_WS_TOOLS


def sanitize_request_id(request_id: Optional[str]) -> Optional[str]:
    """
    Sanitize and validate request_id to prevent injection attacks and log pollution.

    SECURITY: Validates that request_id matches expected format (UUID or alphanumeric)
    to prevent injection attacks or log pollution.

    Args:
        request_id: Request ID from client (can be None)

    Returns:
        Sanitized request_id if valid, None if invalid or missing
    """
    if not request_id:
        return None

    # Enforce maximum length to prevent DoS
    if len(request_id) > MAX_REQUEST_ID_LENGTH:
        return None

    # Allow only alphanumeric characters, hyphens, and underscores
    # This covers UUID format and most standard request ID patterns
    if not REQUEST_ID_PATTERN.match(request_id):
        return None

    return request_id


def sanitize_session_id(session_id: Optional[str]) -> Optional[str]:
    """Sanitize and validate session_id similarly to request_id.

    SECURITY: Enforces same character and length constraints used for request_id
    so that any downstream binding (e.g., CSRF token session binding) cannot be
    abused for log injection or resource exhaustion.

    Args:
        session_id: Raw session identifier from client.

    Returns:
        Sanitized session_id if valid; None otherwise.
    """
    if not session_id:
        return None
    if len(session_id) > MAX_REQUEST_ID_LENGTH:  # Reuse same cap
        return None
    if not REQUEST_ID_PATTERN.match(session_id):
        return None
    return session_id


# ================================
# CORS Middleware Configuration
# ================================

def setup_cors_middleware(app, allow_origins=None, allow_credentials=True,
                          allow_methods=None, allow_headers=None):
    """
    Configure CORS middleware for FastAPI application.

    Args:
        app: FastAPI application instance
        allow_origins: List of allowed origins (default: ["*"])
        allow_credentials: Whether to allow credentials (default: True)
        allow_methods: List of allowed HTTP methods (default: ["*"])
        allow_headers: List of allowed headers (default: ["*"])

    Returns:
        None (modifies app in place)
    """
    # SECURITY FIX: Use secure defaults instead of wildcards
    if allow_origins is None:
        # Get from environment or use localhost defaults
        origins_str = os.getenv("ALLOWED_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
        allow_origins = [origin.strip() for origin in origins_str.split(",")]
    if allow_methods is None:
        allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    if allow_headers is None:
        allow_headers = ["Content-Type", "Authorization", "X-CSRF-Token"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        max_age=86400,  # Cache preflight for 24 hours
    )


# ================================
# Authentication Utilities
# ================================

def require_auth(roles: Optional[List[str]] = None):
    """
    Decorator for requiring authentication with optional role check.
    Placeholder for actual authentication logic.

    Args:
        roles: Optional list of required roles

    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Add actual auth logic here
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def secure_compare(a: str, b: str) -> bool:
    """
    Timing-safe string comparison to prevent timing attacks.

    Args:
        a: First string to compare
        b: Second string to compare

    Returns:
        bool: True if strings are equal, False otherwise
    """
    return hmac.compare_digest(a.encode(), b.encode())
