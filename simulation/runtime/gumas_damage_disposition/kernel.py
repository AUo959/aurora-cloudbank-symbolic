"""Deterministic Phase-7 shield, armor, hull, readiness, and disposition transformer."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from simulation.runtime.gumas_movement_geometry.geometry import round_half_even_fraction
from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as _movement_hash_without_field,
)
from simulation.runtime.gumas_sensing_weapons.kernel import (
    _hash_without_field as _phase6_hash_without_field,
    _source_identity as _phase6_source_identity,
    sha256_canonical,
)

from .constants import (
    ARMOR_ABSORPTION_EFFICIENCY_Q1000,
    CANONICAL_JSON_PROFILE,
    DAMAGE_CONTROL_MAX_MITIGATION_Q1000,
    PHASE7_CONTRACT_ID,
    PHASE7_VERSION,
    PROTECTED_PRIOR_DISPOSITIONS,
    READINESS_FIELDS,
    READINESS_SHOCK_WEIGHTS_Q1000,
)


class Phase7Error(RuntimeError):
    """Raised when Phase-7 input cannot be resolved under the pinned contract."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _hash_without_field(value: Mapping[str, Any], field: str) -> str:
    return hashlib.sha256(
        canonical_json_bytes({key: item for key, item in value.items() if key != field})
    ).hexdigest()


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


