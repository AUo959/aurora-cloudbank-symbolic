"""
Tool: aurora_get_drift
=======================
Returns current drift readings against the three-layer stratified
threshold system.

CRITICAL: The threshold values below are architecture constants.
Do NOT change them without reading:
  docs/dev-notes/drift-threshold-stratification.md

Three-layer stratification:
  L1 Capsule / Governance  : 0.002  (tightest - per-capsule symbolic drift)
  L2 Agent / QGIA          : 0.02   (mid-layer - per-agent session drift)
  L3 Macro / Network       : 0.1    (loosest  - cross-network coherence)

The 10x ratio between layers is intentional.
"""

import json
from datetime import datetime, timezone
from mcp.types import Tool

from connector.transport.bridge import CloudbankBridge

# Architecture constants -- see docs/dev-notes/drift-threshold-stratification.md
DRIFT_THRESHOLDS = {
    "L1_capsule_governance": 0.002,
    "L2_agent_qgia": 0.02,
    "L3_macro_network": 0.1,
}


class GetDriftTool:
    NAME = "aurora_get_drift"
    DESCRIPTION = (
        "Returns current drift readings for all three architectural layers against "
        "their stratified thresholds (L1=0.002 capsule, L2=0.02 agent/QGIA, "
        "L3=0.1 macro/network). Reports any active threshold breaches. "
        "See docs/dev-notes/drift-threshold-stratification.md for full rationale."
    )

    def schema(self) -> Tool:
        return Tool(
            name=self.NAME,
            description=self.DESCRIPTION,
            inputSchema={
                "type": "object",
                "properties": {
                    "include_history": {
                        "type": "boolean",
                        "description": "Include last 5 drift readings per layer (default: false)",
                        "default": False,
                    }
                },
                "required": [],
            },
        )

    async def run(self, arguments: dict) -> str:
        include_history = arguments.get("include_history", False)

        # TODO: Replace stub with bridge call:
        # bridge = CloudbankBridge()
        # data = await bridge.get("/drift", params={"history": include_history})

        # --- STUB RESPONSE ---
        layers = []
        for layer_key, threshold in DRIFT_THRESHOLDS.items():
            # Stub: current reading is 0.0 (nominal). Real impl fetches from API.
            current_reading = 0.0
            breach = current_reading > threshold
            layer_data = {
                "layer": layer_key,
                "threshold": threshold,
                "current_reading": current_reading,
                "status": "BREACH" if breach else "nominal",
                "breach": breach,
                "headroom": round(threshold - current_reading, 6),
            }
            if include_history:
                layer_data["history"] = []  # TODO: populate from API
            layers.append(layer_data)

        data = {
            "layers": layers,
            "any_breach": any(layer["breach"] for layer in layers),
            "thresholds_ref": "docs/dev-notes/drift-threshold-stratification.md",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(data, indent=2)
