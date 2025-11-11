"""
main FastAPI app for Aurora CloudBank Symbolic

Exposes endpoints for quantum and geometric algebra modules.

Enhanced with Claude Sonnet 4 capabilities and ChatGPT Agent Mode integration.
"""

from typing import Any, Dict, Optional

import logging
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from src.middleware.exception_handler import validation_handler
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.sonnet4_integration_hub import enable_sonnet4_globally, sonnet4_hub

# Import ChatGPT Agent Mode integration
from src.integrations.chatgpt_agent_mode import chatgpt_agent_integration

# Import Gemini Agent Mode integration
try:
    from src.integrations.gemini_agent_integration import gemini_agent_integration
    GEMINI_AGENT_AVAILABLE = True
except ImportError:
    logging.getLogger("aurora_api").warning("Gemini Agent not available - Gemini features disabled")
    GEMINI_AGENT_AVAILABLE = False

# Import centralized security configuration
from src.middleware.fastapi_security import (
    limiter,
    security,
    verify_csrf_token,
    verify_ws_token,
    validate_ws_tool,
    sanitize_request_id,
    sanitize_session_id
)

# Import AuMemManager API integration
try:
    from modules.aumemmanager.api_integration import router as aumemmanager_router
    AUMEMMANAGER_AVAILABLE = True
    AUMEMMANAGER_ROUTER = aumemmanager_router
except ImportError:
    logging.getLogger("aurora_api").warning("AuMemManager not available - some memory features disabled")
    AUMEMMANAGER_AVAILABLE = False
    AUMEMMANAGER_ROUTER = None

# Import Data Guardian API integration
try:
    from modules.data_guardian.api import router as data_guardian_router
    DATA_GUARDIAN_AVAILABLE = True
    DATA_GUARDIAN_ROUTER = data_guardian_router
except ImportError:
    logging.getLogger("aurora_api").warning("Data Guardian not available - PII detection/redaction features disabled")
    DATA_GUARDIAN_AVAILABLE = False
    DATA_GUARDIAN_ROUTER = None

# Import Insight Ledger API integration
try:
    from modules.insight_ledger.api import initialize_ledger
    from modules.insight_ledger.api import router as insight_ledger_router
    INSIGHT_LEDGER_AVAILABLE = True
    INSIGHT_LEDGER_ROUTER = insight_ledger_router
except ImportError:
    logging.getLogger("aurora_api").warning("Insight Ledger not available - audit trail features disabled")
    INSIGHT_LEDGER_AVAILABLE = False
    INSIGHT_LEDGER_ROUTER = None
    initialize_ledger = None

# Import Quantum Simulator API integration
try:
    from modules.quantum_simulator.api import router as quantum_simulator_router
    QUANTUM_SIMULATOR_AVAILABLE = True
    QUANTUM_SIMULATOR_ROUTER = quantum_simulator_router
except ImportError:
    logging.getLogger("aurora_api").warning("Quantum Simulator not available - quantum simulation features disabled")
    QUANTUM_SIMULATOR_AVAILABLE = False
    QUANTUM_SIMULATOR_ROUTER = None

# Import Thread Transfer Bridge integration
try:
    from modules.reflective_autonomy.thread_transfer import (
        get_bridge_instance
    )
    THREAD_BRIDGE_AVAILABLE = True
except ImportError:
    logging.getLogger("aurora_api").warning(
        "Thread Transfer Bridge not available - cross-thread continuity features disabled"
    )
    THREAD_BRIDGE_AVAILABLE = False
    get_bridge_instance = None
    initialize_bridge = None

# Import Thread Transfer Bridge v2 integration
try:
    from modules.reflective_autonomy.thread_transfer.v2 import (
        get_node_registry,
        get_drift_predictor,
        get_pattern_analyzer,
        get_auto_corrector,
        get_layer_manager,
        get_hierarchy_validator,
        get_repository_synchronizer,
        get_cross_repository_bridge,
        BridgeLayer,
        DriftFeatures,
    )
    THREAD_BRIDGE_V2_AVAILABLE = True
except ImportError:
    logging.getLogger("aurora_api").warning(
        "Thread Transfer Bridge v2 not available - distributed/predictive features disabled"
    )
    THREAD_BRIDGE_V2_AVAILABLE = False

# Import Event Coordination Registry API integration
try:
    from src.coordination.event_api import router as event_coordination_router
    EVENT_COORDINATION_AVAILABLE = True
    EVENT_COORDINATION_ROUTER = event_coordination_router
except ImportError:
    logging.getLogger("aurora_api").warning(
        "Event Coordination not available - multi-agent coordination features disabled"
    )
    EVENT_COORDINATION_AVAILABLE = False
    EVENT_COORDINATION_ROUTER = None

# Import Fleet Bridge API integration
try:
    from src.integrations.fleet_bridge import router as fleet_bridge_router
    FLEET_BRIDGE_AVAILABLE = True
    FLEET_BRIDGE_ROUTER = fleet_bridge_router
except ImportError:
    logging.getLogger("aurora_api").warning("Fleet Bridge not available - Python-JS fleet sync features disabled")
    FLEET_BRIDGE_AVAILABLE = False
    FLEET_BRIDGE_ROUTER = None

# from modules.symbolic_core.quantum_vsa import QuantumVSA  # Uncomment if available

app = FastAPI(
    title="Aurora CloudBank Symbolic API - Sonnet 4 Enhanced",
    description="Quantum-enhanced symbolic governance system with ChatGPT Agent Mode integration",
    version="1.0.0"
)

# Structured logger (avoids f-string interpolation for security)
logger = logging.getLogger("aurora_api")


