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
from .lin import Lin, get_lin
from .vu import Vu, get_vu
from .sato import Sato, get_sato
from .vell import Vell, get_vell
from .porter import Porter, get_porter
from .tanaka_j import TanakaJ, get_tanaka_j
from .feldman import Feldman, get_feldman
from .patel import Patel, get_patel
from .sorensen import Sorensen, get_sorensen
from .vasquez import Vasquez, get_vasquez
from .martinez import Martinez, get_martinez
from .patel_ryan import PatelRyan, get_patel_ryan
from .okada import Okada, get_okada
from .zhao import Zhao, get_zhao
from .menon import Menon, get_menon
from .kale import Kale, get_kale
from .rivas import Rivas, get_rivas
from .koss import Koss, get_koss
from .kyros import Kyros, get_kyros
from .drev import Drev, get_drev
from .park import Park, get_park
from .suresh import Suresh, get_suresh
from .halden import Halden, get_halden
from .vatra import Vatra, get_vatra

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
    'Lin',
    'Vu',
    'Sato',
    'Vell',
    'Porter',
    'TanakaJ',
    'Feldman',
    'Patel',
    'Sorensen',
    'Vasquez',
    'Martinez',
    'PatelRyan',
    'Okada',
    'Zhao',
    'Menon',
    'Kale',
    'Rivas',
    'Koss',
    'Kyros',
    'Drev',
    'Park',
    'Suresh',
    'Halden',
    'Vatra',
    'get_thorne',
    'get_markov',
    'get_roberts',
    'get_qin',
    'get_chen',
    'get_noor',
    'get_velin',
    'get_shepard',
    'get_lin',
    'get_vu',
    'get_sato',
    'get_vell',
    'get_porter',
    'get_tanaka_j',
    'get_feldman',
    'get_patel',
    'get_sorensen',
    'get_vasquez',
    'get_martinez',
    'get_patel_ryan',
    'get_okada',
    'get_zhao',
    'get_menon',
    'get_kale',
    'get_rivas',
    'get_koss',
    'get_kyros',
    'get_drev',
    'get_park',
    'get_suresh',
    'get_halden',
    'get_vatra',
]
