"""Focused and end-to-end tests for the Narrative River Adapter workflow."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from modules.narrative_river import (
    NarrativeRiverAdapter,
    NarrativeRiverFrame,
    NarrativeRiverStore,
    NarrativeRiverWorkflow,
    SceneRunRequest,
    SceneRiverDelta,
    dumps_json,
    dumps_yaml,
    loads_json,
    loads_yaml,
)
from modules.narrative_river.cli import main


def frame_payload(scene_id: str = "DARKSTAR.CH05.QUIET_LANE.02") -> dict:
    return {
        "scene_id": scene_id,
        "chapter_id": "DARKSTAR.CH05",
        "generated_at_utc": "2026-07-26T18:00:00Z",
        "narrative_status": {
            "current_state": "draft",
            "persistence_class": "draft_persistent",
            "storage_receipt": "file:///temporary/test-fixture",
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


def delta_payload(scene_id: str = "DARKSTAR.CH05.QUIET_LANE.02") -> dict:
    return {
        "scene_id": scene_id,
        "state_changes": ["The approach is confirmed hostile."],
        "new_questions": ["Why was the credential left active?"],
        "closed_questions": ["Who initiated the purge?"],
        "resolved_sediment_ids": ["SED-LETHAN-WITHDRAWAL"],
        "new_sediment": [
            {
                "sediment_id": "SED-IVEN-CREDENTIAL",
                "source_event_id": scene_id,
                "description": "Iven withheld the credential before launch.",
                "current_effect": "Trust and reliance move in different directions.",
            }
        ],
        "next_scene_requirements": ["The credential dispute remains active."],
        "canon_candidates": ["Kallis used layered defenses."],
    }


def test_frame_round_trips_json_and_yaml() -> None:
    adapter = NarrativeRiverAdapter()
    frame = adapter.build_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    assert loads_json(NarrativeRiverFrame, dumps_json(frame)) == frame
    assert loads_yaml(NarrativeRiverFrame, dumps_yaml(frame)) == frame


def test_frame_id_and_prompt_are_deterministic() -> None:
    adapter = NarrativeRiverAdapter()
    first = adapter.build_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    second = adapter.build_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    assert first.frame_id == second.frame_id
    assert adapter.render_prompt_contract(first) == adapter.render_prompt_contract(second)
    assert "UNRESOLVED QUESTIONS" in adapter.render_prompt_contract(first)


def test_unsupported_schema_versions_fail_closed() -> None:
    adapter = NarrativeRiverAdapter()
    payload = frame_payload()
    payload["schema_version"] = "99.0.0"
    snapshot = canon_snapshot()
    with pytest.raises(ValidationError):
        adapter.build_frame(scene_request=payload, canon_snapshot=snapshot)
    with pytest.raises(ValidationError):
        SceneRiverDelta.model_validate({"schema_version": "99.0.0", "scene_id": "S"})


@pytest.mark.parametrize("scene_id", [None, "", "   ", 7])
def test_build_frame_rejects_missing_or_invalid_scene_id(scene_id: object) -> None:
    adapter = NarrativeRiverAdapter()
    snapshot = canon_snapshot()
    payload = frame_payload()
    if scene_id is None:
        payload.pop("scene_id")
    else:
        payload["scene_id"] = scene_id

    with pytest.raises(ValueError, match="non-empty scene_id"):
        adapter.build_frame(
            scene_request=payload,
            canon_snapshot=snapshot,
        )


def test_build_frame_does_not_mutate_inputs_and_carries_delta() -> None:
    adapter = NarrativeRiverAdapter()
    request = frame_payload()
    original = deepcopy(request)
    prior_delta = SceneRiverDelta.model_validate(delta_payload())
    frame = adapter.build_frame(scene_request=request, canon_snapshot=canon_snapshot(), prior_delta=prior_delta)
    assert request == original
    assert "Why was the credential left active?" in frame.unresolved_questions
    assert "Who initiated the purge?" not in frame.unresolved_questions
    assert "The credential dispute remains active." in frame.required_downstream_effects
    assert not any(item.sediment_id == "SED-LETHAN-WITHDRAWAL" for item in frame.sediment)
    assert any(item.sediment_id == "SED-IVEN-CREDENTIAL" for item in frame.sediment)


def test_prior_delta_filters_normalized_questions_and_sediment_ids() -> None:
    adapter = NarrativeRiverAdapter()
    request = frame_payload()
    request["unresolved_questions"] = ["Who initiated the purge? "]
    request["sediment"][0]["sediment_id"] = "SED-LETHAN-WITHDRAWAL "

    frame = adapter.build_frame(
        scene_request=request,
        canon_snapshot=canon_snapshot(),
        prior_delta=delta_payload(),
    )

    assert "Who initiated the purge?" not in frame.unresolved_questions
    assert not any(
        item.sediment_id == "SED-LETHAN-WITHDRAWAL" for item in frame.sediment
    )


def test_persistent_frame_requires_storage_receipt() -> None:
    adapter = NarrativeRiverAdapter()
    snapshot = canon_snapshot()
    payload = frame_payload()
    payload["narrative_status"].pop("storage_receipt")
    with pytest.raises(ValidationError):
        adapter.build_frame(scene_request=payload, canon_snapshot=snapshot)


def test_ranges_and_duplicate_ids_fail_closed() -> None:
    adapter = NarrativeRiverAdapter()
    snapshot = canon_snapshot()
    payload = frame_payload()
    payload["active_pressures"]["tactical"] = 1.2
    with pytest.raises(ValidationError):
        adapter.build_frame(scene_request=payload, canon_snapshot=snapshot)
    duplicate = frame_payload()
    duplicate["evidence_state"].append(deepcopy(duplicate["evidence_state"][0]))
    with pytest.raises(ValidationError):
        adapter.build_frame(scene_request=duplicate, canon_snapshot=snapshot)


def test_advisory_validator_cites_known_failure_patterns() -> None:
    adapter = NarrativeRiverAdapter()
    frame = adapter.build_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    draft = """Neither of them turned it into banter.
