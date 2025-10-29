"""
main FastAPI app for Aurora CloudBank Symbolic

Exposes endpoints for quantum and geometric algebra modules.

Enhanced with Claude Sonnet 4 capabilities and ChatGPT Agent Mode integration.
"""

from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.sonnet4_integration_hub import enable_sonnet4_globally, sonnet4_hub

# Import ChatGPT Agent Mode integration
from src.integrations.chatgpt_agent_mode import chatgpt_agent_integration

# Import centralized security configuration
from src.middleware.fastapi_security import limiter, require_auth, secure_compare, security

# Import AuMemManager API integration
try:
    from modules.aumemmanager.api_integration import router as aumemmanager_router
    AUMEMMANAGER_AVAILABLE = True
    AUMEMMANAGER_ROUTER = aumemmanager_router
except ImportError:
    print("AuMemManager not available - some memory features disabled")
    AUMEMMANAGER_AVAILABLE = False
    AUMEMMANAGER_ROUTER = None

# Import Data Guardian API integration
try:
    from modules.data_guardian.api import router as data_guardian_router
    DATA_GUARDIAN_AVAILABLE = True
    DATA_GUARDIAN_ROUTER = data_guardian_router
except ImportError:
    print("Data Guardian not available - PII detection/redaction features disabled")
    DATA_GUARDIAN_AVAILABLE = False
    DATA_GUARDIAN_ROUTER = None

# Import Insight Ledger API integration
try:
    from modules.insight_ledger.api import initialize_ledger
    from modules.insight_ledger.api import router as insight_ledger_router
    INSIGHT_LEDGER_AVAILABLE = True
    INSIGHT_LEDGER_ROUTER = insight_ledger_router
except ImportError:
    print("Insight Ledger not available - audit trail features disabled")
    INSIGHT_LEDGER_AVAILABLE = False
    INSIGHT_LEDGER_ROUTER = None
    initialize_ledger = None

# Import Quantum Simulator API integration
try:
    from modules.quantum_simulator.api import router as quantum_simulator_router
    QUANTUM_SIMULATOR_AVAILABLE = True
    QUANTUM_SIMULATOR_ROUTER = quantum_simulator_router
except ImportError:
    print("Quantum Simulator not available - quantum simulation features disabled")
    QUANTUM_SIMULATOR_AVAILABLE = False
    QUANTUM_SIMULATOR_ROUTER = None

# Import Thread Transfer Bridge integration
try:
    from modules.reflective_autonomy.thread_transfer import (
        ThreadTransferBridge,
        get_bridge_instance,
        initialize_bridge
    )
    THREAD_BRIDGE_AVAILABLE = True
except ImportError:
    print("Thread Transfer Bridge not available - cross-thread continuity features disabled")
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
    print("Thread Transfer Bridge v2 not available - distributed/predictive features disabled")
    THREAD_BRIDGE_V2_AVAILABLE = False

# from modules.symbolic_core.quantum_vsa import QuantumVSA  # Uncomment if available

app = FastAPI(
    title="Aurora CloudBank Symbolic API - Sonnet 4 Enhanced",
    description="Quantum-enhanced symbolic governance system with ChatGPT Agent Mode integration",
    version="1.0.0"
)

# Include AuMemManager API routes if available
if AUMEMMANAGER_AVAILABLE and AUMEMMANAGER_ROUTER:
    try:
        app.include_router(AUMEMMANAGER_ROUTER)
        print("✅ AuMemManager API routes integrated successfully")
    except Exception as e:
        print(f"❌ Failed to integrate AuMemManager API routes: {e}")
        AUMEMMANAGER_AVAILABLE = False

# Include Data Guardian API routes if available
if DATA_GUARDIAN_AVAILABLE and DATA_GUARDIAN_ROUTER:
    try:
        app.include_router(DATA_GUARDIAN_ROUTER)
        print("✅ Data Guardian API routes integrated successfully")
    except Exception as e:
        print(f"❌ Failed to integrate Data Guardian API routes: {e}")
        DATA_GUARDIAN_AVAILABLE = False

