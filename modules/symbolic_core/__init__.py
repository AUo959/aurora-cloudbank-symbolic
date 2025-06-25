import json
from pathlib import Path

_mcp_bridge_core = None

def load_mcp_bridge_core():
    """Load MCP Bridge Core configuration as a Python dict."""
    mcp_path = Path(__file__).parent / "mcp_bridge_core.json"
    with open(mcp_path, "r") as f:
        return json.load(f)

def get_mcp_bridge_core():
    global _mcp_bridge_core
    if _mcp_bridge_core is None:
        _mcp_bridge_core = load_mcp_bridge_core()
    return _mcp_bridge_core