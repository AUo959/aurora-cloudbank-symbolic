"""Authoritative public boundary for deterministic GUMAS Phase-8 resolution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from simulation.runtime.gumas_damage_disposition import kernel as phase7_kernel
from simulation.runtime.gumas_damage_disposition.normalization import normalizer_source_identity
from simulation.runtime.gumas_movement_geometry.constants import (
    MAX_RUN_DURATION_MS,
    P17_WITHDRAWAL_RADIUS_UM,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as movement_hash_without_field,
)

from . import kernel as _kernel
from .constants import HARD_LIMIT_MS, PHYSICAL_DISPOSITIONS if False else HARD_LIMIT_MS
from .constants import WITHDRAWAL_BOUNDARY_UM

Phase8Error = _kernel.Phase8Error
_raw_step_phase8_state = _kernel.step_phase8_state


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def boundary_source_identity() -> dict[str, Any]:
    directory = Path(__file__).resolve().parent
    modules: dict[str, str] = {}
    bundle = hashlib.sha256()
    for name in ("boundary.py", "__init__.py"):
        data = (directory / name).read_bytes()
        modules[name] = hashlib.sha256(data).hexdigest()
        bundle.update(name.encode("ascii"))
        bundle.update(b"\0")
        bundle.update(data)
        bundle.update(b"\0")
    return {"module_sha256": modules, "bundle_sha256": bundle.hexdigest()}


def _phase7_composite_source_sha256() -> str:
    payload = {
        "damage_core_source_identity": phase7_kernel._source_identity(),
        "semantic_normalizer_source_identity": normalizer_source_identity(),
    }
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _validate_frozen_constants() -> None:
    if HARD_LIMIT_MS != MAX_RUN_DURATION_MS:
        raise Phase8Error("Phase-8 hard limit diverges from accepted movement authority")
    if WITHDRAWAL_BOUNDARY_UM != P17_WITHDRAWAL_RADIUS_UM:
        raise Phase8Error("Phase-8 withdrawal boundary diverges from accepted movement authority")


def _validate_phase7_state_provenance(state: Mapping[str, Any]) -> None:
    if dict(state.get("phase7_source_identity") or {}) != phase7_kernel._source_identity():
        raise Phase8Error("Phase-7 state damage-core identity mismatch")
    if dict(state.get("phase7_semantic_normalizer_source_identity") or {}) != normalizer_source_identity():
        raise Phase8Error("Phase-7 state semantic-normalizer identity mismatch")
    if str(state.get("phase7_composite_source_sha256") or "") != _phase7_composite_source_sha256():
        raise Phase8Error("Phase-7 state composite identity mismatch")


def _validate_authoritative_state_shape(
    state: Mapping[str, Any], phase7_receipt: Mapping[str, Any]
) -> None:
    vessels = state.get("vessels")
    if not isinstance(vessels, Sequence) or isinstance(vessels, (str, bytes)):
        raise Phase8Error("state.vessels must be a sequence")
    ship_ids: set[str] = set()
    for raw in vessels:
        if not isinstance(raw, Mapping):
            raise Phase8Error("vessel must be a mapping")
        ship_id = str(raw.get("ship_id") or "")
        if not ship_id or ship_id in ship_ids:
            raise Phase8Error(f"invalid or duplicate vessel id: {ship_id}")
        ship_ids.add(ship_id)
        if str(raw.get("disposition") or "") not in {
            "combat_capable",
            "degraded",
            "disabled",
            "destroyed",
        }:
            raise Phase8Error(f"unknown physical disposition: {ship_id}")
        physical = raw.get("physical")
        if not isinstance(physical, Mapping):
            raise Phase8Error(f"{ship_id}.physical missing")
        hull_max = physical.get("hull_integrity_milliunits")
        if isinstance(hull_max, bool) or not isinstance(hull_max, int) or hull_max <= 0:
            raise Phase8Error(f"{ship_id}.hull_integrity_milliunits must be positive integer")

    effect_count = phase7_receipt.get("effect_count")
    if isinstance(effect_count, bool) or not isinstance(effect_count, int) or effect_count < 0:
        raise Phase8Error("Phase-7 effect_count must be a non-negative integer")
    target_receipts = phase7_receipt.get("target_damage_receipts")
    if not isinstance(target_receipts, Sequence) or isinstance(target_receipts, (str, bytes)):
        raise Phase8Error("Phase-7 target_damage_receipts must be a sequence")
    seen_targets: set[str] = set()
    for target_receipt in target_receipts:
        if not isinstance(target_receipt, Mapping):
            raise Phase8Error("Phase-7 target damage receipt must be a mapping")
        target_id = str(target_receipt.get("target_ship_id") or "")
        if target_id not in ship_ids or target_id in seen_targets:
            raise Phase8Error(f"invalid/duplicate Phase-7 damage target: {target_id}")
        seen_targets.add(target_id)


def _validate_command_authority(
    command_receipts_by_fleet: Mapping[str, Any], baseline: Mapping[str, Any]
) -> None:
    sides = baseline.get("sides")
    if not isinstance(sides, Mapping):
        raise Phase8Error("baseline.sides missing")
    expected_fleets = {str(side["fleet_id"]) for side in sides.values()}
    if set(command_receipts_by_fleet) != expected_fleets:
        raise Phase8Error("command receipt fleet set differs from frozen baseline")
    for fleet_id in sorted(expected_fleets):
        receipt = command_receipts_by_fleet[fleet_id]
        if not isinstance(receipt, Mapping):
            raise Phase8Error(f"invalid command receipt for {fleet_id}")
        if receipt.get("prose_inputs_used") is not False:
            raise Phase8Error(f"command receipt used prose authority: {fleet_id}")
        if receipt.get("rng_used") is not False:
            raise Phase8Error(f"command receipt used RNG authority: {fleet_id}")


def _validate_prior_resolution(
    prior_resolution_state: Mapping[str, Any] | None,
    baseline: Mapping[str, Any],
) -> None:
    if prior_resolution_state is None:
        return
    if not isinstance(prior_resolution_state, Mapping):
        raise Phase8Error("prior Phase-8 resolution state must be a mapping")
    expected_boundary = boundary_source_identity()
    if dict(prior_resolution_state.get("phase8_boundary_source_identity") or {}) != expected_boundary:
        raise Phase8Error("prior Phase-8 boundary identity mismatch")
    expected_composite = _sha256(
        {
            "resolution_core_source_identity": _kernel._source_identity(),
            "phase8_boundary_source_identity": expected_boundary,
        }
    )
    if str(prior_resolution_state.get("phase8_composite_source_sha256") or "") != expected_composite:
        raise Phase8Error("prior Phase-8 composite identity mismatch")
    sides = set(str(side) for side in (baseline.get("sides") or {}))
    offer_map = prior_resolution_state.get("ceasefire_offer_expiry_macrostep_by_side") or {}
    if not isinstance(offer_map, Mapping) or set(offer_map) != sides:
        raise Phase8Error("prior ceasefire-offer side set mismatch")
    streak = prior_resolution_state.get("mutual_disengage_streak")
    if isinstance(streak, bool) or not isinstance(streak, int) or streak < 0:
        raise Phase8Error("prior mutual-disengagement streak must be non-negative integer")


def step_phase8_state(
    state: Mapping[str, Any],
    phase7_receipt: Mapping[str, Any],
    command_receipts_by_fleet: Mapping[str, Any],
    baseline: Mapping[str, Any],
    prior_resolution_state: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Validate the public boundary, run the Phase-8 core, and bind boundary provenance."""
    _validate_frozen_constants()
    _validate_phase7_state_provenance(state)
    _validate_authoritative_state_shape(state, phase7_receipt)
    _validate_command_authority(command_receipts_by_fleet, baseline)
    _validate_prior_resolution(prior_resolution_state, baseline)

    next_state, resolution_state, receipt = _raw_step_phase8_state(
        state,
        phase7_receipt,
        command_receipts_by_fleet,
        baseline,
        prior_resolution_state,
    )

    boundary_identity = boundary_source_identity()
    composite_sha = _sha256(
        {
            "resolution_core_source_identity": receipt["phase8_source_identity"],
            "phase8_boundary_source_identity": boundary_identity,
        }
    )

    resolution_state["phase8_boundary_source_identity"] = boundary_identity
    resolution_state["phase8_composite_source_sha256"] = composite_sha
    resolution_state["resolution_state_sha256"] = _kernel._hash_without_field(
        resolution_state, "resolution_state_sha256"
    )

    next_state["phase8_boundary_source_identity"] = boundary_identity
    next_state["phase8_composite_source_sha256"] = composite_sha
    next_state["last_phase8_resolution_state_sha256"] = resolution_state[
        "resolution_state_sha256"
    ]
    next_state["state_sha256"] = movement_hash_without_field(
        next_state, "state_sha256"
    )

    receipt["phase8_boundary_source_identity"] = boundary_identity
    receipt["phase8_composite_source_sha256"] = composite_sha
    receipt["resolution_state_sha256"] = resolution_state[
        "resolution_state_sha256"
    ]
    receipt["next_state_sha256"] = next_state["state_sha256"]
    receipt["phase8_public_boundary_validated"] = True
    receipt["phase8_receipt_sha256"] = _kernel._hash_without_field(
        receipt, "phase8_receipt_sha256"
    )
    return next_state, resolution_state, receipt
