from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest


SIMULATION_DIR = Path(__file__).resolve().parents[1] / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

from l1_character_actor import (  # noqa: E402
    PROFILE_PATH,
    BoundedCharacterActor,
    CharacterContext,
    CharacterProfileError,
)
from l1_character_actor_policy import (  # noqa: E402
    CharacterSpeechBoundaryError,
    enforce_diegetic_speech,
)


def _context(content: str, *, prior_actions=()) -> CharacterContext:
    return CharacterContext(
        run_id="59da8a1c-df89-4203-bdd9-5e5ad89090e6",
        tick=7,
        inbound={
            "message_id": "f337174f-19bf-405f-a6d0-d17f52392e32",
            "content": content,
        },
        station_records=(
            {
                "record_id": "record-maintenance",
                "subject": "event:event-maintenance",
                "provenance": "autonomous_runtime_event_ledger",
                "tick": 7,
                "value": "A scheduled maintenance queue advanced.",
            },
        ),
        character_knowledge=(
            {
                "record_id": "record-message",
                "subject": "communication:pilot-message",
                "provenance": "direct_communication_delivery",
                "tick": 7,
                "value": content,
            },
        ),
        recent_events=(
            {
                "event_id": "event-maintenance",
                "kind": "maintenance_queue_progress",
                "tick": 7,
            },
        ),
        prior_actions=prior_actions,
        unresolved_facts=(
            "exact_lagrange_point",
            "exact_current_human_crew_complement",
        ),
    )


@pytest.mark.unit
def test_status_request_is_driven_by_character_duties_and_local_records():
    action = BoundedCharacterActor().decide(
        _context("Commander, how is everything up there? Report station status.")
    )

    assert action["perceived_intents"] == [
        "station_operations_status",
        "welfare_check",
    ]
    assert action["selected_action"] == "review_watch_and_report"
    assert action["duty_drivers"][0] == {
        "id": "station_operations",
        "basis": "Maintain awareness of station operations and material exceptions.",
    }
    assert action["principle_drivers"][0] == {
        "id": "quiet_authority",
        "basis": (
            "Inspect available evidence before speaking and report without "
            "theatrical emphasis."
        ),
    }
    assert action["knowledge_inputs"] == [
        {
            "record_id": "record-maintenance",
            "subject": "event:event-maintenance",
            "provenance": "autonomous_runtime_event_ledger",
            "tick": 7,
            "scope": "station_record",
        },
        {
            "record_id": "record-message",
            "subject": "communication:pilot-message",
            "provenance": "direct_communication_delivery",
            "tick": 7,
            "scope": "character_knowledge",
        },
    ]
    assert action["response_content"] == (
        "Pilot, Thorne. We're steady here. Maintenance moved forward this watch. "
        "I'm keeping the remaining work under command review and will relay any "
        "material change."
    )
    assert action["knowledge_gaps"] == [
        "exact_lagrange_point",
        "exact_current_human_crew_complement",
    ]
    assert "Lagrange" not in action["response_content"]
    assert "crew complement" not in action["response_content"]
    assert "unresolved" not in action["response_content"]
    assert "run" not in action["response_content"]


@pytest.mark.unit
def test_actor_decision_is_deterministic_for_the_same_context():
    actor = BoundedCharacterActor()
    context = _context("Status report, Commander.")
    first_decision = actor.decide(context)
    repeated_decision = actor.decide(context)

    assert first_decision == repeated_decision


@pytest.mark.unit
def test_message_meaning_changes_the_selected_character_action():
    actor = BoundedCharacterActor()
    contact = actor.decide(_context("Commander, radio check."))
    emergency = actor.decide(_context("Commander, is there an emergency?"))

    assert contact["selected_action"] == "acknowledge_and_open_channel"
    assert "operational question or decision" in contact["response_content"]
    assert [
        item["action"]
        for item in contact["options_considered"]
        if item["disposition"] == "selected"
    ] == ["acknowledge_and_open_channel"]
    assert emergency["selected_action"] == "assess_and_escalate_if_warranted"
    assert "cannot confirm the current emergency status" in emergency[
        "response_content"
    ].casefold()


@pytest.mark.unit
def test_recorded_emergency_remains_decision_relevant_after_a_later_event():
    context = replace(
        _context("Commander, is there an emergency?"),
        recent_events=(
            {"event_id": "event-emergency", "kind": "emergency_alarm", "tick": 6},
            {
                "event_id": "event-maintenance",
                "kind": "maintenance_queue_progress",
                "tick": 7,
            },
        ),
    )

    action = BoundedCharacterActor().decide(context)

    assert "An emergency has been recorded" in action["response_content"]
    assessment = next(
        item
        for item in action["operational_steps"]
        if item["kind"] == "assess_command_exception"
    )
    assert assessment["result"] == "recorded_emergency"


@pytest.mark.unit
def test_governed_emergency_overrides_later_routine_event_for_status_report():
    context = replace(
        _context("Commander, report station status."),
        governed_records=(
            {
                "record_id": "record-emergency",
                "subject": "emergency_active",
                "value": True,
                "provenance": "triplex:test:unit-test",
                "tick": 6,
            },
        ),
    )

    action = BoundedCharacterActor().decide(context)

    assert action["selected_action"] == "assess_and_escalate_if_warranted"
    assert "An emergency has been recorded" in action["response_content"]
    assert not any(
        phrase in action["response_content"].casefold()
        for phrase in ("no emergency", "nothing in the command record")
    )
    assert action["knowledge_inputs"][-1]["scope"] == "governed_record"


@pytest.mark.unit
def test_prior_character_commitment_shapes_followup_language():
    previous = {
        "action_id": "prior-action",
        "actor_id": "CMD_001",
        "commitments": [
            {
                "commitment": "monitor_maintenance_queue",
                "status": "active",
                "owner": "CMD_001",
            }
        ],
    }
    action = BoundedCharacterActor().decide(
        _context("Status report, Commander.", prior_actions=(previous,))
    )

    assert action["continuity_inputs"] == ["prior-action"]
    assert "stays under command review" in action["response_content"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "phrase",
    (
        "in this run",
        "runtime projection",
        "canon-level",
        "knowledge gaps",
        "observation aperture",
    ),
)
def test_character_speech_boundary_rejects_control_plane_language(phrase: str):
    with pytest.raises(CharacterSpeechBoundaryError, match="non-diegetic"):
        enforce_diegetic_speech(f"Pilot, Thorne. The {phrase} is clear.")


@pytest.mark.unit
@pytest.mark.parametrize(
    ("field", "value"),
    (("role", "Fleet Admiral"), ("clearance", "L5_COMMAND")),
)
def test_actor_fails_closed_when_identity_projection_conflicts(
    tmp_path: Path,
    field: str,
    value: str,
):
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    payload["profiles"]["CMD_001"]["identity"][field] = value
    drifted = tmp_path / "drifted-profile.json"
    drifted.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(CharacterProfileError, match="conflicts with staff authority"):
        BoundedCharacterActor(drifted)


@pytest.mark.unit
def test_actor_fails_closed_when_profile_evidence_escapes_repository(
    tmp_path: Path,
):
    external_profile = tmp_path / "valid-external-profile.json"
    external_profile.write_text(PROFILE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    actor = BoundedCharacterActor(external_profile)

    with pytest.raises(CharacterProfileError, match="escapes the repository"):
        actor.decide(_context("Status report, Commander."))
