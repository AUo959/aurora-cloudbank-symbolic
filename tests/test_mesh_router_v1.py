"""Tests for the Mesh Router V1 runtime and API surface."""

from __future__ import annotations

import asyncio
import json
import shutil
import time
from pathlib import Path
from typing import Optional
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


def wait_for_reply_agents(runtime: MeshRuntime, channel_id: str, expected_agents: set[str], timeout_s: float = 1.0) -> list[dict]:
    """Poll channel history until the expected agent replies land or timeout expires."""

    deadline = time.time() + timeout_s
    history_limit = max(120, len(expected_agents) * 6)
    history = runtime.get_channel_history(channel_id, limit=history_limit)["events"]
    while time.time() < deadline:
        reply_agents = {event["agent_id"] for event in history if event["event_type"] == "agent_reply"}
        if expected_agents.issubset(reply_agents):
            return history
        time.sleep(0.02)
        history = runtime.get_channel_history(channel_id, limit=history_limit)["events"]
    return history


def wait_for_message_event(
    runtime: MeshRuntime,
    channel_id: str,
    message_id: str,
    event_type: str,
    timeout_s: float = 1.0,
) -> Optional[dict]:
    """Poll channel history until a specific message event is recorded or timeout expires."""

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        history = runtime.get_channel_history(channel_id, limit=120)["events"]
        match = next(
            (
                event
                for event in history
                if event["message_id"] == message_id and event["event_type"] == event_type
            ),
            None,
        )
        if match is not None:
            return match
        time.sleep(0.02)
    return None


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
    expected_targets = sorted(agent["agent_id"] for agent in runtime.list_agents() if "#crew_lounge" in agent["channels"])

    async def scenario():
        result = await runtime.send_message(
            MeshMessageRequest(channel="#crew_lounge", content="Stand up in ten minutes.", type="broadcast")
        )
        history = wait_for_reply_agents(runtime, "#crew_lounge", set(expected_targets))
        return result, history

    result, history = asyncio.run(scenario())
    assert sorted(result["targets"]) == expected_targets
    reply_agents = sorted({event["agent_id"] for event in history if event["event_type"] == "agent_reply"})
    assert reply_agents == expected_targets


def test_aurora_alias_resolution_exposes_profile_and_tool_metadata(tmp_path: Path) -> None:
    """Aurora should resolve by AU alias and expose its extended manifest fields."""

    project_root = copy_mesh_project(tmp_path)
    runtime = MeshRuntime(project_root)

    aurora = runtime.get_agent("AU")
    assert aurora["agent_id"] == "aurora"
    assert aurora["instruction_profile_file"] == "config/mesh/profiles/aurora_instruction_profile.json"
    assert aurora["continuity_log_file"] == "config/mesh/continuity/aurora.jsonl"
    assert "aurora_command_grammar" in aurora["tool_bindings"]
    assert "system_status" in aurora["tool_bindings"]


