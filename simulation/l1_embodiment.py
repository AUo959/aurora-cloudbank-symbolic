#!/usr/bin/env python3
"""Evidence-bound Orion L1 embodiment projection and readiness assessment."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Iterable, Optional

from l1_runtime_types import EmbodimentRunState, EmbodimentState, L1RunState


EXPECTED_EMBODIMENT_IDS = frozenset(
    {
        "L1-EMB-MCP-SHUTTLE-BAY",
        "L1-EMB-COMMAND-BRIDGE",
        "L1-EMB-RELAY-001",
        "L1-EMB-RELAY-002",
        "L1-EMB-RELAY-003",
        "L1-EMB-RELAY-004",
        "L1-EMB-RELAY-005",
        "L1-EMB-HALO",
        "L1-EMB-GUMAS-LABS",
        "L1-EMB-FLEET-DOCKING",
        "L1-EMB-ORD-DISPATCH",
        "L1-EMB-MEMORY-STORAGE",
        "L1-EMB-COMMUNICATIONS",
        "L1-EMB-CREW-LIFE",
        "L1-EMB-ETHICS-TRIPLEX",
        "L1-EMB-SENSORS-OBSERVATORY",
    }
)


def validate_embodiment_registry(registry: Dict[str, Any]) -> None:
    """Reject malformed, activating, incomplete, or over-authoritative registries."""
    if registry.get("registry_id") != "ORION-L1-EMBODIMENT-REGISTRY-0.1":
        raise ValueError("embodiment registry identity is unsupported")
    if registry.get("schema_version") != 1:
        raise ValueError("embodiment registry schema version is unsupported")
    if registry.get("status") != "recovery_projection_noncanonical":
        raise ValueError("embodiment registry exceeds recovery-projection authority")
    if registry.get("activation_authority") is not False:
        raise ValueError("embodiment registry cannot grant activation authority")
    if registry.get("projection_role") != "runtime_projection_non_authoritative":
        raise ValueError("embodiment registry projection role is unsupported")
    if (
        registry.get("resume_policy")
        != "all_required_components_provider_bound_and_authority_gates_satisfied"
    ):
        raise ValueError("embodiment registry resume policy is unsupported")
    records = _registry_records(registry)
    identifiers = [record.embodiment_id for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("embodiment registry contains duplicate identities")
    if set(identifiers) != EXPECTED_EMBODIMENT_IDS:
        raise ValueError("embodiment registry does not contain the audited identity set")


def build_initial_embodiment_state(
    registry: Dict[str, Any],
    registry_sha256: str,
) -> EmbodimentRunState:
    """Bind the audited mapping without activating any missing provider."""
    validate_embodiment_registry(registry)
    records = _registry_records(registry)
    entities = {record.embodiment_id: record for record in records}
    state = EmbodimentRunState(
        registry_status="bound",
        registry_id=registry["registry_id"],
        registry_sha256=registry_sha256,
        projection_role=registry["projection_role"],
        provider_readiness_status=_provider_readiness(records),
        entities=entities,
    )
    state.validate()
    return state


def validate_embodiment_projection(
    state: EmbodimentRunState,
    registry: Dict[str, Any],
    registry_sha256: str,
) -> None:
    """Verify persisted projection identity against the exact registry bytes."""
    validate_embodiment_registry(registry)
    state.validate()
    if state.registry_status != "bound":
        raise ValueError("embodiment registry is not bound")
    if state.registry_id != registry.get("registry_id"):
        raise ValueError("embodiment registry identity does not match runtime")
    if state.registry_sha256 != registry_sha256:
        raise ValueError("embodiment registry digest does not match runtime")
    expected = build_initial_embodiment_state(registry, registry_sha256)
    if state.entities != expected.entities:
        raise ValueError("persisted embodiment projection differs from its registry")
    if state.provider_readiness_status != expected.provider_readiness_status:
        raise ValueError("persisted embodiment readiness differs from its registry")


def assess_embodiment_readiness(registry: Dict[str, Any]) -> Dict[str, Any]:
    """Report resume blockers without treating them as absent station systems."""
    validate_embodiment_registry(registry)
    records = _registry_records(registry)
    blockers = [
        {
            "embodiment_id": record.embodiment_id,
            "component": record.component,
            "provider_status": record.provider_status,
            "blockers": list(record.blockers),
        }
        for record in records
        if record.required_for_resume and record.provider_status != "bound"
    ]
    counts = {
        status: sum(record.provider_status == status for record in records)
        for status in ("bound", "partial", "unbound", "blocked")
    }
    return {
        "registry_id": registry["registry_id"],
        "registry_status": "verified",
        "projection_role": registry["projection_role"],
        "ready": not blockers,
        "provider_counts": counts,
        "resume_blockers": blockers,
        "causal_component_ids": [
            record.embodiment_id
            for record in records
            if record.causal_use_permitted
        ],
    }


def embodiment_observation(
    state: L1RunState,
    focus: str,
) -> Optional[Dict[str, Any]]:
    """Expose embodiment/provider state without advancing or fabricating it."""
    if state.embodiments.registry_status != "bound":
        return _unavailable_observation(state, focus)
    normalized = " ".join(focus.strip().lower().replace("_", " ").split())
    records = _records_for_focus(state.embodiments.entities.values(), normalized)
    if records is None:
        return None
    return {
        "tick": state.manifest.tick,
        "status": "available",
        "provider": "l1_embodiment_registry_projection",
        "projection_role": state.embodiments.projection_role,
        "provider_readiness_status": state.embodiments.provider_readiness_status,
        "causal_effect": False,
        "records": [asdict(record) for record in records],
    }


def _registry_records(registry: Dict[str, Any]) -> list[EmbodimentState]:
    payload = registry.get("embodiments")
    if not isinstance(payload, list):
        raise ValueError("embodiment registry records must be a JSON array")
    records = [_record_from_payload(item, index) for index, item in enumerate(payload)]
    for record in records:
        record.validate()
    return records


def _record_from_payload(value: Any, index: int) -> EmbodimentState:
    if not isinstance(value, dict):
        raise ValueError(f"embodiment registry record {index} must be an object")
    try:
        return EmbodimentState(**value)
    except TypeError as exc:
        raise ValueError(f"embodiment registry record {index} has invalid fields") from exc


def _provider_readiness(records: Iterable[EmbodimentState]) -> str:
    return (
        "ready"
        if all(
            not record.required_for_resume or record.provider_status == "bound"
            for record in records
        )
        else "incomplete"
    )


def _records_for_focus(
    records: Iterable[EmbodimentState],
    normalized: str,
) -> Optional[list[EmbodimentState]]:
    records = list(records)
    if normalized in {
        "architecture",
        "embodiment",
        "embodiments",
        "station architecture",
        "station systems",
    }:
        return records
    if normalized in {"relay", "relays", "relay constellation"}:
        return [
            record
            for record in records
            if record.l1_kind in {"relay_verifier", "continuity_system"}
        ]
    matches = [
        record
        for record in records
        if normalized
        and (
            normalized == record.embodiment_id.lower().replace("_", " ")
            or normalized in record.component.lower().replace("_", " ")
        )
    ]
    return matches or None


def _unavailable_observation(state: L1RunState, focus: str) -> Dict[str, Any]:
    return {
        "tick": state.manifest.tick,
        "status": "unavailable",
        "provider": "l1_embodiment_registry_projection",
        "reason": "registry_unbound",
        "focus": focus,
        "causal_effect": False,
        "records": [],
    }
