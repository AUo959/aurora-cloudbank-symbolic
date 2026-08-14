from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from simulation.runtime.gumas_command_policy.policy import (
    COMMANDER_FIELDS,
    ROLE_ORDER,
    decide,
    normalize_command_team,
    normalize_observation,
    score_specialist,
    score_strategic,
)

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
BASELINE = (
    ROOT
    / "simulation/baselines/gumas/"
    "GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
)


def _baseline():
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def _team(side: str):
    return copy.deepcopy(_baseline()["sides"][side]["command_team"])


def _identity():
    return {
        "baseline_id": "SIM-L2-FR-P17-EQUAL-001",
        "baseline_version": "1.2",
    }


def _observation():
    return {
        "contact_quality": 800,
        "relative_advantage": 400,
        "own_damage": 150,
        "enemy_damage_estimate": 150,
        "logistics_strain": 150,
        "mobility_margin": 800,
        "geometry_opportunity": 100,
        "withdrawal_viability": 700,
        "mission_pressure": 750,
        "time_pressure": 500,
        "negotiation_signal": 0,
        "ew_opportunity": 500,
        "carrier_opportunity": 600,
        "repair_need": 100,
        "enemy_closing_pressure": 600,
        "uncertainty": 250,
    }


def test_replay_order_independence_and_prose_inertness():
    team = _team("loyalist")
    observation = _observation()
    first = decide(
        team,
        observation,
        side_id="loyalist",
        fleet_id="TF-LOYALIST-P17",
        decision_epoch=0,
        baseline_identity=_identity(),
    )
    replay = decide(
        list(reversed(team)),
        dict(reversed(list(observation.items()))),
        side_id="loyalist",
        fleet_id="TF-LOYALIST-P17",
        decision_epoch=0,
        baseline_identity=_identity(),
    )
    assert first == replay

    changed_prose = copy.deepcopy(team)
    for member in changed_prose:
        member["characteristic"] = "Different prose that must remain inert."
        member["name"] = "Display Name Is Non-Authoritative"
    prose_result = decide(
        changed_prose,
        observation,
        side_id="loyalist",
        fleet_id="TF-LOYALIST-P17",
        decision_epoch=0,
        baseline_identity=_identity(),
    )
    assert first == prose_result
    assert first["prose_inputs_used"] is False
    assert first["rng_used"] is False


def test_side_label_is_not_a_behavioral_input():
    team = _team("loyalist")
    observation = _observation()
    left = decide(
        team,
        observation,
        side_id="alpha",
        fleet_id="fleet-a",
        decision_epoch=7,
        baseline_identity=_identity(),
    )
    right = decide(
        team,
        observation,
        side_id="beta",
        fleet_id="fleet-b",
        decision_epoch=7,
        baseline_identity=_identity(),
    )
    assert left["orders"] == right["orders"]
    assert left["strategic"] == right["strategic"]
    assert left["specialists"] == right["specialists"]


def test_strategic_attribute_monotonicity():
    team = normalize_command_team(_team("loyalist"))
    commander = dict(team["commander"]["attributes_q1000"])
    observation = normalize_observation(_observation())
    base = score_strategic(commander, observation)

    aggressive = dict(commander)
    aggressive["aggression"] = min(1000, commander["aggression"] + 200)
    aggressive_scores = score_strategic(aggressive, observation)
    assert (
        aggressive_scores["scores"]["PRESS"]["score"]
        >= base["scores"]["PRESS"]["score"]
    )
    assert (
        aggressive_scores["scores"]["CEASEFIRE_PROBE"]["score"]
        <= base["scores"]["CEASEFIRE_PROBE"]["score"]
    )

    casualty = dict(commander)
    casualty["casualty_aversion"] = min(
        1000, commander["casualty_aversion"] + 200
    )
    casualty_scores = score_strategic(casualty, observation)
    assert (
        casualty_scores["scores"]["DISENGAGE"]["score"]
        >= base["scores"]["DISENGAGE"]["score"]
    )
    assert (
        casualty_scores["scores"]["CEASEFIRE_PROBE"]["score"]
        >= base["scores"]["CEASEFIRE_PROBE"]["score"]
    )
    assert (
        casualty_scores["scores"]["PRESS"]["score"]
        <= base["scores"]["PRESS"]["score"]
    )

    negotiate = dict(commander)
    negotiate["negotiation_openness"] = min(
        1000, commander["negotiation_openness"] + 200
    )
    assert (
        score_strategic(negotiate, observation)["scores"]
        ["CEASEFIRE_PROBE"]["score"]
        >= base["scores"]["CEASEFIRE_PROBE"]["score"]
    )

    maneuver = dict(commander)
    maneuver["adaptability"] = min(1000, commander["adaptability"] + 100)
    maneuver["deception"] = min(1000, commander["deception"] + 100)
    assert (
        score_strategic(maneuver, observation)["scores"]
        ["POSITIONAL_MANEUVER"]["score"]
        >= base["scores"]["POSITIONAL_MANEUVER"]["score"]
    )


