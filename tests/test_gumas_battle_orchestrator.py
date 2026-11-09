from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from simulation.runtime.gumas_battle_orchestrator import (
    Phase9Error,
    derive_live_observations,
    execute_macrostep,
    initialize_run_context,
)
from simulation.runtime.gumas_battle_orchestrator.identity import hash_without_field
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
    "simulation/baselines/gumas/" "GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
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


def _synthetic_run():
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
    return baseline, t0, state, context


def _rehash_state(state):
    state["state_sha256"] = state_hash(state, "state_sha256")


def test_genesis_live_observation_replay_and_mapping_order_are_exact():
    baseline, _, state, context = _synthetic_run()
    first = execute_macrostep(state, baseline, context)
    replay = execute_macrostep(copy.deepcopy(state), copy.deepcopy(baseline), context)
    reversed_baseline = copy.deepcopy(baseline)
    reversed_baseline["sides"] = dict(reversed(list(reversed_baseline["sides"].items())))
    reordered = execute_macrostep(copy.deepcopy(state), reversed_baseline, context)

    assert first == replay == reordered
    assert first["ledger_entry"]["previous_ledger_entry_sha256"] == "GENESIS"
    assert first["ledger_entry"]["run0_executed"] is False
    assert first["reporter_invoked"] is False
    assert first["can_continue"] is True
    for side, observation in first["observations_by_side"].items():
        assert observation["contact_quality"] == 0
        assert observation["uncertainty"] == 1000
        assert observation["negotiation_signal"] == 0
        assert len(observation) == 16
        assert all(type(value) is int and 0 <= value <= 1000 for value in observation.values())
        receipt = first["observation_receipts_by_side"][side]
        assert receipt["enemy_raw_material_state_used"] is False
        assert receipt["source_phase6_receipt_sha256"] == "GENESIS"


def test_unseen_enemy_material_does_not_leak_but_own_state_is_causal():
    baseline, _, state, context = _synthetic_run()
    original, _ = derive_live_observations(state, baseline, context)

    enemy_mutation = copy.deepcopy(state)
    rebel = next(v for v in enemy_mutation["vessels"] if v["side_id"] == "rebel")
    rebel["physical"]["hull_current_milliunits"] = 1
    rebel["readiness_q1000"]["weapons"] = 1
    rebel["resources_q1000"]["ammunition"] = 1
    _rehash_state(enemy_mutation)
    mutated, _ = derive_live_observations(enemy_mutation, baseline, context)
    assert mutated["loyalist"] == original["loyalist"]
    assert mutated["rebel"]["own_damage"] > original["rebel"]["own_damage"]

    own_mutation = copy.deepcopy(state)
    loyal = next(v for v in own_mutation["vessels"] if v["side_id"] == "loyalist")
    loyal["resources_q1000"]["fuel"] = 0
    loyal["resources_q1000"]["ammunition"] = 0
    _rehash_state(own_mutation)
    changed, _ = derive_live_observations(own_mutation, baseline, context)
    assert changed["loyalist"]["logistics_strain"] > original["loyalist"]["logistics_strain"]
    assert changed["loyalist"]["withdrawal_viability"] <= original["loyalist"]["withdrawal_viability"]


def test_continuation_consumes_prior_resolution_and_hash_chains_ledger():
    baseline, _, state, context = _synthetic_run()
    first = execute_macrostep(state, baseline, context)
    second = execute_macrostep(first["committed_state"], baseline, context, first["checkpoint"])
    replay = execute_macrostep(
        copy.deepcopy(first["committed_state"]),
        copy.deepcopy(baseline),
        context,
        copy.deepcopy(first["checkpoint"]),
    )
    assert second == replay
    assert second["ledger_entry"]["previous_ledger_entry_sha256"] == first["ledger_entry"]["ledger_entry_sha256"]
    assert second["ledger_entry"]["macrostep_index"] == 2
    for side, receipt in second["observation_receipts_by_side"].items():
        assert receipt["decision_epoch"] == 1
        assert (
            receipt["source_phase8_resolution_state_sha256"]
            == first["phase8_resolution_state"]["resolution_state_sha256"]
        )
        assert (
            receipt["prior_live_observation_receipt_sha256"]
            == first["observation_receipts_by_side"][side]["live_observation_receipt_sha256"]
        )


