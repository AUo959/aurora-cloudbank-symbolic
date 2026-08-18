"""JSON Schema tests for the prepared corpus archaeology input contract."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "salvage" / "corpus_archaeology_input.schema.json"


@pytest.fixture(scope="module")
def input_schema() -> dict:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return schema


def _validator(schema: dict) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )


def _source(*, access: str, content) -> dict:
    return {
        "source_ref": "fixture:source",
        "title": "Fixture source",
        "source_type": "document",
        "platform": "fixture",
        "creator_type": "human",
        "authority_status": "historical",
        "confidence": 1.0,
        "artifact_id": None,
        "inventory_report_id": None,
        "content_access": access,
        "content": content,
    }


@pytest.mark.unit
def test_released_source_contract_accepts_content(input_schema: dict) -> None:
    payload = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:released",
        "source_inventory_ref": "inventory:" + "1" * 64,
        "sources": [
            _source(
                access="released",
                content="REQUIREMENT[fixture.one]: Preserve this source.\n",
            )
        ],
        "relationship_hints": [],
    }

    _validator(input_schema).validate(payload)


@pytest.mark.unit
def test_metadata_only_source_contract_accepts_absent_content(input_schema: dict) -> None:
    source = _source(access="metadata_only", content=None)
    source.pop("content")
    source["sha256"] = "2" * 64
    payload = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:metadata",
        "sources": [source],
    }

    _validator(input_schema).validate(payload)


@pytest.mark.unit
def test_metadata_only_source_contract_rejects_semantic_content(input_schema: dict) -> None:
    payload = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:blocked-content",
        "sources": [
            _source(
                access="metadata_only",
                content="TODO[unsafe.read]: This must remain inaccessible.\n",
            )
        ],
    }

    with pytest.raises(jsonschema.ValidationError):
        _validator(input_schema).validate(payload)


@pytest.mark.unit
def test_relationship_hint_contract_is_domain_neutral(input_schema: dict) -> None:
    payload = {
        "schema_version": "0.1.0",
        "corpus_id": "fixture:relationships",
        "sources": [
            _source(
                access="released",
                content=(
                    "REQUIREMENT[history.a]: Preserve A.\n"
                    "REQUIREMENT[history.b]: Preserve B.\n"
                ),
            )
        ],
        "relationship_hints": [
            {
                "left_intent_key": "history.a",
                "right_intent_key": "history.b",
                "relationship": "parallel",
                "rationale": "The prepared corpus records concurrent histories.",
                "evidence_source_refs": ["fixture:source"],
            }
        ],
    }

    _validator(input_schema).validate(payload)
