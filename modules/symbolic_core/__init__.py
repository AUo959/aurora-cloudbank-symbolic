import json
from pathlib import Path

def load_mcp_bridge_core():
    """Load MCP Bridge Core configuration as a Python dict."""
    mcp_path = Path(__file__).parent / "mcp_bridge_core.json"
    with open(mcp_path, "r") as f:
        return json.load(f)