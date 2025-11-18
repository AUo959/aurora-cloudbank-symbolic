"""
Authentication API Routes

Provides OAuth2 authentication endpoints for token management.
"""

from datetime import timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.security.oauth2 import (
    OAuth2Handler,
    Token,
    User,
    UserInDB,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.security.roles import Role, get_all_permissions


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
        disabled=False
    ),
    "operator": UserInDB(
        username="operator",
        email="operator@aurora.local",
        full_name="Relay Operator",
        role=Role.RELAY_OPERATOR,
        hashed_password=OAuth2Handler.get_password_hash("operator123"),  # Change in production!
        disabled=False
    ),
    "observer": UserInDB(
        username="observer",
        email="observer@aurora.local",
        full_name="System Observer",
        role=Role.OBSERVER,
        hashed_password=OAuth2Handler.get_password_hash("observer123"),  # Change in production!
        disabled=False
    ),
}


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
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
    user = OAuth2Handler.authenticate_user(
        form_data.username,
        form_data.password,
        USERS_DB
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = OAuth2Handler.create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = OAuth2Handler.create_refresh_token(
        data={"sub": user.username, "role": user.role.value}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        username = payload.get("sub")
        role = payload.get("role")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = OAuth2Handler.create_access_token(
            data={"sub": username, "role": role},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not refresh token: {str(e)}"
        )


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
        "permissions": [p.value for p in permissions]
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
    return {
        "message": "Successfully logged out",
        "username": current_user.username
    }
