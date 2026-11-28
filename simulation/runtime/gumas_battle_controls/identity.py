"""Canonical hashing and source identity for the Phase-11 controls harness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


class Phase11Error(RuntimeError):
    """Raised when a Phase-11 control invariant fails closed."""


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


AUTHORITATIVE_MODULE_NAMES = (
    "__init__.py",
    "constants.py",
    "identity.py",
    "authority.py",
    "inputs.py",
    "runner.py",
    "controls.py",
)


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


def json_diff_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    """Return sorted JSON-pointer-like paths where two JSON values differ."""
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        paths: list[str] = []
        for key in sorted(set(left) | set(right)):
            path = f"{prefix}/{key}"
            if key not in left or key not in right:
                paths.append(path)
            else:
                paths.extend(json_diff_paths(left[key], right[key], path))
        return paths
    if left != right:
        return [prefix or "/"]
    return []
