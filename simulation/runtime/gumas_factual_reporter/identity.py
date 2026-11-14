"""Canonical encoding, hashing, and source identity for GUMAS Phase 10."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .constants import AUTHORITATIVE_MODULE_NAMES


class Phase10Error(RuntimeError):
    """Raised when factual reporting cannot be proven safe and deterministic."""


def _validate_json_value(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise Phase10Error(f"floating-point value prohibited at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise Phase10Error(f"non-string mapping key prohibited at {path}")
            _validate_json_value(item, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]")
        return
    raise Phase10Error(f"non-JSON value prohibited at {path}: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    _validate_json_value(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_without_field(value: Mapping[str, Any], field: str) -> str:
    return sha256_canonical({key: item for key, item in value.items() if key != field})


def source_identity() -> dict[str, Any]:
    directory = Path(__file__).resolve().parent
    modules: dict[str, str] = {}
    bundle = hashlib.sha256()
    for name in AUTHORITATIVE_MODULE_NAMES:
        data = (directory / name).read_bytes()
        modules[name] = hashlib.sha256(data).hexdigest()
        bundle.update(name.encode("ascii"))
        bundle.update(b"\0")
        bundle.update(data)
        bundle.update(b"\0")
    return {"module_sha256": modules, "bundle_sha256": bundle.hexdigest()}


def require_int(value: Any, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Phase10Error(f"{label} must be an integer")
    result = int(value)
    if minimum is not None and result < minimum:
        raise Phase10Error(f"{label} below minimum {minimum}: {result}")
    return result


def require_sha256(value: Any, label: str) -> str:
    text = str(value or "")
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise Phase10Error(f"{label} must be a lowercase SHA-256")
    return text


def json_pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")