def test_contact_damage_memory_and_closing_pressure_are_side_local():
    baseline, _, state, context = _synthetic_run()
    first = execute_macrostep(state, baseline, context)
    committed = first["committed_state"]
    loyal_id = next(v["ship_id"] for v in committed["vessels"] if v["side_id"] == "loyalist")
    rebel_id = next(v["ship_id"] for v in committed["vessels"] if v["side_id"] == "rebel")

    def contact(distance):
        value = {
            "observer_ship_id": loyal_id,
            "target_ship_id": rebel_id,
            "distance_um": distance,
            "contact_quality_q1000": 800,
            "identity_quality_q1000": 700,
            "classification": "hostile_confirmed",
        }
        value["contact_sha256"] = hash_without_field(value, "contact_sha256")
        return value

    effect_id = "attributable-effect"
    phase6 = {
        "contacts": [contact(1_100_000_000_000)],
        "effect_descriptors": [
            {
                "effect_id": effect_id,
                "source_ship_id": loyal_id,
                "target_ship_id": rebel_id,
            }
        ],
    }
    phase6["phase6_receipt_sha256"] = hash_without_field(phase6, "phase6_receipt_sha256")
    phase7 = {
        "target_damage_receipts": [
            {
                "target_ship_id": rebel_id,
                "effect_ids": [effect_id],
                "hull": {"new_hull_loss_q1000": 200},
            }
        ]
    }
    phase7["phase7_receipt_sha256"] = hash_without_field(phase7, "phase7_receipt_sha256")
    observed, receipts = derive_live_observations(
        committed,
        baseline,
        context,
        previous_phase6_receipt=phase6,
        previous_phase7_receipt=phase7,
        previous_resolution_state=first["phase8_resolution_state"],
        previous_phase8_receipt=first["phase8_receipt"],
        previous_observation_receipts_by_side=first["observation_receipts_by_side"],
    )
    assert observed["loyalist"]["contact_quality"] > 0
    assert observed["loyalist"]["enemy_damage_estimate"] > 0
    assert observed["rebel"]["contact_quality"] == 0
    assert receipts["loyalist"]["enemy_damage_estimate_q1000_by_target"][rebel_id] == 200

    phase6_next = {
        "contacts": [contact(900_000_000_000)],
        "effect_descriptors": [],
    }
    phase6_next["phase6_receipt_sha256"] = hash_without_field(phase6_next, "phase6_receipt_sha256")
    phase7_next = {"target_damage_receipts": []}
    phase7_next["phase7_receipt_sha256"] = hash_without_field(phase7_next, "phase7_receipt_sha256")
    observed_next, receipts_next = derive_live_observations(
        committed,
        baseline,
        context,
        previous_phase6_receipt=phase6_next,
        previous_phase7_receipt=phase7_next,
        previous_resolution_state=first["phase8_resolution_state"],
        previous_phase8_receipt=first["phase8_receipt"],
        previous_observation_receipts_by_side=receipts,
    )
    assert observed_next["loyalist"]["enemy_closing_pressure"] > 0
    assert receipts_next["loyalist"]["enemy_damage_estimate_q1000_by_target"][rebel_id] == 200


def test_roster_ledger_and_source_identity_mutations_fail_closed():
    baseline, _, state, context = _synthetic_run()
    roster_mutation = copy.deepcopy(state)
    roster_mutation["vessels"][0]["side_id"] = "third-party"
    _rehash_state(roster_mutation)
    with pytest.raises(Phase9Error, match="roster"):
        execute_macrostep(roster_mutation, baseline, context)

    first = execute_macrostep(state, baseline, context)
    bad_checkpoint = copy.deepcopy(first["checkpoint"])
    bad_checkpoint["ledger_entry"]["previous_committed_state_sha256"] = "0" * 64
    with pytest.raises(Phase9Error, match="ledger"):
        execute_macrostep(first["committed_state"], baseline, context, bad_checkpoint)

    bad_context = copy.deepcopy(context)
    bad_context["accepted_source_identities"]["phase9_orchestrator"]["bundle_sha256"] = "0" * 64
    bad_context["run_identity_sha256"] = hash_without_field(bad_context, "run_identity_sha256")
    with pytest.raises(Phase9Error, match="source identity drift"):
        execute_macrostep(state, baseline, bad_context)


def test_terminal_checkpoint_refuses_another_macrostep_before_command():
    baseline, _, state, context = _synthetic_run()
    first = execute_macrostep(state, baseline, context)
    committed = copy.deepcopy(first["committed_state"])
    checkpoint = copy.deepcopy(first["checkpoint"])

    resolution = checkpoint["phase8_resolution_state"]
    resolution["terminal_outcome"]["terminated"] = True
    resolution["terminal_outcome"]["termination_mode"] = "test_terminal"
    resolution["resolution_state_sha256"] = hash_without_field(resolution, "resolution_state_sha256")
    committed["last_phase8_resolution_state_sha256"] = resolution["resolution_state_sha256"]
    _rehash_state(committed)

    phase8 = checkpoint["phase8_receipt"]
    phase8["resolution_state_sha256"] = resolution["resolution_state_sha256"]
    phase8["next_state_sha256"] = committed["state_sha256"]
    phase8["terminal_outcome"] = copy.deepcopy(resolution["terminal_outcome"])
    phase8["phase8_receipt_sha256"] = hash_without_field(phase8, "phase8_receipt_sha256")

    ledger = checkpoint["ledger_entry"]
    ledger["phase8_next_state_sha256"] = committed["state_sha256"]
    ledger["phase8_resolution_state_sha256"] = resolution["resolution_state_sha256"]
    ledger["phase8_receipt_sha256"] = phase8["phase8_receipt_sha256"]
    ledger["terminal_outcome"] = copy.deepcopy(resolution["terminal_outcome"])
    ledger["ledger_entry_sha256"] = hash_without_field(ledger, "ledger_entry_sha256")

    with pytest.raises(Phase9Error, match="terminal checkpoint"):
        execute_macrostep(committed, baseline, context, checkpoint)
