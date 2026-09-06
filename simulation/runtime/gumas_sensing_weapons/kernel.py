"""Deterministic Phase-6 sensing, EW, targeting, and effective-salvo kernel."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from simulation.runtime.gumas_movement_geometry.geometry import (
    round_half_even_fraction,
    separation_um,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as _movement_hash_without_field,
    _verify_motion_state,
    occulted_by_p17,
)
from simulation.runtime.gumas_command_policy.policy import (
    _source_identity as _command_policy_source_identity,
)

from .constants import (
    ACTIVE_JAM_TRACK_MULTIPLIER_Q1000,
    CANONICAL_JSON_PROFILE,
    CLASSIFY_HOSTILE_Q1000,
    CLASSIFY_SUSPECT_Q1000,
    CONTACT_MIN_Q1000,
    DECEPTION_IDENTITY_MULTIPLIER_Q1000,
    DECEPTION_TRACK_MULTIPLIER_Q1000,
    EW_MODES,
    FIRE_CONTACT_THRESHOLD_Q1000,
    LOGISTICS_EXPENDITURE_Q1000,
    PASSIVE_TRACK_BONUS_Q1000,
    PHASE6_CONTRACT_ID,
    PHASE6_VERSION,
    PROTECTED_DISPOSITIONS,
    PROTECT_NETWORK_MULTIPLIER_Q1000,
    TACTICAL_INTENSITY_Q1000,
)


class Phase6Error(RuntimeError):
    """Raised when Phase-6 state cannot be resolved under the pinned contract."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _hash_without_field(value: Mapping[str, Any], field: str) -> str:
    return sha256_canonical({key: item for key, item in value.items() if key != field})


def _source_identity() -> dict[str, Any]:
    directory = Path(__file__).resolve().parent
    names = ("constants.py", "kernel.py")
    modules: dict[str, str] = {}
    bundle = hashlib.sha256()
    for name in names:
        data = (directory / name).read_bytes()
        modules[name] = hashlib.sha256(data).hexdigest()
        bundle.update(name.encode("ascii"))
        bundle.update(b"\0")
        bundle.update(data)
        bundle.update(b"\0")
    return {"module_sha256": modules, "bundle_sha256": bundle.hexdigest()}


def _clamp(value: int, low: int = 0, high: int = 1000) -> int:
    return max(low, min(high, int(value)))


