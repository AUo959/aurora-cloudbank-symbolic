import pytest

from src.agents.crew.noor import get_noor
from src.agents.crew.lin import get_lin


@pytest.mark.unit
def test_clearance_equality():
    noor = get_noor()
    # Noor should have its own clearance level satisfied
    assert noor.check_clearance(noor.clearance.value) is True

@pytest.mark.unit
def test_clearance_below_required():
    lin_agent = get_lin()
    # Lin (L3_RESEARCH) should satisfy another L3-level clearance requirement (security)
    assert lin_agent.check_clearance("L3_SECURITY") is True

@pytest.mark.unit
def test_clearance_above_required():
    lin_agent = get_lin()
    # Lin should NOT satisfy highest command level
    assert lin_agent.check_clearance("L5_COMMAND") is False
