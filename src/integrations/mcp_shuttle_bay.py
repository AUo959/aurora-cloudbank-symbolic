"""
Structured MCP shuttle-bay adapter for Aurora tool discovery and execution.
"""

import json
from typing import Any, Dict, Optional

from src.integrations.chatgpt_agent_mode import (
    ChatGPTAgentModeIntegration,
    chatgpt_agent_integration,
)
from src.integrations.shuttle_bay_runtime import ShuttleBayMissionController
from src.integrations.shuttle_bay_runtime.policy import evaluate_policy_decision
from src.integrations.shuttle_bay_runtime.resources import MANIFEST_RESOURCE_URI
from src.integrations.shuttle_bay_runtime.routing import resolve_routing_assignment


class MCPShuttleBayAdapter:
    """Expose Aurora's agent-mode tool surface through a stable shuttle-bay contract."""

    READ_ONLY_TOOLS = {"aurora_command_grammar", "geometric_algebra", "system_status"}
    MANIFEST_RESOURCE_URI = MANIFEST_RESOURCE_URI

    def __init__(self, agent_integration: Optional[ChatGPTAgentModeIntegration] = None):
        self.agent_integration = agent_integration or chatgpt_agent_integration
        self.controller = ShuttleBayMissionController(self.agent_integration)

    async def get_manifest(self) -> Dict[str, Any]:
        tools_info = await self.agent_integration.discover_tools()
        return self.controller.build_manifest(tools_info)

    async def discover_tools(self) -> Dict[str, Any]:
        return await self.agent_integration.discover_tools()

    async def execute_tool(
        self, tool_name: str, parameters: Dict[str, Any], session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.controller.execute_tool(tool_name=tool_name, parameters=parameters, session_id=session_id)

    async def manage_session(
        self,
        action: str,
        session_id: Optional[str] = None,
        state_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self.agent_integration.execute_tool(
            tool_name="session_management",
            parameters={
                "action": action,
                "session_id": session_id,
                "state_data": state_data or {},
            },
        )

    async def get_status(self) -> Dict[str, Any]:
        return await self.controller.get_status()

    async def get_mcp_server_descriptor(self) -> Dict[str, Any]:
        bridge_core = self.controller.catalog.bridge_core
        return {
            "protocolVersion": "2025-03-26",
            "serverInfo": {
                "name": "aurora-mcp-shuttle-bay",
                "version": bridge_core.get("version", "1.0.0"),
            },
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"listChanged": False},
            },
        }

    async def list_mcp_tools(self) -> Dict[str, Any]:
        tools_info = await self.discover_tools()
        annotations_by_tool = {
            tool_name: self._tool_policy_annotations(tool_name) for tool_name in tools_info.get("tools", {})
        }
        return {
            "tools": [
                {
                    "name": tool_name,
                    "description": tool_def.get("description", ""),
                    "inputSchema": tool_def.get("parameters", {"type": "object", "properties": {}}),
                    "annotations": {
                        "readOnlyHint": tool_name in self.READ_ONLY_TOOLS,
                        "destructiveHint": annotations_by_tool[tool_name]["destructiveHint"],
                        "openWorldHint": annotations_by_tool[tool_name]["openWorldHint"],
                    },
                }
                for tool_name, tool_def in tools_info.get("tools", {}).items()
            ]
        }

    async def call_mcp_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = await self.execute_tool(tool_name, arguments or {}, session_id=session_id)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, default=str),
                }
            ],
            "structuredContent": result,
            "isError": not result.get("success", True),
        }

    async def list_mcp_resources(self) -> Dict[str, Any]:
        return self.controller.list_resources()

    async def read_mcp_resource(self, uri: str) -> Dict[str, Any]:
        tools_info = await self.agent_integration.discover_tools()
        return self.controller.read_resource(uri, tools_info)

    def _tool_policy_annotations(self, tool_name: str) -> Dict[str, bool]:
        try:
            routing = resolve_routing_assignment(tool_name, self.controller.catalog)
            policy = evaluate_policy_decision(
                tool_name=tool_name,
                tool_domain=routing.tool_domain,
                lane_hint=routing.lane_hint,
                catalog=self.controller.catalog,
                tool_schema_present=tool_name in self.agent_integration.tools_registry,
            )
            return {
                "destructiveHint": policy.destructive,
                "openWorldHint": policy.external,
            }
        except ValueError:
            return {
                "destructiveHint": False,
                "openWorldHint": False,
            }


mcp_shuttle_bay = MCPShuttleBayAdapter()
