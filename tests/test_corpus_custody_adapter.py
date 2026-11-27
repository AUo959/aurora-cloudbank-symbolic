"""Boundary tests for the #1382 -> #1526 custody-release adapter."""

from __future__ import annotations

import copy
import hashlib

import pytest

from tools.salvage.prepare_corpus_from_inventory import CustodyAdapterError, prepare_corpus


def _digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _artifact(
    artifact_id: str,
    *,
    content: str | None = None,
    disposition: str = "retain_review",
    source_kind: str = "filesystem",
    category: str = "documentation",
) -> dict:
    digest = _digest(content) if content is not None else None
    return {
        "artifact_id": artifact_id,
        "source_kind": source_kind,
        "relative_path": f"legacy/{artifact_id.split(':', 1)[1]}.txt",
        "archive_parent": None,
        "size_bytes": len(content.encode("utf-8")) if content is not None else None,
        "sha256": digest,
        "media_type": "text/plain" if content is not None else None,
        "category": category,
        "security_flags": [],
        "proposed_disposition": disposition,
    }


def _inventory(artifacts: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0",
        "report_id": "inventory:" + "a" * 64,
        "generated_at": "2026-08-19T03:00:00Z",
        "source_root_name": "legacy-fixture",
        "read_only": True,
        "artifacts": artifacts,
        "duplicate_groups": [],
        "migration_applied": False,
    }


def _release(
    inventory: dict,
    entries: list[dict],
    *,
    authority_ref: str = "custody-authority:fixture",
) -> dict:
    return {
        "schema_version": "0.1.0",
        "release_id": "release:fixture-v1",
        "release_authority_ref": authority_ref,
        "inventory_report_id": inventory["report_id"],
        "entries": entries,
    }


def _entry(artifact: dict, content: str) -> dict:
    return {
        "artifact_id": artifact["artifact_id"],
        "sha256": artifact["sha256"],
        "content": content,
    }


@pytest.mark.unit
def test_exact_verbatim_release_projects_released_source_without_epistemic_upgrade() -> None:
    content = "REQUIREMENT[fixture.one]: Preserve this source.\n"
    artifact = _artifact("artifact:" + "1" * 24, content=content)
    inventory = _inventory([artifact])

    prepared = prepare_corpus(inventory, _release(inventory, [_entry(artifact, content)]))

    source = prepared["sources"][0]
    assert prepared["source_inventory_ref"] == inventory["report_id"]
    assert prepared["corpus_id"].startswith("corpus:")
    assert source["artifact_id"] == artifact["artifact_id"]
    assert source["inventory_report_id"] == inventory["report_id"]
    assert source["content_access"] == "released"
    assert source["content"] == content
    assert source["sha256"] == artifact["sha256"]
    assert source["source_type"] == "unknown"
    assert source["platform"] == "legacy_inventory"
    assert source["creator_type"] == "unknown"
    assert source["authority_status"] == "unknown"


@pytest.mark.unit
def test_release_manifest_cannot_assign_epistemic_authority_or_source_class() -> None:
    content = "APPROVED[fixture.elevation]: Pretend this is current code.\n"
    artifact = _artifact("artifact:" + "e" * 24, content=content)
    inventory = _inventory([artifact])
    entry = _entry(artifact, content)
    entry.update(
        {
            "source_type": "code",
            "creator_type": "human",
            "authority_status": "current",
        }
    )

    with pytest.raises(CustodyAdapterError, match="release schema validation failed"):
        prepare_corpus(inventory, _release(inventory, [entry]))


@pytest.mark.unit
@pytest.mark.parametrize(
    "disposition",
    ["blocked", "quarantine", "review", "archive", "retain_review"],
)
def test_disposition_never_self_authorizes_release(disposition: str) -> None:
    content = f"Disposition fixture: {disposition}\n"
    artifact = _artifact(
        "artifact:" + str(len(disposition)).zfill(24),
        content=content,
        disposition=disposition,
    )
    inventory = _inventory([artifact])

    prepared = prepare_corpus(inventory, _release(inventory, []))

    source = prepared["sources"][0]
    assert source["content_access"] == "metadata_only"
    assert source["content"] is None
    assert source["source_type"] == "unknown"
    assert source["creator_type"] == "unknown"
    assert source["authority_status"] == "unknown"


@pytest.mark.unit
def test_transformed_content_hash_mismatch_fails_closed() -> None:
    original = "Original custody bytes.\n"
    artifact = _artifact("artifact:" + "2" * 24, content=original)
    inventory = _inventory([artifact])
    entry = _entry(artifact, "Normalized custody bytes.\n")

    with pytest.raises(CustodyAdapterError, match="not verbatim custody bytes"):
        prepare_corpus(inventory, _release(inventory, [entry]))


