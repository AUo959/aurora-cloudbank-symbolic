"""API-level regression checks for the validated mesh runtime surface."""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import quote

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.servers.l2_integration_server import create_app

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
    assert status["total_agents"] == 6

    with client.websocket_connect("/ws/mesh") as websocket:
        initial = websocket.receive_json()
        assert initial["payload"]["phase"] == "socket_connected"
        websocket.send_text("ping")
        pong = websocket.receive_json()
        assert pong["payload"]["phase"] == "pong"

    send = client.post(
        "/api/mesh/messages",
        json={"to": "alex_thorne", "channel": "private:captain:alex", "content": "Status check."},
    )
    assert send.status_code == 200
    history = wait_for_agent_reply(client, "private:captain:alex")
    assert any(event["event_type"] == "agent_reply" for event in history["events"])
