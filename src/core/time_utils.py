"""Timezone-aware time utility helpers.

Provides central functions for UTC timestamps to replace deprecated datetime.utcnow() usage.

Use utc_now() for datetime objects and utc_iso() for ISO-8601 string.
"""
from __future__ import annotations
from datetime import datetime, timezone

__all__ = ["utc_now", "utc_iso", "utc_z"]

def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)

def utc_iso() -> str:
    """Return current UTC time as ISO-8601 string (seconds precision)."""
    return utc_now().isoformat(timespec="seconds")

def utc_z() -> str:
    """Return current UTC time in RFC3339 basic format with 'Z' suffix."""
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")
