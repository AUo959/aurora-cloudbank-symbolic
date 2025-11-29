"""
Aurora CloudBank Symbolic - Crew Agents Module
Chain Notation: #CREW//AGENTS//INIT//
DLP Tag: crew_agents_init_v1

This module exports the crew agent system including base classes,
registration functions, and all individual crew member agents.
"""

from src.agents.crew.base_agent import (
    AgentRole,
    ClearanceLevel,
    CrewAgentCapability,
    CollaborationRecord,
    AgentTask,
    BaseCrewAgent,
    register_crew_agent,
    get_crew_agent,
    get_all_crew_agents,
    get_agents_by_role,
    get_agents_by_division,
)

# Import individual agent getter functions
from src.agents.crew.chen import get_chen
from src.agents.crew.drev import get_drev
from src.agents.crew.el_sayegh import get_el_sayegh
from src.agents.crew.feldman import get_feldman
from src.agents.crew.halden import get_halden
from src.agents.crew.kale import get_kale
from src.agents.crew.koss import get_koss
from src.agents.crew.kyros import get_kyros
from src.agents.crew.lee import get_lee
from src.agents.crew.lin import get_lin
from src.agents.crew.markov import get_markov
from src.agents.crew.martinez import get_martinez
from src.agents.crew.menon import get_menon
from src.agents.crew.nguyen import get_nguyen
from src.agents.crew.noor import get_noor
from src.agents.crew.okada import get_okada
from src.agents.crew.park import get_park
from src.agents.crew.patel import get_patel
from src.agents.crew.patel_ryan import get_patel_ryan
from src.agents.crew.porter import get_porter
from src.agents.crew.qin import get_qin
from src.agents.crew.rivas import get_rivas
from src.agents.crew.roberts import get_roberts
from src.agents.crew.sato import get_sato
from src.agents.crew.shepard import get_shepard
from src.agents.crew.sorensen import get_sorensen
from src.agents.crew.suresh import get_suresh
from src.agents.crew.tanaka_j import get_tanaka_j
from src.agents.crew.thorne import get_thorne
from src.agents.crew.vasquez import get_vasquez
from src.agents.crew.vatra import get_vatra
from src.agents.crew.velin import get_velin
from src.agents.crew.vell import get_vell
from src.agents.crew.vu import get_vu
from src.agents.crew.zhao import get_zhao

__all__ = [
    # Enums
    "AgentRole",
    "ClearanceLevel",
    # Data Classes
    "CrewAgentCapability",
    "CollaborationRecord",
    "AgentTask",
    # Base Class
    "BaseCrewAgent",
    # Registry Functions
    "register_crew_agent",
    "get_crew_agent",
    "get_all_crew_agents",
    "get_agents_by_role",
    "get_agents_by_division",
    # Individual Agent Getters
    "get_chen",
    "get_drev",
    "get_el_sayegh",
    "get_feldman",
    "get_halden",
    "get_kale",
    "get_koss",
    "get_kyros",
    "get_lee",
    "get_lin",
    "get_markov",
    "get_martinez",
    "get_menon",
    "get_nguyen",
    "get_noor",
    "get_okada",
    "get_park",
    "get_patel",
    "get_patel_ryan",
    "get_porter",
    "get_qin",
    "get_rivas",
    "get_roberts",
    "get_sato",
    "get_shepard",
    "get_sorensen",
    "get_suresh",
    "get_tanaka_j",
    "get_thorne",
    "get_vasquez",
    "get_vatra",
    "get_velin",
    "get_vell",
    "get_vu",
    "get_zhao",
]
