"""Custody-identity and conflicting-history tests for corpus archaeology."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "salvage" / "corpus_archaeology.py"
SCHEMA_PATH = REPO_ROOT / "schemas" / "salvage" / "corpus_archaeology_report.schema.json"
FIXED_TIME = "2026-08-18T03:00:00Z"


def _load_module():
    spec = importlib.util.spec_from_file_location("corpus_archaeology_conflicts", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(
    source_ref: str,
    content: str,
    *,
    source_type: str = "document",
    creator_type: str = "human",
    authority_status: str = "historical",
) -> dict:
    return {
        "source_ref": source_ref,
        "title": source_ref,
        "source_type": source_type,
        "platform": "fixture",
        "creator_type": creator_type,
        "authority_status": authority_status,
        "confidence": 1.0,
        "artifact_id": None,
        "inventory_report_id": None,
        "content_access": "released",
        "content": content,
    }


@pytest.mark.unit
def test_top_level_inventory_reference_changes_report_identity() -> None:
    archaeology = _load_module()
    base = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:custody-identity",
        "sources": [
            _source(
                "doc:one",
                "REQUIREMENT[custody.identity]: Bind analysis to custody.\n",
            )
        ],
    }

    first = archaeology.analyze_corpus(
        {**base, "source_inventory_ref": "inventory:" + "1" * 64},
        generated_at=FIXED_TIME,
    )
    second = archaeology.analyze_corpus(
        {**base, "source_inventory_ref": "inventory:" + "2" * 64},
        generated_at=FIXED_TIME,
    )

    assert first["report_id"] != second["report_id"]
    assert first["sources"] == second["sources"]
    assert first["claims"] == second["claims"]


@pytest.mark.unit
def test_rejection_and_historical_implementation_preserve_conflict_without_claiming_current_state() -> None:
    archaeology = _load_module()
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:conflicting-history",
        "sources": [
            _source(
                "issue:human-decision",
                "REJECTED[feature.conflict]: Do not build this capability.\n",
                source_type="issue",
            ),
            _source(
                "code:historical-artifact",
                "IMPLEMENTED[feature.conflict]: A concrete implementation existed.\n",
                source_type="code",
                creator_type="system",
            ),
        ],
    }

    report = archaeology.analyze_corpus(corpus, generated_at=FIXED_TIME)
    candidate = report["candidates"][0]

    assert candidate["historical_state"] == {
        "status": "unknown",
        "explicit_rejection": True,
        "implementation_evidence_present": True,
        "partial_implementation_evidence_present": False,
    }
    assert candidate["recovery"]["disposition"] == "investigate"
    assert "coexist" in candidate["recovery"]["rationale"]
    assert candidate["preservation"]["implementation_preserved"] is None
    assert candidate["preservation"]["capability_preserved"] is None
    assert candidate["preservation"]["intent_preserved"] is None

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(report)


@pytest.mark.unit
def test_current_implementation_artifact_can_establish_implementation_preserved() -> None:
    archaeology = _load_module()
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:current-implementation",
        "sources": [
            _source(
                "doc:requirement",
                "REQUIREMENT[feature.current]: Preserve the current implementation.\n",
            ),
            _source(
                "code:current-artifact",
                "IMPLEMENTED[feature.current]: Current code implements the capability.\n",
                source_type="code",
                creator_type="system",
                authority_status="current",
            ),
        ],
    }

    report = archaeology.analyze_corpus(corpus, generated_at=FIXED_TIME)
    candidate = report["candidates"][0]

    assert candidate["historical_state"]["status"] == "implemented"
    assert candidate["preservation"]["implementation_preserved"] is True
    assert candidate["preservation"]["capability_preserved"] is None
    assert candidate["preservation"]["intent_preserved"] is None
