#!/usr/bin/env python3
"""Real-source Phase-3 deterministic T0 acceptance smoke."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.runtime.canonrec_tactical.resolver import (  # noqa: E402
    CanonRecTacticalResolver,
    canonical_json_bytes,
)
from simulation.runtime.gumas_physical_t0.constructor import (  # noqa: E402
    CONSTRUCTOR_VERSION,
    construct_t0_state,
)

EXPECTED_T0_SHA256 = "47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec"
EXPECTED_CONSTRUCTOR_SOURCE_SHA256 = (
    "01dd9f1ed08ebc1822e42c28d038e2fff742fe8d0421c342198fbebf56208f6f"
)
BASELINE = (
    ROOT
    / "simulation/baselines/gumas/"
    "GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
)
CALIBRATION = (
    ROOT
    / "simulation/calibration/gumas/"
    "GUMAS__CALIBRATION__CANONREC_TO_PHYSICAL_TACTICAL_STATE__v1.0__2026-08-13.json"
)
SOURCE_SET = (
    ROOT
    / "simulation/canon_snapshots/canonrec/"
    "CANONREC__SOURCE_SET__GUMAS_RUN0_PHASE2__v1.0__2026-08-12.json"
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _control_roster(baseline, calibration):
    mapping = calibration["identity_mapping"]["baseline_class_to_canonrec"]
    return [
        {"class_id": mapping[item["class_id"]], "count": int(item["count"])}
        for item in baseline["fleet_template"]["composition"]
    ]


def _material_payload(snapshot):
    return [
        {
            "ship_id_suffix": vessel["ship_id"].split("-", 1)[1],
            "side_id": vessel["side_id"],
            "position_m": vessel["position_m"],
            "velocity_mm_s": vessel["velocity_mm_s"],
            "physical": vessel["physical"],
            "capability_q1000": vessel["capability_q1000"],
            "resources_q1000": vessel["resources_q1000"],
            "readiness_q1000": vessel["readiness_q1000"],
        }
        for vessel in snapshot["vessels"]
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonrec-root", required=True, type=Path)
    parser.add_argument("--snapshot-out", type=Path)
    parser.add_argument("--expected-snapshot", type=Path)
    args = parser.parse_args()

    baseline = _load(BASELINE)
    calibration = _load(CALIBRATION)
    resolver = CanonRecTacticalResolver.from_files(args.canonrec_root, SOURCE_SET)
    manifest = resolver.resolve_roster(
        calibration["identity_mapping"]["organization_id"],
        _control_roster(baseline, calibration),
    )

    first = construct_t0_state(baseline, calibration, manifest)
    replay = construct_t0_state(baseline, calibration, manifest)
    assert first == replay
    assert first["t0_sha256"] == EXPECTED_T0_SHA256
    assert (
        first["run_identity"]["t0_constructor_source_sha256"]
        == EXPECTED_CONSTRUCTOR_SOURCE_SHA256
    )
    assert len(first["vessels"]) == 38
    assert first["symmetry"]["material_symmetry_verified"] is True
    assert first["symmetry"]["position_sign_inversion_verified"] is True
    assert first["symmetry"]["formation_centroid_preserved"] is True

    proxy_mutation = copy.deepcopy(baseline)
    for values in proxy_mutation["fleet_template"]["class_coefficients"].values():
        for key in list(values):
            if isinstance(values[key], (int, float)):
                values[key] = values[key] * 1000 + 777
    mutated = construct_t0_state(proxy_mutation, calibration, manifest)
    assert _material_payload(first) == _material_payload(mutated)
    assert first["t0_sha256"] != mutated["t0_sha256"]

    snapshot_bytes = canonical_json_bytes(first)
    if args.expected_snapshot is not None:
        assert args.expected_snapshot.read_bytes() == snapshot_bytes
    if args.snapshot_out is not None:
        args.snapshot_out.parent.mkdir(parents=True, exist_ok=True)
        args.snapshot_out.write_bytes(snapshot_bytes)

    class_physical = {}
    for vessel in first["vessels"]:
        class_id = vessel["canonrec_class_id"]
        class_physical.setdefault(class_id, vessel["physical"])

    receipt = {
        "status": "ok",
        "constructor_version": CONSTRUCTOR_VERSION,
        "t0_sha256": first["t0_sha256"],
        "baseline_sha256": first["run_identity"]["baseline_sha256"],
        "calibration_sha256": first["run_identity"]["physical_calibration_sha256"],
        "resolved_manifest_sha256": first["run_identity"]["resolved_manifest_sha256"],
        "t0_constructor_source_sha256": first["run_identity"][
            "t0_constructor_source_sha256"
        ],
        "restoration_source_identity": first["run_identity"][
            "restoration_source_identity"
        ],
        "canonrec_resolver_source_identity": first["run_identity"][
            "canonrec_resolver_source_identity"
        ],
        "seed_u64": first["run_identity"]["seed_u64"],
        "vessels_total": len(first["vessels"]),
        "vessels_per_side": first["symmetry"]["vessels_per_side"],
        "material_symmetry_verified": True,
        "position_sign_inversion_verified": True,
        "formation_centroid_preserved": True,
        "baseline_proxy_coefficients_non_authoritative": True,
        "committed_snapshot_match": args.expected_snapshot is not None,
        "planetoid_rotation": first["planetoid"]["rotation"],
        "class_physical": class_physical,
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
