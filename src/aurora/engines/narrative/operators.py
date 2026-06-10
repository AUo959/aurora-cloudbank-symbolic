from __future__ import annotations

from typing import Any, Mapping

from .types import CanonicalState, MotiveRecord, NormalizedTaskRequest, PressureRecord, TaskKind

_SUPPORT_MOTIVE_LABELS = ("rebellion", "mission", "duty")
_SUPPORT_ACTION_TOKENS = ("rebellion", "signal", "save")
_RESISTANCE_MOTIVE_LABELS = ("protect", "loyalty", "trust")
_RESISTANCE_ACTION_TOKENS = ("abandon", "betray", "accuse")


def run_operator_suite(
    state: CanonicalState,
    request: NormalizedTaskRequest,
    proposal: Mapping[str, Any],
) -> dict[str, list[str]]:
    results = {
        "supports": [],
        "soft_blocks": [],
        "hard_blocks": [],
        "missing_bridges": [],
        "confidence_notes": [],
    }
    for operator in (
        motive_inference(state, request, proposal),
        knowledge_propagation(state, request, proposal),
        temporal_sequencing(state, request, proposal),
        plausibility_envelope_check(state, request),
        setup_sufficiency_check(state, request),
    ):
        for key, values in operator.items():
            results[key].extend(values)
    return results


def motive_inference(
    state: CanonicalState,
    request: NormalizedTaskRequest,
    proposal: Mapping[str, Any],
) -> dict[str, list[str]]:
    if request.task_kind != TaskKind.CHARACTER_ACTION_AUDIT:
        return _empty_result()

    actor = str(proposal.get("actor", "")).casefold()
    action_text = _proposal_text(proposal)
    results = _empty_result()

    for motive in state.motives:
        if not _actor_matches(actor, motive.actor):
            continue
        motive_result = _evaluate_motive(motive, action_text)
        for key, values in motive_result.items():
            results[key].extend(values)

    for pressure in state.pressures:
        if not _actor_matches(actor, pressure.actor):
            continue
        key, message = _evaluate_pressure(pressure)
        results[key].append(message)

    return results


def knowledge_propagation(
    state: CanonicalState,
    request: NormalizedTaskRequest,
    proposal: Mapping[str, Any],
) -> dict[str, list[str]]:
    if request.task_kind not in {
        TaskKind.CHARACTER_ACTION_AUDIT,
        TaskKind.NEXT_EVENT_CONTINUITY_CHECK,
    }:
        return _empty_result()

    action_text = _proposal_text(proposal)
    soft_blocks: list[str] = []
    supports: list[str] = []
    for knowledge_state in state.knowledge_states:
        fact = knowledge_state.fact.lower()
        if "innocent" in fact and "accuse" in action_text:
            soft_blocks.append(
                f"{knowledge_state.holder} knows the suspect is innocent, so the accusation fights "
                "knowledge continuity."
            )
        elif "collapse" in fact and any(token in action_text for token in ("save", "deliver", "signal")):
            supports.append(
                f"{knowledge_state.holder}'s knowledge that delay will cause collapse supports urgent action."
            )
    return {
        "supports": supports,
        "soft_blocks": soft_blocks,
        "hard_blocks": [],
        "missing_bridges": [],
        "confidence_notes": [],
    }


def temporal_sequencing(
    state: CanonicalState,
    request: NormalizedTaskRequest,
    proposal: Mapping[str, Any],
) -> dict[str, list[str]]:
    soft_blocks: list[str] = []
    hard_blocks: list[str] = []
    missing_bridges: list[str] = []
    action_text = _proposal_text(proposal)
    timing = str(proposal.get("timing", "")).lower()

    if request.task_kind == TaskKind.NEXT_EVENT_CONTINUITY_CHECK:
        if "same_night" in timing or "same night" in action_text:
            soft_blocks.append("The proposed beat compresses the timeline before a visible turn can occur.")
            missing_bridges.append(
                "Insert coercion, misdirection, or a clear breakdown before the same-night accusation."
            )

    if request.task_kind == TaskKind.HISTORICAL_PLAUSIBILITY_CHECK:
        question = request.user_query.lower()
        has_pretelegraph_context = "pre-telegraph" in question or any(
            "telegraph" in constraint.label.lower() or "courier" in constraint.label.lower()
            for constraint in state.constraints
        )
        if has_pretelegraph_context and "same_day" in timing:
            hard_blocks.append("Same-day coordination fails the communications timeline in a pre-telegraph setting.")

    return {
        "supports": [],
        "soft_blocks": soft_blocks,
        "hard_blocks": hard_blocks,
        "missing_bridges": missing_bridges,
        "confidence_notes": [],
    }


