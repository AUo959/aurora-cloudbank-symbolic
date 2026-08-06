"""Tests for the Mesh Router V1 runtime and API surface."""

from __future__ import annotations

import asyncio
import json
import shutil
import time
import unittest
from pathlib import Path
from urllib.parse import quote

import pytest

from src.mesh.manifests import load_manifests
from src.mesh.models import MeshMessageRequest
from src.mesh.runtime import MeshRuntime

try:
    from fastapi.testclient import TestClient
    from src.servers.l2_integration_server import PROJECT_ROOT, _build_argument_parser, create_app

    FASTAPI_AVAILABLE = True
except ModuleNotFoundError:
    TestClient = None
    create_app = None
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    FASTAPI_AVAILABLE = False


CHECKS = unittest.TestCase()


def test_server_cli_defaults_to_loopback_and_allows_explicit_override(monkeypatch) -> None:
    """The server should bind locally unless the operator explicitly selects another host."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    monkeypatch.delenv("AURORA_L2_HOST", raising=False)
    CHECKS.assertEqual(_build_argument_parser().parse_args([]).host, "127.0.0.1")

    monkeypatch.setenv("AURORA_L2_HOST", "192.0.2.10")
    CHECKS.assertEqual(_build_argument_parser().parse_args([]).host, "192.0.2.10")


@pytest.mark.asyncio
async def test_server_lifespan_disconnects_mesh_agents(monkeypatch) -> None:
    """The server lifespan should disconnect every registered agent on shutdown."""
    from src.servers import l2_integration_server

    disconnected_agents = []

    class _Bridge:
        agents = {"L2_ARCHY": object(), "L2_OPPY": object()}

        async def disconnect_agent(self, agent_id):
            disconnected_agents.append(agent_id)

    monkeypatch.setattr(l2_integration_server, "l2_bridge", _Bridge())

    async with l2_integration_server.lifespan(l2_integration_server.app):
        pass

    CHECKS.assertEqual(disconnected_agents, ["L2_ARCHY", "L2_OPPY"])


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


def agent_ids(project_root: Path) -> list[str]:
    """Return manifest agent ids from the copied mesh fixture."""

    manifests = load_manifests(project_root / "config" / "mesh" / "agents")
    return sorted(manifests)


def channel_agent_ids(project_root: Path, channel: str) -> list[str]:
    """Return agents subscribed to a mesh channel from the copied fixture."""

    manifests = load_manifests(project_root / "config" / "mesh" / "agents")
    return sorted(
        manifest.id
        for manifest in manifests.values()
        if channel in manifest.channels
    )


def test_alias_resolution_and_live_fallback(tmp_path: Path) -> None:
    """Alex should resolve by alias and fall back deterministically when live mode is unavailable."""

    project_root = copy_mesh_project(tmp_path)
    runtime = MeshRuntime(project_root)

    async def scenario():
        result = await runtime.send_message(
            MeshMessageRequest(to="Alex Thorne", content="Need a routing decision before the next checkpoint.")
        )
        # Poll for the terminal event rather than sleeping a fixed interval.
        # The six events below are emitted asynchronously, so a fixed wait races
        # the pipeline: on a loaded runner only the first four had landed, which
        # failed an unrelated PR (#1367, a one-line model-identifier change).
        # Waiting on the condition keeps the assertion strict while removing the
        # dependency on how fast the runner happens to be.
        history = []
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline:
            history = runtime.get_channel_history("private:captain:alex")["events"]
            if any(event["event_type"] == "agent_reply" for event in history):
                break
            await asyncio.sleep(0.01)
        return result, history

    result, history = asyncio.run(scenario())
    CHECKS.assertEqual(result["status"], "accepted")
    event_types = [event["event_type"] for event in history]
    CHECKS.assertEqual(
        event_types[:6],
        [
            "message_accepted",
            "trace_update",
            "agent_ack",
            "agent_typing",
            "trace_update",
            "agent_reply",
        ],
    )

    reply = next(event for event in history if event["event_type"] == "agent_reply")
    CHECKS.assertEqual(reply["agent_id"], "alex_thorne")
    CHECKS.assertEqual(reply["payload"]["mode"], "deterministic_fallback")

    trace = [event for event in history if event["event_type"] == "trace_update"]
    CHECKS.assertTrue(
        any("Live adapter unavailable" in event["payload"].get("detail", "") for event in trace)
    )


def test_broadcast_routes_to_all_channel_agents(tmp_path: Path) -> None:
    """Broadcasts should reach all agents subscribed to the channel."""

    project_root = copy_mesh_project(tmp_path)
    runtime = MeshRuntime(project_root)
    expected_targets = channel_agent_ids(project_root, "#crew_lounge")

    async def scenario():
        result = await runtime.send_message(
            MeshMessageRequest(channel="#crew_lounge", content="Stand up in ten minutes.", type="broadcast")
        )
        # Poll until all targets have replied; gives 47+ agents time without wasting wall time
        target_count = len(expected_targets)
        deadline = 10.0
        elapsed = 0.0
        history = []
        while elapsed < deadline:
            await asyncio.sleep(0.1)
            elapsed += 0.1
            history = runtime.get_channel_history("#crew_lounge", limit=target_count * 6)["events"]
            replied = {event["agent_id"] for event in history if event["event_type"] == "agent_reply"}
            if len(replied) >= target_count:
                break
        return result, history

    checks = unittest.TestCase()
    result, history = asyncio.run(scenario())
    checks.assertEqual(sorted(result["targets"]), expected_targets)
    reply_agents = sorted({event["agent_id"] for event in history if event["event_type"] == "agent_reply"})
    checks.assertEqual(reply_agents, expected_targets)
    checks.assertFalse(any(event["event_type"] == "delivery_error" for event in history))


@pytest.mark.critical
def test_api_surface_and_ui_contract(tmp_path: Path) -> None:
    """The server should expose the canonical APIs, compatibility aliases, and same-origin chamber UI."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))
    expected_total_agents = len(agent_ids(project_root))

    chamber_html = client.get("/chamber")
    CHECKS.assertEqual(chamber_html.status_code, 200)
    CHECKS.assertNotIn("socket.io", chamber_html.text.lower())
    CHECKS.assertNotIn("localhost:8080", chamber_html.text.lower())
    CHECKS.assertIn("new WebSocket", chamber_html.text)

    dashboard_html = client.get("/")
    CHECKS.assertEqual(dashboard_html.status_code, 200)
    CHECKS.assertIn("/api/mesh/status", dashboard_html.text)

    with client.websocket_connect("/ws/mesh") as websocket:
        initial = websocket.receive_json()
        CHECKS.assertEqual(initial["payload"]["phase"], "socket_connected")
        websocket.send_text("ping")
        pong = websocket.receive_json()
        CHECKS.assertEqual(pong["payload"]["phase"], "pong")

    status = client.get("/api/mesh/status").json()
    CHECKS.assertEqual(status["mesh_status"], "operational")
    unittest.TestCase().assertEqual(status["total_agents"], expected_total_agents)

    send = client.post(
        "/api/mesh/messages",
        json={"to": "alex_thorne", "channel": "private:captain:alex", "content": "Status check."},
    )
    CHECKS.assertEqual(send.status_code, 200)

    history_url = "/api/mesh/channels/{}/history?limit=20".format(quote("private:captain:alex", safe=""))
    deadline = time.monotonic() + 2.0
    history = {"events": []}
    while time.monotonic() < deadline:
        history_response = client.get(history_url)
        unittest.TestCase().assertEqual(history_response.status_code, 200)
        history = history_response.json()
        if any(event["event_type"] == "agent_reply" for event in history.get("events", [])):
            break
        time.sleep(0.02)
    unittest.TestCase().assertTrue(
        any(event["event_type"] == "agent_reply" for event in history.get("events", []))
    )

    events = client.get("/api/mesh/events?after=0&limit=50").json()
    CHECKS.assertGreaterEqual(events["next_cursor"], len(events["events"]))

    connect = client.post(
        "/api/bridge/gpt/connect/alex_thorne",
        json={"activationPhrase": "ORION_ALEX_THORNE_RELAY_ACTIVATE//"},
    )
    CHECKS.assertEqual(connect.status_code, 200)
    CHECKS.assertEqual(connect.json()["status"], "connected")

    bridge_status = client.get("/api/bridge/constellation/status").json()
    unittest.TestCase().assertEqual(bridge_status["totalAgents"], expected_total_agents)
    CHECKS.assertEqual(bridge_status["meshStatus"], "operational")


