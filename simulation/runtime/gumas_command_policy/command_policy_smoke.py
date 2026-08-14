#!/usr/bin/env python3
"""Focused real-fixture smoke for deterministic command policy Phase 4."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.runtime.gumas_command_policy.policy import decide  # noqa: E402

BASELINE = (
    ROOT
    / "simulation/baselines/gumas/"
    "GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
)
OBSERVATION = {
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


def main() -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    identity = {
        "baseline_id": baseline["baseline_id"],
        "baseline_version": str(baseline["version"]),
    }
    output = {}
    for side in ("loyalist", "rebel"):
        fleet = baseline["sides"][side]
        first = decide(
            fleet["command_team"],
            OBSERVATION,
            side_id=side,
            fleet_id=fleet["fleet_id"],
            decision_epoch=0,
            baseline_identity=identity,
        )
        replay = decide(
            list(reversed(fleet["command_team"])),
            dict(reversed(list(OBSERVATION.items()))),
            side_id=side,
            fleet_id=fleet["fleet_id"],
            decision_epoch=0,
            baseline_identity=identity,
        )
        assert first == replay
        output[side] = {
            "decision_sha256": first["decision_sha256"],
            "policy_source_sha256": first["policy_source_sha256"],
            "policy_module_sha256": first["policy_module_sha256"],
            "coefficient_table_sha256": first["coefficient_table_sha256"],
            "command_team_numeric_sha256": first[
                "command_team_numeric_sha256"
            ],
            "orders": first["orders"],
            "strategic_scores": {
                action: detail["score"]
                for action, detail in first["strategic"]["scores"].items()
            },
            "dissent_q1000": {
                role: first["specialists"][role]["dissent_q1000"]
                for role in first["specialists"]
            },
        }
    assert (
        output["loyalist"]["orders"]["strategic_posture"]
        == "POSITIONAL_MANEUVER"
    )
    assert output["rebel"]["orders"]["strategic_posture"] == "PRESS"
    assert (
        output["loyalist"]["policy_source_sha256"]
        == output["rebel"]["policy_source_sha256"]
    )
    assert (
        output["loyalist"]["coefficient_table_sha256"]
        == output["rebel"]["coefficient_table_sha256"]
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "observation": OBSERVATION,
                "sides": output,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
