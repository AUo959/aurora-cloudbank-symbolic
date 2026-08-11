#!/usr/bin/env python3
"""Deterministic, run-scoped staffing state for the governed Orion L1 runtime."""

from __future__ import annotations

import copy
import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple


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
ALLOWED_OBSERVATION_FIELDS = {
    "collaboration_pattern",
    "communication_style",
    "demonstrated_skill",
    "operational_preference",
}
PROHIBITED_PERSONA_FIELDS = {
    "appearance",
    "biography",
    "family",
    "hobbies",
    "intimate_history",
    "narrative_arc",
    "personality",
}


@dataclass(frozen=True)
class StaffingDemand:
    """Evidence-backed demand signal; it is not itself authority to hire."""

    demand_id: str
    department: str
    role: str
    staffing_seat: str
    provenance: str
    required_capabilities: Tuple[str, ...] = ()
    workload_utilization: float = 0.0
    sustained_overtime_hours: float = 0.0
    uncovered_shifts: int = 0
    program_expansion: bool = False
    new_capability_requirement: bool = False
    attrition_or_leave: int = 0
    safety_constraint: bool = False
    separation_of_duties: bool = False
    succession_risk: bool = False
    engagement_class: str = "employee"

    def validate(self) -> None:
        strings = (
            self.demand_id,
            self.department,
            self.role,
            self.staffing_seat,
            self.provenance,
        )
        if not all(isinstance(value, str) and value.strip() for value in strings):
            raise ValueError(
                "staffing demand identity fields must be non-empty strings"
            )
        if self.engagement_class not in {"employee", "contractor", "visitor"}:
            raise ValueError("unsupported staffing engagement class")
        if not all(
            isinstance(value, str) and value.strip()
            for value in self.required_capabilities
        ):
            raise ValueError("required staffing capabilities must be non-empty strings")
        self._validate_numeric_signals()
        self._validate_boolean_signals()

    def _validate_numeric_signals(self) -> None:
        _require_nonnegative_numeric(
            (self.workload_utilization, self.sustained_overtime_hours),
            "staffing workload signals",
        )
        _require_nonnegative_integers(
            (self.uncovered_shifts, self.attrition_or_leave),
            "staffing demand counts",
        )

    def _validate_boolean_signals(self) -> None:
        signals = (
            self.program_expansion,
            self.new_capability_requirement,
            self.safety_constraint,
            self.separation_of_duties,
            self.succession_risk,
        )
        if not all(type(value) is bool for value in signals):
            raise ValueError("staffing constraint signals must be booleans")

    def reasons(self) -> Tuple[str, ...]:
        """Return deterministic institutional reasons that justify HR review."""
        signals = (
            (self.workload_utilization > 1.0, "workload_over_capacity"),
            (self.sustained_overtime_hours >= 8.0, "sustained_overtime"),
            (self.uncovered_shifts > 0, "uncovered_shifts"),
            (self.program_expansion, "program_expansion"),
            (
                self.new_capability_requirement,
                "new_technical_capability_requirement",
            ),
            (self.attrition_or_leave > 0, "attrition_or_leave"),
            (self.safety_constraint, "safety_or_ethics_constraint"),
            (self.separation_of_duties, "separation_of_duties"),
            (self.succession_risk, "succession_or_coverage_risk"),
        )
        return tuple(reason for active, reason in signals if active)


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
        if value is None:
            return cls()
        payload = _mapping(value, "staffing")
        personnel_payload = _mapping(payload.get("personnel", {}), "staffing.personnel")
        state = cls(
            personnel={
                _string(
                    personnel_id, "staffing personnel key"
                ): _personnel_from_payload(
                    record,
                    f"staffing.personnel.{personnel_id}",
                )
                for personnel_id, record in personnel_payload.items()
            },
            seats={
                _string(staffing_seat, "staffing seat key"): _seat_from_payload(
                    record,
                    f"staffing.seats.{staffing_seat}",
                )
                for staffing_seat, record in _mapping(
                    payload.get("seats", {}), "staffing.seats"
                ).items()
            },
            actions=_mapping_list(payload.get("actions", []), "staffing.actions"),
            human_complement_delta=_integer(
                payload.get("human_complement_delta", 0),
                "staffing.human_complement_delta",
            ),
            persona_resolved_delta=_integer(
                payload.get("persona_resolved_delta", 0),
                "staffing.persona_resolved_delta",
            ),
        )
        state.validate()
        return state


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


def transfer_personnel_from_orion(
    staffing: StaffingRunState,
    personnel_id: str,
    *,
    provenance: str,
    rationale: str,
    receipt_id: str,
    tick: int,
) -> Dict[str, Any]:
    """Record an outbound transfer without erasing the personnel identity."""
    _validate_lifecycle_inputs(provenance, rationale, receipt_id)
    personnel = staffing.personnel.get(personnel_id)
    if personnel is None:
        raise ValueError("outbound transfer references unknown personnel")
    if personnel.employment_status in {"departed", "off_station"}:
        raise ValueError("personnel is already off Orion")
    if personnel.employment_status == "contractor":
        raise ValueError("contractor departure does not change human crew complement")
    before = asdict(personnel)
    personnel.employment_status = "departed"
    personnel.shift_status = "transferred_off_station"
    personnel.workload_status = "not_assigned"
    action = _lifecycle_action(
        action_type="transfer_from_orion",
        subject_id=personnel_id,
        receipt_id=receipt_id,
        provenance=provenance,
        rationale=rationale,
        tick=tick,
        before=before,
        after=asdict(personnel),
    )
    staffing.actions.append(action)
    staffing.human_complement_delta -= 1
    staffing.validate()
    return copy.deepcopy(action)


