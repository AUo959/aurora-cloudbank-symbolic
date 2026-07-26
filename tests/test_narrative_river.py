"""Focused tests for the passive Narrative River Adapter foundation."""

from __future__ import annotations

from copy import deepcopy

import pytest
from pydantic import ValidationError

from modules.narrative_river import (
    NarrativeRiverAdapter,
    NarrativeRiverFrame,
    SceneRiverDelta,
    dumps_json,
    dumps_yaml,
    loads_json,
    loads_yaml,
)


def frame_payload() -> dict:
    return {
        "scene_id": "DARKSTAR.CH05.QUIET_LANE.02",
        "chapter_id": "DARKSTAR.CH05",
        "generated_at_utc": "2026-07-26T18:00:00Z",
        "narrative_status": {
            "current_state": "draft",
            "persistence_class": "draft_persistent",
            "storage_receipt": "git:agent/narrative-river-adapter-spec/test-fixture",
        },
        "viewpoint": {
            "mode": "close_third",
            "focal_character_ids": ["TESSA_KORR"],
            "prohibited_omniscience": True,
        },
        "scene_objective": {
            "operational_goal": "Reach Kallis Foundry before the archive purge completes.",
            "dramatic_goal": "Show planning under pressure and useful disagreement.",
            "required_state_change": "The approach is confirmed hostile and a witness is recovered.",
        },
        "incoming_flows": [
            {
                "flow_id": "FLOW-KALLIS-PURGE",
                "flow_type": "evidence_loss",
                "source_id": "KALLIS_FOUNDRY",
                "target_id": "THIRD_MEASURE_CREW",
                "carrier": "live_archive_telemetry",
                "strength": 0.86,
                "confidence": 0.91,
            }
        ],
        "active_pressures": {"tactical": 0.77, "evidentiary": 0.91},
        "sediment": [
            {
                "sediment_id": "SED-LETHAN-WITHDRAWAL",
                "source_event_id": "DARK_STAR_BOARDING",
                "description": "The withdrawal disagreement remains unresolved.",
                "affected_actor_ids": ["TESSA_KORR", "IVEN_RAAL", "MAELIN_SAYE"],
                "current_effect": "Each officer interprets uncertainty through a different responsibility.",
            }
        ],
        "evidence_state": [
            {
                "claim_id": "CLAIM-AMBUSH",
                "claim": "The approach corridor is prepared as an ambush.",
                "status": "hypothesis",
                "support": ["unusually clean traffic picture"],
                "confidence": 0.58,
            }
        ],
        "actor_interpretations": [
            {
                "actor_id": "IVEN_RAAL",
                "interpretation": "The clean traffic picture indicates deliberate preparation.",
                "preferred_response": "Expose the trap through an independent decoy.",
                "blind_spot": "He may withhold preparation until he considers it verified.",
            }
        ],
        "scarcity_state": [
            {
                "scarce_asset": "Javelin munitions",
                "current_quantity": 3,
                "consequence": "Firing them now reduces later breaching and defense options.",
            }
        ],
        "required_downstream_effects": ["Iven's warning is only partially validated."],
        "prohibited_shortcuts": ["The administrative root solves the entire fight."],
        "unresolved_questions": ["Who initiated the purge?"],
        "exit_conditions": ["The layered ambush is exposed."],
    }


def canon_snapshot() -> dict:
    return {
        "repository": "AUo959/CanonRec",
        "commit_sha": "abc123",
        "source_files": ["canon/L2/event.json"],
        "authority_status": "mixed",
    }


def test_frame_round_trips_json_and_yaml() -> None:
    adapter = NarrativeRiverAdapter()
    frame = adapter.build_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())

    assert loads_json(NarrativeRiverFrame, dumps_json(frame)) == frame
    assert loads_yaml(NarrativeRiverFrame, dumps_yaml(frame)) == frame
    assert frame.canonical_json() == frame.canonical_json()


