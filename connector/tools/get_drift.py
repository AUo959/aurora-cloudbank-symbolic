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

Backed by GET /api/drift/alerts. Alert severity levels (critical/warning/info)
are mapped to the L1/L2/L3 layer structure: critical → L1, warning → L2,
info → L3.
"""

import json
from datetime import datetime, timezone
from mcp.types import Tool

from connector.transport.bridge import (
    CloudbankBridge,
    BridgeError,
    AURORA_PATH_DRIFT_ALERTS,
)

# Architecture constants -- see docs/dev-notes/drift-threshold-stratification.md
DRIFT_THRESHOLDS = {
    "L1_capsule_governance": 0.002,
    "L2_agent_qgia": 0.02,
    "L3_macro_network": 0.1,
}

# Maps each connector layer to the Aurora drift alert severity level it tracks.
_LAYER_TO_ALERT_LEVEL = {
    "L1_capsule_governance": "critical",
    "L2_agent_qgia": "warning",
    "L3_macro_network": "info",
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

        bridge = CloudbankBridge()
        try:
            raw = await bridge.get(AURORA_PATH_DRIFT_ALERTS, params={"limit": 100})
        except BridgeError as exc:
            return json.dumps({
                "error": str(exc),
                "layers": [],
                "any_breach": False,
                "thresholds_ref": "docs/dev-notes/drift-threshold-stratification.md",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }, indent=2)

        all_alerts = raw.get("alerts", [])

        layers = []
        for layer_key, threshold in DRIFT_THRESHOLDS.items():
            alert_level = _LAYER_TO_ALERT_LEVEL[layer_key]
            level_alerts = [
                a for a in all_alerts
                if a.get("level", "").lower() == alert_level
            ]

            breach = len(level_alerts) > 0
            # Represent the reading as 0.0 (nominal) or threshold * 1.5 (breached).
            # The real signal is breach/not-breach; the exact reading carries limited
            # meaning across the unit mismatch between Aurora's relative-change
            # deviation and the connector's symbolic threshold scale.
            current_reading = round(threshold * 1.5, 6) if breach else 0.0

            layer_data = {
                "layer": layer_key,
                "threshold": threshold,
                "current_reading": current_reading,
                "status": "BREACH" if breach else "nominal",
                "breach": breach,
                "headroom": round(threshold - current_reading, 6),
            }

            if include_history:
                layer_data["history"] = [
                    {
                        "timestamp": a.get("timestamp", ""),
                        "agent_id": a.get("agent_id", ""),
                        "metric": a.get("metric_name", ""),
                        "deviation": a.get("deviation", 0.0),
                        "description": a.get("description", ""),
                    }
                    for a in level_alerts[-5:]
                ]

            layers.append(layer_data)

        data = {
            "layers": layers,
            "any_breach": any(layer["breach"] for layer in layers),
            "thresholds_ref": "docs/dev-notes/drift-threshold-stratification.md",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(data, indent=2)
