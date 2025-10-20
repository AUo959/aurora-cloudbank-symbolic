# Aurora CloudBank Security Patterns Guide

This document outlines security patterns and best practices for Aurora CloudBank Symbolic API development.

## Overview

Aurora CloudBank uses a defense-in-depth security approach with multiple layers of protection:

1. **Rate Limiting** - Prevents abuse and DDoS attacks
2. **CSRF Protection** - HTTPBearer token validation
3. **CORS Configuration** - Controlled cross-origin access
4. **Secure Comparison** - Timing-attack resistant string comparison

## Centralized Security Module

All security configurations are centralized in `src/middleware/fastapi_security.py` for consistency and maintainability.

### Importing Security Components

```python
from src.middleware.fastapi_security import (
    security,           # HTTPBearer instance for CSRF protection
    limiter,           # Rate limiter instance
    setup_cors_middleware,  # CORS configuration helper
    verify_csrf_token, # Token validation function
    require_auth,      # Authentication decorator
    secure_compare,    # Timing-safe comparison
)
```

## Usage Patterns

### 1. Rate Limiting

Rate limiting is configured globally using `slowapi` and the client's IP address:

```python
from src.middleware.fastapi_security import limiter

@app.post("/api/endpoint")
@limiter.limit("10/minute")  # Limit to 10 requests per minute
async def my_endpoint():
    ...
```

### 2. CSRF Token Protection

All POST endpoints should validate CSRF tokens using the `security` dependency:

```python
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.middleware.fastapi_security import security

@app.post("/api/endpoint")
async def my_endpoint(token: HTTPAuthorizationCredentials = Depends(security)):
    # CSRF Token validation
    if not token or len(token.credentials) < 10:
        raise HTTPException(status_code=403, detail='Invalid CSRF token')
    
    # Your endpoint logic here
    ...
```

### 3. CORS Configuration

Configure CORS middleware during application setup:

```python
from fastapi import FastAPI
from src.middleware.fastapi_security import setup_cors_middleware

app = FastAPI(title="My API")

# Use default settings (allows all origins)
setup_cors_middleware(app)

# Or customize
setup_cors_middleware(
    app,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)
```

### 4. Secure String Comparison

Use `secure_compare()` for timing-attack resistant comparisons:

```python
from src.middleware.fastapi_security import secure_compare

if secure_compare(provided_token, expected_token):
    # Token is valid
    ...
```

### 5. Authentication Decorator

Use `require_auth()` decorator for endpoints requiring authentication:

```python
from src.middleware.fastapi_security import require_auth

@app.get("/api/protected")
@require_auth(roles=["admin"])
async def protected_endpoint():
    ...
```

## Security Checklist for New Endpoints

When adding new API endpoints, ensure:

- [ ] Rate limiting is applied if endpoint is resource-intensive
- [ ] POST/PUT/DELETE endpoints validate CSRF tokens
- [ ] Sensitive operations use `secure_compare()` for token validation
- [ ] Authentication is enforced where required
- [ ] Error messages don't leak sensitive information
- [ ] Input validation is performed on all user data

## Architecture Pattern

```
┌─────────────────────────────────────────────┐
│         Client Request                       │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      CORS Middleware                         │
│      (Cross-Origin Control)                  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      Rate Limiter                            │
│      (IP-based throttling)                   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      CSRF Token Validation                   │
│      (HTTPBearer security)                   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      Endpoint Logic                          │
│      (Business logic execution)              │
└─────────────────────────────────────────────┘
```

## Integration with Aurora Symbolic Anchors

Security operations should maintain Aurora's symbolic anchoring patterns:

- Include `context_tag` in security logs
- Preserve T1/SRB anchors in DLP exports
- Use `NativeDLPTracker` for security audit trails

Example:

```python
from src.core.native_dlp_export import NativeDLPTracker

tracker = NativeDLPTracker()
tracker.log_security_event({
    "event": "authentication_attempt",
    "context_tag": "auth_validation",
    "result": "success",
    "timestamp": datetime.now().isoformat()
})
```

## Testing Security Features

Test security middleware with existing test patterns:

```python
import pytest
from fastapi.testclient import TestClient

def test_csrf_protection():
    client = TestClient(app)
    # Should fail without token
    response = client.post("/api/endpoint")
    assert response.status_code == 403
    
    # Should succeed with valid token
    response = client.post(
        "/api/endpoint",
        headers={"Authorization": "Bearer valid_token_123456"}
    )
    assert response.status_code == 200
```

## Best Practices

1. **Don't Duplicate Security Code** - Always import from `src.middleware.fastapi_security`
2. **Validate Early** - Check tokens/auth before expensive operations
3. **Fail Securely** - Return generic error messages, log details server-side
4. **Log Security Events** - Track authentication attempts and token validation
5. **Keep Dependencies Updated** - Regularly update security-related packages
6. **Review Regularly** - Periodic security audits of endpoint protection

## References

- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- SlowAPI Rate Limiting: https://slowapi.readthedocs.io/
- OWASP Security Guidelines: https://owasp.org/www-project-top-ten/

---

*Last Updated: 2025-10-20*
*Aurora CloudBank Symbolic - Quantum-Enhanced Governance Stack*
