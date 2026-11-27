#!/usr/bin/env python3
"""Strict deserialization helpers for persisted L1 staffing state."""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

from l1_staffing import PersonnelRecord, StaffingRunState, StaffingSeatRecord


def staffing_run_state_from_payload(value: Any) -> StaffingRunState:
    """Deserialize persisted staffing state without weakening its contracts."""
    if value is None:
        return StaffingRunState()
    payload = _mapping(value, "staffing")
    personnel_payload = _mapping(payload.get("personnel", {}), "staffing.personnel")
    state = StaffingRunState(
        personnel={
            _string(personnel_id, "staffing personnel key"): _personnel_from_payload(
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


__all__ = ["staffing_run_state_from_payload"]
