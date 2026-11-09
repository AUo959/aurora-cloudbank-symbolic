"""Fail-closed validation for accepted Phase-9 reporting artifacts."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from .constants import (
    CANONICAL_JSON_PROFILE,
    COMMAND_RECEIPT_SCHEMA,
    GENESIS_MARKER,
    HISTORICAL_CANON_STATUS,
    INPUT_SCHEMA,
    MACROSTEP_PACKET_SCHEMA,
    MOVEMENT_RECEIPT_SCHEMA,
    PHASE6_RECEIPT_SCHEMA,
    PHASE7_RECEIPT_SCHEMA,
    PHASE8_RECEIPT_SCHEMA,
    PHASE8_RESOLUTION_SCHEMA,
    PHASE9_CONTRACT_ID,
    PHASE9_LEDGER_ENTRY_SCHEMA,
    PHASE9_OBSERVATION_RECEIPT_SCHEMA,
    PHASE9_RUN_CONTEXT_SCHEMA,
    PHASE9_VERSION,
)
from .identity import (
    Phase10Error,
    canonical_json_bytes,
    hash_without_field,
    require_int,
    require_sha256,
    sha256_canonical,
)


INPUT_FIELDS = frozenset(
    {
        "schema",
        "expected_run_identity_sha256",
        "expected_ledger_head_sha256",
        "run_context",
        "macrosteps",
    }
)
MACROSTEP_FIELDS = frozenset(
    {
        "schema",
        "ledger_entry",
        "observation_receipts_by_side",
        "decisions_by_fleet",
        "movement_receipt",
        "phase6_receipt",
        "phase7_receipt",
        "phase8_resolution_state",
        "phase8_receipt",
    }
)
RUN_CONTEXT_FIELDS = frozenset(
    {
        "schema",
        "phase9_contract_id",
        "phase9_version",
        "canonical_json_profile",
        "historical_canon_status",
        "baseline_id",
        "baseline_version",
        "baseline_sha256",
        "source_t0_sha256",
        "roster_records",
        "t0_roster_sha256",
        "seed_u64",
        "accepted_source_identities",
        "run_identity_sha256",
    }
)
ROSTER_FIELDS = frozenset(
    {
        "ship_id",
        "side_id",
        "fleet_id",
        "baseline_class_id",
        "canonrec_class_id",
        "organization_id",
    }
)
SOURCE_PHASES = frozenset(
    {
        "phase4_command_policy",
        "phase5_movement_geometry",
        "phase6_sensing_weapons",
        "phase7_damage_disposition",
        "phase8_morale_resolution",
        "phase9_orchestrator",
    }
)


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise Phase10Error(f"{label} must be a mapping")
    return value


def _sequence(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise Phase10Error(f"{label} must be a sequence")
    return value


def _exact_keys(value: Mapping[str, Any], expected: frozenset[str], label: str) -> None:
    actual = set(value)
    if actual != set(expected):
        missing = sorted(set(expected) - actual)
        extra = sorted(actual - set(expected))
        raise Phase10Error(f"{label} fields differ; missing={missing}, extra={extra}")


def _verify_hash(value: Mapping[str, Any], field: str, label: str) -> str:
    recorded = require_sha256(value.get(field), f"{label}.{field}")
    actual = hash_without_field(value, field)
    if recorded != actual:
        raise Phase10Error(f"{label} hash mismatch")
    return recorded


def _require_false(value: Mapping[str, Any], field: str, label: str) -> None:
    if value.get(field) is not False:
        raise Phase10Error(f"{label}.{field} must be false")


def _normalized_phase6_receipt_sha256(receipt: Mapping[str, Any]) -> str:
    normalized = copy.deepcopy(dict(receipt))
    normalized.pop("phase6_receipt_sha256", None)
    for field in ("contacts", "selections", "weapon_attempts", "effect_descriptors"):
        value = normalized.get(field)
        if isinstance(value, list):
            normalized[field] = sorted(value, key=canonical_json_bytes)
    return sha256_canonical(normalized)


def _validate_run_context(
    raw: Any,
    expected_run_identity_sha256: str,
) -> tuple[dict[str, Any], dict[str, str], set[str], set[str]]:
    context = _mapping(raw, "run_context")
    _exact_keys(context, RUN_CONTEXT_FIELDS, "run_context")
    if context.get("schema") != PHASE9_RUN_CONTEXT_SCHEMA:
        raise Phase10Error("unsupported Phase-9 run-context schema")
    if context.get("phase9_contract_id") != PHASE9_CONTRACT_ID:
        raise Phase10Error("unsupported Phase-9 contract")
    if context.get("phase9_version") != PHASE9_VERSION:
        raise Phase10Error("unsupported Phase-9 version")
    if context.get("canonical_json_profile") != CANONICAL_JSON_PROFILE:
        raise Phase10Error("unsupported run-context canonical JSON profile")
    if context.get("historical_canon_status") != HISTORICAL_CANON_STATUS:
        raise Phase10Error("run-context historical canon status mismatch")
    recorded = _verify_hash(context, "run_identity_sha256", "run_context")
    if recorded != expected_run_identity_sha256:
        raise Phase10Error("run-context identity differs from accepted trust anchor")
    require_sha256(context.get("baseline_sha256"), "run_context.baseline_sha256")
    require_sha256(context.get("source_t0_sha256"), "run_context.source_t0_sha256")
    require_sha256(context.get("t0_roster_sha256"), "run_context.t0_roster_sha256")
    require_int(context.get("seed_u64"), "run_context.seed_u64", minimum=0)
    if not str(context.get("baseline_id") or "") or not str(context.get("baseline_version") or ""):
        raise Phase10Error("run-context baseline identity missing")

    source_identities = _mapping(
        context.get("accepted_source_identities"),
        "run_context.accepted_source_identities",
    )
    if set(source_identities) != set(SOURCE_PHASES):
        raise Phase10Error("accepted source-identity phase set mismatch")

    roster = _sequence(context.get("roster_records"), "run_context.roster_records")
    normalized_roster: list[dict[str, str]] = []
    ship_ids: set[str] = set()
    side_to_fleet: dict[str, str] = {}
    for index, raw_record in enumerate(roster):
        record = _mapping(raw_record, f"run_context.roster_records[{index}]")
        _exact_keys(record, ROSTER_FIELDS, f"run_context.roster_records[{index}]")
        normalized = {field: str(record.get(field) or "") for field in sorted(ROSTER_FIELDS)}
        if any(not value for value in normalized.values()):
            raise Phase10Error(f"incomplete roster record at index {index}")
        ship_id = normalized["ship_id"]
        if ship_id in ship_ids:
            raise Phase10Error(f"duplicate roster ship: {ship_id}")
        ship_ids.add(ship_id)
        side_id = normalized["side_id"]
        fleet_id = normalized["fleet_id"]
        previous_fleet = side_to_fleet.setdefault(side_id, fleet_id)
        if previous_fleet != fleet_id:
            raise Phase10Error(f"side maps to multiple fleets: {side_id}")
        normalized_roster.append(normalized)
    normalized_roster.sort(key=lambda item: item["ship_id"])
    if list(roster) != normalized_roster:
        raise Phase10Error("run-context roster records are not normalized and sorted")
    if len(side_to_fleet) != 2 or any(not side for side in side_to_fleet):
        raise Phase10Error("Phase-10 reporting requires exactly two non-empty sides")
    if len(set(side_to_fleet.values())) != 2:
        raise Phase10Error("Phase-10 reporting requires distinct frozen fleets")
    if str(context["t0_roster_sha256"]) != sha256_canonical(normalized_roster):
        raise Phase10Error("run-context T0 roster hash mismatch")
    return (
        copy.deepcopy(dict(context)),
        dict(sorted(side_to_fleet.items())),
        ship_ids,
        set(side_to_fleet.values()),
    )


def _validate_observations(
    raw: Any,
    *,
    context: Mapping[str, Any],
    side_to_fleet: Mapping[str, str],
    macrostep_index: int,
    previous_packet: Mapping[str, Any] | None,
    previous_committed_state_sha256: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, str], dict[str, str]]:
    observations = _mapping(raw, "observation_receipts_by_side")
    if set(observations) != set(side_to_fleet):
        raise Phase10Error("live-observation side set mismatch")
    normalized: dict[str, dict[str, Any]] = {}
    observation_hashes: dict[str, str] = {}
    receipt_hashes: dict[str, str] = {}
    previous = previous_packet or {}
    for side_id in sorted(side_to_fleet):
        receipt = _mapping(observations[side_id], f"observation[{side_id}]")
        if receipt.get("schema") != PHASE9_OBSERVATION_RECEIPT_SCHEMA:
            raise Phase10Error(f"unsupported live-observation schema: {side_id}")
        if receipt.get("phase9_contract_id") != PHASE9_CONTRACT_ID or receipt.get("phase9_version") != PHASE9_VERSION:
            raise Phase10Error(f"live-observation Phase-9 identity mismatch: {side_id}")
        if receipt.get("phase9_source_identity") != context["accepted_source_identities"]["phase9_orchestrator"]:
            raise Phase10Error(f"live-observation source identity mismatch: {side_id}")
        if receipt.get("canonical_json_profile") != CANONICAL_JSON_PROFILE:
            raise Phase10Error(f"live-observation canonical profile mismatch: {side_id}")
        if str(receipt.get("run_identity_sha256") or "") != str(context["run_identity_sha256"]):
            raise Phase10Error(f"live-observation run identity mismatch: {side_id}")
        if str(receipt.get("t0_roster_sha256") or "") != str(context["t0_roster_sha256"]):
            raise Phase10Error(f"live-observation roster identity mismatch: {side_id}")
        if str(receipt.get("side_id") or "") != side_id:
            raise Phase10Error(f"live-observation side key mismatch: {side_id}")
        if str(receipt.get("fleet_id") or "") != side_to_fleet[side_id]:
            raise Phase10Error(f"live-observation fleet mismatch: {side_id}")
        if require_int(receipt.get("decision_epoch"), f"observation[{side_id}].decision_epoch", minimum=0) != macrostep_index - 1:
            raise Phase10Error(f"live-observation decision epoch mismatch: {side_id}")
        if str(receipt.get("source_committed_state_sha256") or "") != previous_committed_state_sha256:
            raise Phase10Error(f"live-observation committed-state mismatch: {side_id}")
        observation = _mapping(receipt.get("observation"), f"observation[{side_id}].observation")
        observation_sha = require_sha256(
            receipt.get("observation_sha256"),
            f"observation[{side_id}].observation_sha256",
        )
        if observation_sha != sha256_canonical(observation):
            raise Phase10Error(f"live-observation payload hash mismatch: {side_id}")
        receipt_sha = _verify_hash(
            receipt,
            "live_observation_receipt_sha256",
            f"observation[{side_id}]",
        )
        for field in (
            "enemy_raw_material_state_used",
            "prose_inputs_used",
            "ambient_rng_used",
            "floating_authority_used",
        ):
            _require_false(receipt, field, f"observation[{side_id}]")

        if previous_packet is None:
            expected_prior = {
                "source_phase6_receipt_sha256": GENESIS_MARKER,
                "source_phase7_receipt_sha256": GENESIS_MARKER,
                "source_phase8_resolution_state_sha256": GENESIS_MARKER,
                "source_phase8_receipt_sha256": GENESIS_MARKER,
                "prior_live_observation_receipt_sha256": GENESIS_MARKER,
            }
        else:
            previous_observation = _mapping(
                _mapping(previous["observation_receipts_by_side"], "previous observations")[side_id],
                f"previous observation[{side_id}]",
            )
            expected_prior = {
                "source_phase6_receipt_sha256": str(previous["phase6_receipt"]["phase6_receipt_sha256"]),
                "source_phase7_receipt_sha256": str(previous["phase7_receipt"]["phase7_receipt_sha256"]),
                "source_phase8_resolution_state_sha256": str(
                    previous["phase8_resolution_state"]["resolution_state_sha256"]
                ),
                "source_phase8_receipt_sha256": str(previous["phase8_receipt"]["phase8_receipt_sha256"]),
                "prior_live_observation_receipt_sha256": str(
                    previous_observation["live_observation_receipt_sha256"]
                ),
            }
        for field, expected in expected_prior.items():
            if str(receipt.get(field) or "") != expected:
                raise Phase10Error(f"live-observation prior chain mismatch: {side_id}.{field}")
        normalized[side_id] = copy.deepcopy(dict(receipt))
        observation_hashes[side_id] = observation_sha
        receipt_hashes[side_id] = receipt_sha
    return normalized, observation_hashes, receipt_hashes


def _validate_decisions(
    raw: Any,
    *,
    side_to_fleet: Mapping[str, str],
    macrostep_index: int,
) -> tuple[dict[str, dict[str, Any]], dict[str, str], dict[str, str]]:
    decisions = _mapping(raw, "decisions_by_fleet")
    fleets = set(side_to_fleet.values())
    if set(decisions) != fleets:
        raise Phase10Error("command-decision fleet set mismatch")
    side_by_fleet = {fleet: side for side, fleet in side_to_fleet.items()}
    normalized: dict[str, dict[str, Any]] = {}
    by_fleet: dict[str, str] = {}
    by_side: dict[str, str] = {}
    for fleet_id in sorted(fleets):
        receipt = _mapping(decisions[fleet_id], f"decision[{fleet_id}]")
        if receipt.get("schema") != COMMAND_RECEIPT_SCHEMA:
            raise Phase10Error(f"unsupported command receipt schema: {fleet_id}")
        if str(receipt.get("fleet_id") or "") != fleet_id:
            raise Phase10Error(f"command fleet key mismatch: {fleet_id}")
        side_id = side_by_fleet[fleet_id]
        if str(receipt.get("side_id") or "") != side_id:
            raise Phase10Error(f"command side mismatch: {fleet_id}")
        if require_int(receipt.get("decision_epoch"), f"decision[{fleet_id}].decision_epoch", minimum=0) != macrostep_index - 1:
            raise Phase10Error(f"command decision epoch mismatch: {fleet_id}")
        observation = _mapping(receipt.get("observation"), f"decision[{fleet_id}].observation")
        if str(receipt.get("observation_sha256") or "") != sha256_canonical(observation):
            raise Phase10Error(f"command observation hash mismatch: {fleet_id}")
        _mapping(receipt.get("orders"), f"decision[{fleet_id}].orders")
        _require_false(receipt, "prose_inputs_used", f"decision[{fleet_id}]")
        _require_false(receipt, "rng_used", f"decision[{fleet_id}]")
        decision_sha = _verify_hash(receipt, "decision_sha256", f"decision[{fleet_id}]")
        normalized[fleet_id] = copy.deepcopy(dict(receipt))
        by_fleet[fleet_id] = decision_sha
        by_side[side_id] = decision_sha
    return normalized, by_fleet, by_side


def _validate_phase_receipts(
    packet: Mapping[str, Any],
    *,
    context: Mapping[str, Any],
    macrostep_index: int,
    ship_ids: set[str],
    side_to_fleet: Mapping[str, str],
    decision_hashes_by_fleet: Mapping[str, str],
    decision_hashes_by_side: Mapping[str, str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    movement = _mapping(packet.get("movement_receipt"), "movement_receipt")
    phase6 = _mapping(packet.get("phase6_receipt"), "phase6_receipt")
    phase7 = _mapping(packet.get("phase7_receipt"), "phase7_receipt")
    resolution = _mapping(packet.get("phase8_resolution_state"), "phase8_resolution_state")
    phase8 = _mapping(packet.get("phase8_receipt"), "phase8_receipt")

    if movement.get("schema") != MOVEMENT_RECEIPT_SCHEMA:
        raise Phase10Error("unsupported movement receipt schema")
    _verify_hash(movement, "movement_receipt_sha256", "movement_receipt")
    if movement.get("movement_source_identity") != context["accepted_source_identities"]["phase5_movement_geometry"]:
        raise Phase10Error("movement source identity mismatch")
    if movement.get("canonical_json_profile") != CANONICAL_JSON_PROFILE:
        raise Phase10Error("movement canonical profile mismatch")
    _require_false(movement, "rng_used", "movement_receipt")
    _require_false(movement, "floating_authority_used", "movement_receipt")
    if movement.get("command_decision_sha256_by_fleet") != dict(sorted(decision_hashes_by_fleet.items())):
        raise Phase10Error("movement command-decision map mismatch")
    movement_vessels = _sequence(movement.get("per_vessel"), "movement_receipt.per_vessel")
    movement_ship_ids = [str(_mapping(item, "movement vessel").get("ship_id") or "") for item in movement_vessels]
    if len(movement_ship_ids) != len(set(movement_ship_ids)) or set(movement_ship_ids) != ship_ids:
        raise Phase10Error("movement receipt vessel roster mismatch")

    if phase6.get("schema") != PHASE6_RECEIPT_SCHEMA:
        raise Phase10Error("unsupported Phase-6 receipt schema")
    _verify_hash(phase6, "phase6_receipt_sha256", "phase6_receipt")
    if phase6.get("phase6_source_identity") != context["accepted_source_identities"]["phase6_sensing_weapons"]:
        raise Phase10Error("Phase-6 source identity mismatch")
    _require_false(phase6, "ambient_rng_used", "phase6_receipt")
    _require_false(phase6, "floating_authority_used", "phase6_receipt")
    _require_false(phase6, "damage_applied", "phase6_receipt")
    if phase6.get("command_decision_sha256_by_fleet") != dict(sorted(decision_hashes_by_fleet.items())):
        raise Phase10Error("Phase-6 command-decision map mismatch")
    for field in ("contacts", "selections", "weapon_attempts", "effect_descriptors"):
        _sequence(phase6.get(field), f"phase6_receipt.{field}")

    if phase7.get("schema") != PHASE7_RECEIPT_SCHEMA:
        raise Phase10Error("unsupported Phase-7 receipt schema")
    _verify_hash(phase7, "phase7_receipt_sha256", "phase7_receipt")
    phase7_identity = _mapping(
        context["accepted_source_identities"]["phase7_damage_disposition"],
        "accepted Phase-7 source identity",
    )
    if phase7.get("phase7_source_identity") != phase7_identity.get("damage_core_source_identity"):
        raise Phase10Error("Phase-7 damage-core identity mismatch")
    if phase7.get("phase7_semantic_normalizer_source_identity") != phase7_identity.get(
        "semantic_normalizer_source_identity"
    ):
        raise Phase10Error("Phase-7 semantic-normalizer identity mismatch")
    if str(phase7.get("phase7_composite_source_sha256") or "") != str(
        phase7_identity.get("composite_source_sha256") or ""
    ):
        raise Phase10Error("Phase-7 composite identity mismatch")
    for field in (
        "morale_mutated",
        "cohesion_mutated",
        "termination_decision_made",
        "ambient_rng_used",
        "floating_authority_used",
    ):
        _require_false(phase7, field, "phase7_receipt")
    target_receipts = _sequence(
        phase7.get("target_damage_receipts"),
        "phase7_receipt.target_damage_receipts",
    )
    target_ids: set[str] = set()
    for index, raw_target in enumerate(target_receipts):
        target = _mapping(raw_target, f"target_damage_receipts[{index}]")
        target_sha = _verify_hash(
            target,
            "target_damage_receipt_sha256",
            f"target_damage_receipts[{index}]",
        )
        require_sha256(target_sha, f"target_damage_receipts[{index}].hash")
        target_id = str(target.get("target_ship_id") or "")
        if target_id not in ship_ids or target_id in target_ids:
            raise Phase10Error(f"invalid or duplicate Phase-7 target: {target_id}")
        target_ids.add(target_id)
    if require_int(phase7.get("affected_target_count"), "phase7.affected_target_count", minimum=0) != len(target_receipts):
        raise Phase10Error("Phase-7 affected-target count mismatch")
    if require_int(phase7.get("effect_count"), "phase7.effect_count", minimum=0) != len(
        _sequence(phase6.get("effect_descriptors"), "phase6.effect_descriptors")
    ):
        raise Phase10Error("Phase-7 effect count mismatch")

    if resolution.get("schema") != PHASE8_RESOLUTION_SCHEMA:
        raise Phase10Error("unsupported Phase-8 resolution schema")
    resolution_sha = _verify_hash(
        resolution,
        "resolution_state_sha256",
        "phase8_resolution_state",
    )
    phase8_identity = _mapping(
        context["accepted_source_identities"]["phase8_morale_resolution"],
        "accepted Phase-8 source identity",
    )
    if resolution.get("phase8_source_identity") != phase8_identity.get("resolution_core_source_identity"):
        raise Phase10Error("Phase-8 resolution-core identity mismatch")
    if resolution.get("phase8_boundary_source_identity") != phase8_identity.get("phase8_boundary_source_identity"):
        raise Phase10Error("Phase-8 boundary identity mismatch")
    if str(resolution.get("phase8_composite_source_sha256") or "") != str(
        phase8_identity.get("composite_source_sha256") or ""
    ):
        raise Phase10Error("Phase-8 composite identity mismatch")
    for field in (
        "shock_by_side",
        "dissent_by_side",
        "side_aggregate",
        "withdrawal_by_side",
        "surrender_by_side",
        "engagement_status_by_side",
    ):
        value = _mapping(resolution.get(field), f"phase8_resolution_state.{field}")
        if set(value) != set(side_to_fleet):
            raise Phase10Error(f"Phase-8 side-map mismatch: {field}")
    if resolution.get("command_decision_sha256_by_side") != dict(sorted(decision_hashes_by_side.items())):
        raise Phase10Error("Phase-8 command-decision map mismatch")
    terminal = _mapping(resolution.get("terminal_outcome"), "phase8_resolution_state.terminal_outcome")
    if type(terminal.get("terminated")) is not bool or not str(terminal.get("termination_mode") or ""):
        raise Phase10Error("Phase-8 terminal outcome is incomplete")

    if phase8.get("schema") != PHASE8_RECEIPT_SCHEMA:
        raise Phase10Error("unsupported Phase-8 receipt schema")
    _verify_hash(phase8, "phase8_receipt_sha256", "phase8_receipt")
    if phase8.get("phase8_source_identity") != phase8_identity.get("resolution_core_source_identity"):
        raise Phase10Error("Phase-8 receipt core identity mismatch")
    if phase8.get("phase8_boundary_source_identity") != phase8_identity.get("phase8_boundary_source_identity"):
        raise Phase10Error("Phase-8 receipt boundary identity mismatch")
    if str(phase8.get("phase8_composite_source_sha256") or "") != str(
        phase8_identity.get("composite_source_sha256") or ""
    ):
        raise Phase10Error("Phase-8 receipt composite identity mismatch")
    for field in (
        "physical_state_mutated",
        "ambient_rng_used",
        "floating_authority_used",
        "prose_inputs_used",
    ):
        _require_false(phase8, field, "phase8_receipt")
    if phase8.get("terminal_outcome") != terminal:
        raise Phase10Error("Phase-8 receipt terminal outcome mismatch")
    if str(phase8.get("resolution_state_sha256") or "") != resolution_sha:
        raise Phase10Error("Phase-8 receipt resolution hash mismatch")

    return (
        copy.deepcopy(dict(movement)),
        copy.deepcopy(dict(phase6)),
        copy.deepcopy(dict(phase7)),
        copy.deepcopy(dict(resolution)),
        copy.deepcopy(dict(phase8)),
    )


def _validate_ledger_and_cross_links(
    ledger: Mapping[str, Any],
    *,
    context: Mapping[str, Any],
    macrostep_index: int,
    previous_ledger: Mapping[str, Any] | None,
    expected_ledger_head_sha256: str,
    final: bool,
    observation_hashes: Mapping[str, str],
    observation_receipt_hashes: Mapping[str, str],
    decision_hashes_by_fleet: Mapping[str, str],
    movement: Mapping[str, Any],
    phase6: Mapping[str, Any],
    phase7: Mapping[str, Any],
    resolution: Mapping[str, Any],
    phase8: Mapping[str, Any],
) -> None:
    if ledger.get("schema") != PHASE9_LEDGER_ENTRY_SCHEMA:
        raise Phase10Error("unsupported Phase-9 ledger-entry schema")
    if ledger.get("phase9_contract_id") != PHASE9_CONTRACT_ID or ledger.get("phase9_version") != PHASE9_VERSION:
        raise Phase10Error("ledger Phase-9 identity mismatch")
    if ledger.get("phase9_source_identity") != context["accepted_source_identities"]["phase9_orchestrator"]:
        raise Phase10Error("ledger Phase-9 source identity mismatch")
    if ledger.get("accepted_source_identities") != context["accepted_source_identities"]:
        raise Phase10Error("ledger accepted source identities mismatch")
    if ledger.get("canonical_json_profile") != CANONICAL_JSON_PROFILE:
        raise Phase10Error("ledger canonical JSON profile mismatch")
    if ledger.get("historical_canon_status") != HISTORICAL_CANON_STATUS:
        raise Phase10Error("ledger historical canon status mismatch")
    _require_false(ledger, "reporter_invoked", "ledger_entry")
    _require_false(ledger, "run0_executed", "ledger_entry")
    if str(ledger.get("run_identity_sha256") or "") != str(context["run_identity_sha256"]):
        raise Phase10Error("ledger run identity mismatch")
    if str(ledger.get("t0_roster_sha256") or "") != str(context["t0_roster_sha256"]):
        raise Phase10Error("ledger roster identity mismatch")
    if require_int(ledger.get("macrostep_index"), "ledger.macrostep_index", minimum=1) != macrostep_index:
        raise Phase10Error("ledger macrostep sequence mismatch")
    ledger_sha = _verify_hash(ledger, "ledger_entry_sha256", "ledger_entry")
    expected_previous = (
        GENESIS_MARKER
        if previous_ledger is None
        else str(previous_ledger["ledger_entry_sha256"])
    )
    if str(ledger.get("previous_ledger_entry_sha256") or "") != expected_previous:
        raise Phase10Error("ledger previous-entry chain mismatch")
    if final and ledger_sha != expected_ledger_head_sha256:
        raise Phase10Error("ledger head differs from accepted trust anchor")
    if not final and ledger_sha == expected_ledger_head_sha256:
        raise Phase10Error("accepted ledger head appears before final packet")

    start_ms = require_int(ledger.get("start_elapsed_ms"), "ledger.start_elapsed_ms", minimum=0)
    end_ms = require_int(ledger.get("end_elapsed_ms"), "ledger.end_elapsed_ms", minimum=1)
    if end_ms <= start_ms:
        raise Phase10Error("ledger elapsed time does not advance")
    if previous_ledger is not None:
        if start_ms != int(previous_ledger["end_elapsed_ms"]):
            raise Phase10Error("ledger elapsed-time chain gap")
        if str(ledger.get("previous_committed_state_sha256") or "") != str(
            previous_ledger["phase8_next_state_sha256"]
        ):
            raise Phase10Error("ledger committed-state chain mismatch")

    if ledger.get("live_observation_sha256_by_side") != dict(sorted(observation_hashes.items())):
        raise Phase10Error("ledger observation hash map mismatch")
    if ledger.get("live_observation_receipt_sha256_by_side") != dict(
        sorted(observation_receipt_hashes.items())
    ):
        raise Phase10Error("ledger observation-receipt map mismatch")
    if ledger.get("phase4_decision_sha256_by_fleet") != dict(sorted(decision_hashes_by_fleet.items())):
        raise Phase10Error("ledger command-decision map mismatch")

    hash_links = {
        "phase5_receipt_sha256": movement["movement_receipt_sha256"],
        "phase6_receipt_sha256": phase6["phase6_receipt_sha256"],
        "phase7_receipt_sha256": phase7["phase7_receipt_sha256"],
        "phase8_resolution_state_sha256": resolution["resolution_state_sha256"],
        "phase8_receipt_sha256": phase8["phase8_receipt_sha256"],
        "phase5_state_sha256": movement["next_state_sha256"],
        "phase6_state_sha256": phase6["next_state_sha256"],
        "phase7_state_sha256": phase7["next_state_sha256"],
        "phase8_next_state_sha256": phase8["next_state_sha256"],
    }
    for field, expected in hash_links.items():
        if str(ledger.get(field) or "") != str(expected):
            raise Phase10Error(f"ledger artifact link mismatch: {field}")

    if str(movement.get("prior_state_sha256") or "") != str(ledger["previous_committed_state_sha256"]):
        raise Phase10Error("movement parent state differs from ledger")
    if str(phase6.get("prior_state_sha256") or "") != str(movement["next_state_sha256"]):
        raise Phase10Error("movement to Phase-6 state chain mismatch")
    if str(phase7.get("prior_state_sha256") or "") != str(phase6["next_state_sha256"]):
        raise Phase10Error("Phase-6 to Phase-7 state chain mismatch")
    if str(phase8.get("prior_state_sha256") or "") != str(phase7["next_state_sha256"]):
        raise Phase10Error("Phase-7 to Phase-8 state chain mismatch")
    if str(phase7.get("phase6_receipt_sha256") or "") != _normalized_phase6_receipt_sha256(phase6):
        raise Phase10Error("Phase-7 normalized Phase-6 parent receipt mismatch")
    if str(phase8.get("phase7_receipt_sha256") or "") != str(phase7["phase7_receipt_sha256"]):
        raise Phase10Error("Phase-8 parent receipt mismatch")
    if str(resolution.get("parent_phase7_receipt_sha256") or "") != str(phase7["phase7_receipt_sha256"]):
        raise Phase10Error("Phase-8 resolution parent receipt mismatch")
    if str(resolution.get("parent_phase7_state_sha256") or "") != str(phase7["next_state_sha256"]):
        raise Phase10Error("Phase-8 resolution parent state mismatch")
    if ledger.get("terminal_outcome") != resolution.get("terminal_outcome"):
        raise Phase10Error("ledger terminal outcome differs from Phase 8")

    if require_int(movement.get("macrostep_index"), "movement.macrostep_index", minimum=1) != macrostep_index:
        raise Phase10Error("movement macrostep mismatch")
    if require_int(phase6.get("macrostep_index"), "phase6.macrostep_index", minimum=1) != macrostep_index:
        raise Phase10Error("Phase-6 macrostep mismatch")
    if require_int(phase7.get("macrostep_index"), "phase7.macrostep_index", minimum=1) != macrostep_index:
        raise Phase10Error("Phase-7 macrostep mismatch")
    if require_int(resolution.get("macrostep_index"), "phase8_resolution.macrostep_index", minimum=1) != macrostep_index:
        raise Phase10Error("Phase-8 macrostep mismatch")
    if int(movement.get("start_elapsed_ms", -1)) != start_ms or int(movement.get("end_elapsed_ms", -1)) != end_ms:
        raise Phase10Error("movement elapsed time differs from ledger")
    for label, artifact in (
        ("phase6", phase6),
        ("phase7", phase7),
        ("phase8_resolution", resolution),
    ):
        if require_int(artifact.get("elapsed_ms"), f"{label}.elapsed_ms", minimum=0) != end_ms:
            raise Phase10Error(f"{label} elapsed time differs from ledger")


def validate_report_input(raw: Any) -> dict[str, Any]:
    """Validate and deep-copy a complete genesis-to-head Phase-9 artifact packet."""
    packet = _mapping(raw, "report_input")
    _exact_keys(packet, INPUT_FIELDS, "report_input")
    if packet.get("schema") != INPUT_SCHEMA:
        raise Phase10Error("unsupported Phase-10 input schema")
    expected_run = require_sha256(
        packet.get("expected_run_identity_sha256"),
        "expected_run_identity_sha256",
    )
    expected_head = require_sha256(
        packet.get("expected_ledger_head_sha256"),
        "expected_ledger_head_sha256",
    )
    context, side_to_fleet, ship_ids, _ = _validate_run_context(
        packet.get("run_context"),
        expected_run,
    )
    macrosteps = _sequence(packet.get("macrosteps"), "report_input.macrosteps")
    if not macrosteps:
        raise Phase10Error("Phase-10 reporting requires at least one macrostep")

    normalized_steps: list[dict[str, Any]] = []
    previous_step: Mapping[str, Any] | None = None
    previous_ledger: Mapping[str, Any] | None = None
    for offset, raw_step in enumerate(macrosteps, start=1):
        step = _mapping(raw_step, f"macrosteps[{offset - 1}]")
        _exact_keys(step, MACROSTEP_FIELDS, f"macrosteps[{offset - 1}]")
        if step.get("schema") != MACROSTEP_PACKET_SCHEMA:
            raise Phase10Error(f"unsupported macrostep packet schema at {offset}")
        ledger = _mapping(step.get("ledger_entry"), f"macrosteps[{offset - 1}].ledger_entry")
        previous_state_sha = require_sha256(
            ledger.get("previous_committed_state_sha256"),
            f"macrosteps[{offset - 1}].previous_committed_state_sha256",
        )
        observations, observation_hashes, observation_receipt_hashes = _validate_observations(
            step.get("observation_receipts_by_side"),
            context=context,
            side_to_fleet=side_to_fleet,
            macrostep_index=offset,
            previous_packet=previous_step,
            previous_committed_state_sha256=previous_state_sha,
        )
        decisions, decision_hashes_by_fleet, decision_hashes_by_side = _validate_decisions(
            step.get("decisions_by_fleet"),
            side_to_fleet=side_to_fleet,
            macrostep_index=offset,
        )
        for side_id, fleet_id in side_to_fleet.items():
            if str(decisions[fleet_id].get("observation_sha256") or "") != observation_hashes[side_id]:
                raise Phase10Error(f"command/live observation mismatch: {side_id}")
        movement, phase6, phase7, resolution, phase8 = _validate_phase_receipts(
            step,
            context=context,
            macrostep_index=offset,
            ship_ids=ship_ids,
            side_to_fleet=side_to_fleet,
            decision_hashes_by_fleet=decision_hashes_by_fleet,
            decision_hashes_by_side=decision_hashes_by_side,
        )
        _validate_ledger_and_cross_links(
            ledger,
            context=context,
            macrostep_index=offset,
            previous_ledger=previous_ledger,
            expected_ledger_head_sha256=expected_head,
            final=offset == len(macrosteps),
            observation_hashes=observation_hashes,
            observation_receipt_hashes=observation_receipt_hashes,
            decision_hashes_by_fleet=decision_hashes_by_fleet,
            movement=movement,
            phase6=phase6,
            phase7=phase7,
            resolution=resolution,
            phase8=phase8,
        )
        terminal = _mapping(resolution.get("terminal_outcome"), "terminal_outcome")
        if terminal.get("terminated") is True and offset != len(macrosteps):
            raise Phase10Error("terminal ledger entry must be final")
        normalized_step = {
            "schema": MACROSTEP_PACKET_SCHEMA,
            "ledger_entry": copy.deepcopy(dict(ledger)),
            "observation_receipts_by_side": observations,
            "decisions_by_fleet": decisions,
            "movement_receipt": movement,
            "phase6_receipt": phase6,
            "phase7_receipt": phase7,
            "phase8_resolution_state": resolution,
            "phase8_receipt": phase8,
        }
        normalized_steps.append(normalized_step)
        previous_step = normalized_step
        previous_ledger = normalized_step["ledger_entry"]

    return {
        "schema": INPUT_SCHEMA,
        "expected_run_identity_sha256": expected_run,
        "expected_ledger_head_sha256": expected_head,
        "run_context": context,
        "macrosteps": normalized_steps,
    }