def test_frame_id_and_prompt_are_deterministic() -> None:
    adapter = NarrativeRiverAdapter()
    first = adapter.build_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    second = adapter.build_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())

    assert first.frame_id == second.frame_id
    assert adapter.render_prompt_contract(first) == adapter.render_prompt_contract(second)
    assert "SURFACE-LANGUAGE FIREWALL" in adapter.render_prompt_contract(first)
    assert "The administrative root solves the entire fight." in adapter.render_prompt_contract(first)


def test_build_frame_does_not_mutate_inputs_and_carries_delta() -> None:
    adapter = NarrativeRiverAdapter()
    request = frame_payload()
    original = deepcopy(request)
    prior_delta = SceneRiverDelta(
        scene_id="DARKSTAR.CH04",
        new_sediment=[
            {
                "sediment_id": "SED-IVEN-CREDENTIAL",
                "source_event_id": "DARKSTAR.CH04",
                "description": "Iven withheld a credential before launch.",
                "current_effect": "Trust and operational reliance move in opposite directions.",
            }
        ],
        new_questions=["Why was the credential left active?"],
        next_scene_requirements=["The credential dispute remains active."],
    )

    frame = adapter.build_frame(
        scene_request=request,
        canon_snapshot=canon_snapshot(),
        prior_delta=prior_delta,
    )

    assert request == original
    assert "Why was the credential left active?" in frame.unresolved_questions
    assert "The credential dispute remains active." in frame.required_downstream_effects
    assert any(item.sediment_id == "SED-IVEN-CREDENTIAL" for item in frame.sediment)


def test_persistent_frame_requires_storage_receipt() -> None:
    payload = frame_payload()
    payload["narrative_status"].pop("storage_receipt")
    adapter = NarrativeRiverAdapter()

    with pytest.raises(ValidationError):
        adapter.build_frame(scene_request=payload, canon_snapshot=canon_snapshot())


def test_ranges_and_duplicate_ids_fail_closed() -> None:
    adapter = NarrativeRiverAdapter()
    payload = frame_payload()
    payload["active_pressures"]["tactical"] = 1.2

    with pytest.raises(ValidationError):
        adapter.build_frame(scene_request=payload, canon_snapshot=canon_snapshot())

    duplicate = frame_payload()
    duplicate["evidence_state"].append(deepcopy(duplicate["evidence_state"][0]))
    with pytest.raises(ValidationError):
        adapter.build_frame(scene_request=duplicate, canon_snapshot=canon_snapshot())


def test_advisory_validator_cites_known_failure_patterns() -> None:
    adapter = NarrativeRiverAdapter()
    frame = adapter.build_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    draft = """Neither of them turned it into banter.
\"Gone.\"
\"When?\"
\"Before Lethan.\"
\"What then?\"
The sediment moved through the RiverCycle reservoir.
\"What you came to find.\"
"""

    report = adapter.validate_draft(frame, draft)
    rules = {finding.rule_id for finding in report.findings}

    assert "AXIOM_2_SELF_AWARE_NARRATION" in rules
    assert "AXIOM_10_SHORT_DIALOGUE_RUN" in rules
    assert "AXIOM_10_TRAILER_LINE" in rules
    assert "SURFACE_LANGUAGE_SYMBOLIC_BLEED" in rules
    assert all(finding.passage or finding.rule_id == "FRAME_REQUIRED_EFFECTS_COVERAGE" for finding in report.findings)


def test_create_delta_is_explicit_and_non_mutating() -> None:
    adapter = NarrativeRiverAdapter()
    payload = {
        "scene_id": "DARKSTAR.CH05.QUIET_LANE.02",
        "state_changes": ["The approach is confirmed hostile."],
        "canon_candidates": ["Kallis used layered defenses."],
    }
    original = deepcopy(payload)

    delta = adapter.create_delta(payload)

    assert payload == original
    assert delta.scene_id == payload["scene_id"]
    assert delta.canon_candidates == ["Kallis used layered defenses."]
