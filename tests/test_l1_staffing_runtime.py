from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


SIMULATION_DIR = Path(__file__).resolve().parents[1] / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

from l1_runtime import OrionL1Runtime, PreflightError  # noqa: E402
from l1_runtime_support import GovernanceError  # noqa: E402
from l1_runtime_types import GovernanceReceipt  # noqa: E402
from l1_staffing import (  # noqa: E402
    PersonnelRecord,
    StaffingDemand,
)


CLOUDBANK_SHA = "f572b8e8204a8fd48f3c8a55d3b1c3cec6603579"


def _receipt(receipt_id: str = "triplex-staffing-complete") -> GovernanceReceipt:
    return GovernanceReceipt(
        l3_glyph_arbitration=True,
        continuity_and_relay_verification=True,
        l1_human_consent=True,
        receipt_id=receipt_id,
        provenance="issue-1453-test",
    )


def _incomplete_receipt() -> GovernanceReceipt:
    return GovernanceReceipt(
        l3_glyph_arbitration=True,
        continuity_and_relay_verification=True,
        l1_human_consent=False,
        receipt_id="triplex-staffing-incomplete",
        provenance="issue-1453-test",
    )


def _demand(
    demand_id: str = "staffing-demand-engineering-1",
    **overrides: object,
) -> StaffingDemand:
    payload: dict[str, object] = {
        "demand_id": demand_id,
        "department": "Engineering",
        "role": "Systems Reliability Engineer",
        "staffing_seat": "ENG-RELIABILITY-02",
        "provenance": "runtime:workload-ledger:tick-0",
        "required_capabilities": ("systems_reliability",),
        "workload_utilization": 1.25,
        "sustained_overtime_hours": 10.0,
    }
    payload.update(overrides)
    return StaffingDemand(**payload)  # type: ignore[arg-type]


def _runtime(*, run_root: Path | None = None) -> OrionL1Runtime:
    runtime = OrionL1Runtime()
    runtime.init_run(
        cloudbank_revision=CLOUDBANK_SHA,
        seed=1453,
        run_root=run_root,
        persist=run_root is not None,
    )
    return runtime


def _operational_record(
    personnel_id: str,
    *,
    department: str,
    role: str,
    status: str = "active",
) -> PersonnelRecord:
    return PersonnelRecord(
        personnel_id=personnel_id,
        employment_status=status,
        department=department,
        role=role,
        staffing_seat=f"{department.upper()}-SEAT-1",
        clearance_envelope=["L1_OPERATIONAL"],
        shift_status="alpha_shift",
        workload_status="available",
        arrival_provenance="canonical-roster-projection:test",
        capabilities=["systems_reliability"],
    )


@pytest.mark.unit
def test_need_driven_hire_stays_minimal_and_updates_only_complement(tmp_path: Path):
    runtime = _runtime(run_root=tmp_path)
    demand = _demand()

    decision = runtime.plan_staffing(demand)
    action = runtime.apply_staffing(demand, decision, receipt=_receipt())

    assert decision.action_type == "external_hire"
    assert runtime.state is not None
    record = runtime.state.staffing.personnel[action["personnel_id"]]
    assert record.persona_resolution == "minimal"
    assert record.observed_traits == {}
    assert record.clearance_envelope == ["unassigned_pending_review"]
    assert not hasattr(record, "biography")
    assert not hasattr(record, "personality")
    assert runtime.state.staffing.human_complement_delta == 1
    assert runtime.state.staffing.persona_resolved_delta == 0
    assert runtime.state.world_state["population"]["run_staffing"] == {
        "operational_personnel_records": 1,
        "human_complement_delta": 1,
        "persona_resolved_delta": 0,
        "active_staffing_seats": 1,
        "retired_staffing_seats": 0,
    }
    assert action["seat_before"] is None
    assert action["seat_after"]["status"] == "active"

    loaded = OrionL1Runtime().load_run(
        runtime.state.manifest.run_id,
        run_root=tmp_path,
    )
    assert loaded.staffing.personnel[action["personnel_id"]] == record