+\"Gone.\"
+\"When?\"
+\"Before Lethan.\"
+\"What then?\"
+The sediment moved through the RiverCycle reservoir.
+\"What you came to find.\"
+""".replace("+", "")
    report = adapter.validate_draft(frame, draft)
    rules = {finding.rule_id for finding in report.findings}
    assert {
        "AXIOM_2_SELF_AWARE_NARRATION",
        "AXIOM_10_SHORT_DIALOGUE_RUN",
        "AXIOM_10_TRAILER_LINE",
        "SURFACE_LANGUAGE_SYMBOLIC_BLEED",
    } <= rules
    assert report.has_errors


@pytest.mark.parametrize(
    ("failure_kind", "expected_rule", "draft"),
    [
        (
            "evidence",
            "AXIOM_7_EVIDENCE_LAYER_COLLAPSE",
            "The approach corridor is prepared as an ambush.",
        ),
        (
            "hierarchy",
            "AXIOM_5_HIERARCHY_DRIFT",
            "The junior officer negotiated casually with supreme authority.",
        ),
        (
            "scarcity",
            "AXIOM_11_SCARCITY_VIOLATION",
            "The crew fired the Javelin munitions to clear the approach.",
        ),
    ],
)
def test_fail_on_error_blocks_specified_validation_failures(
    tmp_path: Path,
    failure_kind: str,
    expected_rule: str,
    draft: str,
) -> None:
    request = frame_payload()
    if failure_kind == "hierarchy":
        request["institutional_constraints"] = [
            {
                "constraint_id": "INST-COMMAND-REGISTER",
                "authority": "SUPREME_COMMAND",
                "effect": "Junior officers use a formal command register.",
                "must_not_appear_as": [
                    "junior officer negotiated casually with supreme authority"
                ],
            }
        ]
    elif failure_kind == "scarcity":
        request["scarcity_state"][0]["current_quantity"] = 0

    store = NarrativeRiverStore(tmp_path / "river")
    result = NarrativeRiverWorkflow(store).run_scene(
        SceneRunRequest(
            scene_request=request,
            canon_snapshot=canon_snapshot(),
            draft_text=draft,
            delta_payload=delta_payload(),
            fail_on_error=True,
        )
    )

    report = json.loads(
        Path(result["validation_report_path"]).read_text(encoding="utf-8")
    )
    assert expected_rule in {finding["rule_id"] for finding in report["findings"]}
    assert result["validation_has_errors"] is True
    assert result["scene_closed"] is False
    assert result["delta_path"] is None
    assert store.load_manifest()["latest_closed_scene_id"] is None


def test_storage_paths_are_contained_and_manifested(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    workflow = NarrativeRiverWorkflow(store)
    request = frame_payload("../../DARKSTAR/SCENE")
    frame, path = workflow.build_and_store_frame(scene_request=request, canon_snapshot=canon_snapshot())
    assert store.root in path.parents
    assert ".." not in path.name
    assert frame.narrative_status.storage_receipt == path.as_uri()
    assert store.load_frame_for_scene(frame.scene_id) == frame


def test_end_to_end_scene_cycle_persists_all_artifacts(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    workflow = NarrativeRiverWorkflow(store)
    result = workflow.run_scene(
        SceneRunRequest(
            scene_request=frame_payload(),
            canon_snapshot=canon_snapshot(),
            draft_text=(
                "Tessa altered the route after Iven identified the false traffic "
                "picture. " * 8
            ),
            delta_payload=delta_payload(),
            axioms_text="Write as though the world exists independently of the prose.",
        )
    )
    for key in ("frame_path", "prompt_path", "validation_report_path", "delta_path"):
        assert Path(result[key]).exists()
    assert store.load_manifest()["latest_closed_scene_id"] == result["scene_id"]
    assert store.load_latest_delta() is not None


def test_next_scene_automatically_imports_latest_approved_delta(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    workflow = NarrativeRiverWorkflow(store)
    first_frame, _ = workflow.build_and_store_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    workflow.close_scene(frame=first_frame, delta_payload=delta_payload())

    second_request = frame_payload("DARKSTAR.CH06.NEXT")
    second_request["unresolved_questions"] = ["Who initiated the purge?"]
    second_request["sediment"] = deepcopy(frame_payload()["sediment"])
    second_frame, _ = workflow.build_and_store_frame(
        scene_request=second_request,
        canon_snapshot=canon_snapshot(),
    )
    assert second_frame.narrative_status.previous_scene_id == first_frame.scene_id
    assert "Who initiated the purge?" not in second_frame.unresolved_questions
    assert "Why was the credential left active?" in second_frame.unresolved_questions
    assert not any(item.sediment_id == "SED-LETHAN-WITHDRAWAL" for item in second_frame.sediment)
    assert any(item.sediment_id == "SED-IVEN-CREDENTIAL" for item in second_frame.sediment)


def test_explicit_previous_scene_requires_its_approved_delta(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    workflow = NarrativeRiverWorkflow(store)
    request = frame_payload("DARKSTAR.CH06.NEXT")
    request["narrative_status"]["previous_scene_id"] = "DARKSTAR.CH05.MISSING"

    with pytest.raises(FileNotFoundError, match="no delta recorded"):
        workflow.build_and_store_frame(
            scene_request=request,
            canon_snapshot=canon_snapshot(),
        )


def test_manifest_integrity_check_rejects_tampered_delta(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    workflow = NarrativeRiverWorkflow(store)
    frame, _ = workflow.build_and_store_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    _delta, delta_path = workflow.close_scene(frame=frame, delta_payload=delta_payload())
    delta_path.write_text(delta_path.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")
    with pytest.raises(ValueError, match="integrity verification"):
        store.load_latest_delta()


def test_manifest_record_cannot_escape_workspace(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    store.root.mkdir(parents=True)
    outside = tmp_path / "outside.yaml"
    outside.write_text("scene_id: ESCAPE\n", encoding="utf-8")
    store.manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "0.1.0",
                "latest_closed_scene_id": None,
                "scenes": {
                    "ESCAPE": {
                        "frame": {
                            "path": "../outside.yaml",
                            "sha256": "0" * 64,
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="escapes"):
        store.load_frame_for_scene("ESCAPE")


def test_manifest_symlink_cannot_escape_workspace(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    store.root.mkdir(parents=True)
    outside = tmp_path / "outside-manifest.json"
    outside.write_text(
        json.dumps(
            {
                "schema_version": "0.1.0",
                "latest_closed_scene_id": None,
                "scenes": {},
            }
        ),
        encoding="utf-8",
    )
    store.manifest_path.symlink_to(outside)

    with pytest.raises(ValueError, match="escapes"):
        store.load_manifest()


def test_cli_run_scene_is_a_real_trigger(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    scene_path = inputs / "scene.json"
    canon_path = inputs / "canon.json"
    draft_path = inputs / "draft.md"
    delta_path = inputs / "delta.json"
    scene_path.write_text(json.dumps(frame_payload()), encoding="utf-8")
    canon_path.write_text(json.dumps(canon_snapshot()), encoding="utf-8")
    draft_path.write_text("The crew changed course and preserved the evidence. " * 10, encoding="utf-8")
    delta_path.write_text(json.dumps(delta_payload()), encoding="utf-8")
    workspace = tmp_path / "workflow"

    exit_code = main(
        [
            "run-scene",
            "--workspace",
            str(workspace),
            "--allowed-root",
            str(tmp_path),
            "--scene-request",
            str(scene_path),
            "--canon-snapshot",
            str(canon_path),
            "--draft",
            str(draft_path),
            "--delta",
            str(delta_path),
        ]
    )
    assert exit_code == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["closed_scene_id"] == frame_payload()["scene_id"]
    assert Path(receipt["frame_path"]).exists()
    assert Path(receipt["delta_path"]).exists()


def test_cli_fail_on_error_returns_nonzero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    workflow = NarrativeRiverWorkflow(store)
    frame, frame_path = workflow.build_and_store_frame(scene_request=frame_payload(), canon_snapshot=canon_snapshot())
    draft_path = tmp_path / "draft.md"
    draft_path.write_text("Neither of them turned it into banter.", encoding="utf-8")
    exit_code = main(
        [
            "validate-draft",
            "--workspace",
            str(store.root),
            "--allowed-root",
            str(tmp_path),
            "--frame",
            str(frame_path),
            "--draft",
            str(draft_path),
            "--fail-on-error",
        ]
    )
    assert exit_code == 3
    assert json.loads(capsys.readouterr().out)["has_errors"] is True
    assert frame.scene_id in store.load_manifest()["scenes"]


def test_cli_rejects_input_outside_allowed_root(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    exit_code = main(
        [
            "build-frame",
            "--allowed-root",
            str(allowed_root),
            "--scene-request",
            str(outside),
            "--canon-snapshot",
            str(outside),
        ]
    )

    assert exit_code == 2
    assert "outside allowed root" in capsys.readouterr().err


def test_safe_scene_names_do_not_collide_after_truncation(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    first = "SCENE." + ("A" * 220) + ".ONE"
    second = "SCENE." + ("A" * 220) + ".TWO"
    assert store.frame_path(first) != store.frame_path(second)
    assert store.root in store.frame_path(first).parents
    assert store.root in store.frame_path(second).parents


def test_run_scene_fail_on_error_does_not_close_or_advance_chain(tmp_path: Path) -> None:
    store = NarrativeRiverStore(tmp_path / "river")
    workflow = NarrativeRiverWorkflow(store)
    result = workflow.run_scene(
        SceneRunRequest(
            scene_request=frame_payload(),
            canon_snapshot=canon_snapshot(),
            draft_text="Neither of them turned it into banter.",
            delta_payload=delta_payload(),
            fail_on_error=True,
        )
    )
    assert result["validation_has_errors"] is True
    assert result["scene_closed"] is False
    assert result["delta_path"] is None
    assert store.load_manifest()["latest_closed_scene_id"] is None
    assert store.load_latest_delta() is None
