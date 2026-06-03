"""
Crew Agents API
Aurora CloudBank Symbolic

FastAPI router for Orion Station crew member agents.

Provides REST endpoints for:
- Querying crew agent status and capabilities
- Dispatching tasks to specialized agents
- Coordinating multi-agent collaborations
- Monitoring agent activities

API Routes:
- GET /api/crew/{agent_surname}/status - Get agent status
- GET /api/crew/{agent_surname}/capabilities - Get agent capabilities
- POST /api/crew/{agent_surname}/process - Process task with agent
- POST /api/crew/collaborate - Coordinate multi-agent collaboration
- GET /api/crew/all - Get all crew agents
- GET /api/crew/role/{role} - Get agents by role
- GET /api/crew/division/{division} - Get agents by division
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from src.agents.crew import (
    get_crew_agent,
    get_all_crew_agents,
    get_agents_by_role,
    get_agents_by_division,
    AgentRole,
    get_thorne,
    get_markov,
    get_roberts,
    get_qin,
    get_chen,
    get_noor,
    get_velin,
    get_shepard,
    get_lin,
    get_vu,
    get_sato,
    get_vell,
    get_porter,
    get_tanaka_j,
    get_feldman,
    get_patel,
    get_sorensen,
    get_vasquez,
    get_martinez,
    get_patel_ryan,
    get_okada,
    get_zhao,
    get_menon,
    get_kale,
    get_rivas,
    get_koss,
    get_kyros,
    get_drev,
    get_park,
    get_suresh,
    get_halden,
    get_vatra,
    get_nguyen,
    get_lee,
    get_el_sayegh,
    get_kim,
    get_okafor,
    get_santos,
)

router = APIRouter(prefix="/api/crew", tags=["Crew Agents"])

# Initialize crew agents at module import
get_thorne()
get_markov()
get_roberts()
get_qin()
get_chen()
get_noor()
get_velin()
get_shepard()
get_lin()
get_vu()
get_sato()
get_vell()
get_porter()
get_tanaka_j()
get_feldman()
get_patel()
get_sorensen()
get_vasquez()
get_martinez()
get_patel_ryan()
get_okada()
get_zhao()
get_menon()
get_kale()
get_rivas()
get_koss()
get_kyros()
get_drev()
get_park()
get_suresh()
get_halden()
get_vatra()
get_nguyen()
get_lee()
get_el_sayegh()
get_kim()
get_okafor()
get_santos()


# Pydantic models for requests/responses

class AgentTaskRequest(BaseModel):
    """Request model for agent task processing"""
    task_type: str = Field(..., description="Type of task to execute")
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context and parameters")
    priority: str = Field(default="medium", description="Task priority (low/medium/high/critical)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_type": "strategic_planning",
                "context": {
                    "objectives": ["system_optimization", "crew_coordination"],
                    "timeline": "90_days"
                },
                "priority": "high"
            }
        }
    )


class CollaborationRequest(BaseModel):
    """Request model for multi-agent collaboration"""
    agents: List[str] = Field(..., description="List of agent surnames to collaborate")
    task: AgentTaskRequest = Field(..., description="Collaborative task definition")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "agents": ["thorne", "markov"],
                "task": {
                    "task_type": "security_review",
                    "context": {"scope": "station_wide"},
                    "priority": "high"
                }
            }
        }
    )


class AgentStatusResponse(BaseModel):
    """Response model for agent status"""
    agent_id: str
    surname: str
    full_name: str
    role: str
    clearance: str
    division: str
    location: str
    status: str
    specializations: List[str]
    capabilities_count: int
    active_tasks: int
    collaboration_history_count: int
    statistics: Dict[str, Any]
    relay_liaison: str | None
    glyph_liaison: str | None
    symbolic_tag: str
    model: str
    uptime_hours: float


# API Endpoints

@router.get("/{agent_surname}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_surname: str) -> Dict[str, Any]:
    """
    Get comprehensive status for a crew agent.

    Args:
        agent_surname: Agent surname (e.g., "thorne", "markov")

    Returns:
        Complete agent status including capabilities, statistics, and state

    Examples:
        GET /api/crew/thorne/status
        GET /api/crew/markov/status
    """
    agent = get_crew_agent(agent_surname.lower())

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Crew agent not found: {agent_surname}"
        )

    return agent.get_status()


@router.get("/{agent_surname}/capabilities")
async def get_agent_capabilities(agent_surname: str) -> Dict[str, Any]:
    """
    Get agent's capabilities and tools.

    Args:
        agent_surname: Agent surname

    Returns:
        List of capabilities with descriptions and endpoints
    """
    agent = get_crew_agent(agent_surname.lower())

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Crew agent not found: {agent_surname}"
        )

    return {
        'agent_id': agent.agent_id,
        'surname': agent.surname,
        'full_name': agent.full_name,
        'role': agent.role.value,
        'capabilities': agent.get_capabilities()
    }


@router.post("/{agent_surname}/process")
async def process_agent_task(
    agent_surname: str,
    request: AgentTaskRequest
) -> Dict[str, Any]:
    """
    Process a task with a specific crew agent.

    Args:
        agent_surname: Agent surname
        request: Task request with type, context, and priority

    Returns:
        Task processing result

    Examples:
        POST /api/crew/thorne/process
        {
            "task_type": "strategic_planning",
            "context": {"objectives": ["optimization"]},
            "priority": "high"
        }

        POST /api/crew/markov/process
        {
            "task_type": "security_audit",
            "context": {"scope": "full_station"},
            "priority": "medium"
        }
    """
    agent = get_crew_agent(agent_surname.lower())

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Crew agent not found: {agent_surname}"
        )

    try:
        result = await agent.process_request({
            'task_type': request.task_type,
            'context': request.context,
            'priority': request.priority
        })

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Internal server error"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post("/collaborate")
async def coordinate_collaboration(request: CollaborationRequest) -> Dict[str, Any]:
    """
    Coordinate multi-agent collaboration on a task.

    Args:
        request: Collaboration request with agent list and task

    Returns:
        Collaboration result from all agents

    Example:
        POST /api/crew/collaborate
        {
            "agents": ["thorne", "markov", "roberts"],
            "task": {
                "task_type": "system_security_review",
                "context": {"scope": "authentication_layer"},
                "priority": "high"
            }
        }
    """
    if len(request.agents) < 2:
        raise HTTPException(
            status_code=400,
            detail="Collaboration requires at least 2 agents"
        )

    # Get all agents
    agents = []
    for surname in request.agents:
        agent = get_crew_agent(surname.lower())
        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Crew agent not found: {surname}"
            )
        agents.append(agent)

    # Primary agent initiates collaboration
    primary_agent = agents[0]
    collaborators = agents[1:]

    try:
        results = []

        # Primary agent collaborates with each other agent
        for collaborator in collaborators:
            collab_result = await primary_agent.collaborate_with(
                collaborator,
                {
                    'task_type': request.task.task_type,
                    'context': request.task.context,
                    'priority': request.task.priority
                }
            )
            results.append(collab_result)

        return {
            'success': True,
            'collaboration_count': len(results),
            'primary_agent': primary_agent.surname,
            'collaborators': [c.surname for c in collaborators],
            'results': results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/all")
async def get_all_agents() -> Dict[str, Any]:
    """
    Get all registered crew agents.

    Returns:
        Dictionary of all crew agents with basic information
    """
    all_agents = get_all_crew_agents()

    return {
        'total_agents': len(all_agents),
        'agents': {
            surname: {
                'agent_id': agent.agent_id,
                'surname': agent.surname,
                'full_name': agent.full_name,
                'role': agent.role.value,
                'division': agent.division,
                'location': agent.location,
                'status': agent.status
            }
            for surname, agent in all_agents.items()
        }
    }


@router.get("/role/{role}")
async def get_agents_by_role_endpoint(role: str) -> Dict[str, Any]:
    """
    Get all agents with a specific role.

    Args:
        role: Agent role (command, security, systems, simulation, etc.)

    Returns:
        List of agents with specified role
    """
    try:
        agent_role = AgentRole(role.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {role}. Valid roles: {[r.value for r in AgentRole]}"
        )

    agents = get_agents_by_role(agent_role)

    return {
        'role': role,
        'agent_count': len(agents),
        'agents': [
            {
                'agent_id': agent.agent_id,
                'surname': agent.surname,
                'full_name': agent.full_name,
                'division': agent.division,
                'location': agent.location
            }
            for agent in agents
        ]
    }


@router.get("/division/{division}")
async def get_agents_by_division_endpoint(division: str) -> Dict[str, Any]:
    """
    Get all agents in a specific division.

    Args:
        division: Division name (e.g., "Command & Ethics", "Systems & Infrastructure")

    Returns:
        List of agents in specified division
    """
    agents = get_agents_by_division(division)

    return {
        'division': division,
        'agent_count': len(agents),
        'agents': [
            {
                'agent_id': agent.agent_id,
                'surname': agent.surname,
                'full_name': agent.full_name,
                'role': agent.role.value,
                'location': agent.location
            }
            for agent in agents
        ]
    }
