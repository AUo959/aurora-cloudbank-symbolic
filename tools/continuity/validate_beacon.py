#!/usr/bin/env python3
"""Offline validator for Universal Thread Beacon preservation profiles.

This tool validates schema conformance and deterministic serialization only. It
never performs replay, relay, restore, network access, secret resolution, or
execution of referenced content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

READER_VERSION = "1.0.0"
SUPPORTED_SCHEMA_MAJOR = 1
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "schemas" / "continuity" / "universal_thread_beacon.schema.json"


class BeaconValidationError(ValueError):
    """Raised when a beacon cannot be accepted by the offline reader."""


def _reject_nonfinite(value: str) -> None:
    raise BeaconValidationError(f"Non-finite JSON number is not allowed: {value}")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BeaconValidationError(f"Duplicate JSON object key is not allowed: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    """Load one strict UTF-8 JSON object from disk."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BeaconValidationError(f"Unable to read UTF-8 JSON from {path}: {exc}") from exc

    try:
        payload = json.loads(
            text,
            object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_nonfinite,
        )
    except json.JSONDecodeError as exc:
        raise BeaconValidationError(f"Unable to parse JSON from {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise BeaconValidationError(f"Expected a JSON object in {path}")
    return payload


def semantic_version_tuple(version: str, field_name: str) -> tuple[int, int, int]:
    """Parse the repository's strict three-component semantic-version form."""
    if not isinstance(version, str):
        raise BeaconValidationError(f"Invalid {field_name}: {version!r}")
    parts = version.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise BeaconValidationError(f"Invalid {field_name}: {version!r}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def schema_major(version: str) -> int:
    """Return the semantic-version major component or fail clearly."""
    return semantic_version_tuple(version, "schema version")[0]


def canonical_json(payload: dict[str, Any]) -> str:
    """Serialize deterministically without deleting unknown extension fields."""
    try:
        serialized = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        serialized.encode("utf-8", errors="strict")
        return serialized
    except (TypeError, ValueError, UnicodeError) as exc:
        raise BeaconValidationError(f"Beacon cannot be serialized as strict UTF-8 JSON: {exc}") from exc


def canonical_sha256(payload: dict[str, Any]) -> str:
    """Return the SHA-256 digest of the deterministic JSON representation."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def validate_beacon(payload: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Validate one beacon and return it unchanged.

    Returning the original mapping is intentional: this validator preserves
    unknown fields rather than normalizing them away.
    """
    specification = payload.get("specification")
    if not isinstance(specification, dict):
        raise BeaconValidationError("Missing specification object")

    version = specification.get("schema_version")
    if schema_major(version) != SUPPORTED_SCHEMA_MAJOR:
        raise BeaconValidationError(
            f"Unsupported UTB schema major version {version!r}; supported major is {SUPPORTED_SCHEMA_MAJOR}"
        )

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
        validator.validate(payload)
    except jsonschema.SchemaError as exc:
        location = ".".join(str(part) for part in exc.absolute_schema_path) or "<root>"
        raise BeaconValidationError(f"Invalid reader schema at {location}: {exc.message}") from exc
    except jsonschema.ValidationError as exc:
        location = ".".join(str(part) for part in exc.absolute_path) or "<root>"
        raise BeaconValidationError(f"Schema validation failed at {location}: {exc.message}") from exc

    compatibility = payload["compatibility"]
    minimum_reader_version = compatibility["minimum_reader_version"]
    if semantic_version_tuple(minimum_reader_version, "minimum reader version") > semantic_version_tuple(
        READER_VERSION, "reader version"
    ):
        raise BeaconValidationError(
            f"Beacon requires reader version {minimum_reader_version}; this reader is {READER_VERSION}"
        )

    canonical_json(payload)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a Universal Thread Beacon profile offline")
    parser.add_argument("beacon", type=Path, help="Path to the beacon JSON file")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH, help="Path to the UTB JSON Schema")
    parser.add_argument("--print-canonical", action="store_true", help="Print deterministic canonical JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        schema = load_json(args.schema)
        beacon = load_json(args.beacon)
        validated = validate_beacon(beacon, schema)
        digest = canonical_sha256(validated)
        canonical = canonical_json(validated) if args.print_canonical else None
    except BeaconValidationError as exc:
        print(f"INVALID: {exc}")
        return 1

    print(f"VALID sha256={digest}")
    if canonical is not None:
        print(canonical)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
