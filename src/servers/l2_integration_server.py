#!/usr/bin/env python3
"""Authoritative FastAPI runtime for the Aurora mesh workspace."""

from __future__ import annotations

import argparse
from contextlib import asynccontextmanager
import json
import logging
import os
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mesh.models import MeshMessageRequest
from src.mesh.runtime import ORION_CORE, MeshRuntime, utcnow


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

LOOPBACK_CLIENT_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}


def parse_allowed_origins(raw_value: Optional[str]) -> list[str]:
    """Return an explicit origin allowlist for browser clients."""

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


def activation_phrase(agent_id: str) -> str:
    """Return the expected compatibility activation phrase for an agent."""

    return f"ORION_{agent_id.upper()}_RELAY_ACTIVATE//"


def activation_phrase_env_key(agent_id: str) -> str:
    """Return the environment variable name for an agent activation phrase override."""

    normalized = "".join(character if character.isalnum() else "_" for character in agent_id.upper())
    return f"AURORA_BRIDGE_{normalized}_ACTIVATION_PHRASE"


def normalize_client_host(client_host: Optional[str]) -> str:
    """Normalize a client host so local/remote checks are consistent."""

    if not client_host:
        return ""
    lowered = client_host.strip().lower()
    if lowered.startswith("::ffff:"):
        lowered = lowered.split("::ffff:", 1)[1]
    return lowered


def is_loopback_client(client_host: Optional[str], allowed_hosts: set[str]) -> bool:
    """Return True when the client host is considered local-only."""

    return normalize_client_host(client_host) in allowed_hosts


def extract_bearer_token(raw_header: Optional[str]) -> str:
    """Read a bearer token from an Authorization header."""

    if not isinstance(raw_header, str) or not raw_header.strip():
        return ""
    parts = raw_header.strip().split(" ", 1)
    if len(parts) != 2 or parts[0] != "Bearer" or not parts[1].strip():
        return ""
    return parts[1].strip()


def extract_bridge_session_token(request: Request) -> str:
    """Read a bridge session token from headers."""

    bearer_token = extract_bearer_token(request.headers.get("Authorization"))
    if bearer_token:
        return bearer_token
    header_token = request.headers.get("X-Aurora-Bridge-Session", "")
    return header_token.strip()


def load_html(path: Path) -> str:
    """Read an HTML asset from disk."""

    return path.read_text(encoding="utf-8")


def build_server_info(app: FastAPI) -> Dict[str, Any]:
    """Build common server metadata."""

    state = app.state.server_state
    uptime = (datetime.now() - state["start_time"]).total_seconds()
    return {
        "uptime": uptime,
        "requests_count": state["requests_count"],
        "version": state["version"],
        "timestamp": utcnow(),
    }


