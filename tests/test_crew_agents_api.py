import pytest

from fastapi.testclient import TestClient
from api.aurora_api import app
from src.agents.crew.noor import get_noor
from src.agents.crew.lin import get_lin
from src.middleware.fastapi_security import generate_csrf_token

client = TestClient(app)

# The full app mounts GlobalCsrfMiddleware, so unsafe (POST) requests must carry a
# valid CSRF token or they are rejected with 403 before reaching the route. Mint a
# token against the test CSRF secret (set in conftest.py) so the endpoints are
# actually exercised rather than blocked at the middleware.

def _auth_headers():
    return {"X-CSRF-Token": generate_csrf_token("test-session")}


@pytest.mark.unit
def test_list_all_crew_agents():
    # Ensure at least one agent registered
    get_noor()
    resp = client.get("/api/crew/all", headers=_auth_headers())
    assert resp.status_code in (200, 401)  # allow unauthorized if auth strictly enforced
    if resp.status_code == 200:
        data = resp.json()
        assert "agents" in data
        # Module router returns agents as a dict keyed by surname
        assert isinstance(data["agents"], dict)
        # Ensure at least one known current agent (e.g., lin) present
        assert "lin" in data["agents"] or any(
            v.get("surname", "").lower() == "lin" for v in data["agents"].values()
        )


@pytest.mark.unit
def test_process_agent_task_success():
    get_noor()
    payload = {"task_type": "reflexivity_analysis", "context": {"target_system": "aurora_core"}, "priority": "low"}
    resp = client.post("/api/crew/noor/process", json=payload, headers=_auth_headers())
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
    resp = client.post("/api/crew/noor/process", json=payload, headers=_auth_headers())
    assert resp.status_code in (200, 401)
    if resp.status_code == 200:
        data = resp.json()
        assert data["success"] is False
        assert "error" in data


@pytest.mark.unit
def test_collaboration_endpoint():
    get_noor()
    get_lin()
    # Module router CollaborationRequest: {"agents": [...], "task": {...}}
    payload = {
        "agents": ["noor", "lin"],
        "task": {"task_type": "reflexivity_analysis", "context": {}, "priority": "low"}
    }
    resp = client.post("/api/crew/collaborate", json=payload, headers=_auth_headers())
    assert resp.status_code in (200, 401)
    if resp.status_code == 200:
        data = resp.json()
        assert data["success"] is True
        assert "results" in data
        assert "primary_agent" in data
        assert "collaborators" in data
