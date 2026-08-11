from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

from l1_runtime import OrionL1Runtime  # noqa: E402
from l1_runtime_types import l1_run_state_from_payload  # noqa: E402


CLOUDBANK_SHA = "f572b8e8204a8fd48f3c8a55d3b1c3cec6603579"


def _runtime_payload() -> dict:
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        persist=False,
    )
    return runtime.export_state()


@pytest.mark.unit
def test_contract_v11_payload_cannot_supply_fleet_state() -> None:
    payload = _runtime_payload()
    payload["manifest"]["runtime_contract_version"] = "1.1.0"

    with pytest.raises(
        ValueError,
        match="contract 1.1.0 persisted runs cannot supply fleet state",
    ):
        l1_run_state_from_payload(copy.deepcopy(payload))


@pytest.mark.unit
def test_contract_v11_payload_without_fleet_still_migrates_from_unbound_state() -> None:
    payload = _runtime_payload()
    payload["manifest"]["runtime_contract_version"] = "1.1.0"
    payload.pop("fleet")

    restored = l1_run_state_from_payload(payload)

    assert restored.manifest.runtime_contract_version == "1.1.0"
    assert restored.fleet.provider_status == "unbound"
    assert restored.fleet.entities == {}


@pytest.mark.unit
def test_non_ord_asset_cannot_deserialize_as_explicit_ord_adapter_state() -> None:
    payload = _runtime_payload()
    vessel = payload["fleet"]["entities"]["ORS-02"]
    vessel.update(
        {
            "status": "operating",
            "mission_state_class": "active_explicit_adapter",
            "docking_location_class": "station_proximity",
            "mission_id": "ord-physical-forged",
            "mission_class": "physical_reconnaissance",
        }
    )

    with pytest.raises(
        ValueError,
        match="explicit ORD adapter state is only valid for ORD assets",
    ):
        l1_run_state_from_payload(payload)
