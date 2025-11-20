# RBAC Integration Examples

This document provides practical examples for integrating Role-Based Access Control (RBAC) and OAuth2 authentication into Aurora CloudBank endpoints.

## Table of Contents

1. [Basic Protected Routes](#basic-protected-routes)
2. [Permission-Based Routes](#permission-based-routes)
3. [Role-Based Routes](#role-based-routes)
4. [Integrating with Existing API](#integrating-with-existing-api)
5. [Custom Authorization Logic](#custom-authorization-logic)

## Basic Protected Routes

### Simple Authentication Check

The most basic form of protection - just verify the user is authenticated:

```python
from fastapi import APIRouter, Depends
from src.security.oauth2 import get_current_active_user, User

router = APIRouter()

@router.get("/protected/data")
async def get_protected_data(current_user: User = Depends(get_current_active_user)):
    """
    This endpoint requires authentication but no specific permission.
    Any authenticated user can access it.
    """
    return {
        "message": f"Hello {current_user.username}",
        "role": current_user.role.value,
        "data": "sensitive information"
    }
```

## Permission-Based Routes

### Check Specific Permissions

Protect routes based on specific permissions:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from src.security.oauth2 import get_current_active_user, User
from src.security.roles import Permission, check_permission

router = APIRouter()

@router.post("/data/create")
async def create_data(
    data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create data - requires WRITE permission.
    Available to: relay_operator, admin
    """
    if not check_permission(current_user.role, Permission.WRITE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: write"
        )
    
    # Your data creation logic here
    return {"status": "created", "created_by": current_user.username}


@router.delete("/data/{data_id}")
async def delete_data(
    data_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete data - requires DELETE permission.
    Available to: admin only
    """
    if not check_permission(current_user.role, Permission.DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: delete"
        )
    
    # Your data deletion logic here
    return {"status": "deleted", "id": data_id}


@router.post("/workflow/execute")
async def execute_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute workflow - requires EXECUTE permission.
    Available to: relay_operator, admin
    """
    if not check_permission(current_user.role, Permission.EXECUTE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required: execute"
        )
    
    # Your workflow execution logic here
    return {"status": "executing", "workflow_id": workflow_id}
```

### Multiple Permission Checks

Check for multiple permissions:

```python
from src.security.roles import Permission, check_permission

@router.post("/advanced/operation")
async def advanced_operation(
    current_user: User = Depends(get_current_active_user)
):
    """
    Advanced operation requiring multiple permissions.
    """
    required_permissions = [Permission.WRITE, Permission.EXECUTE, Permission.AUDIT]
    
    for perm in required_permissions:
        if not check_permission(current_user.role, perm):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {perm.value}"
            )
    
    # Your operation logic here
    return {"status": "success"}
```

## Role-Based Routes

### Admin-Only Routes

Restrict routes to admin role:

```python
from src.security.roles import Role

@router.post("/admin/users")
async def create_user(
    username: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create user - admin only.
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Your user creation logic here
    return {"status": "user created", "username": username}


@router.get("/admin/config")
async def get_admin_config(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get admin configuration - admin only.
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return {"config": {"setting1": "value1", "setting2": "value2"}}
```

### Operator Routes

Routes for relay operators:

```python
@router.post("/relay/configure")
async def configure_relay(
    config: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Configure relay - relay_operator or admin.
    """
    if current_user.role not in [Role.RELAY_OPERATOR, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator or admin access required"
        )
    
    # Your relay configuration logic here
    return {"status": "configured"}
```

## Integrating with Existing API

### Example: Protecting Quantum Simulator Routes

```python
# In modules/quantum_simulator/api.py or similar

from fastapi import APIRouter, Depends, HTTPException, status
from src.security.oauth2 import get_current_active_user, User
from src.security.roles import Permission, check_permission

router = APIRouter(prefix="/quantum", tags=["quantum"])

@router.post("/simulate")
async def run_simulation(
    scenario: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Run quantum simulation - requires EXECUTE permission.
    """
    if not check_permission(current_user.role, Permission.EXECUTE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to run simulations"
        )
    
    # Original simulation logic here
    return {"status": "simulation started"}


@router.get("/results/{sim_id}")
async def get_results(
    sim_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get simulation results - requires READ permission (all authenticated users).
    """
    if not check_permission(current_user.role, Permission.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view results"
        )
    
    # Original results retrieval logic here
    return {"results": "simulation data"}
```

### Example: Protecting Memory Manager Routes

```python
# In modules/aumemmanager/api_integration.py or similar

@router.post("/memory/create")
async def create_memory(
    memory_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create memory - requires WRITE permission.
    """
    if not check_permission(current_user.role, Permission.WRITE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create memories"
        )
    
    # Add user context to memory
    memory_data["created_by"] = current_user.username
    memory_data["creator_role"] = current_user.role.value
    
    # Original memory creation logic here
    return {"status": "memory created"}


@router.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete memory - requires DELETE permission (admin only).
    """
    if not check_permission(current_user.role, Permission.DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete memories"
        )
    
    # Original memory deletion logic here
    return {"status": "memory deleted", "id": memory_id}
```

## Custom Authorization Logic

### Dependency Functions

Create reusable dependency functions for common authorization patterns:

```python
from fastapi import Depends, HTTPException, status
from src.security.oauth2 import get_current_active_user, User
from src.security.roles import Role, Permission, check_permission

async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to require admin role."""
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_write_permission(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to require WRITE permission."""
    if not check_permission(current_user.role, Permission.WRITE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write permission required"
        )
    return current_user


async def require_execute_permission(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to require EXECUTE permission."""
    if not check_permission(current_user.role, Permission.EXECUTE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Execute permission required"
        )
    return current_user


# Usage in routes:

@router.post("/admin/settings")
async def update_settings(settings: dict, admin: User = Depends(require_admin)):
    """Update settings - admin only."""
    return {"status": "updated"}


@router.post("/data/write")
async def write_data(data: dict, user: User = Depends(require_write_permission)):
    """Write data - requires write permission."""
    return {"status": "written"}


@router.post("/workflow/run")
async def run_workflow(workflow: dict, user: User = Depends(require_execute_permission)):
    """Run workflow - requires execute permission."""
    return {"status": "running"}
```

### Resource-Based Authorization

Check ownership or specific resource permissions:

```python
@router.put("/data/{data_id}")
async def update_data(
    data_id: str,
    updates: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update data - requires WRITE permission.
    Users can only update their own data unless they're admin.
    """
    if not check_permission(current_user.role, Permission.WRITE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write permission required"
        )
    
    # Fetch data from database (pseudo-code)
    data = get_data_by_id(data_id)
    
    # Check ownership or admin
    if data.owner != current_user.username and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own data"
        )
    
    # Update the data
    updated_data = update_data_in_db(data_id, updates)
    return {"status": "updated", "data": updated_data}
```

### Conditional Permissions

Different permissions for different operations:

```python
@router.get("/data/{data_id}")
async def get_data(
    data_id: str,
    include_sensitive: bool = False,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get data - requires READ permission.
    Sensitive data requires AUDIT permission.
    """
    if not check_permission(current_user.role, Permission.READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Read permission required"
        )
    
    data = get_data_by_id(data_id)
    
    if include_sensitive:
        if not check_permission(current_user.role, Permission.AUDIT):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Audit permission required for sensitive data"
            )
        return {"data": data, "sensitive_info": data.sensitive}
    
    return {"data": data}
```

## Main API Integration

### Updating aurora_api.py

To integrate the authentication routes into the main API:

```python
# In api/aurora_api.py

from src.security.auth_routes import router as auth_router

# Add after other router includes
app.include_router(auth_router, tags=["authentication"])
```

### Full Example with Multiple Routers

```python
from fastapi import FastAPI
from src.security.auth_routes import router as auth_router
from src.middleware.fastapi_security import setup_cors_middleware

app = FastAPI(title="Aurora CloudBank Symbolic")

# Setup CORS
setup_cors_middleware(app)

# Include authentication router
app.include_router(auth_router, tags=["authentication"])

# Include other routers with protection
# Example: Quantum simulator with RBAC
try:
    from modules.quantum_simulator.api import router as quantum_router
    app.include_router(quantum_router, prefix="/quantum", tags=["quantum"])
except ImportError:
    pass

# Example: Memory manager with RBAC
try:
    from modules.aumemmanager.api_integration import router as memory_router
    app.include_router(memory_router, prefix="/memory", tags=["memory"])
except ImportError:
    pass
```

## Testing Protected Routes

### Example Test Case

```python
import pytest
from fastapi.testclient import TestClient

def test_protected_route_with_auth(client: TestClient):
    """Test accessing protected route with authentication."""
    # Login first
    response = client.post(
        "/api/auth/token",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    
    # Access protected route
    response = client.get(
        "/protected/data",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "data" in response.json()


def test_protected_route_without_auth(client: TestClient):
    """Test accessing protected route without authentication."""
    response = client.get("/protected/data")
    
    assert response.status_code == 401


def test_admin_route_with_observer(client: TestClient):
    """Test accessing admin route with observer role."""
    # Login as observer
    response = client.post(
        "/api/auth/token",
        data={"username": "observer", "password": "observer123"}
    )
    token = response.json()["access_token"]
    
    # Try to access admin route
    response = client.get(
        "/admin/config",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]
```

## Best Practices

### 1. Consistent Error Messages

Use consistent error messages for authorization failures:

```python
# Good: Consistent error response
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail=f"Insufficient permissions. Required: {permission.value}"
)

# Bad: Inconsistent error messages
raise HTTPException(status_code=403, detail="No access")
```

### 2. Document Permission Requirements

Always document required permissions in docstrings:

```python
@router.post("/data/create")
async def create_data(current_user: User = Depends(get_current_active_user)):
    """
    Create new data entry.
    
    Required Permission: WRITE
    Available to: relay_operator, admin
    """
    pass
```

### 3. Use Dependency Injection

Leverage FastAPI's dependency injection for cleaner code:

```python
# Good: Reusable dependency
async def require_write(user: User = Depends(get_current_active_user)):
    if not check_permission(user.role, Permission.WRITE):
        raise HTTPException(status_code=403, detail="Write permission required")
    return user

@router.post("/data1")
async def create_data1(user: User = Depends(require_write)):
    pass

@router.post("/data2")
async def create_data2(user: User = Depends(require_write)):
    pass
```

### 4. Audit Trail

Log authorization decisions for security auditing:

```python
import logging

logger = logging.getLogger(__name__)

@router.post("/sensitive/operation")
async def sensitive_operation(current_user: User = Depends(get_current_active_user)):
    if not check_permission(current_user.role, Permission.ADMIN):
        logger.warning(
            f"Unauthorized access attempt to sensitive operation by {current_user.username} "
            f"with role {current_user.role.value}"
        )
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logger.info(f"Sensitive operation authorized for {current_user.username}")
    # Operation logic here
```

### 5. Rate Limiting on Sensitive Routes

Combine RBAC with rate limiting for sensitive operations:

```python
from src.middleware.fastapi_security import limiter

@router.post("/admin/reset")
@limiter.limit("5/hour")
async def reset_system(
    request: Request,
    admin: User = Depends(require_admin)
):
    """Admin operation with rate limiting."""
    # Reset logic here
    pass
```

## Summary

Key points for RBAC integration:

1. **Always authenticate** - Use `get_current_active_user` dependency
2. **Check permissions** - Use `check_permission()` for specific permissions
3. **Check roles** - Compare `current_user.role` for role-specific access
4. **Use dependencies** - Create reusable dependency functions
5. **Document requirements** - Clearly state required permissions/roles
6. **Log access attempts** - Maintain audit trail for security
7. **Test thoroughly** - Write tests for all authorization paths
8. **Consistent errors** - Use standard HTTP status codes and messages

For more information, see:
- [OAuth2 Setup Guide](OAUTH2_SETUP_GUIDE.md)
- [API Reference](../v2_API_REFERENCE.md)
- [Security Policy](../SECURITY.md)