def plausibility_envelope_check(
    state: CanonicalState,
    request: NormalizedTaskRequest,
) -> dict[str, list[str]]:
    if request.task_kind != TaskKind.HISTORICAL_PLAUSIBILITY_CHECK:
        return _empty_result()

    hard_blocks: list[str] = []
    missing_bridges: list[str] = []
    for constraint in state.constraints:
        label = constraint.label.lower()
        if constraint.severity.lower() == "hard" and any(
            token in label for token in ("days apart", "no telegraph", "distant cities", "courier")
        ):
            hard_blocks.append(f"Constraint '{constraint.label}' blocks the event as stated.")
    if hard_blocks:
        missing_bridges.append(
            "Reframe the crackdown as pre-coordinated orders, delegated triggers, or staggered action."
        )
    return {
        "supports": [],
        "soft_blocks": [],
        "hard_blocks": hard_blocks,
        "missing_bridges": missing_bridges,
        "confidence_notes": [],
    }


def setup_sufficiency_check(
    state: CanonicalState,
    request: NormalizedTaskRequest,
) -> dict[str, list[str]]:
    missing_bridges: list[str] = []
    confidence_notes: list[str] = []
    if request.task_kind == TaskKind.CHARACTER_ACTION_AUDIT and state.motives and state.pressures:
        if any(pressure.direction.lower() == "against" for pressure in state.pressures):
            missing_bridges.append(
                "Add a catalyst showing why mission pressure overrides personal loyalty in this moment."
            )
    if request.task_kind == TaskKind.CHARACTER_ACTION_AUDIT and not state.motives:
        missing_bridges.append("Supply motive or pressure data for the acting character.")
    if request.task_kind == TaskKind.NEXT_EVENT_CONTINUITY_CHECK and not state.knowledge_states:
        missing_bridges.append("State what the key actors know before the next beat.")
    if request.task_kind == TaskKind.HISTORICAL_PLAUSIBILITY_CHECK and not state.constraints:
        confidence_notes.append("Historical plausibility is running without explicit logistical constraints.")
    return {
        "supports": [],
        "soft_blocks": [],
        "hard_blocks": [],
        "missing_bridges": missing_bridges,
        "confidence_notes": confidence_notes,
    }


def _proposal_text(proposal: Mapping[str, Any]) -> str:
    parts = [
        str(proposal.get("label", "")),
        str(proposal.get("action", "")),
        str(proposal.get("timing", "")),
    ]
    return " ".join(part for part in parts if part).lower()


def _actor_matches(actor: str, subject: str) -> bool:
    return not actor or subject.casefold() == actor


def _has_any(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token in text for token in tokens)


def _evaluate_motive(motive: MotiveRecord, action_text: str) -> dict[str, list[str]]:
    label = motive.label.lower()
    result = _empty_result()
    if _has_any(label, _SUPPORT_MOTIVE_LABELS) and _has_any(action_text, _SUPPORT_ACTION_TOKENS):
        result["supports"].append(
            f"{motive.actor}'s motive '{motive.label}' aligns with the proposed action."
        )
    if _has_any(label, _RESISTANCE_MOTIVE_LABELS) and _has_any(action_text, _RESISTANCE_ACTION_TOKENS):
        result["soft_blocks"].append(
            f"{motive.actor}'s motive '{motive.label}' resists the proposed action."
        )
    if motive.inferred:
        result["confidence_notes"].append(f"Motive '{motive.label}' is inferred at low confidence.")
    return result


def _evaluate_pressure(pressure: PressureRecord) -> tuple[str, str]:
    message = f"{pressure.actor}'s pressure '{pressure.label}' pulls {pressure.direction} the move."
    if pressure.direction.lower() == "toward":
        return "supports", message
    return "soft_blocks", message


def _empty_result() -> dict[str, list[str]]:
    return {
        "supports": [],
        "soft_blocks": [],
        "hard_blocks": [],
        "missing_bridges": [],
        "confidence_notes": [],
    }
