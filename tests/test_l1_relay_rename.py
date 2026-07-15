"""
Backwards-compatibility proof for the L1 relay rename (LAYER_ARCHITECTURE.md
migration checklist; original background-task brief from the #1065/#1236
terminology correction).

The rename ships as: canonical modules `src/bridges/l1_relay_bridge.py` +
`src/api/l1_relay_api.py`, deprecation shims at the old import paths, and
the routes served at BOTH `/api/l1-relay-agents/*` (canonical) and
`/api/l2-agents/*` (deprecated alias). The pre-existing test files
(test_l2_meta_agent_bridge.py, test_l2_meta_agent_api.py) were deliberately
left untouched — them passing through the shims is itself the primary
compatibility evidence; this file covers what they cannot: identity between
old and new names, the new routes, and the deprecation markers.
"""

import warnings

import pytest
from fastapi.testclient import TestClient

from api.aurora_api import app
from src.bridges.l1_relay_bridge import L1RelayAgent, L1RelayBridge, l1_relay_bridge


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Module-level compatibility: old import paths alias the new objects
# ---------------------------------------------------------------------------

def test_old_bridge_import_path_warns_and_aliases_same_objects():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        import importlib
        import src.bridges.l2_meta_agent_bridge as legacy
        importlib.reload(legacy)  # ensure the warning fires even if cached

    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
    assert legacy.L2MetaAgentBridge is L1RelayBridge
    assert legacy.CustomGptAgent is L1RelayAgent
    # Same singleton instance — state written via one name is visible via
    # the other, so mixed old/new callers cannot diverge.
    assert legacy.l2_bridge is l1_relay_bridge


def test_old_api_import_path_exposes_legacy_router():
    import src.api.l2_meta_agent_api as legacy_api
    from src.api.l1_relay_api import legacy_router

    assert legacy_api.router is legacy_router


def test_agent_specs_carry_reality_layer_and_triplex_role():
    """LAYER_ARCHITECTURE.md checklist: L1 location vs Layer 2 protocol role."""
    for agent in l1_relay_bridge.agents.values():
        assert agent.reality_layer == "L1"
        assert agent.triplex_role == "layer_2_verifier"


# ---------------------------------------------------------------------------
# Route-level compatibility: both prefixes serve, legacy is flagged deprecated
# ---------------------------------------------------------------------------

def test_canonical_and_legacy_health_routes_serve_identically(client):
    canonical = client.get("/api/l1-relay-agents/health")
    legacy = client.get("/api/l2-agents/health")

    assert canonical.status_code == 200
    assert legacy.status_code == 200

    c, l = canonical.json(), legacy.json()
    # Identical payloads modulo the response timestamp
    c.pop("timestamp"), l.pop("timestamp")
    assert c == l
    assert c["total_agents"] == 5


def test_canonical_and_legacy_constellation_routes_serve(client):
    for prefix in ("/api/l1-relay-agents", "/api/l2-agents"):
        response = client.get(f"{prefix}/constellation")
        assert response.status_code == 200, prefix
        assert "relay_tier" in response.json()


def test_legacy_routes_marked_deprecated_in_openapi(client):
    schema = client.get("/openapi.json").json()
    legacy_paths = [p for p in schema["paths"] if p.startswith("/api/l2-agents")]
    canonical_paths = [p for p in schema["paths"] if p.startswith("/api/l1-relay-agents")]

    assert legacy_paths, "legacy alias routes missing from OpenAPI"
    assert canonical_paths, "canonical routes missing from OpenAPI"
    # Same operation set under both prefixes
    assert {p.replace("/api/l2-agents", "") for p in legacy_paths} == {
        p.replace("/api/l1-relay-agents", "") for p in canonical_paths
    }
    for path in legacy_paths:
        for operation in schema["paths"][path].values():
            assert operation.get("deprecated") is True, f"{path} not marked deprecated"
    for path in canonical_paths:
        for operation in schema["paths"][path].values():
            assert operation.get("deprecated") is not True, f"{path} wrongly deprecated"
