import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDENDUM = (
    ROOT
    / "docs"
    / "security"
    / "AURORA_SECURITY__ADDENDUM__PENTEST_SCOPE_V2_GATE_001_DUAL_TRACK__v1.0__2026-07-27.md"
)
ARCHITECTURE_ADDENDUM = (
    ROOT
    / "docs"
    / "architecture"
    / "AURORA_ARCHITECTURE__ADDENDUM__L1_INSTITUTIONAL_MODELING__v1.0__2026-07-27.md"
)
VERIFICATION = ROOT / "docs" / "security" / "recovered_protocol_wiring_verification.md"
PENTEST_SCOPE = ROOT / "docs" / "security" / "pentest_scope_v2.md"
CONTRACT = (
    ROOT
    / "docs"
    / "security"
    / "contracts"
    / "AURORA_L1__CONTRACT__INSTITUTIONAL_ASSURANCE_EVENT__v1.0__2026-07-27.json"
)
VALIDATOR = ROOT / "tools" / "security" / "validate_institutional_assurance_event.py"


def test_gate_001_addendum_preserves_first_class_simulation_data():
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "Gate-001A" in text
    assert "Gate-001B" in text
    assert "first_class_operational_data" in text
    assert "Simulation provenance must not trigger automatic downranking" in text
    assert "Gate-001B cannot be satisfied by Gate-001A output" in text
    assert "Gate-001A records must be deterministic" in text


def test_gate_001_addendum_forbids_substitution_and_mode_rewrite():
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "substitutes_for_real_world_review: false" in text
    assert "simulated finding → independently discovered finding" in text
    assert "A real-world interaction requires a separate evidence event" in text
    assert "immutable across revisions of the same event ID" in text
    assert "prior-event digest" in text


def test_gate_001b_requires_structured_digest_resolved_evidence():
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "external_verification:" in text
    assert "verification_method: repository_evidence_digest" in text
    assert "controlled evidence root" in text
    assert "SHA-256 digest" in text
    assert "metadata alone" in text


def test_l1_institutional_modeling_does_not_create_physical_simulated_entities():
    text = ARCHITECTURE_ADDENDUM.read_text(encoding="utf-8")
    assert "L1 institutional modeling" in text
    assert "simulated_role" in text
    assert "not physical L1 entities" in text
    assert "L2 scenario-world simulation" in text
    assert "Simulated roles never enter the L1 staff registry" in text


def test_local_contract_and_validator_are_vendored_and_parseable():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["schema"] == "aurora.l1.institutional_assurance_event_contract/v1"
    assert "immutable_revision_fields" in contract
    assert contract["mode_rules"]["real_world_external_engagement"][
        "evidence_resolution_required"
    ] is True
    assert VALIDATOR.is_file()


def test_recovered_protocol_verification_keeps_tracks_separate():
    text = VERIFICATION.read_text(encoding="utf-8")
    assert "Record A — Gate-001A deterministic rehearsal" in text
    assert "Record B — Gate-001B real engagement baseline" in text
    assert "l1_simulated_institutional_rehearsal" in text
    assert "real_world_external_engagement" in text
    assert "Record A may not be relabeled or copied into Record B" in text
    assert "Execution mode and assurance authority are immutable" in text


def test_recovered_protocol_gate_001a_requires_complete_replay_package():
    text = VERIFICATION.read_text(encoding="utf-8")
    assert "Required replay and evidence package" in text
    assert "Ordered event and decision trace" in text
    assert "Severity method and rationale" in text
    assert "Remediation state" in text
    assert "Retest state" in text
    assert "If any item is unchecked, the verdict must be **BLOCKED**" in text


def test_recovered_protocol_gate_001b_requires_verified_receipts():
    text = VERIFICATION.read_text(encoding="utf-8")
    assert "Structured external verification" in text
    assert "repository_evidence_digest" in text
    assert "External primary evidence receipts" in text
    assert "matches the recorded lowercase SHA-256 digest" in text
    assert "metadata alone is insufficient" in text


def test_existing_external_engagement_scope_remains_present():
    text = PENTEST_SCOPE.read_text(encoding="utf-8")
    assert "External Security Review Scope v2" in text
    assert "Engagement must not begin until all three signatures are on record" in text
