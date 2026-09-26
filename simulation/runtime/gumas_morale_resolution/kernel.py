"""Deterministic Phase-8 morale, withdrawal, surrender, ceasefire, and termination."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from simulation.runtime.gumas_command_policy import policy as command_policy
from simulation.runtime.gumas_damage_disposition import kernel as phase7_kernel
from simulation.runtime.gumas_damage_disposition.normalization import normalizer_source_identity
from simulation.runtime.gumas_movement_geometry.geometry import round_half_even_fraction
from simulation.runtime.gumas_movement_geometry.kernel import _hash_without_field as movement_hash_without_field

from .constants import (
    ACTIVE_PHYSICAL_DISPOSITIONS,
    BATTLE_SHOCK_WEIGHTS_Q1000,
    CANONICAL_JSON_PROFILE,
    CEASEFIRE_OFFER_TTL_MACROSTEPS,
    COHESION_LOSS_WEIGHTS_Q1000,
    HARD_LIMIT_MS,
    KNOWN_STRATEGIC_POSTURES,
    MORALE_LOSS_WEIGHTS_Q1000,
    MUTUAL_DISENGAGE_REQUIRED_STREAK,
    PHASE8_CONTRACT_ID,
    PHASE8_VERSION,
    SURRENDER_MAX_COMBAT_EFFECTIVE_FRACTION_Q1000,
    SURRENDER_MAX_FLEET_MORALE_Q1000,
    SURRENDER_PRESSURE_WEIGHTS_Q1000,
    SURRENDER_THRESHOLD_BASE_Q1000,
    SURRENDER_THRESHOLD_RESOLVE_SPAN_Q1000,
    SURVIVING_PHYSICAL_DISPOSITIONS,
    WITHDRAWAL_BOUNDARY_UM,
    WITHDRAWAL_SUCCESS_FRACTION_Q1000,
)


class Phase8Error(RuntimeError):
    """Raised when Phase-8 input violates the pinned contract."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _hash_without_field(value: Mapping[str, Any], field: str) -> str:
    return hashlib.sha256(canonical_json_bytes({k: v for k, v in value.items() if k != field})).hexdigest()


def _source_identity() -> dict[str, Any]:
    directory = Path(__file__).resolve().parent
    modules: dict[str, str] = {}
    bundle = hashlib.sha256()
    for name in ("constants.py", "kernel.py"):
        data = (directory / name).read_bytes()
        modules[name] = hashlib.sha256(data).hexdigest()
        bundle.update(name.encode("ascii")); bundle.update(b"\0"); bundle.update(data); bundle.update(b"\0")
    return {"module_sha256": modules, "bundle_sha256": bundle.hexdigest()}


