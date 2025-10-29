"""
main FastAPI app for Aurora CloudBank Symbolic

Exposes endpoints for quantum and geometric algebra modules.

Enhanced with Claude Sonnet 4 capabilities and ChatGPT Agent Mode integration.
"""

from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, WebSocket
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

# Include Cross-Repo Collaboration API routes
try:
    from src.collab.api_routes import router as collab_router
    app.include_router(collab_router)
    print("✅ Cross-Repo Collaboration API routes integrated successfully")
    COLLAB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Cross-Repo Collaboration not available: {e}")
    COLLAB_AVAILABLE = False
except Exception as e:
    print(f"❌ Failed to integrate Cross-Repo Collaboration API routes: {e}")
    COLLAB_AVAILABLE = False

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
async def thread_bridge_status_endpoint():
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
async def thread_bridge_companions_endpoint():
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


# Example quantum endpoint (stub)
# @app.post("/quantum/vsa")
# @app.post("/quantum/vsa")

# def quantum_vsa_endpoint(...):
#     ...
