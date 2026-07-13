from __future__ import annotations

from collections.abc import Callable
from unittest import TestCase

from simulation.scenario_seed_initializer import (
    ScenarioSeedInitializationError,
    initialize_from_uptake_packet,
)

CHECK = TestCase()


def sample_packet() -> dict:
    return {
        "source_card_id": "SCN-0903",
        "consumer_payloads": {
            "simulation_initializer": {
                "seed": 903,
                "ticks": 4,
                "anchor_seed": "EOS_SEED_ORION",
                "initial_condition_vector": {
                    "roles": [
                        "Veteran Trainer",
                        "Civil Authority",
                        "Credential Institution",
                        "Proxy Actor",
                    ],
                    "pressure": ["clock", "legitimacy", "escalation"],
                    "knobs": {
                        "Dominant solver": "truth | diplomacy | containment | reform",
                        "Institution strength": "strong enforcement vs hollow legitimacy",
                        "Mobility": "localized incident -> multi-region mobilization",
                        "Norm enforcement": "high taboo -> low panic",
                        "Power distribution": "state vs league vs sponsors vs insurgents",
                    },
                },
                "runtime_freedoms": [
                    "agent_policy_variation",
                    "knob_sweep_or_sensitivity_run",
                    "exogenous_pressure_variation",
                    "multi_outcome_branch_observation",
                    "post_run_narrative_rendering",
                ],
                "expected_end_state_handling": (
                    "expected_end_states are observation categories and fixture-coverage labels only; "
                    "they must not be converted into required runtime endings."
                ),
            }
        },
        "boundary_assertions": {
            "root_control_plane_only": True,
            "writes_nested_repos": False,
            "cloudbank_runtime_wiring": "not_authorized_by_this_packet",
            "canonrec_promotion": "not_authorized_by_this_packet",
        },
    }


def assert_raises_message(
    exc_type: type[Exception],
    message_fragment: str,
    action: Callable[[], object],
) -> None:
    """Assert that an action raises an expected exception message fragment."""

    try:
        action()
    except exc_type as exc:
        CHECK.assertIn(message_fragment, str(exc))
        return
    raise AssertionError(f"Expected {exc_type.__name__} containing {message_fragment!r}")


def test_initialize_from_root_uptake_packet_preserves_open_outcome_contract():
    initializer = initialize_from_uptake_packet(sample_packet())

    CHECK.assertEqual(initializer.source_card_id, "SCN-0903")
    CHECK.assertEqual(initializer.seed, 903)
    CHECK.assertEqual(initializer.ticks, 4)
    CHECK.assertEqual(initializer.anchor_seed, "EOS_SEED_ORION")
    CHECK.assertIn("multi_outcome_branch_observation", initializer.runtime_freedoms)

    initial_state = initializer.to_initial_state()
    CHECK.assertEqual(
        initial_state["initial_condition_vector"]["roles"][0],
        "Veteran Trainer",
    )
    CHECK.assertNotIn("expected_end_states", initial_state)
    CHECK.assertIn(
        "required runtime endings",
        initial_state["expected_end_state_handling"],
    )


def test_initialize_from_direct_simulation_payload_is_supported():
    payload = sample_packet()["consumer_payloads"]["simulation_initializer"]

    initializer = initialize_from_uptake_packet(payload)

    CHECK.assertEqual(initializer.source_card_id, "unknown")
    CHECK.assertEqual(initializer.to_initial_state()["seed"], 903)


def test_rejects_nested_write_or_canon_promotion_authorization():
    packet = sample_packet()
    packet["boundary_assertions"]["writes_nested_repos"] = True

    assert_raises_message(
        ScenarioSeedInitializationError,
        "nested repo writes",
        lambda: initialize_from_uptake_packet(packet),
    )

    packet = sample_packet()
    packet["boundary_assertions"]["canonrec_promotion"] = "authorized"

    assert_raises_message(
        ScenarioSeedInitializationError,
        "CanonRec promotion",
        lambda: initialize_from_uptake_packet(packet),
    )


def test_rejects_scripted_outcome_semantics():
    packet = sample_packet()
    packet["consumer_payloads"]["simulation_initializer"]["scripted_outcome"] = "Civil authority wins"

    assert_raises_message(
        ScenarioSeedInitializationError,
        "scripted_outcome",
        lambda: initialize_from_uptake_packet(packet),
    )


def test_rejects_low_emergence_capacity_payloads():
    packet = sample_packet()
    packet["consumer_payloads"]["simulation_initializer"]["initial_condition_vector"]["roles"] = ["one"]

    assert_raises_message(
        ScenarioSeedInitializationError,
        "roles",
        lambda: initialize_from_uptake_packet(packet),
    )
