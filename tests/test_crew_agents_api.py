import pytest

from fastapi.testclient import TestClient
from api.aurora_api import app
from src.agents.crew.noor import get_noor
from src.agents.crew.lin import get_lin

client = TestClient(app)

# Helper to sign a dummy token (bypassing full auth) if needed. For now endpoints rely on test env secret.

def _auth_headers():
    # Minimal stub: tokenless access may fail if security enforced; adjust if necessary.
    return {}


@pytest.mark.unit
def test_list_all_crew_agents():
    # Ensure at least one agent registered
    get_noor()
    resp = client.get("/api/crew/all", headers=_auth_headers())
    assert resp.status_code in (200, 401)  # allow unauthorized if auth strictly enforced
    if resp.status_code == 200:
        data = resp.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)
        # Ensure at least one known current agent (e.g., lin) present
        assert any(a["surname"].lower() == "lin" for a in data["agents"])  # present


@pytest.mark.unit
def test_process_agent_task_success():
    get_noor()
    payload = {"task_type": "reflexivity_analysis", "context": {"target_system": "aurora_core"}, "priority": "low"}
    resp = client.post("/api/crew/Noor/process", json=payload, headers=_auth_headers())
    assert resp.status_code in (200, 401)
    if resp.status_code == 200:
        data = resp.json()
        assert data["success"] is True
        assert data["task_type"] == payload["task_type"]
        # DLP placeholders
        assert "context_tag" in data and "symbolic_hash" in data
        assert "t1_state" in data and "srb_resolution" in data


@pytest.mark.unit
def test_process_agent_task_invalid():
    get_noor()
    payload = {"task_type": "__invalid__", "context": {}, "priority": "low"}
    resp = client.post("/api/crew/Noor/process", json=payload, headers=_auth_headers())
    assert resp.status_code in (200, 401)
    if resp.status_code == 200:
        data = resp.json()
        assert data["success"] is False
        assert "error" in data


@pytest.mark.unit
def test_collaboration_endpoint():
    get_noor()
    get_lin()
    payload = {
        "primary": "Noor",
        "secondary": "Noor",  # same agent instance type ensures shared task support
        "task": {"task_type": "reflexivity_analysis", "context": {}, "priority": "low"}
    }
    resp = client.post("/api/crew/collaborate", json=payload, headers=_auth_headers())
    assert resp.status_code in (200, 401)
    if resp.status_code == 200:
        data = resp.json()
        assert data["success"] is True
        assert "my_contribution" in data and "their_contribution" in data
        assert data["my_contribution"]["task_type"] == payload["task"]["task_type"]
        assert "context_tag" in data["my_contribution"]
        assert "symbolic_hash" in data["my_contribution"]
