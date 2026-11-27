from __future__ import annotations

import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIMULATION_DIR = PROJECT_ROOT / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

import l1_runtime  # noqa: E402
from l1_embodiment import (  # noqa: E402
    EXPECTED_EMBODIMENT_IDS,
    validate_embodiment_registry,
)
from l1_instrumentation import build_logical_schematic  # noqa: E402
from l1_runtime import OrionL1Runtime, PreflightError  # noqa: E402
from l1_runtime_types import EmbodimentRunState  # noqa: E402


CLOUDBANK_SHA = "f572b8e8204a8fd48f3c8a55d3b1c3cec6603579"


def _init(*, seed: int = 1337, persist: bool = False, run_root=None):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=seed,
        persist=persist,
        run_root=run_root,
    )
    return runtime, state


@pytest.mark.unit
def test_preflight_binds_registry_but_keeps_full_embodied_resume_blocked():
    runtime = OrionL1Runtime()

    report = runtime.preflight()

    assert report["ready"] is True
    assert report["resume_ready"] is False
    assert report["run_created"] is False
    assert report["tick"] == 0
    assert runtime.state is None
    assert report["embodiment"]["registry_status"] == "verified"
    assert report["embodiment"]["provider_counts"] == {
        "bound": 0,
        "partial": 3,
        "unbound": 10,
        "blocked": 3,
    }
    assert len(report["embodiment"]["resume_blockers"]) == 16


@pytest.mark.unit
def test_run_state_projects_the_audited_station_architecture_without_activation():
    runtime, state = _init()

    assert state.manifest.runtime_contract_version == "1.3.0"
    assert state.embodiments.registry_status == "bound"
    assert state.embodiments.provider_readiness_status == "incomplete"
    assert set(state.embodiments.entities) == EXPECTED_EMBODIMENT_IDS
    assert all(
        not entity.causal_use_permitted
        for entity in state.embodiments.entities.values()
        if entity.provider_status in {"unbound", "blocked"}
    )

    archy = state.embodiments.entities["L1-EMB-RELAY-001"]
    assert archy.component == "ARCHY"
    assert archy.location == "Bridge Chamber, Deck C"
    assert archy.location_certainty == "STAGING"
    assert archy.authority_class == "architecture_and_feasibility_verifier"
    assert "human" not in archy.authority_class

    halo = state.embodiments.entities["L1-EMB-HALO"]
    assert halo.l1_kind == "continuity_system"
    assert halo.component.startswith("HALO continuity system-entity")

    command = state.embodiments.entities["L1-EMB-COMMAND-BRIDGE"]
    assert command.provider_status == "blocked"
    assert command.authority_class == "human_or_valid_delegated_authority"
    assert command.causal_use_permitted is False
    assert runtime.state is state
    assert state.manifest.tick == 0


@pytest.mark.unit
def test_existing_partial_providers_keep_narrow_causal_scopes():
    _, state = _init()

    fleet = state.embodiments.entities["L1-EMB-FLEET-DOCKING"]
    communications = state.embodiments.entities["L1-EMB-COMMUNICATIONS"]
    sensors = state.embodiments.entities["L1-EMB-SENSORS-OBSERVATORY"]

    assert fleet.provider_status == "partial"
    assert fleet.causal_scope == "existing_nonspatial_fleet_projection_only"
    assert communications.causal_scope == "existing_positive_delay_message_queue_only"
    assert sensors.causal_scope == "persisted_run_ledger_and_fleet_channels_only"
    assert "promoted_docking_topology" in fleet.blockers
    assert "environmental_provider" in sensors.blockers


@pytest.mark.unit
def test_relay_constellation_observation_is_read_only_and_includes_halo():
    runtime, state = _init()
    before = asdict(state.embodiments)

    observation = runtime.observe("relay constellation")

    assert observation["status"] == "available"
    assert observation["provider"] == "l1_embodiment_registry_projection"
    assert observation["causal_effect"] is False
    assert len(observation["records"]) == 6
    assert {record["component"] for record in observation["records"]} == {
        "ARCHY",
        "OPPY",
        "LIORA",
        "STARLING_AU",
        "RIVERTHREAD_808",
        "HALO continuity system-entity / HALO-PAS",
    }
    assert asdict(state.embodiments) == before
    assert state.manifest.tick == 0


