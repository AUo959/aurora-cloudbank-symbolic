"""Explicit, operator-triggered Narrative River scene workflow."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .adapter import NarrativeRiverAdapter
from .models import NarrativeRiverFrame, SceneRiverDelta, ValidationReport
from .storage import NarrativeRiverStore


class NarrativeRiverWorkflow:
    """Run scene planning, prompt rendering, validation, and closure as explicit steps."""

    def __init__(self, store: NarrativeRiverStore, adapter: NarrativeRiverAdapter | None = None) -> None:
        self.store = store
        self.adapter = adapter or NarrativeRiverAdapter()

    def _resolve_prior_delta(
        self,
        scene_request: dict[str, Any],
        prior_delta: SceneRiverDelta | dict[str, Any] | None,
        *,
        auto_prior: bool,
    ) -> SceneRiverDelta | dict[str, Any] | None:
        if prior_delta is not None or not auto_prior:
            return prior_delta
        previous_scene_id = scene_request.get("narrative_status", {}).get("previous_scene_id")
        if previous_scene_id:
            try:
                return self.store.load_delta_for_scene(previous_scene_id)
            except FileNotFoundError:
                return None
        return self.store.load_latest_delta()

    def build_and_store_frame(
        self,
        *,
        scene_request: dict[str, Any],
        canon_snapshot: dict[str, Any],
        prior_delta: SceneRiverDelta | dict[str, Any] | None = None,
        auto_prior: bool = True,
    ) -> tuple[NarrativeRiverFrame, Path]:
        payload = deepcopy(scene_request)
        scene_id = payload.get("scene_id")
        if not isinstance(scene_id, str) or not scene_id.strip():
            raise ValueError("scene_request must include a non-empty scene_id")
        resolved_delta = self._resolve_prior_delta(payload, prior_delta, auto_prior=auto_prior)
        status = payload.setdefault("narrative_status", {})
        status.setdefault("current_state", "draft")
        status.setdefault("persistence_class", "draft_persistent")
        status["storage_receipt"] = self.store.frame_receipt(scene_id)
        if resolved_delta is not None and not status.get("previous_scene_id"):
            previous = resolved_delta.scene_id if isinstance(resolved_delta, SceneRiverDelta) else resolved_delta.get("scene_id")
            status["previous_scene_id"] = previous
        frame = self.adapter.build_frame(
            scene_request=payload,
            canon_snapshot=canon_snapshot,
            prior_delta=resolved_delta,
        )
        return frame, self.store.save_frame(frame)

    def render_and_store_prompt(self, frame: NarrativeRiverFrame, axioms_text: str = "") -> tuple[str, Path]:
        prompt = self.adapter.render_prompt_contract(frame, axioms_text=axioms_text)
        return prompt, self.store.save_prompt(frame, prompt)

    def validate_and_store_draft(self, frame: NarrativeRiverFrame, draft_text: str) -> tuple[ValidationReport, Path]:
        report = self.adapter.validate_draft(frame, draft_text)
        report.storage_receipt = self.store.report_receipt(frame.scene_id)
        return report, self.store.save_report(frame, report)

    def close_scene(
        self,
        *,
        frame: NarrativeRiverFrame,
        delta_payload: dict[str, Any] | SceneRiverDelta,
    ) -> tuple[SceneRiverDelta, Path]:
        payload = (
            delta_payload.model_dump(mode="json") if isinstance(delta_payload, SceneRiverDelta) else deepcopy(delta_payload)
        )
        if payload.get("scene_id") != frame.scene_id:
            raise ValueError("scene delta must close the same scene as the frame")
        payload["storage_receipt"] = self.store.delta_receipt(frame.scene_id)
        delta = self.adapter.create_delta(payload)
        return delta, self.store.save_delta(delta)

    def run_scene(
        self,
        *,
        scene_request: dict[str, Any],
        canon_snapshot: dict[str, Any],
        draft_text: str,
        delta_payload: dict[str, Any],
        axioms_text: str = "",
        prior_delta: SceneRiverDelta | dict[str, Any] | None = None,
        auto_prior: bool = True,
        fail_on_error: bool = False,
    ) -> dict[str, Any]:
        frame, frame_path = self.build_and_store_frame(
            scene_request=scene_request,
            canon_snapshot=canon_snapshot,
            prior_delta=prior_delta,
            auto_prior=auto_prior,
        )
        _prompt, prompt_path = self.render_and_store_prompt(frame, axioms_text=axioms_text)
        report, report_path = self.validate_and_store_draft(frame, draft_text)
        result: dict[str, Any] = {
            "scene_id": frame.scene_id,
            "frame_id": frame.frame_id,
            "frame_path": str(frame_path),
            "prompt_path": str(prompt_path),
            "validation_report_path": str(report_path),
            "delta_path": None,
            "validation_findings": len(report.findings),
            "validation_has_errors": report.has_errors,
            "scene_closed": False,
            "closed_scene_id": None,
        }
        if fail_on_error and report.has_errors:
            return result
        delta, delta_path = self.close_scene(frame=frame, delta_payload=delta_payload)
        result.update(
            {
                "delta_path": str(delta_path),
                "scene_closed": True,
                "closed_scene_id": delta.scene_id,
            }
        )
        return result
