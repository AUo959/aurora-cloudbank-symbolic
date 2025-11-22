"""
Crew Agent Module
Aurora CloudBank Symbolic

Provides specialized agent implementations for all Orion Station crew members.

Each crew member is represented as an agent with:
- Unique capabilities based on their role
- Domain-specific expertise and tools
- Collaboration protocols with other crew and relay agents
- Integration with station systems

Agent Naming: Uses surnames (Thorne, Markov, Roberts, etc.)
"""

from .base_agent import (
    BaseCrewAgent,
    AgentRole,
    ClearanceLevel,
    CrewAgentCapability,
    CollaborationRecord,
    AgentTask,
    register_crew_agent,
    get_crew_agent,
    get_all_crew_agents,
    get_agents_by_role,
    get_agents_by_division,
)

# Import crew agents
from .thorne import Thorne, get_thorne
from .markov import Markov, get_markov
from .roberts import Roberts, get_roberts
from .qin import Qin, get_qin
from .chen import Chen, get_chen
from .noor import Noor, get_noor
from .velin import Velin, get_velin
from .shepard import Shepard, get_shepard

__all__ = [
    'BaseCrewAgent',
    'AgentRole',
    'ClearanceLevel',
    'CrewAgentCapability',
    'CollaborationRecord',
    'AgentTask',
    'register_crew_agent',
    'get_crew_agent',
    'get_all_crew_agents',
    'get_agents_by_role',
    'get_agents_by_division',
    # Crew agents
    'Thorne',
    'Markov',
    'Roberts',
    'Qin',
    'Chen',
    'Noor',
    'Velin',
    'Shepard',
    'get_thorne',
    'get_markov',
    'get_roberts',
    'get_qin',
    'get_chen',
    'get_noor',
    'get_velin',
    'get_shepard',
]
