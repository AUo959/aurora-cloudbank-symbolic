"""Side-local live command-observation bridge for GUMAS Phase 9."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from simulation.runtime.gumas_movement_geometry.constants import (
    MAX_RUN_DURATION_MS,
    P17_WITHDRAWAL_RADIUS_UM,
)
from simulation.runtime.gumas_movement_geometry.geometry import (
    norm_nearest,
    round_half_even_fraction,
)

from .constants import (
    CANONICAL_JSON_PROFILE,
    GENESIS_MARKER,
    MISSION_PRESSURE_FLOOR_Q1000,
    OBSERVATION_RECEIPT_SCHEMA,
    PHASE9_CONTRACT_ID,
    PHASE9_VERSION,
)
from .identity import (
    Phase9Error,
    clamp_q1000,
    fraction_q1000,
    hash_without_field,
    mean_round,
    require_int,
    require_q1000,
    sha256_canonical,
    source_identity,
)


def _sides_and_fleets(baseline: Mapping[str, Any]) -> dict[str, str]:
    sides = baseline.get("sides")
    if not isinstance(sides, Mapping) or len(sides) != 2:
        raise Phase9Error("Phase 9 requires exactly two frozen baseline sides")
    result: dict[str, str] = {}
    for side_id, side in sorted(sides.items()):
        if not isinstance(side, Mapping):
            raise Phase9Error(f"invalid baseline side: {side_id}")
        fleet_id = str(side.get("fleet_id") or "")
        if not fleet_id or fleet_id in result.values():
            raise Phase9Error(f"invalid or duplicate fleet id: {fleet_id}")
        result[str(side_id)] = fleet_id
    return result


def _vessels_by_id(state: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    vessels = state.get("vessels")
    if not isinstance(vessels, Sequence) or isinstance(vessels, (str, bytes)):
        raise Phase9Error("state.vessels must be a sequence")
    result: dict[str, Mapping[str, Any]] = {}
    for vessel in vessels:
        if not isinstance(vessel, Mapping):
            raise Phase9Error("state vessel must be a mapping")
        ship_id = str(vessel.get("ship_id") or "")
        if not ship_id or ship_id in result:
            raise Phase9Error(f"invalid or duplicate vessel id: {ship_id}")
        result[ship_id] = vessel
    return result


def _capability(vessel: Mapping[str, Any], name: str) -> int:
    capabilities = vessel.get("capability_q1000")
    if not isinstance(capabilities, Mapping):
        raise Phase9Error(f"{vessel.get('ship_id')}.capability_q1000 missing")
    aliases = (name, f"{name}_q1000")
    for alias in aliases:
        if alias in capabilities:
            return require_q1000(capabilities[alias], f"{vessel['ship_id']}.{alias}")
    raise Phase9Error(f"{vessel['ship_id']}.{name} capability missing")


def _readiness(vessel: Mapping[str, Any], name: str) -> int:
    values = vessel.get("readiness_q1000")
    if not isinstance(values, Mapping):
        raise Phase9Error(f"{vessel.get('ship_id')}.readiness_q1000 missing")
    return require_q1000(values.get(name), f"{vessel['ship_id']}.readiness.{name}")


def _resource(vessel: Mapping[str, Any], name: str) -> int:
    values = vessel.get("resources_q1000")
    if not isinstance(values, Mapping):
        raise Phase9Error(f"{vessel.get('ship_id')}.resources_q1000 missing")
    return require_q1000(values.get(name), f"{vessel['ship_id']}.resources.{name}")


def _own_metrics(vessels: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    current_material = 0
    maximum_material = 0
    resources: list[int] = []
    mobility: list[int] = []
    readiness: list[int] = []
    fuel: list[int] = []
    withdrawal_progress: list[int] = []
    ew_effective: list[int] = []
    carrier_effective: list[int] = []

    active_dispositions = {"combat_capable", "degraded"}
    for vessel in sorted(vessels, key=lambda item: str(item["ship_id"])):
        physical = vessel.get("physical")
        if not isinstance(physical, Mapping):
            raise Phase9Error(f"{vessel['ship_id']}.physical missing")
        for layer in ("shield", "armor", "hull"):
            current = require_int(
                physical.get(f"{layer}_current_milliunits"),
                f"{vessel['ship_id']}.{layer}.current",
                minimum=0,
            )
            maximum = require_int(
                physical.get(
                    "hull_integrity_milliunits"
                    if layer == "hull"
                    else f"{layer}_capacity_milliunits" if layer == "shield" else "armor_integrity_milliunits"
                ),
                f"{vessel['ship_id']}.{layer}.maximum",
                minimum=1,
            )
            if current > maximum:
                raise Phase9Error(f"{vessel['ship_id']}.{layer} exceeds maximum")
            current_material += current
            maximum_material += maximum

        resources.extend(_resource(vessel, field) for field in ("fuel", "energy", "ammunition", "supply"))
        fuel_value = _resource(vessel, "fuel")
        fuel.append(fuel_value)
        overall = _readiness(vessel, "overall")
        damage_control = _readiness(vessel, "damage_control")
        readiness.extend((overall, damage_control))
        ew_ready = _readiness(vessel, "ew")
        ew_effective.append(round_half_even_fraction(_capability(vessel, "electronic_warfare") * ew_ready, 1000))
        carrier_effective.append(
            round_half_even_fraction(
                _capability(vessel, "carrier_projection")
                * min(overall, _resource(vessel, "energy"), _resource(vessel, "supply")),
                1000,
            )
        )

        active = str(vessel.get("disposition") or "") in active_dispositions
        mobility.append(_readiness(vessel, "propulsion") if active else 0)
        if active:
            position = vessel.get("position_um")
            if not isinstance(position, Sequence) or isinstance(position, (str, bytes)):
                raise Phase9Error(f"{vessel['ship_id']}.position_um missing")
            withdrawal_progress.append(
                clamp_q1000(
                    round_half_even_fraction(
                        norm_nearest(position) * 1000,
                        P17_WITHDRAWAL_RADIUS_UM,
                    )
                )
            )

    material_health = fraction_q1000(current_material, maximum_material, "own material health")
    own_damage = 1000 - material_health
    resource_margin = mean_round(resources)
    logistics_strain = 1000 - resource_margin
    mobility_margin = mean_round(mobility)
    readiness_margin = mean_round(readiness)
    readiness_deficit = 1000 - readiness_margin
    repair_need = clamp_q1000(round_half_even_fraction(500 * own_damage + 500 * readiness_deficit, 1000))
    fuel_margin = mean_round(fuel)
    withdrawal_progress_q1000 = mean_round(withdrawal_progress)
    withdrawal_viability = clamp_q1000(
        round_half_even_fraction(
            600 * mobility_margin + 200 * fuel_margin + 200 * withdrawal_progress_q1000,
            1000,
        )
    )
    return {
        "current_material_milliunits": current_material,
        "maximum_material_milliunits": maximum_material,
        "material_health_q1000": material_health,
        "own_damage_q1000": own_damage,
        "resource_margin_q1000": resource_margin,
        "logistics_strain_q1000": logistics_strain,
        "mobility_margin_q1000": mobility_margin,
        "readiness_margin_q1000": readiness_margin,
        "readiness_deficit_q1000": readiness_deficit,
        "repair_need_q1000": repair_need,
        "fuel_margin_q1000": fuel_margin,
        "withdrawal_progress_q1000": withdrawal_progress_q1000,
        "withdrawal_viability_q1000": withdrawal_viability,
        "own_ew_margin_q1000": mean_round(ew_effective),
        "carrier_opportunity_q1000": mean_round(carrier_effective),
    }


def _best_contacts(
    side_id: str,
    phase6_receipt: Mapping[str, Any] | None,
    vessels: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    if phase6_receipt is None:
        return {}
    contacts = phase6_receipt.get("contacts")
    if not isinstance(contacts, Sequence) or isinstance(contacts, (str, bytes)):
        raise Phase9Error("Phase-6 contacts must be a sequence")
    best: dict[str, dict[str, Any]] = {}
    for raw in contacts:
        if not isinstance(raw, Mapping):
            raise Phase9Error("Phase-6 contact must be a mapping")
        observer_id = str(raw.get("observer_ship_id") or "")
        target_id = str(raw.get("target_ship_id") or "")
        if observer_id not in vessels or target_id not in vessels:
            raise Phase9Error("Phase-6 contact references a vessel outside frozen state")
        if str(vessels[observer_id].get("side_id") or "") != side_id:
            continue
        if str(vessels[target_id].get("side_id") or "") == side_id:
            raise Phase9Error("Phase-6 contact targets the observer's own side")
        recorded = str(raw.get("contact_sha256") or "")
        if not recorded or recorded != hash_without_field(raw, "contact_sha256"):
            raise Phase9Error(f"contact hash mismatch: {observer_id}->{target_id}")
        candidate = {
            "observer_ship_id": observer_id,
            "target_ship_id": target_id,
            "distance_um": require_int(raw.get("distance_um"), "contact distance", minimum=0),
            "contact_quality_q1000": require_q1000(raw.get("contact_quality_q1000"), "contact quality"),
            "identity_quality_q1000": require_q1000(raw.get("identity_quality_q1000"), "identity quality"),
            "classification": str(raw.get("classification") or ""),
            "contact_sha256": recorded,
        }
        current = best.get(target_id)
        candidate_key = (
            -candidate["contact_quality_q1000"],
            -candidate["identity_quality_q1000"],
            candidate["observer_ship_id"],
        )
        current_key = (
            (
                -current["contact_quality_q1000"],
                -current["identity_quality_q1000"],
                current["observer_ship_id"],
            )
            if current
            else None
        )
        if current is None or candidate_key < current_key:
            best[target_id] = candidate
    return dict(sorted(best.items()))


def _prior_observation_memory(
    receipt: Mapping[str, Any] | None,
    *,
    side_id: str,
    fleet_id: str,
    enemy_ids: Sequence[str],
    run_identity_sha256: str,
    roster_sha256: str,
) -> tuple[dict[str, int], dict[str, int], str]:
    if receipt is None:
        return (
            {ship_id: 0 for ship_id in enemy_ids},
            {},
            GENESIS_MARKER,
        )
    recorded = str(receipt.get("live_observation_receipt_sha256") or "")
    if not recorded or recorded != hash_without_field(receipt, "live_observation_receipt_sha256"):
        raise Phase9Error(f"prior live-observation receipt hash mismatch: {side_id}")
    if str(receipt.get("side_id") or "") != side_id or str(receipt.get("fleet_id") or "") != fleet_id:
        raise Phase9Error(f"prior live-observation side/fleet mismatch: {side_id}")
    if str(receipt.get("run_identity_sha256") or "") != run_identity_sha256:
        raise Phase9Error(f"prior live-observation run identity mismatch: {side_id}")
    if str(receipt.get("t0_roster_sha256") or "") != roster_sha256:
        raise Phase9Error(f"prior live-observation roster mismatch: {side_id}")
    estimates_raw = receipt.get("enemy_damage_estimate_q1000_by_target")
    if not isinstance(estimates_raw, Mapping) or set(estimates_raw) != set(enemy_ids):
        raise Phase9Error(f"prior enemy-damage memory mismatch: {side_id}")
    estimates = {
        ship_id: require_q1000(estimates_raw[ship_id], f"{side_id}.{ship_id}.damage memory") for ship_id in enemy_ids
    }
    distances_raw = receipt.get("contact_distance_um_by_target") or {}
    if not isinstance(distances_raw, Mapping):
        raise Phase9Error(f"prior contact-distance memory invalid: {side_id}")
    if not set(str(ship_id) for ship_id in distances_raw).issubset(enemy_ids):
        raise Phase9Error(f"prior contact-distance target mismatch: {side_id}")
    distances = {
        str(ship_id): require_int(distance, "prior contact distance", minimum=1)
        for ship_id, distance in sorted(distances_raw.items())
    }
    return estimates, distances, recorded


def _attributable_damage(
    side_id: str,
    contacts: Mapping[str, Mapping[str, Any]],
    phase6_receipt: Mapping[str, Any] | None,
    phase7_receipt: Mapping[str, Any] | None,
    vessels: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    if phase6_receipt is None or phase7_receipt is None:
        return {}, []
    effects = phase6_receipt.get("effect_descriptors")
    targets = phase7_receipt.get("target_damage_receipts")
    if not isinstance(effects, Sequence) or isinstance(effects, (str, bytes)):
        raise Phase9Error("Phase-6 effect descriptors must be a sequence")
    if not isinstance(targets, Sequence) or isinstance(targets, (str, bytes)):
        raise Phase9Error("Phase-7 target damage receipts must be a sequence")
    effect_side: dict[str, tuple[str, str]] = {}
    for effect in effects:
        effect_id = str(effect.get("effect_id") or "")
        source_id = str(effect.get("source_ship_id") or "")
        target_id = str(effect.get("target_ship_id") or "")
        if source_id not in vessels or target_id not in vessels or not effect_id:
            raise Phase9Error("invalid effect descriptor in observation bridge")
        if str(vessels[source_id].get("side_id") or "") == side_id:
            effect_side[effect_id] = (source_id, target_id)

    result: dict[str, int] = {}
    evidence: list[dict[str, Any]] = []
    for target in targets:
        target_id = str(target.get("target_ship_id") or "")
        if target_id not in contacts:
            continue
        effect_ids = target.get("effect_ids")
        if not isinstance(effect_ids, Sequence) or isinstance(effect_ids, (str, bytes)):
            raise Phase9Error("Phase-7 target receipt effect ids invalid")
        attributable = sorted(
            effect_id
            for effect_id in (str(value) for value in effect_ids)
            if effect_id in effect_side and effect_side[effect_id][1] == target_id
        )
        if not attributable:
            continue
        hull = target.get("hull")
        if not isinstance(hull, Mapping):
            raise Phase9Error("Phase-7 target receipt hull data missing")
        loss = require_q1000(
            hull.get("new_hull_loss_q1000"),
            f"{target_id}.new_hull_loss_q1000",
        )
        result[target_id] = loss
        evidence.append(
            {
                "target_ship_id": target_id,
                "effect_ids": attributable,
                "new_hull_loss_q1000": loss,
            }
        )
    return result, sorted(evidence, key=lambda item: item["target_ship_id"])


def derive_live_observations(
    state: Mapping[str, Any],
    baseline: Mapping[str, Any],
    run_context: Mapping[str, Any],
    *,
    previous_phase6_receipt: Mapping[str, Any] | None = None,
    previous_phase7_receipt: Mapping[str, Any] | None = None,
    previous_resolution_state: Mapping[str, Any] | None = None,
    previous_phase8_receipt: Mapping[str, Any] | None = None,
    previous_observation_receipts_by_side: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, Any]]]:
    """Derive deterministic, side-local Phase-4 inputs from committed evidence."""
    continuation_artifacts = (
        previous_phase6_receipt,
        previous_phase7_receipt,
        previous_resolution_state,
        previous_phase8_receipt,
        previous_observation_receipts_by_side,
    )
    if any(value is not None for value in continuation_artifacts) and not all(
        value is not None for value in continuation_artifacts
    ):
        raise Phase9Error("live-observation checkpoint is partial")
    if previous_phase6_receipt is not None:
        for receipt, field, label in (
            (
                previous_phase6_receipt,
                "phase6_receipt_sha256",
                "previous Phase-6 receipt",
            ),
            (
                previous_phase7_receipt,
                "phase7_receipt_sha256",
                "previous Phase-7 receipt",
            ),
            (
                previous_resolution_state,
                "resolution_state_sha256",
                "previous Phase-8 resolution",
            ),
            (
                previous_phase8_receipt,
                "phase8_receipt_sha256",
                "previous Phase-8 receipt",
            ),
        ):
            recorded = str(receipt.get(field) or "")
            if not recorded or recorded != hash_without_field(receipt, field):
                raise Phase9Error(f"{label} hash mismatch")
    side_to_fleet = _sides_and_fleets(baseline)
    vessels = _vessels_by_id(state)
    roster_records = run_context.get("roster_records")
    if not isinstance(roster_records, Sequence):
        raise Phase9Error("run context roster missing")
    run_sha = str(run_context.get("run_identity_sha256") or "")
    roster_sha = str(run_context.get("t0_roster_sha256") or "")
    if not run_sha or not roster_sha:
        raise Phase9Error("run context identities missing")
    previous_observation_receipts_by_side = previous_observation_receipts_by_side or {}

    observations: dict[str, dict[str, int]] = {}
    receipts: dict[str, dict[str, Any]] = {}
    for side_id, fleet_id in sorted(side_to_fleet.items()):
        own_ids = sorted(str(record["ship_id"]) for record in roster_records if str(record["side_id"]) == side_id)
        enemy_ids = sorted(str(record["ship_id"]) for record in roster_records if str(record["side_id"]) != side_id)
        if not own_ids or not enemy_ids:
            raise Phase9Error(f"invalid frozen roster partition for {side_id}")
        own = [vessels[ship_id] for ship_id in own_ids]
        own_metrics = _own_metrics(own)
        contacts = _best_contacts(side_id, previous_phase6_receipt, vessels)
        if not set(contacts).issubset(enemy_ids):
            raise Phase9Error(f"contact target outside opposing roster: {side_id}")

        prior_estimates, prior_distances, prior_receipt_sha = _prior_observation_memory(
            previous_observation_receipts_by_side.get(side_id),
            side_id=side_id,
            fleet_id=fleet_id,
            enemy_ids=enemy_ids,
            run_identity_sha256=run_sha,
            roster_sha256=roster_sha,
        )
        attributable, attributable_evidence = _attributable_damage(
            side_id,
            contacts,
            previous_phase6_receipt,
            previous_phase7_receipt,
            vessels,
        )
        estimates = {
            ship_id: clamp_q1000(prior_estimates[ship_id] + attributable.get(ship_id, 0)) for ship_id in enemy_ids
        }

        contact_quality = round_half_even_fraction(
            sum(int(item["contact_quality_q1000"]) for item in contacts.values()),
            len(enemy_ids),
        )
        identity_quality = round_half_even_fraction(
            sum(int(item["identity_quality_q1000"]) for item in contacts.values()),
            len(enemy_ids),
        )
        uncertainty = 1000 - round_half_even_fraction(contact_quality + identity_quality, 2)

        geometry_values: dict[str, int] = {}
        closing_values: dict[str, int] = {}
        for target_id, contact in contacts.items():
            observer = vessels[str(contact["observer_ship_id"])]
            weapon_range_um = (
                require_int(
                    (observer.get("physical") or {}).get("effective_weapon_range_m"),
                    f"{observer['ship_id']}.effective_weapon_range_m",
                    minimum=1,
                )
                * 1_000_000
            )
            geometry_values[target_id] = clamp_q1000(
                1000 - round_half_even_fraction(int(contact["distance_um"]) * 1000, weapon_range_um)
            )
            prior_distance = prior_distances.get(target_id)
            current_distance = int(contact["distance_um"])
            closing_values[target_id] = (
                clamp_q1000(
                    round_half_even_fraction(
                        (prior_distance - current_distance) * 1000,
                        prior_distance,
                    )
                )
                if prior_distance is not None and current_distance < prior_distance
                else 0
            )

        geometry_opportunity = round_half_even_fraction(sum(geometry_values.values()), len(enemy_ids))
        enemy_closing_pressure = round_half_even_fraction(sum(closing_values.values()), len(enemy_ids))
        enemy_damage_estimate = mean_round(list(estimates.values()))
        relative_advantage = clamp_q1000(
            500 + round_half_even_fraction(enemy_damage_estimate - own_metrics["own_damage_q1000"], 2)
        )
        time_pressure = clamp_q1000(
            round_half_even_fraction(
                require_int(state.get("elapsed_ms"), "state elapsed_ms", minimum=0) * 1000,
                MAX_RUN_DURATION_MS,
            )
        )
        mission_pressure = max(MISSION_PRESSURE_FLOOR_Q1000, time_pressure)
        ew_opportunity = clamp_q1000(
            round_half_even_fraction(
                600 * uncertainty + 400 * own_metrics["own_ew_margin_q1000"],
                1000,
            )
        )
        if previous_resolution_state is None:
            negotiation_signal = 0
            negotiation_source_sha = GENESIS_MARKER
        else:
            signals = previous_resolution_state.get("negotiation_signal_q1000_by_side")
            if not isinstance(signals, Mapping) or set(signals) != set(side_to_fleet):
                raise Phase9Error("prior Phase-8 negotiation-signal side set mismatch")
            negotiation_signal = require_q1000(signals[side_id], f"{side_id}.negotiation_signal")
            negotiation_source_sha = str(previous_resolution_state.get("resolution_state_sha256") or "")

        observation = {
            "contact_quality": clamp_q1000(contact_quality),
            "relative_advantage": relative_advantage,
            "own_damage": own_metrics["own_damage_q1000"],
            "enemy_damage_estimate": enemy_damage_estimate,
            "logistics_strain": own_metrics["logistics_strain_q1000"],
            "mobility_margin": own_metrics["mobility_margin_q1000"],
            "geometry_opportunity": clamp_q1000(geometry_opportunity),
            "withdrawal_viability": own_metrics["withdrawal_viability_q1000"],
            "mission_pressure": mission_pressure,
            "time_pressure": time_pressure,
            "negotiation_signal": negotiation_signal,
            "ew_opportunity": ew_opportunity,
            "carrier_opportunity": own_metrics["carrier_opportunity_q1000"],
            "repair_need": own_metrics["repair_need_q1000"],
            "enemy_closing_pressure": clamp_q1000(enemy_closing_pressure),
            "uncertainty": clamp_q1000(uncertainty),
        }
        for field, value in observation.items():
            require_q1000(value, f"{side_id}.observation.{field}")

        phase6_sha = (
            str(previous_phase6_receipt.get("phase6_receipt_sha256") or "")
            if previous_phase6_receipt is not None
            else GENESIS_MARKER
        )
        phase7_sha = (
            str(previous_phase7_receipt.get("phase7_receipt_sha256") or "")
            if previous_phase7_receipt is not None
            else GENESIS_MARKER
        )
        phase8_sha = (
            str(previous_phase8_receipt.get("phase8_receipt_sha256") or "")
            if previous_phase8_receipt is not None
            else GENESIS_MARKER
        )
        receipt: dict[str, Any] = {
            "schema": OBSERVATION_RECEIPT_SCHEMA,
            "phase9_contract_id": PHASE9_CONTRACT_ID,
            "phase9_version": PHASE9_VERSION,
            "phase9_source_identity": source_identity(),
            "canonical_json_profile": CANONICAL_JSON_PROFILE,
            "run_identity_sha256": run_sha,
            "t0_roster_sha256": roster_sha,
            "side_id": side_id,
            "fleet_id": fleet_id,
            "decision_epoch": require_int(state.get("macrostep_index"), "state macrostep_index", minimum=0),
            "source_committed_state_sha256": str(state.get("state_sha256") or ""),
            "source_phase6_receipt_sha256": phase6_sha,
            "source_phase7_receipt_sha256": phase7_sha,
            "source_phase8_resolution_state_sha256": negotiation_source_sha,
            "source_phase8_receipt_sha256": phase8_sha,
            "prior_live_observation_receipt_sha256": prior_receipt_sha,
            "selected_contact_evidence": list(contacts.values()),
            "contact_distance_um_by_target": {
                target_id: int(item["distance_um"]) for target_id, item in sorted(contacts.items())
            },
            "attributable_damage_evidence": attributable_evidence,
            "enemy_damage_estimate_q1000_by_target": estimates,
            "own_state_terms": own_metrics,
            "field_terms": {
                "contact_identity_quality_q1000": identity_quality,
                "geometry_opportunity_q1000_by_target": geometry_values,
                "closing_pressure_q1000_by_target": closing_values,
                "mission_pressure_floor_q1000": MISSION_PRESSURE_FLOOR_Q1000,
                "hard_limit_ms": MAX_RUN_DURATION_MS,
            },
            "observation": observation,
            "observation_sha256": sha256_canonical(observation),
            "enemy_raw_material_state_used": False,
            "prose_inputs_used": False,
            "ambient_rng_used": False,
            "floating_authority_used": False,
        }
        receipt["live_observation_receipt_sha256"] = hash_without_field(receipt, "live_observation_receipt_sha256")
        observations[side_id] = observation
        receipts[side_id] = receipt
    return dict(sorted(observations.items())), dict(sorted(receipts.items()))
