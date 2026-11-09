"""Shared deterministic control fixture for GUMAS acceptance smokes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from simulation.runtime.canonrec_tactical.resolver import CanonRecTacticalResolver
from simulation.runtime.gumas_command_policy.policy import decide
from simulation.runtime.gumas_movement_geometry.geometry import (
    mean_vector_round_half_even,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    initialize_motion_state,
    order_from_command_receipt,
    step_motion_state,
)
from simulation.runtime.gumas_physical_t0.constructor import construct_t0_state

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_T0_SHA256 = "47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec"
BASELINE = (
    ROOT / "simulation/baselines/gumas/"
    "GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
)
CALIBRATION = (
    ROOT / "simulation/calibration/gumas/"
    "GUMAS__CALIBRATION__CANONREC_TO_PHYSICAL_TACTICAL_STATE__v1.0__2026-08-13.json"
)
SOURCE_SET = (
    ROOT / "simulation/canon_snapshots/canonrec/"
    "CANONREC__SOURCE_SET__GUMAS_RUN0_PHASE2__v1.0__2026-08-12.json"
)
CONTROL_OBSERVATION = {
    "contact_quality": 800,
    "relative_advantage": 400,
    "own_damage": 150,
    "enemy_damage_estimate": 150,
    "logistics_strain": 150,
    "mobility_margin": 800,
    "geometry_opportunity": 100,
    "withdrawal_viability": 700,
    "mission_pressure": 750,
    "time_pressure": 500,
    "negotiation_signal": 0,
    "ew_opportunity": 500,
    "carrier_opportunity": 600,
    "repair_need": 100,
    "enemy_closing_pressure": 600,
    "uncertainty": 250,
}


@dataclass(frozen=True)
class AcceptanceFixture:
    """Resolved common state for a deterministic control-run smoke."""

    baseline: dict[str, Any]
    t0: dict[str, Any]
    initial_motion_state: dict[str, Any]
    fleet_centroids: dict[str, list[int]]
    decisions_by_side: dict[str, dict[str, Any]]
    decisions_by_fleet: dict[str, dict[str, Any]]
    motion_orders: dict[str, dict[str, Any]]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _control_roster(
    baseline: dict[str, Any],
    calibration: dict[str, Any],
) -> list[dict[str, Any]]:
    mapping = calibration["identity_mapping"]["baseline_class_to_canonrec"]
    return [
        {"class_id": mapping[item["class_id"]], "count": int(item["count"])}
        for item in baseline["fleet_template"]["composition"]
    ]


def _fleet_centroids(state: dict[str, Any]) -> dict[str, list[int]]:
    grouped: dict[str, list[list[int]]] = {}
    for vessel in state["vessels"]:
        grouped.setdefault(vessel["fleet_id"], []).append(vessel["position_um"])
    return {
        fleet_id: list(mean_vector_round_half_even(positions))
        for fleet_id, positions in sorted(grouped.items())
    }


def load_acceptance_fixture(canonrec_root: Path) -> AcceptanceFixture:
    """Resolve the canonical T0 state and common deterministic commands."""

    baseline = _load(BASELINE)
    calibration = _load(CALIBRATION)
    resolver = CanonRecTacticalResolver.from_files(canonrec_root, SOURCE_SET)
    manifest = resolver.resolve_roster(
        calibration["identity_mapping"]["organization_id"],
        _control_roster(baseline, calibration),
    )
    t0 = construct_t0_state(baseline, calibration, manifest)
    assert t0["t0_sha256"] == EXPECTED_T0_SHA256
    initial_motion_state = initialize_motion_state(t0)
    baseline_identity = {
        "baseline_id": baseline["baseline_id"],
        "baseline_version": str(baseline["version"]),
    }
    decisions_by_side: dict[str, dict[str, Any]] = {}
    decisions_by_fleet: dict[str, dict[str, Any]] = {}
    motion_orders: dict[str, dict[str, Any]] = {}
    for side in ("loyalist", "rebel"):
        fleet = baseline["sides"][side]
        decision = decide(
            fleet["command_team"],
            CONTROL_OBSERVATION,
            side_id=side,
            fleet_id=fleet["fleet_id"],
            decision_epoch=0,
            baseline_identity=baseline_identity,
        )
        decisions_by_side[side] = decision
        decisions_by_fleet[fleet["fleet_id"]] = decision
        motion_orders[fleet["fleet_id"]] = order_from_command_receipt(decision)
    return AcceptanceFixture(
        baseline=baseline,
        t0=t0,
        initial_motion_state=initial_motion_state,
        fleet_centroids=_fleet_centroids(initial_motion_state),
        decisions_by_side=decisions_by_side,
        decisions_by_fleet=decisions_by_fleet,
        motion_orders=motion_orders,
    )


def opposing_references(
    fixture: AcceptanceFixture,
    *,
    reference_kind: str,
    source_receipt_sha256: str,
) -> dict[str, dict[str, Any]]:
    """Build symmetric opposing-fleet references for one acceptance phase."""

    loyal = fixture.baseline["sides"]["loyalist"]["fleet_id"]
    rebel = fixture.baseline["sides"]["rebel"]["fleet_id"]
    return {
        loyal: {
            "reference_kind": reference_kind,
            "position_um": fixture.fleet_centroids[rebel],
            "source_state_sha256": fixture.initial_motion_state["state_sha256"],
            "source_receipt_sha256": source_receipt_sha256,
            "confidence_q1000": 1000,
        },
        rebel: {
            "reference_kind": reference_kind,
            "position_um": fixture.fleet_centroids[loyal],
            "source_state_sha256": fixture.initial_motion_state["state_sha256"],
            "source_receipt_sha256": source_receipt_sha256,
            "confidence_q1000": 1000,
        },
    }


def step_control_movement(
    fixture: AcceptanceFixture,
    *,
    reference_kind: str,
    source_receipt_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Advance the common control fixture by one deterministic movement step."""

    return step_motion_state(
        fixture.initial_motion_state,
        fixture.motion_orders,
        opposing_references(
            fixture,
            reference_kind=reference_kind,
            source_receipt_sha256=source_receipt_sha256,
        ),
    )
