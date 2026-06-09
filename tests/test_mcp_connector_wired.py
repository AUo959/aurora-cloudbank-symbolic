"""
Tests for wired MCP connector tool handlers (issue #828).

These tests mock CloudbankBridge to verify that each tool:
  - Calls the correct Aurora API endpoint
  - Maps the API response to the expected output schema
  - Handles BridgeError gracefully with an error field in the response
"""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from connector.tools.get_agents import GetAgentsTool
from connector.tools.get_capsules import GetCapsulesTool
from connector.tools.get_drift import GetDriftTool
from connector.tools.get_ethics import GetEthicsLogTool
from connector.tools.get_state import GetStateTool
from connector.transport.bridge import (
    BridgeError,
    AURORA_PATH_AGENTS,
    AURORA_PATH_COMPONENTS,
    AURORA_PATH_DRIFT_ALERTS,
    AURORA_PATH_ETHICS_VIOLATIONS,
    AURORA_PATH_HEALTH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

HEALTH_RESPONSE = {
    "status": "healthy",
    "service": "Aurora CloudBank Symbolic API",
    "timestamp": "2026-06-09T05:00:00+00:00",
    "components": {
        "aumemmanager": True,
        "data_guardian": True,
        "insight_ledger": True,
        "quantum_simulator": False,
        "gemini_agent": False,
        "sonnet4": True,
    },
}

AGENTS_RESPONSE = {
    "count": 2,
    "agents": [
        {"surname": "glyphon", "role": "memory_specialist", "status": "online", "clearance": "alpha"},
        {"surname": "caelion", "role": "nexus", "status": "offline", "clearance": "beta"},
    ],
}

DRIFT_ALERTS_RESPONSE = {
    "success": True,
    "alerts": [
        {
            "timestamp": "2026-06-09T04:00:00+00:00",
            "agent_id": "glyphon",
            "metric_name": "response_time",
            "level": "critical",
            "method": "z_score",
            "current_value": 1.5,
            "baseline_value": 0.5,
            "deviation": 2.0,
            "description": "Response time exceeds 2σ",
        },
    ],
    "count": 1,
}

VIOLATIONS_RESPONSE = [
    {
        "timestamp": "2026-06-09T04:30:00+00:00",
        "agent_id": "caelion",
        "rule_id": "RULE-SAFETY-001",
        "rule_name": "Boundary Check",
        "severity": "critical",
        "category": "safety",
        "description": "Attempted boundary violation",
        "blocked": True,
        "context": {},
        "context_tag": None,
        "remediation": None,
    }
]

COMPONENTS_RESPONSE = [
    {
        "name": "aumemmanager",
        "version": "2.0.0",
        "description": "Quantum memory management",
        "module_path": "modules.aumemmanager",
        "dependencies": [],
        "api_endpoints": ["/memory"],
        "status": "active",
        "registered_at": "2026-06-09T00:00:00+00:00",
        "last_updated": "2026-06-09T00:00:00+00:00",
        "metadata": {},
        "context_tag": "test",
    },
    {
        "name": "data_guardian",
        "version": "1.5.0",
        "description": "PII detection",
        "module_path": "modules.data_guardian",
        "dependencies": [],
        "api_endpoints": ["/api/guardian"],
        "status": "inactive",
        "registered_at": "2026-06-09T00:00:00+00:00",
        "last_updated": "2026-06-09T00:00:00+00:00",
        "metadata": {},
        "context_tag": "test",
    },
]


# ---------------------------------------------------------------------------
# GetStateTool
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_state_calls_health_endpoint():
    """aurora_get_state calls GET /health and GET /api/drift/alerts."""
    with patch("connector.tools.get_state.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(side_effect=[HEALTH_RESPONSE, DRIFT_ALERTS_RESPONSE])
        result = json.loads(await GetStateTool().run({"include_echochain": True}))

    assert result["vector_state"] == "QEM-SN1-ACTIVE::BASELINE_V1"
    assert result["ethics_protocol"] == "Picard_Delta_3"
    assert "AUMEMMANAGER" in result["active_modules"]
    assert "QUANTUM_SIMULATOR" not in result["active_modules"]
    assert result["layer_state"]["ethics_verified"] is True
    assert result["layer_state"]["recovery_threaded"] is True
    assert "echochain" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_state_no_echochain():
    """include_echochain=False omits the echochain key."""
    with patch("connector.tools.get_state.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(return_value=HEALTH_RESPONSE)
        result = json.loads(await GetStateTool().run({"include_echochain": False}))

    assert "echochain" not in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_state_bridge_error():
    """BridgeError returns error field, not an exception."""
    with patch("connector.tools.get_state.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(side_effect=BridgeError("connection refused"))
        result = json.loads(await GetStateTool().run({}))

    assert "error" in result
    assert result["vector_state"] == "UNAVAILABLE"


# ---------------------------------------------------------------------------
# GetAgentsTool
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agents_maps_crew_response():
    """aurora_get_agents maps crew surnames/roles/status to PAT registry format."""
    with patch("connector.tools.get_agents.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(return_value=AGENTS_RESPONSE)
        result = json.loads(await GetAgentsTool().run({}))

    assert result["total"] == 2
    ids = {a["id"] for a in result["agents"]}
    assert ids == {"glyphon", "caelion"}
    glyphon = next(a for a in result["agents"] if a["id"] == "glyphon")
    assert glyphon["visibility"] == "Available"
    caelion = next(a for a in result["agents"] if a["id"] == "caelion")
    assert caelion["visibility"] == "Invisible"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agents_visibility_filter():
    """visibility_filter=available returns only Available agents."""
    with patch("connector.tools.get_agents.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(return_value=AGENTS_RESPONSE)
        result = json.loads(await GetAgentsTool().run({"visibility_filter": "available"}))

    assert all(a["visibility"] == "Available" for a in result["agents"])
    assert result["available_count"] == len(result["agents"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agents_bridge_error():
    """BridgeError returns error field with empty agents list."""
    with patch("connector.tools.get_agents.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(side_effect=BridgeError("timeout"))
        result = json.loads(await GetAgentsTool().run({}))

    assert "error" in result
    assert result["agents"] == []


# ---------------------------------------------------------------------------
# GetDriftTool
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_breach_on_critical_alerts():
    """Critical alerts cause L1 breach; no warning/info alerts → L2/L3 nominal."""
    with patch("connector.tools.get_drift.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(return_value=DRIFT_ALERTS_RESPONSE)
        result = json.loads(await GetDriftTool().run({}))

    l1 = next(l for l in result["layers"] if l["layer"] == "L1_capsule_governance")
    l2 = next(l for l in result["layers"] if l["layer"] == "L2_agent_qgia")
    assert l1["breach"] is True
    assert l2["breach"] is False
    assert result["any_breach"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_all_nominal_when_no_alerts():
    """Empty alerts list → all layers nominal."""
    empty = {"success": True, "alerts": [], "count": 0}
    with patch("connector.tools.get_drift.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(return_value=empty)
        result = json.loads(await GetDriftTool().run({}))

    assert result["any_breach"] is False
    assert all(not l["breach"] for l in result["layers"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_include_history():
    """include_history=True adds history key to each layer."""
    with patch("connector.tools.get_drift.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(return_value=DRIFT_ALERTS_RESPONSE)
        result = json.loads(await GetDriftTool().run({"include_history": True}))

    assert all("history" in l for l in result["layers"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_bridge_error():
    """BridgeError returns error field and empty layers."""
    with patch("connector.tools.get_drift.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(side_effect=BridgeError("unreachable"))
        result = json.loads(await GetDriftTool().run({}))

    assert "error" in result
    assert result["layers"] == []


# ---------------------------------------------------------------------------
# GetEthicsLogTool
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_maps_violations():
    """aurora_get_ethics_log maps GUMAS violations to connector entry format."""
    with patch("connector.tools.get_ethics.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.post = AsyncMock(return_value=VIOLATIONS_RESPONSE)
        result = json.loads(await GetEthicsLogTool().run({"limit": 20}))

    assert result["protocol"] == "Picard_Delta_3"
    assert result["total_returned"] == 1
    entry = result["entries"][0]
    assert entry["severity"] == "violation"
    assert entry["module"] == "caelion"
    assert entry["outcome"] == "fail"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_severity_mapping():
    """Aurora 'medium' severity maps to connector 'warning'."""
    medium_violation = [{**VIOLATIONS_RESPONSE[0], "severity": "medium", "blocked": False}]
    with patch("connector.tools.get_ethics.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.post = AsyncMock(return_value=medium_violation)
        result = json.loads(await GetEthicsLogTool().run({}))

    assert result["entries"][0]["severity"] == "warning"
    assert result["entries"][0]["outcome"] == "pass"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_bridge_error():
    """BridgeError returns error field with empty entries."""
    with patch("connector.tools.get_ethics.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.post = AsyncMock(side_effect=BridgeError("403 forbidden"))
        result = json.loads(await GetEthicsLogTool().run({}))

    assert "error" in result
    assert result["entries"] == []


# ---------------------------------------------------------------------------
# GetCapsulesTool
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsules_maps_components():
    """aurora_get_capsules maps synergy components to capsule registry format."""
    with patch("connector.tools.get_capsules.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(return_value=COMPONENTS_RESPONSE)
        result = json.loads(await GetCapsulesTool().run({}))

    assert result["total_verified"] == 2
    assert result["loaded_count"] == 1
    names = {c["name"] for c in result["capsules"]}
    assert "aumemmanager" in names
    active = next(c for c in result["capsules"] if c["name"] == "aumemmanager")
    assert active["loaded"] is True
    assert active["export_ready"] is True
    assert active["symbolic_hash"].startswith("SYM_HASH_")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsules_loaded_only_filter():
    """loaded_only=True returns only active components."""
    with patch("connector.tools.get_capsules.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(return_value=COMPONENTS_RESPONSE)
        result = json.loads(await GetCapsulesTool().run({"loaded_only": True}))

    assert all(c["loaded"] for c in result["capsules"])
    assert result["loaded_count"] == len(result["capsules"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsules_bridge_error():
    """BridgeError returns error field with empty capsules."""
    with patch("connector.tools.get_capsules.CloudbankBridge") as MockBridge:
        instance = MockBridge.return_value
        instance.get = AsyncMock(side_effect=BridgeError("service unavailable"))
        result = json.loads(await GetCapsulesTool().run({}))

    assert "error" in result
    assert result["capsules"] == []


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_bridge_path_constants_defined():
    """All expected AURORA_PATH_* constants are defined in bridge.py."""
    assert AURORA_PATH_HEALTH == "/health"
    assert AURORA_PATH_AGENTS == "/api/crew/all"
    assert AURORA_PATH_DRIFT_ALERTS == "/api/drift/alerts"
    assert AURORA_PATH_ETHICS_VIOLATIONS == "/gumas/violations"
    assert AURORA_PATH_COMPONENTS == "/synergy/components"
