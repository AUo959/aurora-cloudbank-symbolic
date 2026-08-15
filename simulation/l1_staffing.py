#!/usr/bin/env python3
"""Deterministic, run-scoped staffing state for the governed Orion L1 runtime."""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from l1_staffing_lifecycle import (
    mark_persona_resolved,
    record_personnel_observation,
    retire_staffing_seat,
    transfer_personnel_from_orion,
)
from l1_staffing_types import StaffingDemand
from l1_staffing_validation import (
    ALLOWED_OBSERVATION_FIELDS,
    PROHIBITED_PERSONA_FIELDS,
    action_personnel_ids as _action_personnel_ids,
    complement_delta_from_actions as _complement_delta_from_actions,
    resolved_personnel_ids as _resolved_personnel_ids,
    stable_id as _stable_id,
    validate_action_subject as _validate_action_subject,
)


PLANNED_STAFFING_ACTIONS = {
    "internal_reassignment",
    "acting_promotion",
    "transfer_to_orion",
    "external_hire",
    "contractor_assignment",
}
STAFFING_ACTIONS = PLANNED_STAFFING_ACTIONS | {
    "transfer_from_orion",
    "seat_retirement",
}
PERSONNEL_STATUSES = {
    "active",
    "acting",
    "off_station",
    "contractor",
    "visitor",
    "departed",
}
STAFFING_SEAT_STATUSES = {"active", "retired"}
PERSONA_RESOLUTION_LEVELS = {
    "minimal",
    "partially_observed",
    "persona_resolved_run_state",
}


@dataclass
class PersonnelRecord:
    """Minimum operational record, deliberately separate from a rich persona."""

    personnel_id: str
    employment_status: str
    department: str
    role: str
    staffing_seat: str
    clearance_envelope: List[str]
    shift_status: str
    workload_status: str
    arrival_provenance: str
    capabilities: List[str] = field(default_factory=list)
    persona_resolution: str = "minimal"
    observed_traits: Dict[str, str] = field(default_factory=dict)
    observation_provenance: List[str] = field(default_factory=list)

    def validate(self) -> None:
        strings = (
            self.personnel_id,
            self.department,
            self.role,
            self.staffing_seat,
            self.shift_status,
            self.workload_status,
            self.arrival_provenance,
        )
        if not all(isinstance(value, str) and value.strip() for value in strings):
            raise ValueError("personnel operational fields must be non-empty strings")
        if self.employment_status not in PERSONNEL_STATUSES:
            raise ValueError("unsupported personnel employment status")
        if self.persona_resolution not in PERSONA_RESOLUTION_LEVELS:
            raise ValueError("unsupported persona resolution level")
        self._validate_string_list(self.clearance_envelope, "clearance envelope")
        self._validate_string_list(self.capabilities, "personnel capabilities")
        self._validate_observations()

    @staticmethod
    def _validate_string_list(values: List[str], name: str) -> None:
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError(f"{name} must contain only non-empty strings")
        if len(values) != len(set(values)):
            raise ValueError(f"{name} cannot contain duplicates")

    def _validate_observations(self) -> None:
        if PROHIBITED_PERSONA_FIELDS.intersection(self.observed_traits):
            raise ValueError(
                "personnel observations contain prohibited persona synthesis"
            )
        if not set(self.observed_traits).issubset(ALLOWED_OBSERVATION_FIELDS):
            raise ValueError("personnel observations contain unsupported fields")
        if not all(
            isinstance(value, str) and value.strip()
            for value in self.observed_traits.values()
        ):
            raise ValueError("personnel observations must be non-empty strings")
        self._validate_string_list(
            self.observation_provenance,
            "personnel observation provenance",
        )
        if self.persona_resolution != "minimal" and not self.observed_traits:
            raise ValueError("resolved personnel state requires observations")


