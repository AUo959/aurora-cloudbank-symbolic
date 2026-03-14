import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("."))

from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration
from src.integrations.shuttle_bay_runtime.assignment import build_assignment_metadata
from src.integrations.shuttle_bay_runtime.catalog import load_catalog_bundle
from src.integrations.shuttle_bay_runtime.controller import ShuttleBayMissionController
from src.integrations.shuttle_bay_runtime.models import PersistenceMode
from src.integrations.shuttle_bay_runtime.policy import evaluate_policy_decision
from src.integrations.shuttle_bay_runtime.routing import resolve_routing_assignment


def test_catalog_bundle_loads_canonical_and_overlay_sources():
    catalog = load_catalog_bundle()
    assert catalog.critical_sources_ready() is True
    assert catalog.source_status["bridge_core"]["loaded"] is True
    assert catalog.source_status["fleet_manifest"]["loaded"] is True
    assert catalog.source_status["integration_config"]["loaded"] is True
    assert catalog.source_status["tool_routing"]["loaded"] is True
    assert catalog.source_status["policy_matrix"]["loaded"] is True


def test_policy_and_routing_cover_all_current_tools():
    integration = ChatGPTAgentModeIntegration()
    catalog = load_catalog_bundle()

    for tool_name in integration.tools_registry:
        routing = resolve_routing_assignment(tool_name, catalog)
        policy = evaluate_policy_decision(tool_name, routing.tool_domain, routing.lane_hint, catalog, True)
        assert routing.tool_domain
        assert routing.shuttle_id
        assert routing.relay_agent
        assert routing.authority_role
        assert policy.policy_action in {"allow", "review", "deny"}


def test_assignment_falls_back_to_role_only_when_no_matching_human_found():
    catalog = load_catalog_bundle()
    routing = resolve_routing_assignment("system_status", catalog)
    assignment = build_assignment_metadata(routing, catalog)

    assert assignment["authority_role"] == "Chief Systems Engineer"
    assert assignment["authority_name"] is None
    assert assignment["human_assignment_confirmed"] is False


def test_controller_marks_symbolic_processing_for_review(tmp_path):
    controller = ShuttleBayMissionController(ChatGPTAgentModeIntegration())
    controller.journal_path = tmp_path / "mission_journal.jsonl"

    result = asyncio.run(
        controller.execute_tool(
            "symbolic_processing",
            {"operation": "diagnostic", "data": {"signal": "alpha"}},
        )
    )

    assert result["success"] is True
    assert result["mission"]["lane"] == "gray"
    assert result["mission"]["review_required"] is True
    assert result["mission"]["tool_domain"] == "symbolic_execution"


def test_controller_denies_symbolic_processing_without_anchor(tmp_path):
    controller = ShuttleBayMissionController(ChatGPTAgentModeIntegration())
    controller.journal_path = tmp_path / "mission_journal.jsonl"
    controller.catalog.bridge_core["anchor_seed"] = ""

    result = asyncio.run(
        controller.execute_tool(
            "symbolic_processing",
            {"operation": "diagnostic", "data": {"signal": "alpha"}},
        )
    )

    assert result["success"] is False
    assert result["mission"]["lane"] == "red"
    assert "anchor" in result["error"].lower()


def test_controller_falls_back_to_memory_journal_when_disk_write_fails():
    controller = ShuttleBayMissionController(ChatGPTAgentModeIntegration())
    controller.journal_path = Path("/dev/null/blocked/mission_journal.jsonl")

    result = asyncio.run(controller.execute_tool("system_status", {"detail_level": "basic"}))

    assert result["success"] is True
    assert controller.persistence_mode == PersistenceMode.MEMORY
    assert len(controller.memory_journal) == 1
    assert controller.memory_journal[0]["mission"]["lane"] == "green"
