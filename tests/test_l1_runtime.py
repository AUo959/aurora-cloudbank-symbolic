from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

SIMULATION_DIR = Path(__file__).resolve().parents[1] / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

from l1_runtime import (  # noqa: E402
    GovernanceError,
    GovernanceReceipt,
    OrionL1Runtime,
    PopulationSnapshot,
    PreflightError,
)

CLOUDBANK_SHA = "f572b8e8204a8fd48f3c8a55d3b1c3cec6603579"


def _baseline_payload() -> dict:
    path = Path(__file__).resolve().parents[1] / "config" / "l1_runtime_baseline.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.unit
def test_preflight_is_ready_and_does_not_advance_or_create_run():
    runtime = OrionL1Runtime()

    report = runtime.preflight()

    assert report["ready"] is True
    assert report["blockers"] == []
    assert report["tick"] == 0
    assert report["run_created"] is False
    assert report["orbital_locus"]["siting_class"] == "lagrange_point"
    assert report["orbital_locus"]["exact_point_resolved"] is False
    assert (
        report["orbital_locus"]["communications_latency"][
            "modeled_one_way_light_time_seconds"
        ]
        == 5
    )
    assert runtime.state is None


@pytest.mark.unit
def test_init_creates_tick_zero_run_outside_repo(tmp_path: Path):
    runtime = OrionL1Runtime()

    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )

    assert state.manifest.tick == 0
    assert state.manifest.status == "INITIALIZED"
    assert state.events == []
    assert state.world_state["pilot"] == {
        "role": "Pilot",
        "residency": "Earth",
        "l1_entity": False,
    }
    assert "orion_orbital_locus" not in state.manifest.active_quarantines
    assert "orion_exact_lagrange_point" in state.manifest.active_quarantines
    assert "current_crew_81" in state.manifest.active_quarantines
    assert state.world_state["orbital_locus"]["siting_class"] == "lagrange_point"
    assert state.world_state["orbital_locus"]["certainty"] == "CANON"
    persisted = tmp_path / state.manifest.run_id / "state.json"
    assert persisted.is_file()
    payload = json.loads(persisted.read_text(encoding="utf-8"))
    assert payload["manifest"]["tick"] == 0


@pytest.mark.unit
def test_init_rejects_canonrec_revision_override():
    runtime = OrionL1Runtime()

    with pytest.raises(PreflightError, match="override does not match"):
        runtime.init_run(
            cloudbank_revision=CLOUDBANK_SHA,
            canonrec_revision="0" * 40,
            seed=1337,
            persist=False,
        )

    assert runtime.state is None


@pytest.mark.unit
def test_observation_does_not_advance_or_change_autonomous_event_sequence(tmp_path: Path):
    with_observation = OrionL1Runtime()
    without_observation = OrionL1Runtime()

    with_observation.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=42,
        run_root=tmp_path / "a",
    )
    without_observation.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=42,
        run_root=tmp_path / "b",
    )

    observation = with_observation.observe("Engineering")
    assert observation["pilot_embodied"] is False
    assert observation["generated_world_event"] is False
    assert with_observation.state is not None
    assert with_observation.state.manifest.tick == 0

    event_a = with_observation.advance(elapsed_minutes=17)
    event_b = without_observation.advance(elapsed_minutes=17)

    assert event_a["kind"] == event_b["kind"]
    assert event_a["summary"] == event_b["summary"]
    assert event_a["pilot_attention_influenced_probability"] is False


@pytest.mark.unit
def test_ambiguous_operator_input_is_not_silently_transmitted(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=7,
        run_root=tmp_path,
    )

    result = runtime.route_operator_input("I wonder what Thorne thinks")

    assert result["kind"] == "control"
    assert result["action"] == "no_op"
    assert result["transmitted"] is False
    assert runtime.state is not None
    assert runtime.state.communications == []


@pytest.mark.unit
def test_explicit_communication_is_queued_without_automatic_l1_action(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=8,
        run_root=tmp_path,
    )

    result = runtime.route_operator_input(
        "Please forward this to Commander Thorne.",
        explicit_kind="communication",
    )

    message = result["message"]
    assert message["origin"] == "Earth"
    assert message["sender_id"] == "pilot"
    assert message["automatic_l1_action"] is False
    assert message["status"] == "queued"
    assert message["modeled_one_way_light_time_seconds"] == 5
    assert message["latency_certainty"] == "APPROX"


