"""
L1 Relay Bridge API Router (formerly "L2 Meta-Agent Bridge API")
Aurora CloudBank Symbolic v3.5.1

REST API endpoints exposing the L1RelayBridge for HTTP-based activation,
status monitoring, and inter-agent message relay for the relay-agent
constellation.

ARCHITECTURE NOTE: the relay agents are L1-resident (Orion Station) and
play the Layer 2 verifier ROLE in the Triplex protocol — the old "L2"
naming was a canon error (docs/architecture/LAYER_ARCHITECTURE.md).

ROUTES — served at BOTH prefixes by api/aurora_api.py:
  /api/l1-relay-agents/*   canonical (use this)
  /api/l2-agents/*         deprecated legacy alias, kept for backwards
                           compatibility with existing integrations;
                           marked deprecated in OpenAPI

Supported relay agents:
- ARCHY (Bridge Coordinator)
- OPPY (Vector/Data Processor)
- LIORA (Handshake/Synchronization)
- STARLING_AU (L2 Sim Coordinator)
- RIVERTHREAD_808 (Narrative/Stream)

Supported operational system:
- HALO (station continuity system-entity; activation/status only, not message-routable)

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

# Bind the bridge to the controller already created by the application module.
# Its fallback controller remains available when this router is used standalone.
from src.aurora.continuity import get_active_halo_pas_controller

# Import the canonical L1 Relay Bridge (mesh-backed singleton)
from src.bridges.l1_relay_bridge import l1_relay_bridge as l2_bridge

# Import security utilities
from src.middleware.fastapi_security import (
    limiter,
    security,
    verify_csrf_token,
)

_process_halo_controller = get_active_halo_pas_controller()
if _process_halo_controller is not None:
    l2_bridge.halo_controller = _process_halo_controller

logger = logging.getLogger(__name__)


def _safe_log_id(value: str) -> str:
    """Escape newlines in request-supplied identifiers before logging so a
    crafted value cannot forge log lines (Sonar S5145)."""
    return value[:20].replace("\r", "\\r").replace("\n", "\\n")


# Endpoints are defined on an unprefixed base router; the canonical and
# legacy prefixed routers below both include it, so the same handlers
# serve both paths.
router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================


class ActivationRequest(BaseModel):
    """Request model for relay-agent or system activation.

    DLP: l2_agent_activation_request
    """
    agent_id: str = Field(
        ...,
        description=(
            "Relay agent or operational system identifier "
            "(ARCHY, OPPY, LIORA, STARLING_AU, RIVERTHREAD_808, HALO)"
        ),
        examples=["ARCHY", "HALO"]
    )
    activation_phrase: str = Field(
        ...,
        description="The activation phrase for the agent (format: ORION_{AGENT}_RELAY_ACTIVATE//)",
        examples=["ORION_ARCHY_RELAY_ACTIVATE//"]
    )


class ActivationResponse(BaseModel):
    """Response model for relay-agent or system activation.

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
    participant_type: Optional[str] = Field(None, description="Semantic participant type")
    message_routable: Optional[bool] = Field(None, description="Whether the participant can relay messages")
    registry_designation: Optional[str] = Field(None, description="Preserved registry designation")
    continuity: Optional[Dict[str, Any]] = Field(None, description="Continuity controller status")
    living_entity: Optional[Dict[str, Any]] = Field(None, description="Living system-entity state")
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
    """Response model for relay-agent or system-participant status.

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
    participant_type: Optional[str] = Field(None, description="Semantic participant type")
    message_routable: Optional[bool] = Field(None, description="Whether the participant can relay messages")
    registry_designation: Optional[str] = Field(None, description="Preserved registry designation")
    reality_layer: Optional[str] = Field(None, description="Physical reality layer")
    triplex_role: Optional[str] = Field(None, description="Triplex verification role")
    continuity: Optional[Dict[str, Any]] = Field(None, description="Continuity controller status")
    living_entity: Optional[Dict[str, Any]] = Field(None, description="Living system-entity state")
    error: Optional[str] = Field(None, description="Error message if query failed")


class ConstellationResponse(BaseModel):
    """Response model for constellation status.

    DLP: l2_constellation_status
    """
    relay_tier: Dict[str, Any] = Field(
        ...,
        description="Relay tier information including capsules"
    )
    system_participants: Dict[str, Any] = Field(
        ...,
        description="Operational systems kept distinct from the relay tier"
    )
    orion_core: Dict[str, Any] = Field(
        ...,
        description="ORION core configuration"
    )
    activation_phrases: Dict[str, str] = Field(
        ...,
        description="Activation phrases for relay agents"
    )
    system_activation_phrases: Dict[str, str] = Field(
        ...,
        description="Activation phrases for operational systems"
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
    total_system_participants: int = Field(..., description="Total number of operational systems")
    active_system_participants: int = Field(..., description="Number of active operational systems")
    anchor_seed: str = Field(..., description="Current anchor seed")
    ethics_protocol: str = Field(..., description="Active ethics protocol")
    version: str = Field(..., description="Bridge version")
    timestamp: str = Field(..., description="Health check timestamp")


class DisconnectResponse(BaseModel):
    """Response model for relay disconnection or system stop.

    DLP: l2_agent_disconnect
    """
    success: bool = Field(..., description="Whether disconnection was successful")
    agent_id: str = Field(..., description="Agent identifier")
    status: str = Field(..., description="New agent status")
    timestamp: str = Field(..., description="Disconnection timestamp")
    participant_type: Optional[str] = Field(None, description="Semantic participant type")
    message_routable: Optional[bool] = Field(None, description="Whether the participant can relay messages")
    error: Optional[str] = Field(None, description="Error message if disconnection failed")


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/health", response_model=HealthResponse)
@limiter.limit("60/minute")
async def get_health(request: Request):
    """
    Health check endpoint for the L1 relay and system bridge.

    Returns bridge status, agent counts, and configuration information.

    DLP: l2_health_check
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    """
    try:
        connected_count = sum(
            1 for agent in l2_bridge.agents.values()
            if agent.status == "connected"
        )
        active_system_count = sum(
            1
            for participant_id in l2_bridge.system_participants
            if l2_bridge.get_agent_status(participant_id).get("status") == "running"
        )

        return HealthResponse(
            status="healthy",
            bridge_available=True,
            total_agents=len(l2_bridge.agents),
            connected_agents=connected_count,
            total_system_participants=len(l2_bridge.system_participants),
            active_system_participants=active_system_count,
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
    Get relay constellation status plus distinct operational systems.

    Returns relay tier information, ORION core configuration,
    and activation phrases for relay agents and operational systems.

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
    Activate a relay agent or an operational system participant.

    Relay agents activate through the mesh runtime. HALO activates the
    process-wide HALO/PAS continuity controller and does not gain message
    relay behavior.

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
                description=result.get("description"),
                participant_type=result.get("participant_type"),
                message_routable=result.get("message_routable"),
                registry_designation=result.get("registry_designation"),
                continuity=result.get("continuity"),
                living_entity=result.get("living_entity"),
            )
        else:
            return ActivationResponse(
                success=False,
                agent_id=req.agent_id,
                status=(
                    "stopped"
                    if req.agent_id in l2_bridge.system_participants
                    else "disconnected"
                ),
                error=result.get("error", "Activation failed")
            )
    except Exception as e:
        logger.error("Agent activation failed for %s: %s", _safe_log_id(req.agent_id), str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/agent/{agent_id}", response_model=AgentStatusResponse)
@limiter.limit("60/minute")
async def get_agent_status(agent_id: str, request: Request):
    """
    Get detailed status of a relay agent or operational system.

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
                detail=f"Participant {agent_id} not found: {status.get('error', 'Unknown error')}"
            )

        return AgentStatusResponse(**status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent status for %s: %s", _safe_log_id(agent_id), str(e)[:100])
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
    Disconnect a relay agent or stop an operational system.

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
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                participant_type=result.get("participant_type"),
                message_routable=result.get("message_routable"),
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Participant {agent_id} not found: {result.get('error', 'Unknown error')}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Agent disconnection failed for %s: %s", _safe_log_id(agent_id), str(e)[:100])
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
    Get activation phrases for relay agents and operational systems (dev/testing).

    Returns separate mappings so HALO remains distinct from relay agents.
    Useful for development and testing purposes.

    Requires authentication to prevent unauthorized access.

    DLP: l2_activation_phrases
    Anchors: EOS_SEED_ORION, Picard_Delta_3
    """
    verify_csrf_token(token)
    try:
        return {
            "activation_phrases": l2_bridge.activation_phrases,
            "system_activation_phrases": l2_bridge.system_activation_phrases,
            "agents": list(l2_bridge.agents.keys()),
            "system_participants": list(l2_bridge.system_participants.keys()),
            "handshake_sequence": l2_bridge.handshake_sequence,
            "system_activation_sequence": l2_bridge.system_activation_sequence,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("Failed to get activation phrases: %s", str(e)[:100])
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# =============================================================================
# Canonical and legacy prefixed routers
# =============================================================================

_base_router = router

canonical_router = APIRouter(prefix="/api/l1-relay-agents", tags=["l1-relay-agents"])
canonical_router.include_router(_base_router)

# Deprecated alias: existing integrations still call /api/l2-agents/*.
# deprecated=True marks every operation as deprecated in OpenAPI without
# changing behavior. Remove only after external callers migrate.
legacy_router = APIRouter(prefix="/api/l2-agents", tags=["l2-agents"], deprecated=True)
legacy_router.include_router(_base_router)
