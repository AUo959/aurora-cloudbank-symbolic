import pytest

from src.agents.crew.base_agent import (
    get_all_crew_agents,
)

# Import agent factory/getter functions
from src.agents.crew.lin import get_lin  # noqa: E401
from src.agents.crew.noor import get_noor  # noqa: E401
from src.agents.crew.qin import get_qin  # noqa: E401
from src.agents.crew.sorensen import get_sorensen  # noqa: E401
from src.agents.crew.vasquez import get_vasquez  # noqa: E401
from src.agents.crew.lee import get_lee  # noqa: E401
from src.agents.crew.suresh import get_suresh  # noqa: E401
from src.agents.crew.koss import get_koss  # noqa: E401
from src.agents.crew.menon import get_menon  # noqa: E401
from src.agents.crew.nguyen import get_nguyen  # noqa: E401
from src.agents.crew.park import get_park  # noqa: E401
from src.agents.crew.patel import get_patel  # noqa: E401
from src.agents.crew.halden import get_halden  # noqa: E401
from src.agents.crew.kale import get_kale  # noqa: E401
from src.agents.crew.zhao import get_zhao  # noqa: E401


@pytest.mark.unit
def test_agents_registry_population():
    # Instantiate all agents through their getter to ensure registry population
    # Use currently implemented agent set (legacy agents removed in Phase 3)
    getters = [
        get_lin,
        get_noor,
        get_qin,
        get_sorensen,
        get_vasquez,
        get_lee,
        get_suresh,
        get_koss,
        get_menon,
        get_nguyen,
        get_park,
        get_patel,
        get_halden,
        get_kale,
        get_zhao,
    ]

    for getter in getters:
        agent = getter()
        assert agent is not None
        assert hasattr(agent, "surname")
        assert hasattr(agent, "capabilities")

    registry = get_all_crew_agents()
    # Expect at least these 15 specialized agents populated
    assert len(registry) >= 15
    # Ensure unique surnames keys
    assert len({a.surname for a in registry.values()}) == len(registry)
