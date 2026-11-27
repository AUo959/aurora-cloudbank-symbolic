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

ACE_SEAM_SCHEMA_VERSION = "0.1.0"
ACE_SEAM_TRIGGER_POLICY_REF = "ace.policy.l1-embodiment-coherence-seam.v1"
ACE_SEAM_CALLER_REF = "cloudbank.l1.embodiment_registry"
ACE_SUPPORTED_EMBODIMENT_BLOCKERS = {
    "canonical_location": "facility_topology",
}


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


def build_ace_coherence_seams(registry: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Emit deterministic ACE handoffs for supported, non-authoritative L1 gaps.

    This is a seam producer, not an ACE implementation. It never imports ACE,
    changes registry state, promotes canon, activates a provider, or advances a
    run. The emitted provenance is sufficient for OrionCore to wrap the request
    in the shared autonomic ACE invocation contract.
    """
    validate_embodiment_registry(registry)
    records = _registry_records(registry)
    seams: list[Dict[str, Any]] = []
    for record in records:
        for blocker in record.blockers:
            query_kind = ACE_SUPPORTED_EMBODIMENT_BLOCKERS.get(blocker)
            if query_kind is None:
                continue
            if blocker == "canonical_location" and record.location_certainty == "CANON":
                continue
            seam_ref = f"{record.embodiment_id}:{blocker}"
            seams.append(
                {
                    "schema_version": ACE_SEAM_SCHEMA_VERSION,
                    "record_type": "ace_coherence_seam",
                    "target_engine": "ACE",
                    "invocation_mode": "autonomic",
                    "caller": {
                        "kind": "system",
                        "caller_ref": ACE_SEAM_CALLER_REF,
                    },
                    "trigger": {
                        "kind": "coherence_seam",
                        "reason": (
                            "The audited L1 embodiment registry contains a routine "
                            f"coherence gap for {record.component}: {blocker}."
                        ),
                        "seam_ref": seam_ref,
                        "trigger_policy_ref": ACE_SEAM_TRIGGER_POLICY_REF,
                    },
                    "query_kind": query_kind,
                    "question": f"Determine the canonical L1 facility location for {record.component}.",
                    "subject": {
                        "entity_type": "facility",
                        "subject_ref": record.embodiment_id,
                        "existence_status": "confirmed_unrecorded_attribute",
                        "context": {
                            "component": record.component,
                            "l1_kind": record.l1_kind,
                            "current_location": record.location,
                            "location_certainty": record.location_certainty,
                            "authority_class": record.authority_class,
                            "evidence_class": record.evidence_class,
                            "source_refs": list(record.source_refs),
                            "provider_status": record.provider_status,
                            "required_for_resume": record.required_for_resume,
                            "causal_use_permitted": record.causal_use_permitted,
                            "blockers": list(record.blockers),
                        },
                    },
                    "requested_output": blocker,
                    "constraints": {
                        "specialist_first": True,
                        "inspectable": True,
                        "activation_authority": False,
                        "runtime_mutation_allowed": False,
                        "canon_materialization_authority": False,
                        "experiment_advance_allowed": False,
                    },
                }
            )
    return sorted(seams, key=lambda item: item["trigger"]["seam_ref"])


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
    seams = build_ace_coherence_seams(registry)
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
        "ace_coherence_seam_count": len(seams),
        "ace_coherence_seams": seams,
    }


#: Focus terms this provider owns outright, independent of registry state.
#:
#: The unbound branch below MUST consult these. It previously returned an
#: "unavailable" payload for ANY focus, which made the embodiment provider
#: shadow every other channel whenever the registry was not bound -- observe(
#: "fleet") answered with provider "l1_embodiment_registry_projection" instead
#: of "l1_run_fleet_state". The bound branch was always correct: it returns None
#: for a focus it does not own, deferring to the next provider. The unbound
#: branch simply skipped that check.
EMBODIMENT_FOCUS_ALIASES = frozenset(
    {
        "architecture",
        "embodiment",
        "embodiments",
        "station architecture",
        "station systems",
        "relay",
        "relays",
        "relay constellation",
    }
)


#: Channels owned by OTHER providers. The embodiment provider must never claim
#: these, however well they match a record.
#:
#: Without this guard, focus "fleet" substring-matched the component of
#: L1-EMB-FLEET-DOCKING, so the embodiment provider answered observe("fleet")
#: and the fleet provider never ran. A shared word is not evidence that this
#: provider owns the channel -- the same fragment-matching trap that has bitten
#: entity resolution elsewhere in Aurora.
RESERVED_FOCI = frozenset(
    {"fleet", "proximity", "docking", "drone", "drones", "station"}
)


def normalize_focus(focus: str) -> str:
    return " ".join(focus.strip().lower().replace("_", " ").split())


def embodiment_observation(
    state: L1RunState,
    focus: str,
) -> Optional[Dict[str, Any]]:
    """Expose embodiment/provider state without advancing or fabricating it.

    Returns None for a focus this provider does not own, so observe() falls
    through to the fleet/station providers. That contract holds whether or not
    the registry is bound: an unbound registry means "I own this focus and
    cannot answer it", never "I answer everything".
    """
    normalized = normalize_focus(focus)
    if normalized in RESERVED_FOCI:
        return None
    if state.embodiments.registry_status != "bound":
        if normalized in EMBODIMENT_FOCUS_ALIASES:
            return _unavailable_observation(state, focus)
        return None
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


_ALL_EMBODIMENT_FOCI = frozenset(
    {"architecture", "embodiment", "embodiments", "station architecture", "station systems"}
)
_RELAY_FOCI = frozenset({"relay", "relays", "relay constellation"})
assert _ALL_EMBODIMENT_FOCI | _RELAY_FOCI == EMBODIMENT_FOCUS_ALIASES
assert not (EMBODIMENT_FOCUS_ALIASES & RESERVED_FOCI)


def _records_for_focus(
    records: Iterable[EmbodimentState],
    normalized: str,
) -> Optional[list[EmbodimentState]]:
    records = list(records)
    if normalized in _ALL_EMBODIMENT_FOCI:
        return records
    if normalized in _RELAY_FOCI:
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
