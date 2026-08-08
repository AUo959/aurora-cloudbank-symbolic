from __future__ import annotations

import sys
from pathlib import Path


SIMULATION_DIR = Path(__file__).resolve().parents[1] / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

from l1_instrumentation import (  # noqa: E402
    build_logical_schematic,
    build_sensor_snapshot,
)
from l1_runtime import OrionL1Runtime  # noqa: E402


CLOUDBANK_SHA = "f572b8e8204a8fd48f3c8a55d3b1c3cec6603579"


def test_sensor_snapshot_is_bound_to_run_ledger_without_physical_claims(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )
    runtime.advance(elapsed_minutes=1)

    snapshot = build_sensor_snapshot(state)

    assert snapshot["source"] == "persisted_run_ledger"
    assert snapshot["live_within_simulation"] is True
    assert snapshot["physical_hardware_feed"] is False
    assert snapshot["reading"]["provider_bound"] is True
    assert snapshot["reading"]["values"]["tick"] == 1.0
    assert snapshot["reading"]["values"]["event_count"] == 1.0
    assert "environmental" in snapshot["unavailable_physical_channels"]


def test_logical_schematic_quarantines_stale_physical_layout_claims(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )

    schematic = build_logical_schematic(state, runtime.baseline)

    assert schematic["status"] == "runtime_projection_non_authoritative"
    assert schematic["station"]["siting_class"] == "lagrange_point"
    assert schematic["pilot"]["residency"] == "Earth"
    assert schematic["command_endpoint"] == {
        "id": "CMD_001",
        "name": "Alex Thorne",
        "role": "Commander, Orion Station",
    }
    assert schematic["physical_deck_layout"]["status"] == "unresolved"
    serialized = str(schematic)
    assert "38600" not in serialized
    assert "Pilot Station" not in serialized