# HIGH-5: NoSQL Injection Prevention - Input Validation Helper
def validate_identifier(identifier: str, param_name: str) -> str:
    """
    Validate identifiers (node_id, repo_id, bridge_id, etc.) to prevent injection attacks.
    
    HIGH-5: NoSQL injection prevention pattern
    - Alphanumeric + hyphens/underscores only
    - Max length: 64 characters
    - No path traversal sequences
    - No special characters that could enable injection
    
    Args:
        identifier: The identifier string to validate
        param_name: Name of the parameter (for error messages)
    
    Returns:
        Validated identifier string
    
    Raises:
        HTTPException: If identifier is invalid (400 Bad Request)
    """
    import re
    
    if not identifier or len(identifier) > 64:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name}: must be 1-64 characters"
        )
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', identifier):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name}: alphanumeric, hyphens, underscores only"
        )
    
    # Block path traversal attempts
    if '..' in identifier or '/' in identifier or '\\' in identifier:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name}: path traversal detected"
        )
    
    return identifier

# Include AuMemManager API routes if available
if AUMEMMANAGER_AVAILABLE and AUMEMMANAGER_ROUTER:
    try:
        app.include_router(AUMEMMANAGER_ROUTER)
        logger.info("AuMemManager API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate AuMemManager API routes: %s", e)
        AUMEMMANAGER_AVAILABLE = False

# Include Data Guardian API routes if available
if DATA_GUARDIAN_AVAILABLE and DATA_GUARDIAN_ROUTER:
    try:
        app.include_router(DATA_GUARDIAN_ROUTER)
        logger.info("Data Guardian API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Data Guardian API routes: %s", e)
        DATA_GUARDIAN_AVAILABLE = False

# Include Insight Ledger API routes if available
if INSIGHT_LEDGER_AVAILABLE and INSIGHT_LEDGER_ROUTER:
    try:
        app.include_router(INSIGHT_LEDGER_ROUTER)
        if initialize_ledger:
            initialize_ledger(storage_path="./data/insight_ledger")
        logger.info("Insight Ledger API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Insight Ledger API routes: %s", e)
        INSIGHT_LEDGER_AVAILABLE = False

# Include Quantum Simulator API routes if available
if QUANTUM_SIMULATOR_AVAILABLE and QUANTUM_SIMULATOR_ROUTER:
    try:
        app.include_router(QUANTUM_SIMULATOR_ROUTER)
        logger.info("Quantum Simulator API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Quantum Simulator API routes: %s", e)
        QUANTUM_SIMULATOR_AVAILABLE = False

# Include Cross-Repo Collaboration API routes
try:
    from src.collab.api_routes import router as collab_router
    app.include_router(collab_router)
    logger.info("Cross-Repo Collaboration API routes integrated successfully")
except ImportError as e:
    logger.warning("Cross-Repo Collaboration not available: %s", e)
except Exception as e:
    logger.error("Failed to integrate Cross-Repo Collaboration API routes: %s", e)

# Include Subroutine API routes
try:
    from src.subroutines.api import router as subroutine_router
    app.include_router(subroutine_router)
    logger.info("Subroutine API routes integrated successfully")
    SUBROUTINE_AVAILABLE = True
except ImportError as e:
    logger.warning("Subroutine system not available: %s", e)
    SUBROUTINE_AVAILABLE = False
except Exception as e:
    logger.error("Failed to integrate Subroutine API routes: %s", e)
    SUBROUTINE_AVAILABLE = False

# Include Event Coordination API routes if available
if EVENT_COORDINATION_AVAILABLE and EVENT_COORDINATION_ROUTER:
    try:
        app.include_router(EVENT_COORDINATION_ROUTER)
        logger.info("Event Coordination API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Event Coordination API routes: %s", e)
        EVENT_COORDINATION_AVAILABLE = False

# Include Fleet Bridge API routes if available
if FLEET_BRIDGE_AVAILABLE and FLEET_BRIDGE_ROUTER:
    try:
        app.include_router(FLEET_BRIDGE_ROUTER)
        logger.info("Fleet Bridge API routes integrated successfully")
    except Exception as e:
        logger.error("Failed to integrate Fleet Bridge API routes: %s", e)
        FLEET_BRIDGE_AVAILABLE = False

ga = GeometricAlgebra()


def parse_multivector(expression: str, blades: dict):
    """Safely parse a multivector expression.

    Complexity reduction: Split validation and accumulation into helpers.
    """
    def _tokenize(expr: str) -> list[str]:
        return expr.split()

    def _validate(tokens: list[str], allowed: set[str]) -> None:
        for token in tokens:
            if token not in allowed and not token.isnumeric():
                raise ValueError(f"Invalid token in expression: {token}")

    def _accumulate(tokens: list[str]) -> any:
        result = None
        for token in tokens:
            if token in blades:
                result = blades[token] if result is None else result + blades[token]
            elif token.isnumeric():
                numeric = float(token)
                result = numeric if result is None else result + numeric
        return result

    tokens = _tokenize(expression)
    _validate(tokens, set(blades.keys()))
    return _accumulate(tokens)


def _sanitize_tools_info(info: Dict[str, Any]) -> Dict[str, Any]:
    """Remove non-serializable entries (e.g., callable handlers) from tools payload."""
    if not isinstance(info, dict):
        return {"tools": {}, "error": "invalid_tools_info"}
    sanitized = dict(info)
    tools = sanitized.get("tools")
    if isinstance(tools, dict):
        clean_tools = {}
        for name, tool in tools.items():
            if isinstance(tool, dict):
                clean_tools[name] = {k: v for k, v in tool.items() if k != "handler"}
            else:
                clean_tools[name] = tool
        sanitized["tools"] = clean_tools
    return sanitized


class VectorRequest(BaseModel):
    x: float

    y: float

    z: float


class MultivectorRequest(BaseModel):
    a: str

    b: str


class Sonnet4EnableRequest(BaseModel):
    client_id: str = None

    enable_all: bool = True


class AgentToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    session_id: Optional[str] = None


class AgentSessionRequest(BaseModel):
    action: str
    session_id: Optional[str] = None
    state_data: Optional[Dict[str, Any]] = None


# verify_csrf inside
@app.post("/geometric/vector", dependencies=[Depends(security)])
@limiter.limit("60/minute")  # Computational operation
def create_vector(req: VectorRequest, request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    verify_csrf_token(token)
    v = ga.blades["e1"] * req.x + ga.blades["e2"] * req.y + ga.blades["e3"] * req.z

    return {"vector": str(v)}


# verify_csrf inside
@app.post("/geometric/mult", dependencies=[Depends(security)])
@limiter.limit("60/minute")  # Computational operation
@validation_handler()
def geometric_product(
    req: MultivectorRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    verify_csrf_token(token)
    a = parse_multivector(req.a, ga.blades)
    b = parse_multivector(req.b, ga.blades)
    result = ga.mult(a, b)
    return {"result": str(result)}


# verify_csrf inside
@app.post("/sonnet4/enable", dependencies=[Depends(security)])
@limiter.limit("10/minute")  # State-changing operation
async def enable_sonnet4(
    req: Sonnet4EnableRequest = None,
    request: Request = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """Enable Claude Sonnet 4 for all clients or specific client"""
    verify_csrf_token(token)

    try:
        if req and req.enable_all:
            results = await enable_sonnet4_globally()

            return {
                "status": "success",
                "message": "Claude Sonnet 4 enabled for all clients",
                "results": results,
                "global_status": sonnet4_hub.get_global_status(),
            }

        elif req and req.client_id:
            result = await sonnet4_hub._enable_sonnet4_for_client(req.client_id)

            return {
                "status": "success" if result else "error",
                "client_id": req.client_id,
                "enabled": result,
                "client_status": sonnet4_hub.get_client_status(req.client_id),
            }

        else:
            # Default: enable for all clients
            results = await enable_sonnet4_globally()

            return {
                "status": "success",
                "message": "Claude Sonnet 4 enabled for all clients (default action)",
                "results": results,
                "global_status": sonnet4_hub.get_global_status(),
            }

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to enable Sonnet 4")


@app.get("/sonnet4/status")
@limiter.limit("200/minute")  # Read-only operation
def get_sonnet4_status(request: Request):
    """Get Claude Sonnet 4 status"""
    return {
        "global_status": sonnet4_hub.get_global_status(),
        "configuration": {
            "enabled": sonnet4_hub.sonnet4_config.enabled,
            "enable_for_all_clients": sonnet4_hub.sonnet4_config.enable_for_all_clients,
            "model": sonnet4_hub.sonnet4_config.model,
            "preserve_4o_logic": sonnet4_hub.sonnet4_config.preserve_4o_logic,
            "fallback_model": sonnet4_hub.sonnet4_config.fallback_model,
        },
    }


@app.get("/sonnet4/clients/{client_id}")
@limiter.limit("200/minute")  # Read-only operation - client status
def get_client_sonnet4_status(client_id: str, request: Request):
    """Get Claude Sonnet 4 status for specific client"""
    return sonnet4_hub.get_client_status(client_id)


@app.get("/health")
@limiter.limit("300/minute")  # Health check - frequent monitoring
def health_check(request: Request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Aurora CloudBank Symbolic API",
        "sonnet4_enabled": sonnet4_hub.sonnet4_config.enabled,
        "agent_mode_enabled": True,
        "timestamp": "2025-06-29",
    }


# Compatibility alias for Docker healthcheck (docker-compose points to /api/health)
@app.get("/api/health")
@limiter.limit("300/minute")  # Health check - frequent monitoring
def health_check_api(request: Request):
    return health_check(request)


# ================================
# ChatGPT Agent Mode Endpoints
# ================================

@app.get("/agent/tools")
@limiter.limit("30/minute")  # Agent tools - moderate rate for tool discovery
async def get_agent_tools(request: Request):
    """
    Discover available agent tools and capabilities for ChatGPT Agent Mode
    Returns OpenAPI-compatible tool definitions
    """
    try:
        tools_info = await chatgpt_agent_integration.discover_tools()
        tools_info = _sanitize_tools_info(tools_info)
        return JSONResponse(content=tools_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to discover tools: {str(e)}")


# verify_csrf inside
@app.post("/agent/execute", dependencies=[Depends(security)])
@limiter.limit("30/minute")  # Agent tools - execution rate matches discovery
async def execute_agent_tool(
    req: AgentToolRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute agent tool with validated parameters and Aurora symbolic anchoring
    Supports all registered tools: symbolic_processing, geometric_algebra, session_management, system_status
    """
    bound_session_id = sanitize_session_id(req.session_id)
    verify_csrf_token(token, session_id=bound_session_id)

    try:
        result = await chatgpt_agent_integration.execute_tool(
            tool_name=req.tool_name,
            parameters=req.parameters,
            session_id=req.session_id
        )
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


# verify_csrf inside
@app.post("/agent/session", dependencies=[Depends(security)])
@limiter.limit("10/minute")  # State-changing operation - session management
async def manage_agent_session(
    req: AgentSessionRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Manage agent session state and context persistence
    Actions: create, update, get, delete
    """
    verify_csrf_token(token, session_id=sanitize_session_id(req.session_id))

    try:
        result = await chatgpt_agent_integration.execute_tool(
            tool_name="session_management",
            parameters={
                "action": req.action,
                "session_id": req.session_id,
                "state_data": req.state_data or {}
            }
        )
        # Helper: sanitize recovery suggestions (internal only)

        def sanitize_recovery_suggestions(suggestions):
            sanitized = []
            for s in suggestions:
                if not isinstance(s, str):
                    continue
                s = s.strip()
                # Remove lines that look like stack traces or file paths
                if any(x in s for x in ["Traceback", "File ", ".py", "/", "\\"]):
                    continue
                # Optionally, truncate to 200 chars
                if len(s) > 200:
                    s = s[:200] + "..."
                sanitized.append(s)
            return sanitized
        if not result.get("success", False):
            # Optionally: log result["error"] and other fields here, e.g., using logging module.
            recovery_suggestions = result.get("recovery_suggestions", [])
            safe_recovery_suggestions = sanitize_recovery_suggestions(recovery_suggestions)
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Session management failed.",
                    # Optionally log: result.get("error") server-side here.
                    "recovery_suggestions": safe_recovery_suggestions,
                },
            )
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception:
        # Intentionally avoid leaking internal exception details
        raise HTTPException(status_code=500, detail="Session management failed.")


@app.get("/agent/status")
@limiter.limit("200/minute")  # Read-only operation - agent status
async def get_agent_status(request: Request):
    """Get current agent system status and health information"""
    try:
        status = await chatgpt_agent_integration.get_agent_status()
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@app.websocket("/agent/stream")
async def agent_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent communication
    Supports streaming responses and persistent connections

    SECURITY: Requires authentication token in query params
    """
    # SECURITY FIX: Require authentication before accepting connection
    token = websocket.query_params.get("token")
    client_id = verify_ws_token(token) if token else None

    if not client_id:
        await websocket.close(code=1008, reason="Unauthorized: Invalid or missing token")
        return

    # Accept connection only after authentication
    await websocket.accept()

    def _initial_ws_message(cid: str) -> dict:
        return {
            "type": "connection_established",
            "timestamp": "2025-01-01T00:00:00Z",
            "symbolic_anchor": "EOS_SEED_ORION",
            "ethics_protocol": "Picard_Delta_3",
            "agent_mode": "chatgpt_agent_mode",
            "context_tag": "websocket_agent_stream",
            "client_id": cid,
        }

    async def _handle_tool_execution(websocket: WebSocket, data: dict, request_id: str) -> None:
        tool_name = data.get("tool_name", "").strip()
        if not validate_ws_tool(tool_name):
            await websocket.send_json({
                "type": "error",
                "error": f"Tool '{tool_name}' is not allowed via WebSocket",
                "request_id": request_id,
            })
            return

        parameters = data.get("parameters", {})
        if not isinstance(parameters, dict):
            await websocket.send_json({
                "type": "error",
                "error": "Invalid parameters format (must be object)",
                "request_id": request_id,
            })
            return

        try:
            result = await chatgpt_agent_integration.execute_tool(
                tool_name=tool_name,
                parameters=parameters,
                session_id=sanitize_session_id(data.get("session_id")),
            )
            await websocket.send_json({
                "type": "tool_result",
                "result": result,
                "request_id": request_id,
            })
        except Exception:
            await websocket.send_json({
                "type": "error",
                "error": "Tool execution failed",
                "request_id": request_id,
            })

    async def _handle_ping(websocket: WebSocket, request_id: str) -> None:
        await websocket.send_json({
            "type": "pong",
            "timestamp": "2025-01-01T00:00:00Z",
            "request_id": request_id,
        })

    try:
        await websocket.send_json(_initial_ws_message(client_id))

        while True:
            data = await websocket.receive_json()
            request_id = sanitize_request_id(data.get("request_id"))
            msg_type = data.get("type")

            if msg_type == "tool_execution":
                await _handle_tool_execution(websocket, data, request_id)
            elif msg_type == "ping":
                await _handle_ping(websocket, request_id)

            else:
                await websocket.send_json({
                    "type": "error",
                    "error": "Unknown message type",
                    "supported_types": ["tool_execution", "ping"],
                    "request_id": request_id,
                })

    except Exception:
        await websocket.close(code=1011, reason="Internal error")


# ================================
# Gemini Agent Mode Endpoints
# ================================

@app.get("/agent/gemini/tools")
@limiter.limit("30/minute")  # Agent tools - Gemini tool discovery
async def get_gemini_agent_tools(request: Request):
    """
    Discover available agent tools for Gemini Agent Mode.
    """
    if not GEMINI_AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini Agent not available")
    try:
        tools_info = gemini_agent_integration.list_tools()
        return JSONResponse(content={"tools": tools_info})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to discover Gemini tools")


# verify_csrf inside
@app.post("/agent/gemini/execute", dependencies=[Depends(security)])
@limiter.limit("30/minute")  # Agent tools - Gemini tool execution
async def execute_gemini_agent_tool(
    req: AgentToolRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute a Gemini agent tool, respecting the Symbolic Sandbox Protocol (SSP).
    A 'dry_run' parameter is used to get an impact report before committing.
    """
    verify_csrf_token(token)
    if not GEMINI_AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini Agent not available")

    try:
        result = await gemini_agent_integration.handle_tool_call(
            tool_name=req.tool_name,
            params=req.parameters
        )
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Gemini tool execution failed")


# ==============================================================================
# THREAD TRANSFER BRIDGE ENDPOINTS
# ==============================================================================

@app.get("/api/thread-bridge/status")
@limiter.limit("20/minute")
async def thread_bridge_status_endpoint(request: Request):
    """
    Get Thread Transfer Bridge status
    
    Returns current bridge status, drift metrics, and companion thread health.
    """
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )
    
    try:
        bridge = get_bridge_instance()
        status = bridge.get_status()
        
        return {
            "success": True,
            "status": status.status,
            "drift": status.drift,
            "drift_alert_level": status.drift_alert_level,
            "companion_threads": status.companion_threads,
            "synchronized_threads": status.synchronized_threads,
            "last_handshake": status.last_handshake.isoformat() if status.last_handshake else None,
            "continuity_seal": status.continuity_seal,
            "anchor_seed": status.anchor_seed,
            "ethics_protocol": status.ethics_protocol,
            "context_tag": "thread_bridge_status",
            "timestamp": "2025-10-28T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bridge status error: {str(e)}")


class HandshakeRequest(BaseModel):
    """Request model for thread handshake"""
    thread_id: str


# verify_csrf inside
@app.post("/api/thread-bridge/handshake", dependencies=[Depends(security)])
@limiter.limit("10/minute")
async def thread_bridge_handshake_endpoint(
    request: HandshakeRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Initiate handshake sequence with a companion thread
    
    Executes the 5-stage handshake: INIT → VERIFY_ANCHOR → LOCK_DRIFT →
    ALIGN_ETHICS → SYNC_COMPLETE
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )
    
    try:
        bridge = get_bridge_instance()
        result = bridge.handshake(request.thread_id)
        
        if not result.get("success"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": result.get("error"),
                    "stages": result.get("stages", []),
                    "context_tag": "thread_bridge_handshake_failed"
                }
            )
        
        return {
            "success": True,
            "thread_id": result["thread_id"],
            "timestamp": result["timestamp"].isoformat(),
            "stages": result["stages"],
            "context_tag": "thread_bridge_handshake_success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Handshake error: {str(e)}")


class ValidateRequest(BaseModel):
    """Request model for continuity validation"""
    source: str
    target: str


# verify_csrf inside
@app.post("/api/thread-bridge/validate", dependencies=[Depends(security)])
@limiter.limit("30/minute")
async def thread_bridge_validate_endpoint(
    request: ValidateRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate continuity between two threads before transfer
    
    Checks anchor alignment, drift levels, and ethics compatibility.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )
    
    try:
        bridge = get_bridge_instance()
        validation = bridge.validate_continuity(request.source, request.target)
        
        return {
            "success": True,
            "valid": validation.get("valid"),
            "source": validation["source"],
            "target": validation["target"],
            "timestamp": validation["timestamp"].isoformat(),
            "checks": validation["checks"],
            "error": validation.get("error"),
            "context_tag": "thread_bridge_validation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@app.get("/api/thread-bridge/companions")
@limiter.limit("30/minute")
async def thread_bridge_companions_endpoint(request: Request):
    """
    Get list of all companion threads with their status
    
    Returns detailed information about each companion thread including
    alignment status, drift levels, and last sync timestamp.
    """
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )
    
    try:
        bridge = get_bridge_instance()
        companions = bridge.get_companion_threads()
        
        return {
            "success": True,
            "companion_threads": companions,
            "count": len(companions),
            "anchor_seed": bridge.capsule.get("anchor_seed"),
            "context_tag": "thread_bridge_companions"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Companions query error: {str(e)}")


class TransferRequest(BaseModel):
    """Request model for context transfer"""
    source: str
    target: str
    context_data: Dict[str, Any]


# verify_csrf inside
@app.post("/api/thread-bridge/transfer", dependencies=[Depends(security)])
@limiter.limit("10/minute")
async def thread_bridge_transfer_endpoint(
    request: TransferRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Transfer context from source thread to target thread
    
    Performs full validation, ethics checks, and secure state transfer
    between companion threads.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge not available"
        )
    
    try:
        bridge = get_bridge_instance()
        result = bridge.transfer_context(
            source=request.source,
            target=request.target,
            context_data=request.context_data
        )
        
        if not result.get("success"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": result.get("error"),
                    "validation": result.get("validation"),
                    "context_tag": "thread_bridge_transfer_failed"
                }
            )
        
        return {
            "success": True,
            "source": result["source"],
            "target": result["target"],
            "timestamp": result["timestamp"].isoformat(),
            "bytes_transferred": result["bytes_transferred"],
            "drift_delta": result["drift_delta"],
            "continuity_seal": result["continuity_seal"],
            "context_tag": "thread_bridge_transfer_success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer error: {str(e)}")


# ============================================================================
# THREAD TRANSFER BRIDGE V2 ENDPOINTS
# ============================================================================

# Pydantic models for v2 endpoints
class NodeRegisterRequest(BaseModel):
    hostname: str
    port: int
    region: str
    capacity: int
    version: str = "2.0.0"
    capabilities: Optional[list] = None


class DriftPredictionRequest(BaseModel):
    drift_velocity: float
    drift_acceleration: float
    handshake_count: int
    average_handshake_duration: float
    failed_handshake_ratio: float
    time_of_day: float
    day_of_week: int
    thread_age_hours: float
    anchor_changes: int
    sync_frequency: float
    node_count: int
    thread_id: str


class LayerBridgeRequest(BaseModel):
    bridge_id: str
    layer: str  # L1, L2, or L3
    source_id: str
    target_id: str
    thread_id: str


class RepositoryRegisterRequest(BaseModel):
    repo_id: str
    repo_path: str
    branch: str = "main"


# ------------------------------------------------------------------------
# Phase 1: Distributed Node Management (6 endpoints)
# ------------------------------------------------------------------------

# verify_csrf inside
@app.post("/api/v2/nodes/register", dependencies=[Depends(security)])
@limiter.limit("30/minute")
async def v2_register_node(
    node_request: NodeRegisterRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Register a new bridge node in the distributed constellation.
    
    Requires: hostname, port, region, capacity, version
    Returns: Node metadata with unique node_id
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        registry = get_node_registry()
        node = await registry.register_node(
            hostname=node_request.hostname,
            port=node_request.port,
            region=node_request.region,
            capacity=node_request.capacity,
            version=node_request.version,
            capabilities=node_request.capabilities or []
        )
        
        return {
            "success": True,
            "node": {
                "node_id": node.node_id,
                "hostname": node.hostname,
                "port": node.port,
                "region": node.region,
                "capacity": node.capacity,
                "status": node.status.value,
                "version": node.version,
                "anchor_hash": node.anchor_hash
            },
            "context_tag": "v2_node_registered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Node registration error: {str(e)}")


@app.delete("/api/v2/nodes/{node_id}", dependencies=[Depends(security)])
@limiter.limit("30/minute")
async def v2_unregister_node(
    node_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Unregister a bridge node from the constellation.
    
    Gracefully removes node from registry and load balancing pool.
    
    SECURITY: CSRF protection via token validation (HIGH-4 remediation)
    """
    # HIGH-4: Verify CSRF token before node deletion
    verify_csrf_token(token)
    
    # HIGH-5: Validate node_id parameter to prevent injection
    node_id = validate_identifier(node_id, "node_id")
    
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        registry = get_node_registry()
        success = await registry.unregister_node(node_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        
        return {
            "success": True,
            "node_id": node_id,
            "context_tag": "v2_node_unregistered"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Node unregistration error: {str(e)}")


@app.get("/api/v2/nodes/{node_id}/health")
@limiter.limit("60/minute")
async def v2_get_node_health(node_id: str, request: Request):
    """
    Get detailed health status for a specific node.
    
    Returns: 4-metric health check (heartbeat, API, anchor, drift)
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        registry = get_node_registry()
        node = await registry.get_node(node_id)
        
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        
        return {
            "success": True,
            "node_id": node.node_id,
            "status": node.status.value,
            "is_healthy": node.is_healthy(),
            "current_load": node.current_load,
            "available_capacity": node.available_capacity(),
            "load_percentage": node.load_percentage(),
            "last_heartbeat": node.last_heartbeat.isoformat(),
            "context_tag": "v2_node_health"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")


@app.get("/api/v2/nodes")
@limiter.limit("60/minute")
async def v2_list_nodes(request: Request):
    """
    List all registered bridge nodes.
    
    Returns: Array of node metadata with current status and load
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        registry = get_node_registry()
        nodes = await registry.get_online_nodes()
        
        return {
            "success": True,
            "count": len(nodes),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "hostname": node.hostname,
                    "port": node.port,
                    "region": node.region,
                    "status": node.status.value,
                    "current_load": node.current_load,
                    "capacity": node.capacity,
                    "available_capacity": node.available_capacity(),
                    "version": node.version
                }
                for node in nodes
            ],
            "context_tag": "v2_nodes_listed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Node listing error: {str(e)}")


@app.get("/api/v2/cluster/health")
@limiter.limit("30/minute")
async def v2_get_cluster_health(request: Request):
    """
    Get overall cluster health status.
    
    Returns: Aggregate metrics across all nodes
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        registry = get_node_registry()
        cluster_health = await registry.get_cluster_health()
        
        return {
            "success": True,
            "cluster_health": cluster_health,
            "context_tag": "v2_cluster_health"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cluster health error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/consensus/elect", dependencies=[Depends(security)])
@limiter.limit("10/minute")
async def v2_trigger_election(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Trigger a Raft consensus leader election.
    
    WARNING: Use only for testing or emergency recovery.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    return {
        "success": False,
        "message": "Consensus election must be triggered via node registry",
        "context_tag": "v2_consensus_election_unavailable"
    }


# ------------------------------------------------------------------------
# Phase 2: Cross-Repository Sync (4 endpoints)
# ------------------------------------------------------------------------

# verify_csrf inside
@app.post("/api/v2/repos/register", dependencies=[Depends(security)])
@limiter.limit("20/minute")
async def v2_register_repository(
    request: RepositoryRegisterRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Register a Git repository for cross-repo synchronization.
    
    Enables anchor propagation and thread continuity across repos.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        synchronizer = get_repository_synchronizer()
        repo_info = await synchronizer.register_repository(
            repo_id=request.repo_id,
            repo_path=request.repo_path,
            branch=request.branch
        )
        
        return {
            "success": True,
            "repository": {
                "repo_id": repo_info.repo_id,
                "repo_path": repo_info.repo_path,
                "branch": repo_info.branch,
                "status": repo_info.status.value,
                "last_sync": repo_info.last_sync.isoformat() if repo_info.last_sync else None
            },
            "context_tag": "v2_repo_registered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository registration error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/repos/{repo_id}/sync", dependencies=[Depends(security)])
@limiter.limit("10/minute")
async def v2_sync_repository(
    repo_id: str,
    direction: str = "bidirectional",
    request: Request = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Synchronize a registered repository.
    
    Pulls latest changes and pushes local anchors.
    Direction: push, pull, or bidirectional
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        synchronizer = get_repository_synchronizer()
        
        # Map string to SyncDirection enum
        from modules.reflective_autonomy.thread_transfer.v2 import SyncDirection
        direction_map = {
            "push": SyncDirection.PUSH,
            "pull": SyncDirection.PULL,
            "bidirectional": SyncDirection.BIDIRECTIONAL
        }
        sync_dir = direction_map.get(direction.lower(), SyncDirection.BIDIRECTIONAL)
        
        result = await synchronizer.sync_repository(repo_id, sync_dir)
        
        return {
            "success": result["success"],
            "repo_id": repo_id,
            "direction": direction,
            "message": result.get("message", "Sync completed"),
            "context_tag": "v2_repo_synced"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository sync error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/bridges/cross-repo", dependencies=[Depends(security)])
@limiter.limit("10/minute")
async def v2_create_cross_repo_bridge(
    source_repo: str,
    target_repo: str,
    thread_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a cross-repository bridge for thread continuity.
    
    Initiates 7-stage handshake between repositories.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        cross_repo_bridge = get_cross_repository_bridge()
        # Generate a unique bridge id for this cross-repo bridge
        import uuid as _uuid
        new_bridge_id = _uuid.uuid4().hex

        bridge_obj = await cross_repo_bridge.create_bridge(
            bridge_id=new_bridge_id,
            source_repo_id=source_repo,
            target_repo_id=target_repo,
            thread_id=thread_id
        )

        return {
            "success": True,
            "bridge_id": bridge_obj.bridge_id if hasattr(bridge_obj, "bridge_id") else new_bridge_id,
            "source_repo": source_repo,
            "target_repo": target_repo,
            "thread_id": thread_id,
            "context_tag": "v2_cross_repo_bridge_created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-repo bridge error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/bridges/{bridge_id}/handshake", dependencies=[Depends(security)])
@limiter.limit("10/minute")
async def v2_execute_cross_repo_handshake(
    bridge_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute 7-stage cross-repository handshake.
    
    Completes thread transfer between repositories with full validation.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        cross_repo_bridge = get_cross_repository_bridge()
        
        result = await cross_repo_bridge.execute_handshake(bridge_id)
        
        return {
            "success": result["success"],
            "bridge_id": bridge_id,
            "stages_completed": result.get("stages_completed", 0),
            "drift_percentage": result.get("drift_percentage", 0.0),
            "context_tag": "v2_cross_repo_handshake_executed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-repo handshake error: {str(e)}")


# ------------------------------------------------------------------------
# Phase 3: Drift Prediction (5 endpoints)
# ------------------------------------------------------------------------

# verify_csrf inside
@app.post("/api/v2/drift/predict", dependencies=[Depends(security)])
@limiter.limit("30/minute")
async def v2_predict_drift(
    drift_request: DriftPredictionRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Predict future drift based on current features.
    
    Uses LSTM model with 11-feature input for 24-hour prediction.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        predictor = get_drift_predictor()
        
        features = DriftFeatures(
            drift_velocity=drift_request.drift_velocity,
            drift_acceleration=drift_request.drift_acceleration,
            handshake_count=drift_request.handshake_count,
            average_handshake_duration=drift_request.average_handshake_duration,
            failed_handshake_ratio=drift_request.failed_handshake_ratio,
            time_of_day=drift_request.time_of_day,
            day_of_week=drift_request.day_of_week,
            thread_age_hours=drift_request.thread_age_hours,
            anchor_changes=drift_request.anchor_changes,
            sync_frequency=drift_request.sync_frequency,
            node_count=drift_request.node_count
        )
        
        prediction = await predictor.predict_drift(features, drift_request.thread_id)
        
        return {
            "success": True,
            "thread_id": drift_request.thread_id,
            "predicted_drift": prediction.predicted_drift,
            "severity": prediction.severity.value,
            "confidence": prediction.confidence.value,
            "prediction_horizon_hours": prediction.prediction_horizon_hours,
            "recommendations": prediction.recommendations,
            "context_tag": "v2_drift_predicted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drift prediction error: {str(e)}")


@app.get("/api/v2/drift/patterns")
@limiter.limit("30/minute")
async def v2_analyze_patterns(request: Request):
    """
    Analyze historical drift patterns.
    
    Returns detected patterns: stable, trending, cyclical, volatile, anomalous
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        analyzer = get_pattern_analyzer()
        patterns = await analyzer.analyze_patterns()
        
        return {
            "success": True,
            "patterns": [
                {
                    "pattern_type": p.pattern_type.value,
                    "confidence": p.confidence,
                    "description": p.description,
                    "metadata": p.metadata
                }
                for p in patterns
            ],
            "context_tag": "v2_patterns_analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/drift/observe", dependencies=[Depends(security)])
@limiter.limit("60/minute")
async def v2_record_observation(
    drift: float,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Record a drift observation for pattern analysis.
    
    Adds data point to historical drift tracking.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        from datetime import datetime
        analyzer = get_pattern_analyzer()
        analyzer.add_observation(datetime.now(), drift)
        
        return {
            "success": True,
            "drift": drift,
            "timestamp": datetime.now().isoformat(),
            "context_tag": "v2_observation_recorded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Observation recording error: {str(e)}")


@app.get("/api/v2/drift/accuracy")
@limiter.limit("30/minute")
async def v2_get_prediction_accuracy(request: Request):
    """
    Get prediction accuracy metrics.
    
    Returns: Historical accuracy statistics for drift predictions
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        predictor = get_drift_predictor()
        accuracy = await predictor.get_prediction_accuracy()
        
        return {
            "success": True,
            "accuracy": accuracy,
            "context_tag": "v2_prediction_accuracy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accuracy metrics error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/corrections/apply", dependencies=[Depends(security)])
@limiter.limit("10/minute")
async def v2_apply_correction(
    thread_id: str,
    predicted_drift: float,
    current_drift: float,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Apply auto-correction actions based on drift prediction.
    
    Evaluates correction strategies and executes if drift exceeds threshold.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        corrector = get_auto_corrector()
        
        actions = await corrector.evaluate_correction(
            predicted_drift=predicted_drift,
            current_drift=current_drift,
            thread_id=thread_id,
            metadata={}
        )
        
        return {
            "success": True,
            "thread_id": thread_id,
            "actions_recommended": len(actions),
            "actions": [
                {
                    "strategy": action.strategy.value,
                    "priority": action.priority,
                    "description": action.description
                }
                for action in actions
            ],
            "context_tag": "v2_corrections_evaluated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correction application error: {str(e)}")


# ------------------------------------------------------------------------
# Phase 4: Layer Management (6 endpoints)
# ------------------------------------------------------------------------

# verify_csrf inside
@app.post("/api/v2/layers/bridge", dependencies=[Depends(security)])
@limiter.limit("20/minute")
async def v2_create_layer_bridge(
    layer_request: LayerBridgeRequest,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a multi-layer bridge (L1/L2/L3).
    
    L1: Thread-to-thread (5 stages, 0.0% max drift)
    L2: Repo-to-repo (7 stages, 0.1% max drift)
    L3: Cluster-to-cluster (9 stages, 0.5% max drift, PKI required)
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        layer_manager = get_layer_manager()
        
        # Map string to BridgeLayer enum
        layer_map = {
            "L1": BridgeLayer.L1,
            "L2": BridgeLayer.L2,
            "L3": BridgeLayer.L3
        }
        layer = layer_map.get(layer_request.layer.upper())
        
        if not layer:
            raise HTTPException(status_code=400, detail=f"Invalid layer: {layer_request.layer}")
        
        bridge = await layer_manager.create_bridge(
            bridge_id=layer_request.bridge_id,
            layer=layer,
            source_id=layer_request.source_id,
            target_id=layer_request.target_id,
            thread_id=layer_request.thread_id
        )
        
        return {
            "success": True,
            "bridge": {
                "bridge_id": bridge.bridge_id,
                "layer": bridge.layer.value,
                "source_id": bridge.source_id,
                "target_id": bridge.target_id,
                "thread_id": bridge.thread_id,
                "status": bridge.status
            },
            "context_tag": "v2_layer_bridge_created"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Layer bridge creation error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/layers/{bridge_id}/handshake", dependencies=[Depends(security)])
@limiter.limit("10/minute")
async def v2_execute_layered_handshake(
    bridge_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Execute layer-specific handshake protocol.
    
    Completes all stages for the bridge's layer with proper validation.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        layer_manager = get_layer_manager()
        
        result = await layer_manager.execute_layered_handshake(bridge_id)
        
        return {
            "success": result["success"],
            "bridge_id": bridge_id,
            "stages_completed": result.get("stages_completed", 0),
            "drift_percentage": result.get("drift_percentage", 0.0),
            "context_tag": "v2_layered_handshake_executed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Layered handshake error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/layers/validate", dependencies=[Depends(security)])
@limiter.limit("30/minute")
async def v2_validate_hierarchy(
    thread_id: str,
    strict_mode: bool = False,
    request: Request = None,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate multi-layer hierarchy for a thread.
    
    Checks: layer completion, drift tolerance, PKI (L3), dependencies
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        layer_manager = get_layer_manager()
        validator = get_hierarchy_validator()
        
        bridges = layer_manager.list_bridges(thread_id=thread_id)
        report = await validator.validate_hierarchy(
            bridges=bridges,
            thread_id=thread_id,
            strict_mode=strict_mode
        )
        
        return {
            "success": True,
            "valid": report.valid,
            "thread_id": thread_id,
            "layer_status": report.layer_status,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "layer": issue.layer,
                    "code": issue.code,
                    "message": issue.message
                }
                for issue in report.issues
            ],
            "context_tag": "v2_hierarchy_validated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hierarchy validation error: {str(e)}")


@app.get("/api/v2/layers/bridges")
@limiter.limit("60/minute")
async def v2_list_layer_bridges(thread_id: Optional[str] = None, layer: Optional[str] = None, request: Request = None):
    """
    List all layer bridges, optionally filtered by thread_id or layer.
    
    Returns array of bridge metadata with current status.
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        layer_manager = get_layer_manager()
        
        # Parse layer filter if provided
        layer_enum = None
        if layer:
            layer_map = {
                "L1": BridgeLayer.L1,
                "L2": BridgeLayer.L2,
                "L3": BridgeLayer.L3
            }
            layer_enum = layer_map.get(layer.upper())
        
        bridges = layer_manager.list_bridges(thread_id=thread_id, layer=layer_enum)
        
        return {
            "success": True,
            "count": len(bridges),
            "bridges": [
                {
                    "bridge_id": b.bridge_id,
                    "layer": b.layer.value,
                    "source_id": b.source_id,
                    "target_id": b.target_id,
                    "thread_id": b.thread_id,
                    "status": b.status,
                    "created_at": b.created_at.isoformat() if hasattr(b, 'created_at') else None
                }
                for b in bridges
            ],
            "context_tag": "v2_layer_bridges_listed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Layer bridges listing error: {str(e)}")


@app.get("/api/v2/layers/statistics")
@limiter.limit("60/minute")
async def v2_get_layer_statistics(request: Request):
    """
    Get layer management statistics.
    
    Returns: Counts by layer, status, and aggregate metrics
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        layer_manager = get_layer_manager()
        stats = layer_manager.get_layer_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "context_tag": "v2_layer_statistics"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Layer statistics error: {str(e)}")


# verify_csrf inside
@app.post("/api/v2/layers/cascade-validate", dependencies=[Depends(security)])
@limiter.limit("20/minute")
async def v2_cascade_validate(
    thread_id: str,
    request: Request,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Perform cascading validation across all layers for a thread.
    
    Validates L1 → L2 → L3 dependencies and cross-layer consistency.
    """
    verify_csrf_token(token)
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        layer_manager = get_layer_manager()
        validator = get_hierarchy_validator()
        
        bridges = layer_manager.list_bridges(thread_id=thread_id)
        report = await validator.validate_hierarchy(
            bridges=bridges,
            thread_id=thread_id,
            strict_mode=True  # Cascade validation always strict
        )
        
        return {
            "success": True,
            "valid": report.valid,
            "thread_id": thread_id,
            "cascade_result": "PASS" if report.valid else "FAIL",
            "layer_status": report.layer_status,
            "critical_issues": [
                {
                    "layer": issue.layer,
                    "code": issue.code,
                    "message": issue.message
                }
                for issue in report.issues
                if issue.severity.value == "critical"
            ],
            "context_tag": "v2_cascade_validated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cascade validation error: {str(e)}")


# Example quantum endpoint (stub)
# @app.post(  # verify_csrf inside"/quantum/vsa")
# @app.post(  # verify_csrf inside"/quantum/vsa")

# def quantum_vsa_endpoint(...):
#     ...


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
