"""
Authentication API Routes

Provides OAuth2 authentication endpoints for token management.
"""

from datetime import timedelta
import json
import os
from pathlib import Path
import time
from typing import Any, Dict, Mapping, Optional

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


AUTH_USERS_JSON_ENV = "AURORA_AUTH_USERS_JSON"
AUTH_USERS_FILE_ENV = "AURORA_AUTH_USERS_FILE"
ALLOW_DEV_AUTH_FIXTURE_ENV = "AURORA_ALLOW_DEV_AUTH_FIXTURE"

DEV_AUTH_FIXTURE_USERS: Dict[str, Dict[str, str]] = {
    "admin": {
        "email": "admin@aurora.local",
        "full_name": "System Administrator",
        "role": Role.ADMIN.value,
        "password_env": "AURORA_DEV_ADMIN_PASSWORD",
    },
    "operator": {
        "email": "operator@aurora.local",
        "full_name": "Relay Operator",
        "role": Role.RELAY_OPERATOR.value,
        "password_env": "AURORA_DEV_OPERATOR_PASSWORD",
    },
    "observer": {
        "email": "observer@aurora.local",
        "full_name": "System Observer",
        "role": Role.OBSERVER.value,
        "password_env": "AURORA_DEV_OBSERVER_PASSWORD",
    },
}


def build_auth_users_db(env: Optional[Mapping[str, str]] = None) -> Dict[str, UserInDB]:
    """Build the mounted auth user database from explicit configuration."""
    env_map = env if env is not None else os.environ
    configured_payload = _load_auth_users_payload(env_map)
    if configured_payload:
        return _build_users_from_payload(configured_payload, env_map)

    if _truthy(env_map.get(ALLOW_DEV_AUTH_FIXTURE_ENV)):
        return _build_users_from_payload(DEV_AUTH_FIXTURE_USERS, env_map)

    raise RuntimeError(
        "AURORA auth users are not configured. Set AURORA_AUTH_USERS_JSON or "
        "AURORA_AUTH_USERS_FILE with user password hashes, or explicitly set "
        "AURORA_ALLOW_DEV_AUTH_FIXTURE=true in dev/test with AURORA_DEV_*_PASSWORD secrets."
    )


def _load_auth_users_payload(env: Mapping[str, str]) -> Dict[str, Mapping[str, Any]]:
    raw_payload = env.get(AUTH_USERS_JSON_ENV)
    payload_file = env.get(AUTH_USERS_FILE_ENV)
    if raw_payload and payload_file:
        raise RuntimeError("Set only one of AURORA_AUTH_USERS_JSON or AURORA_AUTH_USERS_FILE.")
    if payload_file:
        raw_payload = Path(payload_file).read_text(encoding="utf-8")
    if not raw_payload:
        return {}
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid auth user JSON: {exc}") from exc
    return _normalise_user_payload(payload)


def _normalise_user_payload(payload: Any) -> Dict[str, Mapping[str, Any]]:
    if isinstance(payload, Mapping):
        return {str(username): record for username, record in payload.items() if isinstance(record, Mapping)}
    if isinstance(payload, list):
        users: Dict[str, Mapping[str, Any]] = {}
        for record in payload:
            if not isinstance(record, Mapping):
                raise RuntimeError("Auth user list entries must be objects.")
            username = record.get("username")
            if not username:
                raise RuntimeError("Auth user list entries must include username.")
            users[str(username)] = record
        return users
    raise RuntimeError("Auth user configuration must be a JSON object or list.")


def _build_users_from_payload(
    payload: Mapping[str, Mapping[str, Any]], env: Mapping[str, str]
) -> Dict[str, UserInDB]:
    if not payload:
        raise RuntimeError("Auth user configuration did not contain any users.")

    users: Dict[str, UserInDB] = {}
    for username, record in payload.items():
        role = _coerce_role(str(record.get("role", Role.OBSERVER.value)), username)
        users[username] = UserInDB(
            username=username,
            email=record.get("email"),
            full_name=record.get("full_name"),
            role=role,
            hashed_password=_resolve_password_hash(username, record, env),
            disabled=bool(record.get("disabled", False)),
        )
    return users


def _resolve_password_hash(username: str, record: Mapping[str, Any], env: Mapping[str, str]) -> str:
    configured_hash = record.get("password_hash") or record.get("hashed_password")
    if configured_hash:
        return str(configured_hash)

    password_env = record.get("password_env")
    if not password_env:
        raise RuntimeError(f"Auth user {username!r} must define password_hash or password_env.")
    password = env.get(str(password_env))
    if not password:
        raise RuntimeError(f"Auth user {username!r} password env {password_env!r} is not set.")
    return OAuth2Handler.get_password_hash(password)


def _coerce_role(raw_role: str, username: str) -> Role:
    try:
        return Role(raw_role)
    except ValueError as exc:
        raise RuntimeError(f"Auth user {username!r} has invalid role {raw_role!r}.") from exc


def _truthy(value: Optional[str]) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


USERS_DB = build_auth_users_db()


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Internal server error")


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