@pytest.mark.unit
def test_internal_reassignment_and_promotion_precede_external_hiring():
    runtime = _runtime()
    assert runtime.state is not None
    staffing = runtime.state.staffing
    staffing.personnel["PERSONNEL-TRANSFER"] = _operational_record(
        "PERSONNEL-TRANSFER",
        department="Operations",
        role="Reliability Specialist",
    )

    reassignment = runtime.plan_staffing(_demand())
    assert reassignment.action_type == "internal_reassignment"
    assert reassignment.personnel_id == "PERSONNEL-TRANSFER"

    staffing.personnel.clear()
    staffing.personnel["PERSONNEL-PROMOTION"] = _operational_record(
        "PERSONNEL-PROMOTION",
        department="Engineering",
        role="Junior Reliability Engineer",
    )
    promotion = runtime.plan_staffing(_demand(demand_id="staffing-demand-promotion"))
    assert promotion.action_type == "acting_promotion"
    assert promotion.personnel_id == "PERSONNEL-PROMOTION"

    staffing.personnel.clear()
    staffing.personnel["PERSONNEL-TRANSFER-IN"] = _operational_record(
        "PERSONNEL-TRANSFER-IN",
        department="Engineering",
        role="Reliability Specialist",
        status="off_station",
    )
    transfer = runtime.plan_staffing(_demand(demand_id="staffing-demand-transfer"))
    assert transfer.action_type == "transfer_to_orion"
    assert transfer.personnel_id == "PERSONNEL-TRANSFER-IN"


@pytest.mark.unit
def test_internal_action_is_audited_without_inflating_complement():
    runtime = _runtime()
    assert runtime.state is not None
    record = _operational_record(
        "PERSONNEL-EXISTING",
        department="Operations",
        role="Reliability Specialist",
    )
    runtime.state.staffing.personnel[record.personnel_id] = record
    demand = _demand()

    decision = runtime.plan_staffing(demand)
    action = runtime.apply_staffing(demand, decision, receipt=_receipt())

    assert action["before"]["department"] == "Operations"
    assert action["after"]["department"] == "Engineering"
    assert runtime.state.staffing.human_complement_delta == 0
    assert runtime.state.staffing.persona_resolved_delta == 0


@pytest.mark.unit
def test_contractor_assignment_does_not_change_human_complement():
    runtime = _runtime()
    demand = _demand(
        demand_id="staffing-demand-contractor",
        engagement_class="contractor",
    )

    decision = runtime.plan_staffing(demand)
    action = runtime.apply_staffing(demand, decision, receipt=_receipt())

    assert decision.action_type == "contractor_assignment"
    assert runtime.state is not None
    assert (
        runtime.state.staffing.personnel[action["personnel_id"]].employment_status
        == "contractor"
    )
    assert runtime.state.staffing.human_complement_delta == 0


@pytest.mark.unit
def test_occupied_seat_turns_repeated_demand_into_no_action():
    runtime = _runtime()
    demand = _demand()
    first_decision = runtime.plan_staffing(demand)
    runtime.apply_staffing(demand, first_decision, receipt=_receipt())

    repeated = runtime.plan_staffing(
        _demand(demand_id="staffing-demand-engineering-repeated")
    )

    assert repeated.action_type == "no_action"
    assert repeated.rationale == "The requested staffing seat is already occupied."
    assert runtime.state is not None
    assert len(runtime.state.staffing.personnel) == 1
    assert runtime.state.staffing.human_complement_delta == 1


@pytest.mark.unit
def test_new_capability_gap_and_visitor_assignment_are_explicit_need_signals():
    runtime = _runtime()
    demand = _demand(
        demand_id="staffing-demand-specialist-visitor",
        workload_utilization=0.8,
        sustained_overtime_hours=0.0,
        new_capability_requirement=True,
        engagement_class="visitor",
    )

    decision = runtime.plan_staffing(demand)
    action = runtime.apply_staffing(demand, decision, receipt=_receipt())

    assert decision.reasons == ("new_technical_capability_requirement",)
    assert runtime.state is not None
    assert (
        runtime.state.staffing.personnel[action["personnel_id"]].employment_status
        == "visitor"
    )
    assert runtime.state.staffing.human_complement_delta == 0


