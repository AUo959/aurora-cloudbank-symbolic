"""
Tool: aurora_get_agents
========================
Returns the current PAT (Personal Agent Terminal) registry:
  - All registered agents with role, PAT visibility, and status
  - Summary counts (total, available, DND, invisible)

PAT visibility states: Available | DND | Invisible
"""

import json
from datetime import datetime, timezone
from mcp.types import Tool

from connector.transport.bridge import CloudbankBridge


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

        # TODO: Replace stub with bridge call:
        # bridge = CloudbankBridge()
        # data = await bridge.get("/agents", params={"visibility": visibility_filter})

        # --- STUB RESPONSE ---
        agents = [
            {"id": "glyphon", "role": "Symbolic Memory Triad", "visibility": "Available", "specialty": "Glyph encoding, symbolic anchoring"},
            {"id": "axiomera", "role": "Symbolic Memory Triad", "visibility": "Available", "specialty": "Axiomatic reasoning, constraint propagation"},
            {"id": "sentari", "role": "Symbolic Memory Triad", "visibility": "Available", "specialty": "Sentiment threading, emotional coherence"},
            {"id": "caelion", "role": "Nexus", "visibility": "Available", "specialty": "Cross-agent coordination, thread nexus"},
        ]

        if visibility_filter != "all":
            agents = [a for a in agents if a["visibility"].lower() == visibility_filter]

        data = {
            "agents": agents,
            "total": len(agents),
            "available_count": sum(1 for a in agents if a["visibility"] == "Available"),
            "dnd_count": sum(1 for a in agents if a["visibility"] == "DND"),
            "invisible_count": sum(1 for a in agents if a["visibility"] == "Invisible"),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(data, indent=2)
