"""
Rate Limiting Configuration for Aurora CloudBank API

Implements SlowAPI rate limiting for all computational and state-changing endpoints.
Prevents DoS attacks and resource exhaustion.

Created: 2025-11-11
Part of: Phase 2 HIGH-2 Sprint (Issue #322)
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from typing import Callable

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/day", "50/hour"],
    headers_enabled=True,
)


def rate_limit_error_handler(exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom error handler for rate limit exceeded responses
    
    Returns 429 with Retry-After header
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": "Too many requests. Please try again later.",
            "retry_after": exc.detail
        },
        headers={"Retry-After": str(exc.detail)}
    )


# Rate limit tiers for different endpoint types
class RateLimits:
    """Predefined rate limits for different endpoint categories"""
    
    # Computational operations (expensive CPU/memory)
    COMPUTATIONAL = "60/minute"
    
    # State-changing operations (must be protected)
    STATE_CHANGE = "10/minute"
    
    # Read-only operations (less restrictive)
    READ_ONLY = "200/minute"
    
    # Authentication attempts (prevent brute force)
    AUTH = "5/minute"
    
    # Health checks (allow frequent monitoring)
    HEALTH = "300/minute"
    
    # Agent tool execution (moderate restrictions)
    AGENT_TOOLS = "30/minute"


def computational_limit() -> Callable:
    """Decorator for computational endpoints (60/minute)"""
    return limiter.limit(RateLimits.COMPUTATIONAL)


def state_change_limit() -> Callable:
    """Decorator for state-changing endpoints (10/minute)"""
    return limiter.limit(RateLimits.STATE_CHANGE)


def read_only_limit() -> Callable:
    """Decorator for read-only endpoints (200/minute)"""
    return limiter.limit(RateLimits.READ_ONLY)


def auth_limit() -> Callable:
    """Decorator for authentication endpoints (5/minute)"""
    return limiter.limit(RateLimits.AUTH)


def health_limit() -> Callable:
    """Decorator for health check endpoints (300/minute)"""
    return limiter.limit(RateLimits.HEALTH)


def agent_tools_limit() -> Callable:
    """Decorator for agent tool endpoints (30/minute)"""
    return limiter.limit(RateLimits.AGENT_TOOLS)
