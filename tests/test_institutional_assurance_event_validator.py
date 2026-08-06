from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "security" / "validate_institutional_assurance_event.py"
SPEC = importlib.util.spec_from_file_location("l1_assurance_validator", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
CHECK = TestCase()

BASE_SHA = "a" * 40


def simulated_event() -> dict:
    return {
        "event_id": "GATE-001A-security-review-rehearsal",
        "run_id": "run-seed-808",
        "revision": 1,
        "previous_event_digest": None,
        "canon_status": "current_canon",
        "layer": "L1",
        "execution_mode": "l1_simulated_institutional_rehearsal",
        "evidence_authority": "operational_simulation_evidence",
        "data_treatment": "first_class_operational_data",
        "gate_track": "GATE-001A",
        "real_world_interaction": False,
        "independent_external_assurance": False,
        "substitutes_for_real_world_review": False,
        "provenance": {
            "scenario_id": "external-security-review-v1",
            "baseline_commit": BASE_SHA,
            "tool": "tools/hour_aboard.py",
            "tool_version": "1.0",
            "executed_at": "2026-07-27T05:00:00Z",
            "operator": "Aurora GitHubOps",
            "deterministic": True,
            "seed": 808,
        },
        "institutional_roles": [
            {
                "role_id": "assessor-lead",
                "label": "External Assessor Lead",
                "representation": "simulated_role",
            }
        ],
        "evidence_references": [
            {
                "origin": "simulation_primary_evidence",
                "reference": "reports/simulation/gate-001a/run-seed-808.json",
            }
        ],
    }


def external_event(evidence_path: str, digest: str) -> dict:
    return {
        "event_id": "GATE-001B-external-review-2027",
        "run_id": "engagement-001",
        "revision": 1,
        "previous_event_digest": None,
        "canon_status": "current_canon",
        "layer": "L1",
        "execution_mode": "real_world_external_engagement",
        "evidence_authority": "independent_external_assurance",
        "data_treatment": "first_class_operational_data",
        "gate_track": "GATE-001B",
        "real_world_interaction": True,
        "independent_external_assurance": True,
        "substitutes_for_real_world_review": False,
        "provenance": {
            "scenario_id": "external-security-review-scope-v2",
            "baseline_commit": BASE_SHA,
            "tool": "external-engagement-record",
            "tool_version": "1.0",
            "executed_at": "2027-01-15T12:00:00Z",
            "operator": "verified-owner",
        },
        "external_verification": {
            "organization": "Verified Security Firm",
            "assessor": "Verified Assessor",
            "scope_reference": "scope-001",
            "authorization_reference": "authorization-001",
            "verified_by": "Aurora Owner",
            "verified_at": "2027-01-15T12:00:00Z",
            "verification_method": "repository_evidence_digest",
        },
        "institutional_roles": [
            {
                "role_id": "external-firm",
                "label": "Verified Security Firm",
                "representation": "verified_external_organization",
            }
        ],
        "evidence_references": [
            {
                "origin": "external_primary_evidence",
                "reference": evidence_path,
                "sha256": digest,
            },
            {
                "origin": "simulation_primary_evidence",
                "reference": "reports/simulation/gate-001a/run-seed-808.json",
            },
        ],
    }


def test_committed_simulated_output_is_valid_first_class_data():
    assert validator.validate_event(simulated_event()) == []


def test_external_engagement_requires_resolved_digest_evidence(tmp_path):
    receipt = tmp_path / "evidence" / "external_receipt.json"
    receipt.parent.mkdir()
    receipt.write_text('{"assessor":"verified"}\n', encoding="utf-8")
    digest = hashlib.sha256(receipt.read_bytes()).hexdigest()
    event = external_event("evidence/external_receipt.json", digest)
    assert validator.validate_event(event, evidence_root=tmp_path) == []


def test_external_engagement_without_evidence_root_fails_closed():
    event = external_event("evidence/external_receipt.json", "b" * 64)
    errors = validator.validate_event(event)
    assert any("requires evidence_root" in error for error in errors)


def test_external_engagement_rejects_missing_or_mismatched_evidence(tmp_path):
    event = external_event("evidence/missing.json", "b" * 64)
    errors = validator.validate_event(event, evidence_root=tmp_path)
    assert any("does not resolve to a file" in error for error in errors)

    receipt = tmp_path / "evidence" / "external_receipt.json"
    receipt.parent.mkdir()
    receipt.write_text("different", encoding="utf-8")
    event = external_event("evidence/external_receipt.json", "b" * 64)
    errors = validator.validate_event(event, evidence_root=tmp_path)
    assert any("sha256 does not match" in error for error in errors)


def test_simulation_cannot_claim_real_world_interaction_or_assurance():
    event = simulated_event()
    event["real_world_interaction"] = True
    event["independent_external_assurance"] = True
    errors = validator.validate_event(event)
    assert any("real_world_interaction" in error for error in errors)
    assert any("independent_external_assurance" in error for error in errors)


def test_simulation_cannot_be_treated_as_secondary_data():
    event = simulated_event()
    event["data_treatment"] = "reference_data"
    errors = validator.validate_event(event)
    assert any("first_class_operational_data" in error for error in errors)


def test_simulated_roles_cannot_be_relabelled_as_verified_external_entities():
    event = simulated_event()
    event["institutional_roles"][0]["representation"] = "verified_external_organization"
    errors = validator.validate_event(event)
    assert any("not allowed" in error for error in errors)


def test_gate_001b_requires_external_primary_evidence(tmp_path):
    event = external_event("evidence/receipt.json", "b" * 64)
    event["evidence_references"] = [
        {
            "origin": "simulation_primary_evidence",
            "reference": "reports/simulation/gate-001a/run-seed-808.json",
        }
    ]
    errors = validator.validate_event(event, evidence_root=tmp_path)
    assert any("external_primary_evidence" in error for error in errors)


def test_non_substitution_flag_must_always_be_false():
    event = simulated_event()
    event["substitutes_for_real_world_review"] = True
    errors = validator.validate_event(event)
    assert any("must be false" in error for error in errors)


def test_simulation_requires_replay_provenance():
    event = simulated_event()
    event["provenance"].pop("seed")
    event["provenance"]["deterministic"] = False
    errors = validator.validate_event(event)
    assert any("deterministic=true" in error for error in errors)
    assert any("provenance.seed" in error for error in errors)


def test_revision_history_prevents_execution_mode_rewrite(tmp_path):
    prior = simulated_event()
    current = external_event("evidence/receipt.json", "b" * 64)
    current["event_id"] = prior["event_id"]
    current["revision"] = 2
    current["previous_event_digest"] = validator.canonical_event_digest(prior)
    errors = validator.validate_event(current, prior_event=prior, evidence_root=tmp_path)
    assert any("immutable revision field changed: execution_mode" in error for error in errors)
    assert any("immutable revision field changed: evidence_authority" in error for error in errors)


def test_same_mode_revision_with_matching_digest_is_valid():
    prior = simulated_event()
    current = simulated_event()
    current["revision"] = 2
    current["run_id"] = "run-seed-808-retest"
    current["previous_event_digest"] = validator.canonical_event_digest(prior)
    current["evidence_references"].append(
        {
            "origin": "reference_evidence",
            "reference": "issues/1350/retest-note",
        }
    )
    assert validator.validate_event(current, prior_event=prior) == []


def test_revision_greater_than_one_requires_prior_event():
    event = simulated_event()
    event["revision"] = 2
    event["previous_event_digest"] = "c" * 64
    errors = validator.validate_event(event)
    assert any("requires --prior-event" in error for error in errors)


def test_cli_json_loader_accepts_files_inside_controlled_root(tmp_path):
    event_path = tmp_path / "events" / "event.json"
    event_path.parent.mkdir()
    event_path.write_text(json.dumps(simulated_event()), encoding="utf-8")

    CHECK.assertEqual(
        validator._load_json(event_path, allowed_root=tmp_path), simulated_event()
    )


def test_cli_json_loader_rejects_escape_from_controlled_root(tmp_path):
    controlled_root = tmp_path / "controlled"
    controlled_root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps(simulated_event()), encoding="utf-8")

    try:
        validator._load_json(outside, allowed_root=controlled_root)
    except ValueError as exc:
        CHECK.assertIn("escapes controlled root", str(exc))
    else:
        raise AssertionError("an out-of-root CLI path must be rejected")
