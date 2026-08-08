from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

import l1_runtime_support  # noqa: E402
from l1_fleet import (  # noqa: E402
    build_initial_fleet_state,
    docking_observation,
    drone_observation,
    fleet_observation,
    proximity_observation,
)
from l1_runtime import OrionL1Runtime, PreflightError  # noqa: E402
from l1_runtime_support import GovernanceError  # noqa: E402
from l1_runtime_types import FleetRunState, GovernanceReceipt  # noqa: E402
from modules.ord import MissionBrief, OrdPolicyEngine  # noqa: E402


CLOUDBANK_SHA = "f572b8e8204a8fd48f3c8a55d3b1c3cec6603579"
EXPECTED_FLEET_IDS = {
    "ORF-01",
    "ORS-01",
    "ORS-02",
    "ORS-03",
    "ORS-04",
    "ORS-05",
    "ORP-1",
    "ORP-2",
    "ORD-1",
    "ORD-2",
    "ORD-3",
    "ORD-4",
}


def _init(seed: int = 1337) -> OrionL1Runtime:
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=seed,
        persist=False,
    )
    return runtime


@pytest.mark.unit
def test_fleet_receipt_projects_modular_identities_without_stale_missions():
    runtime = _init()
    state = runtime.state

    assert state is not None
    assert runtime.preflight()["ready"] is True
    assert state.fleet.provider_status == "bound"
    assert state.fleet.projection_role == "runtime_projection_non_authoritative"
    assert set(state.fleet.entities) == EXPECTED_FLEET_IDS
    assert all(entity.status == "identity_projected" for entity in state.fleet.entities.values())
    assert all(entity.mission_state_class == "unassigned" for entity in state.fleet.entities.values())
    assert all(entity.mission_id is None for entity in state.fleet.entities.values())
    assert all(entity.mission_class is None for entity in state.fleet.entities.values())
    assert all(entity.docking_location_class == "unresolved" for entity in state.fleet.entities.values())

    serialized = json.dumps(runtime.export_state()["fleet"], sort_keys=True)
    assert "AURORA_PRIME" not in serialized
    assert "ORS-SURVEY-128" not in serialized
    assert "2025-" not in serialized


@pytest.mark.unit
@pytest.mark.parametrize("entities", ["not-a-list", ["not-an-object"]])
def test_fleet_receipt_rejects_malformed_entity_collections(entities):
    runtime = OrionL1Runtime()
    receipt = json.loads(json.dumps(runtime.fleet_receipt))
    receipt["entities"] = entities

    with pytest.raises(ValueError, match="list of objects"):
        build_initial_fleet_state(receipt)


@pytest.mark.unit
def test_fleet_world_process_is_deterministic_and_observation_non_central():
    observed = _init(seed=42)
    unobserved = _init(seed=42)

    for elapsed in (15, 7, 22):
        observed.observe("fleet")
        observed.observe("proximity")
        observed.observe("docking")
        observed.observe("drones")
        event_a = observed.advance(elapsed_minutes=elapsed)
        event_b = unobserved.advance(elapsed_minutes=elapsed)
        assert event_a["kind"] == event_b["kind"]

    assert observed.state is not None
    assert unobserved.state is not None
    assert asdict(observed.state.fleet) == asdict(unobserved.state.fleet)
    assert observed.state.fleet.process_position == 3
    assert all(
        transition["pilot_attention_influenced_probability"] is False
        for transition in observed.state.fleet.transitions
    )


@pytest.mark.unit
def test_bound_fleet_proximity_docking_and_drone_providers_are_explicit():
    runtime = _init()
    state = runtime.state
    assert state is not None

    fleet = runtime.observe("fleet")
    proximity = runtime.observe("proximity")
    docking = runtime.observe("docking")
    drones = runtime.observe("drones")

    assert fleet["status"] == "available"
    assert fleet["provider"] == "l1_run_fleet_state"
    assert len(fleet["records"]) == 12
    assert proximity["status"] == "available"
    assert all(record["exact_range_available"] is False for record in proximity["records"])
    assert docking["status"] == "available"
    assert all(record["trajectory_available"] is False for record in docking["records"])
    assert drones["status"] == "available"
    assert len(drones["records"]) == 4
    assert all(
        record["mcp_policy_dispatch_implies_flight"] is False
        for record in drones["records"]
    )
    assert state.manifest.tick == 0