def _require_int(value: Any, label: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Phase7Error(f"{label} must be an integer")
    result = int(value)
    if minimum is not None and result < minimum:
        raise Phase7Error(f"{label} below minimum {minimum}: {result}")
    return result


def _require_q1000(value: Any, label: str) -> int:
    result = _require_int(value, label)
    if not 0 <= result <= 1000:
        raise Phase7Error(f"{label} outside q1000 bounds: {result}")
    return result


def _ceil_fraction(numerator: int, denominator: int) -> int:
    if numerator < 0 or denominator <= 0:
        raise Phase7Error("invalid integer ceiling operands")
    return (numerator + denominator - 1) // denominator


def _fraction_q1000(current: int, maximum: int, label: str) -> int:
    if maximum <= 0 or current < 0 or current > maximum:
        raise Phase7Error(f"invalid capacity state for {label}: {current}/{maximum}")
    return max(0, min(1000, round_half_even_fraction(current * 1000, maximum)))


def _verify_phase6_inputs(
    state: Mapping[str, Any], phase6_receipt: Mapping[str, Any]
) -> None:
    recorded_state = str(state.get("state_sha256") or "")
    actual_state = _movement_hash_without_field(state, "state_sha256")
    if not recorded_state or recorded_state != actual_state:
        raise Phase7Error("Phase-6 next-state hash mismatch")

    recorded_receipt = str(phase6_receipt.get("phase6_receipt_sha256") or "")
    actual_receipt = _phase6_hash_without_field(
        phase6_receipt, "phase6_receipt_sha256"
    )
    if not recorded_receipt or recorded_receipt != actual_receipt:
        raise Phase7Error("Phase-6 receipt hash mismatch")

    if str(phase6_receipt.get("next_state_sha256") or "") != recorded_state:
        raise Phase7Error("Phase-6 receipt does not bind supplied current state")

    supplied_identity = phase6_receipt.get("phase6_source_identity")
    if not isinstance(supplied_identity, Mapping):
        raise Phase7Error("Phase-6 receipt missing source identity")
    if dict(supplied_identity) != _phase6_source_identity():
        raise Phase7Error("Phase-6 source identity mismatch")
    if phase6_receipt.get("damage_applied") is not False:
        raise Phase7Error("Phase-6 receipt unexpectedly claims damage application")
    if not str(phase6_receipt.get("fire_control_state_sha256") or ""):
        raise Phase7Error("Phase-6 receipt missing fire-control identity")


def _phase6_semantic_receipt_sha256(
    phase6_receipt: Mapping[str, Any],
) -> str:
    """Hash validated Phase-6 semantics independent of effect-list insertion order.

    The raw Phase-6 receipt hash is still verified before this helper is used.
    Phase 7 consumes the effect descriptors as a simultaneous set, so carrying
    the raw serialization-sensitive receipt hash into Phase-7 state would make
    equivalent effect sets produce different authoritative state hashes.
    """
    normalized = copy.deepcopy(dict(phase6_receipt))
    normalized.pop("phase6_receipt_sha256", None)
    effects = normalized.get("effect_descriptors")
    if not isinstance(effects, Sequence) or isinstance(effects, (str, bytes)):
        raise Phase7Error("Phase-6 effect_descriptors must be a sequence")
    normalized["effect_descriptors"] = sorted(
        (dict(item) for item in effects),
        key=lambda item: str(item.get("effect_id") or ""),
    )
    return sha256_canonical(normalized)


def _vessel_lookup(state: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    vessels = state.get("vessels")
    if not isinstance(vessels, Sequence) or isinstance(vessels, (str, bytes)):
        raise Phase7Error("state.vessels must be a sequence")
    lookup: dict[str, Mapping[str, Any]] = {}
    for vessel in vessels:
        if not isinstance(vessel, Mapping):
            raise Phase7Error("vessel must be a mapping")
        ship_id = str(vessel.get("ship_id") or "")
        if not ship_id or ship_id in lookup:
            raise Phase7Error(f"invalid or duplicate vessel id: {ship_id}")
        lookup[ship_id] = vessel
    return lookup


def _validate_material(vessel: Mapping[str, Any]) -> dict[str, int]:
    ship_id = str(vessel["ship_id"])
    physical = vessel.get("physical")
    if not isinstance(physical, Mapping):
        raise Phase7Error(f"{ship_id}.physical missing")
    values = {
        "shield_max": _require_int(
            physical.get("shield_capacity_milliunits"),
            f"{ship_id}.shield_capacity",
            minimum=1,
        ),
        "shield_current": _require_int(
            physical.get("shield_current_milliunits"),
            f"{ship_id}.shield_current",
            minimum=0,
        ),
        "armor_max": _require_int(
            physical.get("armor_integrity_milliunits"),
            f"{ship_id}.armor_integrity",
            minimum=1,
        ),
        "armor_current": _require_int(
            physical.get("armor_current_milliunits"),
            f"{ship_id}.armor_current",
            minimum=0,
        ),
        "hull_max": _require_int(
            physical.get("hull_integrity_milliunits"),
            f"{ship_id}.hull_integrity",
            minimum=1,
        ),
        "hull_current": _require_int(
            physical.get("hull_current_milliunits"),
            f"{ship_id}.hull_current",
            minimum=0,
        ),
    }
    for layer in ("shield", "armor", "hull"):
        if values[f"{layer}_current"] > values[f"{layer}_max"]:
            raise Phase7Error(f"{ship_id}.{layer} current exceeds maximum")
    readiness = vessel.get("readiness_q1000")
    if not isinstance(readiness, Mapping):
        raise Phase7Error(f"{ship_id}.readiness_q1000 missing")
    for field in READINESS_FIELDS:
        _require_q1000(readiness.get(field), f"{ship_id}.readiness.{field}")
    _require_q1000(vessel.get("morale_q1000"), f"{ship_id}.morale_q1000")
    _require_q1000(vessel.get("cohesion_q1000"), f"{ship_id}.cohesion_q1000")
    return values


def _validate_effects(
    phase6_receipt: Mapping[str, Any],
    vessels: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    effects = phase6_receipt.get("effect_descriptors")
    if not isinstance(effects, Sequence) or isinstance(effects, (str, bytes)):
        raise Phase7Error("Phase-6 effect_descriptors must be a sequence")
    prior_state_sha = str(phase6_receipt.get("prior_state_sha256") or "")
    if not prior_state_sha:
        raise Phase7Error("Phase-6 receipt missing prior state identity")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for raw in effects:
        if not isinstance(raw, Mapping):
            raise Phase7Error("effect descriptor must be a mapping")
        effect = dict(raw)
        effect_id = str(effect.get("effect_id") or "")
        attempt_id = str(effect.get("attempt_id") or "")
        source_id = str(effect.get("source_ship_id") or "")
        target_id = str(effect.get("target_ship_id") or "")
        if not effect_id or effect_id in seen:
            raise Phase7Error(f"missing or duplicate effect_id: {effect_id}")
        seen.add(effect_id)
        if not attempt_id or not source_id or not target_id:
            raise Phase7Error(f"incomplete effect descriptor: {effect_id}")
        if source_id not in vessels:
            raise Phase7Error(f"effect source absent from current state: {source_id}")
        if target_id not in vessels:
            raise Phase7Error(f"effect target absent from current state: {target_id}")
        if str(vessels[target_id].get("disposition") or "") in PROTECTED_PRIOR_DISPOSITIONS:
            raise Phase7Error(f"effect targets already destroyed vessel: {target_id}")
        delivered = _require_int(
            effect.get("delivered_effect_milliunits"),
            f"{effect_id}.delivered_effect_milliunits",
            minimum=1,
        )
        _require_q1000(
            effect.get("impact_quality_q1000"), f"{effect_id}.impact_quality_q1000"
        )
        if str(effect.get("source_state_sha256") or "") != prior_state_sha:
            raise Phase7Error(f"effect source-state mismatch: {effect_id}")
        expected_effect_id = sha256_canonical(
            {
                "attempt_id": attempt_id,
                "delivered_effect_milliunits": delivered,
            }
        )
        if effect_id != expected_effect_id:
            raise Phase7Error(f"effect identity mismatch: {effect_id}")
        normalized.append(effect)
    return sorted(normalized, key=lambda item: str(item["effect_id"]))


def _classify_damage(
    *,
    shield_current: int,
    shield_max: int,
    armor_current: int,
    armor_max: int,
    hull_current: int,
    hull_max: int,
) -> str:
    hull_fraction = _fraction_q1000(hull_current, hull_max, "hull")
    if hull_current == 0:
        return "destroyed"
    if hull_fraction <= 300:
        return "critical_damage"
    if hull_fraction <= 600:
        return "major_damage"
    if hull_current < hull_max:
        return "hull_damaged"
    if armor_current < armor_max:
        return "armor_damaged"
    if shield_current < shield_max:
        return "shield_damaged"
    return "undamaged"


def _classify_disposition(
    hull_current: int,
    hull_max: int,
    readiness: Mapping[str, Any],
) -> str:
    hull_fraction = _fraction_q1000(hull_current, hull_max, "hull")
    ready = {
        field: _require_q1000(readiness.get(field), f"readiness.{field}")
        for field in READINESS_FIELDS
    }
    if hull_current == 0:
        return "destroyed"
    if (
        hull_fraction <= 150
        or ready["overall"] < 150
        or (ready["propulsion"] < 150 and ready["weapons"] < 150)
    ):
        return "disabled"
    if (
        hull_fraction < 600
        or ready["propulsion"] < 500
        or ready["weapons"] < 500
        or ready["sensors"] < 500
        or ready["ew"] < 500
        or ready["damage_control"] < 500
    ):
        return "degraded"
    return "combat_capable"


def _readiness_after_hull_loss(
    prior: Mapping[str, Any],
    new_hull_loss_q1000: int,
) -> tuple[dict[str, int], dict[str, int], int]:
    prior_ready = {
        field: _require_q1000(prior.get(field), f"readiness.{field}")
        for field in READINESS_FIELDS
    }
    mitigation = round_half_even_fraction(
        prior_ready["damage_control"] * DAMAGE_CONTROL_MAX_MITIGATION_Q1000,
        1000,
    )
    effective_shock = round_half_even_fraction(
        new_hull_loss_q1000 * (1000 - mitigation), 1000
    )
    delta: dict[str, int] = {}
    after: dict[str, int] = {}
    for field in READINESS_FIELDS:
        loss = round_half_even_fraction(
            effective_shock * READINESS_SHOCK_WEIGHTS_Q1000[field], 1000
        )
        delta[field] = -loss
        after[field] = max(0, prior_ready[field] - loss)
    return after, delta, effective_shock


def _apply_target_damage(
    vessel: Mapping[str, Any],
    effects: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    before = copy.deepcopy(dict(vessel))
    material = _validate_material(before)
    incoming = sum(int(item["delivered_effect_milliunits"]) for item in effects)

    shield_absorbed = min(incoming, material["shield_current"])
    shield_after = material["shield_current"] - shield_absorbed
    residual = incoming - shield_absorbed

    armor_effect_capacity = round_half_even_fraction(
        material["armor_current"] * ARMOR_ABSORPTION_EFFICIENCY_Q1000, 1000
    )
    armor_absorbed = min(residual, armor_effect_capacity)
    armor_integrity_loss = min(
        material["armor_current"],
        _ceil_fraction(
            armor_absorbed * 1000, ARMOR_ABSORPTION_EFFICIENCY_Q1000
        )
        if armor_absorbed
        else 0,
    )
    armor_after = material["armor_current"] - armor_integrity_loss
    residual_after_armor = residual - armor_absorbed

    hull_loss = min(residual_after_armor, material["hull_current"])
    hull_after = material["hull_current"] - hull_loss
    overkill = residual_after_armor - hull_loss
    new_hull_loss_q1000 = round_half_even_fraction(
        hull_loss * 1000, material["hull_max"]
    )

    readiness_before = copy.deepcopy(dict(before["readiness_q1000"]))
    if hull_loss:
        readiness_after, readiness_delta, effective_shock = _readiness_after_hull_loss(
            readiness_before, new_hull_loss_q1000
        )
    else:
        readiness_after = copy.deepcopy(readiness_before)
        readiness_delta = {field: 0 for field in READINESS_FIELDS}
        effective_shock = 0

    after = copy.deepcopy(before)
    after["physical"]["shield_current_milliunits"] = shield_after
    after["physical"]["armor_current_milliunits"] = armor_after
    after["physical"]["hull_current_milliunits"] = hull_after
    after["readiness_q1000"] = dict(sorted(readiness_after.items()))
    after["damage_state"] = _classify_damage(
        shield_current=shield_after,
        shield_max=material["shield_max"],
        armor_current=armor_after,
        armor_max=material["armor_max"],
        hull_current=hull_after,
        hull_max=material["hull_max"],
    )
    after["disposition"] = _classify_disposition(
        hull_after, material["hull_max"], after["readiness_q1000"]
    )

    if after["morale_q1000"] != before["morale_q1000"]:
        raise Phase7Error("Phase 7 mutated morale")
    if after["cohesion_q1000"] != before["cohesion_q1000"]:
        raise Phase7Error("Phase 7 mutated cohesion")

    receipt: dict[str, Any] = {
        "target_ship_id": str(before["ship_id"]),
        "effect_ids": [str(item["effect_id"]) for item in effects],
        "total_incoming_effect_milliunits": incoming,
        "shield": {
            "before": material["shield_current"],
            "absorbed": shield_absorbed,
            "after": shield_after,
            "fraction_before_q1000": _fraction_q1000(
                material["shield_current"], material["shield_max"], "shield"
            ),
            "fraction_after_q1000": _fraction_q1000(
                shield_after, material["shield_max"], "shield"
            ),
        },
        "armor": {
            "before": material["armor_current"],
            "effect_capacity": armor_effect_capacity,
            "effect_absorbed": armor_absorbed,
            "integrity_lost": armor_integrity_loss,
            "after": armor_after,
            "fraction_before_q1000": _fraction_q1000(
                material["armor_current"], material["armor_max"], "armor"
            ),
            "fraction_after_q1000": _fraction_q1000(
                armor_after, material["armor_max"], "armor"
            ),
        },
        "hull": {
            "before": material["hull_current"],
            "lost": hull_loss,
            "after": hull_after,
            "overkill": overkill,
            "new_hull_loss_q1000": new_hull_loss_q1000,
            "fraction_before_q1000": _fraction_q1000(
                material["hull_current"], material["hull_max"], "hull"
            ),
            "fraction_after_q1000": _fraction_q1000(
                hull_after, material["hull_max"], "hull"
            ),
        },
        "readiness": {
            "before": dict(sorted(readiness_before.items())),
            "delta": dict(sorted(readiness_delta.items())),
            "after": dict(sorted(readiness_after.items())),
            "effective_shock_q1000": effective_shock,
        },
        "damage_state": {
            "before": str(before.get("damage_state") or ""),
            "after": str(after["damage_state"]),
        },
        "physical_disposition": {
            "before": str(before.get("disposition") or ""),
            "after": str(after["disposition"]),
        },
        "morale_q1000": {
            "before": int(before["morale_q1000"]),
            "after": int(after["morale_q1000"]),
            "unchanged": True,
        },
        "cohesion_q1000": {
            "before": int(before["cohesion_q1000"]),
            "after": int(after["cohesion_q1000"]),
            "unchanged": True,
        },
    }
    receipt["target_damage_receipt_sha256"] = _hash_without_field(
        receipt, "target_damage_receipt_sha256"
    )
    return after, receipt


def step_phase7_state(
    state: Mapping[str, Any],
    phase6_receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply one deterministic Phase-7 damage transition."""
    _verify_phase6_inputs(state, phase6_receipt)
    vessels_by_id = _vessel_lookup(state)
    for vessel in vessels_by_id.values():
        _validate_material(vessel)
    effects = _validate_effects(phase6_receipt, vessels_by_id)
    phase6_semantic_receipt_sha256 = _phase6_semantic_receipt_sha256(phase6_receipt)

    grouped: dict[str, list[dict[str, Any]]] = {}
    for effect in effects:
        grouped.setdefault(str(effect["target_ship_id"]), []).append(effect)
    for target_id in grouped:
        grouped[target_id].sort(key=lambda item: str(item["effect_id"]))

    next_state = copy.deepcopy(dict(state))
    next_state.pop("state_sha256", None)
    next_state["parent_state_sha256"] = str(state["state_sha256"])
    next_vessels = {
        str(item["ship_id"]): copy.deepcopy(item) for item in next_state["vessels"]
    }

    target_receipts: list[dict[str, Any]] = []
    for target_id in sorted(grouped):
        updated, target_receipt = _apply_target_damage(
            next_vessels[target_id], grouped[target_id]
        )
        next_vessels[target_id] = updated
        target_receipts.append(target_receipt)

    next_state["vessels"] = [next_vessels[key] for key in sorted(next_vessels)]
    source_identity = _source_identity()
    damage_ledger = {
        "schema": "aurora://simulation/gumas/phase7_damage_ledger/v1.0",
        "phase7_contract_id": PHASE7_CONTRACT_ID,
        "phase7_version": PHASE7_VERSION,
        "phase7_source_identity": source_identity,
        "prior_state_sha256": str(state["state_sha256"]),
        "phase6_semantic_receipt_sha256": phase6_semantic_receipt_sha256,
        "fire_control_state_sha256": str(phase6_receipt["fire_control_state_sha256"]),
        "target_damage_receipts": target_receipts,
    }
    damage_ledger["damage_ledger_sha256"] = _hash_without_field(
        damage_ledger, "damage_ledger_sha256"
    )

    next_state["phase7_source_identity"] = source_identity
    next_state["last_phase6_semantic_receipt_sha256"] = phase6_semantic_receipt_sha256
    next_state["last_damage_ledger_sha256"] = damage_ledger["damage_ledger_sha256"]
    next_state["state_sha256"] = _movement_hash_without_field(
        next_state, "state_sha256"
    )

    receipt: dict[str, Any] = {
        "schema": "aurora://simulation/gumas/phase7_step_receipt/v1.0",
        "phase7_contract_id": PHASE7_CONTRACT_ID,
        "phase7_version": PHASE7_VERSION,
        "phase7_source_identity": source_identity,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "prior_state_sha256": str(state["state_sha256"]),
        "phase6_semantic_receipt_sha256": phase6_semantic_receipt_sha256,
        "phase6_raw_receipt_validated": True,
        "fire_control_state_sha256": str(phase6_receipt["fire_control_state_sha256"]),
        "next_state_sha256": str(next_state["state_sha256"]),
        "macrostep_index": int(state["macrostep_index"]),
        "elapsed_ms": int(state["elapsed_ms"]),
        "effect_count": len(effects),
        "affected_target_count": len(target_receipts),
        "damage_ledger_sha256": damage_ledger["damage_ledger_sha256"],
        "target_damage_receipts": target_receipts,
        "morale_mutated": False,
        "cohesion_mutated": False,
        "termination_decision_made": False,
        "ambient_rng_used": False,
        "floating_authority_used": False,
    }
    receipt["phase7_receipt_sha256"] = _hash_without_field(
        receipt, "phase7_receipt_sha256"
    )
    return next_state, receipt
