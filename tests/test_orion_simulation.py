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
