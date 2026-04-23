from __future__ import annotations

from .types import EvaluationPacket, NormalizedTaskRequest, ResponsePayload, Verdict


def build_response_payload(request: NormalizedTaskRequest, evaluation: EvaluationPacket) -> ResponsePayload:
    if not request.supported_in_phase_one:
        return ResponsePayload(
            summary=(
                "Phase one only supports character action audits, next-event continuity checks, "
                "and historical plausibility checks."
            ),
            verdict=None,
            main_supports=[],
            main_blockers=[],
            missing_bridges=[],
            smallest_fix=["Reframe the request as one of the three supported validation tasks."],
            confidence=0.2,
            supported_in_phase_one=False,
            unsupported_reason=request.unsupported_reason,
        )

    verdict = _determine_verdict(evaluation)
    confidence = _compute_confidence(evaluation, verdict)
    summary = _build_summary(request, evaluation, verdict)
    smallest_fix = _smallest_fix(request, evaluation, verdict)
    return ResponsePayload(
        summary=summary,
        verdict=verdict,
        main_supports=evaluation.supports[:3],
        main_blockers=evaluation.blocks[:3],
        missing_bridges=evaluation.missing_bridges[:3],
        smallest_fix=smallest_fix,
        confidence=confidence,
    )


def _determine_verdict(evaluation: EvaluationPacket) -> Verdict:
    if evaluation.hard_blocks:
        return Verdict.CONTRADICTORY
    if evaluation.soft_blocks:
        if evaluation.supports and evaluation.missing_bridges:
            return Verdict.POSSIBLE_WITH_SETUP
        if evaluation.supports:
            return Verdict.PLAUSIBLE
        return Verdict.STRAINED
    if evaluation.missing_layers:
        return Verdict.POSSIBLE_WITH_SETUP
    if evaluation.supports:
        return Verdict.SUPPORTED
    return Verdict.PLAUSIBLE


def _compute_confidence(evaluation: EvaluationPacket, verdict: Verdict) -> float:
    confidence = 0.78
    if verdict == Verdict.SUPPORTED:
        confidence += 0.1
    elif verdict == Verdict.PLAUSIBLE:
        confidence += 0.02
    elif verdict == Verdict.POSSIBLE_WITH_SETUP:
        confidence -= 0.05
    elif verdict == Verdict.STRAINED:
        confidence -= 0.12
    elif verdict == Verdict.CONTRADICTORY:
        confidence += 0.08

    confidence += min(0.12, 0.05 * len(evaluation.supports))
    confidence -= min(0.36, 0.12 * len(evaluation.missing_layers))
    confidence -= min(0.2, 0.07 * len(evaluation.soft_blocks))
    confidence += min(0.2, 0.15 * len(evaluation.hard_blocks))
    if any("inferred" in note.lower() for note in evaluation.confidence_notes):
        confidence -= 0.08
    return max(0.15, min(0.95, round(confidence, 2)))


def _build_summary(request: NormalizedTaskRequest, evaluation: EvaluationPacket, verdict: Verdict) -> str:
    first_support = evaluation.supports[0] if evaluation.supports else "direct support remains thin."
    first_block = evaluation.blocks[0] if evaluation.blocks else "no major blocker is established."
    if request.task_kind.value == "character_action_audit":
        return f"This character move is {verdict.value}: {first_support} But {first_block}"
    if request.task_kind.value == "next_event_continuity_check":
        return f"This next beat is {verdict.value}: {first_block}"
    if request.task_kind.value == "historical_plausibility_check":
        return f"As stated, this event is {verdict.value}: {first_block}"
    return f"Phase-one evaluation returned {verdict.value}."


def _smallest_fix(
    request: NormalizedTaskRequest,
    evaluation: EvaluationPacket,
    verdict: Verdict,
) -> list[str]:
    if evaluation.missing_bridges:
        return evaluation.missing_bridges[:2]
    if evaluation.missing_layers:
        return [f"Add evidence for the missing layer(s): {', '.join(evaluation.missing_layers)}."]
    if verdict == Verdict.CONTRADICTORY and request.task_kind.value == "historical_plausibility_check":
        return ["Reframe the action around pre-coordination or staggered execution."]
    if verdict == Verdict.STRAINED:
        return ["Insert one visible bridge event before this move."]
    return ["Preserve the current setup and add one more direct support if stronger confidence is required."]