@pytest.mark.unit
def test_communication_requires_positive_advancement_before_delivery(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=8,
        run_root=tmp_path,
    )

    result = runtime.send_communication(
        "Cmdr Thorne, this is Pilot - Earth side.",
        target="CMD_001",
    )
    message = result["message"]

    assert message["status"] == "queued"
    assert runtime.state is not None
    assert runtime.state.manifest.tick == 0
    assert runtime.state.station_records == []

    runtime.advance(elapsed_minutes=1)

    assert message["status"] == "delivered_to_station"
    assert message["delivered_tick"] == 1
    assert message["latency"]["exact_value_known"] is False
    delivery_record = runtime.state.station_records[-1]
    assert delivery_record.subject == f"communication:{message['message_id']}"
    assert delivery_record.provenance == "earth_to_orion_communications_ledger"
    assert delivery_record.value["target"] == "CMD_001"


@pytest.mark.unit
def test_persisted_run_can_reload_and_continue_deterministically(tmp_path: Path):
    uninterrupted = OrionL1Runtime()
    reloaded_source = OrionL1Runtime()
    uninterrupted.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=42,
        run_root=tmp_path / "uninterrupted",
    )
    reloaded_state = reloaded_source.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=42,
        run_root=tmp_path / "reloaded",
    )

    uninterrupted.advance(elapsed_minutes=1)
    uninterrupted_second = uninterrupted.advance(elapsed_minutes=1)
    reloaded_source.advance(elapsed_minutes=1)

    continued = OrionL1Runtime()
    loaded = continued.load_run(
        reloaded_state.manifest.run_id,
        run_root=tmp_path / "reloaded",
    )
    continued_second = continued.advance(elapsed_minutes=1)

    assert loaded.manifest.tick == 2
    assert continued_second["kind"] == uninterrupted_second["kind"]
    assert continued_second["summary"] == uninterrupted_second["summary"]


@pytest.mark.unit
def test_load_run_rejects_manifest_path_mismatch(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=42,
        run_root=tmp_path,
    )
    payload_path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["manifest"]["run_id"] = "3b62eecf-5a9e-4784-920d-f83f15da950f"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="does not match its persistence path"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_load_run_rejects_malformed_communication_ledger(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=42,
        run_root=tmp_path,
    )
    runtime.send_communication("Status request.", target="CMD_001")
    payload_path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["communications"][0]["message_id"] = ""
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="message_id must be a non-empty string"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_commander_response_is_character_caused_grounded_and_delayed(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )
    inbound = runtime.send_communication(
        "Cmdr Thorne, please report station operations and status.",
        target="CMD_001",
    )["message"]

    runtime.advance(elapsed_minutes=1)

    assert runtime.state is not None
    responses = [
        item
        for item in runtime.state.communications
        if item.get("reply_to_message_id") == inbound["message_id"]
    ]
    assert len(responses) == 1
    response = responses[0]
    assert response["sender_id"] == "CMD_001"
    assert response["sender_name"] == "Commander Alex Thorne"
    assert response["origin"] == "Orion Station"
    assert response["target"] == "pilot"
    assert response["status"] == "queued"
    assert response["pilot_directed_content"] is False
    assert response["response_policy"] == "bounded_character_action_v1"
    assert "reviewed the current watch record" in response["content"]
    assert "scheduled maintenance queue" in response["content"]
    assert "No emergency is recorded" in response["content"]
    assert "will not turn either into an estimate" in response["content"]
    assert len(runtime.state.character_actions) == 1
    action = runtime.state.character_actions[0]
    assert response["caused_by_action_id"] == action["action_id"]
    assert action["selected_action"] == "review_watch_and_report"
    assert action["perceived_intents"] == ["station_operations_status"]
    assert "station_operations" in {
        item["id"] for item in action["duty_drivers"]
    }
    assert "quiet_authority" in {
        item["id"] for item in action["principle_drivers"]
    }
    assert action["commitments"] == [
        {
            "commitment": "monitor_maintenance_queue",
            "status": "active",
            "owner": "CMD_001",
        }
    ]
    assert any(
        item["kind"] == "review_station_records"
        for item in action["operational_steps"]
    )
    assert any(
        item.subject.startswith("character_action:")
        for item in runtime.state.character_knowledge["CMD_001"]
    )
    assert runtime.state.manifest.tick == 1

    runtime.advance(elapsed_minutes=1)

    assert response["status"] == "delivered_to_earth"
    assert response["delivered_tick"] == 2
    testimony = runtime.state.pilot_knowledge[-1]
    assert testimony.epistemic_class == "testimony"
    assert testimony.provenance == "station_to_earth_communications_ledger"
    assert testimony.value["sender_id"] == "CMD_001"


