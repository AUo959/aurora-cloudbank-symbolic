import pytest

from src.aurora.engines import NarrativeValidationEngine
from src.aurora.engines.narrative import TaskKind, Verdict


ENGINE = NarrativeValidationEngine()

MARA_INPUT = {
    "task_hint": "character_action_audit",
    "question": "Would Mara really abandon Teren here to save the rebellion?",
    "declared_layers": ["character", "motive", "event", "knowledge", "continuity"],
    "entities": [
        {"name": "Mara", "entity_type": "character", "role": "courier", "traits": ["duty-driven", "protective"]},
        {"name": "Teren", "entity_type": "character", "role": "friend"},
    ],
    "events": [
        {
            "label": "The rebellion will collapse if the signal is not delivered tonight.",
            "timing": "tonight",
            "participants": ["Mara"],
        },
        {
            "label": "Mara previously risked herself to protect Teren.",
            "timing": "prior",
            "participants": ["Mara", "Teren"],
        },
    ],
    "motives": [
        {"actor": "Mara", "label": "protect Teren", "strength": 0.93},
        {"actor": "Mara", "label": "preserve the rebellion", "strength": 0.88},
    ],
    "pressures": [
        {"actor": "Mara", "label": "duty to deliver the signal", "direction": "toward", "strength": 0.91},
        {"actor": "Mara", "label": "personal loyalty to Teren", "direction": "against", "strength": 0.86},
    ],
    "knowledge_states": [
        {
            "holder": "Mara",
            "fact": "If the signal does not go out tonight, the rebellion loses its safe corridor.",
        }
    ],
    "continuity": {"notes": ["Mara is consistently protective of Teren."]},
}

MARA_PROPOSAL = {
    "actor": "Mara",
    "action": "abandon Teren to deliver the rebellion signal",
    "type": "action",
}

DETECTIVE_INPUT = {
    "task_hint": "next_event_continuity_check",
    "question": "Can this happen next, with the detective accusing him that same night?",
    "declared_layers": ["event", "temporal", "knowledge", "continuity", "character"],
    "entities": [
        {"name": "Detective Vale", "entity_type": "character", "role": "detective"},
        {"name": "Rian", "entity_type": "character", "role": "suspect"},
    ],
    "events": [
        {
            "label": "Detective Vale privately learns that Rian is innocent.",
            "timing": "same afternoon",
            "participants": ["Detective Vale"],
        }
    ],
    "knowledge_states": [
        {"holder": "Detective Vale", "fact": "Rian is innocent."},
    ],
    "continuity": {"notes": ["Vale has been quietly trying to clear Rian."]},
}

DETECTIVE_PROPOSAL = {
    "actor": "Detective Vale",
    "action": "publicly accuse Rian that same night",
    "type": "event",
    "timing": "same_night",
}

HISTORICAL_INPUT = {
    "task_hint": "historical_plausibility_check",
    "question": "Could a pre-telegraph queen coordinate a same-day crackdown across six distant cities as stated?",
    "declared_layers": ["institutional", "temporal", "logistical", "political"],
    "entities": [
        {"name": "The Queen", "entity_type": "character", "role": "monarch"},
        {"name": "Crown Guard", "entity_type": "institution", "role": "security apparatus"},
        {"name": "The Six Cities", "entity_type": "city", "role": "distant provincial capitals"},
    ],
    "constraints": [
        {
            "label": "No telegraph or rapid long-distance signaling exists.",
            "constraint_type": "logistical",
            "severity": "hard",
        },
        {
            "label": "The cities are days apart by courier.",
            "constraint_type": "temporal",
            "severity": "hard",
        },
        {
            "label": "The crown must coordinate through provincial governors.",
            "constraint_type": "political",
            "severity": "soft",
        },
    ],
    "pressures": [
        {"actor": "The Queen", "label": "crown pressure to suppress unrest", "direction": "toward", "strength": 0.84},
    ],
    "continuity": {"notes": ["Orders normally move by courier over several days."]},
}

HISTORICAL_PROPOSAL = {
    "actor": "The Queen",
    "action": "coordinate a same-day crackdown across six distant cities",
    "type": "event",
    "timing": "same_day",
}


