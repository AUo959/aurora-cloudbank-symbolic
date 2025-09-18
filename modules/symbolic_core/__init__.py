

_mcp_bridge_core = None


def load_mcp_bridge_core():
    pass
    """Load MCP Bridge Core configuration as a Python dict."""
    mcp_path = Path(__file__).parent / "mcp_bridge_core.json"
    with open(mcp_path, "r") as f:
    pass
    return json.load(f)


def get_mcp_bridge_core():
    pass
    global _mcp_bridge_core
    if _mcp_bridge_core is None:
    pass
    _mcp_bridge_core = load_mcp_bridge_core()
    return _mcp_bridge_core
