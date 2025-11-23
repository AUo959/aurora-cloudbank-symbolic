import pytest

from src.agents.crew.thorne import get_thorne
from src.agents.crew.markov import get_markov


@pytest.mark.unit
def test_clearance_equality():
    thorne = get_thorne()
    # Thorne should have its own clearance level satisfied
    assert thorne.check_clearance(thorne.clearance.value) is True

@pytest.mark.unit
def test_clearance_below_required():
    markov = get_markov()
    # Markov (security) should satisfy a lower technical clearance
    assert markov.check_clearance("L3_SECURITY") is True

@pytest.mark.unit
def test_clearance_above_required():
    markov = get_markov()
    # Markov should NOT satisfy highest command level
    assert markov.check_clearance("L5_COMMAND") is False