def test_specialist_domain_skill_is_role_local():
    team = _team("loyalist")
    observation = _observation()
    base = decide(
        team,
        observation,
        side_id="loyalist",
        fleet_id="TF-LOYALIST-P17",
        decision_epoch=0,
        baseline_identity=_identity(),
    )
    changed = copy.deepcopy(team)
    for member in changed:
        if member["assignment"] == "engineering":
            member["attributes"]["domain_skill"] = 1.0
    variant = decide(
        changed,
        observation,
        side_id="loyalist",
        fleet_id="TF-LOYALIST-P17",
        decision_epoch=0,
        baseline_identity=_identity(),
    )
    assert base["strategic"] == variant["strategic"]
    for role in ROLE_ORDER:
        if role != "engineering":
            assert base["specialists"][role] == variant["specialists"][role]
    assert (
        base["specialists"]["engineering"]
        != variant["specialists"]["engineering"]
    )


def test_lower_alignment_can_create_more_explicit_dissent():
    observation = normalize_observation(
        {
            "contact_quality": 700,
            "relative_advantage": 500,
            "own_damage": 800,
            "enemy_damage_estimate": 200,
            "logistics_strain": 700,
            "mobility_margin": 500,
            "geometry_opportunity": 300,
            "withdrawal_viability": 800,
            "mission_pressure": 800,
            "time_pressure": 500,
            "negotiation_signal": 0,
            "ew_opportunity": 300,
            "carrier_opportunity": 300,
            "repair_need": 700,
            "enemy_closing_pressure": 800,
            "uncertainty": 500,
        }
    )
    commander = {field: 500 for field in COMMANDER_FIELDS}
    aligned_attrs = {
        "domain_skill": 900,
        "initiative": 500,
        "discipline": 900,
        "stress_tolerance": 900,
        "risk_tolerance": 200,
        "commander_alignment": 900,
    }
    aligned = score_specialist(
        "tactical", aligned_attrs, commander, observation, "PRESS"
    )
    independent_attrs = dict(aligned_attrs)
    independent_attrs["commander_alignment"] = 0
    independent = score_specialist(
        "tactical", independent_attrs, commander, observation, "PRESS"
    )
    assert aligned["dissent_q1000"] == 0
    assert independent["dissent_q1000"] > aligned["dissent_q1000"]
    assert independent["independence_q1000"] > aligned["independence_q1000"]


def test_control_teams_diverge_only_through_numeric_attributes():
    observation = _observation()
    loyalist = decide(
        _team("loyalist"),
        observation,
        side_id="loyalist",
        fleet_id="TF-LOYALIST-P17",
        decision_epoch=0,
        baseline_identity=_identity(),
    )
    rebel = decide(
        _team("rebel"),
        observation,
        side_id="rebel",
        fleet_id="TF-REBEL-P17",
        decision_epoch=0,
        baseline_identity=_identity(),
    )
    assert loyalist["orders"]["strategic_posture"] == "POSITIONAL_MANEUVER"
    assert rebel["orders"]["strategic_posture"] == "PRESS"
    loyal_scores = {
        key: value["score"]
        for key, value in loyalist["strategic"]["scores"].items()
    }
    rebel_scores = {
        key: value["score"]
        for key, value in rebel["strategic"]["scores"].items()
    }
    assert loyal_scores != rebel_scores
    assert (
        loyalist["command_team_numeric_sha256"]
        != rebel["command_team_numeric_sha256"]
    )
    assert loyalist["prose_inputs_used"] is False
    assert rebel["prose_inputs_used"] is False


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        normalize_observation({"unknown_signal": 500})
    with pytest.raises(TypeError):
        normalize_observation({"contact_quality": 0.5})
    duplicate = _team("loyalist") + [copy.deepcopy(_team("loyalist")[0])]
    with pytest.raises(ValueError):
        normalize_command_team(duplicate)