@pytest.mark.unit
def test_commander_actor_cannot_read_pilot_observation_aperture(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )
    private_focus = "PILOT_PRIVATE_APERTURE_MARKER"
    observation = runtime.observe(private_focus)
    assert observation["focus"] == private_focus

    runtime.send_communication("Status report, Commander.", target="CMD_001")
    runtime.advance(elapsed_minutes=1)

    assert runtime.state is not None
    assert private_focus in json.dumps(
        [asdict(item) for item in runtime.state.runtime_observations]
    )
    assert private_focus not in json.dumps(runtime.state.character_actions)
    assert private_focus not in json.dumps(
        [asdict(item) for item in runtime.state.character_knowledge["CMD_001"]]
    )


@pytest.mark.unit
def test_load_run_rejects_character_action_with_missing_response(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )
    runtime.send_communication("Status report.", target="CMD_001")
    runtime.advance(elapsed_minutes=1)
    payload_path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["character_actions"][0]["response_message_id"] = "missing-message"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="unavailable communication"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_load_run_rejects_inconsistent_character_response_causality(tmp_path: Path):
    runtime = OrionL1Runtime()
    state = runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )
    runtime.send_communication("Status report.", target="CMD_001")
    runtime.advance(elapsed_minutes=1)
    payload_path = tmp_path / state.manifest.run_id / "state.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    response = next(
        item
        for item in payload["communications"]
        if item.get("direction") == "station_to_earth"
    )
    response["caused_by_action_id"] = "tampered-action"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="causality is inconsistent"):
        OrionL1Runtime().load_run(state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_commander_response_is_not_duplicated_or_misdirected(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1337,
        run_root=tmp_path,
    )
    runtime.send_communication("Status request for Engineering.", target="SYS_001")

    runtime.advance(elapsed_minutes=1)
    runtime.advance(elapsed_minutes=1)

    assert runtime.state is not None
    assert not any(
        item.get("sender_id") == "CMD_001" for item in runtime.state.communications
    )

    inbound = runtime.send_communication("Status report, Commander.", target="CMD_001")[
        "message"
    ]
    runtime.advance(elapsed_minutes=1)
    runtime.advance(elapsed_minutes=1)
    runtime.advance(elapsed_minutes=1)

    responses = [
        item
        for item in runtime.state.communications
        if item.get("reply_to_message_id") == inbound["message_id"]
    ]
    assert len(responses) == 1


@pytest.mark.unit
def test_locus_preflight_rejects_broad_unknown_status(tmp_path: Path):
    baseline = _baseline_payload()
    baseline["orbital_locus"]["status"] = "quarantined_conflict"
    path = tmp_path / "stale-locus-baseline.json"
    path.write_text(json.dumps(baseline), encoding="utf-8")

    report = OrionL1Runtime(baseline_path=path).preflight()

    assert report["ready"] is False
    assert "Lagrange-point siting class is not resolved" in report["blockers"]


@pytest.mark.unit
def test_locus_preflight_rejects_zero_latency_model(tmp_path: Path):
    baseline = _baseline_payload()
    baseline["orbital_locus"]["communications_latency"][
        "modeled_one_way_light_time_seconds"
    ] = 0
    path = tmp_path / "zero-latency-baseline.json"
    path.write_text(json.dumps(baseline), encoding="utf-8")

    report = OrionL1Runtime(baseline_path=path).preflight()

    assert report["ready"] is False
    assert (
        "communications latency model must be a positive integer" in report["blockers"]
    )


@pytest.mark.unit
def test_epistemic_states_do_not_collapse_into_each_other(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=9,
        run_root=tmp_path,
    )

    belief = runtime.record_character_belief(
        "CMD_001",
        "maintenance_window_safe",
        False,
        confidence=0.6,
        provenance="character_assessment",
    )
    observation = runtime.observe("maintenance records")

    assert belief.epistemic_class == "character_belief"
    assert runtime.state is not None
    assert runtime.state.character_knowledge["CMD_001"][0].value is False
    assert runtime.state.station_records == []
    assert runtime.state.runtime_observations[0].epistemic_class == "runtime_observation"
    assert runtime.state.pilot_knowledge[0].epistemic_class == "pilot_knowledge"
    assert observation["instrumentation"] is True


@pytest.mark.unit
def test_observation_payloads_are_isolated_across_epistemic_ledgers(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=91,
        run_root=tmp_path,
    )

    observation = runtime.observe("Engineering")
    assert runtime.state is not None
    runtime_value = runtime.state.runtime_observations[0].value
    pilot_value = runtime.state.pilot_knowledge[0].value

    observation["focus"] = "caller annotation"
    runtime_value["records"].append({"caller": "runtime ledger mutation"})

    assert runtime_value["focus"] == "Engineering"
    assert pilot_value["focus"] == "Engineering"
    assert pilot_value["records"] == []


@pytest.mark.unit
def test_population_schema_allows_large_complement_with_smaller_resolved_subset():
    snapshot = PopulationSnapshot(
        crew_capacity=250,
        current_human_crew_complement=81,
        identified_human_records=35,
        persona_resolved_humans=20,
        missing_named_human_claim=False,
        system_entities={"aurora_core": 1, "l1_relay_agents": 5},
    )

    snapshot.validate()


@pytest.mark.unit
def test_population_baseline_rejects_non_integer_numeric_fields(tmp_path: Path):
    baseline = _baseline_payload()
    baseline["population"]["crew_capacity"] = "250"
    path = tmp_path / "invalid-baseline.json"
    path.write_text(json.dumps(baseline), encoding="utf-8")

    with pytest.raises(ValueError, match="crew_capacity must be an integer or null"):
        OrionL1Runtime(baseline_path=path)


@pytest.mark.unit
def test_population_baseline_rejects_boolean_system_entity_count(tmp_path: Path):
    baseline = _baseline_payload()
    baseline["population"]["system_entities"]["aurora_core"] = True
    path = tmp_path / "invalid-system-count.json"
    path.write_text(json.dumps(baseline), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="system_entities.aurora_core must be an integer",
    ):
        OrionL1Runtime(baseline_path=path)


@pytest.mark.unit
def test_false_missing_human_claim_is_not_active():
    runtime = OrionL1Runtime()

    assert runtime.population.identified_human_records == 35
    assert runtime.population.missing_named_human_claim is False
    assert runtime.population.historical_aggregate_claims[
        "declared_humans_36"
    ].startswith("retired")


@pytest.mark.unit
def test_actionable_event_fails_closed_without_complete_triplex_receipt(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=10,
        run_root=tmp_path,
    )
    incomplete = GovernanceReceipt(
        l3_glyph_arbitration=True,
        continuity_and_relay_verification=True,
        l1_human_consent=False,
        receipt_id="triplex-test-incomplete",
        provenance="unit-test",
    )

    with pytest.raises(GovernanceError):
        runtime.apply_governed_event(
            subject="exceptional_action",
            value="executed",
            receipt=incomplete,
        )

    assert runtime.state is not None
    assert "exceptional_action" not in runtime.state.world_state


@pytest.mark.unit
@pytest.mark.parametrize(
    "invalid_stage",
    ["false", 1, None],
)
def test_triplex_receipt_rejects_non_boolean_stages(invalid_stage):
    with pytest.raises(ValueError, match="stages must be booleans"):
        GovernanceReceipt(
            l3_glyph_arbitration=invalid_stage,
            continuity_and_relay_verification=True,
            l1_human_consent=True,
            receipt_id="triplex-invalid-type",
            provenance="unit-test",
        )


@pytest.mark.unit
def test_complete_triplex_receipt_can_apply_run_scoped_fact(tmp_path: Path):
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=11,
        run_root=tmp_path,
    )
    complete = GovernanceReceipt(
        l3_glyph_arbitration=True,
        continuity_and_relay_verification=True,
        l1_human_consent=True,
        receipt_id="triplex-test-complete",
        provenance="unit-test",
    )

    record = runtime.apply_governed_event(
        subject="exceptional_action",
        value="executed",
        receipt=complete,
    )

    assert record.canon_status == "run_state"
    assert runtime.state is not None
    assert runtime.state.world_state["exceptional_action"] == "executed"
    assert runtime.state.governance_receipts == [complete]
    assert runtime.state.governed_records == [record]
    exported = runtime.export_state()
    assert exported["governance_receipts"][0] == {
        "l3_glyph_arbitration": True,
        "continuity_and_relay_verification": True,
        "l1_human_consent": True,
        "receipt_id": "triplex-test-complete",
        "provenance": "unit-test",
    }
    assert exported["governed_records"][0]["record_id"] == record.record_id
    event = exported["events"][-1]
    assert event["record_id"] == record.record_id
    assert event["receipt_id"] == complete.receipt_id

    persisted = tmp_path / runtime.state.manifest.run_id / "state.json"
    payload = json.loads(persisted.read_text(encoding="utf-8"))
    assert payload["governance_receipts"] == exported["governance_receipts"]
    assert payload["governed_records"] == exported["governed_records"]


@pytest.mark.unit
def test_run_persistence_rejects_repository_paths():
    runtime = OrionL1Runtime()

    with pytest.raises(PreflightError):
        runtime.init_run(
            cloudbank_revision=CLOUDBANK_SHA,
            seed=12,
            run_root=Path(__file__).resolve().parents[1] / ".aurora" / "runs",
        )
