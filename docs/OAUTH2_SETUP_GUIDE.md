# OAuth2 and RBAC Setup Guide

## Overview

Aurora CloudBank Symbolic now includes Role-Based Access Control (RBAC) and OAuth2 authentication with JWT tokens. This guide explains how to configure and use the authentication system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Configuration](#environment-configuration)
3. [User Roles and Permissions](#user-roles-and-permissions)
4. [API Endpoints](#api-endpoints)
5. [Integrating Protected Routes](#integrating-protected-routes)
6. [Security Best Practices](#security-best-practices)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Set Environment Variables

Generate a strong JWT secret key:

```bash
# Generate a secure random key
openssl rand -hex 32

# Set in your environment (Linux/macOS)
export JWT_SECRET_KEY="your-generated-key-here"

# Or set in .env file
echo "JWT_SECRET_KEY=your-generated-key-here" >> .env
```

Required environment variables:

```bash
# Required
JWT_SECRET_KEY=your-generated-key-here

# Optional (with defaults)
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 2. Start the API Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the server
python api/aurora_api.py
```

### 3. Test Authentication

```bash
# Login as a configured admin user
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${AURORA_ADMIN_USERNAME}&password=${AURORA_ADMIN_PASSWORD}"

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Use the access token
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens (REQUIRED) | Generated with `openssl rand -hex 32` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration time in minutes | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration time in days | `7` |

### Configuration File

The system also reads configuration from `config/oauth_config.yaml`. See the file for all available options including:

- JWT settings
- RBAC configuration
- Security settings
- Rate limiting
- Audit logging

## User Roles and Permissions

### Available Roles

Aurora CloudBank defines three roles with hierarchical permissions:

#### 1. Observer (Read-Only)

**Permissions:**
- `READ` - View data
- `MONITOR` - View monitoring and metrics

**Use Case:** Read-only access for monitoring and observing system state

**Example Users:** Auditors, stakeholders, read-only API consumers

#### 2. Relay Operator (Operational)

**Permissions:**
- `READ` - View data
- `WRITE` - Create and update data
- `MONITOR` - View monitoring and metrics
- `EXECUTE` - Execute operations and workflows
- `AUDIT` - Access audit logs

**Use Case:** Operational personnel who can perform actions

**Example Users:** System operators, engineers, automated systems

#### 3. Admin (Full Access)

**Permissions:**
- All permissions from Observer and Relay Operator
- `DELETE` - Remove data
- `ADMIN` - Full system administration
- `CONFIGURE` - Modify system configuration
- `MANAGE_USERS` - User management
- `MANAGE_ROLES` - Role management

**Use Case:** System administrators with full control

**Example Users:** System administrators, DevOps team

### Auth User Store

The mounted auth router does not ship default passwords. Configure users with
`AURORA_AUTH_USERS_JSON` or `AURORA_AUTH_USERS_FILE`; each user must provide a
`password_hash`/`hashed_password` value or a `password_env` reference to a
secret environment variable.

Dev/test fixture users are available only when
`AURORA_ALLOW_DEV_AUTH_FIXTURE=true` and the corresponding
`AURORA_DEV_*_PASSWORD` variables are set.

## API Endpoints

### Authentication Endpoints

All authentication endpoints are under `/api/auth`:

#### POST /api/auth/token

Login and obtain access and refresh tokens.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${AURORA_ADMIN_USERNAME}&password=${AURORA_ADMIN_PASSWORD}"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### POST /api/auth/refresh

Refresh an access token using a refresh token.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/refresh?refresh_token=YOUR_REFRESH_TOKEN"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET /api/auth/me

Get current authenticated user information.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "username": "admin",
  "email": "admin@aurora.local",
  "full_name": "System Administrator",
  "role": "admin",
  "disabled": false
}
```

#### GET /api/auth/me/permissions

Get current user's role and permissions.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/auth/me/permissions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "username": "admin",
  "role": "admin",
  "permissions": [
    "read",
    "write",
    "delete",
    "admin",
    "monitor",
    "execute",
    "configure",
    "audit",
    "manage_users",
    "manage_roles"
  ]
}
```

#### POST /api/auth/logout

Logout (client-side token removal).

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "message": "Successfully logged out",
  "username": "admin"
}
```

## Integrating Protected Routes

### Protecting Routes with Decorators

Use the RBAC decorators to protect your routes:

#### Require Specific Permission

```python
from fastapi import APIRouter, Depends
from src.security.oauth2 import get_current_active_user, require_permission
from src.security.roles import Permission, Role
from src.security.oauth2 import User

router = APIRouter()

@router.get("/admin/users")
async def list_users(current_user: User = Depends(get_current_active_user)):
    """List users - requires MANAGE_USERS permission."""
    if not check_permission(current_user.role, Permission.MANAGE_USERS):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Your logic here
    return {"users": []}
```

#### Require Specific Role

```python
from src.security.oauth2 import require_role

@router.delete("/admin/config")
async def delete_config(current_user: User = Depends(get_current_active_user)):
    """Delete configuration - admin only."""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")
    
    # Your logic here
    return {"status": "deleted"}
```

#### Using FastAPI Dependencies

```python
from fastapi import Depends, HTTPException, status
from src.security.oauth2 import get_current_active_user, User
from src.security.roles import Role, check_permission, Permission

async def require_admin(current_user: User = Depends(get_current_active_user)):
    """Dependency to require admin role."""
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/admin/settings")
async def get_settings(admin: User = Depends(require_admin)):
    """Get admin settings - requires admin role."""
    return {"settings": {...}}
```

### Public Routes

Public routes don't require authentication:

```python
@router.get("/health")
async def health_check():
    """Public health check endpoint."""
    return {"status": "healthy"}
```

## Security Best Practices

### 1. Environment Variables

- ✅ **DO:** Use strong, randomly generated JWT_SECRET_KEY
- ✅ **DO:** Store secrets in environment variables, not in code
- ✅ **DO:** Use different secrets for development and production
- ❌ **DON'T:** Commit secrets to version control
- ❌ **DON'T:** Use default or weak secrets

### 2. Password Management

- ✅ **DO:** Change default demo passwords immediately in production
- ✅ **DO:** Use strong passwords (minimum 12 characters)
- ✅ **DO:** Implement password rotation policies
- ❌ **DON'T:** Store passwords in plain text
- ❌ **DON'T:** Share credentials between users

### 3. Token Management

- ✅ **DO:** Use short expiration times for access tokens (15-30 minutes)
- ✅ **DO:** Store tokens securely on the client side
- ✅ **DO:** Implement token refresh flow
- ✅ **DO:** Clear tokens on logout
- ❌ **DON'T:** Store tokens in localStorage (use httpOnly cookies in production)
- ❌ **DON'T:** Share tokens between users or systems

### 4. HTTPS

- ✅ **DO:** Always use HTTPS in production
- ✅ **DO:** Enforce HTTPS at the infrastructure level
- ✅ **DO:** Use HSTS headers
- ❌ **DON'T:** Send tokens over HTTP in production

### 5. Rate Limiting

- ✅ **DO:** Implement rate limiting on authentication endpoints
- ✅ **DO:** Log failed authentication attempts
- ✅ **DO:** Implement account lockout after multiple failures
- ❌ **DON'T:** Allow unlimited login attempts

### 6. Logging and Monitoring

- ✅ **DO:** Log all authentication events
- ✅ **DO:** Monitor for suspicious activity
- ✅ **DO:** Set up alerts for multiple failed logins
- ❌ **DON'T:** Log passwords or tokens

## Troubleshooting

### Error: "JWT_SECRET_KEY environment variable must be set"

**Problem:** The JWT_SECRET_KEY environment variable is not configured.

**Solution:**
```bash
# Generate a key
openssl rand -hex 32

# Set the environment variable
export JWT_SECRET_KEY="your-generated-key-here"

# Or add to .env file
echo "JWT_SECRET_KEY=your-generated-key-here" >> .env
```

### Error: "Could not validate credentials"

**Problem:** The JWT token is invalid, expired, or malformed.

**Solution:**
1. Check if the token has expired (default 30 minutes)
2. Use the refresh token endpoint to get a new access token
3. Re-authenticate if the refresh token has also expired
4. Verify the token format: `Bearer <token>`

### Error: "Insufficient permissions"

**Problem:** The user's role doesn't have the required permission.

**Solution:**
1. Check the user's role with `GET /api/auth/me/permissions`
2. Verify the endpoint's required permissions
3. Use an account with appropriate permissions
4. Contact an administrator to update your role

### Error: "Incorrect username or password"

**Problem:** Invalid credentials provided.

**Solution:**
1. Verify the username and password are correct
2. Check if the account exists
3. Verify the password hasn't been changed
4. Check if the account is disabled

### Error: "Inactive user"

**Problem:** The user account has been disabled.

**Solution:**
1. Contact an administrator to reactivate the account
2. Verify account status in the user database

## Advanced Configuration

### Custom User Database

Replace the in-memory `USERS_DB` in `src/security/auth_routes.py` with your database:

```python
from your_db import get_user_by_username

async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Fetch user from database
    user = await get_user_by_username(form_data.username)
    
    if not user or not OAuth2Handler.verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Generate tokens...
```

### Token Blacklist (Server-Side Logout)

For true server-side logout, implement a token blacklist with Redis:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def logout(current_user: User = Depends(get_current_active_user)):
    # Add token to blacklist
    redis_client.setex(
        f"blacklist:{token}",
        ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "1"
    )
    return {"message": "Successfully logged out"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Check if token is blacklisted
    if redis_client.exists(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    # Continue with normal validation...
```

### Multi-Factor Authentication (MFA)

For additional security, implement MFA:

```python
import pyotp

async def verify_mfa(username: str, mfa_code: str) -> bool:
    """Verify MFA code."""
    user = await get_user_by_username(username)
    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(mfa_code)

@router.post("/auth/token")
async def login_with_mfa(
    form_data: OAuth2PasswordRequestForm = Depends(),
    mfa_code: str = Form(...)
):
    # Verify password
    user = OAuth2Handler.authenticate_user(...)
    
    # Verify MFA
    if not await verify_mfa(user.username, mfa_code):
        raise HTTPException(
            status_code=401,
            detail="Invalid MFA code"
        )
    
    # Generate tokens...
```

## Support and Documentation

- **Issue Tracker:** [GitHub Issues](https://github.com/AUo959/aurora-cloudbank-symbolic/issues)
- **Security Policy:** See `SECURITY.md`
- **API Reference:** See `v2_API_REFERENCE.md`
- **Configuration:** See `config/oauth_config.yaml`

For security vulnerabilities, please follow the responsible disclosure process outlined in `SECURITY.md`.
