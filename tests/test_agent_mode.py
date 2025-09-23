import pytest
from fastapi.testclient import TestClient

from aurora_api import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_agent_tools(client):
    resp = client.get("/agent/tools")
    assert resp.status_code == 200
    data = resp.json()
    assert "tools" in data
    assert "geometric_algebra" in data["tools"]
    assert data.get("dlp_level") == "DLP_L1_OK"


def test_session_create_and_update(client):
    # Create session
    create_resp = client.post(
        "/agent/session",
        json={"action": "create", "state_data": {"context": "test"}},
    )
    assert create_resp.status_code == 200
    create_data = create_resp.json()
    assert create_data.get("success") is True
    sess_id = create_data["result"]["session_id"]
    assert isinstance(sess_id, str) and sess_id

    # Update session
    update_resp = client.post(
        "/agent/session",
        json={
            "action": "update",
            "session_id": sess_id,
            "state_data": {"step": 1},
        },
    )
    assert update_resp.status_code == 200
    update_data = update_resp.json()
    assert update_data.get("success") is True
    assert update_data["result"]["state"]["state"]["context"] == "test"
    assert update_data["result"]["state"]["state"]["step"] == 1


def test_api_health_alias(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"
    assert data.get("agent_mode_enabled") is True
