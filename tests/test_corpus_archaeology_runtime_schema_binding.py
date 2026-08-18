"""Runtime binding tests for the prepared-corpus JSON Schema contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "salvage" / "corpus_archaeology.py"
FIXED_TIME = "2026-08-18T03:00:00Z"


def _load_module():
    spec = importlib.util.spec_from_file_location("corpus_archaeology_schema_binding", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source() -> dict:
    return {
        "source_ref": "fixture:source",
        "title": "Fixture source",
        "source_type": "document",
        "creator_type": "human",
        "authority_status": "historical",
        "content_access": "released",
        "content": "REQUIREMENT[fixture.schema]: Preserve schema parity.\n",
    }


def _corpus(source: dict | None = None) -> dict:
    return {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:runtime-schema-binding",
        "sources": [source or _source()],
    }


@pytest.mark.unit
def test_runtime_rejects_unknown_top_level_and_source_fields() -> None:
    archaeology = _load_module()

    top_level = _corpus()
    top_level["unexpected"] = "must fail"
    with pytest.raises(archaeology.CorpusArchaeologyError, match="additionalProperties"):
        archaeology.analyze_corpus(top_level, generated_at=FIXED_TIME)

    source = _source()
    source["unexpected"] = "must fail"
    with pytest.raises(archaeology.CorpusArchaeologyError, match="additionalProperties"):
        archaeology.analyze_corpus(_corpus(source), generated_at=FIXED_TIME)


@pytest.mark.unit
def test_runtime_rejects_missing_schema_required_source_fields() -> None:
    archaeology = _load_module()

    for field in ("source_type", "creator_type", "authority_status", "content_access"):
        source = _source()
        source.pop(field)
        with pytest.raises(archaeology.CorpusArchaeologyError, match="required"):
            archaeology.analyze_corpus(_corpus(source), generated_at=FIXED_TIME)


@pytest.mark.unit
@pytest.mark.parametrize("value", ["0.5", True])
def test_runtime_rejects_non_schema_numeric_confidence(value) -> None:
    archaeology = _load_module()
    source = _source()
    source["confidence"] = value

    with pytest.raises(archaeology.CorpusArchaeologyError, match="violates type"):
        archaeology.analyze_corpus(_corpus(source), generated_at=FIXED_TIME)


@pytest.mark.unit
def test_runtime_rejects_malformed_metadata_only_digest() -> None:
    archaeology = _load_module()
    source = _source()
    source.update(
        {
            "content_access": "metadata_only",
            "content": None,
            "sha256": "not-a-sha256",
        }
    )

    with pytest.raises(archaeology.CorpusArchaeologyError, match="violates pattern"):
        archaeology.analyze_corpus(_corpus(source), generated_at=FIXED_TIME)


@pytest.mark.unit
def test_runtime_fails_closed_when_committed_schema_is_unavailable(tmp_path: Path) -> None:
    archaeology = _load_module()
    archaeology.INPUT_SCHEMA_PATH = tmp_path / "missing.schema.json"

    with pytest.raises(
        archaeology.CorpusArchaeologyError,
        match="committed prepared-corpus input schema is unavailable or invalid",
    ):
        archaeology.analyze_corpus(_corpus(), generated_at=FIXED_TIME)


@pytest.mark.unit
def test_schema_bound_runtime_still_accepts_valid_prepared_corpus() -> None:
    archaeology = _load_module()
    report = archaeology.analyze_corpus(_corpus(), generated_at=FIXED_TIME)

    assert report["schema_version"] == "0.1.0"
    assert report["read_only"] is True
    assert report["mutation_performed"] is False
    assert report["candidates"][0]["intent_key"] == "fixture.schema"