def retire_staffing_seat(
    staffing: StaffingRunState,
    staffing_seat: str,
    *,
    provenance: str,
    rationale: str,
    receipt_id: str,
    tick: int,
) -> Dict[str, Any]:
    """Retire a vacant organizational seat while preserving its provenance."""
    _validate_lifecycle_inputs(provenance, rationale, receipt_id)
    seat = staffing.seats.get(staffing_seat)
    if seat is None:
        raise ValueError("seat retirement references unknown staffing seat")
    if seat.status == "retired":
        raise ValueError("staffing seat is already retired")
    if any(
        record.staffing_seat == staffing_seat
        and record.employment_status not in {"departed", "off_station"}
        for record in staffing.personnel.values()
    ):
        raise ValueError("occupied staffing seat cannot be retired")
    before = asdict(seat)
    seat.status = "retired"
    seat.retirement_provenance = provenance
    action = _lifecycle_action(
        action_type="seat_retirement",
        subject_id=staffing_seat,
        receipt_id=receipt_id,
        provenance=provenance,
        rationale=rationale,
        tick=tick,
        before=before,
        after=asdict(seat),
    )
    staffing.actions.append(action)
    staffing.validate()
    return copy.deepcopy(action)


def record_personnel_observation(
    staffing: StaffingRunState,
    personnel_id: str,
    observations: Dict[str, str],
    *,
    provenance: str,
) -> PersonnelRecord:
    """Add observed traits without synthesizing biography or canon persona."""
    record = staffing.personnel.get(personnel_id)
    if record is None:
        raise ValueError("staffing observation references unknown personnel")
    _validate_observation_payload(observations, provenance)
    record.observed_traits.update(copy.deepcopy(observations))
    if provenance not in record.observation_provenance:
        record.observation_provenance.append(provenance)
    record.persona_resolution = "partially_observed"
    record.validate()
    staffing.validate()
    return copy.deepcopy(record)


def mark_persona_resolved(
    staffing: StaffingRunState,
    personnel_id: str,
    *,
    receipt_id: str,
    tick: int,
) -> Dict[str, Any]:
    """Mark a run-state persona resolved only after observation and review."""
    record = staffing.personnel.get(personnel_id)
    if record is None:
        raise ValueError("persona resolution references unknown personnel")
    if not record.observed_traits:
        raise ValueError("persona resolution requires prior observations")
    if record.persona_resolution == "persona_resolved_run_state":
        raise ValueError("personnel persona is already resolved in this run")
    record.persona_resolution = "persona_resolved_run_state"
    staffing.persona_resolved_delta += 1
    action = {
        "action_id": _stable_id(
            "staffing-action",
            personnel_id,
            "persona-resolution",
            str(tick),
        ),
        "action_type": "persona_resolution",
        "demand_id": "progressive_persona_resolution",
        "personnel_id": personnel_id,
        "receipt_id": receipt_id,
        "tick": tick,
        "rationale": "Observed run-state traits reviewed for progressive resolution.",
        "canon_status": "run_state_not_canon_promotion",
    }
    staffing.actions.append(action)
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


def _validate_observation_payload(
    observations: Dict[str, str],
    provenance: str,
) -> None:
    if not provenance:
        raise ValueError("staffing observation requires provenance")
    if not observations:
        raise ValueError("staffing observation must contain evidence")
    if not set(observations).issubset(ALLOWED_OBSERVATION_FIELDS):
        raise ValueError("staffing observation contains unsupported persona fields")
    if not all(
        isinstance(value, str) and value.strip() for value in observations.values()
    ):
        raise ValueError("staffing observations must be non-empty strings")


def _action_personnel_ids(
    actions: List[Dict[str, Any]],
    action_types: set[str],
) -> set[str]:
    return {
        action["personnel_id"]
        for action in actions
        if action.get("action_type") in action_types
    }


def _complement_delta_from_actions(actions: List[Dict[str, Any]]) -> int:
    arrivals = sum(
        action.get("action_type") in {"external_hire", "transfer_to_orion"}
        for action in actions
    )
    departures = sum(
        action.get("action_type") == "transfer_from_orion" for action in actions
    )
    return arrivals - departures


def _validate_action_subject(action: Dict[str, Any]) -> None:
    action_type = action["action_type"]
    if action_type == "seat_retirement":
        if (
            not isinstance(action.get("staffing_seat"), str)
            or not action["staffing_seat"]
        ):
            raise ValueError("staffing seat action lacks seat identity")
        if action.get("personnel_id") is not None:
            raise ValueError("staffing seat action cannot carry personnel identity")
        return
    if not isinstance(action.get("personnel_id"), str) or not action["personnel_id"]:
        raise ValueError("staffing personnel action lacks personnel identity")


