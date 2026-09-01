"""Project custody inventory + verbatim release manifest into corpus input.

This Phase-1 adapter is intentionally a pure in-memory transformation. It accepts
already-loaded #1382 inventory and custody-release records, verifies identity/digest
boundaries, and returns a deterministic #1533 prepared corpus record.

It does not open source artifacts, manifests, archives, or output paths. Transport and
filesystem I/O belong to a separately reviewed boundary.

Custody release authorizes exact bytes only. It does not grant creator identity,
epistemic authority, source semantics, or implementation-evidence classification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from tools.salvage.corpus_archaeology_shared import (
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
        "source_type": "unknown",
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
    """Return a deterministic prepared corpus without performing external I/O."""
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