def test_aurora_tool_bindings_use_shared_runtime_and_append_continuity(tmp_path: Path) -> None:
    """Aurora should execute bound tools through the shared integration and append continuity reflections."""

    project_root = copy_mesh_project(tmp_path)
    runtime = MeshRuntime(project_root)
    continuity_path = project_root / "config" / "mesh" / "continuity" / "aurora.jsonl"
    baseline_count = len([line for line in continuity_path.read_text().splitlines() if line.strip()])
    calls: list[tuple[str, dict, Optional[str]]] = []

    async def fake_execute_tool(tool_name: str, parameters: dict, session_id: Optional[str] = None) -> dict:
        calls.append((tool_name, parameters, session_id))
        if tool_name == "aurora_command_grammar":
            accepted = parameters["command_text"].strip().endswith("//.")
            return {
                "success": True,
                "result": {
                    "accepted": accepted,
                    "executable": accepted,
                    "normalized_text": parameters["command_text"].strip(),
                    "enforcement": {"execute_terminator": "//."},
                },
            }
        if tool_name == "system_status":
            return {"success": True, "result": {"agent_status": "ready", "active_sessions": 0}}
        return {"success": True, "result": {"tool_name": tool_name}}

    runtime.agent_tool_runtime.execute_tool = fake_execute_tool  # type: ignore[method-assign]

    async def scenario():
        first = await runtime.send_message(MeshMessageRequest(to="AU", content="Please inspect 001//. and give me status."))
        await asyncio.sleep(0.08)
        history_one = runtime.get_channel_history("direct:aurora", limit=40)["events"]

        second = await runtime.send_message(MeshMessageRequest(to="Aurora", content="What is still open from that thread?"))
        await asyncio.sleep(0.08)
        history_two = runtime.get_channel_history("direct:aurora", limit=80)["events"]
        return first, second, history_one, history_two

    first, second, history_one, history_two = asyncio.run(scenario())
    assert first["status"] == "accepted"
    assert second["status"] == "accepted"
    assert {call[0] for call in calls} >= {"aurora_command_grammar", "system_status"}
    assert all(call[2] == "mesh::aurora" for call in calls)

    first_reply = next(
        event for event in history_one if event["event_type"] == "agent_reply" and event["message_id"] == first["message_id"]
    )
    assert "Tool signals:" in first_reply["payload"]["content"]

    second_reply = next(
        event for event in history_two if event["event_type"] == "agent_reply" and event["message_id"] == second["message_id"]
    )
    assert "Continuity note:" in second_reply["payload"]["content"]

    updated_count = len([line for line in continuity_path.read_text().splitlines() if line.strip()])
    assert updated_count == baseline_count + 2


def test_worker_crash_is_persisted_as_delivery_error(tmp_path: Path) -> None:
    """Background worker crashes should emit a terminal delivery_error event."""

    project_root = copy_mesh_project(tmp_path)
    runtime = MeshRuntime(project_root)

    async def crashing_process_target(*args, **kwargs):
        raise KeyboardInterrupt("simulated worker crash")

    runtime._process_target = crashing_process_target  # type: ignore[method-assign]

    async def scenario():
        return await runtime.send_message(
            MeshMessageRequest(to="Alex Thorne", content="Need a routing decision before the next checkpoint.")
        )

    result = asyncio.run(scenario())
    error_event = wait_for_message_event(
        runtime,
        channel_id="private:captain:alex",
        message_id=result["message_id"],
        event_type="delivery_error",
    )

    assert error_event is not None
    assert error_event["payload"]["phase"] == "worker_crash"
    assert error_event["payload"]["error_type"] == "KeyboardInterrupt"


