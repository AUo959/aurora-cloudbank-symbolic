"""
Tool: aurora_get_capsules
==========================
Returns the Aurora capsule module registry.

Each Aurora component registered in the synergy registry is surfaced
here as a capsule. Components with status "active" are considered
loaded and export-ready.

Capsule categories are inferred from component names/descriptions:
  Knowledge, Ethics, Memory, Quantum, Observability, Security, Core

Backed by GET /synergy/components.
"""

import hashlib
import json
from datetime import datetime, timezone
from mcp.types import Tool

from connector.transport.bridge import (
    CloudbankBridge,
    BridgeError,
    AURORA_PATH_COMPONENTS,
)


def _infer_category(name: str, description: str) -> str:
    """Infer a capsule category from component name and description keywords."""
    text = (name + " " + description).lower()
    if any(k in text for k in ("ethics", "gumas", "compliance", "audit")):
        return "Ethics Audit Log"
    if any(k in text for k in ("memory", "aumem", "symbolic")):
        return "SymbolicMemory Merge"
    if any(k in text for k in ("quantum", "forge", "simulator")):
        return "Knowledge (Ev)"
    if any(k in text for k in ("observ", "telemetry", "drift", "monitor")):
        return "Knowledge (In)"
    if any(k in text for k in ("security", "guardian", "auth", "csrf")):
        return "Knowledge (B)"
    return "Knowledge"


def _symbolic_hash(name: str, version: str) -> str:
    """Derive a stable symbolic hash from component identity."""
    raw = f"{name}:{version}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
    return f"SYM_HASH_{digest}"


class GetCapsulesTool:
    NAME = "aurora_get_capsules"
    DESCRIPTION = (
        "Returns the Aurora capsule module registry. "
        "Reports load status, export readiness, and symbolic hash for all "
        "registered capsule modules. "
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

        bridge = CloudbankBridge()
        try:
            components = await bridge.get(AURORA_PATH_COMPONENTS)
        except BridgeError as exc:
            return json.dumps({
                "error": str(exc),
                "capsules": [],
                "total_verified": 0,
                "loaded_count": 0,
                "export_ready": False,
                "engine": "gpt-symbolic-memetic",
                "binding": "Aurora_Core_Flowstate",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2)

        capsules = []
        for i, comp in enumerate(components, start=1):
            is_active = comp.get("status", "") == "active"
            capsules.append({
                "id": f"CAPSULE-{i:03d}",
                "name": comp.get("name", f"CapsuleModule-{i}"),
                "loaded": is_active,
                "export_ready": is_active,
                "symbolic_hash": _symbolic_hash(
                    comp.get("name", f"module-{i}"),
                    comp.get("version", "0.0.0"),
                ),
                "category": _infer_category(
                    comp.get("name", ""),
                    comp.get("description", ""),
                ),
            })

        if loaded_only:
            capsules = [c for c in capsules if c["loaded"]]

        data = {
            "capsules": capsules,
            "total_verified": len(capsules),
            "loaded_count": sum(1 for c in capsules if c["loaded"]),
            "export_ready": all(c["export_ready"] for c in capsules) if capsules else False,
            "engine": "gpt-symbolic-memetic",
            "binding": "Aurora_Core_Flowstate",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(data, indent=2)
