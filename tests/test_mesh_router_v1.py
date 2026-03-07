"""Tests for the Mesh Router V1 runtime and API surface."""

from __future__ import annotations

import asyncio
import json
import shutil
import time
from pathlib import Path
from urllib.parse import quote

import pytest

from src.mesh.models import MeshMessageRequest
from src.mesh.runtime import MeshRuntime

try:
    from fastapi.testclient import TestClient
    from src.servers.l2_integration_server import PROJECT_ROOT, create_app

    FASTAPI_AVAILABLE = True
except ModuleNotFoundError:
    TestClient = None
    create_app = None
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    FASTAPI_AVAILABLE = False


def copy_mesh_project(tmp_path: Path) -> Path:
    """Copy the mesh config and UI assets into a disposable project root."""

    for relative in ["config/mesh", "src/dashboard", "src/interfaces"]:
        source = PROJECT_ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, dirs_exist_ok=True)

    for manifest_path in (tmp_path / "config" / "mesh" / "agents").glob("*.json"):
        manifest = json.loads(manifest_path.read_text())
        manifest["typing_profile"]["delay_ms"] = 5
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    return tmp_path


def test_alias_resolution_and_live_fallback(tmp_path: Path) -> None:
    """Alex should resolve by alias and fall back deterministically when live mode is unavailable."""

    project_root = copy_mesh_project(tmp_path)
    runtime = MeshRuntime(project_root)

    async def scenario():
        result = await runtime.send_message(
            MeshMessageRequest(to="Alex Thorne", content="Need a routing decision before the next checkpoint.")
        )
        await asyncio.sleep(0.08)
        history = runtime.get_channel_history("private:captain:alex")["events"]
        return result, history

    result, history = asyncio.run(scenario())
    assert result["status"] == "accepted"
    event_types = [event["event_type"] for event in history]
    assert event_types[:6] == [
        "message_accepted",
        "trace_update",
        "agent_ack",
        "agent_typing",
        "trace_update",
        "agent_reply",
    ]

    reply = next(event for event in history if event["event_type"] == "agent_reply")
    assert reply["agent_id"] == "alex_thorne"
    assert reply["payload"]["mode"] == "deterministic_fallback"

    trace = [event for event in history if event["event_type"] == "trace_update"]
    assert any("Live adapter unavailable" in event["payload"].get("detail", "") for event in trace)


def test_broadcast_routes_to_all_channel_agents(tmp_path: Path) -> None:
    """Broadcasts should reach all agents subscribed to the channel."""

    project_root = copy_mesh_project(tmp_path)
    runtime = MeshRuntime(project_root)

    async def scenario():
        result = await runtime.send_message(
            MeshMessageRequest(channel="#crew_lounge", content="Stand up in ten minutes.", type="broadcast")
        )
        await asyncio.sleep(0.12)
        history = runtime.get_channel_history("#crew_lounge")["events"]
        return result, history

    result, history = asyncio.run(scenario())
    assert sorted(result["targets"]) == [
        "alex_thorne",
        "archy",
        "liora",
        "oppy",
        "riverthread_808",
        "starling_au",
    ]
    reply_agents = sorted({event["agent_id"] for event in history if event["event_type"] == "agent_reply"})
    assert reply_agents == [
        "alex_thorne",
        "archy",
        "liora",
        "oppy",
        "riverthread_808",
        "starling_au",
    ]


def test_api_surface_and_ui_contract(tmp_path: Path) -> None:
    """The server should expose the canonical APIs, compatibility aliases, and same-origin chamber UI."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))

    chamber_html = client.get("/chamber")
    assert chamber_html.status_code == 200
    assert "socket.io" not in chamber_html.text.lower()
    assert "localhost:8080" not in chamber_html.text.lower()
    assert "new WebSocket" in chamber_html.text

    dashboard_html = client.get("/")
    assert dashboard_html.status_code == 200
    assert "/api/mesh/status" in dashboard_html.text

    with client.websocket_connect("/ws/mesh") as websocket:
        initial = websocket.receive_json()
        assert initial["payload"]["phase"] == "socket_connected"
        websocket.send_text("ping")
        pong = websocket.receive_json()
        assert pong["payload"]["phase"] == "pong"

    status = client.get("/api/mesh/status").json()
    assert status["mesh_status"] == "operational"
    assert status["total_agents"] == 6

    send = client.post(
        "/api/mesh/messages",
        json={"to": "alex_thorne", "channel": "private:captain:alex", "content": "Status check."},
    )
    assert send.status_code == 200

    time.sleep(0.08)
    history = client.get(
        "/api/mesh/channels/{}/history?limit=20".format(quote("private:captain:alex", safe=""))
    ).json()
    assert any(event["event_type"] == "agent_reply" for event in history["events"])

    events = client.get("/api/mesh/events?after=0&limit=50").json()
    assert events["next_cursor"] >= len(events["events"])

    connect = client.post(
        "/api/bridge/gpt/connect/alex_thorne",
        json={"activationPhrase": "ORION_ALEX_THORNE_RELAY_ACTIVATE//"},
    )
    assert connect.status_code == 200
    assert connect.json()["status"] == "connected"

    bridge_status = client.get("/api/bridge/constellation/status").json()
    assert bridge_status["totalAgents"] == 6
    assert bridge_status["meshStatus"] == "operational"
