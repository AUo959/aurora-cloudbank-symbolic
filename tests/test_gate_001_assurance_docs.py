from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDENDUM = (
    ROOT
    / "docs"
    / "security"
    / "AURORA_SECURITY__ADDENDUM__PENTEST_SCOPE_V2_GATE_001_DUAL_TRACK__v1.0__2026-07-27.md"
)
VERIFICATION = ROOT / "docs" / "security" / "recovered_protocol_wiring_verification.md"
PENTEST_SCOPE = ROOT / "docs" / "security" / "pentest_scope_v2.md"


def test_gate_001_addendum_preserves_first_class_simulation_data():
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "Gate-001A" in text
    assert "Gate-001B" in text
    assert "first_class_operational_data" in text
    assert "Simulation provenance must not trigger automatic downranking" in text
    assert "Gate-001B cannot be satisfied by Gate-001A output" in text


def test_gate_001_addendum_forbids_substitution():
    text = ADDENDUM.read_text(encoding="utf-8")
    assert "substitutes_for_real_world_review: false" in text
    assert "simulated finding → independently discovered finding" in text
    assert "A real-world interaction requires a separate evidence event" in text


def test_recovered_protocol_verification_keeps_tracks_separate():
    text = VERIFICATION.read_text(encoding="utf-8")
    assert "Record A — Gate-001A deterministic rehearsal" in text
    assert "Record B — Gate-001B real engagement baseline" in text
    assert "l1_simulated_institutional_rehearsal" in text
    assert "real_world_external_engagement" in text
    assert "Record A may not be relabeled or copied into Record B" in text


def test_existing_external_engagement_scope_remains_present():
    text = PENTEST_SCOPE.read_text(encoding="utf-8")
    assert "External Security Review Scope v2" in text
    assert "Engagement must not begin until all three signatures are on record" in text
