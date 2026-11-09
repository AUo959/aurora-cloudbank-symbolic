"""Canonical Phase-6 receipt normalization for authoritative Phase-7 entry."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from simulation.runtime.gumas_sensing_weapons.kernel import (
    _hash_without_field as _phase6_hash_without_field,
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def normalize_phase6_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the raw Phase-6 receipt, then canonicalize semantically unordered lists."""
    raw = copy.deepcopy(dict(receipt))
    recorded = str(raw.get("phase6_receipt_sha256") or "")
    actual = _phase6_hash_without_field(raw, "phase6_receipt_sha256")
    if not recorded or recorded != actual:
        raise ValueError("Phase-6 raw receipt hash mismatch")

    normalized = copy.deepcopy(raw)
    normalized.pop("phase6_receipt_sha256", None)
    for field in ("contacts", "selections", "weapon_attempts", "effect_descriptors"):
        value = normalized.get(field)
        if isinstance(value, list):
            normalized[field] = sorted(value, key=_canonical_bytes)
    normalized["phase6_receipt_sha256"] = hashlib.sha256(
        _canonical_bytes(normalized)
    ).hexdigest()
    return normalized


def normalizer_source_identity() -> dict[str, Any]:
    directory = Path(__file__).resolve().parent
    modules: dict[str, str] = {}
    bundle = hashlib.sha256()
    for name in ("normalization.py", "__init__.py"):
        data = (directory / name).read_bytes()
        modules[name] = hashlib.sha256(data).hexdigest()
        bundle.update(name.encode("ascii"))
        bundle.update(b"\0")
        bundle.update(data)
        bundle.update(b"\0")
    return {"module_sha256": modules, "bundle_sha256": bundle.hexdigest()}