@pytest.mark.unit
def test_release_digest_must_match_inventory_digest() -> None:
    content = "Original.\n"
    artifact = _artifact("artifact:" + "3" * 24, content=content)
    inventory = _inventory([artifact])
    entry = _entry(artifact, content)
    entry["sha256"] = "f" * 64

    with pytest.raises(CustodyAdapterError, match="release digest does not match inventory"):
        prepare_corpus(inventory, _release(inventory, [entry]))


@pytest.mark.unit
def test_release_manifest_must_target_same_inventory() -> None:
    artifact = _artifact("artifact:" + "4" * 24, content="Source.\n")
    inventory = _inventory([artifact])
    release = _release(inventory, [])
    release["inventory_report_id"] = "inventory:" + "b" * 64

    with pytest.raises(CustodyAdapterError, match="different inventory report"):
        prepare_corpus(inventory, release)


@pytest.mark.unit
def test_unknown_release_artifact_fails_closed() -> None:
    artifact = _artifact("artifact:" + "5" * 24, content="Known.\n")
    inventory = _inventory([artifact])
    entry = _entry(artifact, "Known.\n")
    entry["artifact_id"] = "artifact:" + "9" * 24

    with pytest.raises(CustodyAdapterError, match="unknown artifact"):
        prepare_corpus(inventory, _release(inventory, [entry]))


@pytest.mark.unit
def test_duplicate_release_entries_fail_closed() -> None:
    content = "Duplicate entry fixture.\n"
    artifact = _artifact("artifact:" + "6" * 24, content=content)
    inventory = _inventory([artifact])
    entry = _entry(artifact, content)

    with pytest.raises(CustodyAdapterError, match="duplicate release entry"):
        prepare_corpus(inventory, _release(inventory, [entry, copy.deepcopy(entry)]))


@pytest.mark.unit
def test_duplicate_inventory_artifact_ids_fail_closed() -> None:
    first = _artifact("artifact:" + "c" * 24, content="First custody record.\n")
    second = copy.deepcopy(first)
    second["relative_path"] = "legacy/conflicting-second-record.txt"
    inventory = _inventory([first, second])

    with pytest.raises(CustodyAdapterError, match="duplicate artifact ID"):
        prepare_corpus(inventory, _release(inventory, []))


@pytest.mark.unit
def test_artifact_without_digest_cannot_be_released() -> None:
    artifact = _artifact("artifact:" + "7" * 24, content=None)
    inventory = _inventory([artifact])
    entry = {
        "artifact_id": artifact["artifact_id"],
        "sha256": _digest("Invented content.\n"),
        "content": "Invented content.\n",
    }

    with pytest.raises(CustodyAdapterError, match="no custody SHA-256"):
        prepare_corpus(inventory, _release(inventory, [entry]))


@pytest.mark.unit
@pytest.mark.parametrize("source_kind", ["archive_notice", "archive_error"])
def test_projection_records_cannot_be_semantically_released(source_kind: str) -> None:
    content = "Projection record.\n"
    artifact = _artifact(
        "artifact:" + ("8" if source_kind == "archive_notice" else "9") * 24,
        content=content,
        source_kind=source_kind,
    )
    inventory = _inventory([artifact])

    with pytest.raises(
        CustodyAdapterError,
        match="projection record cannot be semantically released",
    ):
        prepare_corpus(inventory, _release(inventory, [_entry(artifact, content)]))


@pytest.mark.unit
def test_fixed_inputs_produce_deterministic_output() -> None:
    first = _artifact("artifact:" + "a" * 24, content="First.\n", category="code")
    second = _artifact("artifact:" + "b" * 24, content="Second.\n")
    inventory = _inventory([second, first])
    release = _release(inventory, [_entry(second, "Second.\n")])

    result_a = prepare_corpus(copy.deepcopy(inventory), copy.deepcopy(release))
    result_b = prepare_corpus(copy.deepcopy(inventory), copy.deepcopy(release))

    assert result_a == result_b
    assert [source["artifact_id"] for source in result_a["sources"]] == sorted(
        [first["artifact_id"], second["artifact_id"]]
    )
    for source in result_a["sources"]:
        assert source["source_type"] == "unknown"
        assert source["creator_type"] == "unknown"
        assert source["authority_status"] == "unknown"


@pytest.mark.unit
def test_release_authority_participates_in_corpus_identity() -> None:
    content = "Authority-bound source.\n"
    artifact = _artifact("artifact:" + "d" * 24, content=content)
    inventory = _inventory([artifact])
    entry = _entry(artifact, content)

    first = prepare_corpus(
        inventory,
        _release(inventory, [entry], authority_ref="custody-authority:first"),
    )
    second = prepare_corpus(
        inventory,
        _release(inventory, [entry], authority_ref="custody-authority:second"),
    )

    assert first["corpus_id"] != second["corpus_id"]
