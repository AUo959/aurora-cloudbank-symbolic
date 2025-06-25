"""
MCP Security & Anchor Validation: Enforce security layers and anchor validation using MCP Bridge Core config.
"""
from modules.symbolic_core import get_mcp_bridge_core
from fastapi import HTTPException, Depends

class MCPSecurity:
    def __init__(self):
        self.mcp = get_mcp_bridge_core()
        self.security_layers = self.mcp.get("security_layers", {})
        self.ethics_protocol = self.mcp.get("ethics_protocol", "")

    def enforce_security(self):
        if self.security_layers.get("drift_lock") != "ACTIVE":
            raise HTTPException(status_code=403, detail="Drift lock not active")
        if self.security_layers.get("guardian_ring") not in ("ACTIVE", "STAGED_ACTIVE"):
            raise HTTPException(status_code=403, detail="Guardian ring not active")
        if self.security_layers.get("ethics_lock") != "ENFORCED":
            raise HTTPException(status_code=403, detail="Ethics lock not enforced")

    def validate_anchor(self, anchor: str):
        # Example: anchor must match MCP anchor_seed
        if anchor != self.mcp.get("anchor_seed"):
            raise HTTPException(status_code=401, detail="Anchor validation failed")

# FastAPI dependency for endpoints
mcp_security = MCPSecurity()
def mcp_security_dependency():
    mcp_security.enforce_security()