def test_spawned_mesh_workers_are_non_daemon(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Accepted mesh work should use non-daemon threads so shutdowns do not drop replies silently."""

    project_root = copy_mesh_project(tmp_path)
    runtime = MeshRuntime(project_root)
    manifest = runtime.manifests["alex_thorne"]
    request = MeshMessageRequest(to="Alex Thorne", content="Status check.")
    thread_config: dict[str, object] = {}

    class FakeThread:
        def __init__(self, *, target, daemon, name):
            thread_config["target"] = target
            thread_config["daemon"] = daemon
            thread_config["name"] = name

        def start(self) -> None:
            thread_config["started"] = True

    monkeypatch.setattr("src.mesh.runtime.threading.Thread", FakeThread)

    runtime._spawn_target("message1234abcd", "private:captain:alex", request, manifest)

    assert thread_config["started"] is True
    assert thread_config["daemon"] is False
    assert thread_config["name"] == "mesh-target-alex_thorne-message1"


def test_app_lifespan_resets_bridge_sessions(tmp_path: Path) -> None:
    """App lifespan should clear stale bridge session state across startup and shutdown."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    app = create_app(project_root)
    app.state.bridge_sessions["alex_thorne"] = "stale-token"

    with TestClient(app):
        assert app.state.bridge_sessions == {}
        app.state.bridge_sessions["alex_thorne"] = "live-token"

    assert app.state.bridge_sessions == {}


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
    expected_total = client.get("/api/mesh/agents").json()["total"]
    assert status["total_agents"] == expected_total

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
    assert connect.json()["sessionToken"]

    missing_phrase = client.post("/api/bridge/gpt/connect/alex_thorne", json={})
    assert missing_phrase.status_code == 401
    assert missing_phrase.json()["detail"] == "Missing activation phrase"

    bridge_status = client.get("/api/bridge/constellation/status").json()
    assert bridge_status["totalAgents"] == expected_total
    assert bridge_status["meshStatus"] == "operational"

    orion_core = client.get("/api/orion-core").json()
    assert orion_core["activation_phrase_required"] is True
    assert "activation_phrases" not in orion_core
    assert "alex_thorne" in orion_core["supported_agents"]


def test_remote_control_routes_require_token_and_bridge_session(tmp_path: Path) -> None:
    """Remote clients should need explicit control or bridge session tokens."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    app = create_app(project_root)
    app.state.loopback_client_hosts = {"127.0.0.1", "::1", "localhost"}
    app.state.mesh_control_token = "mesh-control-secret"
    app.state.bridge_activation_phrases["alex_thorne"] = "bridge-connect-secret"
    client = TestClient(app)

    missing_control = client.post(
        "/api/mesh/messages",
        json={"to": "alex_thorne", "channel": "private:captain:alex", "content": "Status check."},
    )
    assert missing_control.status_code == 401
    assert missing_control.json()["detail"] == "Missing mesh control token"

    invalid_control = client.post(
        "/api/mesh/messages",
        json={"to": "alex_thorne", "channel": "private:captain:alex", "content": "Status check."},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert invalid_control.status_code == 401
    assert invalid_control.json()["detail"] == "Invalid mesh control token"

    send = client.post(
        "/api/mesh/messages",
        json={"to": "alex_thorne", "channel": "private:captain:alex", "content": "Status check."},
        headers={"Authorization": "Bearer mesh-control-secret"},
    )
    assert send.status_code == 200

    remote_events = client.get("/api/mesh/events?after=0&limit=10")
    assert remote_events.status_code == 401
    assert remote_events.json()["detail"] == "Missing mesh control token"

    missing_session = client.post("/api/bridge/gpt/message/alex_thorne", json={"message": "Ping"})
    assert missing_session.status_code == 404
    assert missing_session.json()["detail"] == "Agent not connected"

    connect = client.post(
        "/api/bridge/gpt/connect/alex_thorne",
        json={"activationPhrase": "bridge-connect-secret"},
    )
    assert connect.status_code == 200
    session_token = connect.json()["sessionToken"]

    bridge_without_session = client.post("/api/bridge/gpt/message/alex_thorne", json={"message": "Ping"})
    assert bridge_without_session.status_code == 401
    assert bridge_without_session.json()["detail"] == "Missing bridge session token"

    bridge_message = client.post(
        "/api/bridge/gpt/message/alex_thorne",
        json={"message": "Ping"},
        headers={"Authorization": f"Bearer {session_token}"},
    )
    assert bridge_message.status_code == 200

    bridge_status = client.get("/api/bridge/gpt/status/alex_thorne")
    assert bridge_status.status_code == 401
    assert bridge_status.json()["detail"] == "Missing bridge session token"

    bridge_status = client.get(
        "/api/bridge/gpt/status/alex_thorne",
        headers={"Authorization": f"Bearer {session_token}"},
    )
    assert bridge_status.status_code == 200


def test_remote_bridge_connect_requires_configured_activation_phrase(tmp_path: Path) -> None:
    """Remote bridge clients should not be allowed to use deterministic fallback phrases."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    app = create_app(project_root)
    app.state.loopback_client_hosts = {"127.0.0.1", "::1", "localhost"}
    client = TestClient(app)

    connect = client.post(
        "/api/bridge/gpt/connect/alex_thorne",
        json={"activationPhrase": "ORION_ALEX_THORNE_RELAY_ACTIVATE//"},
    )
    assert connect.status_code == 503
    assert "AURORA_BRIDGE_ALEX_THORNE_ACTIVATION_PHRASE" in connect.json()["detail"]
