"""Passive orchestration for Narrative River Frames and Scene River Deltas."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from typing import Any

from .models import CanonSnapshot, NarrativeRiverFrame, SceneRiverDelta, ValidationReport
from .prompt_contract import render_prompt_contract
from .validator import validate_draft


class NarrativeRiverAdapter:
    """Build and inspect narrative artifacts without mutating runtime or canon state."""

    @staticmethod
    def deterministic_frame_id(scene_id: str, schema_version: str = "0.1.0") -> str:
        """Create a stable frame identifier from the scene and schema version."""

        digest = sha256(f"{schema_version}:{scene_id}".encode("utf-8")).hexdigest()[:12].upper()
        return f"NRF-{digest}"

    def build_frame(
        self,
        *,
        scene_request: dict[str, Any],
        canon_snapshot: dict[str, Any] | CanonSnapshot,
        prior_delta: dict[str, Any] | SceneRiverDelta | None = None,
    ) -> NarrativeRiverFrame:
        """Validate a manual frame payload and carry explicit prior-scene obligations forward."""

        payload = deepcopy(scene_request)
        snapshot = (
            canon_snapshot.model_dump(mode="json")
            if isinstance(canon_snapshot, CanonSnapshot)
            else deepcopy(canon_snapshot)
        )
        payload["canon_snapshot"] = snapshot
        payload.setdefault("schema_version", "0.1.0")
        payload.setdefault("frame_id", self.deterministic_frame_id(payload["scene_id"], payload["schema_version"]))

        if prior_delta is not None:
            delta = prior_delta if isinstance(prior_delta, SceneRiverDelta) else SceneRiverDelta.model_validate(prior_delta)
            effects = payload.setdefault("required_downstream_effects", [])
            questions = payload.setdefault("unresolved_questions", [])
            for requirement in delta.next_scene_requirements:
                if requirement not in effects:
                    effects.append(requirement)
            for question in delta.new_questions:
                if question not in delta.closed_questions and question not in questions:
                    questions.append(question)
            sediment = payload.setdefault("sediment", [])
            existing_ids = {
                item.sediment_id if hasattr(item, "sediment_id") else item.get("sediment_id") for item in sediment
            }
            for item in delta.new_sediment:
                if item.sediment_id not in existing_ids and item.sediment_id not in delta.resolved_sediment_ids:
                    sediment.append(item.model_dump(mode="json"))

        return NarrativeRiverFrame.model_validate(payload)

    def render_prompt_contract(self, frame: NarrativeRiverFrame, axioms_text: str = "") -> str:
        """Render the passive prose-generation contract."""

        return render_prompt_contract(frame, axioms_text=axioms_text)

    def validate_draft(self, frame: NarrativeRiverFrame, draft_text: str) -> ValidationReport:
        """Run advisory prose checks without rewriting the draft."""

        return validate_draft(frame, draft_text)

    def create_delta(self, delta_payload: dict[str, Any]) -> SceneRiverDelta:
        """Validate an explicit post-scene delta without inferring canon or state changes."""

        return SceneRiverDelta.model_validate(deepcopy(delta_payload))
