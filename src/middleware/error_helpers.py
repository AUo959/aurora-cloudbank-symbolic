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
    """Return an HTTPException with a safe detail string and log the real exception."""
    if exc is not None:
        logger.exception("Internal error (status=%d, detail=%r): %s", status_code, safe_detail, exc)
    return HTTPException(status_code=status_code, detail=safe_detail)