@dataclass
class StaffingSeatRecord:
    """Run-scoped organizational seat with an explicit lifecycle."""

    staffing_seat: str
    department: str
    role: str
    status: str
    creation_provenance: str
    retirement_provenance: Optional[str] = None

    def validate(self) -> None:
        strings = (
            self.staffing_seat,
            self.department,
            self.role,
            self.creation_provenance,
        )
        if not all(isinstance(value, str) and value.strip() for value in strings):
            raise ValueError("staffing seat fields must be non-empty strings")
        if self.status not in STAFFING_SEAT_STATUSES:
            raise ValueError("unsupported staffing seat status")
        self._validate_lifecycle_provenance()

    def _validate_lifecycle_provenance(self) -> None:
        if self.status == "retired" and not self.retirement_provenance:
            raise ValueError("retired staffing seat requires provenance")
        if self.status == "active" and self.retirement_provenance is not None:
            raise ValueError("active staffing seat cannot carry retirement provenance")


@dataclass(frozen=True)
class StaffingDecision:
    demand_id: str
    action_type: str
    personnel_id: Optional[str]
    rationale: str
    reasons: Tuple[str, ...]

    def validate(self) -> None:
        if not self.demand_id or not self.rationale:
            raise ValueError("staffing decision identity and rationale are required")
        if self.action_type not in PLANNED_STAFFING_ACTIONS | {"no_action"}:
            raise ValueError("unsupported staffing decision action")
        if (
            self.action_type
            in {
                "internal_reassignment",
                "acting_promotion",
                "transfer_to_orion",
            }
            and not self.personnel_id
        ):
            raise ValueError("internal staffing action requires personnel identity")
        if (
            self.action_type in {"external_hire", "contractor_assignment", "no_action"}
            and self.personnel_id is not None
        ):
            raise ValueError(
                "new/no-action staffing decision cannot preselect personnel"
            )


@dataclass
class StaffingRunState:
    """Run-scoped staffing ledger; missing biographies never imply missing staff."""

    personnel: Dict[str, PersonnelRecord] = field(default_factory=dict)
    seats: Dict[str, StaffingSeatRecord] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    human_complement_delta: int = 0
    persona_resolved_delta: int = 0

    def validate(self) -> None:
        self._validate_counter_types()
        self._validate_records()
        self._validate_actions()
        self._validate_counters()

    def _validate_counter_types(self) -> None:
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (self.human_complement_delta,)
        ):
            raise ValueError("human complement delta must be an integer")
        if (
            isinstance(self.persona_resolved_delta, bool)
            or not isinstance(self.persona_resolved_delta, int)
            or self.persona_resolved_delta < 0
        ):
            raise ValueError("persona-resolved delta must be a non-negative integer")

    def _validate_records(self) -> None:
        for personnel_id, record in self.personnel.items():
            if personnel_id != record.personnel_id:
                raise ValueError("personnel mapping key does not match record identity")
            record.validate()
        for staffing_seat, record in self.seats.items():
            if staffing_seat != record.staffing_seat:
                raise ValueError("staffing seat mapping key does not match identity")
            record.validate()

    def _validate_counters(self) -> None:
        complement_delta = _complement_delta_from_actions(self.actions)
        resolved_ids = _resolved_personnel_ids(self.personnel)
        resolution_sources = _action_personnel_ids(
            self.actions,
            {"persona_resolution"},
        )
        if self.human_complement_delta != complement_delta:
            raise ValueError("human complement delta does not match staffing actions")
        if self.persona_resolved_delta != len(resolved_ids):
            raise ValueError("persona-resolved delta does not match personnel records")
        if resolved_ids != resolution_sources:
            raise ValueError("resolved personnel state lacks resolution audit action")
        if self.persona_resolved_delta > len(self.personnel):
            raise ValueError(
                "persona-resolved staffing count exceeds personnel records"
            )

    def _validate_actions(self) -> None:
        action_ids = set()
        for action in self.actions:
            required = (
                "action_id",
                "action_type",
                "demand_id",
                "receipt_id",
                "rationale",
            )
            if not all(
                isinstance(action.get(key), str) and action[key] for key in required
            ):
                raise ValueError("staffing action lacks required audit identity")
            if action["action_type"] not in STAFFING_ACTIONS | {"persona_resolution"}:
                raise ValueError("staffing action type is unsupported")
            _validate_action_subject(action)
            if action["action_id"] in action_ids:
                raise ValueError("staffing action IDs must be unique")
            action_ids.add(action["action_id"])

    @classmethod
    def from_payload(cls, value: Any) -> "StaffingRunState":
        from l1_staffing_serialization import staffing_run_state_from_payload

        return staffing_run_state_from_payload(value)


