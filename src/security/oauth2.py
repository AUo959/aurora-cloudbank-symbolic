"""
OAuth2 Authentication Module

Provides JWT token-based authentication with role-based access control.
Implements OAuth2 password flow with secure token management.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel, Field

from src.security.roles import Role, Permission, check_permission


# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable must be set. "
        "Generate a strong random key (e.g., openssl rand -hex 32)"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None


class User(BaseModel):
    """User model with role-based permissions."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Role = Role.OBSERVER
    disabled: bool = False


class UserInDB(User):
    """User model with hashed password for database storage."""
    hashed_password: str


class OAuth2Handler:
    """
    Handler for OAuth2 authentication operations.
    
    Provides methods for token creation, validation, and user authentication.
    """
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        now = datetime.utcnow()
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": now,
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token with longer expiration.
        
        Args:
            data: Data to encode in the token
            
        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        now = datetime.utcnow()
        expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": now,
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded token payload
            
        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @classmethod
    def authenticate_user(
        cls,
        username: str,
        password: str,
        user_db: Dict[str, UserInDB]
    ) -> Optional[UserInDB]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Plain text password
            user_db: Dictionary of users (username -> UserInDB)
            
        Returns:
            UserInDB if authentication successful, None otherwise
        """
        user = user_db.get(username)
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: JWT token from request
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = OAuth2Handler.decode_token(token)
        username: str = payload.get("sub")
        role_str: str = payload.get("role")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(
            username=username,
            role=role_str,
            exp=payload.get("exp")
        )
    except JWTError:
        raise credentials_exception
    
    # In production, fetch user from database
    # For now, create user from token data
    user = User(
        username=token_data.username,
        role=Role(token_data.role) if token_data.role else Role.OBSERVER
    )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active (non-disabled) user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User object if active
        
    Raises:
        HTTPException: If user is disabled
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission for route access.
    
    Usage:
        @app.get("/admin/users")
        @require_permission(Permission.MANAGE_USERS)
        async def list_users(user: User = Depends(get_current_active_user)):
            ...
    
    Args:
        permission: Required permission
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), **kwargs):
            if not check_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """
    Decorator to require a specific role for route access.
    
    Usage:
        @app.get("/admin/config")
        @require_role(Role.ADMIN)
        async def get_config(user: User = Depends(get_current_active_user)):
            ...
    
    Args:
        role: Required role
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_active_user), **kwargs):
            if current_user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient role. Required: {role.value}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