@pytest.mark.unit
@pytest.mark.parametrize("engagement_class", ["contractor", "visitor"])
def test_non_complement_departure_cannot_decrement_crew(
    engagement_class: str,
):
    runtime = _runtime()
    demand = _demand(
        demand_id=f"staffing-demand-{engagement_class}-departure",
        engagement_class=engagement_class,
    )
    action = runtime.apply_staffing(
        demand,
        runtime.plan_staffing(demand),
        receipt=_receipt(),
    )

    with pytest.raises(ValueError, match="non-complement personnel departure"):
        runtime.transfer_personnel_off_station(
            action["personnel_id"],
            provenance="hr:departure-order:tick-0",
            rationale="End the temporary Orion assignment.",
            receipt=_receipt("triplex-temporary-departure"),
        )

    assert runtime.state is not None
    assert runtime.state.staffing.human_complement_delta == 0
    assert (
        runtime.state.staffing.personnel[action["personnel_id"]].employment_status
        == engagement_class
    )


@pytest.mark.unit
def test_transfer_from_orion_and_vacant_seat_retirement_are_audited(
    tmp_path: Path,
):
    runtime = _runtime(run_root=tmp_path)
    demand = _demand()
    hired = runtime.apply_staffing(
        demand,
        runtime.plan_staffing(demand),
        receipt=_receipt("triplex-hire"),
    )

    with pytest.raises(ValueError, match="occupied staffing seat"):
        runtime.retire_staffing_seat(
            demand.staffing_seat,
            provenance="hr:seat-review:tick-0",
            rationale="Retire an unneeded reliability seat.",
            receipt=_receipt("triplex-premature-retirement"),
        )

    transfer = runtime.transfer_personnel_off_station(
        hired["personnel_id"],
        provenance="hr:transfer-order:tick-0",
        rationale="Transfer accepted into the Earth-side reliability office.",
        receipt=_receipt("triplex-transfer-out"),
    )
    assert transfer["action_type"] == "transfer_from_orion"
    assert runtime.state is not None
    assert runtime.state.staffing.human_complement_delta == 0
    assert (
        runtime.state.staffing.personnel[hired["personnel_id"]].employment_status
        == "departed"
    )

    retirement = runtime.retire_staffing_seat(
        demand.staffing_seat,
        provenance="hr:seat-review:tick-0",
        rationale="The transferred function no longer requires an Orion seat.",
        receipt=_receipt("triplex-seat-retirement"),
    )
    assert retirement["action_type"] == "seat_retirement"
    assert retirement["personnel_id"] is None
    assert runtime.state.staffing.seats[demand.staffing_seat].status == "retired"
    assert runtime.state.world_state["population"]["run_staffing"] == {
        "operational_personnel_records": 1,
        "human_complement_delta": 0,
        "persona_resolved_delta": 0,
        "active_staffing_seats": 0,
        "retired_staffing_seats": 1,
    }

    loaded = OrionL1Runtime().load_run(
        runtime.state.manifest.run_id,
        run_root=tmp_path,
    )
    assert loaded.staffing.seats[demand.staffing_seat].status == "retired"


