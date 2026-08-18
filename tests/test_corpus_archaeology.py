"""Determinism, provenance, and preservation tests for corpus archaeology."""

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
    spec = importlib.util.spec_from_file_location("corpus_archaeology", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def archaeology_module():
    return _load_module()


@pytest.fixture(scope="module")
def report_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _source(
    *,
    source_ref: str,
    title: str,
    content: str | None,
    source_type: str = "document",
    creator_type: str = "human",
    authority_status: str = "historical",
    content_access: str = "released",
    confidence: float = 1.0,
) -> dict:
    return {
        "source_ref": source_ref,
        "title": title,
        "source_type": source_type,
        "platform": "fixture",
        "creator_type": creator_type,
        "authority_status": authority_status,
        "confidence": confidence,
        "artifact_id": None,
        "inventory_report_id": None,
        "content_access": content_access,
        "content": content,
    }


@pytest.mark.unit
def test_report_is_deterministic_schema_valid_and_read_only(
    archaeology_module,
    report_schema: dict,
) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:threadcore",
        "source_inventory_ref": "inventory:" + "a" * 64,
        "sources": [
            _source(
                source_ref="chat:001",
                title="Native thread",
                content=(
                    "REQUIREMENT[threadcore.unutilized_logic]: Extract unutilized logic.\n"
                    "APPROVED[threadcore.unutilized_logic]: Proceed with the extractor.\n"
                    "TODO[threadcore.unutilized_logic]: Implement the read-only pass.\n"
                ),
            ),
            _source(
                source_ref="doc:002",
                title="Current implementation note",
                creator_type="assistant",
                content=(
                    "RATIONALE[threadcore.unutilized_logic]: "
                    "Absence of implementation is not rejection.\n"
                ),
            ),
        ],
        "relationship_hints": [],
    }

    first = archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)
    second = archaeology_module.analyze_corpus(
        {
            **corpus,
            "sources": list(reversed(corpus["sources"])),
        },
        generated_at=FIXED_TIME,
    )

    assert first == second
    assert first["read_only"] is True
    assert first["mutation_performed"] is False
    assert len(first["claims"]) == 4
    assert len(first["candidates"]) == 1
    candidate = first["candidates"][0]
    assert candidate["intent_key"] == "threadcore.unutilized_logic"
    assert candidate["recovery"]["disposition"] == "investigate"
    assert candidate["ranking"]["components"]["implementation_gap"] == 1.0
    assert candidate["historical_state"]["status"] == "approved"

    jsonschema.Draft202012Validator.check_schema(report_schema)
    jsonschema.Draft202012Validator(
        report_schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(first)


@pytest.mark.unit
def test_claims_retain_exact_line_span_and_creator_evidence_type(
    archaeology_module,
) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:evidence",
        "sources": [
            _source(
                source_ref="chat:human",
                title="Human source",
                content=(
                    "ordinary context\n"
                    "REQUIREMENT[evidence.boundary]: Preserve exact spans.\n"
                ),
            ),
            _source(
                source_ref="chat:assistant",
                title="Assistant source",
                creator_type="assistant",
                content="PATCH[evidence.boundary]: Add a deterministic span record.\n",
            ),
        ],
    }

    report = archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)
    human_claim = next(
        claim for claim in report["claims"] if claim["span"]["source_ref"] == "chat:human"
    )
    model_claim = next(
        claim for claim in report["claims"] if claim["span"]["source_ref"] == "chat:assistant"
    )

    assert human_claim["span"]["line_start"] == 2
    assert human_claim["span"]["line_end"] == 2
    assert human_claim["span"]["excerpt"] == (
        "REQUIREMENT[evidence.boundary]: Preserve exact spans."
    )
    assert human_claim["evidence_kind"] == "human_statement"
    assert model_claim["evidence_kind"] == "model_statement"


@pytest.mark.unit
def test_explicit_implementation_and_rejection_are_not_treated_as_missing(
    archaeology_module,
) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:status",
        "sources": [
            _source(
                source_ref="doc:requirements",
                title="Requirements",
                content=(
                    "REQUIREMENT[feature.one]: Keep feature one.\n"
                    "REQUIREMENT[feature.two]: Keep feature two.\n"
                ),
            ),
            _source(
                source_ref="code:implementation",
                title="Implementation record",
                source_type="code",
                creator_type="system",
                authority_status="current",
                content="IMPLEMENTED[feature.one]: Current handler exists.\n",
            ),
            _source(
                source_ref="issue:decision",
                title="Decision record",
                source_type="issue",
                content="REJECTED[feature.two]: Rejected after explicit review.\n",
            ),
        ],
    }

    report = archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)
    candidates = {item["intent_key"]: item for item in report["candidates"]}

    implemented = candidates["feature.one"]
    rejected = candidates["feature.two"]

    assert implemented["historical_state"]["status"] == "implemented"
    assert implemented["recovery"]["disposition"] == "preserve"
    assert implemented["ranking"]["components"]["implementation_gap"] == 0.0
    implementation_claim = next(
        claim
        for claim in report["claims"]
        if claim["intent_key"] == "feature.one"
        and claim["claim_type"] == "implementation_evidence"
    )
    assert implementation_claim["evidence_kind"] == "implementation_artifact"

    assert rejected["historical_state"]["status"] == "rejected"
    assert rejected["historical_state"]["explicit_rejection"] is True
    assert rejected["recovery"]["disposition"] == "reject_with_evidence"
    assert rejected["ranking"]["components"]["implementation_gap"] == 0.0


