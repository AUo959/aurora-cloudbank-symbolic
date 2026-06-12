"""Schema tests for recovered ethics protocol custody fixtures.

These tests keep the recovered Sherlock / Watson / Moriarty / Tribunal /
SHADOWFAX material in a planning-only custody lane. They intentionally do not
wire any recovered protocol into runtime ethics enforcement.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "ethics" / "recovered_protocol.schema.json"
MANIFEST_PATH = (
    REPO_ROOT
    / "docs"
    / "ethics"
    / "recovered_protocols"
    / "recovered_protocol_manifest.example.json"
)
EXPECTED_PROTOCOLS = {"sherlock", "watson", "moriarty", "tribunal", "shadowfax"}


@pytest.fixture(scope="module")
def recovered_protocol_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def custody_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def protocol_records(custody_manifest: dict) -> list[dict]:
    return custody_manifest["protocols"]


@pytest.mark.unit
def test_manifest_is_planning_only(custody_manifest: dict) -> None:
    assert custody_manifest["runtime_posture"] == "planning_only_no_runtime_enforcement"
    assert "not runtime canon" in custody_manifest["canon_posture"]
    assert "do not authorize enforcement wiring" in custody_manifest["canon_posture"]


@pytest.mark.unit
def test_manifest_contains_expected_protocol_records(protocol_records: list[dict]) -> None:
    assert {record["protocol_id"] for record in protocol_records} == EXPECTED_PROTOCOLS


@pytest.mark.unit
def test_protocol_records_validate_against_common_schema(
    recovered_protocol_schema: dict,
    protocol_records: list[dict],
) -> None:
    for record in protocol_records:
        jsonschema.validate(record, recovered_protocol_schema)


@pytest.mark.unit
def test_protocol_records_keep_custody_blockers(protocol_records: list[dict]) -> None:
    for record in protocol_records:
        assert "custody" in record, f"{record['protocol_id']} must include custody metadata"
        blockers = record["custody"].get("blockers", [])
        assert blockers, f"{record['protocol_id']} must keep explicit custody blockers"
        assert any("hash" in blocker.lower() for blocker in blockers), record["protocol_id"]


@pytest.mark.unit
def test_protocol_records_are_not_repo_canon(protocol_records: list[dict]) -> None:
    for record in protocol_records:
        assert record["status"] != "repo_canon"
        assert record["source_classification"] != "repo_canon"


@pytest.mark.unit
def test_protocol_separation_of_duties(protocol_records: list[dict]) -> None:
    by_protocol = {record["protocol_id"]: record for record in protocol_records}

    assert "enforce_containment" in by_protocol["sherlock"]["forbidden_actions"]
    assert "mutate_subject_state" in by_protocol["sherlock"]["forbidden_actions"]
    assert "adjudicate_appeals" in by_protocol["sherlock"]["forbidden_actions"]

    assert "alter_sherlock_logs" in by_protocol["watson"]["forbidden_actions"]
    assert "enforce_containment" in by_protocol["watson"]["forbidden_actions"]
    assert "adjudicate_disputes" in by_protocol["watson"]["forbidden_actions"]

    assert "adjudicate_own_actions" in by_protocol["moriarty"]["forbidden_actions"]
    assert "mutate_l1_state" in by_protocol["moriarty"]["forbidden_actions"]

    assert "secretly_enforce_containment" in by_protocol["tribunal"]["forbidden_actions"]
    assert "rule_without_evidence" in by_protocol["tribunal"]["forbidden_actions"]

    assert "bypass_evidence" in by_protocol["shadowfax"]["forbidden_actions"]
    assert "override_without_audit" in by_protocol["shadowfax"]["forbidden_actions"]


@pytest.mark.unit
def test_cross_layer_rules_preserve_no_l2_to_l1_bleed(protocol_records: list[dict]) -> None:
    all_cross_layer_rules = [
        rule.lower()
        for record in protocol_records
        for rule in record["layer_boundaries"]["cross_layer_rules"]
    ]
    assert any("l2-to-l1" in rule for rule in all_cross_layer_rules)
    assert any("enforcement" in rule for rule in all_cross_layer_rules)
