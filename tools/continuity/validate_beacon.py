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
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema

SPECIFICATION_NAME = "UTB-PS-001"
SUPPORTED_SCHEMA_VERSION = "0.1.0"
EXPECTED_SCHEMA_ID = (
    "https://raw.githubusercontent.com/AUo959/aurora-cloudbank-symbolic/"
    "main/schemas/continuity/universal_thread_beacon.schema.json"
)
READER_VERSION = "1.0.0"
CANONICALIZATION = "utb-json-subset-v1"
MAX_SAFE_INTEGER = 9_007_199_254_740_991
SEMVER_COMPONENT_MAX_DIGITS = 9
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "schemas" / "continuity" / "universal_thread_beacon.schema.json"

# A minimum-profile beacon is a small descriptive record. The cap exists so an
# oversized input is refused before it is read, rather than after the reader has
# materialised it and walked it several times.
MAX_BEACON_BYTES = 1 << 20  # 1 MiB

# Several identity fields are compared before schema validation can bound their
# length, so error messages must not echo them whole.
ERROR_ECHO_MAX_CHARS = 96

# Instance locations the schema constrains with `pattern` or `format`, re-checked
# here because jsonschema alone does not enforce either one strictly enough:
#
#   pattern - jsonschema compiles patterns with Python's `re`, where `$` also
#     matches immediately before a final newline. "a"*64 + "\n" therefore
#     satisfies "^[a-fA-F0-9]{64}$". Two of these fields feed the canonical
#     digest, so the same logical value would have two distinct encodings.
#     Fixed with re.fullmatch, which has no such leniency. The schema keeps `$`
#     because that is correct under ECMA-262, which is what JSON Schema
#     specifies and what non-Python readers implement.
#
#   format - format assertions are annotations by default, and `date-time` is
#     only checked when rfc3339-validator is installed. It is not a declared
#     dependency, so these were silently unenforced and a beacon could validate
#     for one reader and not another depending on what happened to be on the
#     path. Checked here instead of adding the dependency, matching how this
#     module already hand-validates semantic versions and integer bounds.
#
# test_reader_covers_every_schema_pattern_and_format re-derives this table from
# the schema and fails if a constraint is added without being covered.
PATTERNED_FIELDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("manifest_version",), r"[0-9]+\.[0-9]+\.[0-9]+"),
    (("integrity", "digest"), r"[a-fA-F0-9]{64}"),
    (("compatibility", "minimum_reader_version"), r"[0-9]+\.[0-9]+\.[0-9]+"),
)
FORMATTED_FIELDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("lifecycle", "created_at"), "date-time"),
    (("lifecycle", "updated_at"), "date-time"),
)

# RFC 3339 date-time. Deliberately stricter than datetime.fromisoformat, which
# accepts spellings RFC 3339 does not (a space separator, an omitted offset).
_RFC3339_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}"
    r"[Tt]"
    r"\d{2}:\d{2}:\d{2}(?:\.\d+)?"
    r"(?:[Zz]|[+-]\d{2}:\d{2})"
)


class BeaconValidationError(ValueError):
    """Raised when a beacon cannot be accepted by the offline reader."""


def _echo(value: Any) -> str:
    """Return a length-bounded repr safe to put in an error message.

    specification.name, specification.schema_version and
    compatibility.canonicalization are all compared before schema validation
    runs, so no maxLength bounds them at that point. Interpolating them raw let
    a 5 MB field produce a 5 MB message, printed verbatim to stdout by main().
    """
    text = repr(value)
    if len(text) <= ERROR_ECHO_MAX_CHARS:
        return text
    return f"{text[:ERROR_ECHO_MAX_CHARS]}... ({len(text)} chars total)"


def _resolve(payload: Any, path: tuple[str, ...]) -> Any:
    """Return the value at a dotted instance path, or None if absent."""
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _validate_strict_formats(payload: dict[str, Any]) -> None:
    """Re-check pattern and format constraints that jsonschema under-enforces.

    See PATTERNED_FIELDS / FORMATTED_FIELDS for why each is needed.
    """
    for path, pattern in PATTERNED_FIELDS:
        value = _resolve(payload, path)
        if value is None or not isinstance(value, str):
            continue
        if re.fullmatch(pattern, value) is None:
            raise BeaconValidationError(
                f"Invalid {'.'.join(path)}: {_echo(value)} does not match {pattern!r} "
                f"under strict full-string matching"
            )

    for path, fmt in FORMATTED_FIELDS:
        value = _resolve(payload, path)
        if value is None or not isinstance(value, str):
            continue
        if fmt != "date-time":
            raise BeaconValidationError(f"Reader cannot enforce format {fmt!r} at {'.'.join(path)}")
        if _RFC3339_RE.fullmatch(value) is None:
            raise BeaconValidationError(
                f"Invalid {'.'.join(path)}: {_echo(value)} is not an RFC 3339 date-time"
            )
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00").replace("z", "+00:00"))
        except ValueError as exc:
            raise BeaconValidationError(
                f"Invalid {'.'.join(path)}: {_echo(value)} is not a real date-time ({exc})"
            ) from exc


