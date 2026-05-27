"""
Aurora MCP Tool Registry
=========================
All tool handlers are registered here. Import order determines
the order tools appear in tools/list responses.
"""

from connector.tools.get_state import GetStateTool
from connector.tools.get_agents import GetAgentsTool
from connector.tools.get_drift import GetDriftTool
from connector.tools.get_ethics import GetEthicsLogTool
from connector.tools.get_capsules import GetCapsulesTool

# Registry maps tool name -> tool instance
TOOL_REGISTRY = {
    "aurora_get_state": GetStateTool(),
    "aurora_get_agents": GetAgentsTool(),
    "aurora_get_drift": GetDriftTool(),
    "aurora_get_ethics_log": GetEthicsLogTool(),
    "aurora_get_capsules": GetCapsulesTool(),
}

__all__ = ["TOOL_REGISTRY"]
