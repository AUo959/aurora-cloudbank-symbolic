import json
from pathlib import Path
from typing import Dict, Any, Optional

_mcp_bridge_core = None


def load_mcp_configuration() -> Dict[str, Any]:
    """
    Load MCP Bridge Core configuration from the centralized JSON file.

    This is the single authoritative source of truth for:
    - Capsule definitions and their security context
    - Security layer validation rules
    - Anchor seed and ethics protocol enforcement
    - External hooks and governance layers

    Returns:
        Dict[str, Any]: Complete MCP configuration dictionary

    Raises:
        FileNotFoundError: If configuration file is missing
        json.JSONDecodeError: If configuration file is invalid JSON
    """
    mcp_path = Path(__file__).parent / "mcp_bridge_core.json"
    with open(mcp_path, "r") as f:
        return json.load(f)


def load_mcp_bridge_core():
    """
    Load MCP Bridge Core configuration as a Python dict.

    Deprecated: Use load_mcp_configuration() instead for better naming clarity.
    """
    return load_mcp_configuration()


def get_mcp_bridge_core():
    """
    Get cached MCP Bridge Core configuration.

    Returns cached configuration if available, otherwise loads from file.
    This ensures configuration is loaded only once per process.
    """
    global _mcp_bridge_core
    if _mcp_bridge_core is None:
        _mcp_bridge_core = load_mcp_configuration()
    return _mcp_bridge_core


def validate_security_layer(layer_name: str, layer_value: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Validate a security layer value against configuration rules.

    Args:
        layer_name: Name of the security layer (e.g., 'drift_lock')
        layer_value: Current value of the security layer
        config: Optional MCP configuration dict (loads from cache if not provided)

    Returns:
        bool: True if the security layer value is valid according to rules
    """
    if config is None:
        config = get_mcp_bridge_core()

    validation_rules = config.get("security_validation_rules", {})
    layer_rules = validation_rules.get(layer_name, {})

    if not layer_rules:
        # No rules defined, accept any value
        return True

    # Check against required_state (single value)
    if "required_state" in layer_rules:
        return layer_value == layer_rules["required_state"]

    # Check against required_states (multiple acceptable values)
    if "required_states" in layer_rules:
        return layer_value in layer_rules["required_states"]

    # Fallback: check if value is in valid_states
    valid_states = layer_rules.get("valid_states", [])
    return layer_value in valid_states


def get_capsule(capsule_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Get capsule configuration by ID.

    Args:
        capsule_id: ID of the capsule (e.g., 'OPPY', 'ARCHY')
        config: Optional MCP configuration dict (loads from cache if not provided)

    Returns:
        Optional[Dict[str, Any]]: Capsule configuration or None if not found
    """
    if config is None:
        config = get_mcp_bridge_core()

    capsules = config.get("capsules", {})
    return capsules.get(capsule_id)
