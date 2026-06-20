import pytest

from simulation.orion_station_simulation import OrionSimulation


@pytest.mark.unit
def test_phase1_completes_deterministic():
    sim = OrionSimulation(seed=1337, enable_emergent=False)
    result = sim.run(max_ticks=20)

    assert result["completed"] is True
    assert set(result["completed_ids"]) == {"T1", "T2", "T3", "T4"}
    assert result["ticks"] <= 20


@pytest.mark.unit
def test_transcript_contains_kickoff_message():
    sim = OrionSimulation(seed=1337, enable_emergent=False)
    result = sim.run(max_ticks=5)

    transcript = result["transcript"]
    assert transcript, "Transcript should not be empty"
    # First tick should include Alex Thorn kickoff note
    assert any("Alex Thorn" in line for line in transcript)


@pytest.mark.unit
@pytest.mark.simulation
def test_first_tick_emergence_is_possible():
    """Regression: events were emitted before assignment, so working-agent
    emergence (swarm_sync, collaboration_boost, cross_pollination) could
    never fire on the first tick of any run."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "simulation"))
    from orion_station_simulation_v2 import OrionSimulationV2

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
