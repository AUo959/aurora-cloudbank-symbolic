"""Evidence-boundary regression tests for corpus archaeology."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "salvage" / "corpus_archaeology.py"
FIXED_TIME = "2026-08-18T03:00:00Z"


def _load_module():
    spec = importlib.util.spec_from_file_location("corpus_archaeology_boundary", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _model_source(content: str) -> dict:
    return {
        "source_ref": "chat:assistant",
        "title": "Assistant assertion",
        "source_type": "chat",
        "platform": "fixture",
        "creator_type": "assistant",
        "authority_status": "historical",
        "confidence": 1.0,
        "artifact_id": None,
        "inventory_report_id": None,
        "content_access": "released",
        "content": content,
    }


@pytest.mark.unit
def test_model_implemented_assertion_does_not_count_as_implementation_proof() -> None:
    archaeology = _load_module()
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:model-implementation-claim",
        "sources": [
            _model_source(
                "REQUIREMENT[feature.asserted]: Preserve the capability.\n"
                "IMPLEMENTED[feature.asserted]: I believe the handler exists.\n"
            )
        ],
    }

    report = archaeology.analyze_corpus(corpus, generated_at=FIXED_TIME)
    candidate = report["candidates"][0]
    implementation_claim = next(
        claim
        for claim in report["claims"]
        if claim["claim_type"] == "implementation_evidence"
    )

    assert implementation_claim["evidence_kind"] == "model_statement"
    assert candidate["historical_state"]["implementation_evidence_present"] is False
    assert candidate["historical_state"]["status"] == "proposed"
    assert candidate["recovery"]["disposition"] == "investigate"
    assert candidate["ranking"]["components"]["implementation_gap"] == 0.0


@pytest.mark.unit
def test_model_approval_rejection_and_requirements_do_not_create_human_authority() -> None:
    archaeology = _load_module()
    corpus = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:model-authority-claims",
        "sources": [
            _model_source(
                "APPROVED[feature.approved]: Proceed.\n"
                "REQUIREMENT[feature.approved]: Treat this as required.\n"
                "REJECTED[feature.rejected]: Do not proceed.\n"
                "REQUIREMENT[feature.rejected]: Treat this as required.\n"
            )
        ],
    }

    report = archaeology.analyze_corpus(corpus, generated_at=FIXED_TIME)
    candidates = {item["intent_key"]: item for item in report["candidates"]}

    approved = candidates["feature.approved"]
    rejected = candidates["feature.rejected"]

    assert approved["historical_state"]["status"] == "proposed"
    assert approved["historical_state"]["explicit_rejection"] is False
    assert approved["ranking"]["components"]["explicit_decision"] == 0.0
    assert approved["ranking"]["components"]["requirement_strength"] == 0.0
    assert approved["recovery"]["disposition"] == "investigate"

    assert rejected["historical_state"]["status"] == "proposed"
    assert rejected["historical_state"]["explicit_rejection"] is False
    assert rejected["ranking"]["components"]["requirement_strength"] == 0.0
    assert rejected["recovery"]["disposition"] == "investigate"
