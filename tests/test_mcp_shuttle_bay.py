import os
import sys
from copy import deepcopy
from contextlib import contextmanager
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))

import aurora_api
import aurora_gui_cloudhub_fastapi


@contextmanager
def preserved_agent_access_state():
    original_hosts = set(aurora_api.app.state.loopback_client_hosts)
    original_token = aurora_api.app.state.agent_control_token
    controller = aurora_api.mcp_shuttle_bay.controller
    original_bridge_core = deepcopy(controller.catalog.bridge_core)
    original_metrics = dict(controller.metrics)
    original_active_missions = controller.active_missions
    original_persistence_mode = controller.persistence_mode
    original_memory_journal = list(controller.memory_journal)
    original_journal_path = controller.journal_path
    try:
        yield
    finally:
        aurora_api.app.state.loopback_client_hosts = original_hosts
        aurora_api.app.state.agent_control_token = original_token
        controller.catalog.bridge_core.clear()
        controller.catalog.bridge_core.update(original_bridge_core)
        controller.metrics.clear()
        controller.metrics.update(original_metrics)
        controller.active_missions = original_active_missions
        controller.persistence_mode = original_persistence_mode
        controller.memory_journal.clear()
        controller.memory_journal.extend(original_memory_journal)
        controller.journal_path = original_journal_path


def test_agent_tools_and_shuttle_manifest_are_json_safe():
    with preserved_agent_access_state():
        aurora_api.mcp_shuttle_bay.controller.journal_path = Path(os.getcwd()) / "data" / "shuttle_bay" / "test_manifest_journal.jsonl"
        with TestClient(aurora_api.app) as client:
            tools_response = client.get("/agent/tools")
            assert tools_response.status_code == 200

            tools_payload = tools_response.json()
            assert "tools" in tools_payload
            assert "handler" not in tools_payload["tools"]["system_status"]
            assert "aurora_command_grammar" in tools_payload["tools"]

            manifest_response = client.get("/mcp/shuttle-bay")
            assert manifest_response.status_code == 200

            manifest = manifest_response.json()
            assert manifest["shuttle_bay"]["transport"] == "http_json_adapter"
            assert manifest["security"]["remote_access_token_env"] == "AURORA_AGENT_CONTROL_TOKEN"
            assert "handler" not in manifest["tools"]["system_status"]
            assert "aurora_command_grammar" in manifest["tools"]
            assert manifest["mission_pipeline"]["policy_mode"] == "policy_first"
            assert len(manifest["resources"]) == 5


def test_remote_shuttle_bay_requires_control_token():
    with preserved_agent_access_state():
        aurora_api.app.state.loopback_client_hosts = {"127.0.0.1", "::1", "localhost"}
        aurora_api.app.state.agent_control_token = "agent-control-secret"
        aurora_api.mcp_shuttle_bay.controller.journal_path = Path(os.getcwd()) / "data" / "shuttle_bay" / "test_remote_journal.jsonl"

        with TestClient(aurora_api.app) as client:
            unauthorized = client.get("/mcp/shuttle-bay")
            assert unauthorized.status_code == 401

            forbidden = client.get("/mcp/shuttle-bay", headers={"Authorization": "Bearer wrong-secret"})
            assert forbidden.status_code == 401

            authorized = client.get(
                "/mcp/shuttle-bay",
                headers={"Authorization": "Bearer agent-control-secret"},
            )
            assert authorized.status_code == 200

            execute_response = client.post(
                "/mcp/shuttle-bay/execute",
                headers={"Authorization": "Bearer agent-control-secret"},
                json={"tool_name": "system_status", "parameters": {"detail_level": "basic"}},
            )
            assert execute_response.status_code == 200
            assert execute_response.json()["success"] is True
            assert execute_response.json()["mission"]["lane"] == "green"
            assert execute_response.json()["mission"]["policy_action"] == "allow"


def test_shuttle_bay_gray_lane_and_red_lane_behavior():
    with preserved_agent_access_state():
        aurora_api.mcp_shuttle_bay.controller.journal_path = Path(os.getcwd()) / "data" / "shuttle_bay" / "test_lane_journal.jsonl"

        with TestClient(aurora_api.app) as client:
            gray_response = client.post(
                "/mcp/shuttle-bay/execute",
                json={"tool_name": "symbolic_processing", "parameters": {"operation": "diagnostic", "data": {"signal": "alpha"}}},
            )
            assert gray_response.status_code == 200
            gray_payload = gray_response.json()
            assert gray_payload["success"] is True
            assert gray_payload["mission"]["lane"] == "gray"
            assert gray_payload["mission"]["review_required"] is True

            aurora_api.mcp_shuttle_bay.controller.catalog.bridge_core["anchor_seed"] = ""
            red_response = client.post(
                "/mcp/shuttle-bay/execute",
                json={"tool_name": "symbolic_processing", "parameters": {"operation": "diagnostic", "data": {"signal": "alpha"}}},
            )
            assert red_response.status_code == 200
            red_payload = red_response.json()
            assert red_payload["success"] is False
            assert red_payload["mission"]["lane"] == "red"


