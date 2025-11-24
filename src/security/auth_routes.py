"""
Authentication API Routes

Provides OAuth2 authentication endpoints for token management.
"""

from datetime import timedelta
import time
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.security.oauth2 import (
    OAuth2Handler,
    Token,
    User,
    UserInDB,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.middleware.fastapi_security import limiter
import os
from src.security.roles import Role, get_all_permissions

# Ensure fresh rate limiter storage for isolated test app constructions.
# Some pytest scenarios build multiple FastAPI app instances sharing the global
# limiter object, which can retain counters across tests and cause an immediate
# 429 on the first request of a new app. We defensively flush storage if supported.
try:  # pragma: no cover - best effort cleanup, harmless if unsupported
    storage = getattr(limiter, "_storage", None) or getattr(limiter, "storage", None)
    if storage and hasattr(storage, "flush"):
        storage.flush()
except Exception:
    pass


# Router for authentication endpoints
router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)


# In-memory user database for demonstration
# In production, replace with actual database
USERS_DB: Dict[str, UserInDB] = {
    "admin": UserInDB(
        username="admin",
        email="admin@aurora.local",
        full_name="System Administrator",
        role=Role.ADMIN,
        hashed_password=OAuth2Handler.get_password_hash("admin123"),  # Change in production!
        disabled=False,
    ),
    "operator": UserInDB(
        username="operator",
        email="operator@aurora.local",
        full_name="Relay Operator",
        role=Role.RELAY_OPERATOR,
        hashed_password=OAuth2Handler.get_password_hash("operator123"),  # Change in production!
        disabled=False,
    ),
    "observer": UserInDB(
        username="observer",
        email="observer@aurora.local",
        full_name="System Observer",
        role=Role.OBSERVER,
        hashed_password=OAuth2Handler.get_password_hash("observer123"),  # Change in production!
        disabled=False,
    ),
}


# Rate limit configuration:
# By default use production-like limits. Optional elevation only when explicitly requested.
AUTH_TOKEN_PER_MINUTE = int(os.getenv("RATE_LIMIT_AUTH_TOKEN_PER_MIN", "10"))
AUTH_REFRESH_PER_MINUTE = int(os.getenv("RATE_LIMIT_AUTH_REFRESH_PER_MIN", "30"))

if os.getenv("AURORA_ELEVATED_AUTH_LIMITS", "false").lower() == "true":  # pragma: no cover
    AUTH_TOKEN_PER_MINUTE = int(os.getenv("ELEVATED_AUTH_TOKEN_PER_MIN", "1000"))
    AUTH_REFRESH_PER_MINUTE = int(os.getenv("ELEVATED_AUTH_REFRESH_PER_MIN", "2000"))

# Dynamic per-minute token counting to honor runtime overrides in test utilities that
# adjust RATE_LIMIT_AUTH_TOKEN_PER_MIN after module import (decorator is static).
_dynamic_token_counts: Dict[str, int] = {}


def _enforce_dynamic_token_limit(request: Request) -> None:
    desired_limit = int(os.getenv("RATE_LIMIT_AUTH_TOKEN_PER_MIN", str(AUTH_TOKEN_PER_MINUTE)))
    if desired_limit >= AUTH_TOKEN_PER_MINUTE:
        return  # Static decorator already sufficient or widened limit
    # Build window key using remote address and current minute bucket
    try:
        remote_ip = request.client.host if request.client else "unknown"
    except Exception:
        remote_ip = "unknown"
    minute_bucket = int(time.time() // 60)
    window_key = f"{remote_ip}:{minute_bucket}"
    current = _dynamic_token_counts.get(window_key, 0)
    if current >= desired_limit:
        # Manual HTTP 429 with standard headers (mirrors rate_limit_handler output)
        from fastapi import HTTPException
        headers = {"Retry-After": "60", "X-RateLimit-Limit": str(desired_limit)}
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers=headers)
    _dynamic_token_counts[window_key] = current + 1


@router.post("/token", response_model=Token)
@limiter.limit(f"{AUTH_TOKEN_PER_MINUTE}/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):  # request required for limiter
    """
    OAuth2 compatible token endpoint.

    Authenticates user and returns JWT access and refresh tokens.

    Args:
        form_data: OAuth2 form with username and password

    Returns:
        Token object with access_token and refresh_token

    Raises:
        HTTPException: If authentication fails
    """
    # Dynamic override enforcement (must occur before auth evaluation)
    _enforce_dynamic_token_limit(request)

    user = OAuth2Handler.authenticate_user(form_data.username, form_data.password, USERS_DB)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User account is disabled")

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = OAuth2Handler.create_access_token(
        data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = OAuth2Handler.create_refresh_token(data={"sub": user.username, "role": user.role.value})

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
@limiter.limit(f"{AUTH_REFRESH_PER_MINUTE}/minute")
async def refresh_token(request: Request, refresh_token: str):  # request required for limiter
    """
    Refresh an access token using a refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        New Token object with fresh access_token

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        payload = OAuth2Handler.decode_token(refresh_token)

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        username = payload.get("sub")
        role = payload.get("role")

        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = OAuth2Handler.create_access_token(
            data={"sub": username, "role": role}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer", expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not refresh token: {str(e)}")


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information.

    Args:
        current_user: Current user from token

    Returns:
        User object with current user data
    """
    return current_user


@router.get("/me/permissions")
async def read_users_permissions(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's permissions.

    Args:
        current_user: Current user from token

    Returns:
        Dict with user role and permissions
    """
    permissions = get_all_permissions(current_user.role)
    return {
        "username": current_user.username,
        "role": current_user.role.value,
        "permissions": [p.value for p in permissions],
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint (client-side token removal).

    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. For true server-side logout, implement
    a token blacklist with Redis or similar.

    Args:
        current_user: Current user from token

    Returns:
        Success message
    """
    return {"message": "Successfully logged out", "username": current_user.username}