def plan_staffing_action(
    staffing: StaffingRunState,
    demand: StaffingDemand,
) -> StaffingDecision:
    """Prefer existing institutional capacity before creating a new person."""
    staffing.validate()
    demand.validate()
    reasons = demand.reasons()
    if not reasons:
        decision = StaffingDecision(
            demand_id=demand.demand_id,
            action_type="no_action",
            personnel_id=None,
            rationale="No evidence-backed staffing threshold is met.",
            reasons=(),
        )
        decision.validate()
        return decision
    if _seat_is_occupied(staffing, demand.staffing_seat):
        decision = StaffingDecision(
            demand_id=demand.demand_id,
            action_type="no_action",
            personnel_id=None,
            rationale="The requested staffing seat is already occupied.",
            reasons=reasons,
        )
        decision.validate()
        return decision
    capabilities = set(demand.required_capabilities)
    active = _eligible_records(staffing, capabilities, {"active", "acting"})
    reassignment = _first_reassignment(active, demand)
    if reassignment is not None:
        return _decision(demand, "internal_reassignment", reassignment, reasons)
    promotion = _first_promotion(active, demand)
    if promotion is not None:
        return _decision(demand, "acting_promotion", promotion, reasons)
    transfer = _first_transfer(staffing, capabilities)
    if transfer is not None:
        return _decision(demand, "transfer_to_orion", transfer, reasons)
    action_type = (
        "contractor_assignment"
        if demand.engagement_class in {"contractor", "visitor"}
        else "external_hire"
    )
    return _decision(demand, action_type, None, reasons)


def apply_staffing_decision(
    staffing: StaffingRunState,
    demand: StaffingDemand,
    decision: StaffingDecision,
    *,
    receipt_id: str,
    tick: int,
) -> Dict[str, Any]:
    """Apply the deterministic plan and append one provenance-rich audit event."""
    decision.validate()
    expected = plan_staffing_action(staffing, demand)
    if decision != expected:
        raise ValueError("staffing decision does not match deterministic demand plan")
    if decision.action_type == "no_action":
        raise ValueError("no-action staffing decision cannot be applied")
    if not receipt_id:
        raise ValueError("staffing action requires governance receipt identity")
    before = _record_snapshot(staffing, decision.personnel_id)
    seat_before = _seat_snapshot(staffing, demand.staffing_seat)
    seat = _ensure_active_seat(staffing, demand)
    personnel = _apply_personnel_change(staffing, demand, decision)
    action = {
        "action_id": _stable_id(
            "staffing-action",
            demand.demand_id,
            str(tick),
            str(len(staffing.actions)),
        ),
        "action_type": decision.action_type,
        "demand_id": demand.demand_id,
        "personnel_id": personnel.personnel_id,
        "staffing_seat": demand.staffing_seat,
        "receipt_id": receipt_id,
        "tick": tick,
        "reasons": list(decision.reasons),
        "rationale": decision.rationale,
        "demand_provenance": demand.provenance,
        "before": before,
        "after": asdict(personnel),
        "seat_before": seat_before,
        "seat_after": asdict(seat),
        "canon_status": "run_state",
    }
    staffing.actions.append(action)
    if decision.action_type in {"external_hire", "transfer_to_orion"}:
        staffing.human_complement_delta += 1
    staffing.validate()
    return copy.deepcopy(action)


def _eligible_records(
    staffing: StaffingRunState,
    capabilities: set[str],
    statuses: set[str],
) -> List[PersonnelRecord]:
    return sorted(
        (
            record
            for record in staffing.personnel.values()
            if record.employment_status in statuses
            and record.workload_status != "overloaded"
            and capabilities.issubset(record.capabilities)
        ),
        key=lambda record: record.personnel_id,
    )


def _first_reassignment(
    active: List[PersonnelRecord],
    demand: StaffingDemand,
) -> Optional[PersonnelRecord]:
    return next(
        (record for record in active if record.department != demand.department),
        None,
    )


def _first_promotion(
    active: List[PersonnelRecord],
    demand: StaffingDemand,
) -> Optional[PersonnelRecord]:
    return next(
        (
            record
            for record in active
            if record.department == demand.department and record.role != demand.role
        ),
        None,
    )


