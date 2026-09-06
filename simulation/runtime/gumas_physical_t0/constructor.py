"""Deterministic Phase-3 T0 physical-state construction for GUMAS.

This module instantiates state only. It does not resolve movement, command,
combat, damage, withdrawal, surrender, or any battle outcome.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from simulation.runtime.canonrec_tactical.resolver import (
    canonical_json_bytes,
    normalize_seed64,
    sha256_json,
)

CONSTRUCTOR_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0"
CANONICAL_JSON_PROFILE = "aurora-canonical-json-v1"
ATTITUDE_SCALE = 1_000_000_000_000
HISTORICAL_SOURCE_TREE_SHA256 = (
    "a218541009b0a870eb3558f09d3a497ff31673143a47b6ce1191715fc9617ed9"
)
RESTORATION_SOURCE_GIT_BLOB_SHA1 = "371c2025773b47904a7a2a0c16a69ba1bea76414"
CANONREC_RESOLVER_SOURCE_GIT_BLOB_SHA1 = "9eebd574ab1669331227bf854396acb1cffe56b5"


class T0ConstructionError(RuntimeError):
    """Raised when deterministic T0 state cannot be constructed safely."""


def _round_half_even_fraction(numerator: int, denominator: int) -> int:
    """Round a non-negative rational to the nearest integer, ties to even."""
    if denominator <= 0:
        raise T0ConstructionError("Rounding denominator must be positive")
    if numerator < 0:
        return -_round_half_even_fraction(-numerator, denominator)
    quotient, remainder = divmod(numerator, denominator)
    doubled = remainder * 2
    if doubled < denominator:
        return quotient
    if doubled > denominator:
        return quotient + 1
    return quotient if quotient % 2 == 0 else quotient + 1


def _decimal_to_scaled_int(value: Any, scale: int) -> int:
    """Convert decimal-text-compatible input to a fixed-point integer."""
    if isinstance(value, bool):
        raise T0ConstructionError("Boolean is not a numeric state value")
    decimal_value = Decimal(str(value))
    if not decimal_value.is_finite():
        raise T0ConstructionError(f"Non-finite numeric input: {value!r}")
    return int(
        (decimal_value * Decimal(scale)).quantize(
            Decimal("1"), rounding=ROUND_HALF_EVEN
        )
    )


def _normalize_q12(vector: Sequence[int]) -> List[int]:
    if len(vector) != 3:
        raise T0ConstructionError("Attitude vectors must have exactly 3 axes")
    with localcontext() as context:
        context.prec = 80
        components = [Decimal(int(value)) for value in vector]
        norm_squared = sum(value * value for value in components)
        if norm_squared == 0:
            raise T0ConstructionError("Cannot normalize zero-length attitude vector")
        norm = context.sqrt(norm_squared)
        return [
            int(
                ((value * Decimal(ATTITUDE_SCALE)) / norm).quantize(
                    Decimal("1"), rounding=ROUND_HALF_EVEN
                )
            )
            for value in components
        ]


def _vector_subtract(left: Sequence[int], right: Sequence[int]) -> List[int]:
    return [int(left[i]) - int(right[i]) for i in range(3)]


def _vector_add(left: Sequence[int], right: Sequence[int]) -> List[int]:
    return [int(left[i]) + int(right[i]) for i in range(3)]


def _vector_negate(vector: Sequence[int]) -> List[int]:
    return [-int(value) for value in vector]


def _vector_sum(vectors: Iterable[Sequence[int]]) -> List[int]:
    total = [0, 0, 0]
    for vector in vectors:
        for index in range(3):
            total[index] += int(vector[index])
    return total


def _attitude_up_q12(
    forward_q12: Sequence[int], calibration: Mapping[str, Any]
) -> List[int]:
    spin_axis = list(calibration["planetoid_rotation_completion"]["spin_axis_q12"])
    if (
        int(forward_q12[0]) == 0
        and int(forward_q12[1]) == 0
        and abs(int(forward_q12[2])) == ATTITUDE_SCALE
    ):
        return list(calibration["attitude"]["parallel_fallback_up_q12"])
    return spin_axis


def _inside_triaxial_ellipsoid(
    position_m: Sequence[int], semi_axes_m: Sequence[int]
) -> bool:
    """Exact integer membership test for axis-aligned triaxial ellipsoid."""
    x, y, z = (int(value) for value in position_m)
    a, b, c = (int(value) for value in semi_axes_m)
    if min(a, b, c) <= 0:
        raise T0ConstructionError("Planetoid semi-axes must be positive")
    lhs = (
        x * x * b * b * c * c
        + y * y * a * a * c * c
        + z * z * a * a * b * b
    )
    rhs = a * a * b * b * c * c
    return lhs <= rhs


def _load_json(source: str | Path | Mapping[str, Any]) -> Dict[str, Any]:
    if isinstance(source, Mapping):
        return dict(source)
    return json.loads(Path(source).read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_payload_for_hash(manifest: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "manifest_sha256"}


def _validate_manifest(manifest: Mapping[str, Any], calibration: Mapping[str, Any]) -> None:
    expected_profile = calibration["numeric_policy"]["canonical_json_profile"]
    if manifest.get("canonical_json_profile") != expected_profile:
        raise T0ConstructionError("CanonRec canonical JSON profile mismatch")
    actual_hash = sha256_json(_manifest_payload_for_hash(manifest))
    recorded_hash = str(manifest.get("manifest_sha256") or "")
    if actual_hash != recorded_hash:
        raise T0ConstructionError(
            f"Resolved manifest hash mismatch: {actual_hash} != {recorded_hash}"
        )
    expected_hash = str(
        calibration["authority_boundary"].get("control_manifest_sha256") or ""
    )
    if expected_hash and recorded_hash != expected_hash:
        raise T0ConstructionError(
            f"Resolved manifest is not the accepted control manifest: "
            f"{recorded_hash} != {expected_hash}"
        )
    authority = manifest.get("authority", {})
    expected_org = calibration["identity_mapping"]["organization_id"]
    if authority.get("authority_id") != expected_org:
        raise T0ConstructionError(
            f"Authority mismatch: {authority.get('authority_id')} != {expected_org}"
        )


def _capability_lookup(manifest: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for entry in manifest.get("roster", []):
        class_id = str(entry.get("class_id") or "")
        if not class_id or class_id in lookup:
            raise T0ConstructionError(f"Invalid or duplicate manifest class: {class_id}")
        resolved = entry.get("resolved")
        if not isinstance(resolved, Mapping):
            raise T0ConstructionError(f"Missing resolved class payload: {class_id}")
        values = resolved.get("capability_vector", {}).get("values", {})
        if not isinstance(values, Mapping):
            raise T0ConstructionError(f"Missing capability vector: {class_id}")
        normalized: Dict[str, int] = {}
        for key, value in values.items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise T0ConstructionError(
                    f"Capability {class_id}.{key} is not an integer: {value!r}"
                )
            if not 0 <= value <= 1000:
                raise T0ConstructionError(
                    f"Capability {class_id}.{key} outside q1000 bounds: {value}"
                )
            normalized[str(key)] = int(value)
        lookup[class_id] = {
            "values": normalized,
            "resolution_sha256": str(resolved.get("resolution_sha256") or ""),
            "count": int(entry.get("count", 0)),
        }
    return lookup


def _require_capability(values: Mapping[str, int], key: str) -> int:
    try:
        value = int(values[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise T0ConstructionError(f"Required capability missing: {key}") from exc
    if not 0 <= value <= 1000:
        raise T0ConstructionError(f"Capability {key} outside q1000 bounds: {value}")
    return value


def _calibrate_physical(
    capability_values: Mapping[str, int], calibration: Mapping[str, Any]
) -> Tuple[Dict[str, int], Dict[str, int]]:
    physical: Dict[str, int] = {}
    equations = calibration["physical_equations"]
    for output_key, rule in sorted(equations.items()):
        base = int(rule["base"])
        span = int(rule["span"])
        if "source_capability" in rule:
            capability = _require_capability(
                capability_values, str(rule["source_capability"])
            )
            delta = _round_half_even_fraction(span * capability, 1000)
        else:
            sources = rule.get("source_capabilities", {})
            denominator = int(rule["weight_denominator"])
            weighted = 0
            for capability_key, weight in sorted(sources.items()):
                weighted += _require_capability(capability_values, capability_key) * int(
                    weight
                )
            delta = _round_half_even_fraction(
                span * weighted, denominator * 1000
            )
        physical[str(output_key)] = base + delta

    direct: Dict[str, int] = {}
    for output_key, capability_key in sorted(
        calibration["direct_capability_fields_q1000"].items()
    ):
        direct[str(output_key)] = _require_capability(
            capability_values, str(capability_key)
        )
    return physical, direct


def _build_ship_templates(
    baseline: Mapping[str, Any], calibration: Mapping[str, Any]
) -> List[Dict[str, Any]]:
    class_map = calibration["identity_mapping"]["baseline_class_to_canonrec"]
    templates: List[Dict[str, Any]] = []
    seen_ids = set()
    side_prefixes = baseline["determinism"]["side_prefixes"]
    for side_id in sorted(baseline["sides"]):
        prefix = str(side_prefixes[side_id])
        for composition in baseline["fleet_template"]["composition"]:
            baseline_class_id = str(composition["class_id"])
            try:
                canonrec_class_id = str(class_map[baseline_class_id])
            except KeyError as exc:
                raise T0ConstructionError(
                    f"No CanonRec identity mapping for {baseline_class_id}"
                ) from exc
            token = baseline_class_id
            if not token.startswith("CLASS-") or not token.endswith("-01"):
                raise T0ConstructionError(
                    f"Unsupported baseline class token format: {baseline_class_id}"
                )
            token = token[len("CLASS-") : -len("-01")]
            count = int(composition["count"])
            if count <= 0:
                raise T0ConstructionError(
                    f"Non-positive vessel count for {baseline_class_id}: {count}"
                )
            for instance in range(1, count + 1):
                ship_id = f"{prefix}-{token}-{instance:02d}"
                if ship_id in seen_ids:
                    raise T0ConstructionError(f"Duplicate ship ID: {ship_id}")
                seen_ids.add(ship_id)
                templates.append(
                    {
                        "ship_id": ship_id,
                        "side_id": side_id,
                        "baseline_class_id": baseline_class_id,
                        "canonrec_class_id": canonrec_class_id,
                        "role": str(composition["role"]),
                    }
                )
    return sorted(templates, key=lambda item: item["ship_id"])


def _assign_slots(
    templates: Sequence[Mapping[str, Any]],
    side_id: str,
    calibration: Mapping[str, Any],
) -> Dict[str, int]:
    side_templates = [item for item in templates if item["side_id"] == side_id]
    flagship_role = calibration["formation"]["flagship_role"]
    flagships = [item for item in side_templates if item["role"] == flagship_role]
    if len(flagships) != 1:
        raise T0ConstructionError(
            f"Expected exactly one {flagship_role} vessel for {side_id}; got {len(flagships)}"
        )
    flagship_id = str(flagships[0]["ship_id"])
    assignments = {flagship_id: 0}
    remaining = sorted(
        (item for item in side_templates if str(item["ship_id"]) != flagship_id),
        key=lambda item: str(item["ship_id"]),
    )
    slot_table = calibration["formation"]["slots_permille"]
    if len(remaining) != len(slot_table):
        raise T0ConstructionError(
            f"Formation template expects {len(slot_table)} non-flagships; "
            f"{side_id} has {len(remaining)}"
        )
    for slot, item in enumerate(remaining, start=1):
        if str(slot) not in slot_table:
            raise T0ConstructionError(f"Missing formation slot {slot}")
        assignments[str(item["ship_id"])] = slot
    return assignments


def _slot_offset_m(
    slot: int,
    formation_radius_km: Any,
    side_id: str,
    calibration: Mapping[str, Any],
) -> List[int]:
    if slot == 0:
        return [0, 0, 0]
    formation = calibration["formation"]
    vector = formation["slots_permille"].get(str(slot))
    if vector is None or len(vector) != 3:
        raise T0ConstructionError(f"Invalid formation slot vector: {slot}")
    scale = int(formation["slot_scale_permille"])
    radius_m = _decimal_to_scaled_int(formation_radius_km, 1000)
    sign = int(formation["side_transform_sign"][side_id])
    offsets = [
        sign * _round_half_even_fraction(radius_m * int(component), scale)
        for component in vector
    ]
    if sum(component * component for component in offsets) > radius_m * radius_m:
        raise T0ConstructionError(f"Formation slot {slot} exceeds formation radius")
    return offsets


def _command_payload(side: Mapping[str, Any]) -> Dict[str, Any]:
    assignments: Dict[str, str] = {}
    for member in side.get("command_team", []):
        assignment = str(member.get("assignment") or "")
        entity_id = str(member.get("entity_id") or "")
        if not assignment or not entity_id or assignment in assignments:
            raise T0ConstructionError("Invalid or duplicate command-team assignment")
        assignments[assignment] = entity_id
    try:
        commander = assignments["commander"]
    except KeyError as exc:
        raise T0ConstructionError("Command team has no commander") from exc
    return {
        "fleet_commander_id": commander,
        "command_assignments": dict(sorted(assignments.items())),
        "command_team_ids": sorted(assignments.values()),
    }


def construct_t0_state(
    baseline_source: str | Path | Mapping[str, Any],
    calibration_source: str | Path | Mapping[str, Any],
    resolved_manifest: Mapping[str, Any],
) -> Dict[str, Any]:
    """Construct and hash a complete deterministic Run-0 T0 snapshot."""
    baseline = _load_json(baseline_source)
    calibration = _load_json(calibration_source)
    manifest = dict(resolved_manifest)

    if baseline.get("baseline_id") != "SIM-L2-FR-P17-EQUAL-001":
        raise T0ConstructionError("Unsupported baseline identity")
    if str(baseline.get("version")) != "1.2":
        raise T0ConstructionError("Unsupported baseline version")
    if calibration.get("version") != "1.0":
        raise T0ConstructionError("Unsupported physical calibration version")
    if calibration["numeric_policy"]["canonical_json_profile"] != CANONICAL_JSON_PROFILE:
        raise T0ConstructionError("Unsupported canonical JSON profile")

    _validate_manifest(manifest, calibration)
    capabilities = _capability_lookup(manifest)
    templates = _build_ship_templates(baseline, calibration)

    symmetry_contract = calibration["run0_symmetry_contract"]
    expected_total = int(symmetry_contract["expected_total_vessels"])
    if len(templates) != expected_total:
        raise T0ConstructionError(
            f"Expected {expected_total} total vessels; got {len(templates)}"
        )
    if int(manifest.get("total_vessels", 0)) != int(
        symmetry_contract["expected_vessels_per_side"]
    ):
        raise T0ConstructionError("Resolved control roster vessel count mismatch")

    expected_class_counts = {
        str(calibration["identity_mapping"]["baseline_class_to_canonrec"][entry["class_id"]]): int(
            entry["count"]
        )
        for entry in baseline["fleet_template"]["composition"]
    }
    actual_class_counts = {
        class_id: int(holder["count"]) for class_id, holder in capabilities.items()
    }
    if expected_class_counts != actual_class_counts:
        raise T0ConstructionError(
            f"Resolved roster does not match frozen control composition: "
            f"{actual_class_counts} != {expected_class_counts}"
        )

    semi_axes_m = [
        _decimal_to_scaled_int(baseline["battlefield"]["semi_axes_km"][axis], 1000)
        for axis in ("a", "b", "c")
    ]
    centroids_m = {
        side_id: [
            _decimal_to_scaled_int(value, 1000)
            for value in side["initial_centroid_position_km"]
        ]
        for side_id, side in baseline["sides"].items()
    }
    centroid_velocities = {
        side_id: [
            _decimal_to_scaled_int(value, 1_000_000)
            for value in side["initial_centroid_velocity_km_s"]
        ]
        for side_id, side in baseline["sides"].items()
    }
    side_ids = sorted(baseline["sides"])
    if len(side_ids) != 2:
        raise T0ConstructionError("Phase-3 control expects exactly two sides")
    if centroids_m[side_ids[0]] != _vector_negate(centroids_m[side_ids[1]]):
        raise T0ConstructionError("Control centroids are not exact sign inverses")
    if centroid_velocities[side_ids[0]] != _vector_negate(
        centroid_velocities[side_ids[1]]
    ):
        raise T0ConstructionError("Control centroid velocities are not exact sign inverses")

    slot_assignments = {
        side_id: _assign_slots(templates, side_id, calibration)
        for side_id in side_ids
    }
    local_offsets: Dict[str, List[int]] = {}
    positions: Dict[str, List[int]] = {}
    for template in templates:
        side_id = str(template["side_id"])
        ship_id = str(template["ship_id"])
        slot = slot_assignments[side_id][ship_id]
        offset = _slot_offset_m(
            slot,
            baseline["sides"][side_id]["formation_radius_km"],
            side_id,
            calibration,
        )
        local_offsets[ship_id] = offset
        position = _vector_add(centroids_m[side_id], offset)
        if _inside_triaxial_ellipsoid(position, semi_axes_m):
            raise T0ConstructionError(f"Generated vessel intersects P17: {ship_id}")
        positions[ship_id] = position

    for side_id in side_ids:
        side_offsets = [
            local_offsets[str(template["ship_id"])]
            for template in templates
            if template["side_id"] == side_id
        ]
        if _vector_sum(side_offsets) != [0, 0, 0]:
            raise T0ConstructionError(f"Formation offsets do not preserve centroid: {side_id}")
        side_positions = [
            tuple(positions[str(template["ship_id"])])
            for template in templates
            if template["side_id"] == side_id
        ]
        if len(side_positions) != len(set(side_positions)):
            raise T0ConstructionError(f"Duplicate T0 positions for side: {side_id}")

    initial = calibration["initial_state"]
    organization_id = calibration["identity_mapping"]["organization_id"]
    vessels: List[Dict[str, Any]] = []

    for template in templates:
        ship_id = str(template["ship_id"])
        side_id = str(template["side_id"])
        other_side = side_ids[1] if side_id == side_ids[0] else side_ids[0]
        canonrec_class_id = str(template["canonrec_class_id"])
        capability_holder = capabilities.get(canonrec_class_id)
        if capability_holder is None:
            raise T0ConstructionError(
                f"Resolved manifest lacks class {canonrec_class_id} for {ship_id}"
            )
        values = capability_holder["values"]
        physical_base, direct_q1000 = _calibrate_physical(values, calibration)
        physical = dict(physical_base)
        physical["shield_current_milliunits"] = physical[
            "shield_capacity_milliunits"
        ]
        physical["armor_current_milliunits"] = physical[
            "armor_integrity_milliunits"
        ]
        physical["hull_current_milliunits"] = physical[
            "hull_integrity_milliunits"
        ]
        forward = _normalize_q12(
            _vector_subtract(centroids_m[other_side], positions[ship_id])
        )
        command = _command_payload(baseline["sides"][side_id])
        slot = slot_assignments[side_id][ship_id]
        vessel = {
            "ship_id": ship_id,
            "side_id": side_id,
            "fleet_id": baseline["sides"][side_id]["fleet_id"],
            "baseline_class_id": template["baseline_class_id"],
            "canonrec_class_id": canonrec_class_id,
            "organization_id": organization_id,
            "role": template["role"],
            "formation_slot": slot,
            "position_m": positions[ship_id],
            "velocity_mm_s": list(centroid_velocities[side_id]),
            "attitude": {
                "frame": calibration["attitude"]["frame"],
                "forward_q12": forward,
                "up_q12": _attitude_up_q12(forward, calibration),
            },
            "physical": dict(sorted(physical.items())),
            "capability_q1000": dict(sorted(direct_q1000.items())),
            "resources_q1000": dict(sorted(initial["resources_q1000"].items())),
            "readiness_q1000": dict(sorted(initial["readiness_q1000"].items())),
            "command": command,
            "morale_q1000": int(initial["morale_q1000"]),
            "cohesion_q1000": int(initial["cohesion_q1000"]),
            "damage_state": initial["damage_state"],
            "disposition": initial["disposition"],
            "provenance": {
                "identity": "CANON_DIRECT",
                "capability_vector": "DERIVED_FROM_CANON",
                "physical_calibration": "SCENARIO_LOCAL",
                "formation_and_initial_state": "SCENARIO_LOCAL",
                "canonrec_resolution_sha256": capability_holder[
                    "resolution_sha256"
                ],
            },
        }
        vessels.append(vessel)

    vessels.sort(key=lambda item: item["ship_id"])
    if len({vessel["ship_id"] for vessel in vessels}) != len(vessels):
        raise T0ConstructionError("Duplicate vessel IDs after construction")

    loyalist_id = "loyalist"
    rebel_id = "rebel"
    if loyalist_id not in side_ids or rebel_id not in side_ids:
        raise T0ConstructionError("Run-0 symmetry expects loyalist and rebel sides")
    loyalist_vessels = {
        vessel["ship_id"].split("-", 1)[1]: vessel
        for vessel in vessels
        if vessel["side_id"] == loyalist_id
    }
    rebel_vessels = {
        vessel["ship_id"].split("-", 1)[1]: vessel
        for vessel in vessels
        if vessel["side_id"] == rebel_id
    }
    if loyalist_vessels.keys() != rebel_vessels.keys():
        raise T0ConstructionError("Side vessel identity sets are not symmetric")
    for suffix in sorted(loyalist_vessels):
        loyalist = loyalist_vessels[suffix]
        rebel = rebel_vessels[suffix]
        if loyalist["position_m"] != _vector_negate(rebel["position_m"]):
            raise T0ConstructionError(f"Position symmetry failed: {suffix}")
        if loyalist["velocity_mm_s"] != _vector_negate(rebel["velocity_mm_s"]):
            raise T0ConstructionError(f"Velocity symmetry failed: {suffix}")
        for field in (
            "physical",
            "capability_q1000",
            "resources_q1000",
            "readiness_q1000",
        ):
            if loyalist[field] != rebel[field]:
                raise T0ConstructionError(
                    f"Material symmetry failed for {suffix}.{field}"
                )
        for field in (
            "morale_q1000",
            "cohesion_q1000",
            "damage_state",
            "disposition",
        ):
            if loyalist[field] != rebel[field]:
                raise T0ConstructionError(
                    f"Material symmetry failed for {suffix}.{field}"
                )

    baseline_sha = sha256_json(baseline)
    calibration_sha = sha256_json(calibration)
    constructor_source_sha256 = _sha256_file(Path(__file__).resolve())
    snapshot: Dict[str, Any] = {
        "schema": "aurora://simulation/gumas/deterministic_t0_physical_state/v1.0",
        "schema_version": SCHEMA_VERSION,
        "constructor_version": CONSTRUCTOR_VERSION,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "run_identity": {
            "baseline_id": baseline["baseline_id"],
            "baseline_version": str(baseline["version"]),
            "baseline_sha256": baseline_sha,
            "seed_u64": normalize_seed64(baseline["determinism"]["seed_u64"]),
            "historical_source_tree_sha256": HISTORICAL_SOURCE_TREE_SHA256,
            "restoration_version": "2.0.1-restored.2",
            "restoration_source_identity": {
                "digest_type": "git_blob_sha1",
                "digest": RESTORATION_SOURCE_GIT_BLOB_SHA1,
            },
            "canonrec_commit": manifest["canonrec_commit"],
            "canonrec_resolver_source_identity": {
                "digest_type": "git_blob_sha1",
                "digest": CANONREC_RESOLVER_SOURCE_GIT_BLOB_SHA1,
            },
            "canonrec_resolver_version": manifest["resolver_version"],
            "canonrec_derivation_version": manifest["derivation_version"],
            "resolved_manifest_sha256": manifest["manifest_sha256"],
            "physical_calibration_version": str(calibration["version"]),
            "physical_calibration_sha256": calibration_sha,
            "t0_constructor_version": CONSTRUCTOR_VERSION,
            "t0_constructor_source_sha256": constructor_source_sha256,
        },
        "numeric_policy": dict(calibration["numeric_policy"]),
        "planetoid": {
            "body_id": baseline["battlefield"]["body_id"],
            "semi_axes_m": {
                "a": semi_axes_m[0],
                "b": semi_axes_m[1],
                "c": semi_axes_m[2],
            },
            "mass_kg_decimal": str(baseline["battlefield"]["mass_kg"]),
            "gravitational_parameter_m3_s2_decimal": str(
                baseline["battlefield"]["gravitational_parameter_m3_s2"]
            ),
            "combat_volume_radius_m": _decimal_to_scaled_int(
                baseline["battlefield"]["combat_volume_radius_km"], 1000
            ),
            "withdrawal_boundary_m": _decimal_to_scaled_int(
                baseline["battlefield"]["withdrawal_boundary_km"], 1000
            ),
            "integration_step_ms": _decimal_to_scaled_int(
                baseline["battlefield"]["integration_step_s"], 1000
            ),
            "rotation": dict(calibration["planetoid_rotation_completion"]),
        },
        "fleets": {
            side_id: {
                "fleet_id": baseline["sides"][side_id]["fleet_id"],
                "organization_id": organization_id,
                "centroid_position_m": centroids_m[side_id],
                "centroid_velocity_mm_s": centroid_velocities[side_id],
                "formation_radius_m": _decimal_to_scaled_int(
                    baseline["sides"][side_id]["formation_radius_km"], 1000
                ),
                "command": _command_payload(baseline["sides"][side_id]),
            }
            for side_id in side_ids
        },
        "vessels": vessels,
        "symmetry": {
            "material_symmetry_verified": True,
            "position_sign_inversion_verified": True,
            "velocity_sign_inversion_verified": True,
            "formation_centroid_preserved": True,
            "vessels_per_side": int(symmetry_contract["expected_vessels_per_side"]),
            "total_vessels": len(vessels),
        },
        "historical_canon_status": "non_canon_simulation_instance",
    }
    snapshot["t0_sha256"] = hashlib.sha256(canonical_json_bytes(snapshot)).hexdigest()
    return snapshot


def snapshot_without_hash(snapshot: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in snapshot.items() if key != "t0_sha256"}