@pytest.mark.critical
def test_mesh_agents_list(tmp_path: Path) -> None:
    """GET /api/mesh/agents should return all registered agents with expected fields."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))
    expected_agent_ids = set(agent_ids(project_root))

    checks = unittest.TestCase()
    response = client.get("/api/mesh/agents")
    checks.assertEqual(response.status_code, 200)
    body = response.json()
    checks.assertEqual(body["total"], len(expected_agent_ids))
    checks.assertEqual(len(body["agents"]), len(expected_agent_ids))
    response_agent_ids = {agent["agent_id"] for agent in body["agents"]}
    checks.assertEqual(response_agent_ids, expected_agent_ids)
    # Every agent record must have the required contract fields
    for agent in body["agents"]:
        checks.assertIn("agent_id", agent)
        checks.assertIn("status", agent)


@pytest.mark.critical
def test_mesh_agent_get_by_id(tmp_path: Path) -> None:
    """GET /api/mesh/agents/{agent_id} should return detail for a known agent."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))

    response = client.get("/api/mesh/agents/alex_thorne")
    CHECKS.assertEqual(response.status_code, 200)
    body = response.json()
    CHECKS.assertIs(body["success"], True)
    CHECKS.assertEqual(body["agent_id"], "alex_thorne")


@pytest.mark.critical
def test_mesh_agent_get_unknown_returns_404(tmp_path: Path) -> None:
    """GET /api/mesh/agents/{agent_id} for an unknown agent should return 404."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))

    response = client.get("/api/mesh/agents/nonexistent_agent_xyz")
    CHECKS.assertEqual(response.status_code, 404)


@pytest.mark.critical
def test_mesh_agent_activate(tmp_path: Path) -> None:
    """POST /api/mesh/agents/{agent_id}/activate should return success and connected status."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))

    response = client.post(
        "/api/mesh/agents/alex_thorne/activate",
        json={"activationPhrase": "ORION_ALEX_THORNE_RELAY_ACTIVATE//"},
    )
    CHECKS.assertEqual(response.status_code, 200)
    body = response.json()
    CHECKS.assertIs(body["success"], True)
    CHECKS.assertEqual(body["agent_id"], "alex_thorne")
    CHECKS.assertEqual(body["status"], "connected")


@pytest.mark.critical
def test_mesh_agent_activate_missing_phrase(tmp_path: Path) -> None:
    """POST /api/mesh/agents/{agent_id}/activate without activationPhrase should return 400."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))

    response = client.post("/api/mesh/agents/alex_thorne/activate", json={})
    CHECKS.assertEqual(response.status_code, 400)
    CHECKS.assertIn("activationPhrase", response.json()["detail"])


@pytest.mark.critical
def test_mesh_agent_activate_unknown_returns_404(tmp_path: Path) -> None:
    """POST /api/mesh/agents/{agent_id}/activate for unknown agent should return 404."""

    if not FASTAPI_AVAILABLE:
        pytest.skip("fastapi is not installed in this environment")

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))

    response = client.post(
        "/api/mesh/agents/nonexistent_agent_xyz/activate",
        json={"activationPhrase": "ORION_RELAY_ACTIVATE//"},
    )
    CHECKS.assertEqual(response.status_code, 404)
