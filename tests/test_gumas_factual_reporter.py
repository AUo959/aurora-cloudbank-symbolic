from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from simulation.runtime.gumas_battle_orchestrator import (
    execute_macrostep,
    initialize_run_context,
)
from simulation.runtime.gumas_factual_reporter import (
    PUBLIC_SUMMARY_PROFILE,
    SIMULATION_TRUTH_PROFILE,
    Phase10Error,
    export_factual_report,
)
from simulation.runtime.gumas_factual_reporter.constants import (
    INPUT_SCHEMA,
    MACROSTEP_PACKET_SCHEMA,
)
from simulation.runtime.gumas_factual_reporter.identity import (
    canonical_json_bytes,
    hash_without_field,
)
from simulation.runtime.gumas_movement_geometry.constants import (
    MACROSTEP_MS,
    P17_AXES_UM,
    Q12,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as state_hash,
    initialize_motion_state,
)

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / (
    "simulation/baselines/gumas/"
    "GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
)


def _baseline():
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def _t0_vessel(index: int, side: str, fleet: str):
    sign = -1 if side == "loyalist" else 1
    return {
        "ship_id": f"{side}-ship-{index:02d}",
        "side_id": side,
        "fleet_id": fleet,
        "baseline_class_id": "synthetic-baseline-class",
        "canonrec_class_id": "synthetic-canonrec-class",
        "organization_id": "synthetic-organization",
        "role": "synthetic-role",
        "formation_slot": index,
        "position_m": [sign * 6_000_000, index * 10_000, 2_000_000],
        "velocity_mm_s": [0, 0, 0],
        "attitude": {
            "frame": "P17_SCENARIO_INERTIAL_XYZ",
            "forward_q12": [-sign * Q12, 0, 0],
            "up_q12": [0, 0, Q12],
        },
        "physical": {
            "max_accel_mm_s2": 50_000,
            "firepower_milliunits": 10_000,
            "shield_capacity_milliunits": 10_000,
            "shield_current_milliunits": 10_000,
            "armor_integrity_milliunits": 10_000,
            "armor_current_milliunits": 10_000,
            "hull_integrity_milliunits": 10_000,
            "hull_current_milliunits": 10_000,
            "effective_weapon_range_m": 1_500_000,
            "sensor_range_m": 3_000_000,
        },
        "capability_q1000": {
            "sensors": 600,
            "mobility": 500,
            "electronic_warfare_q1000": 500,
            "stealth_q1000": 500,
            "carrier_projection_q1000": 250,
        },
        "resources_q1000": {
            "fuel": 1000,
            "energy": 1000,
            "ammunition": 1000,
            "supply": 1000,
        },
        "readiness_q1000": {
            "overall": 1000,
            "sensors": 1000,
            "ew": 1000,
            "propulsion": 1000,
            "weapons": 1000,
            "damage_control": 1000,
        },
        "command": {},
        "morale_q1000": 1000,
        "cohesion_q1000": 1000,
        "damage_state": "undamaged",
        "disposition": "combat_capable",
        "provenance": {"test_fixture": True},
    }


def _synthetic_results(step_count: int = 1):
    baseline = _baseline()
    vessels = []
    for side, data in sorted(baseline["sides"].items()):
        vessels.extend(_t0_vessel(index, side, data["fleet_id"]) for index in range(19))
    t0 = {
        "schema": "aurora://simulation/gumas/deterministic_t0_physical_state/v1.0",
        "run_identity": {"test_fixture": True},
        "planetoid": {
            "semi_axes_m": {
                "a": P17_AXES_UM[0] // 1_000_000,
                "b": P17_AXES_UM[1] // 1_000_000,
                "c": P17_AXES_UM[2] // 1_000_000,
            },
            "integration_step_ms": MACROSTEP_MS,
        },
        "vessels": sorted(vessels, key=lambda item: item["ship_id"]),
    }
    t0["t0_sha256"] = state_hash(t0, "t0_sha256")
    state = initialize_motion_state(t0)
    context = initialize_run_context(t0, state, baseline)
    prior_checkpoint = None
    results = []
    for _ in range(step_count):
        result = execute_macrostep(state, baseline, context, prior_checkpoint)
        results.append(result)
        state = result["committed_state"]
        prior_checkpoint = result["checkpoint"]
    return context, results


def _report_input(step_count: int = 1):
    context, results = _synthetic_results(step_count)
    macrosteps = []
    for result in results:
        macrosteps.append(
            {
                "schema": MACROSTEP_PACKET_SCHEMA,
                "ledger_entry": copy.deepcopy(result["ledger_entry"]),
                "observation_receipts_by_side": copy.deepcopy(
                    result["observation_receipts_by_side"]
                ),
                "decisions_by_fleet": copy.deepcopy(result["decisions_by_fleet"]),
                "movement_receipt": copy.deepcopy(result["movement_receipt"]),
                "phase6_receipt": copy.deepcopy(result["phase6_receipt"]),
                "phase7_receipt": copy.deepcopy(result["phase7_receipt"]),
                "phase8_resolution_state": copy.deepcopy(
                    result["phase8_resolution_state"]
                ),
                "phase8_receipt": copy.deepcopy(result["phase8_receipt"]),
            }
        )
    return {
        "schema": INPUT_SCHEMA,
        "expected_run_identity_sha256": context["run_identity_sha256"],
        "expected_ledger_head_sha256": results[-1]["ledger_entry"][
            "ledger_entry_sha256"
        ],
        "run_context": copy.deepcopy(context),
        "macrosteps": macrosteps,
    }


