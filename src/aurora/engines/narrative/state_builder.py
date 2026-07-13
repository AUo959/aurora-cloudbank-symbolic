from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .evidence import (
    CANDIDATE_AUTHORITY_TIERS,
    CANON_AUTHORITY_TIERS,
    INFERRED_FACT_STATUSES,
    REJECTED_FACT_STATUSES,
    NarrativeEvidenceBundle,
    NarrativeEvidenceSource,
    NarrativeFact,
    StateBuildReceipt,
    promotion_safety_for_bundle,
    stable_receipt_id,
)
from .types import (
    CanonicalState,
    ConstraintRecord,
    EntityRecord,
    EventRecord,
    KnowledgeStateRecord,
    LayerRecord,
    MotiveRecord,
    NormalizedTaskRequest,
    PressureRecord,
    TaskKind,
    UncertaintyRecord,
)

_ORIGIN_PRECEDENCE = {"declared": 3, "recovered": 2, "inferred": 1}
_INSTITUTIONAL_ENTITY_TYPES = {"institution", "government", "city"}
_LOGISTICAL_CONSTRAINT_TYPES = {"logistical", "communication"}
_TEMPORAL_CONSTRAINT_TYPES = {"temporal", "time"}
_POLITICAL_CONSTRAINT_TYPES = {"political", "institutional"}
_TEMPORAL_QUESTION_TOKENS = ("same night", "tonight", "next")
_LOGISTICAL_QUESTION_TOKENS = ("pre-telegraph", "courier", "distant cities")
_FACT_COLLECTION_BY_TYPE = {
    "constraint": "constraints",
    "entity": "entities",
    "event": "events",
    "knowledge": "knowledge_states",
    "knowledge_state": "knowledge_states",
    "motive": "motives",
    "pressure": "pressures",
    "uncertainty": "uncertainties",
}
_NON_ESTABLISHED_EVENT_STATUSES = {
    "candidate",
    "draft",
    "llm_candidate",
    "operational",
    "proposed",
    "simulation",
    "staging",
}


def build_canonical_state(
    payload: Mapping[str, Any],
    request: NormalizedTaskRequest,
    proposal: Mapping[str, Any],
) -> CanonicalState:
    state = CanonicalState(
        state_id=_stable_state_id(payload, proposal),
        input_profile={
            "evidence_density": _evidence_density(payload),
            "input_kind": request.input_kind,
            "question": request.user_query,
        },
        continuity=_normalize_continuity(payload.get("continuity")),
        narrative_context={
            "question": request.user_query,
            "declared_layers": list(payload.get("declared_layers", [])),
            "task_kind": request.task_kind.value,
        },
    )
    state.entities = [
        _entity_from_mapping(item) for item in payload.get("entities", [])
    ]
    state.pressures = [
        _pressure_from_mapping(item) for item in payload.get("pressures", [])
    ]
    state.constraints = [
        _constraint_from_mapping(item) for item in payload.get("constraints", [])
    ]
    state.motives = [_motive_from_mapping(item) for item in payload.get("motives", [])]
    state.events = [_event_from_mapping(item) for item in payload.get("events", [])]
    state.knowledge_states = [
        _knowledge_from_mapping(item) for item in payload.get("knowledge_states", [])
    ]
    state.uncertainties = [
        _uncertainty_from_mapping(item) for item in payload.get("uncertainties", [])
    ]

    _append_proposal_event(state, proposal)
    _infer_minimal_motives(state, proposal)
    _ensure_sparse_uncertainty(state)
    state.layers = _collect_layers(state, payload, request)
    state.continuity.setdefault(
        "established_events",
        [event.label for event in state.events if _is_established_event(event)],
    )
    return state