@pytest.mark.unit
def test_unbound_fleet_providers_fail_as_unavailable_not_false_negative():
    runtime = _init()
    state = runtime.state
    assert state is not None
    state.fleet = FleetRunState.unbound()

    for provider in (
        fleet_observation,
        proximity_observation,
        docking_observation,
        drone_observation,
    ):
        observation = provider(state)
        assert observation["status"] == "unavailable"
        assert observation["reason"] == "provider_unbound"
        assert observation["records"] == []


@pytest.mark.unit
@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("authority_receipt_id", "unexpected-receipt"),
        ("projection_role", "runtime_projection_non_authoritative"),
        ("process_position", 1),
        ("elapsed_minutes", 1),
        ("transitions", [{"transition_id": "unexpected"}]),
        ("migrated_from_contract_version", "1.1.0"),
    ),
)
def test_unbound_fleet_state_rejects_bound_runtime_fields(field, value):
    fleet = FleetRunState.unbound()
    setattr(fleet, field, value)

    with pytest.raises(ValueError, match="carries bound runtime state"):
        fleet.validate()


@pytest.mark.unit
def test_fleet_receipt_hash_read_failure_becomes_preflight_blocker(monkeypatch):
    def unreadable_receipt(_path):
        raise OSError("unit-test read failure")

    monkeypatch.setattr(l1_runtime_support, "sha256_file", unreadable_receipt)

    report = OrionL1Runtime().preflight()

    assert report["ready"] is False
    assert "fleet authority receipt is unavailable or invalid" in report["blockers"]


@pytest.mark.unit
def test_ord_policy_requires_explicit_adapter_and_triplex_before_physical_flight():
    runtime = _init(seed=7)
    state = runtime.state
    assert state is not None
    before = asdict(state.fleet)
    order = OrdPolicyEngine().create_dispatch_order(
        MissionBrief(
            mission_id="mcp-policy-test",
            tool_name="create_branch",
            risk_level=0.8,
            destination="https://github.com/AUo959/example",
        )
    )

    assert order.drones_required
    assert asdict(state.fleet) == before
    proposal = runtime.propose_ord_physical_mission(
        order,
        physical_mission_class="physical_reconnaissance",
        docking_location_class="station_proximity",
    )
    assert proposal.status == "proposal_only"
    assert proposal.physical_execution is False
    assert asdict(state.fleet) == before

    incomplete = GovernanceReceipt(
        l3_glyph_arbitration=True,
        continuity_and_relay_verification=True,
        l1_human_consent=False,
        receipt_id="ord-incomplete",
        provenance="unit-test",
    )
    with pytest.raises(GovernanceError, match="ORD physical mission rejected"):
        runtime.activate_ord_physical_mission(proposal, receipt=incomplete)
    assert asdict(state.fleet) == before

    complete = GovernanceReceipt(
        l3_glyph_arbitration=True,
        continuity_and_relay_verification=True,
        l1_human_consent=True,
        receipt_id="ord-complete",
        provenance="unit-test",
    )
    event = runtime.activate_ord_physical_mission(proposal, receipt=complete)

    assert state.manifest.tick == 0
    assert event["cause"] == "explicit_ord_physical_mission_adapter"
    assert event["receipt_id"] == "ord-complete"
    for drone_id in proposal.drone_ids:
        entity = state.fleet.entities[drone_id]
        assert entity.status == "operating"
        assert entity.mission_state_class == "active_explicit_adapter"
        assert entity.mission_id == proposal.proposal_id
        assert entity.mission_class == "physical_reconnaissance"


