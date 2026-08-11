#!/usr/bin/env python3
"""Lifecycle operations for governed L1 staffing state."""

from __future__ import annotations

import copy
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict

from l1_staffing_validation import (
    lifecycle_action,
    stable_id,
    validate_lifecycle_inputs,
    validate_observation_payload,
)

if TYPE_CHECKING:
    from l1_staffing import PersonnelRecord, StaffingRunState


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
    validate_lifecycle_inputs(provenance, rationale, receipt_id)
    personnel = staffing.personnel.get(personnel_id)
    if personnel is None:
        raise ValueError("outbound transfer references unknown personnel")
    if personnel.employment_status in {"departed", "off_station"}:
        raise ValueError("personnel is already off Orion")
    if personnel.employment_status in {"contractor", "visitor"}:
        raise ValueError(
            "non-complement personnel departure cannot change human crew complement"
        )
    before = asdict(personnel)
    personnel.employment_status = "departed"
    personnel.shift_status = "transferred_off_station"
    personnel.workload_status = "not_assigned"
    action = lifecycle_action(
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
    validate_lifecycle_inputs(provenance, rationale, receipt_id)
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
    action = lifecycle_action(
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
    validate_observation_payload(observations, provenance)
    record.observed_traits.update(copy.deepcopy(observations))
    if provenance not in record.observation_provenance:
        record.observation_provenance.append(provenance)
    if record.persona_resolution == "minimal":
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
        "action_id": stable_id(
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


__all__ = [
    "mark_persona_resolved",
    "record_personnel_observation",
    "retire_staffing_seat",
    "transfer_personnel_from_orion",
]
