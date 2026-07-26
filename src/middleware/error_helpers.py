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
    """Return an HTTPException with a safe detail string and log the real exception.

    For client errors (4xx) the exception is logged at WARNING level without a
    stack trace — these represent expected, routine error conditions (invalid
    input, state conflicts) and emitting a full traceback for every one is
    high-volume noise in production logs that can also leak internal details.

    For server errors (5xx) the full traceback is preserved via
    ``logger.exception()`` because those require investigation.
    """
    if exc is not None:
        if status_code >= 500:
            logger.exception(
                "Internal error (status=%d, detail=%r): %s",
                status_code, safe_detail, exc,
            )
        else:
            logger.warning(
                "Client error (status=%d, detail=%r): %s",
                status_code, safe_detail, exc,
            )
    return HTTPException(status_code=status_code, detail=safe_detail)