def _q1000(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 1000:
        raise Phase8Error(f"{label} must be integer q1000")
    return int(value)


def _nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Phase8Error(f"{label} must be a non-negative integer")
    return int(value)


def _mean_q1000(values: Sequence[int]) -> int:
    return round_half_even_fraction(sum(values), len(values)) if values else 0


def _weighted_q1000(terms: Mapping[str, int], weights: Mapping[str, int]) -> int:
    total = sum(int(terms[key]) * int(weight) for key, weight in weights.items())
    return max(0, min(1000, round_half_even_fraction(total, 1000)))


def _phase7_composite_source_sha256() -> str:
    payload = {
        "damage_core_source_identity": phase7_kernel._source_identity(),
        "semantic_normalizer_source_identity": normalizer_source_identity(),
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _verify_phase7(state: Mapping[str, Any], receipt: Mapping[str, Any]) -> None:
    recorded_state = str(state.get("state_sha256") or "")
    if not recorded_state or recorded_state != movement_hash_without_field(state, "state_sha256"):
        raise Phase8Error("Phase-7 state hash mismatch")
    recorded_receipt = str(receipt.get("phase7_receipt_sha256") or "")
    if not recorded_receipt or recorded_receipt != phase7_kernel._hash_without_field(receipt, "phase7_receipt_sha256"):
        raise Phase8Error("Phase-7 receipt hash mismatch")
    if str(receipt.get("next_state_sha256") or "") != recorded_state:
        raise Phase8Error("Phase-7 receipt does not bind current state")
    if dict(receipt.get("phase7_source_identity") or {}) != phase7_kernel._source_identity():
        raise Phase8Error("Phase-7 damage-core source identity mismatch")
    if dict(receipt.get("phase7_semantic_normalizer_source_identity") or {}) != normalizer_source_identity():
        raise Phase8Error("Phase-7 semantic normalizer identity mismatch")
    if str(receipt.get("phase7_composite_source_sha256") or "") != _phase7_composite_source_sha256():
        raise Phase8Error("Phase-7 composite source identity mismatch")
    if receipt.get("morale_mutated") is not False or receipt.get("cohesion_mutated") is not False:
        raise Phase8Error("Phase-7 receipt unexpectedly claims morale/cohesion mutation")
    if receipt.get("termination_decision_made") is not False:
        raise Phase8Error("Phase-7 receipt unexpectedly claims termination")


def _baseline_identity(baseline: Mapping[str, Any]) -> dict[str, str]:
    return {"baseline_id": str(baseline["baseline_id"]), "baseline_version": str(baseline["version"])}


def _side_fleet_map(baseline: Mapping[str, Any]) -> dict[str, str]:
    sides = baseline.get("sides")
    if not isinstance(sides, Mapping) or len(sides) != 2:
        raise Phase8Error("Phase 8 requires exactly two frozen sides")
    result = {str(side): str(data["fleet_id"]) for side, data in sides.items()}
    if any(not side or not fleet for side, fleet in result.items()) or len(set(result.values())) != 2:
        raise Phase8Error("invalid side/fleet mapping")
    return dict(sorted(result.items()))


def _verify_command_receipts(command_receipts: Mapping[str, Any], baseline: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    side_to_fleet = _side_fleet_map(baseline)
    expected_baseline = _baseline_identity(baseline)
    expected_source = command_policy._source_identity()
    result: dict[str, dict[str, Any]] = {}
    for side, fleet in side_to_fleet.items():
        raw = command_receipts.get(fleet)
        if not isinstance(raw, Mapping):
            raise Phase8Error(f"missing command receipt for {fleet}")
        receipt = copy.deepcopy(dict(raw))
        recorded = str(receipt.get("decision_sha256") or "")
        payload = {k: v for k, v in receipt.items() if k != "decision_sha256"}
        if not recorded or recorded != command_policy.sha256_canonical(payload):
            raise Phase8Error(f"command receipt hash mismatch for {fleet}")
        if str(receipt.get("policy_source_sha256") or "") != expected_source["bundle_sha256"]:
            raise Phase8Error(f"command policy source mismatch for {fleet}")
        if str(receipt.get("policy_module_sha256") or "") != expected_source["policy_module_sha256"]:
            raise Phase8Error(f"command module source mismatch for {fleet}")
        if str(receipt.get("coefficient_table_sha256") or "") != expected_source["coefficient_table_sha256"]:
            raise Phase8Error(f"command coefficient source mismatch for {fleet}")
        if str(receipt.get("side_id") or "") != side or str(receipt.get("fleet_id") or "") != fleet:
            raise Phase8Error(f"command side/fleet mismatch for {fleet}")
        if dict(receipt.get("baseline_identity") or {}) != expected_baseline:
            raise Phase8Error(f"command baseline mismatch for {fleet}")
        posture = str((receipt.get("orders") or {}).get("strategic_posture") or "")
        if posture not in KNOWN_STRATEGIC_POSTURES:
            raise Phase8Error(f"unknown strategic posture for {fleet}: {posture}")
        result[side] = receipt
    if set(command_receipts) != set(side_to_fleet.values()):
        raise Phase8Error("unexpected command receipt fleet key")
    return result


def _verify_prior_resolution(prior: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if prior is None:
        return None
    recorded = str(prior.get("resolution_state_sha256") or "")
    if not recorded or recorded != _hash_without_field(prior, "resolution_state_sha256"):
        raise Phase8Error("prior Phase-8 resolution state hash mismatch")
    if dict(prior.get("phase8_source_identity") or {}) != _source_identity():
        raise Phase8Error("prior Phase-8 source identity mismatch")
    return copy.deepcopy(dict(prior))


def _vessels_by_side(state: Mapping[str, Any], side_to_fleet: Mapping[str, str]) -> dict[str, list[dict[str, Any]]]:
    result = {side: [] for side in side_to_fleet}
    seen: set[str] = set()
    vessels = state.get("vessels")
    if not isinstance(vessels, Sequence) or isinstance(vessels, (str, bytes)):
        raise Phase8Error("state.vessels must be a sequence")
    for raw in vessels:
        if not isinstance(raw, Mapping):
            raise Phase8Error("vessel must be a mapping")
        vessel = copy.deepcopy(dict(raw))
        ship_id = str(vessel.get("ship_id") or "")
        side = str(vessel.get("side_id") or "")
        fleet = str(vessel.get("fleet_id") or "")
        if not ship_id or ship_id in seen or side not in result or fleet != side_to_fleet[side]:
            raise Phase8Error(f"invalid vessel identity: {ship_id}")
        seen.add(ship_id)
        _q1000(vessel.get("morale_q1000"), f"{ship_id}.morale")
        _q1000(vessel.get("cohesion_q1000"), f"{ship_id}.cohesion")
        readiness = vessel.get("readiness_q1000") or {}
        _q1000(readiness.get("propulsion"), f"{ship_id}.propulsion readiness")
        _q1000(readiness.get("weapons"), f"{ship_id}.weapons readiness")
        position = vessel.get("position_um")
        velocity = vessel.get("velocity_um_s")
        if not isinstance(position, Sequence) or len(position) != 3 or not isinstance(velocity, Sequence) or len(velocity) != 3:
            raise Phase8Error(f"{ship_id} missing position/velocity")
        if any(isinstance(x, bool) or not isinstance(x, int) for x in [*position, *velocity]):
            raise Phase8Error(f"{ship_id} position/velocity must be integer")
        result[side].append(vessel)
    for side in result:
        result[side].sort(key=lambda item: str(item["ship_id"]))
        if not result[side]:
            raise Phase8Error(f"side {side} has no vessels in frozen roster")
    return result


def _damage_receipts_by_ship(phase7_receipt: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    receipts = phase7_receipt.get("target_damage_receipts") or []
    if not isinstance(receipts, Sequence):
        raise Phase8Error("Phase-7 target damage receipts invalid")
    for receipt in receipts:
        ship_id = str(receipt.get("target_ship_id") or "")
        if not ship_id or ship_id in result:
            raise Phase8Error("invalid Phase-7 target damage receipt")
        result[ship_id] = receipt
    return result


def _side_shock(side_vessels: Sequence[Mapping[str, Any]], damage_by_ship: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    total_max_hull = 0
    total_new_hull_loss = 0
    newly_incapacitated = 0
    for vessel in side_vessels:
        ship_id = str(vessel["ship_id"])
        physical = vessel.get("physical") or {}
        total_max_hull += _nonnegative_int(physical.get("hull_integrity_milliunits"), f"{ship_id}.hull max")
        target = damage_by_ship.get(ship_id)
        if target:
            hull = target.get("hull") or {}
            total_new_hull_loss += _nonnegative_int(hull.get("lost"), f"{ship_id}.new hull loss")
            disp = target.get("physical_disposition") or {}
            if str(disp.get("before")) in ACTIVE_PHYSICAL_DISPOSITIONS and str(disp.get("after")) in {"disabled", "destroyed"}:
                newly_incapacitated += 1
    if total_max_hull <= 0:
        raise Phase8Error("side maximum hull must be positive")
    fleet_hull_loss = max(0, min(1000, round_half_even_fraction(total_new_hull_loss * 1000, total_max_hull)))
    incapacity = round_half_even_fraction(newly_incapacitated * 1000, len(side_vessels))
    battle_shock = _weighted_q1000({"fleet_hull_loss": fleet_hull_loss, "new_incapacity": incapacity}, BATTLE_SHOCK_WEIGHTS_Q1000)
    return {"fleet_hull_loss_q1000": fleet_hull_loss, "new_incapacity_q1000": incapacity, "newly_incapacitated_count": newly_incapacitated, "battle_shock_q1000": battle_shock}


def _mean_dissent(command_receipt: Mapping[str, Any]) -> int:
    specialists = command_receipt.get("specialists")
    if not isinstance(specialists, Mapping) or not specialists:
        raise Phase8Error("command receipt missing specialists")
    values = [_q1000(data.get("dissent_q1000"), f"{role}.dissent") for role, data in sorted(specialists.items())]
    return _mean_q1000(values)


def _update_morale_cohesion(side_vessels: Sequence[Mapping[str, Any]], damage_by_ship: Mapping[str, Mapping[str, Any]], shock: Mapping[str, int], command_receipt: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    mean_dissent = _mean_dissent(command_receipt)
    coupled_dissent = round_half_even_fraction(mean_dissent * shock["battle_shock_q1000"], 1000)
    updated: list[dict[str, Any]] = []
    for raw in side_vessels:
        vessel = copy.deepcopy(dict(raw))
        ship_id = str(vessel["ship_id"])
        target = damage_by_ship.get(ship_id)
        local_hull_loss = _nonnegative_int(((target or {}).get("hull") or {}).get("new_hull_loss_q1000", 0), f"{ship_id}.local hull loss")
        local_hull_loss = max(0, min(1000, local_hull_loss))
        if str(vessel.get("disposition")) != "destroyed":
            morale_loss = _weighted_q1000({"local_hull_loss": local_hull_loss, "fleet_hull_loss": shock["fleet_hull_loss_q1000"], "new_incapacity": shock["new_incapacity_q1000"]}, MORALE_LOSS_WEIGHTS_Q1000)
            cohesion_loss = _weighted_q1000({"fleet_hull_loss": shock["fleet_hull_loss_q1000"], "new_incapacity": shock["new_incapacity_q1000"], "shock_coupled_dissent": coupled_dissent}, COHESION_LOSS_WEIGHTS_Q1000)
            vessel["morale_q1000"] = max(0, int(vessel["morale_q1000"]) - morale_loss)
            vessel["cohesion_q1000"] = max(0, int(vessel["cohesion_q1000"]) - cohesion_loss)
        updated.append(vessel)
    return updated, {"mean_dissent_q1000": mean_dissent, "shock_coupled_dissent_q1000": coupled_dissent}


def _aggregate_side(vessels: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    surviving = [v for v in vessels if str(v.get("disposition")) in SURVIVING_PHYSICAL_DISPOSITIONS]
    mobile = [v for v in surviving if str(v.get("disposition")) in ACTIVE_PHYSICAL_DISPOSITIONS and int((v.get("readiness_q1000") or {}).get("propulsion", 0)) >= 150]
    effective = [v for v in surviving if str(v.get("disposition")) in ACTIVE_PHYSICAL_DISPOSITIONS and int((v.get("readiness_q1000") or {}).get("weapons", 0)) >= 150]
    disabled = [v for v in surviving if str(v.get("disposition")) == "disabled"]
    destroyed = [v for v in vessels if str(v.get("disposition")) == "destroyed"]
    morale = _mean_q1000([int(v["morale_q1000"]) for v in surviving])
    cohesion = _mean_q1000([int(v["cohesion_q1000"]) for v in surviving])
    effective_fraction = round_half_even_fraction(len(effective) * 1000, len(surviving)) if surviving else 0
    hull_current = sum(int(v["physical"]["hull_current_milliunits"]) for v in surviving)
    hull_max = sum(int(v["physical"]["hull_integrity_milliunits"]) for v in surviving)
    hull_fraction = round_half_even_fraction(hull_current * 1000, hull_max) if hull_max else 0
    return {
        "surviving_ship_ids": sorted(str(v["ship_id"]) for v in surviving),
        "mobile_ship_ids": sorted(str(v["ship_id"]) for v in mobile),
        "combat_effective_ship_ids": sorted(str(v["ship_id"]) for v in effective),
        "disabled_ship_ids": sorted(str(v["ship_id"]) for v in disabled),
        "destroyed_ship_ids": sorted(str(v["ship_id"]) for v in destroyed),
        "fleet_morale_q1000": morale,
        "fleet_cohesion_q1000": cohesion,
        "combat_effective_fraction_q1000": max(0, min(1000, effective_fraction)),
        "surviving_hull_fraction_q1000": max(0, min(1000, hull_fraction)),
    }


def _update_offers(current_macrostep: int, commands_by_side: Mapping[str, Mapping[str, Any]], prior: Mapping[str, Any] | None) -> tuple[dict[str, int | None], dict[str, bool], dict[str, int]]:
    prior_offers = (prior or {}).get("ceasefire_offer_expiry_macrostep_by_side") or {}
    expiry: dict[str, int | None] = {}
    active: dict[str, bool] = {}
    sides = sorted(commands_by_side)
    for side in sides:
        posture = str(commands_by_side[side]["orders"]["strategic_posture"])
        prior_expiry = prior_offers.get(side)
        if posture == "CEASEFIRE_PROBE":
            value: int | None = current_macrostep + CEASEFIRE_OFFER_TTL_MACROSTEPS
        elif posture == "PRESS":
            value = None
        elif isinstance(prior_expiry, int) and not isinstance(prior_expiry, bool) and current_macrostep <= prior_expiry:
            value = prior_expiry
        else:
            value = None
        expiry[side] = value
        active[side] = value is not None and current_macrostep <= int(value)
    negotiation: dict[str, int] = {}
    for side in sides:
        opponent = next(other for other in sides if other != side)
        negotiation[side] = 1000 if active[opponent] else 0
    return expiry, active, negotiation


def _withdrawal_receipt(vessels: Sequence[Mapping[str, Any]], posture: str) -> dict[str, Any]:
    mobile = [v for v in vessels if str(v.get("disposition")) in ACTIVE_PHYSICAL_DISPOSITIONS and int((v.get("readiness_q1000") or {}).get("propulsion", 0)) >= 150]
    withdrawn: list[str] = []
    for v in mobile:
        p = [int(x) for x in v["position_um"]]
        vel = [int(x) for x in v["velocity_um_s"]]
        radius_sq = sum(x * x for x in p)
        outbound_dot = sum(a * b for a, b in zip(p, vel))
        if radius_sq >= WITHDRAWAL_BOUNDARY_UM * WITHDRAWAL_BOUNDARY_UM and outbound_dot > 0:
            withdrawn.append(str(v["ship_id"]))
    fraction = round_half_even_fraction(len(withdrawn) * 1000, len(mobile)) if mobile else 0
    success = posture == "DISENGAGE" and bool(mobile) and fraction >= WITHDRAWAL_SUCCESS_FRACTION_Q1000
    withdrawn_set = set(withdrawn)
    stranded = sorted(str(v["ship_id"]) for v in vessels if str(v.get("disposition")) != "destroyed" and str(v["ship_id"]) not in withdrawn_set) if success else []
    return {"boundary_um": WITHDRAWAL_BOUNDARY_UM, "intent": posture == "DISENGAGE", "mobile_ship_ids": sorted(str(v["ship_id"]) for v in mobile), "withdrawn_mobile_ship_ids": sorted(withdrawn), "withdrawn_mobile_fraction_q1000": max(0, min(1000, fraction)), "success": success, "stranded_or_abandoned_ship_ids": stranded}


def _surrender_receipt(command_receipt: Mapping[str, Any], aggregate: Mapping[str, Any], withdrawal: Mapping[str, Any], opponent_aggregate: Mapping[str, Any]) -> dict[str, Any]:
    posture = str(command_receipt["orders"]["strategic_posture"])
    commander = command_receipt["command_team_numeric"]["commander"]["attributes_q1000"]
    command_skill = _q1000(commander.get("command_skill"), "commander.command_skill")
    discipline = _q1000(commander.get("discipline"), "commander.discipline")
    casualty_aversion = _q1000(commander.get("casualty_aversion"), "commander.casualty_aversion")
    negotiation = _q1000(commander.get("negotiation_openness"), "commander.negotiation_openness")
    resolve = round_half_even_fraction(command_skill + discipline + (1000 - casualty_aversion) + (1000 - negotiation), 4)
    threshold = SURRENDER_THRESHOLD_BASE_Q1000 + round_half_even_fraction(resolve * SURRENDER_THRESHOLD_RESOLVE_SPAN_Q1000, 1000)
    obs = command_receipt.get("observation") or {}
    withdrawal_viability = _q1000(obs.get("withdrawal_viability"), "observation.withdrawal_viability")
    terms = {"combat_deficit": 1000 - int(aggregate["combat_effective_fraction_q1000"]), "hull_deficit": 1000 - int(aggregate["surviving_hull_fraction_q1000"]), "morale_deficit": 1000 - int(aggregate["fleet_morale_q1000"]), "cohesion_deficit": 1000 - int(aggregate["fleet_cohesion_q1000"]), "withdrawal_failure": 1000 - withdrawal_viability}
    pressure = _weighted_q1000(terms, SURRENDER_PRESSURE_WEIGHTS_Q1000)
    eligible = posture in {"CEASEFIRE_PROBE", "DISENGAGE"}
    predicate = bool(aggregate["surviving_ship_ids"]) and bool(opponent_aggregate["combat_effective_ship_ids"]) and not bool(withdrawal["success"]) and eligible and int(aggregate["combat_effective_fraction_q1000"]) <= SURRENDER_MAX_COMBAT_EFFECTIVE_FRACTION_Q1000 and int(aggregate["fleet_morale_q1000"]) <= SURRENDER_MAX_FLEET_MORALE_Q1000 and pressure >= threshold
    return {"eligible_posture": eligible, "commander_resolve_q1000": resolve, "surrender_threshold_q1000": threshold, "pressure_terms_q1000": terms, "surrender_pressure_q1000": pressure, "predicate": predicate}


def _outcome(sides: Sequence[str], aggregate: Mapping[str, Mapping[str, Any]], active_offers: Mapping[str, bool], disengage_streak: int, withdrawal: Mapping[str, Mapping[str, Any]], surrender: Mapping[str, Mapping[str, Any]], elapsed_ms: int) -> dict[str, Any]:
    annihilated = [s for s in sides if not aggregate[s]["surviving_ship_ids"]]
    incapacitated = [s for s in sides if aggregate[s]["surviving_ship_ids"] and not aggregate[s]["combat_effective_ship_ids"]]
    surrendered = [s for s in sides if surrender[s]["predicate"]]
    withdrawn = [s for s in sides if withdrawal[s]["success"]]
    mode = "ongoing"; victor = None; local_control = None; stalemate = False
    if len(annihilated) == 2:
        mode = "mutual_annihilation"
    elif len(annihilated) == 1:
        mode = "annihilation"; victor = next(s for s in sides if s not in annihilated); local_control = victor
    elif all(active_offers[s] for s in sides):
        mode = "mutual_ceasefire"
    elif len(surrendered) == 2:
        mode = "mutual_stand_down"
    elif len(incapacitated) == 2:
        mode = "mutual_incapacity"
    elif len(incapacitated) == 1:
        mode = "combat_incapacity"; winner = next(s for s in sides if s not in incapacitated)
        if aggregate[winner]["combat_effective_ship_ids"]:
            victor = winner; local_control = winner
    elif len(surrendered) == 1:
        mode = "surrender"; victor = next(s for s in sides if s not in surrendered); local_control = victor
    elif disengage_streak >= MUTUAL_DISENGAGE_REQUIRED_STREAK:
        mode = "mutual_disengagement"
    elif len(withdrawn) == 2:
        mode = "mutual_withdrawal"
    elif len(withdrawn) == 1:
        mode = "successful_withdrawal"; opponent = next(s for s in sides if s not in withdrawn)
        if aggregate[opponent]["surviving_ship_ids"]:
            local_control = opponent
    elif elapsed_ms >= HARD_LIMIT_MS:
        mode = "hard_limit_stalemate"; stalemate = True
    terminated = mode != "ongoing"
    return {"terminated": terminated, "termination_mode": mode, "victor_side_id": victor, "local_control_side_id": local_control, "withdrawn_side_ids": sorted(withdrawn), "surrendered_side_ids": sorted(surrendered), "incapacitated_side_ids": sorted(incapacitated), "annihilated_side_ids": sorted(annihilated), "stalemate": stalemate, "reason_code": mode}


def _engagement_and_protection(sides: Sequence[str], outcome: Mapping[str, Any], aggregate: Mapping[str, Mapping[str, Any]]) -> tuple[dict[str, str], list[str]]:
    status = {s: "engaged" for s in sides}
    protected: set[str] = set()
    mode = str(outcome["termination_mode"])
    if mode == "mutual_ceasefire":
        status = {s: "ceasefire" for s in sides}; protected.update(ship for s in sides for ship in aggregate[s]["surviving_ship_ids"])
    elif mode in {"mutual_disengagement", "mutual_withdrawal"}:
        status = {s: "disengaged" for s in sides}; protected.update(ship for s in sides for ship in aggregate[s]["surviving_ship_ids"])
    elif mode in {"mutual_stand_down", "mutual_incapacity"}:
        value = "surrendered" if mode == "mutual_stand_down" else "incapacitated"
        status = {s: value for s in sides}; protected.update(ship for s in sides for ship in aggregate[s]["surviving_ship_ids"])
    else:
        for s in outcome["annihilated_side_ids"]: status[s] = "annihilated"
        for s in outcome["incapacitated_side_ids"]: status[s] = "incapacitated"; protected.update(aggregate[s]["surviving_ship_ids"])
        for s in outcome["surrendered_side_ids"]: status[s] = "surrendered"; protected.update(aggregate[s]["surviving_ship_ids"])
        for s in outcome["withdrawn_side_ids"]: status[s] = "withdrawn"; protected.update(aggregate[s]["surviving_ship_ids"])
    return dict(sorted(status.items())), sorted(protected)


def _assert_no_forbidden_mutation(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    before_by_id = {str(v["ship_id"]): v for v in before["vessels"]}
    after_by_id = {str(v["ship_id"]): v for v in after["vessels"]}
    for ship_id in before_by_id:
        for field in ("position_um", "velocity_um_s", "physical", "readiness_q1000", "damage_state", "disposition"):
            if before_by_id[ship_id].get(field) != after_by_id[ship_id].get(field):
                raise Phase8Error(f"Phase 8 mutated forbidden vessel field {ship_id}.{field}")


def step_phase8_state(state: Mapping[str, Any], phase7_receipt: Mapping[str, Any], command_receipts_by_fleet: Mapping[str, Any], baseline: Mapping[str, Any], prior_resolution_state: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Apply deterministic morale/resolution semantics after one accepted Phase-7 step."""
    _verify_phase7(state, phase7_receipt)
    prior = _verify_prior_resolution(prior_resolution_state)
    commands_by_side = _verify_command_receipts(command_receipts_by_fleet, baseline)
    side_to_fleet = _side_fleet_map(baseline)
    sides = sorted(side_to_fleet)
    vessels_by_side = _vessels_by_side(state, side_to_fleet)
    damage_by_ship = _damage_receipts_by_ship(phase7_receipt)

    shock_by_side = {side: _side_shock(vessels_by_side[side], damage_by_ship) for side in sides}
    dissent_by_side: dict[str, dict[str, int]] = {}
    updated_by_side: dict[str, list[dict[str, Any]]] = {}
    for side in sides:
        updated, dissent = _update_morale_cohesion(vessels_by_side[side], damage_by_ship, shock_by_side[side], commands_by_side[side])
        updated_by_side[side] = updated; dissent_by_side[side] = dissent

    aggregate = {side: _aggregate_side(updated_by_side[side]) for side in sides}
    macrostep = _nonnegative_int(state.get("macrostep_index"), "macrostep_index")
    elapsed_ms = _nonnegative_int(state.get("elapsed_ms"), "elapsed_ms")
    offer_expiry, active_offers, negotiation_signal = _update_offers(macrostep, commands_by_side, prior)
    qualifies_disengage = all(str(commands_by_side[s]["orders"]["strategic_posture"]) == "DISENGAGE" for s in sides) and int(phase7_receipt.get("effect_count", 0)) == 0
    prior_streak = int((prior or {}).get("mutual_disengage_streak", 0))
    disengage_streak = prior_streak + 1 if qualifies_disengage else 0

    withdrawal = {side: _withdrawal_receipt(updated_by_side[side], str(commands_by_side[side]["orders"]["strategic_posture"])) for side in sides}
    surrender = {}
    for side in sides:
        opponent = next(other for other in sides if other != side)
        surrender[side] = _surrender_receipt(commands_by_side[side], aggregate[side], withdrawal[side], aggregate[opponent])
    outcome = _outcome(sides, aggregate, active_offers, disengage_streak, withdrawal, surrender, elapsed_ms)
    engagement, protected = _engagement_and_protection(sides, outcome, aggregate)

    source_identity = _source_identity()
    resolution_state: dict[str, Any] = {
        "schema": "aurora://simulation/gumas/phase8_resolution_state/v1.0",
        "phase8_contract_id": PHASE8_CONTRACT_ID,
        "phase8_version": PHASE8_VERSION,
        "phase8_source_identity": source_identity,
        "parent_phase7_state_sha256": str(state["state_sha256"]),
        "parent_phase7_receipt_sha256": str(phase7_receipt["phase7_receipt_sha256"]),
        "parent_resolution_state_sha256": str((prior or {}).get("resolution_state_sha256") or "") or None,
        "command_decision_sha256_by_side": {s: str(commands_by_side[s]["decision_sha256"]) for s in sides},
        "macrostep_index": macrostep,
        "elapsed_ms": elapsed_ms,
        "shock_by_side": shock_by_side,
        "dissent_by_side": dissent_by_side,
        "side_aggregate": aggregate,
        "ceasefire_offer_expiry_macrostep_by_side": offer_expiry,
        "active_ceasefire_offer_by_side": active_offers,
        "negotiation_signal_q1000_by_side": negotiation_signal,
        "mutual_disengage_streak": disengage_streak,
        "withdrawal_by_side": withdrawal,
        "surrender_by_side": surrender,
        "engagement_status_by_side": engagement,
        "protected_ship_ids": protected,
        "terminal_outcome": outcome,
    }
    resolution_state["resolution_state_sha256"] = _hash_without_field(resolution_state, "resolution_state_sha256")

    next_state = copy.deepcopy(dict(state)); next_state.pop("state_sha256", None)
    next_state["parent_state_sha256"] = str(state["state_sha256"])
    updated_by_id = {str(v["ship_id"]): v for side in sides for v in updated_by_side[side]}
    next_state["vessels"] = [updated_by_id[str(v["ship_id"])] for v in sorted(state["vessels"], key=lambda item: str(item["ship_id"]))]
    next_state["phase8_source_identity"] = source_identity
    next_state["last_phase8_resolution_state_sha256"] = resolution_state["resolution_state_sha256"]
    next_state["state_sha256"] = movement_hash_without_field(next_state, "state_sha256")
    _assert_no_forbidden_mutation(state, next_state)

    receipt: dict[str, Any] = {
        "schema": "aurora://simulation/gumas/phase8_step_receipt/v1.0",
        "phase8_contract_id": PHASE8_CONTRACT_ID,
        "phase8_version": PHASE8_VERSION,
        "phase8_source_identity": source_identity,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "prior_state_sha256": str(state["state_sha256"]),
        "phase7_receipt_sha256": str(phase7_receipt["phase7_receipt_sha256"]),
        "next_state_sha256": str(next_state["state_sha256"]),
        "resolution_state_sha256": str(resolution_state["resolution_state_sha256"]),
        "command_decision_sha256_by_side": resolution_state["command_decision_sha256_by_side"],
        "terminal_outcome": outcome,
        "morale_or_cohesion_mutated": any(int(before["morale_q1000"]) != int(updated_by_id[str(before["ship_id"])]["morale_q1000"]) or int(before["cohesion_q1000"]) != int(updated_by_id[str(before["ship_id"])]["cohesion_q1000"]) for before in state["vessels"]),
        "physical_state_mutated": False,
        "ambient_rng_used": False,
        "floating_authority_used": False,
        "prose_inputs_used": False,
    }
    receipt["phase8_receipt_sha256"] = _hash_without_field(receipt, "phase8_receipt_sha256")
    return next_state, resolution_state, receipt
