from __future__ import annotations

from typing import Any, Mapping

from .layer_resolver import resolve_layers
from .operators import run_operator_suite
from .renderer import compact_response, finalize_evaluation
from .router import build_request
from .state_builder import build_canonical_state
from .types import EvaluationPacket, NarrativeValidationRun, ResponsePayload
from .validator import build_response_payload


class NarrativeValidationEngine:
    """Deterministic validation-first narrative reasoning engine for phase one."""

    def run(
        self,
        raw_input: str | Mapping[str, Any],
        proposal: Mapping[str, Any] | None = None,
        strictness: str = "default",
    ) -> NarrativeValidationRun:
        request, payload, normalized_proposal = build_request(raw_input, proposal, strictness)
        state = build_canonical_state(payload, request, normalized_proposal)

        if not request.supported_in_phase_one:
            response = compact_response(build_response_payload(request, EvaluationPacket()))
            return NarrativeValidationRun(
                request=request,
                state=state,
                evaluation=EvaluationPacket(),
                response=response,
            )

        evaluation = resolve_layers(state, request)
        operator_results = run_operator_suite(state, request, normalized_proposal)
        evaluation.supports.extend(operator_results["supports"])
        evaluation.soft_blocks.extend(operator_results["soft_blocks"])
        evaluation.hard_blocks.extend(operator_results["hard_blocks"])
        evaluation.missing_bridges.extend(operator_results["missing_bridges"])
        evaluation.confidence_notes.extend(operator_results["confidence_notes"])
        evaluation.missing_bridges.extend(_bridges_for_missing_layers(evaluation.missing_layers))
        evaluation = finalize_evaluation(evaluation)

        response = compact_response(build_response_payload(request, evaluation))
        return NarrativeValidationRun(
            request=request,
            state=state,
            evaluation=evaluation,
            response=response,
        )


def _bridges_for_missing_layers(missing_layers: list[str]) -> list[str]:
    guidance = []
    for layer in missing_layers:
        if layer == "motive":
            guidance.append("Supply motive or pressure data for the acting character.")
        elif layer == "knowledge":
            guidance.append("State what the key actor knows before judging the move.")
        elif layer == "temporal":
            guidance.append("State the timing between the established event and the proposal.")
        elif layer == "logistical":
            guidance.append("Add communications or transport constraints for the setting.")
        elif layer == "political":
            guidance.append("Add institutional or political pressure shaping the decision.")
        else:
            guidance.append(f"Add evidence for the missing layer: {layer}.")
    return guidance
