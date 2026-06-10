from __future__ import annotations

from .types import CanonicalState, EvaluationPacket, NormalizedTaskRequest, TaskKind

REQUIRED_LAYERS = {
    TaskKind.CHARACTER_ACTION_AUDIT: ["character", "motive", "event", "knowledge", "continuity"],
    TaskKind.NEXT_EVENT_CONTINUITY_CHECK: ["event", "temporal", "knowledge", "continuity", "character"],
    TaskKind.HISTORICAL_PLAUSIBILITY_CHECK: ["institutional", "temporal", "logistical", "political"],
}

SELECTED_OPERATORS = {
    TaskKind.CHARACTER_ACTION_AUDIT: [
        "motive_inference",
        "knowledge_propagation",
        "setup_sufficiency_check",
    ],
    TaskKind.NEXT_EVENT_CONTINUITY_CHECK: [
        "knowledge_propagation",
        "temporal_sequencing",
        "setup_sufficiency_check",
    ],
    TaskKind.HISTORICAL_PLAUSIBILITY_CHECK: [
        "temporal_sequencing",
        "plausibility_envelope_check",
        "setup_sufficiency_check",
    ],
}


def resolve_layers(state: CanonicalState, request: NormalizedTaskRequest) -> EvaluationPacket:
    available_layers = {layer.name: layer for layer in state.layers if layer.status == "available"}
    required_layers = REQUIRED_LAYERS.get(request.task_kind, [])
    active_layers = [layer for layer in required_layers if layer in available_layers]
    missing_layers = [layer for layer in required_layers if layer not in available_layers]
    confidence_notes = []
    for layer_name in active_layers:
        layer_record = available_layers[layer_name]
        if layer_record.origin == "inferred":
            confidence_notes.append(f"{layer_name} layer is inferred rather than directly supported.")
    if missing_layers:
        confidence_notes.append(
            "Missing load-bearing layers: " + ", ".join(missing_layers)
        )

    return EvaluationPacket(
        active_layers=active_layers,
        missing_layers=missing_layers,
        selected_operators=SELECTED_OPERATORS.get(request.task_kind, []),
        confidence_notes=confidence_notes,
    )
