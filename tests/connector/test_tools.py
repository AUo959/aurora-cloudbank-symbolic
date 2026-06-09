"""
Tests for individual MCP tool handlers in connector/tools/.

Covers:
  - GetStateTool   (aurora_get_state)
  - GetAgentsTool  (aurora_get_agents)
  - GetDriftTool   (aurora_get_drift)
  - GetEthicsLogTool (aurora_get_ethics_log)
  - GetCapsulesTool  (aurora_get_capsules)

Each tool is tested for:
  1. .schema() returns a Tool with the correct name
  2. .run({}) returns valid JSON with expected top-level keys
  3. Parameter-specific behaviour (where the tool accepts input args)
"""

import json

import pytest
from mcp.types import Tool

from connector.tools.get_state import GetStateTool
from connector.tools.get_agents import GetAgentsTool
from connector.tools.get_drift import GetDriftTool, DRIFT_THRESHOLDS
from connector.tools.get_ethics import GetEthicsLogTool
from connector.tools.get_capsules import GetCapsulesTool, TOTAL_VERIFIED_CAPSULES


# ---------------------------------------------------------------------------
# aurora_get_state
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_state_schema_name():
    """GetStateTool.schema() must return a Tool named 'aurora_get_state'."""
    tool = GetStateTool()
    schema = tool.schema()
    assert isinstance(schema, Tool)
    assert schema.name == "aurora_get_state"


