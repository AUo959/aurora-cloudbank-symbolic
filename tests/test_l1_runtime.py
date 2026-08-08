from __future__ import annotations

import json
import sys
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