def build_state_from_evidence(
    bundle: NarrativeEvidenceBundle,
    request: NormalizedTaskRequest,
    proposal: Mapping[str, Any],
) -> tuple[CanonicalState, StateBuildReceipt]:
    payload, accepted_fact_ids, rejected_fact_ids, inferred_fact_ids = (
        _payload_from_evidence_bundle(bundle)
    )
    state = build_canonical_state(payload, request, proposal)
    state.state_id = _stable_state_id(
        {"evidence_bundle_id": bundle.bundle_id, "payload": payload}, proposal
    )

    active_authority_tiers = _active_authority_tiers(bundle, accepted_fact_ids)
    freshness_summary = _freshness_summary(bundle)
    promotion_safety = promotion_safety_for_bundle(bundle)
    _attach_evidence_context(
        state,
        bundle,
        active_authority_tiers=active_authority_tiers,
        promotion_safety=promotion_safety,
    )

    receipt = _build_state_receipt(
        bundle=bundle,
        state=state,
        accepted_fact_ids=accepted_fact_ids,
        rejected_fact_ids=rejected_fact_ids,
        inferred_fact_ids=inferred_fact_ids,
        active_authority_tiers=active_authority_tiers,
        freshness_summary=freshness_summary,
        promotion_safety=promotion_safety,
    )
    return state, receipt


def _attach_evidence_context(
    state: CanonicalState,
    bundle: NarrativeEvidenceBundle,
    *,
    active_authority_tiers: tuple[str, ...],
    promotion_safety: Mapping[str, Any],
) -> None:
    state.input_profile.update(
        {
            "evidence_bundle_id": bundle.bundle_id,
            "evidence_builder": "phase_two_fixture_contract",
            "evidence_fact_count": len(bundle.facts),
            "evidence_source_count": len(bundle.sources),
        }
    )
    state.narrative_context.update(
        {
            "active_authority_tiers": list(active_authority_tiers),
            "evidence_bundle_id": bundle.bundle_id,
            "evidence_source_ids": [source.source_id for source in bundle.sources],
            "promotion_safety": promotion_safety,
            "source_policy": dict(bundle.source_policy),
        }
    )


def _build_state_receipt(
    *,
    bundle: NarrativeEvidenceBundle,
    state: CanonicalState,
    accepted_fact_ids: tuple[str, ...],
    rejected_fact_ids: tuple[str, ...],
    inferred_fact_ids: tuple[str, ...],
    active_authority_tiers: tuple[str, ...],
    freshness_summary: Mapping[str, Any],
    promotion_safety: Mapping[str, Any],
) -> StateBuildReceipt:
    receipt_payload = {
        "accepted_fact_ids": accepted_fact_ids,
        "active_authority_tiers": active_authority_tiers,
        "bundle_id": bundle.bundle_id,
        "inferred_fact_ids": inferred_fact_ids,
        "promotion_safety": promotion_safety,
        "rejected_fact_ids": rejected_fact_ids,
        "state_id": state.state_id,
    }
    return StateBuildReceipt(
        receipt_id=stable_receipt_id(receipt_payload),
        bundle_id=bundle.bundle_id,
        state_id=state.state_id,
        accepted_fact_ids=accepted_fact_ids,
        rejected_fact_ids=rejected_fact_ids,
        inferred_fact_ids=inferred_fact_ids,
        active_authority_tiers=active_authority_tiers,
        freshness_summary=freshness_summary,
        promotion_safety=promotion_safety,
        source_policy=dict(bundle.source_policy),
    )


