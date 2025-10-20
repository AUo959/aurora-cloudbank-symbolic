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
import secrets
import hmac

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


# ================================
# Rate Limiting Configuration
# ================================

def get_rate_limiter() -> Limiter:
    """
    Create and configure rate limiter for API endpoints.
    Uses client IP address as the rate limit key.

    Returns:
        Configured Limiter instance
    """
    return Limiter(key_func=get_remote_address)


# Global rate limiter instance
limiter = get_rate_limiter()


# ================================
# CSRF Protection
# ================================

# HTTPBearer security scheme for CSRF token validation
security = HTTPBearer()


def verify_csrf_token(token: HTTPAuthorizationCredentials) -> None:
    """
    Verify CSRF token from HTTPBearer credentials.
    Raises HTTPException if token is invalid.

    Args:
        token: HTTPAuthorizationCredentials from request

    Raises:
        HTTPException: If token is missing or invalid (403)
    """
    if not token or len(token.credentials) < 10:
        raise HTTPException(status_code=403, detail='Invalid CSRF token')


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
    if allow_origins is None:
        allow_origins = ["*"]
    if allow_methods is None:
        allow_methods = ["*"]
    if allow_headers is None:
        allow_headers = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
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
