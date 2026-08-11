#!/usr/bin/env python3
"""Validation and audit helpers for governed L1 staffing state."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, Tuple


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


def validate_observation_payload(
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


def action_personnel_ids(
    actions: list[Dict[str, Any]],
    action_types: set[str],
) -> set[str]:
    return {
        action["personnel_id"]
        for action in actions
        if action.get("action_type") in action_types
    }


def complement_delta_from_actions(actions: list[Dict[str, Any]]) -> int:
    arrivals = sum(
        action.get("action_type") in {"external_hire", "transfer_to_orion"}
        for action in actions
    )
    departures = sum(
        action.get("action_type") == "transfer_from_orion" for action in actions
    )
    return arrivals - departures


def validate_action_subject(action: Dict[str, Any]) -> None:
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


def resolved_personnel_ids(personnel: Dict[str, Any]) -> set[str]:
    return {
        record.personnel_id
        for record in personnel.values()
        if record.persona_resolution == "persona_resolved_run_state"
    }


def require_nonnegative_numeric(values: Tuple[float, ...], name: str) -> None:
    if any(
        isinstance(value, bool) or not isinstance(value, (int, float))
        for value in values
    ):
        raise ValueError(f"{name} must be numeric")
    if any(value < 0 for value in values):
        raise ValueError(f"{name} cannot be negative")


def require_nonnegative_integers(values: Tuple[int, ...], name: str) -> None:
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ValueError(f"{name} must be integers")
    if any(value < 0 for value in values):
        raise ValueError(f"{name} cannot be negative")


def validate_lifecycle_inputs(
    provenance: str,
    rationale: str,
    receipt_id: str,
) -> None:
    if not all(
        isinstance(value, str) and value.strip()
        for value in (provenance, rationale, receipt_id)
    ):
        raise ValueError("staffing lifecycle action requires provenance and authority")


def lifecycle_action(
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
        "action_id": stable_id(
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


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256(":".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


__all__ = [
    "ALLOWED_OBSERVATION_FIELDS",
    "PROHIBITED_PERSONA_FIELDS",
    "action_personnel_ids",
    "complement_delta_from_actions",
    "lifecycle_action",
    "require_nonnegative_integers",
    "require_nonnegative_numeric",
    "resolved_personnel_ids",
    "stable_id",
    "validate_action_subject",
    "validate_lifecycle_inputs",
    "validate_observation_payload",
]
