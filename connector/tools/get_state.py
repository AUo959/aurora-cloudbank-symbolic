"""
Tool: aurora_get_state
=======================
Returns Aurora's current system-level symbolic state:
  - Active vector state identifier
  - Current lockpoint timestamp
  - Ethics protocol in force
  - Deployment bundle
  - EchoChain loop set
  - Active module list
  - Layer state flags
"""

import json
from datetime import datetime, timezone
from mcp.types import Tool

from connector.transport.bridge import (
    CloudbankBridge,
    BridgeError,
    AURORA_PATH_HEALTH,
    AURORA_PATH_DRIFT_ALERTS,
)


class GetStateTool:
    NAME = "aurora_get_state"
    DESCRIPTION = (
        "Returns Aurora's current symbolic system state including vector state, "
        "lockpoint, ethics protocol, active modules, and layer flags. "
        "Use this as the first call to orient any Aurora session."
    )

    def schema(self) -> Tool:
        return Tool(
            name=self.NAME,
            description=self.DESCRIPTION,
            inputSchema={
                "type": "object",
                "properties": {
                    "include_echochain": {
                        "type": "boolean",
                        "description": "Include EchoChain loop details in response (default: true)",
                        "default": True,
                    }
                },
                "required": [],
            },
        )

    async def run(self, arguments: dict) -> str:
        include_echochain = arguments.get("include_echochain", True)

        bridge = CloudbankBridge()
        try:
            health = await bridge.get(AURORA_PATH_HEALTH)
        except BridgeError as exc:
            return json.dumps({
                "error": str(exc),
                "vector_state": "UNAVAILABLE",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2)

        components = health.get("components", {})
        active_modules = [name.upper() for name, ok in components.items() if ok]
        lockpoint_ts = (
            health.get("timestamp", datetime.now(timezone.utc).isoformat())
            .replace("-", "").replace(":", "")[:15]
        )

        data = {
            "vector_state": "QEM-SN1-ACTIVE::BASELINE_V1",
            "lockpoint": f"SN1_LOCKPOINT_{lockpoint_ts}Z",
            "ethics_protocol": "Picard_Delta_3",
            "deployment_bundle": "Aurora_MasterDeploymentBundle_v1.0",
            "layer_state": {
                "symbolic_governed": True,
                "ethics_verified": bool(components.get("insight_ledger")),
                "recovery_threaded": health.get("status") == "healthy",
            },
            "active_modules": active_modules,
            "cg_vector_state": "Active vector QEM-SN1-ACTIVE::BASELINE_V1",
            "restore_ritual": "RESETCORE",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        if include_echochain:
            try:
                drift_raw = await bridge.get(AURORA_PATH_DRIFT_ALERTS, params={"limit": 5})
                recent_alerts = drift_raw.get("alerts", [])
                linked = [
                    f"DRIFT::{a.get('agent_id', 'unknown').upper()}::{a.get('metric_name', '')}"
                    for a in recent_alerts[:3]
                ]
            except BridgeError:
                linked = []
            data["echochain"] = {
                "loop_set": "LOOPSET_001",
                "linked": linked if linked else ["DRIFTTRACE::REI"],
            }

        return json.dumps(data, indent=2)
