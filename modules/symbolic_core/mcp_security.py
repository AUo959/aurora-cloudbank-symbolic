"""
MCP Security & Anchor Validation: Enforce security layers and anchor validation using MCP Bridge Core config.

This module is fully driven by the centralized configuration in mcp_bridge_core.json.
All validation rules, anchor seeds, and ethics protocols are read from the config file.
"""

from typing import Dict, Any
from fastapi import HTTPException

from modules.symbolic_core import get_mcp_bridge_core, validate_security_layer


class MCPSecurity:
    """
    MCP Security manager that enforces security layers and anchor validation.

    All security rules are read from the centralized mcp_bridge_core.json configuration.
    This ensures there is a single source of truth for security policies.
    """

    def __init__(self):
        """Initialize MCPSecurity with configuration from the central config file."""
        self.mcp = get_mcp_bridge_core()
        self.security_layers = self.mcp.get("security_layers", {})
        self.ethics_protocol = self.mcp.get("ethics_protocol", "")
        self.validation_rules = self.mcp.get("security_validation_rules", {})
        self.anchor_validation_config = self.mcp.get("anchor_validation", {})
        self.ethics_enforcement_config = self.mcp.get("ethics_enforcement", {})

    def enforce_security(self) -> None:
        """
        Enforce all security layers according to validation rules from config.

        Raises:
            HTTPException: If any security layer validation fails
        """
        errors = []

        for layer_name, layer_value in self.security_layers.items():
            if not validate_security_layer(layer_name, layer_value, self.mcp):
                layer_rules = self.validation_rules.get(layer_name, {})
                description = layer_rules.get("description", f"{layer_name} validation failed")
                errors.append(f"{layer_name}: {description} (current: {layer_value})")

        if errors:
            raise HTTPException(
                status_code=403,
                detail=f"Security layer validation failed: {'; '.join(errors)}"
            )

    def validate_anchor(self, anchor: str) -> None:
        """
        Validate anchor seed against configuration rules.

        Args:
            anchor: The anchor seed to validate

        Raises:
            HTTPException: If anchor validation fails
        """
        if not self.anchor_validation_config.get("enabled", True):
            return  # Validation disabled

        validation_mode = self.anchor_validation_config.get("validation_mode", "STRICT")
        allowed_seeds = self.anchor_validation_config.get("allowed_seeds", [])

        if validation_mode == "STRICT":
            if anchor not in allowed_seeds:
                raise HTTPException(
                    status_code=401,
                    detail=f"Anchor validation failed: '{anchor}' not in allowed seeds"
                )
        else:
            # Lenient mode: just check if it matches the current seed
            current_seed = self.mcp.get("anchor_seed")
            if anchor != current_seed:
                raise HTTPException(
                    status_code=401,
                    detail=f"Anchor validation failed: expected '{current_seed}'"
                )

    def validate_ethics_protocol(self, protocol: str) -> bool:
        """
        Validate that ethics protocol matches configuration.

        Args:
            protocol: The ethics protocol to validate

        Returns:
            bool: True if protocol is valid
        """
        if not self.ethics_enforcement_config.get("enabled", True):
            return True  # Enforcement disabled

        expected_protocol = self.ethics_enforcement_config.get("protocol", self.ethics_protocol)
        return protocol == expected_protocol

    def get_capsule_security_level(self, capsule_id: str) -> str:
        """
        Get security level for a specific capsule.

        Args:
            capsule_id: ID of the capsule

        Returns:
            str: Security level (HIGH, MEDIUM, LOW) or UNKNOWN
        """
        from modules.symbolic_core import get_capsule
        capsule = get_capsule(capsule_id, self.mcp)
        if capsule:
            return capsule.get("security_level", "UNKNOWN")
        return "UNKNOWN"

    def get_security_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current security state.

        Returns:
            Dict with security layer status, anchor validation, and ethics enforcement
        """
        return {
            "security_layers": self.security_layers,
            "validation_rules": self.validation_rules,
            "anchor_validation": self.anchor_validation_config,
            "ethics_enforcement": self.ethics_enforcement_config,
            "ethics_protocol": self.ethics_protocol,
            "anchor_seed": self.mcp.get("anchor_seed"),
        }


# FastAPI dependency for endpoints
mcp_security = MCPSecurity()


def mcp_security_dependency() -> None:
    """FastAPI dependency that enforces MCP security on endpoints."""
    mcp_security.enforce_security()
