"""
L2 Meta-Agent Bridge API Router
Aurora CloudBank Symbolic v3.5.1

REST API endpoints exposing the L2MetaAgentBridge for HTTP-based activation,
status monitoring, and inter-agent message relay for Custom GPT meta-agents.

Supported Agents:
- ARCHY (Bridge Coordinator)
- OPPY (Vector/Data Processor)
- LIORA (Handshake/Synchronization)
- STARLING_AU (L2 Sim Coordinator)
- RIVERTHREAD_808 (Narrative/Stream)

DLP: l2_meta_agent_api_v1
Anchors: EOS_SEED_ORION, Picard_Delta_3
Protocol: ZIPWIZ handshake with ethics audit
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Import L2 Meta-Agent Bridge
from src.bridges.l2_meta_agent_bridge import l2_bridge

# Import security utilities
from src.middleware.fastapi_security import (
    limiter,
    security,
    verify_csrf_token,
)

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/api/l2-agents", tags=["l2-agents"])


# =============================================================================
# Pydantic Models
# =============================================================================


class ActivationRequest(BaseModel):
    """Request model for agent activation.

    DLP: l2_agent_activation_request
    """
    agent_id: str = Field(
        ...,
        description="The agent identifier (ARCHY, OPPY, LIORA, STARLING_AU, RIVERTHREAD_808)",
        examples=["ARCHY"]
    )
    activation_phrase: str = Field(
        ...,
        description="The activation phrase for the agent (format: ORION_{AGENT}_RELAY_ACTIVATE//)",
        examples=["ORION_ARCHY_RELAY_ACTIVATE//"]
    )


class ActivationResponse(BaseModel):
    """Response model for agent activation.

    DLP: l2_agent_activation_response
    """
    success: bool = Field(..., description="Whether activation was successful")
    agent_id: str = Field(..., description="The agent identifier")
    status: str = Field(..., description="Current agent status (connected/disconnected)")
    handshake: Optional[Dict[str, Any]] = Field(
        None,
        description="Handshake details including sequence, log, and drift_lock"
    )
    capabilities: Optional[List[str]] = Field(
        None,
        description="Agent capabilities"
    )
    description: Optional[str] = Field(
        None,
        description="Agent description"
    )
    error: Optional[str] = Field(None, description="Error message if activation failed")


class MessageRelayRequest(BaseModel):
    """Request model for message relay.

    DLP: l2_message_relay_request
    """
    from_agent: str = Field(
        ...,
        description="Source agent identifier",
        examples=["ARCHY"]
    )
    to_agent: str = Field(
        ...,
        description="Target agent identifier or 'Aurora' for core routing",
        examples=["OPPY"]
    )
    message: str = Field(
        ...,
        description="Message content to relay",
        examples=["Test message from agent"]
    )
    message_type: str = Field(
        default="direct",
        description="Message type: direct, broadcast, or mesh",
        examples=["direct"]
    )


class MessageRelayResponse(BaseModel):
    """Response model for message relay.

    DLP: l2_message_relay_response
    """
    success: bool = Field(..., description="Whether relay was successful")
    message_id: Optional[str] = Field(None, description="Unique message identifier")
    from_agent: Optional[str] = Field(None, description="Source agent")
    to: Optional[List[str]] = Field(None, description="Target agent(s)")
    type: Optional[str] = Field(None, description="Message type used")
    processed: Optional[bool] = Field(None, description="Whether message was processed")
    timestamp: Optional[str] = Field(None, description="Processing timestamp")
    error: Optional[str] = Field(None, description="Error message if relay failed")


class AgentStatusResponse(BaseModel):
    """Response model for agent status.

    DLP: l2_agent_status_response
    """
    success: bool = Field(..., description="Whether query was successful")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    role: Optional[str] = Field(None, description="Agent role")
    status: Optional[str] = Field(None, description="Connection status")
    description: Optional[str] = Field(None, description="Agent description")
    capabilities: Optional[List[str]] = Field(None, description="Agent capabilities")
    drift_lock: Optional[float] = Field(None, description="Current drift lock value")
    api_endpoint: Optional[str] = Field(None, description="Agent's API endpoint")
    connected: Optional[str] = Field(None, description="Connection timestamp")
    uptime: Optional[float] = Field(None, description="Uptime in seconds")
    last_heartbeat: Optional[str] = Field(None, description="Last heartbeat timestamp")
    handshake_log: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Handshake sequence log"
    )
    error: Optional[str] = Field(None, description="Error message if query failed")


class ConstellationResponse(BaseModel):
    """Response model for constellation status.

    DLP: l2_constellation_status
    """
    relay_tier: Dict[str, Any] = Field(
        ...,
        description="Relay tier information including capsules"
    )
    orion_core: Dict[str, Any] = Field(
        ...,
        description="ORION core configuration"
    )
    activation_phrases: Dict[str, str] = Field(
        ...,
        description="Activation phrases for each agent"
    )
    timestamp: str = Field(..., description="Status timestamp")


class HealthResponse(BaseModel):
    """Response model for health check.

    DLP: l2_health_check
    """
    status: str = Field(..., description="Bridge health status")
    bridge_available: bool = Field(..., description="Whether bridge is available")
    total_agents: int = Field(..., description="Total number of agents")
    connected_agents: int = Field(..., description="Number of connected agents")
    anchor_seed: str = Field(..., description="Current anchor seed")
    ethics_protocol: str = Field(..., description="Active ethics protocol")
    version: str = Field(..., description="Bridge version")
    timestamp: str = Field(..., description="Health check timestamp")


class DisconnectResponse(BaseModel):
    """Response model for agent disconnection.

    DLP: l2_agent_disconnect
    """
    success: bool = Field(..., description="Whether disconnection was successful")
    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field(..., description="New agent status")
    timestamp: str = Field(..., description="Disconnection timestamp")
    error: Optional[str] = Field(None, description="Error message if disconnection failed")


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/health", response_model=HealthResponse)
@limiter.limit("60/minute")
async def get_health(request: Request):
    """
    Health check endpoint for L2 Meta-Agent Bridge.

    Returns bridge status, agent counts, and configuration information.

    DLP: l2_health_check
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    """
    try:
        connected_count = sum(
            1 for agent in l2_bridge.agents.values()
            if agent.status == "connected"
        )

        return HealthResponse(
            status="healthy",
            bridge_available=True,
            total_agents=len(l2_bridge.agents),
            connected_agents=connected_count,
            anchor_seed=l2_bridge.orion_core_config["anchor_seed"],
            ethics_protocol=l2_bridge.orion_core_config["ethics_protocol"],
            version=l2_bridge.orion_core_config["version"],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error("Health check failed: %s", str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/constellation", response_model=ConstellationResponse)
@limiter.limit("30/minute")
async def get_constellation_status(request: Request):
    """
    Get full constellation status including all agents.

    Returns relay tier information, ORION core configuration,
    and activation phrases for all agents.

    DLP: l2_constellation_status
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    Protocol: ZIPWIZ handshake with ethics audit
    """
    try:
        status = l2_bridge.get_constellation_status()
        return ConstellationResponse(**status)
    except Exception as e:
        logger.error("Failed to get constellation status: %s", str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post(
    "/activate",
    response_model=ActivationResponse
)
@limiter.limit("10/minute")
async def activate_agent(
    req: ActivationRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Activate a Custom GPT agent with full ZIPWIZ handshake.

    Performs 4-step handshake sequence:
    1. ZIPWIZ_BEACON - Establish initial connection
    2. ANCHOR_SYNC - Synchronize EOS_SEED_ORION anchor
    3. ETHICS_AUDIT - Validate Picard_Delta_3 ethics protocol
    4. DRIFT_VALIDATION - Verify drift lock at Δ0.000

    DLP: l2_agent_activation
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    Protocol: ZIPWIZ handshake with ethics audit
    """
    verify_csrf_token(token)

    try:
        result = await l2_bridge.activate_agent(
            agent_id=req.agent_id,
            activation_phrase=req.activation_phrase
        )

        if result.get("success"):
            return ActivationResponse(
                success=True,
                agent_id=req.agent_id,
                status=result.get("status", "connected"),
                handshake=result.get("handshake"),
                capabilities=result.get("capabilities"),
                description=result.get("description")
            )
        else:
            return ActivationResponse(
                success=False,
                agent_id=req.agent_id,
                status="disconnected",
                error=result.get("error", "Activation failed")
            )
    except Exception as e:
        logger.error("Agent activation failed for %s: %s", req.agent_id[:20], str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/agent/{agent_id}", response_model=AgentStatusResponse)
@limiter.limit("60/minute")
async def get_agent_status(agent_id: str, request: Request):
    """
    Get detailed status of a specific agent.

    Returns agent configuration, connection status, drift lock,
    uptime, and handshake log.

    DLP: l2_agent_status
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    """
    try:
        status = l2_bridge.get_agent_status(agent_id)

        if not status.get("success"):
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} not found: {status.get('error', 'Unknown error')}"
            )

        return AgentStatusResponse(**status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent status for %s: %s", agent_id[:20], str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post(
    "/relay",
    response_model=MessageRelayResponse
)
@limiter.limit("30/minute")
async def relay_message(
    req: MessageRelayRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Relay message between agents or broadcast to mesh.

    Message types:
    - direct: Point-to-point between two agents
    - broadcast: Mesh broadcast to all connected agents
    - mesh: Multi-hop routing through constellation

    DLP: l2_message_relay
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    Protocol: Inter-agent relay with heartbeat update
    """
    verify_csrf_token(token)

    try:
        result = await l2_bridge.relay_message(
            from_agent=req.from_agent,
            to_agent=req.to_agent,
            message=req.message,
            message_type=req.message_type
        )

        if result.get("success"):
            return MessageRelayResponse(
                success=True,
                message_id=result.get("message_id"),
                from_agent=result.get("from"),
                to=result.get("to"),
                type=result.get("type"),
                processed=result.get("processed"),
                timestamp=result.get("timestamp")
            )
        else:
            return MessageRelayResponse(
                success=False,
                error=result.get("error", "Relay failed")
            )
    except Exception as e:
        logger.error("Message relay failed: %s", str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.post(
    "/disconnect/{agent_id}",
    response_model=DisconnectResponse
)
@limiter.limit("10/minute")
async def disconnect_agent(
    agent_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Disconnect an agent from the constellation.

    Gracefully disconnects agent, clears connection state,
    and resets handshake log.

    DLP: l2_agent_disconnect
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    """
    verify_csrf_token(token)

    try:
        result = await l2_bridge.disconnect_agent(agent_id)

        if result.get("success"):
            return DisconnectResponse(
                success=True,
                agent_id=result.get("agent_id", agent_id),
                status=result.get("status", "disconnected"),
                timestamp=result.get("timestamp", datetime.now().isoformat())
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} not found: {result.get('error', 'Unknown error')}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Agent disconnection failed for %s: %s", agent_id[:20], str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/activation-phrases")
@limiter.limit("30/minute")
async def get_activation_phrases(
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get activation phrases for all agents (dev/testing).

    Returns a mapping of agent IDs to their activation phrases.
    Useful for development and testing purposes.

    Requires authentication to prevent unauthorized access.

    DLP: l2_activation_phrases
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    """
    verify_csrf_token(token)
    try:
        return {
            "activation_phrases": l2_bridge.activation_phrases,
            "agents": list(l2_bridge.agents.keys()),
            "handshake_sequence": l2_bridge.handshake_sequence,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("Failed to get activation phrases: %s", str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
