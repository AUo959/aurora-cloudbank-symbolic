# Rate Limiting Guide

This guide documents Aurora's production-grade rate limiting, configuration patterns, deployment guidance, and troubleshooting. It is suitable for the GitHub Wiki and can be synced as-is.

## Overview

Aurora uses SlowAPI for request throttling with:
- Global middleware + per-endpoint decorators (auth routes are guarded by default).
- Standards-compliant 429 responses including `Retry-After` and `X-RateLimit-Limit` headers.
- Configurable keying strategies:
  - `ip`: client IP only (default)
  - `ip_user`: composite key of client IP + JWT `sub` when available
- Optional Redis-backed storage for distributed environments.
- System-wide enable/disable toggle for testing or controlled load windows.

## Configuration

Set environment variables (copy from `.env.example`):

- `RATE_LIMIT_ENABLED` (default `true`): master toggle
- `RATE_LIMIT_KEY_STRATEGY` (`ip` | `ip_user`): key derivation strategy
- `REDIS_URL` (optional): `redis://host:port` for distributed limits
- `RATE_LIMIT_AUTH_TOKEN_PER_MIN`: cap for `/api/auth/token`
- `RATE_LIMIT_AUTH_REFRESH_PER_MIN`: cap for `/api/auth/refresh`

### Local (In-Memory)
```bash
export RATE_LIMIT_ENABLED=true
export RATE_LIMIT_KEY_STRATEGY=ip
unset REDIS_URL
export RATE_LIMIT_AUTH_TOKEN_PER_MIN=10
export RATE_LIMIT_AUTH_REFRESH_PER_MIN=30
```

### Production (Redis + Composite Key)
```bash
export RATE_LIMIT_ENABLED=true
export RATE_LIMIT_KEY_STRATEGY=ip_user
export REDIS_URL=redis://aurora-redis:6379
export RATE_LIMIT_AUTH_TOKEN_PER_MIN=5
export RATE_LIMIT_AUTH_REFRESH_PER_MIN=20
```

## Behavior & Headers

On limit breach, Aurora returns HTTP 429 with headers:
- `Retry-After`: seconds until the next available request in the window
- `X-RateLimit-Limit`: the configured limit for the endpoint/window

These are set via the global rate limit exception handler, with a middleware fallback to ensure consistent headers for any bypass path.

## Key Strategy Details

- `ip`: best-effort protection at the edge (works pre-auth, during login)
- `ip_user`: combines client IP and JWT subject (user) when token is present
  - Note: login requests do not include `Authorization` so they fall back to IP-only
  - After authentication, per-user differentiation activates automatically

## Distributed Deployment

- Use `REDIS_URL` to enable Redis-backed storage for synchronized limits across replicas.
- Ensure your ingress/proxy preserves the client IP (e.g., `X-Forwarded-For`).
- Configure your ASGI server/proxy to trust proxy headers so the limiter sees the real client IP.

## Testing Tips

- For deterministic tests, isolate a fresh FastAPI app per test class/module that exercises rate limits.
- Avoid cross-test interference by:
  - Using higher threshold env vars, or
  - Setting `RATE_LIMIT_ENABLED=false` in non-rate-limit tests.
- When validating composite keys, remember login flows won’t carry `Authorization`; adapt expectations accordingly.

## Troubleshooting

- Seeing unexpected 429s during local development:
  - Temporarily raise `RATE_LIMIT_AUTH_*` values or disable with `RATE_LIMIT_ENABLED=false`.
- Using a load balancer and all requests appear from the same IP:
  - Ensure proxy headers are forwarded and trusted by your ASGI server.
- No headers on 429 responses:
  - Ensure the global rate limit exception handler is active; a fallback middleware adds headers defensively.

## Security Guidance

- Keep authentication endpoints conservative to prevent abuse.
- Use `ip_user` in production to fairly partition limits post-auth while retaining pre-auth protection.
- Prefer Redis-backed storage when running multiple API instances.

## Related Files

- `api/aurora_api.py` – global middleware and 429 handler
- `src/middleware/fastapi_security.py` – limiter configuration, storage, and key strategy
- `src/security/auth_routes.py` – per-endpoint rate limits for auth
- `.env.example` – complete environment configuration reference
