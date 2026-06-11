"""
Token Usage API

Exposes per-user and global token consumption metrics gathered by TokenBudget.

Routes:
    GET /api/usage/me     — per-user rolling-window totals (authenticated)
    GET /api/usage/global — global rolling-window totals + configured limits (admin)

Security note:
    Both endpoints currently accept a ``user_id`` query parameter as a placeholder.
    Before exposing these endpoints in production, replace the ``user_id`` parameter
    with a proper ``Depends()`` authentication dependency that extracts the user
    identity from a verified JWT bearer token, and restrict the ``/global`` endpoint
    to admin roles via role-based access control.

Anchor: T1-AIB-001
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from modules.ai_core.token_budget import token_budget

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/usage", tags=["Token Usage"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class UserUsageResponse(BaseModel):
    """Per-user rolling-window token consumption."""

    user_id: str = Field(..., description="User identifier")
    hour_tokens: int = Field(..., ge=0, description="Tokens used in the last hour")
    day_tokens: int = Field(..., ge=0, description="Tokens used in the last 24 hours")
    limits: Dict[str, Optional[int]] = Field(
        ..., description="Configured caps applicable to this user"
    )


class GlobalUsageResponse(BaseModel):
    """Global rolling-window token consumption (admin view)."""

    hour_tokens: int = Field(..., ge=0, description="Tokens used globally in the last hour")
    limits: Dict[str, Any] = Field(..., description="All configured token caps")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/me",
    response_model=UserUsageResponse,
    summary="Get token usage for the current user",
    description=(
        "Returns rolling hourly and daily token totals for a user. "
        "**Production hardening required**: replace the ``user_id`` query parameter "
        "with a JWT-extraction dependency (e.g. ``Depends(get_current_user)``) so "
        "callers can only query their own usage."
    ),
)
async def get_user_usage(
    user_id: str = Query(default="anonymous", min_length=1, max_length=256),
) -> UserUsageResponse:
    """Return per-user token consumption for the rolling windows."""
    try:
        usage = token_budget.get_user_usage(user_id)
        return UserUsageResponse(
            user_id=user_id,
            hour_tokens=usage["hour_tokens"],
            day_tokens=usage["day_tokens"],
            limits={
                "max_per_request": token_budget.max_per_request,
                "max_per_user_hour": token_budget.max_per_user_hour,
                "max_per_user_day": token_budget.max_per_user_day,
            },
        )
    except Exception as exc:
        logger.error("Failed to retrieve user usage: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve usage data.",
        ) from exc


@router.get(
    "/global",
    response_model=GlobalUsageResponse,
    summary="Get global token usage (admin)",
    description=(
        "Returns the global rolling hourly token total and all configured caps. "
        "**Production hardening required**: restrict to admin roles via role-based "
        "access control before exposing in a multi-tenant environment."
    ),
)
async def get_global_usage() -> GlobalUsageResponse:
    """Return global token consumption across all users."""
    try:
        usage = token_budget.get_global_usage()
        return GlobalUsageResponse(
            hour_tokens=usage["hour_tokens"],
            limits=usage["limits"],
        )
    except Exception as exc:
        logger.error("Failed to retrieve global usage: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve global usage data.",
        ) from exc
