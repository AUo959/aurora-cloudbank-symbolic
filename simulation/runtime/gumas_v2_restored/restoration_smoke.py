#!/usr/bin/env python3
"""Focused deterministic smoke test for the GUMAS v2.0.1-restored.1 contract."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from restored_engine import GUMASEngine, RESTORATION_VERSION  # noqa: E402
from modules.gumas.models import (  # noqa: E402
    BattlefieldCondition,
    EventType,
    FleetState,
    GUMASState,
    SimulationEvent,
)


def _state(reverse: bool = False) -> GUMASState:
    fleets = [
        FleetState(
            fleet_id="fleet_a",
            faction_id="alpha",
            name="Alpha",
            strength=0.8,
            technology_modifier=1.0,
            morale=0.8,
            location_node="test_node",
            supply_level=1.0,
            experience=0.6,
        ),
        FleetState(
            fleet_id="fleet_b",
            faction_id="beta",
            name="Beta",
            strength=0.8,
            technology_modifier=1.0,
            morale=0.8,
            location_node="test_node",
            supply_level=1.0,
            experience=0.6,
        ),
    ]
    if reverse:
        fleets.reverse()
    return GUMASState(
        scenario_id="combat_restore_test",
        seed=123,
        fleets={fleet.fleet_id: fleet for fleet in fleets},
    )


def _normalize(value):
    if isinstance(value, dict):
        return {
            key: _normalize(item)
            for key, item in sorted(value.items())
            if key != "timestamp"
        }
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def _run(*, explicit: bool = False, reverse: bool = False):
    engine = GUMASEngine(seed=123)
    engine.init_scenario(_state(reverse=reverse))
    if explicit:
        engine.inject_event(
            SimulationEvent(
                event_id="battle-1",
                event_type=EventType.FLEET_BATTLE,
                turn=0,
                source_faction="alpha",
                target_faction="beta",
                parameters={
                    "location": "test_node",
                    "condition": BattlefieldCondition.CHOKEPOINT.value,
                },
                injected=True,
            )
        )
    result = engine.step()
    snapshot = _normalize(engine.export_state(include_history=True))
    return engine, result, snapshot


def main() -> None:
    engine, result, snapshot = _run()
    combat = next(iter(engine.get_state().combat_zones.values()))
    assert combat.turns_active == 1
    assert combat.condition == BattlefieldCondition.OPEN_SPACE
    assert engine.get_state().fleets["fleet_a"].strength < 0.8
    assert engine.get_state().fleets["fleet_b"].strength < 0.8
    assert sum("combat[" in str(change) for change in result.state_changes) == 1

    explicit_engine, explicit_result, _ = _run(explicit=True)
    explicit_combat = next(iter(explicit_engine.get_state().combat_zones.values()))
    assert explicit_combat.turns_active == 1
    assert explicit_combat.condition == BattlefieldCondition.CHOKEPOINT
    assert any(
        "fleet_battle_prepared" in str(change)
        for change in explicit_result.state_changes
    )
    assert sum("combat[" in str(change) for change in explicit_result.state_changes) == 1

    _, _, replay = _run()
    _, _, reverse = _run(reverse=True)
    assert snapshot == replay
    assert snapshot == reverse

    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    print(
        json.dumps(
            {
                "status": "ok",
                "restoration_version": RESTORATION_VERSION,
                "normalized_replay_sha256": digest,
                "combat_id": combat.combat_id,
                "automatic_condition": combat.condition.value,
                "explicit_condition": explicit_combat.condition.value,
                "combat_turns": combat.turns_active,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
