"""Helpers for producing operator-safe HTTPException responses."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def http_error(
    status_code: int,
    safe_detail: str,
    exc: Optional[BaseException] = None,
) -> HTTPException:
    """Return an HTTPException while keeping response and logs bounded.

    Expected client errors log only the status, approved detail, and exception
    type. Raw exception messages commonly contain user input or internal state
    and are intentionally excluded.

    Server errors retain an explicit traceback tuple derived from ``exc`` so
    diagnostics work both inside and outside an active ``except`` block.
    """
    if exc is not None:
        if status_code >= 500:
            logger.error(
                "Internal error (status=%d, detail=%r, exception_type=%s)",
                status_code,
                safe_detail,
                type(exc).__name__,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
        else:
            logger.warning(
                "Client error (status=%d, detail=%r, exception_type=%s)",
                status_code,
                safe_detail,
                type(exc).__name__,
            )
    return HTTPException(status_code=status_code, detail=safe_detail)