def create_app(project_root: Optional[Path] = None) -> FastAPI:
    """Create a configured FastAPI mesh runtime app."""

    root = project_root or PROJECT_ROOT
    runtime = MeshRuntime(root)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.server_state["start_time"] = datetime.now()
        app.state.server_state["requests_count"] = 0
        app.state.bridge_sessions.clear()
        logger.info("Aurora Mesh Router runtime starting")
        try:
            yield
        finally:
            app.state.bridge_sessions.clear()
            runtime.websocket_hub.clear()
            logger.info("Aurora Mesh Router runtime shutting down")

    app = FastAPI(
        title="Aurora Mesh Router Runtime",
        description="Local-first collaboration runtime for the Aurora mesh workspace",
        version=ORION_CORE["version"],
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )
    app.state.runtime = runtime
    app.state.server_state = {
        "start_time": datetime.now(),
        "requests_count": 0,
        "version": ORION_CORE["version"],
    }
    app.state.loopback_client_hosts = {normalize_client_host(host) for host in LOOPBACK_CLIENT_HOSTS}
    app.state.mesh_control_token = os.getenv("AURORA_MESH_CONTROL_TOKEN", "").strip()
    app.state.bridge_activation_phrases = {
        agent["agent_id"]: os.getenv(activation_phrase_env_key(agent["agent_id"]), "").strip()
        for agent in runtime.list_agents()
    }
    app.state.bridge_sessions: Dict[str, str] = {}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=parse_allowed_origins(os.getenv("AURORA_ALLOWED_ORIGINS")),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def track_requests(request: Request, call_next):
        app.state.server_state["requests_count"] += 1
        return await call_next(request)

    def require_control_access(request: Request) -> None:
        """Allow local control requests and require a bearer token for remote ones."""

        client_host = request.client.host if request.client else None
        if is_loopback_client(client_host, app.state.loopback_client_hosts):
            return

        expected_token = app.state.mesh_control_token
        if not expected_token:
            raise HTTPException(status_code=403, detail="Remote control routes require AURORA_MESH_CONTROL_TOKEN")

        provided_token = extract_bearer_token(request.headers.get("Authorization"))
        if not provided_token:
            raise HTTPException(status_code=401, detail="Missing mesh control token")

        if not secrets.compare_digest(provided_token, expected_token):
            raise HTTPException(status_code=401, detail="Invalid mesh control token")

    def resolve_bridge_activation_phrase(agent_id: str) -> tuple[str, bool]:
        """Return the expected activation phrase and whether it was explicitly configured."""

        configured_phrase = app.state.bridge_activation_phrases.get(agent_id, "")
        if configured_phrase:
            return configured_phrase, True
        return activation_phrase(agent_id), False

    def require_bridge_session(agent_id: str, request: Request) -> str:
        """Require a valid per-agent bridge session token."""

        try:
            agent = runtime.get_agent(agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        canonical_agent_id = agent["agent_id"]
        expected_token = app.state.bridge_sessions.get(canonical_agent_id, "")
        if not expected_token:
            raise HTTPException(status_code=404, detail="Agent not connected")

        provided_token = extract_bridge_session_token(request)
        if not provided_token:
            raise HTTPException(status_code=401, detail="Missing bridge session token")

        if not secrets.compare_digest(provided_token, expected_token):
            raise HTTPException(status_code=401, detail="Invalid bridge session token")

        return canonical_agent_id

    async def allow_mesh_socket(websocket: WebSocket) -> bool:
        """Restrict live socket access to local clients."""

        client_host = websocket.client.host if websocket.client else None
        if is_loopback_client(client_host, app.state.loopback_client_hosts):
            await runtime.websocket_hub.connect(websocket)
            return True

        await websocket.close(code=1008, reason="Remote WebSocket access is disabled")
        return False

    dashboard_path = root / "src" / "dashboard" / "agent_constellation.html"
    chamber_path = root / "src" / "interfaces" / "aurora_collaboration_chamber.html"

    @app.get("/", response_class=HTMLResponse)
    async def dashboard() -> HTMLResponse:
        return HTMLResponse(load_html(dashboard_path))

    @app.get("/chamber", response_class=HTMLResponse)
    async def chamber() -> HTMLResponse:
        return HTMLResponse(load_html(chamber_path))

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        status = runtime.get_status()
        return {
            "status": "healthy",
            "server": build_server_info(app),
            "mesh_status": status["mesh_status"],
            "event_cursor": status["event_cursor"],
            "live_adapter_available": status["live_adapter"]["available"],
        }

    @app.get("/api/mesh/status")
    async def mesh_status() -> Dict[str, Any]:
        return {**runtime.get_status(), "server_info": build_server_info(app)}

    @app.get("/api/mesh/agents")
    async def mesh_agents() -> Dict[str, Any]:
        agents = runtime.list_agents()
        return {"agents": agents, "total": len(agents), "server_info": build_server_info(app)}

    @app.get("/api/mesh/agents/{agent_id}")
    async def mesh_agent(agent_id: str) -> Dict[str, Any]:
        try:
            return runtime.get_agent(agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/mesh/agents/{agent_id}/activate")
    async def mesh_activate(agent_id: str, _: None = Depends(require_control_access)) -> Dict[str, Any]:
        try:
            agent = runtime.activate_agent(agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"success": True, "agent": agent, "server_info": build_server_info(app)}

    @app.post("/api/mesh/messages")
    async def mesh_send(request_data: MeshMessageRequest, _: None = Depends(require_control_access)) -> Dict[str, Any]:
        try:
            result = await runtime.send_message(request_data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {**result, "server_info": build_server_info(app)}

    @app.get("/api/mesh/channels/{channel_id:path}/history")
    async def mesh_history(
        channel_id: str,
        limit: int = Query(default=100, ge=1, le=500),
        _: None = Depends(require_control_access),
    ) -> Dict[str, Any]:
        history = runtime.get_channel_history(channel_id, limit=limit)
        return {**history, "channel_id": channel_id, "server_info": build_server_info(app)}

    @app.get("/api/mesh/events")
    async def mesh_events(
        after: int = Query(default=0, ge=0),
        limit: int = Query(default=100, ge=1, le=500),
        _: None = Depends(require_control_access),
    ) -> Dict[str, Any]:
        events = runtime.get_events_after(after=after, limit=limit)
        return {**events, "server_info": build_server_info(app)}

    @app.websocket("/ws/mesh")
    async def mesh_socket(websocket: WebSocket) -> None:
        if not await allow_mesh_socket(websocket):
            return
        await websocket.send_json(
            {
                "event_id": runtime.store.last_event_id(),
                "event_type": "trace_update",
                "message_id": "system",
                "channel_id": "system",
                "agent_id": None,
                "timestamp": utcnow(),
                "payload": {
                    "phase": "socket_connected",
                    "detail": "Mesh WebSocket connected",
                    "event_cursor": runtime.store.last_event_id(),
                },
            }
        )
        try:
            while True:
                message = await websocket.receive_text()
                if message.strip().lower() == "ping":
                    await websocket.send_json(
                        {
                            "event_id": runtime.store.last_event_id(),
                            "event_type": "trace_update",
                            "message_id": "system",
                            "channel_id": "system",
                            "agent_id": None,
                            "timestamp": utcnow(),
                            "payload": {"phase": "pong", "detail": "Mesh WebSocket heartbeat"},
                        }
                    )
        except WebSocketDisconnect:
            await runtime.websocket_hub.disconnect(websocket)

    @app.get("/api/aurora/status")
    async def aurora_status() -> Dict[str, Any]:
        return {
            "available": True,
            "runtime": "mesh_router_v1",
            "mesh": runtime.get_status(),
            "server_info": build_server_info(app),
        }

    @app.post("/api/aurora/initialize")
    async def aurora_initialize(_: None = Depends(require_control_access)) -> Dict[str, Any]:
        activated = [runtime.activate_agent(agent["agent_id"]) for agent in runtime.list_agents()]
        return {"success": True, "agents": activated, "server_info": build_server_info(app)}

    @app.post("/api/aurora/command")
    async def aurora_command(request_data: Dict[str, Any], _: None = Depends(require_control_access)) -> Dict[str, Any]:
        command = request_data.get("command", {})
        context = request_data.get("context", {})
        if isinstance(command, dict):
            content = command.get("content") or command.get("message") or json.dumps(command, sort_keys=True)
        else:
            content = str(command)
        target = context.get("to", "alex_thorne")
        payload = MeshMessageRequest(
            to=target,
            channel=context.get("channel"),
            content=content,
            sender_id=context.get("sender_id", "aurora"),
            sender_name=context.get("sender_name", "Aurora"),
            type=context.get("type", "direct"),
        )
        result = await runtime.send_message(payload)
        return {"success": True, "result": result, "server_info": build_server_info(app)}

    @app.post("/api/bridge/gpt/connect/{agent_id}")
    async def bridge_connect(agent_id: str, request_data: Dict[str, Any], request: Request) -> JSONResponse:
        try:
            agent = runtime.get_agent(agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        phrase = request_data.get("activationPhrase")
        expected_phrase, explicitly_configured = resolve_bridge_activation_phrase(agent["agent_id"])
        client_host = request.client.host if request.client else None
        if not explicitly_configured and not is_loopback_client(client_host, app.state.loopback_client_hosts):
            raise HTTPException(
                status_code=503,
                detail=f"Remote bridge activation requires {activation_phrase_env_key(agent['agent_id'])}",
            )
        if not isinstance(phrase, str) or not phrase.strip():
            raise HTTPException(status_code=401, detail="Missing activation phrase")
        if not secrets.compare_digest(phrase, expected_phrase):
            raise HTTPException(status_code=401, detail="Invalid activation phrase")

        activated = runtime.activate_agent(agent["agent_id"])
        session_token = secrets.token_urlsafe(32)
        app.state.bridge_sessions[activated["agent_id"]] = session_token
        handshake = {
            "success": True,
            "sequence": ["ZIPWIZ_BEACON", "ANCHOR_SYNC", "ETHICS_AUDIT", "DRIFT_VALIDATION"],
            "log": [
                {"step": "ZIPWIZ_BEACON", "result": {"success": True}, "timestamp": utcnow()},
                {"step": "ANCHOR_SYNC", "result": {"success": True}, "timestamp": utcnow()},
                {"step": "ETHICS_AUDIT", "result": {"success": True}, "timestamp": utcnow()},
                {"step": "DRIFT_VALIDATION", "result": {"success": True, "drift": 0.0}, "timestamp": utcnow()},
            ],
            "driftLock": 0.0,
        }
        return JSONResponse(
            {
                "success": True,
                "agentId": activated["agent_id"],
                "status": "connected",
                "sessionToken": session_token,
                "handshake": handshake,
                "constellation": [agent["agent_id"] for agent in runtime.list_agents()],
                "server_info": build_server_info(app),
            }
        )

    @app.post("/api/bridge/gpt/message/{agent_id}")
    async def bridge_message(
        agent_id: str,
        request_data: Dict[str, Any],
        connected_agent_id: str = Depends(require_bridge_session),
    ) -> JSONResponse:
        message = request_data.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="Missing message content")
        target = request_data.get("target", "Aurora")
        message_type = request_data.get("type", "direct")
        try:
            result = await runtime.inject_agent_message(connected_agent_id, target, message, message_type)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return JSONResponse(
            {
                "success": True,
                "messageId": result["message_id"],
                "relayStatus": result["relay_status"],
                "channelId": result["channel_id"],
                "timestamp": utcnow(),
            }
        )

    @app.get("/api/bridge/constellation/status")
    async def bridge_status(_: None = Depends(require_control_access)) -> JSONResponse:
        mesh = runtime.get_status()
        active_agents = runtime.list_agents()
        return JSONResponse(
            {
                "constellation": "L2_META_AGENTS",
                "version": mesh["version"],
                "total_agents": mesh["total_agents"],
                "totalAgents": mesh["total_agents"],
                "connected_agents": mesh["active_agents"],
                "connectedAgents": mesh["active_agents"],
                "active_agents": active_agents,
                "activeAgents": active_agents,
                "meshStatus": mesh["mesh_status"],
                "orion_core": mesh["orion_core"],
                "server_info": build_server_info(app),
            }
        )

    @app.get("/api/bridge/gpt/status/{agent_id}")
    async def bridge_agent_status(agent_id: str, connected_agent_id: str = Depends(require_bridge_session)) -> JSONResponse:
        try:
            return JSONResponse(runtime.get_agent(connected_agent_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/bridge/gpt/heartbeat/{agent_id}")
    async def bridge_heartbeat(agent_id: str, connected_agent_id: str = Depends(require_bridge_session)) -> JSONResponse:
        try:
            agent = runtime.heartbeat(connected_agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return JSONResponse({"success": True, "agent_id": agent["agent_id"], "heartbeat": utcnow(), "status": agent["status"]})

    @app.post("/api/bridge/gpt/disconnect/{agent_id}")
    async def bridge_disconnect(agent_id: str, connected_agent_id: str = Depends(require_bridge_session)) -> JSONResponse:
        try:
            agent = runtime.disconnect_agent(connected_agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        app.state.bridge_sessions.pop(agent["agent_id"], None)
        return JSONResponse({"success": True, "agent_id": agent["agent_id"], "status": agent["status"]})

    @app.get("/api/agents")
    async def list_agents() -> Dict[str, Any]:
        agents = runtime.list_agents()
        return {"agents": agents, "total": len(agents)}

    @app.get("/api/orion-core")
    async def orion_core() -> Dict[str, Any]:
        return {
            "orion_core": ORION_CORE,
            "activation_phrase_required": True,
            "supported_agents": [agent["agent_id"] for agent in runtime.list_agents()],
            "server_version": build_server_info(app)["version"],
        }

    return app


app = create_app()


def main() -> None:
    """Run the mesh runtime with uvicorn."""

    parser = argparse.ArgumentParser(description="Aurora Mesh Router Runtime")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    args = parser.parse_args()

    print("=" * 60)
    print("AURORA MESH ROUTER RUNTIME")
    print("=" * 60)
    print(f"Dashboard: http://{args.host}:{args.port}")
    print(f"Chamber:   http://{args.host}:{args.port}/chamber")
    print(f"Docs:      http://{args.host}:{args.port}/api/docs")
    print("=" * 60)
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload, log_level=args.log_level)


if __name__ == "__main__":
    main()
