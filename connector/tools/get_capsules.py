"""
Tool: aurora_get_capsules
==========================
Returns the Aurora capsule module registry.

Aurora has 13 verified capsule modules. Each capsule encapsulates
a discrete capability set. This tool reports load status, export
readiness, and symbolic hash for each.

Capsule categories follow the QUANTUM_FORGE engine schema:
  Knowledge (Ev/In/B), SymbolicMemory Merge, Ethics Audit Log
"""

import json
from datetime import datetime, timezone
from mcp.types import Tool

from connector.transport.bridge import CloudbankBridge

TOTAL_VERIFIED_CAPSULES = 13


class GetCapsulesTool:
    NAME = "aurora_get_capsules"
    DESCRIPTION = (
        "Returns the Aurora capsule module registry. "
        "Reports load status, export readiness, and symbolic hash for all "
        f"{TOTAL_VERIFIED_CAPSULES} verified capsule modules. "
        "Capsule categories: Knowledge (Ev/In/B), SymbolicMemory Merge, Ethics Audit Log."
    )

    def schema(self) -> Tool:
        return Tool(
            name=self.NAME,
            description=self.DESCRIPTION,
            inputSchema={
                "type": "object",
                "properties": {
                    "loaded_only": {
                        "type": "boolean",
                        "description": "Return only currently loaded capsules (default: false)",
                        "default": False,
                    }
                },
                "required": [],
            },
        )

    async def run(self, arguments: dict) -> str:
        loaded_only = arguments.get("loaded_only", False)

        # TODO: Replace stub with bridge call:
        # bridge = CloudbankBridge()
        # data = await bridge.get("/capsules", params={"loaded_only": loaded_only})

        # --- STUB RESPONSE (shape-correct, IDs are placeholders) ---
        capsules = [
            {"id": f"CAPSULE-{i:03d}", "name": f"CapsuleModule-{i}",
             "loaded": True, "export_ready": True,
             "symbolic_hash": f"SYM_HASH_{i:03d}_STUB",
             "category": "Knowledge"}
            for i in range(1, TOTAL_VERIFIED_CAPSULES + 1)
        ]

        if loaded_only:
            capsules = [c for c in capsules if c["loaded"]]

        data = {
            "capsules": capsules,
            "total_verified": TOTAL_VERIFIED_CAPSULES,
            "loaded_count": sum(1 for c in capsules if c["loaded"]),
            "export_ready": all(c["export_ready"] for c in capsules),
            "engine": "gpt-symbolic-memetic",
            "binding": "Aurora_Core_Flowstate",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(data, indent=2)
