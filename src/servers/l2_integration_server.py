#!/usr/bin/env python3
"""Authoritative FastAPI runtime for the Aurora mesh workspace."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mesh.models import MeshMessageRequest
from src.mesh.runtime import ORION_CORE, MeshRuntime, utcnow


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def activation_phrase(agent_id: str) -> str:
    """Return the expected compatibility activation phrase for an agent."""

    return f"ORION_{agent_id.upper()}_RELAY_ACTIVATE//"


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

    app = FastAPI(
        title="Aurora Mesh Router Runtime",
        description="Local-first collaboration runtime for the Aurora mesh workspace",
        version=ORION_CORE["version"],
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )
    app.state.runtime = runtime
    app.state.server_state = {
        "start_time": datetime.now(),
        "requests_count": 0,
        "version": ORION_CORE["version"],
    }

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def track_requests(request: Request, call_next):
        app.state.server_state["requests_count"] += 1
        return await call_next(request)

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
    async def mesh_activate(agent_id: str) -> Dict[str, Any]:
        try:
            agent = runtime.activate_agent(agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"success": True, "agent": agent, "server_info": build_server_info(app)}

    @app.post("/api/mesh/messages")
    async def mesh_send(request_data: MeshMessageRequest) -> Dict[str, Any]:
        try:
            result = await runtime.send_message(request_data)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {**result, "server_info": build_server_info(app)}

    @app.get("/api/mesh/channels/{channel_id:path}/history")
    async def mesh_history(channel_id: str, limit: int = Query(default=100, ge=1, le=500)) -> Dict[str, Any]:
        history = runtime.get_channel_history(channel_id, limit=limit)
        return {**history, "channel_id": channel_id, "server_info": build_server_info(app)}

    @app.get("/api/mesh/events")
    async def mesh_events(after: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=500)) -> Dict[str, Any]:
        events = runtime.get_events_after(after=after, limit=limit)
        return {**events, "server_info": build_server_info(app)}

    @app.websocket("/ws/mesh")
    async def mesh_socket(websocket: WebSocket) -> None:
        await runtime.websocket_hub.connect(websocket)
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
    async def aurora_initialize() -> Dict[str, Any]:
        activated = [runtime.activate_agent(agent["agent_id"]) for agent in runtime.list_agents()]
        return {"success": True, "agents": activated, "server_info": build_server_info(app)}

    @app.post("/api/aurora/command")
    async def aurora_command(request_data: Dict[str, Any]) -> Dict[str, Any]:
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
    async def bridge_connect(agent_id: str, request_data: Dict[str, Any]) -> JSONResponse:
        try:
            agent = runtime.get_agent(agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        phrase = request_data.get("activationPhrase")
        expected_phrase = activation_phrase(agent["agent_id"])
        if phrase and phrase != expected_phrase:
            raise HTTPException(status_code=401, detail="Invalid activation phrase")

        activated = runtime.activate_agent(agent["agent_id"])
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
                "handshake": handshake,
                "constellation": [agent["agent_id"] for agent in runtime.list_agents()],
                "server_info": build_server_info(app),
            }
        )

    @app.post("/api/bridge/gpt/message/{agent_id}")
    async def bridge_message(agent_id: str, request_data: Dict[str, Any]) -> JSONResponse:
        message = request_data.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="Missing message content")
        target = request_data.get("target", "Aurora")
        message_type = request_data.get("type", "direct")
        try:
            result = await runtime.inject_agent_message(agent_id, target, message, message_type)
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
    async def bridge_status() -> JSONResponse:
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
    async def bridge_agent_status(agent_id: str) -> JSONResponse:
        try:
            return JSONResponse(runtime.get_agent(agent_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/bridge/gpt/heartbeat/{agent_id}")
    async def bridge_heartbeat(agent_id: str) -> JSONResponse:
        try:
            agent = runtime.heartbeat(agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return JSONResponse({"success": True, "agent_id": agent["agent_id"], "heartbeat": utcnow(), "status": agent["status"]})

    @app.post("/api/bridge/gpt/disconnect/{agent_id}")
    async def bridge_disconnect(agent_id: str) -> JSONResponse:
        try:
            agent = runtime.disconnect_agent(agent_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return JSONResponse({"success": True, "agent_id": agent["agent_id"], "status": agent["status"]})

    @app.get("/api/agents")
    async def list_agents() -> Dict[str, Any]:
        agents = runtime.list_agents()
        return {"agents": agents, "total": len(agents)}

    @app.get("/api/orion-core")
    async def orion_core() -> Dict[str, Any]:
        return {
            "orion_core": ORION_CORE,
            "activation_phrases": {agent["agent_id"]: activation_phrase(agent["agent_id"]) for agent in runtime.list_agents()},
            "server_version": build_server_info(app)["version"],
        }

    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info("Aurora Mesh Router runtime starting")

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        logger.info("Aurora Mesh Router runtime shutting down")

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
