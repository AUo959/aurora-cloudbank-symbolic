from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.security.validate_institutional_assurance_event import validate_event

ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = (
    ROOT
    / "docs"
    / "security"
    / "assurance_runs"
    / "gate-001a"
    / "2026-07-27-run-001-recovered-protocol-wiring"
)
EVENT = RUN_ROOT / "AURORA_SECURITY__EVENT__GATE_001A_RECOVERED_PROTOCOL_WIRING__v1.0__2026-07-27.json"
MANIFEST = (
    RUN_ROOT
    / "AURORA_SECURITY__MANIFEST__GATE_001A_RECOVERED_PROTOCOL_WIRING__v1.0__2026-07-27.json"
)
REPORT = RUN_ROOT / "AURORA_SECURITY__REPORT__GATE_001A_RECOVERED_PROTOCOL_WIRING__v1.0__2026-07-27.md"
FINDINGS = (
    RUN_ROOT
    / "AURORA_SECURITY__FINDINGS__GATE_001A_RECOVERED_PROTOCOL_WIRING__v1.0__2026-07-27.json"
)
REPLAY_RECEIPT = (
    RUN_ROOT
    / "AURORA_SECURITY__RECEIPT__GATE_001A_DETERMINISTIC_REPLAY__v1.0__2026-07-27.json"
)


def test_gate_001a_run_001_event_conforms_to_contract() -> None:
    event = json.loads(EVENT.read_text(encoding="utf-8"))
    assert validate_event(event) == []


def test_gate_001a_run_001_preserves_first_class_simulated_provenance() -> None:
    event = json.loads(EVENT.read_text(encoding="utf-8"))
    assert event["layer"] == "L1"
    assert event["execution_mode"] == "l1_simulated_institutional_rehearsal"
    assert event["evidence_authority"] == "operational_simulation_evidence"
    assert event["data_treatment"] == "first_class_operational_data"
    assert event["real_world_interaction"] is False
    assert event["independent_external_assurance"] is False
    assert event["substitutes_for_real_world_review"] is False
    assert all(
        role["representation"] == "simulated_role"
        for role in event["institutional_roles"]
    )


def test_gate_001a_run_001_manifest_digests_resolve() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        assert path.is_file(), entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_gate_001a_run_001_replay_is_set_equivalent() -> None:
    receipt = json.loads(REPLAY_RECEIPT.read_text(encoding="utf-8"))
    assert receipt["baseline_commit"] == "3142aa47afac0b8e63cc5bc46f9fa8ae40592354"
    assert receipt["step2"] == {
        "canonical_exit_code": 1,
        "canonical_match_count": 0,
        "deterministic_match_count": 0,
        "set_equivalent": True,
    }
    assert receipt["step3"] == {
        "canonical_exit_code": 0,
        "canonical_match_count": 38,
        "deterministic_match_count": 38,
        "set_equivalent": True,
    }


def test_gate_001a_run_001_finding_is_actionable_without_overclaiming() -> None:
    register = json.loads(FINDINGS.read_text(encoding="utf-8"))
    finding = register["findings"][0]
    assert register["verdict"] == "FINDING"
    assert finding["severity"] == "HIGH"
    assert finding["tracking_issue"] == 1361
    assert finding["confidence"]["shared_lineage_with_recovered_protocol"] == "UNDETERMINED"
    assert finding["confidence"]["active_autonomous_enforcement"] == "NOT_ESTABLISHED"


def test_gate_001a_run_001_report_keeps_simulated_output_operational() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert "Institutional process capability:** PASS" in text
    assert "Subject verification verdict:** FINDING" in text
    assert "first-class operational data" in text
    assert "not real-world signatures" in text
    assert "does not claim that a real firm" in text
