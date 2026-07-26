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

    For client errors (4xx) the exception *type* is logged at WARNING level
    without a stack trace or message — emitting the full exception string risks
    leaking internal details or raw user input into operator logs, and a full
    traceback for routine client errors is high-volume noise.

    For server errors (5xx) the traceback is preserved via an explicit
    ``exc_info`` tuple derived from ``exc``.  Unlike ``logger.exception()``,
    which pulls from ``sys.exc_info()`` and emits a useless ``NoneType: None``
    entry when called outside an ``except`` block, ``logger.error(...,
    exc_info=...)`` always uses the exception object we hold.
    """
    if exc is not None:
        if status_code >= 500:
            logger.error(
                "Internal error (status=%d, detail=%r): %s",
                status_code, safe_detail, type(exc).__name__,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
        else:
            logger.warning(
                "Client error (status=%d, detail=%r): %s",
                status_code, safe_detail, type(exc).__name__,
            )
    return HTTPException(status_code=status_code, detail=safe_detail)
