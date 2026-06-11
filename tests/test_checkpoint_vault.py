"""Tests for the Ethical Checkpoint Vault module.

DLP: checkpoint_vault_tests_v1
Anchors: T1:TEST_CHECKPOINT, SRB:GUMAS_VAULT
"""

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-checkpoint-vault")


def _auth_headers() -> dict[str, str]:
    from src.middleware.fastapi_security import generate_csrf_token

    token = generate_csrf_token("checkpoint-vault-test-session")
    return {"Authorization": f"Bearer {token}", "X-CSRF-Token": token}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """Return a test client for the FastAPI app."""
    try:
        from api.aurora_api import app
        return TestClient(app, raise_server_exceptions=True)
    except ImportError:
        pytest.skip("aurora_api not importable — skipping checkpoint tests")


@pytest.fixture(scope="module")
def create_payload():
    """Minimal valid payload for POST /checkpoint/create."""
    return {
        "agent_id": "test-agent-001",
        "trigger": "manual",
        "state_snapshot": {"action": "test", "value": 42},
        "ethics_profile": {"compliant": True, "rule_violations": []},
        "tags": ["unit-test"],
        "context_tag": "checkpoint_vault_tests_v1",
    }


# ---------------------------------------------------------------------------
# Unit tests for the store directly
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.aurora
def test_store_create_returns_record():
    """CheckpointVault.create() should persist a record with CHKP-* id."""
    from modules.checkpoint_vault.store import CheckpointVault
    from modules.checkpoint_vault.models import CreateCheckpointRequest

    vault = CheckpointVault()
    req = CreateCheckpointRequest(
        agent_id="agent-store-test",
        state_snapshot={"key": "value"},
        ethics_profile={"compliant": True},
    )
    record = vault.create(req)
    assert record.checkpoint_id.startswith("CHKP-")
    assert record.agent_id == "agent-store-test"
    assert record.version == 1
    assert record.status == "active"


@pytest.mark.unit
@pytest.mark.aurora
def test_store_versioning():
    """Each subsequent create for the same agent increments version."""
    from modules.checkpoint_vault.store import CheckpointVault
    from modules.checkpoint_vault.models import CreateCheckpointRequest

    vault = CheckpointVault()
    req = CreateCheckpointRequest(agent_id="versioned-agent", state_snapshot={}, ethics_profile={})

    r1 = vault.create(req)
    r2 = vault.create(req)
    assert r2.version == r1.version + 1


@pytest.mark.unit
@pytest.mark.aurora
def test_store_supersedes_previous_active():
    """Creating a new checkpoint marks prior ACTIVE ones as SUPERSEDED."""
    from modules.checkpoint_vault.store import CheckpointVault
    from modules.checkpoint_vault.models import CreateCheckpointRequest

    vault = CheckpointVault()
    req = CreateCheckpointRequest(agent_id="supersede-agent", state_snapshot={}, ethics_profile={})
    first = vault.create(req)
    vault.create(req)

    stored_first = vault.get(first.checkpoint_id)
    assert stored_first is not None
    assert stored_first.status == "superseded"


@pytest.mark.unit
@pytest.mark.aurora
def test_store_rollback():
    """rollback() sets status to rolled_back and records reason in meta."""
    from modules.checkpoint_vault.store import CheckpointVault
    from modules.checkpoint_vault.models import CreateCheckpointRequest

    vault = CheckpointVault()
    req = CreateCheckpointRequest(agent_id="rb-agent", state_snapshot={}, ethics_profile={})
    record = vault.create(req)

    rolled = vault.rollback(record.checkpoint_id, reason="test rollback", performed_by="pytest")
    assert rolled.status == "rolled_back"
    assert "rollback_reason" in rolled.meta
    assert rolled.meta["rollback_reason"] == "test rollback"


@pytest.mark.unit
@pytest.mark.aurora
def test_store_rollback_twice_raises():
    """Rolling back an already-rolled-back checkpoint raises ValueError."""
    from modules.checkpoint_vault.store import CheckpointVault
    from modules.checkpoint_vault.models import CreateCheckpointRequest

    vault = CheckpointVault()
    req = CreateCheckpointRequest(agent_id="rb2-agent", state_snapshot={}, ethics_profile={})
    record = vault.create(req)
    vault.rollback(record.checkpoint_id, reason="first", performed_by="pytest")

    with pytest.raises(ValueError, match="already rolled back"):
        vault.rollback(record.checkpoint_id, reason="second", performed_by="pytest")


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.unit
def test_vault_health(client):
    """GET /checkpoint/health should return 200 with status=healthy."""
    resp = client.get("/checkpoint/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "total_checkpoints" in data
    assert "agents_tracked" in data


@pytest.mark.api
@pytest.mark.unit
def test_create_checkpoint(client, create_payload):
    """POST /checkpoint/create should return 201 and a valid CheckpointRecord."""
    resp = client.post("/checkpoint/create", json=create_payload, headers=_auth_headers())
    assert resp.status_code == 201
    data = resp.json()
    assert data["checkpoint_id"].startswith("CHKP-")
    assert data["agent_id"] == "test-agent-001"
    assert data["version"] >= 1
    assert data["status"] == "active"


@pytest.mark.api
@pytest.mark.unit
def test_list_checkpoints(client, create_payload):
    """GET /checkpoint should return a list."""
    client.post("/checkpoint/create", json=create_payload, headers=_auth_headers())
    resp = client.get("/checkpoint")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.api
@pytest.mark.unit
def test_get_checkpoint_by_id(client, create_payload):
    """GET /checkpoint/{id} should return the full record."""
    post = client.post("/checkpoint/create", json=create_payload, headers=_auth_headers())
    assert post.status_code == 201
    chkp_id = post.json()["checkpoint_id"]

    get = client.get(f"/checkpoint/{chkp_id}")
    assert get.status_code == 200
    assert get.json()["checkpoint_id"] == chkp_id


@pytest.mark.api
@pytest.mark.unit
def test_get_checkpoint_not_found(client):
    """GET /checkpoint/UNKNOWN should return 404."""
    resp = client.get("/checkpoint/CHKP-NONEXISTENT000000")
    assert resp.status_code == 404


@pytest.mark.api
@pytest.mark.unit
def test_rollback_checkpoint(client, create_payload):
    """POST /checkpoint/{id}/rollback should set status to rolled_back."""
    post = client.post("/checkpoint/create", json=create_payload, headers=_auth_headers())
    assert post.status_code == 201
    chkp_id = post.json()["checkpoint_id"]

    roll = client.post(
        f"/checkpoint/{chkp_id}/rollback",
        json={"reason": "ethics violation detected", "performed_by": "pytest"},
        headers=_auth_headers(),
    )
    assert roll.status_code == 200
    assert roll.json()["status"] == "rolled_back"


@pytest.mark.api
@pytest.mark.unit
def test_agent_history(client, create_payload):
    """GET /checkpoint/agent/{id}/history should return records for that agent."""
    # Create two checkpoints for the same agent
    for _ in range(2):
        client.post("/checkpoint/create", json=create_payload, headers=_auth_headers())

    resp = client.get("/checkpoint/agent/test-agent-001/history")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert all(r["agent_id"] == "test-agent-001" for r in data)
