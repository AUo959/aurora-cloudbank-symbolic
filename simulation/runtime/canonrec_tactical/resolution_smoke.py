#!/usr/bin/env python3
"""Real-source Phase-2 acceptance smoke against a pinned CanonRec checkout."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from simulation.runtime.canonrec_tactical.resolver import CanonRecTacticalResolver

ROOT = Path(__file__).resolve().parents[3]
SOURCE_SET = ROOT / "simulation/canon_snapshots/canonrec/CANONREC__SOURCE_SET__GUMAS_RUN0_PHASE2__v1.0__2026-08-12.json"
CONTROL = [
    {"class_id": "cls_judicator", "count": 1},
    {"class_id": "cls_aegis", "count": 3},
    {"class_id": "cls_palisade", "count": 1},
    {"class_id": "cls_sentinel", "count": 2},
    {"class_id": "cls_obsidian", "count": 1},
    {"class_id": "cls_vanguard", "count": 4},
    {"class_id": "cls_peregrine", "count": 6},
    {"class_id": "cls_reliant", "count": 1},
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonrec-root", required=True, type=Path)
    args = parser.parse_args()

    resolver = CanonRecTacticalResolver.from_files(args.canonrec_root, SOURCE_SET)
    control = resolver.resolve_roster("org_galactic_union", CONTROL)
    replay = resolver.resolve_roster("org_galactic_union", list(reversed(CONTROL)))

    substitution = [dict(item) for item in CONTROL]
    for item in substitution:
        if item["class_id"] == "cls_peregrine":
            item["count"] = 5
    substitution.append({"class_id": "cls_bastion", "count": 1})
    changed = resolver.resolve_roster("org_galactic_union", substitution)

    gu = resolver.resolve_authority("org_galactic_union")
    prime = resolver.resolve_authority("polity_prime_construct")
    peregrine = resolver.resolve_class("cls_peregrine", "org_galactic_union")
    judicator = resolver.resolve_class("cls_judicator", "org_galactic_union")
    aegis = resolver.resolve_class("cls_aegis", "org_galactic_union")

    assert control == replay
    assert control["total_vessels"] == 19
    assert changed["total_vessels"] == 19
    assert control["manifest_sha256"] != changed["manifest_sha256"]
    assert control["aggregate_capability_vector"]["values"] != changed["aggregate_capability_vector"]["values"]
    assert gu["doctrine_vector"]["values"] != prime["doctrine_vector"]["values"]
    assert peregrine["scoped_doctrine_sources"] == []
    assert judicator["scoped_doctrine_sources"] or aegis["scoped_doctrine_sources"]

    receipt = {
        "status": "ok",
        "canonrec_commit": resolver.expected_commit,
        "material_source_set_sha256": resolver.source_set_sha256,
        "control_manifest_sha256": control["manifest_sha256"],
        "substitution_manifest_sha256": changed["manifest_sha256"],
        "gu_authority_sha256": gu["resolution_sha256"],
        "prime_construct_authority_sha256": prime["resolution_sha256"],
        "control_aggregate": control["aggregate_capability_vector"]["values"],
        "substitution_aggregate": changed["aggregate_capability_vector"]["values"],
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
