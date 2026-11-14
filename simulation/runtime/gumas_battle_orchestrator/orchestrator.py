"""Authoritative deterministic Phase-9 GUMAS macrostep orchestrator."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from simulation.runtime.gumas_command_policy.policy import (
    _source_identity as command_source_identity,
    decide,
)
from simulation.runtime.gumas_damage_disposition import step_phase7_state
from simulation.runtime.gumas_damage_disposition import kernel as phase7_kernel
from simulation.runtime.gumas_damage_disposition.normalization import (
    normalizer_source_identity,
)
from simulation.runtime.gumas_morale_resolution import (
    boundary_source_identity,
    step_phase8_state,
)
from simulation.runtime.gumas_morale_resolution import kernel as phase8_kernel
from simulation.runtime.gumas_movement_geometry.geometry import (
    mean_vector_round_half_even,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    _source_identity as movement_source_identity,
    _verify_motion_state,
    _verify_t0_snapshot,
    order_from_command_receipt,
    step_motion_state,
)
from simulation.runtime.gumas_sensing_weapons import step_phase6_state
from simulation.runtime.gumas_sensing_weapons import kernel as phase6_kernel

from .constants import (
    CANONICAL_JSON_PROFILE,
    GENESIS_MARKER,
    LEDGER_ENTRY_SCHEMA,
    PHASE9_CONTRACT_ID,
    PHASE9_VERSION,
    RUN_CONTEXT_SCHEMA,
)
from .identity import (
    Phase9Error,
    hash_without_field,
    mean_round,
    require_int,
    sha256_canonical,
    source_identity,
)
from .live_observation import derive_live_observations


def _phase7_identity() -> dict[str, Any]:
    core = phase7_kernel._source_identity()
    normalizer = normalizer_source_identity()
    composite = sha256_canonical(
        {
            "damage_core_source_identity": core,
            "semantic_normalizer_source_identity": normalizer,
        }
    )
    return {
        "damage_core_source_identity": core,
        "semantic_normalizer_source_identity": normalizer,
        "composite_source_sha256": composite,
    }


def _phase8_identity() -> dict[str, Any]:
    core = phase8_kernel._source_identity()
    boundary = boundary_source_identity()
    composite = sha256_canonical(
        {
            "resolution_core_source_identity": core,
            "phase8_boundary_source_identity": boundary,
        }
    )
    return {
        "resolution_core_source_identity": core,
        "phase8_boundary_source_identity": boundary,
        "composite_source_sha256": composite,
    }


def accepted_source_identities() -> dict[str, Any]:
    return {
        "phase4_command_policy": command_source_identity(),
        "phase5_movement_geometry": movement_source_identity(),
        "phase6_sensing_weapons": phase6_kernel._source_identity(),
        "phase7_damage_disposition": _phase7_identity(),
        "phase8_morale_resolution": _phase8_identity(),
        "phase9_orchestrator": source_identity(),
    }


def _roster_records(vessels: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    records = []
    seen: set[str] = set()
    for vessel in vessels:
        ship_id = str(vessel.get("ship_id") or "")
        if not ship_id or ship_id in seen:
            raise Phase9Error(f"invalid or duplicate roster vessel: {ship_id}")
        seen.add(ship_id)
        record = {
            key: str(vessel.get(key) or "")
            for key in (
                "ship_id",
                "side_id",
                "fleet_id",
                "baseline_class_id",
                "canonrec_class_id",
                "organization_id",
            )
        }
        if any(not value for value in record.values()):
            raise Phase9Error(f"incomplete frozen roster record: {ship_id}")
        records.append(record)
    return sorted(records, key=lambda item: item["ship_id"])


def initialize_run_context(
    t0_snapshot: Mapping[str, Any],
    initial_state: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    """Freeze the non-canon run, roster, seed, and accepted source identities."""
    _verify_t0_snapshot(t0_snapshot)
    _verify_motion_state(initial_state)
    if int(initial_state.get("macrostep_index", -1)) != 0 or int(initial_state.get("elapsed_ms", -1)) != 0:
        raise Phase9Error("Phase-9 run context requires an unadvanced T0 state")
    if str(initial_state.get("source_t0_sha256") or "") != str(t0_snapshot.get("t0_sha256") or ""):
        raise Phase9Error("initial movement state does not bind supplied T0")
    t0_records = _roster_records(t0_snapshot.get("vessels") or [])
    state_records = _roster_records(initial_state.get("vessels") or [])
    if state_records != t0_records:
        raise Phase9Error("initial movement roster differs from T0 roster")
    baseline_sides = baseline.get("sides")
    if not isinstance(baseline_sides, Mapping) or len(baseline_sides) != 2:
        raise Phase9Error("Phase-9 baseline requires exactly two sides")
    side_to_fleet = {
        str(side_id): str(side.get("fleet_id") or "")
        for side_id, side in sorted(baseline_sides.items())
        if isinstance(side, Mapping)
    }
    if set(side_to_fleet) != set(str(side) for side in baseline_sides):
        raise Phase9Error("invalid baseline side mapping")
    if set(record["side_id"] for record in t0_records) != set(side_to_fleet):
        raise Phase9Error("T0 roster side set differs from frozen baseline")
    for record in t0_records:
        if side_to_fleet[record["side_id"]] != record["fleet_id"]:
            raise Phase9Error("T0 roster fleet mapping differs from frozen baseline")
    seed = require_int(
        (baseline.get("determinism") or {}).get("seed_u64"),
        "baseline seed_u64",
        minimum=0,
    )
    if seed >= 2**64:
        raise Phase9Error("baseline seed_u64 exceeds unsigned 64-bit range")
    baseline_id = str(baseline.get("baseline_id") or "")
    baseline_version = str(baseline.get("version") or "")
    if not baseline_id or not baseline_version:
        raise Phase9Error("baseline identity missing")
    context: dict[str, Any] = {
        "schema": RUN_CONTEXT_SCHEMA,
        "phase9_contract_id": PHASE9_CONTRACT_ID,
        "phase9_version": PHASE9_VERSION,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "historical_canon_status": "non_canon_simulation_instance",
        "baseline_id": baseline_id,
        "baseline_version": baseline_version,
        "baseline_sha256": sha256_canonical(baseline),
        "source_t0_sha256": str(t0_snapshot["t0_sha256"]),
        "roster_records": t0_records,
        "t0_roster_sha256": sha256_canonical(t0_records),
        "seed_u64": seed,
        "accepted_source_identities": accepted_source_identities(),
    }
    context["run_identity_sha256"] = hash_without_field(context, "run_identity_sha256")
    return context


def _validate_run_context(run_context: Mapping[str, Any], baseline: Mapping[str, Any]) -> None:
    if run_context.get("schema") != RUN_CONTEXT_SCHEMA:
        raise Phase9Error("unsupported Phase-9 run-context schema")
    recorded = str(run_context.get("run_identity_sha256") or "")
    if not recorded or recorded != hash_without_field(run_context, "run_identity_sha256"):
        raise Phase9Error("run-context hash mismatch")
    if str(run_context.get("baseline_sha256") or "") != sha256_canonical(baseline):
        raise Phase9Error("run-context baseline hash mismatch")
    if run_context.get("accepted_source_identities") != accepted_source_identities():
        raise Phase9Error("accepted phase source identity drift")
    seed = require_int(run_context.get("seed_u64"), "run-context seed", minimum=0)
    if seed != require_int(
        (baseline.get("determinism") or {}).get("seed_u64"),
        "baseline seed",
        minimum=0,
    ):
        raise Phase9Error("run-context seed mismatch")


def _validate_state_and_roster(state: Mapping[str, Any], run_context: Mapping[str, Any]) -> None:
    _verify_motion_state(state)
    vessels = state.get("vessels")
    if not isinstance(vessels, Sequence) or isinstance(vessels, (str, bytes)):
        raise Phase9Error("state.vessels must be a sequence")
    if _roster_records(vessels) != run_context.get("roster_records"):
        raise Phase9Error("current state violates frozen T0 roster")
    if str(state.get("source_t0_sha256") or "") != str(run_context.get("source_t0_sha256") or ""):
        raise Phase9Error("current state T0 identity mismatch")
    require_int(state.get("macrostep_index"), "state macrostep index", minimum=0)
    require_int(state.get("elapsed_ms"), "state elapsed", minimum=0)


def _verify_receipt_hash(receipt: Mapping[str, Any], field: str, label: str) -> str:
    recorded = str(receipt.get(field) or "")
    if not recorded or recorded != hash_without_field(receipt, field):
        raise Phase9Error(f"{label} hash mismatch")
    return recorded


def _validate_prior_checkpoint(
    state: Mapping[str, Any],
    run_context: Mapping[str, Any],
    prior_checkpoint: Mapping[str, Any] | None,
    baseline: Mapping[str, Any],
) -> None:
    macrostep = int(state["macrostep_index"])
    if prior_checkpoint is None:
        if macrostep != 0:
            raise Phase9Error("non-genesis state requires a complete prior checkpoint")
        return

    required = {
        "phase6_receipt",
        "phase7_receipt",
        "phase8_resolution_state",
        "phase8_receipt",
        "live_observation_receipts_by_side",
        "ledger_entry",
    }
    if set(prior_checkpoint) != required:
        raise Phase9Error("prior checkpoint is partial or contains unknown fields")
    phase6 = prior_checkpoint["phase6_receipt"]
    phase7 = prior_checkpoint["phase7_receipt"]
    resolution = prior_checkpoint["phase8_resolution_state"]
    phase8 = prior_checkpoint["phase8_receipt"]
    ledger = prior_checkpoint["ledger_entry"]
    observations = prior_checkpoint["live_observation_receipts_by_side"]
    if not all(isinstance(value, Mapping) for value in (phase6, phase7, resolution, phase8, ledger, observations)):
        raise Phase9Error("prior checkpoint artifacts must be mappings")

    phase6_sha = _verify_receipt_hash(phase6, "phase6_receipt_sha256", "prior Phase-6 receipt")
    phase7_sha = _verify_receipt_hash(phase7, "phase7_receipt_sha256", "prior Phase-7 receipt")
    resolution_sha = _verify_receipt_hash(resolution, "resolution_state_sha256", "prior Phase-8 resolution")
    phase8_sha = _verify_receipt_hash(phase8, "phase8_receipt_sha256", "prior Phase-8 receipt")
    ledger_sha = _verify_receipt_hash(ledger, "ledger_entry_sha256", "prior Phase-9 ledger")

    if str(phase7.get("prior_state_sha256") or "") != str(phase6.get("next_state_sha256") or ""):
        raise Phase9Error("prior Phase-6 to Phase-7 state chain mismatch")
    if str(phase8.get("prior_state_sha256") or "") != str(phase7.get("next_state_sha256") or ""):
        raise Phase9Error("prior Phase-7 to Phase-8 state chain mismatch")
    if str(phase8.get("next_state_sha256") or "") != str(state["state_sha256"]):
        raise Phase9Error("prior Phase-8 receipt does not bind current state")
    if str(phase8.get("resolution_state_sha256") or "") != resolution_sha:
        raise Phase9Error("prior Phase-8 receipt/resolution mismatch")
    if str(state.get("last_phase6_receipt_sha256") or "") != phase6_sha:
        raise Phase9Error("current state does not retain prior Phase-6 receipt")
    if str(state.get("last_phase8_resolution_state_sha256") or "") != resolution_sha:
        raise Phase9Error("current state does not retain prior Phase-8 resolution")
    if dict(state.get("phase7_source_identity") or {}) != phase7_kernel._source_identity():
        raise Phase9Error("current state Phase-7 source identity drift")
    if str(state.get("phase7_composite_source_sha256") or "") != _phase7_identity()["composite_source_sha256"]:
        raise Phase9Error("current state Phase-7 composite identity drift")
    if str(state.get("phase8_composite_source_sha256") or "") != _phase8_identity()["composite_source_sha256"]:
        raise Phase9Error("current state Phase-8 composite identity drift")
    if phase6.get("phase6_source_identity") != phase6_kernel._source_identity():
        raise Phase9Error("prior Phase-6 source identity drift")
    if str(phase7.get("phase7_composite_source_sha256") or "") != _phase7_identity()["composite_source_sha256"]:
        raise Phase9Error("prior Phase-7 source identity drift")
    if str(phase8.get("phase8_composite_source_sha256") or "") != _phase8_identity()["composite_source_sha256"]:
        raise Phase9Error("prior Phase-8 source identity drift")

    terminal = resolution.get("terminal_outcome")
    if not isinstance(terminal, Mapping):
        raise Phase9Error("prior Phase-8 terminal outcome missing")
    if terminal.get("terminated") is True:
        raise Phase9Error("terminal checkpoint cannot execute another macrostep")
    if terminal.get("terminated") is not False:
        raise Phase9Error("prior Phase-8 terminal flag must be boolean")
    if int(resolution.get("macrostep_index", -1)) != macrostep:
        raise Phase9Error("prior Phase-8 resolution macrostep mismatch")

    sides = set(str(side) for side in (baseline.get("sides") or {}))
    if set(observations) != sides:
        raise Phase9Error("prior live-observation side set mismatch")
    for side_id, receipt in observations.items():
        if not isinstance(receipt, Mapping):
            raise Phase9Error(f"invalid live-observation receipt: {side_id}")
        _verify_receipt_hash(
            receipt,
            "live_observation_receipt_sha256",
            f"prior live observation {side_id}",
        )
        if int(receipt.get("decision_epoch", -1)) != macrostep - 1:
            raise Phase9Error(f"prior live-observation epoch mismatch: {side_id}")

    if str(ledger.get("run_identity_sha256") or "") != str(run_context["run_identity_sha256"]):
        raise Phase9Error("prior ledger run identity mismatch")
    if str(ledger.get("t0_roster_sha256") or "") != str(run_context["t0_roster_sha256"]):
        raise Phase9Error("prior ledger roster identity mismatch")
    if ledger.get("accepted_source_identities") != accepted_source_identities():
        raise Phase9Error("prior ledger source identity drift")
    if int(ledger.get("macrostep_index", -1)) != macrostep:
        raise Phase9Error("prior ledger macrostep mismatch")
    if str(ledger.get("phase6_receipt_sha256") or "") != phase6_sha:
        raise Phase9Error("prior ledger Phase-6 receipt mismatch")
    if str(ledger.get("phase7_receipt_sha256") or "") != phase7_sha:
        raise Phase9Error("prior ledger Phase-7 receipt mismatch")
    if str(ledger.get("phase8_resolution_state_sha256") or "") != resolution_sha:
        raise Phase9Error("prior ledger Phase-8 resolution mismatch")
    if str(ledger.get("phase8_receipt_sha256") or "") != phase8_sha:
        raise Phase9Error("prior ledger Phase-8 receipt mismatch")
    if str(ledger.get("phase8_next_state_sha256") or "") != str(state["state_sha256"]):
        raise Phase9Error("prior ledger does not bind current committed state")
    ledger_observations = ledger.get("live_observation_receipt_sha256_by_side")
    expected_observations = {
        str(side): str(receipt["live_observation_receipt_sha256"]) for side, receipt in sorted(observations.items())
    }
    if ledger_observations != expected_observations:
        raise Phase9Error("prior ledger live-observation receipt mismatch")
    if phase8.get("terminal_outcome") != resolution.get("terminal_outcome"):
        raise Phase9Error("prior Phase-8 terminal-outcome mismatch")
    if str(ledger.get("ledger_entry_sha256") or "") != ledger_sha:
        raise Phase9Error("prior ledger hash instability")


def _motion_references(
    state: Mapping[str, Any],
    decisions_by_side: Mapping[str, Mapping[str, Any]],
    observation_receipts_by_side: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    vessels = {str(v["ship_id"]): v for v in state["vessels"]}
    references: dict[str, dict[str, Any]] = {}
    for side_id, decision in sorted(decisions_by_side.items()):
        navigation = str(((decision.get("orders") or {}).get("specialist_intents") or {}).get("navigation") or "")
        if navigation != "EVASIVE_VECTOR":
            continue
        receipt = observation_receipts_by_side[side_id]
        contacts = receipt.get("selected_contact_evidence") or []
        if not contacts:
            raise Phase9Error(f"EVASIVE_VECTOR lacks a side-local contact reference: {side_id}")
        target_positions = []
        qualities = []
        for contact in contacts:
            target_id = str(contact.get("target_ship_id") or "")
            if target_id not in vessels:
                raise Phase9Error("motion reference target absent from state")
            target_positions.append(vessels[target_id]["position_um"])
            qualities.append(int(contact["contact_quality_q1000"]))
        fleet_id = str(decision["fleet_id"])
        references[fleet_id] = {
            "reference_kind": "phase9_side_local_contact_centroid",
            "position_um": list(mean_vector_round_half_even(target_positions)),
            "source_state_sha256": str(state["state_sha256"]),
            "source_receipt_sha256": str(receipt["source_phase6_receipt_sha256"]),
            "confidence_q1000": mean_round(qualities),
        }
    return references


def _ledger_entry(
    *,
    prior_ledger: Mapping[str, Any] | None,
    run_context: Mapping[str, Any],
    prior_state: Mapping[str, Any],
    observation_receipts: Mapping[str, Mapping[str, Any]],
    decisions_by_fleet: Mapping[str, Mapping[str, Any]],
    movement_state: Mapping[str, Any],
    movement_receipt: Mapping[str, Any],
    phase6_state: Mapping[str, Any],
    phase6_receipt: Mapping[str, Any],
    phase7_state: Mapping[str, Any],
    phase7_receipt: Mapping[str, Any],
    phase8_state: Mapping[str, Any],
    resolution_state: Mapping[str, Any],
    phase8_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "schema": LEDGER_ENTRY_SCHEMA,
        "phase9_contract_id": PHASE9_CONTRACT_ID,
        "phase9_version": PHASE9_VERSION,
        "phase9_source_identity": source_identity(),
        "historical_canon_status": "non_canon_simulation_instance",
        "run_identity_sha256": str(run_context["run_identity_sha256"]),
        "t0_roster_sha256": str(run_context["t0_roster_sha256"]),
        "macrostep_index": int(movement_state["macrostep_index"]),
        "start_elapsed_ms": int(prior_state["elapsed_ms"]),
        "end_elapsed_ms": int(phase8_state["elapsed_ms"]),
        "previous_ledger_entry_sha256": (
            str(prior_ledger["ledger_entry_sha256"]) if prior_ledger is not None else GENESIS_MARKER
        ),
        "previous_committed_state_sha256": str(prior_state["state_sha256"]),
        "live_observation_sha256_by_side": {
            side: str(receipt["observation_sha256"]) for side, receipt in sorted(observation_receipts.items())
        },
        "live_observation_receipt_sha256_by_side": {
            side: str(receipt["live_observation_receipt_sha256"])
            for side, receipt in sorted(observation_receipts.items())
        },
        "phase4_decision_sha256_by_fleet": {
            fleet: str(receipt["decision_sha256"]) for fleet, receipt in sorted(decisions_by_fleet.items())
        },
        "phase5_state_sha256": str(movement_state["state_sha256"]),
        "phase5_receipt_sha256": str(movement_receipt["movement_receipt_sha256"]),
        "phase6_state_sha256": str(phase6_state["state_sha256"]),
        "phase6_receipt_sha256": str(phase6_receipt["phase6_receipt_sha256"]),
        "phase7_state_sha256": str(phase7_state["state_sha256"]),
        "phase7_receipt_sha256": str(phase7_receipt["phase7_receipt_sha256"]),
        "phase8_next_state_sha256": str(phase8_state["state_sha256"]),
        "phase8_resolution_state_sha256": str(resolution_state["resolution_state_sha256"]),
        "phase8_receipt_sha256": str(phase8_receipt["phase8_receipt_sha256"]),
        "terminal_outcome": dict(resolution_state["terminal_outcome"]),
        "accepted_source_identities": accepted_source_identities(),
        "reporter_invoked": False,
        "run0_executed": False,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
    }
    entry["ledger_entry_sha256"] = hash_without_field(entry, "ledger_entry_sha256")
    return entry


def execute_macrostep(
    state: Mapping[str, Any],
    baseline: Mapping[str, Any],
    run_context: Mapping[str, Any],
    prior_checkpoint: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute and ledger exactly one authoritative Phase-4 through Phase-8 step."""
    _validate_run_context(run_context, baseline)
    _validate_state_and_roster(state, run_context)
    _validate_prior_checkpoint(state, run_context, prior_checkpoint, baseline)

    prior = prior_checkpoint or {}
    observations, observation_receipts = derive_live_observations(
        state,
        baseline,
        run_context,
        previous_phase6_receipt=prior.get("phase6_receipt"),
        previous_phase7_receipt=prior.get("phase7_receipt"),
        previous_resolution_state=prior.get("phase8_resolution_state"),
        previous_phase8_receipt=prior.get("phase8_receipt"),
        previous_observation_receipts_by_side=prior.get("live_observation_receipts_by_side"),
    )
    baseline_identity = {
        "baseline_id": str(baseline["baseline_id"]),
        "baseline_version": str(baseline["version"]),
    }
    decisions_by_side: dict[str, dict[str, Any]] = {}
    decisions_by_fleet: dict[str, dict[str, Any]] = {}
    orders_by_fleet: dict[str, dict[str, Any]] = {}
    for side_id, side in sorted((baseline.get("sides") or {}).items()):
        fleet_id = str(side["fleet_id"])
        decision = decide(
            side["command_team"],
            observations[str(side_id)],
            side_id=str(side_id),
            fleet_id=fleet_id,
            decision_epoch=int(state["macrostep_index"]),
            baseline_identity=baseline_identity,
        )
        decisions_by_side[str(side_id)] = decision
        decisions_by_fleet[fleet_id] = decision
        orders_by_fleet[fleet_id] = order_from_command_receipt(decision)

    references = _motion_references(state, decisions_by_side, observation_receipts)
    movement_state, movement_receipt = step_motion_state(state, orders_by_fleet, references)
    phase6_state, phase6_receipt = step_phase6_state(
        movement_state,
        decisions_by_fleet,
        int(run_context["seed_u64"]),
    )
    phase7_state, phase7_receipt = step_phase7_state(phase6_state, phase6_receipt)
    phase8_state, resolution_state, phase8_receipt = step_phase8_state(
        phase7_state,
        phase7_receipt,
        decisions_by_fleet,
        baseline,
        prior.get("phase8_resolution_state"),
    )

    if str(movement_receipt.get("prior_state_sha256") or "") != str(state["state_sha256"]):
        raise Phase9Error("Phase-5 parent hash mismatch")
    if str(phase6_receipt.get("prior_state_sha256") or "") != str(movement_state["state_sha256"]):
        raise Phase9Error("Phase-6 parent hash mismatch")
    if str(phase7_receipt.get("prior_state_sha256") or "") != str(phase6_state["state_sha256"]):
        raise Phase9Error("Phase-7 parent hash mismatch")
    if str(phase8_receipt.get("prior_state_sha256") or "") != str(phase7_state["state_sha256"]):
        raise Phase9Error("Phase-8 parent hash mismatch")

    prior_ledger = prior.get("ledger_entry")
    ledger = _ledger_entry(
        prior_ledger=prior_ledger,
        run_context=run_context,
        prior_state=state,
        observation_receipts=observation_receipts,
        decisions_by_fleet=decisions_by_fleet,
        movement_state=movement_state,
        movement_receipt=movement_receipt,
        phase6_state=phase6_state,
        phase6_receipt=phase6_receipt,
        phase7_state=phase7_state,
        phase7_receipt=phase7_receipt,
        phase8_state=phase8_state,
        resolution_state=resolution_state,
        phase8_receipt=phase8_receipt,
    )
    checkpoint = {
        "phase6_receipt": phase6_receipt,
        "phase7_receipt": phase7_receipt,
        "phase8_resolution_state": resolution_state,
        "phase8_receipt": phase8_receipt,
        "live_observation_receipts_by_side": observation_receipts,
        "ledger_entry": ledger,
    }
    return {
        "schema": "aurora://simulation/gumas/phase9_macrostep_result/v1.0",
        "run_identity_sha256": str(run_context["run_identity_sha256"]),
        "observations_by_side": observations,
        "observation_receipts_by_side": observation_receipts,
        "decisions_by_side": decisions_by_side,
        "decisions_by_fleet": decisions_by_fleet,
        "motion_references_by_fleet": references,
        "movement_state": movement_state,
        "movement_receipt": movement_receipt,
        "phase6_state": phase6_state,
        "phase6_receipt": phase6_receipt,
        "phase7_state": phase7_state,
        "phase7_receipt": phase7_receipt,
        "committed_state": phase8_state,
        "phase8_resolution_state": resolution_state,
        "phase8_receipt": phase8_receipt,
        "ledger_entry": ledger,
        "checkpoint": checkpoint,
        "can_continue": not bool(resolution_state["terminal_outcome"]["terminated"]),
        "reporter_invoked": False,
        "run0_executed": False,
    }