@pytest.mark.unit
def test_logical_schematic_exposes_embodiments_but_keeps_layout_noncausal():
    runtime, state = _init()

    schematic = build_logical_schematic(state, runtime.baseline)

    nodes = {
        item["id"]: item
        for item in schematic["topology"]["nodes"]
        if item["id"].startswith("L1-EMB-")
    }
    assert set(nodes) == EXPECTED_EMBODIMENT_IDS
    assert nodes["L1-EMB-MCP-SHUTTLE-BAY"]["provider_status"] == "unbound"
    assert nodes["L1-EMB-MCP-SHUTTLE-BAY"]["causal_use_permitted"] is False
    assert nodes["L1-EMB-RELAY-003"]["location"] == "Communications Hub, Deck B"
    assert schematic["physical_deck_layout"]["status"] == "unresolved"
    assert schematic["physical_deck_layout"]["causal_use_permitted"] is False


@pytest.mark.unit
def test_missing_registry_fails_bootstrap_as_unavailable_not_empty(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setattr(
        l1_runtime,
        "EMBODIMENT_REGISTRY_PATH",
        tmp_path / "missing-embodiment-registry.json",
    )

    report = OrionL1Runtime().preflight()

    assert report["ready"] is False
    assert report["resume_ready"] is False
    assert "embodiment registry is unavailable" in report["blockers"]
    assert report["embodiment"]["registry_status"] == "unavailable"


@pytest.mark.unit
def test_registry_cannot_self_authorize_activation():
    registry = json.loads(
        (PROJECT_ROOT / "config" / "l1_embodiment_registry.json").read_text(
            encoding="utf-8"
        )
    )
    registry["activation_authority"] = True

    with pytest.raises(ValueError, match="cannot grant activation authority"):
        validate_embodiment_registry(registry)


@pytest.mark.unit
def test_unbound_provider_cannot_claim_causal_use():
    _, state = _init()
    archy = state.embodiments.entities["L1-EMB-RELAY-001"]
    state.embodiments.entities[archy.embodiment_id] = replace(
        archy,
        causal_use_permitted=True,
        causal_scope="architecture_mutation",
    )

    with pytest.raises(ValueError, match="unavailable embodiment provider"):
        state.embodiments.validate()


@pytest.mark.unit
def test_current_contract_rejects_missing_embodiment_projection(tmp_path: Path):
    runtime, state = _init(persist=True, run_root=tmp_path)
    path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("embodiments")
    payload["manifest"].pop("embodiment_registry_sha256")
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="persisted L1 run state"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_tick7_v1_1_migration_binds_embodiments_without_advancing(tmp_path: Path):
    runtime, state = _init(seed=1337, persist=True, run_root=tmp_path)
    for elapsed in (1, 1, 1, 1, 1, 1, 15):
        runtime.advance(elapsed_minutes=elapsed)
    path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["manifest"]["runtime_contract_version"] = "1.1.0"
    payload["manifest"]["status"] = "PAUSED"
    payload["manifest"]["fleet_authority_receipt_sha256"] = None
    payload["manifest"]["embodiment_registry_sha256"] = None
    payload.pop("fleet")
    payload.pop("embodiments")
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    before = path.read_bytes()

    loaded = OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)

    assert loaded.manifest.tick == 7
    assert loaded.manifest.station_cycle_minute == 21
    assert loaded.manifest.status == "PAUSED"
    assert loaded.manifest.runtime_contract_version == "1.3.0"
    assert loaded.fleet.process_position == 7
    assert loaded.embodiments.registry_status == "bound"
    assert loaded.embodiments.migrated_from_contract_version == "1.1.0"
    assert set(loaded.embodiments.entities) == EXPECTED_EMBODIMENT_IDS
    assert path.read_bytes() == before


@pytest.mark.unit
def test_pre_1_3_payload_cannot_smuggle_embodiment_state(tmp_path: Path):
    _, state = _init(persist=True, run_root=tmp_path)
    path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["manifest"]["runtime_contract_version"] = "1.2.0"
    payload["manifest"]["embodiment_registry_sha256"] = None
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="persisted L1 run state"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_unbound_embodiment_state_rejects_bound_fields():
    state = EmbodimentRunState.unbound()
    state.registry_id = "unexpected"

    with pytest.raises(ValueError, match="carries bound state"):
        state.validate()