def _reverse_mappings(value):
    if isinstance(value, dict):
        return {
            key: _reverse_mappings(item)
            for key, item in reversed(list(value.items()))
        }
    if isinstance(value, list):
        return [_reverse_mappings(item) for item in value]
    return value


def _events_by_type(report, fact_type):
    return [event for event in report["events"] if event["fact_type"] == fact_type]


def test_truth_report_replay_mapping_order_and_evidence_are_exact():
    packet = _report_input()
    first = export_factual_report(packet)
    replay = export_factual_report(copy.deepcopy(packet))
    reordered = export_factual_report(_reverse_mappings(packet))
    assert first == replay == reordered

    report = first["normalized_report"]
    assert report["profile_id"] == SIMULATION_TRUTH_PROFILE
    assert report["macrostep_count"] == 1
    assert report["run0_executed"] is False
    assert len(_events_by_type(report, "command_observation")) == 2
    assert len(_events_by_type(report, "command_order")) == 2
    assert len(_events_by_type(report, "movement_vessel")) == 38

    observations = {
        event["subject_id"]: event for event in _events_by_type(report, "command_observation")
    }
    for command in _events_by_type(report, "command_order"):
        assert (
            command["fields"]["observation_sha256"]
            == observations[command["subject_id"]]["fields"]["observation_sha256"]
        )

    index = first["evidence_index"]
    assert set(index["event_to_evidence_ref_ids"]) == {
        event["event_id"] for event in report["events"]
    }
    assert all(index["event_to_evidence_ref_ids"].values())
    assert all(index["rendered_statement_to_event_ids"].values())
    rendered = first["rendered_report"]
    assert rendered["text"].endswith("\n")
    assert not rendered["text"].endswith("\n\n")
    assert "TERMINAL terminated=false mode=ongoing" in rendered["text"]
    receipt = first["export_receipt"]
    assert receipt["transition_execution_imported"] is False
    assert receipt["transition_execution_called"] is False
    assert receipt["report_feedback_applied"] is False
    assert receipt["llm_used"] is False


def test_public_profile_is_a_deterministic_redaction_of_truth():
    packet = _report_input()
    truth = export_factual_report(packet)
    public = export_factual_report(packet, profile_id=PUBLIC_SUMMARY_PROFILE)
    replay = export_factual_report(
        copy.deepcopy(packet),
        profile_id=PUBLIC_SUMMARY_PROFILE,
    )
    assert public == replay
    public_report = public["normalized_report"]
    assert public_report["profile_id"] == PUBLIC_SUMMARY_PROFILE
    assert {event["fact_type"] for event in public_report["events"]} == {
        "macrostep_boundary",
        "movement_aggregate",
        "sensing_fire_aggregate",
        "damage_aggregate",
        "side_resolution",
        "terminal_outcome",
    }
    public_bytes = canonical_json_bytes(public)
    assert b"start_position_um" not in public_bytes
    assert b"command_observation" not in public_bytes
    assert b"loyalist-ship-" not in public_bytes
    assert "COMMAND " not in public["rendered_report"]["text"]
    assert (
        public["export_receipt"]["truth_normalized_report_sha256"]
        == truth["normalized_report"]["normalized_report_sha256"]
    )
    assert (
        public["normalized_report"]["normalized_report_sha256"]
        != truth["normalized_report"]["normalized_report_sha256"]
    )


def test_mutated_or_extra_input_fails_closed():
    packet = _report_input()
    mutated = copy.deepcopy(packet)
    mutated["macrosteps"][0]["phase7_receipt"]["effect_count"] += 1
    with pytest.raises(Phase10Error, match="phase7_receipt hash mismatch"):
        export_factual_report(mutated)

    extra = copy.deepcopy(packet)
    extra["macrosteps"][0]["committed_state"] = {"hidden": True}
    with pytest.raises(Phase10Error, match="fields differ"):
        export_factual_report(extra)

    wrong_anchor = copy.deepcopy(packet)
    wrong_anchor["expected_ledger_head_sha256"] = "0" * 64
    with pytest.raises(Phase10Error, match="ledger head"):
        export_factual_report(wrong_anchor)


