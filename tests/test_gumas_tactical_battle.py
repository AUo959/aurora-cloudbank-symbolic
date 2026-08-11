from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE = (
    REPO_ROOT
    / "simulation"
    / "baselines"
    / "gumas"
    / "GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.0__2026-08-11.json"
)
RESOLVER = REPO_ROOT / "simulation" / "gumas" / "tactical_battle.py"


def _load_resolver():
    spec = importlib.util.spec_from_file_location("gumas_tactical_battle", RESOLVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_baseline_is_materially_symmetric() -> None:
    module = _load_resolver()
    baseline, digest = module.load_baseline(BASELINE)
    battle = module.TacticalBattle(baseline, digest)

    assert len(battle.ships["loyalist"]) == 19
    assert len(battle.ships["rebel"]) == 19
    assert battle.initial_power["loyalist"] == battle.initial_power["rebel"] == 89.7
    assert baseline["conflict"]["reinforcements"] is False
    assert baseline["conflict"]["third_party_intervention"] is False


def test_initial_geometry_is_occulted_by_planetoid() -> None:
    module = _load_resolver()
    baseline, digest = module.load_baseline(BASELINE)
    battle = module.TacticalBattle(baseline, digest)

    assert battle._los_blocked() is True


def test_same_baseline_and_seed_replay_identically() -> None:
    module = _load_resolver()

    first = module.run_baseline(BASELINE)
    second = module.run_baseline(BASELINE)

    assert first == second
    assert first["final_state_sha256"] == second["final_state_sha256"]
    assert first["historical_canon_status"] == "non_canon_simulation_instance"


def test_baseline_resolves_without_forced_annihilation() -> None:
    module = _load_resolver()
    result = module.run_baseline(BASELINE)

    assert result["termination"] in {
        "mutual_ceasefire",
        "withdrawal",
        "surrender",
        "mutual_disengagement",
        "combat_incapacity",
        "hard_time_limit",
        "formation_collision",
    }
    assert result["elapsed_s"] <= 21600
    assert len(result["sides"]["loyalist"]["ships"]) == 19
    assert len(result["sides"]["rebel"]["ships"]) == 19
    assert not any(event.get("type") == "reinforcement" for event in result["events"])


def test_disabled_or_surrendered_targets_are_excluded() -> None:
    module = _load_resolver()
    baseline, digest = module.load_baseline(BASELINE)
    battle = module.TacticalBattle(baseline, digest)

    target = battle.ships["rebel"][0]
    target.status = "mission_kill"
    candidates, _ = battle._target_candidates("rebel")
    assert target not in candidates

    target.status = "undamaged"
    target.surrendered = True
    candidates, _ = battle._target_candidates("rebel")
    assert target not in candidates