def _reject_nonfinite(value: str) -> None:
    raise BeaconValidationError(f"Non-finite JSON number is not allowed: {value}")


def _reject_float(value: str) -> None:
    raise BeaconValidationError(
        f"Floating-point JSON numbers are not allowed by {CANONICALIZATION}: {value}"
    )


def _parse_bounded_int(value: str) -> int:
    digits = value[1:] if value.startswith("-") else value
    if len(digits) > 16:
        raise BeaconValidationError(f"JSON integer exceeds the safe canonical range: {value[:32]!r}")
    try:
        parsed = int(value)
    except ValueError as exc:
        raise BeaconValidationError(f"Invalid JSON integer: {value!r}") from exc
    if abs(parsed) > MAX_SAFE_INTEGER:
        raise BeaconValidationError(f"JSON integer exceeds the safe canonical range: {value!r}")
    return parsed


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
        size = path.stat().st_size
    except OSError as exc:
        raise BeaconValidationError(f"Unable to stat {path}: {exc}") from exc
    if size > MAX_BEACON_BYTES:
        raise BeaconValidationError(
            f"Refusing to read {path}: {size} bytes exceeds the {MAX_BEACON_BYTES}-byte "
            f"limit for a minimum-profile beacon"
        )

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BeaconValidationError(f"Unable to read UTF-8 JSON from {path}: {exc}") from exc

    try:
        payload = json.loads(
            text,
            object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_nonfinite,
            parse_float=_reject_float,
            parse_int=_parse_bounded_int,
        )
    except BeaconValidationError:
        raise
    except RecursionError as exc:
        # RecursionError is not a ValueError, so deeply nested input would
        # otherwise escape this handler and reach the caller as a raw traceback
        # instead of a controlled INVALID result.
        raise BeaconValidationError(f"Unable to parse JSON from {path}: input nested too deeply") from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise BeaconValidationError(f"Unable to parse JSON from {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise BeaconValidationError(f"Expected a JSON object in {path}")
    return payload


def semantic_version_tuple(version: str, field_name: str) -> tuple[int, int, int]:
    """Parse a bounded three-component semantic-version form."""
    if not isinstance(version, str):
        raise BeaconValidationError(f"Invalid {field_name}: {_echo(version)}")
    parts = version.split(".")
    # str.isdigit() is true for non-ASCII decimal digits that int() also
    # accepts, so "١.٠.٠" would otherwise parse as (1, 0, 0). This runs on
    # specification.schema_version before any schema validation, so the ASCII
    # restriction has to be explicit here.
    if (
        len(parts) != 3
        or any(not (part.isascii() and part.isdigit()) for part in parts)
        or any(len(part) > SEMVER_COMPONENT_MAX_DIGITS for part in parts)
    ):
        raise BeaconValidationError(f"Invalid {field_name}: {_echo(version)}")
    try:
        parsed = tuple(int(part) for part in parts)
    except ValueError as exc:
        raise BeaconValidationError(f"Invalid {field_name}: {_echo(version)}") from exc
    return parsed  # type: ignore[return-value]


def _validate_schema_contents(schema: dict[str, Any], payload_version: str) -> None:
    """Bind validation to the committed bundled schema, not self-asserted markers."""
    bundled_schema = load_json(DEFAULT_SCHEMA_PATH)
    if schema != bundled_schema:
        raise BeaconValidationError(
            "Schema content does not match the committed bundled UTB schema"
        )

    expected = {
        "$id": EXPECTED_SCHEMA_ID,
        "x-utb-specification": SPECIFICATION_NAME,
        "x-utb-schema-version": SUPPORTED_SCHEMA_VERSION,
    }
    mismatches = [key for key, value in expected.items() if schema.get(key) != value]
    if mismatches:
        raise BeaconValidationError(
            "Bundled schema has invalid UTB identity fields: " + ", ".join(sorted(mismatches))
        )
    if payload_version != schema["x-utb-schema-version"]:
        raise BeaconValidationError(
            f"Beacon schema version {payload_version!r} does not match reader schema "
            f"{schema['x-utb-schema-version']!r}"
        )


def _validate_canonical_subset(value: Any, path: str = "$") -> None:
    """Enforce the value domain used by the UTB canonical byte encoding."""
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise BeaconValidationError(f"Integer outside canonical range at {path}: {value}")
        return
    if isinstance(value, float):
        raise BeaconValidationError(f"Floating-point value is not allowed at {path}")
    if isinstance(value, str):
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise BeaconValidationError(f"Invalid Unicode scalar value at {path}: {exc}") from exc
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_canonical_subset(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise BeaconValidationError(f"Non-string object key at {path}: {key!r}")
            if not key.isascii() or any(ord(character) < 0x20 or ord(character) > 0x7E for character in key):
                raise BeaconValidationError(f"Object key is outside printable ASCII at {path}: {key!r}")
            _validate_canonical_subset(item, f"{path}.{key}")
        return
    raise BeaconValidationError(f"Unsupported JSON value at {path}: {type(value).__name__}")


_SHORT_ESCAPES = {
    '"': '\\"',
    "\\": "\\\\",
    "\b": "\\b",
    "\t": "\\t",
    "\n": "\\n",
    "\f": "\\f",
    "\r": "\\r",
}


def _canonical_string(value: str) -> str:
    """Encode one JSON string with the exact UTB v1 escaping rules."""
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise BeaconValidationError(f"Invalid Unicode scalar value: {exc}") from exc

    encoded: list[str] = ['"']
    for character in value:
        escaped = _SHORT_ESCAPES.get(character)
        if escaped is not None:
            encoded.append(escaped)
        elif ord(character) < 0x20:
            encoded.append(f"\\u{ord(character):04x}")
        else:
            encoded.append(character)
    encoded.append('"')
    return "".join(encoded)


def _canonical_serialize(value: Any, path: str = "$") -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > MAX_SAFE_INTEGER:
            raise BeaconValidationError(f"Integer outside canonical range at {path}: {value}")
        return str(value)
    if isinstance(value, float):
        raise BeaconValidationError(f"Floating-point value is not allowed at {path}")
    if isinstance(value, str):
        return _canonical_string(value)
    if isinstance(value, list):
        return "[" + ",".join(
            _canonical_serialize(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        ) + "]"
    if isinstance(value, dict):
        items: list[str] = []
        for key in sorted(value):
            if not isinstance(key, str):
                raise BeaconValidationError(f"Non-string object key at {path}: {key!r}")
            if not key.isascii() or any(ord(character) < 0x20 or ord(character) > 0x7E for character in key):
                raise BeaconValidationError(f"Object key is outside printable ASCII at {path}: {key!r}")
            items.append(
                _canonical_string(key)
                + ":"
                + _canonical_serialize(value[key], f"{path}.{key}")
            )
        return "{" + ",".join(items) + "}"
    raise BeaconValidationError(f"Unsupported JSON value at {path}: {type(value).__name__}")


def canonical_json(payload: dict[str, Any]) -> str:
    """Return the exact UTB v1 canonical JSON text.

    The byte representation is UTF-8 without a BOM or trailing newline. Object
    keys are printable ASCII and sorted by ascending ASCII code. No whitespace
    is emitted. Strings escape only quotation mark, reverse solidus, and control
    characters; all other Unicode scalar values are emitted directly without
    normalization. Integers use ordinary base-10 notation.
    """
    _validate_canonical_subset(payload)
    return _canonical_serialize(payload)


def canonical_sha256(payload: dict[str, Any]) -> str:
    """Return the SHA-256 digest of the canonical UTF-8 byte representation."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def validate_beacon(payload: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Validate one beacon and return it unchanged."""
    specification = payload.get("specification")
    if not isinstance(specification, dict):
        raise BeaconValidationError("Missing specification object")
    if specification.get("name") != SPECIFICATION_NAME:
        raise BeaconValidationError(f"Unsupported specification name: {_echo(specification.get('name'))}")

    version = specification.get("schema_version")
    semantic_version_tuple(version, "schema version")
    if version != SUPPORTED_SCHEMA_VERSION:
        raise BeaconValidationError(
            f"Unsupported UTB schema version {_echo(version)}; supported version is {SUPPORTED_SCHEMA_VERSION}"
        )

    _validate_schema_contents(schema, version)

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

    # jsonschema has now passed, which is necessary but not sufficient: its
    # `pattern` handling is Python-regex-lenient about a trailing newline, and
    # its `format` handling is a no-op without rfc3339-validator. See
    # PATTERNED_FIELDS / FORMATTED_FIELDS.
    _validate_strict_formats(payload)

    compatibility = payload["compatibility"]
    minimum_reader_version = compatibility["minimum_reader_version"]
    if semantic_version_tuple(minimum_reader_version, "minimum reader version") > semantic_version_tuple(
        READER_VERSION, "reader version"
    ):
        raise BeaconValidationError(
            f"Beacon requires reader version {minimum_reader_version}; this reader is {READER_VERSION}"
        )
    if compatibility["canonicalization"] != CANONICALIZATION:
        raise BeaconValidationError(
            f"Unsupported canonicalization {_echo(compatibility['canonicalization'])}; expected {CANONICALIZATION!r}"
        )

    # Assert the canonical value domain without serialising. This used to call
    # canonical_json() and discard the string, which meant main() built the same
    # canonical text twice -- the most expensive step in the reader, done once
    # for its side effect and once for its value.
    _validate_canonical_subset(payload)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a Universal Thread Beacon profile offline")
    parser.add_argument("beacon", type=Path, help="Path to the beacon JSON file")
    parser.add_argument("--print-canonical", action="store_true", help="Print canonical UTB JSON v1")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        schema = load_json(DEFAULT_SCHEMA_PATH)
        beacon = load_json(args.beacon)
        validated = validate_beacon(beacon, schema)
        canonical = canonical_json(validated)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    except BeaconValidationError as exc:
        print(f"INVALID: {exc}")
        return 1

    print(f"VALID sha256={digest}")
    if args.print_canonical:
        print(canonical)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
