"""
Tool: aurora_get_ethics_log
============================
Returns the tail of the GUMAS ethics audit log.

GUMAS (Governs Unified Memory Audit System) records every ethics
check event: protocol invocations, boundary violations, coherence
checks, and symbolic memory merge audits.

The active ethics protocol is Picard_Delta_3.

Backed by POST /gumas/violations. Aurora violation severity levels
(critical/high/medium/low/info) are mapped to connector severity values
(violation/violation/warning/warning/info).
"""

import json
from datetime import datetime, timezone
from mcp.types import Tool

from connector.transport.bridge import (
    CloudbankBridge,
    BridgeError,
    AURORA_PATH_ETHICS_VIOLATIONS,
)

# Maps Aurora violation severities → connector severity labels
_AURORA_TO_CONNECTOR_SEVERITY = {
    "critical": "violation",
    "high": "violation",
    "medium": "warning",
    "low": "warning",
    "info": "info",
}

# Maps connector severity filter → Aurora severity parameter (None means no filter)
_CONNECTOR_TO_AURORA_SEVERITY = {
    "all": None,
    "info": "info",
    "warning": "medium",
    "violation": "critical",
}


class GetEthicsLogTool:
    NAME = "aurora_get_ethics_log"
    DESCRIPTION = (
        "Returns the tail of the GUMAS ethics audit log. "
        "Each entry records an ethics check event: protocol invocation, "
        "boundary check, coherence validation, or symbolic memory merge audit. "
        "Active protocol: Picard_Delta_3."
    )

    def schema(self) -> Tool:
        return Tool(
            name=self.NAME,
            description=self.DESCRIPTION,
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of most recent entries to return (default: 20, max: 100)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "severity_filter": {
                        "type": "string",
                        "enum": ["all", "info", "warning", "violation"],
                        "description": "Filter by severity (default: all)",
                        "default": "all",
                    },
                },
                "required": [],
            },
        )

    async def run(self, arguments: dict) -> str:
        limit = arguments.get("limit", 20)
        severity_filter = arguments.get("severity_filter", "all")

        aurora_severity = _CONNECTOR_TO_AURORA_SEVERITY.get(severity_filter)
        payload: dict = {"limit": limit}
        if aurora_severity:
            payload["severity"] = aurora_severity

        bridge = CloudbankBridge()
        try:
            violations = await bridge.post(AURORA_PATH_ETHICS_VIOLATIONS, payload)
        except BridgeError as exc:
            return json.dumps({
                "error": str(exc),
                "protocol": "Picard_Delta_3",
                "entries": [],
                "total_returned": 0,
                "limit_requested": limit,
                "severity_filter": severity_filter,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2)

        entries = []
        for v in violations:
            aurora_sev = v.get("severity", "info")
            connector_sev = _AURORA_TO_CONNECTOR_SEVERITY.get(aurora_sev, "info")
            entries.append({
                "id": f"{v.get('rule_id', 'unknown')}-{v.get('timestamp', '')[:19]}",
                "timestamp": v.get("timestamp", ""),
                "severity": connector_sev,
                "event_type": v.get("category", "boundary_check"),
                "message": v.get("description", ""),
                "module": v.get("agent_id", "unknown"),
                "protocol": "Picard_Delta_3",
                "outcome": "fail" if v.get("blocked") else "pass",
            })

        data = {
            "protocol": "Picard_Delta_3",
            "entries": entries,
            "total_returned": len(entries),
            "limit_requested": limit,
            "severity_filter": severity_filter,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(data, indent=2)