@pytest.mark.unit
@pytest.mark.aurora
@pytest.mark.parametrize(
    (
        "raw_input",
        "proposal",
        "expected_kind",
        "expected_verdict",
        "expected_layers",
        "support_snippet",
        "blocker_snippet",
    ),
    [
        (
            MARA_INPUT,
            MARA_PROPOSAL,
            TaskKind.CHARACTER_ACTION_AUDIT,
            Verdict.POSSIBLE_WITH_SETUP,
            ["character", "motive", "event", "knowledge", "continuity"],
            "rebellion",
            "protect Teren",
        ),
        (
            DETECTIVE_INPUT,
            DETECTIVE_PROPOSAL,
            TaskKind.NEXT_EVENT_CONTINUITY_CHECK,
            Verdict.STRAINED,
            ["event", "temporal", "knowledge", "continuity", "character"],
            "",
            "innocent",
        ),
        (
            HISTORICAL_INPUT,
            HISTORICAL_PROPOSAL,
            TaskKind.HISTORICAL_PLAUSIBILITY_CHECK,
            Verdict.CONTRADICTORY,
            ["institutional", "temporal", "logistical", "political"],
            "",
            "same-day coordination",
        ),
    ],
)
def test_narrative_engine_golden_cases(
    raw_input,
    proposal,
    expected_kind,
    expected_verdict,
    expected_layers,
    support_snippet,
    blocker_snippet,
):
    run = ENGINE.run(raw_input, proposal=proposal)

    assert run.request.task_kind == expected_kind, (  # nosec B101
        f"Expected task kind {expected_kind}, got {run.request.task_kind}"
    )
    assert run.response.verdict == expected_verdict, (  # nosec B101
        f"Expected verdict {expected_verdict}, got {run.response.verdict}"
    )
    assert run.evaluation.active_layers == expected_layers, (  # nosec B101
        f"Expected active layers {expected_layers}, got {run.evaluation.active_layers}"
    )
    assert run.response.supported_in_phase_one, "Expected phase-one support"  # nosec B101
    if support_snippet:
        assert any(support_snippet.lower() in item.lower() for item in run.response.main_supports), (  # nosec B101
            f"Expected support snippet {support_snippet!r}"
        )
    assert any(blocker_snippet.lower() in item.lower() for item in run.response.main_blockers), (  # nosec B101
        f"Expected blocker snippet {blocker_snippet!r}"
    )
    assert run.response.smallest_fix, "Expected a smallest-fix recommendation"  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_sparse_input_restraint_stays_minimal():
    run = ENGINE.run("a hero came to a fork in the road")

    assert run.request.task_kind == TaskKind.EXPANSION, (  # nosec B101
        f"Expected expansion, got {run.request.task_kind}"
    )
    assert not run.response.supported_in_phase_one, "Expected unsupported phase-one response"  # nosec B101
    assert run.response.verdict is None, f"Expected no verdict, got {run.response.verdict}"  # nosec B101
    assert not run.state.entities, f"Expected no entities, got {run.state.entities}"  # nosec B101
    assert not run.state.motives, f"Expected no motives, got {run.state.motives}"  # nosec B101
    assert run.state.uncertainties, "Expected sparse-input uncertainty"  # nosec B101
    assert run.response.confidence <= 0.2, f"Expected low confidence, got {run.response.confidence}"  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_missing_layer_honesty_reduces_confidence():
    run = ENGINE.run(
        {
            "task_hint": "character_action_audit",
            "question": "Would Ilya betray the crew here?",
            "entities": [{"name": "Ilya", "entity_type": "character", "role": "pilot"}],
            "events": [{"label": "Ilya has stayed with the crew through prior danger.", "timing": "prior"}],
            "continuity": {"notes": ["Ilya has been loyal so far."]},
        },
        proposal={"actor": "Ilya", "action": "betray the crew", "type": "action"},
    )

    assert "motive" in run.evaluation.missing_layers, f"Expected missing motive layer: {run.evaluation}"  # nosec B101
    assert run.response.verdict == Verdict.POSSIBLE_WITH_SETUP, (  # nosec B101
        f"Expected possible-with-setup verdict, got {run.response.verdict}"
    )
    assert run.response.confidence < 0.55, f"Expected reduced confidence, got {run.response.confidence}"  # nosec B101
    has_fix_guidance = any(
        "motive" in item.lower() or "pressure" in item.lower()
        for item in run.response.smallest_fix
    )
    assert has_fix_guidance, (  # nosec B101
        f"Expected motive or pressure smallest-fix guidance, got {run.response.smallest_fix}"
    )


@pytest.mark.unit
@pytest.mark.aurora
def test_symbolic_request_is_typed_unsupported_without_overclaim():
    run = ENGINE.run("Does the moon above the ruined bridge definitely symbolize rebirth?")

    assert run.request.task_kind == TaskKind.UNSUPPORTED, (  # nosec B101
        f"Expected unsupported, got {run.request.task_kind}"
    )
    assert not run.response.supported_in_phase_one, "Expected unsupported phase-one response"  # nosec B101
    assert run.response.verdict is None, f"Expected no verdict, got {run.response.verdict}"  # nosec B101
    assert run.response.main_supports == [], f"Expected no supports, got {run.response.main_supports}"  # nosec B101
    assert run.response.main_blockers == [], f"Expected no blockers, got {run.response.main_blockers}"  # nosec B101
    assert run.response.confidence <= 0.2, f"Expected low confidence, got {run.response.confidence}"  # nosec B101


@pytest.mark.unit
@pytest.mark.aurora
def test_proposal_stays_provisional_in_state():
    run = ENGINE.run(MARA_INPUT, proposal=MARA_PROPOSAL)

    proposed_events = [event for event in run.state.events if event.status == "proposed"]
    assert len(proposed_events) == 1, f"Expected one proposed event, got {proposed_events}"  # nosec B101
    assert proposed_events[0].label == "abandon Teren to deliver the rebellion signal", (  # nosec B101
        f"Unexpected proposed event label: {proposed_events[0].label}"
    )
    assert proposed_events[0].label not in run.state.continuity["established_events"], (  # nosec B101
        "Expected proposed event to stay out of established continuity"
    )