@pytest.mark.unit
def test_progressive_resolution_requires_observation_and_separate_authority():
    runtime = _runtime()
    demand = _demand()
    action = runtime.apply_staffing(
        demand,
        runtime.plan_staffing(demand),
        receipt=_receipt("triplex-hire"),
    )
    personnel_id = action["personnel_id"]

    with pytest.raises(ValueError, match="requires prior observations"):
        runtime.resolve_personnel_persona(
            personnel_id,
            receipt=_receipt("triplex-premature-resolution"),
        )
    with pytest.raises(ValueError, match="unsupported persona fields"):
        runtime.observe_personnel(
            personnel_id,
            {"biography": "Invented childhood"},
            provenance="runtime-observation:test",
        )

    observed = runtime.observe_personnel(
        personnel_id,
        {
            "demonstrated_skill": "restored relay redundancy under supervision",
            "communication_style": "uses concise incident handoffs",
        },
        provenance="runtime-observation:incident-7",
    )
    assert observed.persona_resolution == "partially_observed"
    assert runtime.state is not None
    assert runtime.state.staffing.persona_resolved_delta == 0
    assert runtime.state.staffing.human_complement_delta == 1

    resolved = runtime.resolve_personnel_persona(
        personnel_id,
        receipt=_receipt("triplex-persona-review"),
    )
    assert resolved["canon_status"] == "run_state_not_canon_promotion"
    assert runtime.state.staffing.persona_resolved_delta == 1
    assert runtime.state.staffing.human_complement_delta == 1

    observed_again = runtime.observe_personnel(
        personnel_id,
        {"operational_preference": "documents rollback points before changes"},
        provenance="runtime-observation:incident-8",
    )
    assert observed_again.persona_resolution == "persona_resolved_run_state"
    assert runtime.state.staffing.persona_resolved_delta == 1


@pytest.mark.unit
def test_staffing_action_requires_evidence_and_complete_triplex():
    runtime = _runtime()
    no_need = _demand(
        demand_id="staffing-demand-no-threshold",
        workload_utilization=0.8,
        sustained_overtime_hours=0.0,
    )
    no_action = runtime.plan_staffing(no_need)
    assert no_action.action_type == "no_action"
    with pytest.raises(ValueError, match="no-action"):
        runtime.apply_staffing(no_need, no_action, receipt=_receipt())

    demand = _demand()
    with pytest.raises(GovernanceError, match="staffing action rejected"):
        runtime.apply_staffing(
            demand,
            runtime.plan_staffing(demand),
            receipt=_incomplete_receipt(),
        )
    assert runtime.state is not None
    assert runtime.state.staffing.personnel == {}
    assert runtime.state.staffing.actions == []


@pytest.mark.unit
@pytest.mark.parametrize("tamper", ["receipt", "counter", "persona", "event"])
def test_persisted_staffing_state_fails_closed_when_evidence_is_tampered(
    tmp_path: Path,
    tamper: str,
):
    runtime = _runtime(run_root=tmp_path)
    demand = _demand()
    action = runtime.apply_staffing(
        demand,
        runtime.plan_staffing(demand),
        receipt=_receipt(),
    )
    assert runtime.state is not None
    state_path = tmp_path / runtime.state.manifest.run_id / "state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    if tamper == "receipt":
        payload["governance_receipts"] = []
    elif tamper == "counter":
        payload["staffing"]["human_complement_delta"] = 0
    elif tamper == "event":
        payload["events"] = [
            event
            for event in payload["events"]
            if event.get("kind") != "governed_staffing_action"
        ]
    else:
        record = payload["staffing"]["personnel"][action["personnel_id"]]
        record["persona_resolution"] = "persona_resolved_run_state"
        record["observed_traits"] = {"demonstrated_skill": "forged"}
        payload["staffing"]["persona_resolved_delta"] = 1
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PreflightError, match="persisted (L1 run state|staffing)"):
        OrionL1Runtime().load_run(runtime.state.manifest.run_id, run_root=tmp_path)


@pytest.mark.unit
def test_pre_staffing_contract_state_loads_without_new_staffing_projection(
    tmp_path: Path,
):
    runtime = _runtime(run_root=tmp_path)
    assert runtime.state is not None
    state_path = tmp_path / runtime.state.manifest.run_id / "state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    payload.pop("staffing")
    payload["world_state"]["population"].pop("run_staffing", None)
    state_path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = OrionL1Runtime().load_run(
        runtime.state.manifest.run_id,
        run_root=tmp_path,
    )
    assert loaded.staffing.personnel == {}
    assert loaded.staffing.seats == {}
