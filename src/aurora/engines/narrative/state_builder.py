from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

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
    state.entities = [_entity_from_mapping(item) for item in payload.get("entities", [])]
    state.pressures = [_pressure_from_mapping(item) for item in payload.get("pressures", [])]
    state.constraints = [_constraint_from_mapping(item) for item in payload.get("constraints", [])]
    state.motives = [_motive_from_mapping(item) for item in payload.get("motives", [])]
    state.events = [_event_from_mapping(item) for item in payload.get("events", [])]
    state.knowledge_states = [_knowledge_from_mapping(item) for item in payload.get("knowledge_states", [])]
    state.uncertainties = [_uncertainty_from_mapping(item) for item in payload.get("uncertainties", [])]

    _append_proposal_event(state, proposal)
    _infer_minimal_motives(state, proposal)
    _ensure_sparse_uncertainty(state)
    state.layers = _collect_layers(state, payload, request)
    state.continuity.setdefault(
        "established_events",
        [event.label for event in state.events if event.status != "proposed"],
    )
    return state


def _stable_state_id(payload: Mapping[str, Any], proposal: Mapping[str, Any]) -> str:
    canonical = json.dumps({"payload": payload, "proposal": proposal}, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


def _evidence_density(payload: Mapping[str, Any]) -> str:
    populated = 0
    for key in ("entities", "events", "motives", "pressures", "constraints", "knowledge_states", "continuity"):
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
    label = str(proposal.get("label") or proposal.get("action") or proposal.get("event") or "Proposed move")
    state.events.append(
        EventRecord(
            label=label,
            status="proposed",
            timing=str(proposal.get("timing", "")),
            participants=[str(proposal.get("actor", ""))] if proposal.get("actor") else [],
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
    if any((state.entities, state.events, state.motives, state.knowledge_states, state.constraints, state.pressures)):
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


def _collect_declared_layers(layers: dict[str, LayerRecord], payload: Mapping[str, Any]) -> None:
    for declared in payload.get("declared_layers", []):
        _upsert_layer(layers, str(declared), "declared", 1.0)


def _collect_entity_layers(layers: dict[str, LayerRecord], state: CanonicalState) -> None:
    if any(entity.entity_type == "character" for entity in state.entities):
        _upsert_layer(layers, "character", "recovered", 0.95)
    if any(entity.entity_type in _INSTITUTIONAL_ENTITY_TYPES for entity in state.entities):
        _upsert_layer(layers, "institutional", "recovered", 0.9)


def _collect_state_layers(layers: dict[str, LayerRecord], state: CanonicalState) -> None:
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


def _collect_motive_layer(layers: dict[str, LayerRecord], state: CanonicalState) -> None:
    origin = "recovered" if any(not motive.inferred for motive in state.motives) else "inferred"
    confidence = 0.9 if origin == "recovered" else 0.55
    _upsert_layer(layers, "motive", origin, confidence)


def _collect_pressure_layers(layers: dict[str, LayerRecord], state: CanonicalState) -> None:
    _upsert_layer(layers, "pressure", "recovered", 0.9)
    if any(_pressure_is_political(pressure.label) for pressure in state.pressures):
        _upsert_layer(layers, "political", "inferred", 0.65)


def _pressure_is_political(label: str) -> bool:
    normalized = label.lower()
    return "crown" in normalized or "government" in normalized


def _collect_constraint_layers(layers: dict[str, LayerRecord], state: CanonicalState) -> None:
    if not state.constraints:
        return
    _upsert_layer(layers, "constraint", "recovered", 0.95)
    for constraint in state.constraints:
        _collect_constraint_type_layer(layers, constraint.constraint_type.lower())


def _collect_constraint_type_layer(layers: dict[str, LayerRecord], constraint_type: str) -> None:
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
    if any(event.timing for event in state.events) or _has_question_token(question, _TEMPORAL_QUESTION_TOKENS):
        _upsert_layer(layers, "temporal", "inferred", 0.7)
    if request.task_kind == TaskKind.HISTORICAL_PLAUSIBILITY_CHECK and _has_question_token(
        question,
        _LOGISTICAL_QUESTION_TOKENS,
    ):
        _upsert_layer(layers, "logistical", "inferred", 0.75)


def _has_question_token(question: str, tokens: tuple[str, ...]) -> bool:
    return any(token in question for token in tokens)


def _upsert_layer(layers: dict[str, LayerRecord], name: str, origin: str, confidence: float) -> None:
    current = layers.get(name)
    candidate = LayerRecord(name=name, origin=origin, confidence=confidence)
    if current is None:
        layers[name] = candidate
        return
    current_rank = _ORIGIN_PRECEDENCE.get(current.origin, 0)
    candidate_rank = _ORIGIN_PRECEDENCE.get(origin, 0)
    if candidate_rank > current_rank or (candidate_rank == current_rank and confidence > current.confidence):
        layers[name] = candidate