def test_legacy_mcp_bridge_routes_remain_available():
    with TestClient(aurora_gui_cloudhub_fastapi.app) as client:
        bridge_response = client.get("/mcp_bridge")
        assert bridge_response.status_code == 200
        assert bridge_response.json()["legacy_bridge"] is True

        route_response = client.post(
            "/mcp_bridge/route_command",
            json={"command": "mesh.status", "anchor": "EOS_SEED_ORION"},
        )
        assert route_response.status_code == 200
        payload = route_response.json()
        assert payload["status"] == "ROUTED"
        assert payload["legacy_bridge"] is True


def test_cloud_gui_lifespan_clears_connection_state():
    aurora_gui_cloudhub_fastapi.connections.append(object())  # type: ignore[arg-type]

    with TestClient(aurora_gui_cloudhub_fastapi.app):
        assert aurora_gui_cloudhub_fastapi.connections == []
        aurora_gui_cloudhub_fastapi.connections.append(object())  # type: ignore[arg-type]

    assert aurora_gui_cloudhub_fastapi.connections == []


def test_mcp_jsonrpc_endpoint_supports_initialize_tools_and_resources():
    with preserved_agent_access_state():
        aurora_api.mcp_shuttle_bay.controller.journal_path = Path(os.getcwd()) / "data" / "shuttle_bay" / "test_jsonrpc_journal.jsonl"
        with TestClient(aurora_api.app) as client:
            initialize_response = client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            )
            assert initialize_response.status_code == 200
            initialize_result = initialize_response.json()["result"]
            assert initialize_result["serverInfo"]["name"] == "aurora-mcp-shuttle-bay"

            tools_response = client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            )
            assert tools_response.status_code == 200
            tools = tools_response.json()["result"]["tools"]
            assert any(tool["name"] == "system_status" for tool in tools)
            assert any(tool["name"] == "aurora_command_grammar" for tool in tools)

            resources_response = client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 5, "method": "resources/list", "params": {}},
            )
            assert resources_response.status_code == 200
            resource_uris = [resource["uri"] for resource in resources_response.json()["result"]["resources"]]
            assert "aurora://mcp-shuttle-bay/fleet" in resource_uris
            assert "aurora://mcp-shuttle-bay/policy" in resource_uris

            call_response = client.post(
                "/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "system_status", "arguments": {"detail_level": "basic"}},
                },
            )
            assert call_response.status_code == 200
            structured = call_response.json()["result"]["structuredContent"]
            assert structured["success"] is True
            assert structured["mission"]["lane"] == "green"

            resource_response = client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 4, "method": "resources/read", "params": {"uri": "aurora://mcp-shuttle-bay/manifest"}},
            )
            assert resource_response.status_code == 200
            resource_text = resource_response.json()["result"]["contents"][0]["text"]
            assert "aurora-mcp-shuttle-bay" in resource_text

            fleet_resource_response = client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 6, "method": "resources/read", "params": {"uri": "aurora://mcp-shuttle-bay/fleet"}},
            )
            assert fleet_resource_response.status_code == 200
            assert "SHUTTLE_01_AURORA" in fleet_resource_response.json()["result"]["contents"][0]["text"]


def test_shuttle_bay_status_exposes_pipeline_metadata():
    with preserved_agent_access_state():
        with TestClient(aurora_api.app) as client:
            status_response = client.get("/mcp/shuttle-bay/status")
            assert status_response.status_code == 200
            payload = status_response.json()
            assert payload["pipeline_readiness"]["ready"] is True
            assert "tool_routing" in payload["loaded_sources"]
            assert "policy_matrix" in payload["loaded_sources"]
            assert "active" in payload["mission_counters"]
            assert "persistence_mode" in payload["degraded_modes"]


def test_remote_mcp_jsonrpc_requires_control_token():
    with preserved_agent_access_state():
        aurora_api.app.state.loopback_client_hosts = {"127.0.0.1", "::1", "localhost"}
        aurora_api.app.state.agent_control_token = "agent-control-secret"

        with TestClient(aurora_api.app) as client:
            unauthorized = client.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {}},
            )
            assert unauthorized.status_code == 401

            authorized = client.post(
                "/mcp",
                headers={"Authorization": "Bearer agent-control-secret"},
                json={"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {}},
            )
            assert authorized.status_code == 200
            assert authorized.json()["result"] == {}
