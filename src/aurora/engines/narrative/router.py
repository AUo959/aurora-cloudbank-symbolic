from __future__ import annotations

from typing import Any, Mapping

from .types import NormalizedTaskRequest, Strictness, TaskKind

SUPPORTED_TASKS = {
    TaskKind.CHARACTER_ACTION_AUDIT,
    TaskKind.NEXT_EVENT_CONTINUITY_CHECK,
    TaskKind.HISTORICAL_PLAUSIBILITY_CHECK,
}

_TASK_HINT_MAP = {
    "character_action_audit": TaskKind.CHARACTER_ACTION_AUDIT,
    "character_action": TaskKind.CHARACTER_ACTION_AUDIT,
    "next_event_continuity_check": TaskKind.NEXT_EVENT_CONTINUITY_CHECK,
    "next_event": TaskKind.NEXT_EVENT_CONTINUITY_CHECK,
    "historical_plausibility_check": TaskKind.HISTORICAL_PLAUSIBILITY_CHECK,
    "historical_plausibility": TaskKind.HISTORICAL_PLAUSIBILITY_CHECK,
    "expansion": TaskKind.EXPANSION,
    "translation": TaskKind.TRANSLATION,
}


def normalize_input(raw_input: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(raw_input, str):
        return {"question": raw_input, "raw_text": raw_input}
    return dict(raw_input)


def normalize_proposal(payload: Mapping[str, Any], proposal: Mapping[str, Any] | None) -> dict[str, Any]:
    normalized = dict(payload.get("proposal", {}))
    if proposal is not None:
        normalized.update(dict(proposal))
    return normalized


def build_request(
    raw_input: str | Mapping[str, Any],
    proposal: Mapping[str, Any] | None,
    strictness: str | Strictness = Strictness.DEFAULT,
) -> tuple[NormalizedTaskRequest, dict[str, Any], dict[str, Any]]:
    payload = normalize_input(raw_input)
    normalized_proposal = normalize_proposal(payload, proposal)
    strictness_value = _normalize_strictness(strictness)
    task_kind, unsupported_reason = _classify_task(payload, normalized_proposal)
    supported_in_phase_one = task_kind in SUPPORTED_TASKS
    task_type = "validate" if task_kind in SUPPORTED_TASKS or task_kind == TaskKind.UNSUPPORTED else task_kind.value

    request = NormalizedTaskRequest(
        task_kind=task_kind,
        proposal_present=bool(normalized_proposal),
        strictness=strictness_value,
        task_type=task_type,
        input_kind="text" if isinstance(raw_input, str) else "mapping",
        user_query=_extract_question(payload),
        supported_in_phase_one=supported_in_phase_one,
        unsupported_reason=unsupported_reason,
    )
    return request, payload, normalized_proposal


def _normalize_strictness(strictness: str | Strictness) -> Strictness:
    if isinstance(strictness, Strictness):
        return strictness
    normalized = strictness.strip().lower()
    if normalized == Strictness.LENIENT.value:
        return Strictness.LENIENT
    if normalized == Strictness.STRICT.value:
        return Strictness.STRICT
    return Strictness.DEFAULT


def _extract_question(payload: Mapping[str, Any]) -> str:
    for key in ("question", "query", "prompt", "raw_text"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _classify_task(payload: Mapping[str, Any], proposal: Mapping[str, Any]) -> tuple[TaskKind, str | None]:
    hint = str(payload.get("task_hint") or payload.get("task_kind") or "").strip().lower().replace(" ", "_")
    if hint in _TASK_HINT_MAP:
        task_kind = _TASK_HINT_MAP[hint]
        return task_kind, _unsupported_reason(task_kind)

    question = _extract_question(payload).lower()
    if not question and proposal:
        if proposal.get("timing"):
            return TaskKind.NEXT_EVENT_CONTINUITY_CHECK, None
        if proposal.get("actor"):
            return TaskKind.CHARACTER_ACTION_AUDIT, None

    if any(token in question for token in ("translate", "convert this into", "structural translation")):
        return TaskKind.TRANSLATION, _unsupported_reason(TaskKind.TRANSLATION)
    if any(token in question for token in ("expand this", "what myths", "what civilization", "fork in the road")):
        return TaskKind.EXPANSION, _unsupported_reason(TaskKind.EXPANSION)
    if "symbolize" in question or "symbolic fit" in question:
        return TaskKind.UNSUPPORTED, "Phase one does not implement symbolic-fit audits."
    if any(token in question for token in ("historical", "pre-telegraph", "as stated", "plausible in the setting")):
        return TaskKind.HISTORICAL_PLAUSIBILITY_CHECK, None
    if any(token in question for token in ("next beat", "next scene", "happen next", "same night")):
        return TaskKind.NEXT_EVENT_CONTINUITY_CHECK, None
    if any(token in question for token in ("would", "really do this", "make sense for")) and proposal.get("actor"):
        return TaskKind.CHARACTER_ACTION_AUDIT, None
    if question.endswith("?") and proposal.get("actor"):
        return TaskKind.CHARACTER_ACTION_AUDIT, None
    if question:
        return TaskKind.UNSUPPORTED, "Phase one only supports three validation tasks."
    return TaskKind.UNSUPPORTED, "Phase one only supports three validation tasks."


def _unsupported_reason(task_kind: TaskKind) -> str | None:
    if task_kind == TaskKind.EXPANSION:
        return "Phase one intentionally excludes expansion mode."
    if task_kind == TaskKind.TRANSLATION:
        return "Phase one intentionally excludes translation mode."
    if task_kind == TaskKind.UNSUPPORTED:
        return "Phase one only supports three validation tasks."
    return None
