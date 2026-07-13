"""API-level regression checks for the validated mesh runtime surface."""

from __future__ import annotations

import json
import shutil
import sys
import time
import unittest
from pathlib import Path
from urllib.parse import quote

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.servers.l2_integration_server import create_app  # noqa: E402

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError:  # pragma: no cover - dependency varies by environment
    TestClient = None


def copy_mesh_project(tmp_path: Path) -> Path:
    """Copy the runtime assets needed to boot the mesh API in isolation."""

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


def wait_for_agent_reply(client: TestClient, channel_id: str, timeout: float = 1.5) -> dict:
    """Poll channel history until the async agent reply appears."""

    deadline = time.time() + timeout
    path = "/api/mesh/channels/{}/history?limit=40".format(quote(channel_id, safe=""))
    while time.time() < deadline:
        history = client.get(path).json()
        if any(event["event_type"] == "agent_reply" for event in history["events"]):
            return history
        time.sleep(0.05)
    pytest.fail(f"Timed out waiting for agent reply on {channel_id}")


@pytest.mark.skipif(TestClient is None, reason="fastapi test client is not installed")
def test_mesh_runtime_api_surface(tmp_path: Path) -> None:
    """The FastAPI runtime should expose the validated mesh dashboard and API contract."""
    checks = unittest.TestCase()

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))

    chamber_html = client.get("/chamber")
    assert chamber_html.status_code == 200
    assert "socket.io" not in chamber_html.text.lower()
    assert "new WebSocket" in chamber_html.text

    dashboard_html = client.get("/")
    assert dashboard_html.status_code == 200
    assert "/api/mesh/status" in dashboard_html.text

    health = client.get("/health").json()
    assert health["status"] == "healthy"
    assert health["mesh_status"] == "operational"

    status = client.get("/api/mesh/status").json()
    assert status["mesh_status"] == "operational"
    assert status["total_agents"] == 47
    checks.assertEqual(status["total_terminals"], 55)
    agent_ids = {agent["agent_id"] for agent in status["agents"]}
    assert "aurora" in agent_ids, "Aurora's seat is canonical: L1 station core, always-on arbitration"

    terminals = client.get("/api/mesh/terminals").json()
    checks.assertEqual(terminals["total"], 55)
    carmen_terminal = client.get("/api/mesh/terminals/core_development.carmen.term")
    checks.assertEqual(carmen_terminal.status_code, 200)
    checks.assertEqual(carmen_terminal.json()["owner_agent_id"], "carmen_rivas")

    dev_terminal_group = client.get("/api/mesh/terminals/aurora.dev.code.query")
    checks.assertEqual(dev_terminal_group.status_code, 200)
    checks.assertIs(dev_terminal_group.json()["terminal_group"], True)

    personnel_tag = quote("{{@Carmen-Rivas:::Adhesive flow rate nominal}}", safe="")
    invalid_terminal = client.get(f"/api/mesh/terminals/{personnel_tag}")
    checks.assertEqual(invalid_terminal.status_code, 400)
    checks.assertIn("Personnel Attention Tags", invalid_terminal.json()["detail"])

    unknown_terminal = client.get("/api/mesh/terminals/not-a-terminal")
    checks.assertEqual(unknown_terminal.status_code, 404)

    with client.websocket_connect("/ws/mesh") as websocket:
        initial = websocket.receive_json()
        assert initial["payload"]["phase"] == "socket_connected"
        websocket.send_text("ping")
        pong = websocket.receive_json()
        assert pong["payload"]["phase"] == "pong"


@pytest.mark.skipif(TestClient is None, reason="fastapi test client is not installed")
def test_mesh_runtime_api_message_routing(tmp_path: Path) -> None:
    """Direct messages, the Aurora handshake, and terminal-namespace routing should all reply."""
    checks = unittest.TestCase()

    project_root = copy_mesh_project(tmp_path)
    client = TestClient(create_app(project_root))

    send = client.post(
        "/api/mesh/messages",
        json={"to": "Alex Thorne", "channel": "private:captain:alex", "content": "Status check."},
    )
    assert send.status_code == 200
    history = wait_for_agent_reply(client, "private:captain:alex")
    assert any(event["event_type"] == "agent_reply" for event in history["events"])

    # Aurora handshake: the station core must be reachable and answer on
    # their direct channel (registry: "All staff must handshake with Aurora").
    handshake = client.post(
        "/api/mesh/messages",
        json={"to": "Aurora", "channel": "direct:aurora", "content": "Handshake. Please report status."},
    )
    assert handshake.status_code == 200
    aurora_history = wait_for_agent_reply(client, "direct:aurora")
    aurora_replies = [
        event for event in aurora_history["events"] if event["event_type"] == "agent_reply"
    ]
    assert aurora_replies, "Aurora must answer the handshake"
    assert any(event.get("agent_id") == "aurora" for event in aurora_replies)

    terminal_send = client.post(
        "/api/mesh/messages",
        json={"to": "core_development.carmen.term", "content": "Terminal namespace status check."},
    )
    checks.assertEqual(terminal_send.status_code, 200)
    terminal_payload = terminal_send.json()
    checks.assertEqual(terminal_payload["targets"], ["carmen_rivas"])
    checks.assertEqual(terminal_payload["target_terminals"], ["l1_carmen_rivas_terminal"])
    checks.assertEqual(terminal_payload["channel_id"], "private:crew:carmen_rivas")
