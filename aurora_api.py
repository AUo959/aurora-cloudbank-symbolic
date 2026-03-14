"""
main FastAPI app for Aurora CloudBank Symbolic


Exposes endpoints for quantum and geometric algebra modules.


Enhanced with Claude Sonnet 4 capabilities and ChatGPT Agent Mode integration.
"""

import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.sonnet4_integration_hub import (
    enable_sonnet4_globally,
    sonnet4_hub,
)

# Import ChatGPT Agent Mode integration
from src.integrations.chatgpt_agent_mode import chatgpt_agent_integration
from src.integrations.mcp_shuttle_bay import mcp_shuttle_bay

# from modules.symbolic_core.quantum_vsa import QuantumVSA  # Uncomment if available

app = FastAPI(
    title="Aurora CloudBank Symbolic API - Sonnet 4 Enhanced",
    description="Quantum-enhanced symbolic governance system with ChatGPT Agent Mode integration",
    version="1.0.0",
)


def parse_allowed_origins(raw_value: Optional[str]) -> List[str]:
    if raw_value:
        configured = [origin.strip().rstrip("/") for origin in raw_value.split(",") if origin.strip() and origin.strip() != "*"]
        if configured:
            return configured
    return [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_allowed_origins(os.getenv("AURORA_ALLOWED_ORIGINS")),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

LOOPBACK_CLIENT_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}

app.state.loopback_client_hosts = set(LOOPBACK_CLIENT_HOSTS)
app.state.agent_control_token = os.getenv("AURORA_AGENT_CONTROL_TOKEN", "").strip()


ga = GeometricAlgebra()


def normalize_client_host(host: Optional[str]) -> str:
    return (host or "").split("%", 1)[0].lower()


def is_loopback_client(host: Optional[str], allowed_hosts: List[str]) -> bool:
    return normalize_client_host(host) in {normalize_client_host(item) for item in allowed_hosts}


def extract_bearer_token(value: Optional[str]) -> str:
    if not value:
        return ""
    parts = value.strip().split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return ""


def token_matches(expected: str, actual: str) -> bool:
    return bool(expected and actual and secrets.compare_digest(expected, actual))


def require_agent_control_access(request: Request) -> None:
    client_host = request.client.host if request.client else ""
    if is_loopback_client(client_host, list(app.state.loopback_client_hosts)):
        return

    expected_token = getattr(app.state, "agent_control_token", "")
    presented_token = extract_bearer_token(request.headers.get("Authorization"))
    if not expected_token:
        raise HTTPException(status_code=403, detail="Remote agent routes require AURORA_AGENT_CONTROL_TOKEN")
    if not token_matches(expected_token, presented_token):
        raise HTTPException(status_code=401, detail="Agent control token required")


async def allow_agent_websocket(websocket: WebSocket) -> None:
    client_host = websocket.client.host if websocket.client else ""
    if is_loopback_client(client_host, list(app.state.loopback_client_hosts)):
        return

    expected_token = getattr(app.state, "agent_control_token", "")
    presented_token = extract_bearer_token(websocket.headers.get("authorization"))
    if not presented_token:
        presented_token = (websocket.query_params.get("token") or "").strip()

    if not expected_token:
        await websocket.close(code=1008, reason="Remote agent WebSocket requires AURORA_AGENT_CONTROL_TOKEN")
        raise RuntimeError("Remote agent WebSocket requires AURORA_AGENT_CONTROL_TOKEN")
    if not token_matches(expected_token, presented_token):
        await websocket.close(code=1008, reason="Agent WebSocket access denied")
        raise RuntimeError("Agent WebSocket access denied")


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


# ================================
# ChatGPT Agent Mode Endpoints
# ================================


def build_agent_stream_message() -> Dict[str, Any]:
    return {
        "type": "connection_established",
        "timestamp": "2025-01-01T00:00:00Z",
        "symbolic_anchor": "EOS_SEED_ORION",
        "ethics_protocol": "Picard_Delta_3",
        "agent_mode": "chatgpt_agent_mode",
        "context_tag": "websocket_agent_stream",
    }


