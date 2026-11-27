"""Integration tests proving custody release cannot manufacture evidence authority."""

from __future__ import annotations

import hashlib

import pytest

from tools.salvage.corpus_archaeology import analyze_corpus
from tools.salvage.prepare_corpus_from_inventory import prepare_corpus


def _digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _inventory(category: str, content: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "report_id": "inventory:" + "c" * 64,
        "generated_at": "2026-08-19T03:00:00Z",
        "source_root_name": "epistemic-fixture",
        "read_only": True,
        "artifacts": [
            {
                "artifact_id": "artifact:" + "e" * 24,
                "source_kind": "filesystem",
                "relative_path": "legacy/claim.txt",
                "archive_parent": None,
                "size_bytes": len(content.encode("utf-8")),
                "sha256": _digest(content),
                "media_type": "text/plain",
                "category": category,
                "security_flags": [],
                "proposed_disposition": "retain_review",
            }
        ],
        "duplicate_groups": [],
        "migration_applied": False,
    }


def _release(inventory: dict, content: str) -> dict:
    artifact = inventory["artifacts"][0]
    return {
        "schema_version": "0.1.0",
        "release_id": "release:epistemic-fixture",
        "release_authority_ref": "custody-authority:fixture",
        "inventory_report_id": inventory["report_id"],
        "entries": [
            {
                "artifact_id": artifact["artifact_id"],
                "sha256": artifact["sha256"],
                "content": content,
            }
        ],
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    "category",
    [
        "code",
        "documentation",
        "data",
        "configuration",
        "generated_media",
        "archive",
        "executable",
        "unknown",
    ],
)
def test_custody_categories_do_not_become_implementation_authority(
    category: str,
) -> None:
    content = "IMPLEMENTED[fixture.capability]: Custody metadata says implemented.\n"
    inventory = _inventory(category, content)
    prepared = prepare_corpus(inventory, _release(inventory, content))

    source = prepared["sources"][0]
    assert source["source_type"] == "unknown"
    assert source["creator_type"] == "unknown"
    assert source["authority_status"] == "unknown"

    report = analyze_corpus(prepared, generated_at="2026-08-19T03:00:00Z")
    claim = report["claims"][0]
    candidate = report["candidates"][0]

    assert claim["claim_type"] == "implementation_evidence"
    assert claim["evidence_kind"] == "unknown"
    assert candidate["historical_state"]["implementation_evidence_present"] is False
    assert candidate["historical_state"]["status"] == "proposed"
    assert candidate["preservation"]["implementation_preserved"] is None