def _stable_state_id(payload: Mapping[str, Any], proposal: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        {"payload": payload, "proposal": proposal}, sort_keys=True, default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


def _evidence_density(payload: Mapping[str, Any]) -> str:
    populated = 0
    for key in (
        "entities",
        "events",
        "motives",
        "pressures",
        "constraints",
        "knowledge_states",
        "continuity",
    ):
        value = payload.get(key)
        if value:
            populated += 1
    if populated <= 1:
        return "minimal"
    if populated <= 3:
        return "sparse"
    if populated <= 5:
        return "moderate"
    if populated <= 7:
        return "rich"
    return "dense"


def _normalize_continuity(raw_continuity: Any) -> dict[str, Any]:
    if isinstance(raw_continuity, Mapping):
        return dict(raw_continuity)
    return {}


def _payload_from_evidence_bundle(
    bundle: NarrativeEvidenceBundle,
) -> tuple[dict[str, Any], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    payload: dict[str, Any] = {
        "continuity": {"evidence_bundle_id": bundle.bundle_id},
        "declared_layers": [],
    }
    sources_by_id = {source.source_id: source for source in bundle.sources}
    accepted_fact_ids: list[str] = []
    rejected_fact_ids: list[str] = []
    inferred_fact_ids: list[str] = []

    for fact in bundle.facts:
        status = fact.status.lower()
        if status in REJECTED_FACT_STATUSES:
            rejected_fact_ids.append(fact.fact_id)
            continue
        accepted_fact_ids.append(fact.fact_id)
        if _is_inferred_fact(fact, sources_by_id):
            inferred_fact_ids.append(fact.fact_id)
        _merge_evidence_fact(payload, fact, sources_by_id)

    _dedupe_continuity_list(payload["continuity"], "authority_tiers")
    _dedupe_continuity_list(payload["continuity"], "evidence_fact_ids")
    return (
        payload,
        tuple(sorted(accepted_fact_ids)),
        tuple(sorted(rejected_fact_ids)),
        tuple(sorted(inferred_fact_ids)),
    )


def _merge_evidence_fact(
    payload: dict[str, Any],
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> None:
    claim_type = fact.claim_type.lower().replace("-", "_")
    if claim_type in {"declared_layer", "layer"}:
        _merge_layer_fact(payload, fact)
        return
    if claim_type == "continuity":
        _merge_continuity_fact(payload, fact, sources_by_id)
        return

    collection = _FACT_COLLECTION_BY_TYPE.get(claim_type)
    if collection is None:
        _merge_unknown_fact(payload, fact, sources_by_id)
        return
    item = _state_payload_for_fact(fact, claim_type, sources_by_id)
    payload.setdefault(collection, []).append(item)


def _merge_layer_fact(payload: dict[str, Any], fact: NarrativeFact) -> None:
    name = (
        fact.payload.get("name")
        or fact.payload.get("layer")
        or fact.payload.get("label")
    )
    if not name:
        return
    declared_layers = payload.setdefault("declared_layers", [])
    if str(name) not in declared_layers:
        declared_layers.append(str(name))


def _merge_continuity_fact(
    payload: dict[str, Any],
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> None:
    continuity = payload.setdefault("continuity", {})
    for key, value in fact.payload.items():
        if (
            key in continuity
            and isinstance(continuity[key], list)
            and isinstance(value, list)
        ):
            continuity[key].extend(value)
        else:
            continuity[key] = value
    continuity.setdefault("evidence_fact_ids", []).append(fact.fact_id)
    continuity.setdefault("authority_tiers", []).extend(
        sorted(_fact_authority_tiers(fact, sources_by_id))
    )


def _merge_unknown_fact(
    payload: dict[str, Any],
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> None:
    continuity = payload.setdefault("continuity", {})
    continuity.setdefault("unmapped_fact_ids", []).append(fact.fact_id)
    continuity.setdefault("authority_tiers", []).extend(
        sorted(_fact_authority_tiers(fact, sources_by_id))
    )


def _state_payload_for_fact(
    fact: NarrativeFact,
    claim_type: str,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> dict[str, Any]:
    item = dict(fact.payload)
    item.setdefault("confidence", fact.confidence)
    item.setdefault("source", _record_source_for_fact(fact, sources_by_id))
    if claim_type == "event":
        item.setdefault("status", _default_event_status_for_fact(fact, sources_by_id))
        notes = list(item.get("notes", []))
        notes.extend(
            [f"evidence_fact:{fact.fact_id}", f"authority_tier:{fact.authority_tier}"]
        )
        notes.extend(fact.notes)
        item["notes"] = notes
    return item


def _record_source_for_fact(
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> str:
    tiers = _fact_authority_tiers(fact, sources_by_id)
    if _is_inferred_fact(fact, sources_by_id):
        return "inferred"
    if tiers.intersection(CANON_AUTHORITY_TIERS):
        return "declared"
    return "recovered"


def _default_event_status_for_fact(
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> str:
    tiers = _fact_authority_tiers(fact, sources_by_id)
    status = fact.status.lower()
    if status == "proposed":
        return "proposed"
    if status in INFERRED_FACT_STATUSES or tiers.intersection(
        CANDIDATE_AUTHORITY_TIERS
    ):
        return "candidate"
    return "established"


def _is_inferred_fact(
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> bool:
    tiers = _fact_authority_tiers(fact, sources_by_id)
    return fact.status.lower() in INFERRED_FACT_STATUSES or bool(
        tiers.intersection(CANDIDATE_AUTHORITY_TIERS)
    )


def _fact_authority_tiers(
    fact: NarrativeFact,
    sources_by_id: Mapping[str, NarrativeEvidenceSource],
) -> set[str]:
    tiers = {fact.authority_tier}
    tiers.update(
        sources_by_id[source_id].authority_tier
        for source_id in fact.source_ids
        if source_id in sources_by_id
    )
    return tiers


def _active_authority_tiers(
    bundle: NarrativeEvidenceBundle,
    accepted_fact_ids: tuple[str, ...],
) -> tuple[str, ...]:
    sources_by_id = {source.source_id: source for source in bundle.sources}
    accepted = set(accepted_fact_ids)
    tiers: set[str] = set()
    for fact in bundle.facts:
        if fact.fact_id not in accepted:
            continue
        tiers.update(_fact_authority_tiers(fact, sources_by_id))
    return tuple(sorted(tiers))


def _freshness_summary(bundle: NarrativeEvidenceBundle) -> dict[str, Any]:
    observed = [
        source.observed_at_utc for source in bundle.sources if source.observed_at_utc
    ]
    return {
        "generated_at_utc": bundle.generated_at_utc,
        "latest_observed_at_utc": max(observed) if observed else "",
        "source_count": len(bundle.sources),
        "source_ids": [source.source_id for source in bundle.sources],
    }


def _dedupe_continuity_list(continuity: dict[str, Any], key: str) -> None:
    values = continuity.get(key)
    if isinstance(values, list):
        continuity[key] = sorted({str(value) for value in values})


def _is_established_event(event: EventRecord) -> bool:
    return event.status.lower() not in _NON_ESTABLISHED_EVENT_STATUSES


def _entity_from_mapping(item: Mapping[str, Any]) -> EntityRecord:
    return EntityRecord(
        name=str(item.get("name", "")),
        entity_type=str(item.get("entity_type", "character")),
        role=str(item.get("role", "")),
        traits=list(item.get("traits", [])),
        source=str(item.get("source", item.get("origin", "declared"))),
        confidence=float(item.get("confidence", 1.0)),
    )


def _pressure_from_mapping(item: Mapping[str, Any]) -> PressureRecord:
    return PressureRecord(
        actor=str(item.get("actor", "")),
        label=str(item.get("label", "")),
        direction=str(item.get("direction", "toward")),
        strength=float(item.get("strength", 0.5)),
        source=str(item.get("source", item.get("origin", "declared"))),
        confidence=float(item.get("confidence", 1.0)),
    )


def _constraint_from_mapping(item: Mapping[str, Any]) -> ConstraintRecord:
    return ConstraintRecord(
        label=str(item.get("label", "")),
        constraint_type=str(item.get("constraint_type", "generic")),
        severity=str(item.get("severity", "soft")),
        details=str(item.get("details", "")),
        source=str(item.get("source", item.get("origin", "declared"))),
        confidence=float(item.get("confidence", 1.0)),
    )


def _motive_from_mapping(item: Mapping[str, Any]) -> MotiveRecord:
    source = str(item.get("source", item.get("origin", "declared")))
    return MotiveRecord(
        actor=str(item.get("actor", "")),
        label=str(item.get("label", "")),
        strength=float(item.get("strength", 0.5)),
        source=source,
        confidence=float(item.get("confidence", 1.0)),
        inferred=source == "inferred" or bool(item.get("inferred")),
    )


def _event_from_mapping(item: Mapping[str, Any]) -> EventRecord:
    return EventRecord(
        label=str(item.get("label", "")),
        status=str(item.get("status", "established")),
        timing=str(item.get("timing", "")),
        participants=list(item.get("participants", [])),
        source=str(item.get("source", item.get("origin", "declared"))),
        confidence=float(item.get("confidence", 1.0)),
        notes=list(item.get("notes", [])),
    )


def _knowledge_from_mapping(item: Mapping[str, Any]) -> KnowledgeStateRecord:
    return KnowledgeStateRecord(
        holder=str(item.get("holder", "")),
        fact=str(item.get("fact", "")),
        status=str(item.get("status", "knows")),
        source=str(item.get("source", item.get("origin", "declared"))),
        confidence=float(item.get("confidence", 1.0)),
    )


def _uncertainty_from_mapping(item: Mapping[str, Any]) -> UncertaintyRecord:
    return UncertaintyRecord(
        label=str(item.get("label", "")),
        reason=str(item.get("reason", "")),
        source=str(item.get("source", item.get("origin", "declared"))),
        confidence=float(item.get("confidence", 1.0)),
    )


def _append_proposal_event(state: CanonicalState, proposal: Mapping[str, Any]) -> None:
    if not proposal:
        return
    label = str(
        proposal.get("label")
        or proposal.get("action")
        or proposal.get("event")
        or "Proposed move"
    )
    state.events.append(
        EventRecord(
            label=label,
            status="proposed",
            timing=str(proposal.get("timing", "")),
            participants=[str(proposal.get("actor", ""))]
            if proposal.get("actor")
            else [],
            source="declared",
            confidence=1.0,
            notes=["proposal_preserved_as_provisional"],
        )
    )


def _infer_minimal_motives(state: CanonicalState, proposal: Mapping[str, Any]) -> None:
    if state.motives or not proposal:
        return
    actor = str(proposal.get("actor", ""))
    if not actor:
        return
    candidate_pressures = [
        pressure
        for pressure in state.pressures
        if pressure.actor.casefold() == actor.casefold() and pressure.strength >= 0.8
    ]
    for pressure in candidate_pressures:
        state.motives.append(
            MotiveRecord(
                actor=actor,
                label=pressure.label,
                strength=max(0.4, pressure.strength - 0.2),
                source="inferred",
                confidence=0.55,
                inferred=True,
            )
        )


def _ensure_sparse_uncertainty(state: CanonicalState) -> None:
    if any(
        (
            state.entities,
            state.events,
            state.motives,
            state.knowledge_states,
            state.constraints,
            state.pressures,
        )
    ):
        return
    state.uncertainties.append(
        UncertaintyRecord(
            label="sparse_input",
            reason="The input does not provide enough structured state for a full audit.",
            source="recovered",
            confidence=0.95,
        )
    )


def _collect_layers(
    state: CanonicalState,
    payload: Mapping[str, Any],
    request: NormalizedTaskRequest,
) -> list[LayerRecord]:
    layers: dict[str, LayerRecord] = {}
    _collect_declared_layers(layers, payload)
    _collect_entity_layers(layers, state)
    _collect_state_layers(layers, state)
    _collect_constraint_layers(layers, state)
    _collect_question_layers(layers, state, request)

    return sorted(layers.values(), key=lambda layer: layer.name)


def _collect_declared_layers(
    layers: dict[str, LayerRecord], payload: Mapping[str, Any]
) -> None:
    for declared in payload.get("declared_layers", []):
        _upsert_layer(layers, str(declared), "declared", 1.0)


def _collect_entity_layers(
    layers: dict[str, LayerRecord], state: CanonicalState
) -> None:
    if any(entity.entity_type == "character" for entity in state.entities):
        _upsert_layer(layers, "character", "recovered", 0.95)
    if any(
        entity.entity_type in _INSTITUTIONAL_ENTITY_TYPES for entity in state.entities
    ):
        _upsert_layer(layers, "institutional", "recovered", 0.9)


def _collect_state_layers(
    layers: dict[str, LayerRecord], state: CanonicalState
) -> None:
    if state.motives:
        _collect_motive_layer(layers, state)
    if state.events:
        _upsert_layer(layers, "event", "recovered", 0.95)
    if state.knowledge_states:
        _upsert_layer(layers, "knowledge", "recovered", 0.95)
    if state.continuity:
        _upsert_layer(layers, "continuity", "recovered", 0.95)
    if state.pressures:
        _collect_pressure_layers(layers, state)


def _collect_motive_layer(
    layers: dict[str, LayerRecord], state: CanonicalState
) -> None:
    origin = (
        "recovered"
        if any(not motive.inferred for motive in state.motives)
        else "inferred"
    )
    confidence = 0.9 if origin == "recovered" else 0.55
    _upsert_layer(layers, "motive", origin, confidence)


def _collect_pressure_layers(
    layers: dict[str, LayerRecord], state: CanonicalState
) -> None:
    _upsert_layer(layers, "pressure", "recovered", 0.9)
    if any(_pressure_is_political(pressure.label) for pressure in state.pressures):
        _upsert_layer(layers, "political", "inferred", 0.65)


def _pressure_is_political(label: str) -> bool:
    normalized = label.lower()
    return "crown" in normalized or "government" in normalized


def _collect_constraint_layers(
    layers: dict[str, LayerRecord], state: CanonicalState
) -> None:
    if not state.constraints:
        return
    _upsert_layer(layers, "constraint", "recovered", 0.95)
    for constraint in state.constraints:
        _collect_constraint_type_layer(layers, constraint.constraint_type.lower())


def _collect_constraint_type_layer(
    layers: dict[str, LayerRecord], constraint_type: str
) -> None:
    if constraint_type in _LOGISTICAL_CONSTRAINT_TYPES:
        _upsert_layer(layers, "logistical", "recovered", 0.95)
    if constraint_type in _TEMPORAL_CONSTRAINT_TYPES:
        _upsert_layer(layers, "temporal", "recovered", 0.95)
    if constraint_type in _POLITICAL_CONSTRAINT_TYPES:
        _upsert_layer(layers, "political", "recovered", 0.9)


def _collect_question_layers(
    layers: dict[str, LayerRecord],
    state: CanonicalState,
    request: NormalizedTaskRequest,
) -> None:
    question = request.user_query.lower()
    if any(event.timing for event in state.events) or _has_question_token(
        question, _TEMPORAL_QUESTION_TOKENS
    ):
        _upsert_layer(layers, "temporal", "inferred", 0.7)
    if (
        request.task_kind == TaskKind.HISTORICAL_PLAUSIBILITY_CHECK
        and _has_question_token(
            question,
            _LOGISTICAL_QUESTION_TOKENS,
        )
    ):
        _upsert_layer(layers, "logistical", "inferred", 0.75)


def _has_question_token(question: str, tokens: tuple[str, ...]) -> bool:
    return any(token in question for token in tokens)


def _upsert_layer(
    layers: dict[str, LayerRecord], name: str, origin: str, confidence: float
) -> None:
    current = layers.get(name)
    candidate = LayerRecord(name=name, origin=origin, confidence=confidence)
    if current is None:
        layers[name] = candidate
        return
    current_rank = _ORIGIN_PRECEDENCE.get(current.origin, 0)
    candidate_rank = _ORIGIN_PRECEDENCE.get(origin, 0)
    if candidate_rank > current_rank or (
        candidate_rank == current_rank and confidence > current.confidence
    ):
        layers[name] = candidate