# Include Insight Ledger API routes if available
if INSIGHT_LEDGER_AVAILABLE and INSIGHT_LEDGER_ROUTER:
    try:
        app.include_router(INSIGHT_LEDGER_ROUTER)
        # Initialize ledger with default storage path
        if initialize_ledger:
            initialize_ledger(storage_path="./data/insight_ledger")
        print("✅ Insight Ledger API routes integrated successfully")
    except Exception as e:
        print(f"❌ Failed to integrate Insight Ledger API routes: {e}")
        INSIGHT_LEDGER_AVAILABLE = False

# Include Quantum Simulator API routes if available
if QUANTUM_SIMULATOR_AVAILABLE and QUANTUM_SIMULATOR_ROUTER:
    try:
        app.include_router(QUANTUM_SIMULATOR_ROUTER)
        print("✅ Quantum Simulator API routes integrated successfully")
    except Exception as e:
        print(f"❌ Failed to integrate Quantum Simulator API routes: {e}")
        QUANTUM_SIMULATOR_AVAILABLE = False

ga = GeometricAlgebra()


def parse_multivector(expression: str, blades: dict):
    """Safely parse a multivector expression."""
    allowed_symbols = set(blades.keys())

    tokens = expression.split()

    for token in tokens:
        if token not in allowed_symbols and not token.isnumeric():
            raise ValueError(f"Invalid token in expression: {token}")
    # Construct the multivector using the blades dictionary
    result = None

    for token in tokens:
        if token in blades:
            result = blades[token] if result is None else result + blades[token]

        elif token.isnumeric():
            result = float(token) if result is None else result + float(token)

    return result


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


@app.post("/geometric/vector")
def create_vector(req: VectorRequest):
    v = ga.blades["e1"] * req.x + ga.blades["e2"] * req.y + ga.blades["e3"] * req.z

    return {"vector": str(v)}