@pytest.mark.unit
def test_persisted_fleet_replay_continues_at_same_position(tmp_path: Path):
    uninterrupted = OrionL1Runtime()
    resumed_source = OrionL1Runtime()
    uninterrupted.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=99,
        run_root=tmp_path / "uninterrupted",
    )
    resumed_state = resumed_source.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=99,
        run_root=tmp_path / "resumed",
    )

    for elapsed in (5, 8, 13):
        uninterrupted.advance(elapsed_minutes=elapsed)
        resumed_source.advance(elapsed_minutes=elapsed)
    uninterrupted.advance(elapsed_minutes=21)

    resumed = OrionL1Runtime()
    loaded = resumed.load_run(
        resumed_state.manifest.run_id,
        run_root=tmp_path / "resumed",
    )
    resumed.advance(elapsed_minutes=21)

    assert uninterrupted.state is not None
    assert asdict(loaded.fleet) == asdict(uninterrupted.state.fleet)
    assert loaded.manifest.tick == 4


@pytest.mark.unit
def test_pr1480_contract_run_migrates_at_paused_tick_seven_without_advancing(tmp_path: Path):
    source = OrionL1Runtime()
    state = source.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=314159,
        run_root=tmp_path,
    )
    for _ in range(7):
        source.advance(elapsed_minutes=3)
    expected_fleet = asdict(state.fleet)
    state_path = tmp_path / state.manifest.run_id / "state.json"
    legacy_payload = json.loads(state_path.read_text(encoding="utf-8"))
    legacy_payload["manifest"]["runtime_contract_version"] = "1.1.0"
    legacy_payload.pop("fleet")
    state_path.write_text(json.dumps(legacy_payload), encoding="utf-8")

    resumed = OrionL1Runtime()
    loaded = resumed.load_run(state.manifest.run_id, run_root=tmp_path)

    assert loaded.manifest.tick == 7
    assert loaded.manifest.station_cycle_minute == 21
    assert loaded.manifest.runtime_contract_version == "1.2.0"
    assert loaded.fleet.process_position == 7
    assert loaded.fleet.migrated_from_contract_version == "1.1.0"
    reconstructed = asdict(loaded.fleet)
    expected_fleet["migrated_from_contract_version"] = "1.1.0"
    assert reconstructed == expected_fleet
    persisted_after_load = json.loads(state_path.read_text(encoding="utf-8"))
    assert persisted_after_load["manifest"]["tick"] == 7
    assert persisted_after_load["manifest"]["station_cycle_minute"] == 21
    assert "fleet" not in persisted_after_load

    resumed.observe("fleet")
    persisted_after_observation = json.loads(state_path.read_text(encoding="utf-8"))
    assert persisted_after_observation["manifest"]["tick"] == 7
    assert persisted_after_observation["manifest"]["station_cycle_minute"] == 21
    assert persisted_after_observation["fleet"]["process_position"] == 7


@pytest.mark.unit
def test_persisted_stale_2025_mission_cannot_become_current_run_truth(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=88,
        run_root=tmp_path,
    )
    state_path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    liora = payload["fleet"]["entities"]["ORS-02"]
    liora["status"] = "operating"
    liora["mission_state_class"] = "active_routine"
    liora["docking_location_class"] = "external_operating_area"
    liora["mission_id"] = "ORS-SURVEY-128"
    liora["mission_class"] = "research_survey"
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="persisted L1 run state is unavailable or invalid"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_persisted_fleet_rejects_unsupported_current_state_source(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=88,
        run_root=tmp_path,
    )
    state_path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["fleet"]["entities"]["ORS-02"]["provenance"][
        "current_state_source"
    ] = "unverified_external_state"
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="persisted L1 run state is unavailable"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_replay_rejects_truncated_autonomous_event_ledger(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=55,
        run_root=tmp_path,
    )
    runtime.advance(elapsed_minutes=1)
    runtime.advance(elapsed_minutes=1)
    state_path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["events"] = payload["events"][:-1]
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="event ledger does not match run tick"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_replay_rejects_boolean_autonomous_event_tick(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=55,
        run_root=tmp_path,
    )
    runtime.advance(elapsed_minutes=1)
    state_path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload["events"][0]["tick"] = True
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="event ledger is not contiguous"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)