async def execute_session_action(request: AgentSessionRequest) -> Dict[str, Any]:
    return await chatgpt_agent_integration.execute_tool(
        tool_name="session_management",
        parameters={
            "action": request.action,
            "session_id": request.session_id,
            "state_data": request.state_data or {},
        },
    )


def build_jsonrpc_result(request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def build_jsonrpc_error(request_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


async def handle_mcp_rpc_request(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return build_jsonrpc_error(None, -32600, "Invalid Request")

    request_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params") or {}

    if payload.get("jsonrpc") != "2.0" or not method:
        return build_jsonrpc_error(request_id, -32600, "Invalid Request")

    if method == "notifications/initialized":
        return None

    try:
        if method == "initialize":
            result = await mcp_shuttle_bay.get_mcp_server_descriptor()
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = await mcp_shuttle_bay.list_mcp_tools()
        elif method == "tools/call":
            result = await mcp_shuttle_bay.call_mcp_tool(
                tool_name=params.get("name", ""),
                arguments=params.get("arguments") or {},
                session_id=params.get("session_id"),
            )
        elif method == "resources/list":
            result = await mcp_shuttle_bay.list_mcp_resources()
        elif method == "resources/read":
            result = await mcp_shuttle_bay.read_mcp_resource(params.get("uri", ""))
        else:
            return build_jsonrpc_error(request_id, -32601, f"Method not found: {method}")
    except ValueError as e:
        return build_jsonrpc_error(request_id, -32602, str(e))
    except HTTPException as e:
        return build_jsonrpc_error(request_id, -32000, e.detail)
    except Exception as e:
        return build_jsonrpc_error(request_id, -32000, str(e))

    if request_id is None:
        return None

    return build_jsonrpc_result(request_id, result)


@app.post("/sonnet4/enable")
async def enable_sonnet4(req: Sonnet4EnableRequest = None, _: None = Depends(require_agent_control_access)):
    """Enable Claude Sonnet 4 for all clients or specific client"""
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
def get_sonnet4_status(_: None = Depends(require_agent_control_access)):
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
def get_client_sonnet4_status(client_id: str, _: None = Depends(require_agent_control_access)):
    """Get Claude Sonnet 4 status for specific client"""
    return sonnet4_hub.get_client_status(client_id)


@app.get("/agent/tools")
async def get_agent_tools(_: None = Depends(require_agent_control_access)):
    """
    Discover available agent tools and capabilities for ChatGPT Agent Mode
    Returns OpenAPI-compatible tool definitions
    """
    try:
        tools_info = await chatgpt_agent_integration.discover_tools()
        return JSONResponse(content=tools_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to discover tools: {str(e)}")


@app.post("/agent/execute")
async def execute_agent_tool(request: AgentToolRequest, _: None = Depends(require_agent_control_access)):
    """
    Execute agent tool with validated parameters and Aurora symbolic anchoring
    Supports all registered tools: symbolic_processing, geometric_algebra, session_management, system_status
    """
    try:
        result = await chatgpt_agent_integration.execute_tool(
            tool_name=request.tool_name, parameters=request.parameters, session_id=request.session_id
        )
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


@app.post("/agent/session")
async def manage_agent_session(request: AgentSessionRequest, _: None = Depends(require_agent_control_access)):
    """
    Manage agent session state and context persistence
    Actions: create, update, get, delete
    """
    try:
        return JSONResponse(content=await execute_session_action(request))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session management failed: {str(e)}")


@app.get("/agent/status")
async def get_agent_status(_: None = Depends(require_agent_control_access)):
    """Get current agent system status and health information"""
    try:
        status = await chatgpt_agent_integration.get_agent_status()
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@app.get("/mcp/shuttle-bay")
async def get_mcp_shuttle_bay_manifest(_: None = Depends(require_agent_control_access)):
    """Expose the structured shuttle-bay manifest for Aurora MCP-style integrations."""
    try:
        manifest = await mcp_shuttle_bay.get_manifest()
        return JSONResponse(content=manifest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load shuttle-bay manifest: {str(e)}")


@app.get("/mcp/shuttle-bay/tools")
async def get_mcp_shuttle_bay_tools(_: None = Depends(require_agent_control_access)):
    """Return the shuttle-bay tool catalog backed by the agent-mode registry."""
    try:
        tools_info = await mcp_shuttle_bay.discover_tools()
        return JSONResponse(content=tools_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to discover shuttle-bay tools: {str(e)}")


@app.post("/mcp/shuttle-bay/execute")
async def execute_mcp_shuttle_bay_tool(request: AgentToolRequest, _: None = Depends(require_agent_control_access)):
    """Execute a shuttle-bay tool invocation against Aurora's agent runtime."""
    try:
        result = await mcp_shuttle_bay.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters,
            session_id=request.session_id,
        )
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shuttle-bay execution failed: {str(e)}")


@app.post("/mcp/shuttle-bay/session")
async def manage_mcp_shuttle_bay_session(
    request: AgentSessionRequest,
    _: None = Depends(require_agent_control_access),
):
    """Mirror agent session lifecycle controls through the shuttle-bay surface."""
    try:
        result = await mcp_shuttle_bay.manage_session(
            action=request.action,
            session_id=request.session_id,
            state_data=request.state_data,
        )
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shuttle-bay session management failed: {str(e)}")


@app.get("/mcp/shuttle-bay/status")
async def get_mcp_shuttle_bay_status(_: None = Depends(require_agent_control_access)):
    """Return combined agent runtime and bridge metadata for shuttle-bay health checks."""
    try:
        status = await mcp_shuttle_bay.get_status()
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get shuttle-bay status: {str(e)}")


@app.get("/mcp")
async def get_mcp_endpoint_info(_: None = Depends(require_agent_control_access)):
    """Human-readable MCP endpoint summary for local inspection."""
    descriptor = await mcp_shuttle_bay.get_mcp_server_descriptor()
    descriptor["transport"] = {
        "endpoint": "/mcp",
        "methods": ["initialize", "ping", "tools/list", "tools/call", "resources/list", "resources/read"],
    }
    return JSONResponse(content=descriptor)


@app.post("/mcp")
async def mcp_rpc_endpoint(request: Request, _: None = Depends(require_agent_control_access)):
    """Minimal JSON-RPC MCP surface backed by the shuttle-bay adapter."""
    payload = await request.json()

    if isinstance(payload, list):
        responses = []
        for item in payload:
            response = await handle_mcp_rpc_request(item)
            if response is not None:
                responses.append(response)
        if not responses:
            return Response(status_code=202)
        return JSONResponse(content=responses)

    response = await handle_mcp_rpc_request(payload)
    if response is None:
        return Response(status_code=202)
    return JSONResponse(content=response)


@app.websocket("/agent/stream")
async def agent_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent communication
    Supports streaming responses and persistent connections
    """
    try:
        await allow_agent_websocket(websocket)
    except RuntimeError:
        return
    await websocket.accept()

    try:
        await websocket.send_json(build_agent_stream_message())

        while True:
            data = await websocket.receive_json()

            if data.get("type") == "tool_execution":
                try:
                    result = await chatgpt_agent_integration.execute_tool(
                        tool_name=data.get("tool_name"),
                        parameters=data.get("parameters", {}),
                        session_id=data.get("session_id"),
                    )
                    await websocket.send_json(
                        {"type": "tool_result", "result": result, "request_id": data.get("request_id")}
                    )
                except Exception as e:
                    await websocket.send_json({"type": "error", "error": str(e), "request_id": data.get("request_id")})
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": "2025-01-01T00:00:00Z"})
            else:
                await websocket.send_json(
                    {"type": "error", "error": "Unknown message type", "supported_types": ["tool_execution", "ping"]}
                )

    except Exception as e:
        await websocket.close(code=1000, reason=f"WebSocket error: {str(e)}")
