#!/usr/bin/env python3
"""Project custody inventory + verbatim release manifest into corpus input.

This adapter deliberately does not open legacy source artifacts. It accepts only the
#1382 inventory report and a separate custody-issued release manifest, verifies
identity/digest boundaries, and emits a deterministic #1533 prepared corpus record.

Custody release authorizes exact bytes only. It does not grant creator identity,
epistemic authority, or implementation-evidence classification.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

import jsonschema

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from tools.salvage.corpus_archaeology_shared import (  # noqa: E402
    CorpusArchaeologyError,
    make_id,
    sha256_text,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_SCHEMA_PATH = (
    REPO_ROOT / "schemas" / "salvage" / "legacy_asset_inventory.schema.json"
)
RELEASE_SCHEMA_PATH = (
    REPO_ROOT / "schemas" / "salvage" / "corpus_custody_release.schema.json"
)
CORPUS_SCHEMA_PATH = (
    REPO_ROOT / "schemas" / "salvage" / "corpus_archaeology_input.schema.json"
)
MAX_MANIFEST_BYTES = 64 * 1024 * 1024

_CATEGORY_SOURCE_TYPE = {
    "code": "code",
    "documentation": "document",
    "data": "artifact",
    "generated_media": "artifact",
    "configuration": "artifact",
    "archive": "artifact",
    "executable": "artifact",
    "unknown": "unknown",
}


class CustodyAdapterError(CorpusArchaeologyError):
    """Inventory/release projection violates a custody or schema boundary."""


def _load_validator(path: Path) -> jsonschema.Draft202012Validator:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        raise CustodyAdapterError(
            f"committed schema unavailable or invalid: {path.name}"
        ) from exc
    return jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )


def _validate(value: Any, path: Path, label: str) -> None:
    errors = sorted(
        _load_validator(path).iter_errors(value),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if not errors:
        return
    error = errors[0]
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    raise CustodyAdapterError(
        f"{label} schema validation failed at {location}: {error.message}"
    )


def _index_artifacts(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for artifact in inventory["artifacts"]:
        artifact_id = artifact["artifact_id"]
        if artifact_id in indexed:
            raise CustodyAdapterError(
                f"inventory contains duplicate artifact ID: {artifact_id}"
            )
        indexed[artifact_id] = artifact
    return indexed


def _index_releases(
    release: dict[str, Any], artifacts: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for entry in release["entries"]:
        artifact_id = entry["artifact_id"]
        if artifact_id in indexed:
            raise CustodyAdapterError(f"duplicate release entry for artifact: {artifact_id}")
        if artifact_id not in artifacts:
            raise CustodyAdapterError(f"release references unknown artifact: {artifact_id}")
        indexed[artifact_id] = entry
    return indexed


def _verify_release(artifact: dict[str, Any], entry: dict[str, Any]) -> None:
    artifact_id = artifact["artifact_id"]
    if artifact["source_kind"] in {"archive_notice", "archive_error"}:
        raise CustodyAdapterError(
            f"projection record cannot be semantically released: {artifact_id}"
        )
    inventory_digest = artifact.get("sha256")
    if inventory_digest is None:
        raise CustodyAdapterError(
            f"released artifact has no custody SHA-256: {artifact_id}"
        )
    if entry["sha256"] != inventory_digest:
        raise CustodyAdapterError(
            f"release digest does not match inventory: {artifact_id}"
        )
    if sha256_text(entry["content"]) != inventory_digest:
        raise CustodyAdapterError(
            f"released content is not verbatim custody bytes: {artifact_id}"
        )


def _base_source(artifact: dict[str, Any], report_id: str) -> dict[str, Any]:
    source: dict[str, Any] = {
        "source_ref": f"custody:{artifact['artifact_id']}",
        "title": artifact["relative_path"],
        "source_type": _CATEGORY_SOURCE_TYPE[artifact["category"]],
        "platform": "legacy_inventory",
        "creator_type": "unknown",
        "authority_status": "unknown",
        "artifact_id": artifact["artifact_id"],
        "inventory_report_id": report_id,
        "content_access": "metadata_only",
        "content": None,
    }
    if artifact.get("sha256") is not None:
        source["sha256"] = artifact["sha256"]
    return source


def _released_source(
    artifact: dict[str, Any], entry: dict[str, Any], report_id: str
) -> dict[str, Any]:
    _verify_release(artifact, entry)
    source = _base_source(artifact, report_id)
    source["content_access"] = "released"
    source["content"] = entry["content"]
    source["sha256"] = entry["sha256"]
    return source


def prepare_corpus(
    inventory: dict[str, Any], release: dict[str, Any]
) -> dict[str, Any]:
    """Return a deterministic prepared corpus without reading legacy artifacts."""
    _validate(inventory, INVENTORY_SCHEMA_PATH, "inventory")
    _validate(release, RELEASE_SCHEMA_PATH, "release")

    report_id = inventory["report_id"]
    if release["inventory_report_id"] != report_id:
        raise CustodyAdapterError("release manifest targets a different inventory report")

    artifacts = _index_artifacts(inventory)
    if not artifacts:
        raise CustodyAdapterError("inventory contains no artifacts to project")
    releases = _index_releases(release, artifacts)

    sources = []
    for artifact_id in sorted(artifacts):
        artifact = artifacts[artifact_id]
        entry = releases.get(artifact_id)
        source = (
            _released_source(artifact, entry, report_id)
            if entry is not None
            else _base_source(artifact, report_id)
        )
        sources.append(source)

    identity_material = {
        "inventory_report_id": report_id,
        "release_id": release["release_id"],
        "release_authority_ref": release["release_authority_ref"],
        "sources": sources,
    }
    prepared = {
        "schema_version": "0.1.0",
        "corpus_id": make_id("corpus", identity_material, length=64),
        "source_inventory_ref": report_id,
        "sources": sources,
        "relationship_hints": [],
    }
    _validate(prepared, CORPUS_SCHEMA_PATH, "prepared corpus")
    return prepared


def _read_json(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise CustodyAdapterError(f"input manifest must not be a symlink: {path}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise CustodyAdapterError(f"cannot open input manifest safely: {path}") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise CustodyAdapterError(f"input manifest must be a regular file: {path}")
        if info.st_size > MAX_MANIFEST_BYTES:
            raise CustodyAdapterError(f"input manifest exceeds size limit: {path}")
        with os.fdopen(fd, "r", encoding="utf-8") as stream:
            fd = -1
            value = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CustodyAdapterError(f"invalid input manifest: {path}") from exc
    finally:
        if fd >= 0:
            os.close(fd)
    if not isinstance(value, dict):
        raise CustodyAdapterError(
            f"input manifest must contain a JSON object: {path}"
        )
    return value


def _write_new(path: Path, payload: str) -> None:
    path = path.resolve(strict=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise CustodyAdapterError(
            f"output path must be new and writable: {path}"
        ) from exc
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Project a custody inventory + verbatim release manifest into corpus input"
        )
    )
    parser.add_argument("inventory", type=Path)
    parser.add_argument("release", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    try:
        inventory = _read_json(args.inventory)
        release = _read_json(args.release)
        prepared = prepare_corpus(inventory, release)
        payload = json.dumps(
            prepared,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ) + "\n"
        if args.output is None:
            print(payload, end="")
        else:
            if args.output.resolve(strict=False) in {
                args.inventory.resolve(strict=False),
                args.release.resolve(strict=False),
            }:
                raise CustodyAdapterError(
                    "output path must not replace an input manifest"
                )
            _write_new(args.output, payload)
    except CustodyAdapterError as exc:
        print(f"INVALID: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