def _require_q1000(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Phase6Error(f"{label} must be an integer q1000 value")
    if not 0 <= value <= 1000:
        raise Phase6Error(f"{label} outside q1000 bounds: {value}")
    return int(value)


def _capability_q1000(vessel: Mapping[str, Any], name: str) -> int:
    """Read a Phase-3 capability without requiring a richer post-T0 schema.

    Phase 3 intentionally preserves direct capability fields under their
    calibrated output names and folds sensors/mobility into invertible physical
    calibration fields. Synthetic tests may provide the original short names.
    """
    capabilities = vessel.get("capability_q1000", {}) or {}
    if name in capabilities:
        return _require_q1000(
            capabilities[name], f"{vessel['ship_id']}.{name}"
        )

    aliases = {
        "electronic_warfare": "electronic_warfare_q1000",
        "stealth": "stealth_q1000",
    }
    alias = aliases.get(name)
    if alias and alias in capabilities:
        return _require_q1000(
            capabilities[alias], f"{vessel['ship_id']}.{alias}"
        )

    physical = vessel.get("physical", {}) or {}
    if name == "sensors":
        sensor_range_m = int(physical.get("sensor_range_m", -1))
        if sensor_range_m < 3_000_000:
            raise Phase6Error(
                f"{vessel['ship_id']}.sensor_range_m outside Phase-3 calibration"
            )
        return _clamp(
            round_half_even_fraction(
                (sensor_range_m - 3_000_000) * 1000,
                15_000_000,
            )
        )
    if name == "mobility":
        max_accel_mm_s2 = int(physical.get("max_accel_mm_s2", -1))
        if max_accel_mm_s2 < 5_000:
            raise Phase6Error(
                f"{vessel['ship_id']}.max_accel_mm_s2 outside Phase-3 calibration"
            )
        return _clamp(
            round_half_even_fraction(
                (max_accel_mm_s2 - 5_000) * 1000,
                115_000,
            )
        )
    raise Phase6Error(f"required Phase-6 capability missing: {vessel['ship_id']}.{name}")


def _verify_command_receipt(receipt: Mapping[str, Any]) -> None:
    recorded = str(receipt.get("decision_sha256") or "")
    actual = _hash_without_field(receipt, "decision_sha256")
    if not recorded or recorded != actual:
        raise Phase6Error("command decision receipt hash mismatch")
    expected_policy = _command_policy_source_identity()["bundle_sha256"]
    if str(receipt.get("policy_source_sha256") or "") != expected_policy:
        raise Phase6Error("command policy source identity mismatch")
    orders = receipt.get("orders") or {}
    specialist = orders.get("specialist_intents") or {}
    tactical = str(specialist.get("tactical") or "")
    ew_mode = str(specialist.get("ew_sensors") or "")
    logistics = str(specialist.get("logistics") or "")
    navigation = str(specialist.get("navigation") or "")
    if tactical not in TACTICAL_INTENSITY_Q1000:
        raise Phase6Error(f"unsupported tactical intent: {tactical}")
    if ew_mode not in EW_MODES:
        raise Phase6Error(f"unsupported EW intent: {ew_mode}")
    if logistics not in LOGISTICS_EXPENDITURE_Q1000:
        raise Phase6Error(f"unsupported logistics intent: {logistics}")
    if not navigation:
        raise Phase6Error("command receipt missing navigation intent")


def _command_by_fleet(receipts: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for fleet_id, receipt in sorted(receipts.items()):
        _verify_command_receipt(receipt)
        if str(receipt.get("fleet_id") or "") != fleet_id:
            raise Phase6Error("command receipt fleet key mismatch")
        specialist = receipt["orders"]["specialist_intents"]
        result[fleet_id] = {
            "decision_sha256": str(receipt["decision_sha256"]),
            "strategic_posture": str(receipt["orders"]["strategic_posture"]),
            "tactical": str(specialist["tactical"]),
            "ew_sensors": str(specialist["ew_sensors"]),
            "logistics": str(specialist["logistics"]),
            "navigation": str(specialist["navigation"]),
        }
    return result


def _range_quality_q1000(distance_um: int, maximum_range_um: int) -> int:
    if maximum_range_um <= 0:
        raise Phase6Error("range must be positive")
    fraction = _clamp(round_half_even_fraction(distance_um * 1000, maximum_range_um))
    return 250 + round_half_even_fraction(750 * (1000 - fraction), 1000)


def _vessel_lookup(state: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    vessels = sorted(state.get("vessels", []), key=lambda item: item["ship_id"])
    lookup: dict[str, Mapping[str, Any]] = {}
    for vessel in vessels:
        ship_id = str(vessel.get("ship_id") or "")
        if not ship_id or ship_id in lookup:
            raise Phase6Error(f"invalid or duplicate vessel id: {ship_id}")
        lookup[ship_id] = vessel
    return lookup


def _ew_strength(vessel: Mapping[str, Any]) -> int:
    capability = _capability_q1000(vessel, "electronic_warfare")
    readiness = _require_q1000(
        vessel.get("readiness_q1000", {}).get("ew"),
        f"{vessel['ship_id']}.readiness.ew",
    )
    return round_half_even_fraction(capability * readiness, 1000)


def _sensor_candidate(
    observer: Mapping[str, Any],
    target: Mapping[str, Any],
    elapsed_ms: int,
) -> dict[str, Any] | None:
    sensor_range_um = int(observer["physical"]["sensor_range_m"]) * 1_000_000
    distance_um = separation_um(observer["position_um"], target["position_um"])
    if distance_um > sensor_range_um:
        return None
    if occulted_by_p17(observer["position_um"], target["position_um"], elapsed_ms):
        return None
    range_quality = _range_quality_q1000(distance_um, sensor_range_um)
    sensors = _capability_q1000(observer, "sensors")
    readiness = _require_q1000(
        observer.get("readiness_q1000", {}).get("sensors"),
        f"{observer['ship_id']}.readiness.sensors",
    )
    stealth = _capability_q1000(target, "stealth")
    raw = _clamp(
        round_half_even_fraction(
            4 * sensors + 3 * range_quality + 3 * readiness - 5 * stealth,
            10,
        )
    )
    if raw < CONTACT_MIN_Q1000:
        return None
    return {
        "observer_ship_id": str(observer["ship_id"]),
        "target_ship_id": str(target["ship_id"]),
        "distance_um": distance_um,
        "sensor_range_um": sensor_range_um,
        "range_quality_q1000": range_quality,
        "raw_contact_q1000": raw,
    }


def _jam_effects(
    observer: Mapping[str, Any],
    vessels: Sequence[Mapping[str, Any]],
    commands: Mapping[str, Mapping[str, Any]],
    elapsed_ms: int,
) -> tuple[list[dict[str, Any]], int, int]:
    observer_fleet = str(observer["fleet_id"])
    observer_command = commands[observer_fleet]
    defender_ew = _ew_strength(observer)
    if observer_command["ew_sensors"] == "PROTECT_NETWORK":
        defender_ew = round_half_even_fraction(
            defender_ew * PROTECT_NETWORK_MULTIPLIER_Q1000, 1000
        )
    track_loss = 0
    identity_loss = 0
    details = []
    for jammer in sorted(vessels, key=lambda item: item["ship_id"]):
        if jammer["side_id"] == observer["side_id"]:
            continue
        jammer_command = commands[str(jammer["fleet_id"])]
        mode = jammer_command["ew_sensors"]
        if mode not in {"ACTIVE_JAM", "DECEPTIVE_EMISSIONS"}:
            continue
        ew_range_um = int(jammer["physical"]["sensor_range_m"]) * 1_000_000
        distance_um = separation_um(jammer["position_um"], observer["position_um"])
        if distance_um > ew_range_um:
            continue
        if occulted_by_p17(jammer["position_um"], observer["position_um"], elapsed_ms):
            continue
        range_quality = _range_quality_q1000(distance_um, ew_range_um)
        pressure = round_half_even_fraction(_ew_strength(jammer) * range_quality, 1000)
        net = max(0, pressure - defender_ew)
        if mode == "ACTIVE_JAM":
            track_delta = round_half_even_fraction(
                net * ACTIVE_JAM_TRACK_MULTIPLIER_Q1000, 1000
            )
            identity_delta = 0
        else:
            track_delta = round_half_even_fraction(
                net * DECEPTION_TRACK_MULTIPLIER_Q1000, 1000
            )
            identity_delta = round_half_even_fraction(
                net * DECEPTION_IDENTITY_MULTIPLIER_Q1000, 1000
            )
        track_loss += track_delta
        identity_loss += identity_delta
        details.append(
            {
                "source_ship_id": str(jammer["ship_id"]),
                "mode": mode,
                "range_quality_q1000": range_quality,
                "jam_pressure_q1000": pressure,
                "defender_protection_q1000": defender_ew,
                "net_jam_q1000": net,
                "track_loss_q1000": track_delta,
                "identity_loss_q1000": identity_delta,
            }
        )
    return details, track_loss, identity_loss


def _classification(identity_quality: int) -> str:
    if identity_quality >= CLASSIFY_HOSTILE_Q1000:
        return "hostile_confirmed"
    if identity_quality >= CLASSIFY_SUSPECT_Q1000:
        return "suspected_hostile"
    return "unknown"


def build_observation_state(
    state: Mapping[str, Any],
    command_receipts_by_fleet: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    _verify_motion_state(state)
    commands = _command_by_fleet(command_receipts_by_fleet)
    vessels = sorted(state["vessels"], key=lambda item: item["ship_id"])
    fleets = {str(vessel["fleet_id"]) for vessel in vessels}
    if fleets != set(commands):
        raise Phase6Error("command receipts do not cover exactly the active fleets")
    elapsed_ms = int(state["elapsed_ms"])
    contacts = []
    for observer in vessels:
        ew_details, track_loss, identity_loss = _jam_effects(
            observer, vessels, commands, elapsed_ms
        )
        passive_bonus = (
            PASSIVE_TRACK_BONUS_Q1000
            if commands[str(observer["fleet_id"])]["ew_sensors"] == "PASSIVE_TRACK"
            else 0
        )
        for target in vessels:
            if observer["side_id"] == target["side_id"]:
                continue
            candidate = _sensor_candidate(observer, target, elapsed_ms)
            if candidate is None:
                continue
            raw = int(candidate["raw_contact_q1000"])
            track = _clamp(raw + passive_bonus - track_loss)
            identity = _clamp(raw - identity_loss)
            contact = {
                **candidate,
                "line_of_sight_clear": True,
                "ew_effects": copy.deepcopy(ew_details),
                "passive_track_bonus_q1000": passive_bonus,
                "contact_quality_q1000": track,
                "identity_quality_q1000": identity,
                "classification": _classification(identity),
            }
            contact["contact_sha256"] = sha256_canonical(contact)
            contacts.append(contact)
    observation: dict[str, Any] = {
        "schema": "aurora://simulation/gumas/phase6_observation_state/v1.0",
        "phase6_contract_id": PHASE6_CONTRACT_ID,
        "phase6_version": PHASE6_VERSION,
        "phase6_source_identity": _source_identity(),
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "source_state_sha256": str(state["state_sha256"]),
        "macrostep_index": int(state["macrostep_index"]),
        "elapsed_ms": elapsed_ms,
        "command_decision_sha256_by_fleet": {
            fleet: commands[fleet]["decision_sha256"] for fleet in sorted(commands)
        },
        "contacts": sorted(
            contacts,
            key=lambda item: (item["observer_ship_id"], item["target_ship_id"]),
        ),
    }
    observation["observation_state_sha256"] = _hash_without_field(
        observation, "observation_state_sha256"
    )
    return observation


def _weapon_proximity(distance_um: int, weapon_range_um: int) -> int:
    return _clamp(1000 - round_half_even_fraction(distance_um * 1000, weapon_range_um))


def _target_score(contact: Mapping[str, Any], target: Mapping[str, Any], weapon_range_um: int) -> int:
    proximity = _weapon_proximity(int(contact["distance_um"]), weapon_range_um)
    firepower = int(target["physical"]["firepower_milliunits"])
    threat = _clamp(round_half_even_fraction(firepower * 1000, 20_000))
    return 5 * int(contact["contact_quality_q1000"]) + 3 * threat + 2 * proximity


def _child_draw(
    seed_u64: int,
    macrostep_index: int,
    shooter_id: str,
    target_id: str,
    shot_ordinal: int,
    source_sha256: str,
) -> tuple[int, str, str]:
    if not 0 <= int(seed_u64) < 2**64:
        raise Phase6Error("seed_u64 outside unsigned 64-bit range")
    material = (
        "AURORA::GUMAS::PHASE6::SHOT::"
        f"{int(seed_u64):016x}::{int(macrostep_index)}::{shooter_id}::"
        f"{target_id}::{int(shot_ordinal)}::{source_sha256}"
    )
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    u64 = int.from_bytes(digest[:8], "big", signed=False)
    return (
        u64 * 1000 // (2**64),
        hashlib.sha256(material.encode("utf-8")).hexdigest(),
        material,
    )


def _selected_contact(
    shooter: Mapping[str, Any],
    contacts: Sequence[Mapping[str, Any]],
    vessels_by_id: Mapping[str, Mapping[str, Any]],
    tactical: str,
) -> tuple[Mapping[str, Any] | None, int | None]:
    if tactical == "HOLD_FIRE":
        return None, None
    threshold = FIRE_CONTACT_THRESHOLD_Q1000[tactical]
    weapon_range_um = int(shooter["physical"]["effective_weapon_range_m"]) * 1_000_000
    eligible = []
    for contact in contacts:
        if contact["observer_ship_id"] != shooter["ship_id"]:
            continue
        target = vessels_by_id[contact["target_ship_id"]]
        if str(target.get("disposition") or "") in PROTECTED_DISPOSITIONS:
            continue
        if contact["classification"] != "hostile_confirmed":
            continue
        if int(contact["contact_quality_q1000"]) < threshold:
            continue
        if int(contact["distance_um"]) > weapon_range_um:
            continue
        score = _target_score(contact, target, weapon_range_um)
        eligible.append((score, str(target["ship_id"]), contact))
    if not eligible:
        return None, None
    eligible.sort(key=lambda item: (-item[0], item[1]))
    score, _, contact = eligible[0]
    return contact, score


def step_phase6_state(
    state: Mapping[str, Any],
    command_receipts_by_fleet: Mapping[str, Mapping[str, Any]],
    seed_u64: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _verify_motion_state(state)
    commands = _command_by_fleet(command_receipts_by_fleet)
    observation = build_observation_state(state, command_receipts_by_fleet)
    vessels_by_id = _vessel_lookup(state)
    contacts = observation["contacts"]
    source_identity = _source_identity()
    source_sha = source_identity["bundle_sha256"]

    next_state = copy.deepcopy(dict(state))
    next_state.pop("state_sha256", None)
    next_state["parent_state_sha256"] = str(state["state_sha256"])
    next_vessels = {
        str(v["ship_id"]): copy.deepcopy(v) for v in next_state["vessels"]
    }
    attempts = []
    effects = []
    selections = []

    for shooter_id in sorted(vessels_by_id):
        shooter = vessels_by_id[shooter_id]
        fleet_id = str(shooter["fleet_id"])
        command = commands[fleet_id]
        tactical = command["tactical"]
        if str(shooter.get("disposition") or "") in PROTECTED_DISPOSITIONS:
            selections.append(
                {
                    "shooter_ship_id": shooter_id,
                    "selected_target_ship_id": None,
                    "reason": "shooter_not_combat_capable",
                }
            )
            continue
        contact, score = _selected_contact(
            shooter, contacts, vessels_by_id, tactical
        )
        if contact is None:
            reason = "hold_fire" if tactical == "HOLD_FIRE" else "no_eligible_target"
            selections.append(
                {
                    "shooter_ship_id": shooter_id,
                    "selected_target_ship_id": None,
                    "reason": reason,
                }
            )
            continue
        target_id = str(contact["target_ship_id"])
        target = vessels_by_id[target_id]
        weapon_range_um = int(shooter["physical"]["effective_weapon_range_m"]) * 1_000_000
        proximity = _weapon_proximity(int(contact["distance_um"]), weapon_range_um)
        tactical_intensity = TACTICAL_INTENSITY_Q1000[tactical]
        logistics = LOGISTICS_EXPENDITURE_Q1000[command["logistics"]]
        salvo = round_half_even_fraction(tactical_intensity * logistics, 1000)
        weapons_readiness = _require_q1000(
            shooter.get("readiness_q1000", {}).get("weapons"),
            f"{shooter_id}.readiness.weapons",
        )
        resources = next_vessels[shooter_id]["resources_q1000"]
        ammo_cost = (
            max(1, round_half_even_fraction(12 * salvo, 1000)) if salvo else 0
        )
        energy_cost = (
            max(1, round_half_even_fraction(8 * salvo, 1000)) if salvo else 0
        )
        if int(resources.get("ammunition", 0)) < ammo_cost or int(
            resources.get("energy", 0)
        ) < energy_cost:
            attempts.append(
                {
                    "attempt_id": sha256_canonical(
                        {
                            "macrostep_index": state["macrostep_index"],
                            "shooter": shooter_id,
                            "target": target_id,
                            "ordinal": 0,
                            "rejected": "insufficient_resources",
                        }
                    ),
                    "shooter_ship_id": shooter_id,
                    "target_ship_id": target_id,
                    "fired": False,
                    "rejection_reason": "insufficient_resources",
                }
            )
            selections.append(
                {
                    "shooter_ship_id": shooter_id,
                    "selected_target_ship_id": target_id,
                    "target_score": score,
                    "reason": "insufficient_resources",
                }
            )
            continue
        target_evasion = _capability_q1000(target, "mobility")
        target_nav = commands[str(target["fleet_id"])]["navigation"]
        if target_nav == "EVASIVE_VECTOR":
            target_evasion = _clamp(target_evasion + 150)
        hit_chance = _clamp(
            50
            + round_half_even_fraction(
                500 * int(contact["contact_quality_q1000"]), 1000
            )
            + round_half_even_fraction(200 * proximity, 1000)
            + round_half_even_fraction(200 * weapons_readiness, 1000)
            - round_half_even_fraction(250 * target_evasion, 1000),
            25,
            975,
        )
        draw, material_sha, material = _child_draw(
            seed_u64,
            int(state["macrostep_index"]),
            shooter_id,
            target_id,
            0,
            source_sha,
        )
        hit = draw < hit_chance
        base_effect = round_half_even_fraction(
            int(shooter["physical"]["firepower_milliunits"])
            * salvo
            * weapons_readiness,
            1_000_000,
        )
        impact_quality = 0
        delivered = 0
        if hit:
            impact_quality = _clamp(
                500 + round_half_even_fraction(hit_chance - draw, 2),
                250,
                1000,
            )
            delivered = round_half_even_fraction(
                base_effect * impact_quality, 1000
            )
        resources["ammunition"] = int(resources["ammunition"]) - ammo_cost
        resources["energy"] = int(resources["energy"]) - energy_cost
        attempt = {
            "attempt_id": sha256_canonical(
                {
                    "macrostep_index": int(state["macrostep_index"]),
                    "shooter_ship_id": shooter_id,
                    "target_ship_id": target_id,
                    "shot_ordinal": 0,
                    "phase6_source_sha256": source_sha,
                }
            ),
            "shooter_ship_id": shooter_id,
            "target_ship_id": target_id,
            "command_decision_sha256": command["decision_sha256"],
            "contact_sha256": contact["contact_sha256"],
            "tactical_intent": tactical,
            "logistics_intent": command["logistics"],
            "salvo_intensity_q1000": salvo,
            "distance_um": int(contact["distance_um"]),
            "proximity_q1000": proximity,
            "contact_quality_q1000": int(contact["contact_quality_q1000"]),
            "hit_chance_q1000": hit_chance,
            "draw_q1000": draw,
            "child_material_sha256": material_sha,
            "child_material": material,
            "hit": hit,
            "base_effect_milliunits": base_effect,
            "impact_quality_q1000": impact_quality,
            "delivered_effect_milliunits": delivered,
            "ammo_cost_q1000": ammo_cost,
            "energy_cost_q1000": energy_cost,
            "fired": True,
            "rejection_reason": None,
        }
        attempts.append(attempt)
        selections.append(
            {
                "shooter_ship_id": shooter_id,
                "selected_target_ship_id": target_id,
                "target_score": score,
                "reason": "selected",
            }
        )
        if delivered > 0:
            effect = {
                "effect_id": sha256_canonical(
                    {
                        "attempt_id": attempt["attempt_id"],
                        "delivered_effect_milliunits": delivered,
                    }
                ),
                "attempt_id": attempt["attempt_id"],
                "source_ship_id": shooter_id,
                "target_ship_id": target_id,
                "delivered_effect_milliunits": delivered,
                "impact_quality_q1000": impact_quality,
                "source_state_sha256": str(state["state_sha256"]),
            }
            effects.append(effect)

    next_state["vessels"] = [
        next_vessels[ship_id] for ship_id in sorted(next_vessels)
    ]
    next_state["phase6_source_identity"] = source_identity
    next_state["last_observation_state_sha256"] = observation[
        "observation_state_sha256"
    ]
    next_state["state_sha256"] = _movement_hash_without_field(
        next_state, "state_sha256"
    )

    fire_control = {
        "schema": "aurora://simulation/gumas/phase6_fire_control_state/v1.0",
        "source_state_sha256": str(state["state_sha256"]),
        "observation_state_sha256": observation["observation_state_sha256"],
        "selections": sorted(
            selections, key=lambda item: item["shooter_ship_id"]
        ),
        "weapon_attempts": sorted(
            attempts,
            key=lambda item: (
                item["shooter_ship_id"],
                item.get("target_ship_id") or "",
            ),
        ),
        "effect_descriptors": sorted(effects, key=lambda item: item["effect_id"]),
    }
    fire_control["fire_control_state_sha256"] = _hash_without_field(
        fire_control, "fire_control_state_sha256"
    )
    receipt = {
        "schema": "aurora://simulation/gumas/phase6_step_receipt/v1.0",
        "phase6_contract_id": PHASE6_CONTRACT_ID,
        "phase6_version": PHASE6_VERSION,
        "phase6_source_identity": source_identity,
        "prior_state_sha256": str(state["state_sha256"]),
        "next_state_sha256": next_state["state_sha256"],
        "macrostep_index": int(state["macrostep_index"]),
        "elapsed_ms": int(state["elapsed_ms"]),
        "observation_state_sha256": observation["observation_state_sha256"],
        "fire_control_state_sha256": fire_control[
            "fire_control_state_sha256"
        ],
        "command_decision_sha256_by_fleet": {
            fleet: commands[fleet]["decision_sha256"]
            for fleet in sorted(commands)
        },
        "contacts": observation["contacts"],
        "selections": fire_control["selections"],
        "weapon_attempts": fire_control["weapon_attempts"],
        "effect_descriptors": fire_control["effect_descriptors"],
        "deterministic_child_draw_used": any(
            item.get("fired") for item in attempts
        ),
        "ambient_rng_used": False,
        "floating_authority_used": False,
        "damage_applied": False,
    }
    receipt["phase6_receipt_sha256"] = _hash_without_field(
        receipt, "phase6_receipt_sha256"
    )
    return next_state, receipt
