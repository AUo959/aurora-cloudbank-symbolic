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

## Migration Guide for Existing Code

If you have existing FastAPI endpoints that need to be migrated to use the centralized security module:

### Step 1: Update Imports

**Before:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware

limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()
```

**After:**
```python
from src.middleware.fastapi_security import security, limiter, setup_cors_middleware
from fastapi.security import HTTPAuthorizationCredentials
```

### Step 2: Update CORS Middleware Setup

**Before:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**After:**
```python
setup_cors_middleware(app)  # Uses sensible defaults
```

### Step 3: No Changes Needed for Endpoints

Endpoint definitions remain the same:
```python
@app.post("/api/endpoint")
async def my_endpoint(token: HTTPAuthorizationCredentials = Depends(security)):
    # CSRF Token validation
    if not token or len(token.credentials) < 10:
        raise HTTPException(status_code=403, detail='Invalid CSRF token')
    # ... rest of endpoint logic
```

### Step 4: Remove Duplicate Definitions

Remove any duplicate:
- `@app.post()` decorators
- `async def` function definitions
- Import statements

---

*Migration completed as of commit e075190*
*All API files now use centralized security module*

---

## Session and Cookie Posture (#788)

**Aurora's FastAPI app does not set authentication or session cookies.**

- Authentication is HTTP `Authorization: Bearer <jwt>` only (`src/security/oauth2.py`).
- CSRF tokens are header-based (`X-CSRF-Token` / `Depends(verify_csrf_token)`),
  not cookie-stored.
- `Set-Cookie` is not emitted by any production endpoint — verified by
  `grep -rn "set_cookie\|Set-Cookie\|response\.cookies" --include="*.py" api/ modules/ src/`
  returning zero hits in production code.
- The lone reference to cookie attributes in `src/agents/crew/markov.py:148-152`
  is **declarative metadata returned by an agent task description**, not a
  live `Set-Cookie` code path.

**Therefore no global `SessionMiddleware` or cookie-flag middleware is
required at this time.**

### If cookies are added in the future

If a future endpoint introduces cookies (e.g. for a browser-targeted
session UX), it MUST set the following attributes:

| Attribute | Value | Rationale |
|---|---|---|
| `Secure` | `True` (when TLS is terminated upstream) | Prevents transmission over plaintext |
| `HttpOnly` | `True` | Blocks JavaScript access; mitigates XSS token theft |
| `SameSite` | `"Strict"` (or `"Lax"` with explicit justification) | Mitigates CSRF in browser contexts |
| `Domain` | The exact host serving the cookie | Avoids subdomain leakage |
| `Path` | The narrowest path that needs the cookie | Limits scope |

At that point, add a `SessionMiddleware` or a small response-side middleware
in `src/middleware/` that enforces these defaults on every `Set-Cookie`
header, and add an integration test that asserts the flags. Update this
section and #788 / its successor accordingly.
