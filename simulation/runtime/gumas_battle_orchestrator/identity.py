"""Canonical hashing and source identity for GUMAS Phase 9."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from simulation.runtime.gumas_movement_geometry.geometry import (
    round_half_even_fraction,
)


class Phase9Error(RuntimeError):
    """Raised when a Phase-9 transition cannot be proven valid."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def hash_without_field(value: Mapping[str, Any], field: str) -> str:
    return sha256_canonical({key: item for key, item in value.items() if key != field})


def source_identity() -> dict[str, Any]:
    directory = Path(__file__).resolve().parent
    names = (
        "__init__.py",
        "constants.py",
        "identity.py",
        "live_observation.py",
        "orchestrator.py",
    )
    modules: dict[str, str] = {}
    bundle = hashlib.sha256()
    for name in names:
        data = (directory / name).read_bytes()
        modules[name] = hashlib.sha256(data).hexdigest()
        bundle.update(name.encode("ascii"))
        bundle.update(b"\0")
        bundle.update(data)
        bundle.update(b"\0")
    return {"module_sha256": modules, "bundle_sha256": bundle.hexdigest()}


def require_int(value: Any, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Phase9Error(f"{label} must be an integer")
    result = int(value)
    if minimum is not None and result < minimum:
        raise Phase9Error(f"{label} below minimum {minimum}: {result}")
    return result


def require_q1000(value: Any, label: str) -> int:
    result = require_int(value, label)
    if not 0 <= result <= 1000:
        raise Phase9Error(f"{label} outside q1000 bounds: {result}")
    return result


def clamp_q1000(value: int) -> int:
    return max(0, min(1000, int(value)))


def mean_round(values: Sequence[int]) -> int:
    return round_half_even_fraction(sum(int(value) for value in values), len(values)) if values else 0


def fraction_q1000(current: int, maximum: int, label: str) -> int:
    if maximum <= 0 or current < 0 or current > maximum:
        raise Phase9Error(f"invalid fraction for {label}: {current}/{maximum}")
    return clamp_q1000(round_half_even_fraction(current * 1000, maximum))