def _first_transfer(
    staffing: StaffingRunState,
    capabilities: set[str],
) -> Optional[PersonnelRecord]:
    return next(
        iter(_eligible_records(staffing, capabilities, {"off_station"})),
        None,
    )


def _decision(
    demand: StaffingDemand,
    action_type: str,
    personnel: Optional[PersonnelRecord],
    reasons: Tuple[str, ...],
) -> StaffingDecision:
    personnel_id = personnel.personnel_id if personnel is not None else None
    target = personnel_id or "a minimal operational personnel record"
    decision = StaffingDecision(
        demand_id=demand.demand_id,
        action_type=action_type,
        personnel_id=personnel_id,
        rationale=(
            f"{action_type} selected for {demand.department}/{demand.staffing_seat}; "
            f"institutional evidence={','.join(reasons)}; target={target}."
        ),
        reasons=reasons,
    )
    decision.validate()
    return decision


def _apply_personnel_change(
    staffing: StaffingRunState,
    demand: StaffingDemand,
    decision: StaffingDecision,
) -> PersonnelRecord:
    if decision.personnel_id is None:
        personnel = _minimal_personnel_record(staffing, demand, decision.action_type)
        staffing.personnel[personnel.personnel_id] = personnel
        return personnel
    personnel = staffing.personnel[decision.personnel_id]
    personnel.department = demand.department
    personnel.role = demand.role
    personnel.staffing_seat = demand.staffing_seat
    if decision.action_type == "acting_promotion":
        personnel.employment_status = "acting"
    else:
        personnel.employment_status = "active"
    return personnel


def _ensure_active_seat(
    staffing: StaffingRunState,
    demand: StaffingDemand,
) -> StaffingSeatRecord:
    seat = staffing.seats.get(demand.staffing_seat)
    if seat is None:
        seat = StaffingSeatRecord(
            staffing_seat=demand.staffing_seat,
            department=demand.department,
            role=demand.role,
            status="active",
            creation_provenance=demand.provenance,
        )
        staffing.seats[seat.staffing_seat] = seat
        return seat
    if seat.status != "active":
        raise ValueError("retired staffing seat cannot receive personnel")
    if seat.department != demand.department or seat.role != demand.role:
        raise ValueError("staffing demand conflicts with the existing seat definition")
    if _seat_is_occupied(staffing, demand.staffing_seat):
        raise ValueError("occupied staffing seat cannot receive another person")
    return seat


def _seat_is_occupied(staffing: StaffingRunState, staffing_seat: str) -> bool:
    return any(
        record.staffing_seat == staffing_seat
        and record.employment_status not in {"departed", "off_station"}
        for record in staffing.personnel.values()
    )


def _minimal_personnel_record(
    staffing: StaffingRunState,
    demand: StaffingDemand,
    action_type: str,
) -> PersonnelRecord:
    personnel_id = _stable_id(
        "L1-HR",
        demand.demand_id,
        demand.department,
        demand.staffing_seat,
        str(len(staffing.personnel)),
    )
    status = (
        demand.engagement_class if action_type == "contractor_assignment" else "active"
    )
    return PersonnelRecord(
        personnel_id=personnel_id,
        employment_status=status,
        department=demand.department,
        role=demand.role,
        staffing_seat=demand.staffing_seat,
        clearance_envelope=["unassigned_pending_review"],
        shift_status="assignment_pending",
        workload_status="unmeasured",
        arrival_provenance=demand.provenance,
        capabilities=list(demand.required_capabilities),
    )


def _record_snapshot(
    staffing: StaffingRunState,
    personnel_id: Optional[str],
) -> Optional[Dict[str, Any]]:
    if personnel_id is None:
        return None
    return asdict(staffing.personnel[personnel_id])


def _seat_snapshot(
    staffing: StaffingRunState,
    staffing_seat: str,
) -> Optional[Dict[str, Any]]:
    seat = staffing.seats.get(staffing_seat)
    return None if seat is None else asdict(seat)


__all__ = [
    "PersonnelRecord",
    "StaffingDecision",
    "StaffingDemand",
    "StaffingRunState",
    "StaffingSeatRecord",
    "apply_staffing_decision",
    "mark_persona_resolved",
    "plan_staffing_action",
    "record_personnel_observation",
    "retire_staffing_seat",
    "transfer_personnel_from_orion",
]
