"""
Tool: aurora_get_agents
========================
Returns the current PAT (Personal Agent Terminal) registry:
  - All registered agents with role, PAT visibility, and status
  - Summary counts (total, available, DND, invisible)

PAT visibility states: Available | DND | Invisible

Backed by GET /api/crew/all. Agent "status" (online/offline)
is mapped to PAT visibility: online → Available, offline → Invisible.
"""

import json
from datetime import datetime, timezone
from mcp.types import Tool

from connector.transport.bridge import (
    CloudbankBridge,
    BridgeError,
    AURORA_PATH_AGENTS,
)


class GetAgentsTool:
    NAME = "aurora_get_agents"
    DESCRIPTION = (
        "Returns the Aurora agent PAT registry. Lists all active agents with "
        "their role, current PAT visibility status (Available/DND/Invisible), "
        "and specialty. Use to understand who is reachable in the current session."
    )

    def schema(self) -> Tool:
        return Tool(
            name=self.NAME,
            description=self.DESCRIPTION,
            inputSchema={
                "type": "object",
                "properties": {
                    "visibility_filter": {
                        "type": "string",
                        "enum": ["all", "available", "dnd", "invisible"],
                        "description": "Filter agents by PAT visibility (default: all)",
                        "default": "all",
                    }
                },
                "required": [],
            },
        )

    async def run(self, arguments: dict) -> str:
        visibility_filter = arguments.get("visibility_filter", "all").lower()

        bridge = CloudbankBridge()
        try:
            raw = await bridge.get(AURORA_PATH_AGENTS)
        except BridgeError as exc:
            return json.dumps({
                "error": str(exc),
                "agents": [],
                "total": 0,
                "available_count": 0,
                "dnd_count": 0,
                "invisible_count": 0,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2)

        agents = []
        for a in raw.get("agents", []):
            status = a.get("status", "offline")
            visibility = "Available" if status in ("online", "active") else "Invisible"
            agents.append({
                "id": a.get("surname", "unknown"),
                "role": a.get("role", "crew"),
                "visibility": visibility,
                "specialty": a.get("clearance", "unspecified"),
            })

        if visibility_filter != "all":
            agents = [a for a in agents if a["visibility"].lower() == visibility_filter]

        data = {
            "agents": agents,
            "total": raw.get("count", len(agents)),
            "available_count": sum(1 for a in agents if a["visibility"] == "Available"),
            "dnd_count": sum(1 for a in agents if a["visibility"] == "DND"),
            "invisible_count": sum(1 for a in agents if a["visibility"] == "Invisible"),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(data, indent=2)
