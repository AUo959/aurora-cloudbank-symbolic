"""Core orchestration for Narrative River Frames and Scene River Deltas."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any

from .models import (
    SUPPORTED_SCHEMA_VERSION,
    CanonSnapshot,
    NarrativeRiverFrame,
    SceneRiverDelta,
    ValidationReport,
)
from .prompt_contract import render_prompt_contract
from .validator import validate_draft


class NarrativeRiverAdapter:
    """Build and inspect narrative artifacts without mutating simulation or canon state."""

    @staticmethod
    def deterministic_frame_id(
        scene_id: str,
        schema_version: str = SUPPORTED_SCHEMA_VERSION,
    ) -> str:
        digest = sha256(
            f"{schema_version}:{scene_id}".encode("utf-8")
        ).hexdigest()[:12].upper()
        return f"NRF-{digest}"

    def build_frame(
        self,
        *,
        scene_request: dict[str, Any],
        canon_snapshot: dict[str, Any] | CanonSnapshot,
        prior_delta: dict[str, Any] | SceneRiverDelta | None = None,
    ) -> NarrativeRiverFrame:
        """Validate a frame payload and carry explicit prior-scene state forward."""

        payload = deepcopy(scene_request)
        payload["canon_snapshot"] = _snapshot_payload(canon_snapshot)
        payload.setdefault("schema_version", SUPPORTED_SCHEMA_VERSION)
        scene_id = payload.get("scene_id")
        if not isinstance(scene_id, str) or not scene_id.strip():
            raise ValueError("scene_request must include a non-empty scene_id")
        payload.setdefault(
            "frame_id",
            self.deterministic_frame_id(scene_id, payload["schema_version"]),
        )

        if prior_delta is not None:
            _apply_prior_delta(payload, prior_delta)

        return NarrativeRiverFrame.model_validate(payload)

    def render_prompt_contract(self, frame: NarrativeRiverFrame, axioms_text: str = "") -> str:
        return render_prompt_contract(frame, axioms_text=axioms_text)

    def validate_draft(self, frame: NarrativeRiverFrame, draft_text: str) -> ValidationReport:
        return validate_draft(frame, draft_text)

    def create_delta(self, delta_payload: dict[str, Any]) -> SceneRiverDelta:
        return SceneRiverDelta.model_validate(deepcopy(delta_payload))


def _snapshot_payload(snapshot: dict[str, Any] | CanonSnapshot) -> dict[str, Any]:
    if isinstance(snapshot, CanonSnapshot):
        return snapshot.model_dump(mode="json")
    return deepcopy(snapshot)


def _apply_prior_delta(
    payload: dict[str, Any],
    prior_delta: dict[str, Any] | SceneRiverDelta,
) -> None:
    delta = (
        prior_delta
        if isinstance(prior_delta, SceneRiverDelta)
        else SceneRiverDelta.model_validate(prior_delta)
    )
    _append_unique(
        payload.setdefault("required_downstream_effects", []),
        delta.next_scene_requirements,
    )
    payload["unresolved_questions"] = _merged_questions(payload, delta)
    payload["sediment"] = _merged_sediment(payload, delta)


def _append_unique(target: list[Any], additions: list[Any]) -> None:
    for item in additions:
        if item not in target:
            target.append(item)


def _merged_questions(
    payload: dict[str, Any],
    delta: SceneRiverDelta,
) -> list[str]:
    closed = set(delta.closed_questions)
    questions = [
        question
        for question in payload.setdefault("unresolved_questions", [])
        if question not in closed
    ]
    _append_unique(questions, [item for item in delta.new_questions if item not in closed])
    return questions


def _merged_sediment(
    payload: dict[str, Any],
    delta: SceneRiverDelta,
) -> list[Any]:
    resolved = set(delta.resolved_sediment_ids)
    sediment: list[Any] = []
    existing_ids: set[str] = set()
    for item in payload.setdefault("sediment", []):
        _append_sediment(sediment, existing_ids, resolved, item)
    for item in delta.new_sediment:
        _append_sediment(
            sediment,
            existing_ids,
            resolved,
            item.model_dump(mode="json"),
        )
    return sediment


def _append_sediment(
    sediment: list[Any],
    existing_ids: set[str],
    resolved: set[str],
    item: Any,
) -> None:
    sediment_id = (
        item.sediment_id if hasattr(item, "sediment_id") else item.get("sediment_id")
    )
    if not sediment_id or sediment_id in resolved or sediment_id in existing_ids:
        return
    sediment.append(item)
    existing_ids.add(sediment_id)