@app.post("/geometric/mult")
def geometric_product(req: MultivectorRequest):
    try:
        a = parse_multivector(req.a, ga.blades)

        b = parse_multivector(req.b, ga.blades)

        result = ga.mult(a, b)

        return {"result": str(result)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/sonnet4/enable")
async def enable_sonnet4(req: Sonnet4EnableRequest = None, token: HTTPAuthorizationCredentials = Depends(security)):
    """Enable Claude Sonnet 4 for all clients or specific client"""
    # CSRF Token validation
    if not token or len(token.credentials) < 10:
        raise HTTPException(status_code=403, detail='Invalid CSRF token')

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable Sonnet 4: {str(e)}")


@app.get("/sonnet4/status")
def get_sonnet4_status():
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
def get_client_sonnet4_status(client_id: str):
    """Get Claude Sonnet 4 status for specific client"""
    return sonnet4_hub.get_client_status(client_id)


@app.get("/health")
def health_check():
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
def health_check_api():
    return health_check()


# ================================
# ChatGPT Agent Mode Endpoints
# ================================

@app.get("/agent/tools")
async def get_agent_tools():
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


@app.post("/agent/execute")
async def execute_agent_tool(request: AgentToolRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Execute agent tool with validated parameters and Aurora symbolic anchoring
    Supports all registered tools: symbolic_processing, geometric_algebra, session_management, system_status
    """
    # CSRF Token validation
    if not token or len(token.credentials) < 10:
        raise HTTPException(status_code=403, detail='Invalid CSRF token')

    try:
        result = await chatgpt_agent_integration.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters,
            session_id=request.session_id
        )
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


@app.post("/agent/session")
async def manage_agent_session(request: AgentSessionRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Manage agent session state and context persistence
    Actions: create, update, get, delete
    """
    # CSRF Token validation
    if not token or len(token.credentials) < 10:
        raise HTTPException(status_code=403, detail='Invalid CSRF token')

    try:
        result = await chatgpt_agent_integration.execute_tool(
            tool_name="session_management",
            parameters={
                "action": request.action,
                "session_id": request.session_id,
                "state_data": request.state_data or {}
            }
        )
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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Session management failed.")


@app.get("/agent/status")
async def get_agent_status():
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
    """
    await websocket.accept()

    try:
        # Send initial connection confirmation with Aurora symbolic anchoring
        initial_message = {
            "type": "connection_established",
            "timestamp": "2025-01-01T00:00:00Z",
            "symbolic_anchor": "EOS_SEED_ORION",
            "ethics_protocol": "Picard_Delta_3",
            "agent_mode": "chatgpt_agent_mode",
            "context_tag": "websocket_agent_stream"
        }
        await websocket.send_json(initial_message)
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            # Process agent requests through WebSocket
            if data.get("type") == "tool_execution":
                try:
                    result = await chatgpt_agent_integration.execute_tool(
                        tool_name=data.get("tool_name"),
                        parameters=data.get("parameters", {}),
                        session_id=data.get("session_id")
                    )
                    await websocket.send_json({
                        "type": "tool_result",
                        "result": result,
                        "request_id": data.get("request_id")
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e),
                        "request_id": data.get("request_id"),
                    })
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": "2025-01-01T00:00:00Z"})
            else:
                await websocket.send_json({
                    "type": "error",
                    "error": "Unknown message type",
                    "supported_types": ["tool_execution", "ping"],
                })

    except Exception as e:
        await websocket.close(code=1000, reason=f"WebSocket error: {str(e)}")


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


@app.post("/api/thread-bridge/handshake")
@limiter.limit("10/minute")
async def thread_bridge_handshake_endpoint(request: HandshakeRequest):
    """
    Initiate handshake sequence with a companion thread
    
    Executes the 5-stage handshake: INIT → VERIFY_ANCHOR → LOCK_DRIFT →
    ALIGN_ETHICS → SYNC_COMPLETE
    """
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


@app.post("/api/thread-bridge/validate")
@limiter.limit("30/minute")
async def thread_bridge_validate_endpoint(request: ValidateRequest):
    """
    Validate continuity between two threads before transfer
    
    Checks anchor alignment, drift levels, and ethics compatibility.
    """
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


@app.post("/api/thread-bridge/transfer")
@limiter.limit("10/minute")
async def thread_bridge_transfer_endpoint(request: TransferRequest):
    """
    Transfer context from source thread to target thread
    
    Performs full validation, ethics checks, and secure state transfer
    between companion threads.
    """
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

@app.post("/api/v2/nodes/register")
@limiter.limit("30/minute")
async def v2_register_node(node_request: NodeRegisterRequest, request: Request):
    """
    Register a new bridge node in the distributed constellation.
    
    Requires: hostname, port, region, capacity, version
    Returns: Node metadata with unique node_id
    """
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


@app.delete("/api/v2/nodes/{node_id}")
@limiter.limit("30/minute")
async def v2_unregister_node(node_id: str, request: Request):
    """
    Unregister a bridge node from the constellation.
    
    Gracefully removes node from registry and load balancing pool.
    """
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


@app.post("/api/v2/consensus/elect")
@limiter.limit("10/minute")
async def v2_trigger_election(request: Request):
    """
    Trigger a Raft consensus leader election.
    
    WARNING: Use only for testing or emergency recovery.
    """
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

@app.post("/api/v2/repos/register")
@limiter.limit("20/minute")
async def v2_register_repository(request: RepositoryRegisterRequest):
    """
    Register a Git repository for cross-repo synchronization.
    
    Enables anchor propagation and thread continuity across repos.
    """
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


@app.post("/api/v2/repos/{repo_id}/sync")
@limiter.limit("10/minute")
async def v2_sync_repository(repo_id: str, direction: str = "bidirectional", request: Request = None):
    """
    Synchronize a registered repository.
    
    Pulls latest changes and pushes local anchors.
    Direction: push, pull, or bidirectional
    """
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


@app.post("/api/v2/bridges/cross-repo")
@limiter.limit("10/minute")
async def v2_create_cross_repo_bridge(source_repo: str, target_repo: str, thread_id: str, request: Request):
    """
    Create a cross-repository bridge for thread continuity.
    
    Initiates 7-stage handshake between repositories.
    """
    if not THREAD_BRIDGE_V2_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Thread Transfer Bridge v2 not available"
        )
    
    try:
        cross_repo_bridge = get_cross_repository_bridge()
        
        result = await cross_repo_bridge.create_bridge(
            source_repo_id=source_repo,
            target_repo_id=target_repo,
            thread_id=thread_id
        )
        
        return {
            "success": result["success"],
            "bridge_id": result.get("bridge_id"),
            "source_repo": source_repo,
            "target_repo": target_repo,
            "thread_id": thread_id,
            "context_tag": "v2_cross_repo_bridge_created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-repo bridge error: {str(e)}")


@app.post("/api/v2/bridges/{bridge_id}/handshake")
@limiter.limit("10/minute")
async def v2_execute_cross_repo_handshake(bridge_id: str, request: Request):
    """
    Execute 7-stage cross-repository handshake.
    
    Completes thread transfer between repositories with full validation.
    """
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

@app.post("/api/v2/drift/predict")
@limiter.limit("30/minute")
async def v2_predict_drift(drift_request: DriftPredictionRequest, request: Request):
    """
    Predict future drift based on current features.
    
    Uses LSTM model with 11-feature input for 24-hour prediction.
    """
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
            "horizon_hours": prediction.horizon_hours,
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


@app.post("/api/v2/drift/observe")
@limiter.limit("60/minute")
async def v2_record_observation(drift: float, request: Request):
    """
    Record a drift observation for pattern analysis.
    
    Adds data point to historical drift tracking.
    """
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
        accuracy = await predictor.get_accuracy_metrics()
        
        return {
            "success": True,
            "accuracy": accuracy,
            "context_tag": "v2_prediction_accuracy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accuracy metrics error: {str(e)}")


@app.post("/api/v2/corrections/apply")
@limiter.limit("10/minute")
async def v2_apply_correction(thread_id: str, predicted_drift: float, current_drift: float, request: Request):
    """
    Apply auto-correction actions based on drift prediction.
    
    Evaluates correction strategies and executes if drift exceeds threshold.
    """
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
                    "description": action.description,
                    "requires_approval": action.requires_manual_approval
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

@app.post("/api/v2/layers/bridge")
@limiter.limit("20/minute")
async def v2_create_layer_bridge(layer_request: LayerBridgeRequest, request: Request):
    """
    Create a multi-layer bridge (L1/L2/L3).
    
    L1: Thread-to-thread (5 stages, 0.0% max drift)
    L2: Repo-to-repo (7 stages, 0.1% max drift)
    L3: Cluster-to-cluster (9 stages, 0.5% max drift, PKI required)
    """
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


@app.post("/api/v2/layers/{bridge_id}/handshake")
@limiter.limit("10/minute")
async def v2_execute_layered_handshake(bridge_id: str, request: Request):
    """
    Execute layer-specific handshake protocol.
    
    Completes all stages for the bridge's layer with proper validation.
    """
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


@app.post("/api/v2/layers/validate")
@limiter.limit("30/minute")
async def v2_validate_hierarchy(thread_id: str, strict_mode: bool = False, request: Request = None):
    """
    Validate multi-layer hierarchy for a thread.
    
    Checks: layer completion, drift tolerance, PKI (L3), dependencies
    """
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


@app.post("/api/v2/layers/cascade-validate")
@limiter.limit("20/minute")
async def v2_cascade_validate(thread_id: str, request: Request):
    """
    Perform cascading validation across all layers for a thread.
    
    Validates L1 → L2 → L3 dependencies and cross-layer consistency.
    """
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
# @app.post("/quantum/vsa")
# @app.post("/quantum/vsa")

# def quantum_vsa_endpoint(...):
#     ...


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