@pytest.mark.unit
def test_metadata_only_source_is_preserved_without_content_analysis(
    archaeology_module,
) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:metadata-only",
        "sources": [
            {
                "source_ref": "artifact:blocked",
                "title": "Quarantined archive member",
                "source_type": "artifact",
                "platform": "legacy_inventory",
                "creator_type": "unknown",
                "authority_status": "reference",
                "confidence": 0.5,
                "artifact_id": "artifact:" + "1" * 24,
                "inventory_report_id": "inventory:" + "2" * 64,
                "content_access": "metadata_only",
                "content": None,
                "sha256": "3" * 64,
            }
        ],
    }

    report = archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)

    assert report["sources"][0]["content_access"] == "metadata_only"
    assert report["sources"][0]["sha256"] == "3" * 64
    assert report["claims"] == []
    assert report["candidates"] == []


@pytest.mark.unit
def test_metadata_only_source_rejects_supplied_content(archaeology_module) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:metadata-violation",
        "sources": [
            _source(
                source_ref="artifact:blocked",
                title="Blocked source",
                content="TODO[unsafe.read]: This must not be analyzed.\n",
                source_type="artifact",
                content_access="metadata_only",
            )
        ],
    }

    with pytest.raises(
        archaeology_module.CorpusArchaeologyError,
        match="metadata_only",
    ):
        archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)


@pytest.mark.unit
def test_released_source_hash_must_match_prepared_content(
    archaeology_module,
) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:hash-mismatch",
        "sources": [
            {
                **_source(
                    source_ref="doc:hash",
                    title="Hashed source",
                    content="REQUIREMENT[hash.check]: Validate source content.\n",
                ),
                "sha256": "0" * 64,
            }
        ],
    }

    with pytest.raises(
        archaeology_module.CorpusArchaeologyError,
        match="does not match prepared content",
    ):
        archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)


@pytest.mark.unit
def test_unkeyed_claim_keeps_provenance_without_candidate_promotion(
    archaeology_module,
) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:unkeyed",
        "sources": [
            _source(
                source_ref="doc:unkeyed",
                title="Unkeyed source",
                content="TODO: Review this later.\n",
            )
        ],
    }

    report = archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)

    assert len(report["claims"]) == 1
    assert report["claims"][0]["intent_key"] is None
    assert report["candidates"] == []
    assert report["unkeyed_claim_ids"] == [report["claims"][0]["claim_id"]]


@pytest.mark.unit
def test_relationship_hints_preserve_parallel_history_without_adjudication(
    archaeology_module,
) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:relationship",
        "sources": [
            _source(
                source_ref="doc:a",
                title="History A",
                content="REQUIREMENT[history.a]: Preserve history A.\n",
            ),
            _source(
                source_ref="doc:b",
                title="History B",
                content="REQUIREMENT[history.b]: Preserve history B.\n",
            ),
        ],
        "relationship_hints": [
            {
                "left_intent_key": "history.a",
                "right_intent_key": "history.b",
                "relationship": "parallel",
                "rationale": "The prepared sources describe concurrent histories.",
                "evidence_source_refs": ["doc:a", "doc:b"],
            }
        ],
    }

    report = archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)

    assert len(report["relationships"]) == 1
    relationship = report["relationships"][0]
    assert relationship["relationship"] == "parallel"
    assert relationship["evidence_source_refs"] == ["doc:a", "doc:b"]


@pytest.mark.unit
def test_markdown_renderer_is_deterministic_and_reports_candidate_state(
    archaeology_module,
) -> None:
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:markdown",
        "sources": [
            _source(
                source_ref="doc:one",
                title="One",
                content="REQUIREMENT[feature.md]: Render a stable summary.\n",
            )
        ],
    }

    report = archaeology_module.analyze_corpus(corpus, generated_at=FIXED_TIME)
    markdown = archaeology_module.render_markdown(report)

    assert markdown.startswith("# Corpus Archaeology Report\n")
    assert "`feature.md`" in markdown
    assert "Disposition: `investigate`" in markdown
    assert report["report_id"] in markdown
