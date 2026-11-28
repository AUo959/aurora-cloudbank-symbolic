"""Shared deterministic primitives for Phase-1 corpus archaeology."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "0.1.0"


class CorpusArchaeologyError(ValueError):
    """Prepared corpus is invalid or violates a Phase-1 safety boundary."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def make_id(prefix: str, value: Any, length: int = 24) -> str:
    digest = hashlib.sha256(canonical_bytes(value)).hexdigest()
    return f"{prefix}:{digest[:length]}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def semantic_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CorpusArchaeologyError(f"{name} must be a non-empty string")
    return value.strip()


def _parse_timestamp(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise CorpusArchaeologyError(
            "generated_at must be timezone-aware ISO-8601"
        ) from exc


def normalize_timestamp(value: str | None) -> str:
    parsed = datetime.now(timezone.utc) if value is None else _parse_timestamp(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CorpusArchaeologyError("generated_at must include timezone information")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
