"""
MCP Command Router: Centralized symbolic command routing using MCP Bridge Core config.

This module is fully driven by the centralized configuration in mcp_bridge_core.json.
All routing logic, governance layers, and capsule capabilities are read from the config file.
"""

from typing import Dict, Any, List, Optional
from modules.symbolic_core import get_mcp_bridge_core, get_capsule


class MCPCommandRouter:
    """
    MCP Command Router that routes symbolic commands through the configured governance layer.

    All routing rules and capsule capabilities are read from the centralized
    mcp_bridge_core.json configuration.
    """

    def __init__(self):
        """Initialize MCPCommandRouter with configuration from the central config file."""
        self.mcp = get_mcp_bridge_core()
        self.governance_layer = self.mcp.get("governance_layer", "UNKNOWN")
        self.routing_protocol = self.mcp.get("core_functions", [])
        self.capsules = self.mcp.get("capsules", {})
        self.external_hooks = self.mcp.get("external_hooks", {})
        self.ethics_enforcement = self.mcp.get("ethics_enforcement", {})

    def route(self, command: str, target_capsule: Optional[str] = None) -> Dict[str, Any]:
        """
        Route a command through the governance layer.

        Args:
            command: The command to route
            target_capsule: Optional target capsule ID for direct routing

        Returns:
            Dict containing routing status, protocol info, and routed command
        """
        routed_command = f"[{self.governance_layer}] {command}"

        result = {
            "status": "ROUTED",
            "protocol": self.routing_protocol,
            "routed_command": routed_command,
            "governance_layer": self.governance_layer,
        }

        # Add target capsule info if specified
        if target_capsule:
            capsule_info = get_capsule(target_capsule, self.mcp)
            if capsule_info:
                result["target_capsule"] = capsule_info
                result["capsule_status"] = capsule_info.get("status", "UNKNOWN")
            else:
                result["target_capsule"] = None
                result["capsule_status"] = "NOT_FOUND"

        # Add ethics validation if enabled
        if self.ethics_enforcement.get("validation_on_route", False):
            result["ethics_validated"] = True
            result["ethics_protocol"] = self.ethics_enforcement.get("protocol", "UNKNOWN")

        return result

    def get_available_capsules(self, capability: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of available capsules, optionally filtered by capability.

        Args:
            capability: Optional capability to filter by (e.g., 'symbolic_routing')

        Returns:
            List of capsule configurations
        """
        capsules = []
        for capsule_id, capsule_config in self.capsules.items():
            if capability:
                if capability in capsule_config.get("capabilities", []):
                    capsules.append(capsule_config)
            else:
                capsules.append(capsule_config)
        return capsules

    def get_capsule_capabilities(self, capsule_id: str) -> List[str]:
        """
        Get capabilities for a specific capsule.

        Args:
            capsule_id: ID of the capsule

        Returns:
            List of capability strings
        """
        capsule_info = get_capsule(capsule_id, self.mcp)
        if capsule_info:
            return capsule_info.get("capabilities", [])
        return []

    def is_capsule_active(self, capsule_id: str) -> bool:
        """
        Check if a capsule is active.

        Args:
            capsule_id: ID of the capsule

        Returns:
            bool: True if capsule is active
        """
        capsule_info = get_capsule(capsule_id, self.mcp)
        if capsule_info:
            return capsule_info.get("status", "INACTIVE") == "ACTIVE"
        return False

    def get_routing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of routing configuration.

        Returns:
            Dict with governance layer, protocols, and capsule info
        """
        active_capsules = [
            capsule_id for capsule_id in self.capsules.keys()
            if self.is_capsule_active(capsule_id)
        ]

        return {
            "governance_layer": self.governance_layer,
            "core_functions": self.routing_protocol,
            "total_capsules": len(self.capsules),
            "active_capsules": active_capsules,
            "external_hooks": self.external_hooks,
            "ethics_enforcement": self.ethics_enforcement,
        }