@pytest.mark.unit
def test_get_state_schema_has_include_echochain_property():
    """schema().inputSchema must advertise the include_echochain parameter."""
    tool = GetStateTool()
    schema = tool.schema()
    assert "include_echochain" in schema.inputSchema["properties"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_state_default_returns_valid_json():
    """run({}) must return a JSON string with required top-level keys."""
    tool = GetStateTool()
    result = await tool.run({})
    data = json.loads(result)
    assert "vector_state" in data
    assert "lockpoint" in data
    assert "ethics_protocol" in data
    assert "layer_state" in data
    assert "active_modules" in data
    assert "retrieved_at" in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_state_includes_echochain_by_default():
    """run({}) with no args must include echochain (default include_echochain=True)."""
    tool = GetStateTool()
    result = await tool.run({})
    data = json.loads(result)
    assert "echochain" in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_state_excludes_echochain_when_disabled():
    """run({"include_echochain": False}) must omit the echochain key."""
    tool = GetStateTool()
    result = await tool.run({"include_echochain": False})
    data = json.loads(result)
    assert "echochain" not in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_state_explicit_include_echochain():
    """run({"include_echochain": True}) must include echochain with loop_set."""
    tool = GetStateTool()
    result = await tool.run({"include_echochain": True})
    data = json.loads(result)
    assert "echochain" in data
    assert "loop_set" in data["echochain"]


# ---------------------------------------------------------------------------
# aurora_get_agents
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_agents_schema_name():
    """GetAgentsTool.schema() must return a Tool named 'aurora_get_agents'."""
    tool = GetAgentsTool()
    schema = tool.schema()
    assert isinstance(schema, Tool)
    assert schema.name == "aurora_get_agents"


@pytest.mark.unit
def test_get_agents_schema_has_visibility_filter():
    """schema().inputSchema must advertise the visibility_filter parameter."""
    tool = GetAgentsTool()
    schema = tool.schema()
    assert "visibility_filter" in schema.inputSchema["properties"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agents_default_returns_valid_json():
    """run({}) must return a JSON string with required top-level keys."""
    tool = GetAgentsTool()
    result = await tool.run({})
    data = json.loads(result)
    assert "agents" in data
    assert "total" in data
    assert "retrieved_at" in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agents_default_returns_all_agents():
    """run({}) with no filter must return all available agents."""
    tool = GetAgentsTool()
    result = await tool.run({})
    data = json.loads(result)
    # Stub has 4 agents; total must reflect the list length
    assert data["total"] == len(data["agents"])
    assert data["total"] > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agents_visibility_filter_available():
    """run({"visibility_filter": "available"}) must return only Available agents."""
    tool = GetAgentsTool()
    result = await tool.run({"visibility_filter": "available"})
    data = json.loads(result)
    for agent in data["agents"]:
        assert agent["visibility"].lower() == "available"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agents_visibility_filter_dnd_returns_subset():
    """run({"visibility_filter": "dnd"}) must return only DND agents (may be empty)."""
    tool = GetAgentsTool()
    result = await tool.run({"visibility_filter": "dnd"})
    data = json.loads(result)
    for agent in data["agents"]:
        assert agent["visibility"].lower() == "dnd"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_agents_all_filter_matches_no_filter():
    """Explicitly passing visibility_filter='all' should behave like no filter."""
    tool = GetAgentsTool()
    result_default = await tool.run({})
    result_all = await tool.run({"visibility_filter": "all"})
    data_default = json.loads(result_default)
    data_all = json.loads(result_all)
    assert data_default["total"] == data_all["total"]


# ---------------------------------------------------------------------------
# aurora_get_drift
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_drift_schema_name():
    """GetDriftTool.schema() must return a Tool named 'aurora_get_drift'."""
    tool = GetDriftTool()
    schema = tool.schema()
    assert isinstance(schema, Tool)
    assert schema.name == "aurora_get_drift"


@pytest.mark.unit
def test_get_drift_schema_has_include_history():
    """schema().inputSchema must advertise the include_history parameter."""
    tool = GetDriftTool()
    schema = tool.schema()
    assert "include_history" in schema.inputSchema["properties"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_default_returns_valid_json():
    """run({}) must return a JSON string with required top-level keys."""
    tool = GetDriftTool()
    result = await tool.run({})
    data = json.loads(result)
    assert "layers" in data
    assert "any_breach" in data
    assert "timestamp" in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_has_three_layers():
    """run({}) must include exactly three stratification layers."""
    tool = GetDriftTool()
    result = await tool.run({})
    data = json.loads(result)
    assert len(data["layers"]) == len(DRIFT_THRESHOLDS)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_layer_fields():
    """Each drift layer entry must have required fields including threshold and status."""
    tool = GetDriftTool()
    result = await tool.run({})
    data = json.loads(result)
    for layer in data["layers"]:
        assert "layer" in layer
        assert "threshold" in layer
        assert "current_reading" in layer
        assert "status" in layer
        assert "breach" in layer
        assert "headroom" in layer


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_thresholds_match_constants():
    """Layer thresholds in the response must match the DRIFT_THRESHOLDS constants."""
    tool = GetDriftTool()
    result = await tool.run({})
    data = json.loads(result)
    threshold_map = {layer["layer"]: layer["threshold"] for layer in data["layers"]}
    for key, expected in DRIFT_THRESHOLDS.items():
        assert threshold_map[key] == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_with_history():
    """run({"include_history": True}) must add a history key to each layer."""
    tool = GetDriftTool()
    result = await tool.run({"include_history": True})
    data = json.loads(result)
    for layer in data["layers"]:
        assert "history" in layer


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_drift_without_history_has_no_history_key():
    """run({"include_history": False}) must NOT add a history key to layers."""
    tool = GetDriftTool()
    result = await tool.run({"include_history": False})
    data = json.loads(result)
    for layer in data["layers"]:
        assert "history" not in layer


# ---------------------------------------------------------------------------
# aurora_get_ethics_log
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_ethics_log_schema_name():
    """GetEthicsLogTool.schema() must return a Tool named 'aurora_get_ethics_log'."""
    tool = GetEthicsLogTool()
    schema = tool.schema()
    assert isinstance(schema, Tool)
    assert schema.name == "aurora_get_ethics_log"


@pytest.mark.unit
def test_get_ethics_log_schema_has_limit_and_severity():
    """schema().inputSchema must advertise the limit and severity_filter parameters."""
    tool = GetEthicsLogTool()
    schema = tool.schema()
    props = schema.inputSchema["properties"]
    assert "limit" in props
    assert "severity_filter" in props


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_default_returns_valid_json():
    """run({}) must return a JSON string with required top-level keys."""
    tool = GetEthicsLogTool()
    result = await tool.run({})
    data = json.loads(result)
    assert "protocol" in data
    assert "entries" in data
    assert "total_returned" in data
    assert "limit_requested" in data
    assert "retrieved_at" in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_default_limit():
    """run({}) with no args must reflect the default limit of 20."""
    tool = GetEthicsLogTool()
    result = await tool.run({})
    data = json.loads(result)
    assert data["limit_requested"] == 20


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_custom_limit():
    """run({"limit": 5}) must reflect limit_requested == 5."""
    tool = GetEthicsLogTool()
    result = await tool.run({"limit": 5})
    data = json.loads(result)
    assert data["limit_requested"] == 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_limit_capped_at_100():
    """Passing limit > 100 must be capped to 100."""
    tool = GetEthicsLogTool()
    result = await tool.run({"limit": 999})
    data = json.loads(result)
    assert data["limit_requested"] <= 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_severity_filter_reflected():
    """run({"severity_filter": "warning"}) must reflect severity_filter in response."""
    tool = GetEthicsLogTool()
    result = await tool.run({"severity_filter": "warning"})
    data = json.loads(result)
    assert data["severity_filter"] == "warning"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ethics_log_entries_are_list():
    """entries field must be a list."""
    tool = GetEthicsLogTool()
    result = await tool.run({})
    data = json.loads(result)
    assert isinstance(data["entries"], list)


# ---------------------------------------------------------------------------
# aurora_get_capsules
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_capsules_schema_name():
    """GetCapsulesTool.schema() must return a Tool named 'aurora_get_capsules'."""
    tool = GetCapsulesTool()
    schema = tool.schema()
    assert isinstance(schema, Tool)
    assert schema.name == "aurora_get_capsules"


@pytest.mark.unit
def test_get_capsules_schema_has_loaded_only():
    """schema().inputSchema must advertise the loaded_only parameter."""
    tool = GetCapsulesTool()
    schema = tool.schema()
    assert "loaded_only" in schema.inputSchema["properties"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsules_default_returns_valid_json():
    """run({}) must return a JSON string with required top-level keys."""
    tool = GetCapsulesTool()
    result = await tool.run({})
    data = json.loads(result)
    assert "capsules" in data
    assert "total_verified" in data
    assert "loaded_count" in data
    assert "export_ready" in data
    assert "retrieved_at" in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsules_total_verified_matches_constant():
    """total_verified in response must equal TOTAL_VERIFIED_CAPSULES constant."""
    tool = GetCapsulesTool()
    result = await tool.run({})
    data = json.loads(result)
    assert data["total_verified"] == TOTAL_VERIFIED_CAPSULES


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsules_default_returns_all_capsules():
    """run({}) with no filter must return all verified capsules."""
    tool = GetCapsulesTool()
    result = await tool.run({})
    data = json.loads(result)
    assert len(data["capsules"]) == TOTAL_VERIFIED_CAPSULES


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsules_loaded_only_returns_only_loaded():
    """run({"loaded_only": True}) must return only loaded capsules."""
    tool = GetCapsulesTool()
    result = await tool.run({"loaded_only": True})
    data = json.loads(result)
    for capsule in data["capsules"]:
        assert capsule["loaded"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsules_each_has_symbolic_hash():
    """Every capsule in the response must have a symbolic_hash field."""
    tool = GetCapsulesTool()
    result = await tool.run({})
    data = json.loads(result)
    for capsule in data["capsules"]:
        assert "symbolic_hash" in capsule
        assert capsule["symbolic_hash"]  # non-empty