def _resolved_personnel_ids(
    personnel: Dict[str, PersonnelRecord],
) -> set[str]:
    return {
        record.personnel_id
        for record in personnel.values()
        if record.persona_resolution == "persona_resolved_run_state"
    }


def _require_nonnegative_numeric(values: Tuple[float, ...], name: str) -> None:
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        for value in values
    ):
        raise ValueError(f"{name} must be numeric")
    if any(value < 0 for value in values):
        raise ValueError(f"{name} cannot be negative")


def _require_nonnegative_integers(values: Tuple[int, ...], name: str) -> None:
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ValueError(f"{name} must be integers")
    if any(value < 0 for value in values):
        raise ValueError(f"{name} cannot be negative")


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
    return seat


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


def _validate_lifecycle_inputs(
    provenance: str,
    rationale: str,
    receipt_id: str,
) -> None:
    if not all(
        isinstance(value, str) and value.strip()
        for value in (provenance, rationale, receipt_id)
    ):
        raise ValueError("staffing lifecycle action requires provenance and authority")


def _lifecycle_action(
    *,
    action_type: str,
    subject_id: str,
    receipt_id: str,
    provenance: str,
    rationale: str,
    tick: int,
    before: Dict[str, Any],
    after: Dict[str, Any],
) -> Dict[str, Any]:
    personnel_id = subject_id if action_type == "transfer_from_orion" else None
    staffing_seat = subject_id if action_type == "seat_retirement" else None
    return {
        "action_id": _stable_id(
            "staffing-action",
            action_type,
            subject_id,
            str(tick),
        ),
        "action_type": action_type,
        "demand_id": f"staffing-lifecycle:{subject_id}",
        "personnel_id": personnel_id,
        "staffing_seat": staffing_seat,
        "receipt_id": receipt_id,
        "tick": tick,
        "rationale": rationale,
        "demand_provenance": provenance,
        "before": before,
        "after": after,
        "canon_status": "run_state",
    }


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _personnel_from_payload(value: Any, name: str) -> PersonnelRecord:
    payload = _mapping(value, name)
    observed = _mapping(payload.get("observed_traits", {}), f"{name}.observed_traits")
    record = PersonnelRecord(
        personnel_id=_string(payload.get("personnel_id"), f"{name}.personnel_id"),
        employment_status=_string(
            payload.get("employment_status"),
            f"{name}.employment_status",
        ),
        department=_string(payload.get("department"), f"{name}.department"),
        role=_string(payload.get("role"), f"{name}.role"),
        staffing_seat=_string(payload.get("staffing_seat"), f"{name}.staffing_seat"),
        clearance_envelope=_string_list(
            payload.get("clearance_envelope", []),
            f"{name}.clearance_envelope",
        ),
        shift_status=_string(payload.get("shift_status"), f"{name}.shift_status"),
        workload_status=_string(
            payload.get("workload_status"),
            f"{name}.workload_status",
        ),
        arrival_provenance=_string(
            payload.get("arrival_provenance"),
            f"{name}.arrival_provenance",
        ),
        capabilities=_string_list(
            payload.get("capabilities", []),
            f"{name}.capabilities",
        ),
        persona_resolution=_string(
            payload.get("persona_resolution", "minimal"),
            f"{name}.persona_resolution",
        ),
        observed_traits={
            _string(key, f"{name}.observed_traits key"): _string(
                item,
                f"{name}.observed_traits.{key}",
            )
            for key, item in observed.items()
        },
        observation_provenance=_string_list(
            payload.get("observation_provenance", []),
            f"{name}.observation_provenance",
        ),
    )
    record.validate()
    return record


def _seat_from_payload(value: Any, name: str) -> StaffingSeatRecord:
    payload = _mapping(value, name)
    record = StaffingSeatRecord(
        staffing_seat=_string(payload.get("staffing_seat"), f"{name}.staffing_seat"),
        department=_string(payload.get("department"), f"{name}.department"),
        role=_string(payload.get("role"), f"{name}.role"),
        status=_string(payload.get("status"), f"{name}.status"),
        creation_provenance=_string(
            payload.get("creation_provenance"),
            f"{name}.creation_provenance",
        ),
        retirement_provenance=_optional_string(
            payload.get("retirement_provenance"),
            f"{name}.retirement_provenance",
        ),
    )
    record.validate()
    return record


def _mapping_list(value: Any, name: str) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")
    return [
        copy.deepcopy(_mapping(item, f"{name}[{index}]"))
        for index, item in enumerate(value)
    ]


def _mapping(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def _string_list(value: Any, name: str) -> List[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ValueError(f"{name} must be an array of non-empty strings")
    return list(value)


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _optional_string(value: Any, name: str) -> Optional[str]:
    if value is None:
        return None
    return _string(value, name)


def _integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


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
