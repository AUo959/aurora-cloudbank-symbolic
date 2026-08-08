import sys
from pathlib import Path

import pytest

SIMULATION_DIR = Path(__file__).resolve().parent.parent / "simulation"
SIMULATION_PATH = str(SIMULATION_DIR)
if SIMULATION_PATH not in sys.path:
    sys.path.insert(0, SIMULATION_PATH)

from orion_station_simulation_v2 import Agent, OrionSimulationV2  # noqa: E402


@pytest.mark.unit
def test_fatigue_never_scores_benchmark_work_speed():
    agent = Agent(
        name="Benchmark Agent",
        role="Regression fixture",
        character_id="TEST_001",
        base_speed=1.5,
        collaboration_bonus=0.2,
        fatigue=100.0,
    )

    assert agent.effective_speed() == pytest.approx(1.5)
    assert agent.effective_speed(is_collaborative_context=True) == pytest.approx(1.8)


@pytest.mark.unit
def test_phase1_completes_deterministic():
    sim = OrionSimulationV2(seed=1337, enable_emergent=False)
    result = sim.run(max_ticks=20)

    assert result["completed"] is True
    assert set(result["completed_ids"]) == {"T1", "T2", "T3", "T4"}
    assert result["ticks"] <= 20
    assert result["version"] == "2.0_l1_canon"


@pytest.mark.unit
def test_transcript_contains_canonical_kickoff_message():
    sim = OrionSimulationV2(seed=1337, enable_emergent=False)
    result = sim.run(max_ticks=5)

    transcript = result["transcript"]
    assert transcript, "Transcript should not be empty"
    assert any("Alex Thorne" in line for line in transcript)


@pytest.mark.unit
@pytest.mark.simulation
def test_first_tick_emergence_is_possible():
    """Working-agent emergence must remain possible on tick zero."""
    working_kinds = {"swarm_sync", "collaboration_boost", "cross_pollination"}
    for seed in range(30):
        sim = OrionSimulationV2(seed=seed, enable_emergent=True)
        sim.run(max_ticks=1)
        if any(e.tick == 0 and e.kind in working_kinds for e in sim.aurora.events):
            return
    raise AssertionError(
        "no working-agent emergence on tick 0 across 30 seeds — "
        "events are likely emitted before assignments again"
    )