def test_ledger_reordering_gap_duplicate_fork_and_truncation_fail_closed():
    packet = _report_input(step_count=2)
    assert export_factual_report(packet)["normalized_report"]["macrostep_count"] == 2

    reordered = copy.deepcopy(packet)
    reordered["macrosteps"].reverse()
    with pytest.raises(Phase10Error, match="macrostep|ledger|observation"):
        export_factual_report(reordered)

    truncated = copy.deepcopy(packet)
    truncated["macrosteps"] = truncated["macrosteps"][:1]
    with pytest.raises(Phase10Error, match="ledger head"):
        export_factual_report(truncated)

    duplicate = copy.deepcopy(packet)
    duplicate["macrosteps"][1] = copy.deepcopy(duplicate["macrosteps"][0])
    with pytest.raises(Phase10Error, match="macrostep|observation"):
        export_factual_report(duplicate)

    forked = copy.deepcopy(packet)
    second_ledger = forked["macrosteps"][1]["ledger_entry"]
    second_ledger["previous_ledger_entry_sha256"] = "0" * 64
    second_ledger["ledger_entry_sha256"] = hash_without_field(
        second_ledger,
        "ledger_entry_sha256",
    )
    forked["expected_ledger_head_sha256"] = second_ledger["ledger_entry_sha256"]
    with pytest.raises(Phase10Error, match="previous-entry"):
        export_factual_report(forked)

    gap = copy.deepcopy(packet)
    gap["macrosteps"] = gap["macrosteps"][1:]
    with pytest.raises(Phase10Error, match="macrostep|GENESIS|observation"):
        export_factual_report(gap)


def test_consistent_factual_fixture_mutation_is_projection_local():
    packet = _report_input()
    original = export_factual_report(packet)["normalized_report"]

    changed = copy.deepcopy(packet)
    step = changed["macrosteps"][0]
    movement = step["movement_receipt"]
    movement["per_vessel"][0]["collision"] = {
        "body_id": "TEST-ONLY-COLLISION",
        "substep_index": 0,
    }
    movement["movement_receipt_sha256"] = hash_without_field(
        movement,
        "movement_receipt_sha256",
    )
    ledger = step["ledger_entry"]
    ledger["phase5_receipt_sha256"] = movement["movement_receipt_sha256"]
    ledger["ledger_entry_sha256"] = hash_without_field(
        ledger,
        "ledger_entry_sha256",
    )
    changed["expected_ledger_head_sha256"] = ledger["ledger_entry_sha256"]
    projected = export_factual_report(changed)["normalized_report"]

    original_fields = {event["event_id"]: event["fields"] for event in original["events"]}
    changed_fields = {event["event_id"]: event["fields"] for event in projected["events"]}
    changed_types = {
        event["fact_type"]
        for event in projected["events"]
        if original_fields[event["event_id"]] != changed_fields[event["event_id"]]
    }
    assert changed_types == {
        "macrostep_boundary",
        "movement_vessel",
        "movement_aggregate",
    }


def test_terminal_outcome_is_copied_without_redecision():
    packet = _report_input()
    changed = copy.deepcopy(packet)
    step = changed["macrosteps"][0]
    terminal = copy.deepcopy(step["phase8_resolution_state"]["terminal_outcome"])
    terminal.update(
        {
            "terminated": True,
            "termination_mode": "test_only_terminal",
            "reason_code": "test_only_terminal",
        }
    )
    resolution = step["phase8_resolution_state"]
    resolution["terminal_outcome"] = terminal
    resolution["resolution_state_sha256"] = hash_without_field(
        resolution,
        "resolution_state_sha256",
    )
    phase8 = step["phase8_receipt"]
    phase8["terminal_outcome"] = copy.deepcopy(terminal)
    phase8["resolution_state_sha256"] = resolution["resolution_state_sha256"]
    phase8["phase8_receipt_sha256"] = hash_without_field(
        phase8,
        "phase8_receipt_sha256",
    )
    ledger = step["ledger_entry"]
    ledger["terminal_outcome"] = copy.deepcopy(terminal)
    ledger["phase8_resolution_state_sha256"] = resolution[
        "resolution_state_sha256"
    ]
    ledger["phase8_receipt_sha256"] = phase8["phase8_receipt_sha256"]
    ledger["ledger_entry_sha256"] = hash_without_field(
        ledger,
        "ledger_entry_sha256",
    )
    changed["expected_ledger_head_sha256"] = ledger["ledger_entry_sha256"]

    output = export_factual_report(changed)
    terminal_event = _events_by_type(
        output["normalized_report"],
        "terminal_outcome",
    )[0]
    assert terminal_event["fields"] == terminal
    assert "mode=test_only_terminal" in output["rendered_report"]["text"]


def test_float_and_unknown_profile_are_rejected():
    packet = _report_input()
    floating = copy.deepcopy(packet)
    floating["macrosteps"][0]["ledger_entry"]["start_elapsed_ms"] = 0.0
    with pytest.raises(Phase10Error, match="floating-point"):
        export_factual_report(floating)
    with pytest.raises(Phase10Error, match="unsupported Phase-10 profile"):
        export_factual_report(packet, profile_id="narrative_freeform")
