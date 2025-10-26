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

# Example quantum endpoint (stub)
# @app.post("/quantum/vsa")
# @app.post("/quantum/vsa")

# def quantum_vsa_endpoint(...):
#     ...
