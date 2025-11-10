"""Aurora Sub-Core entity implementation (modularized)."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict

__all__ = ["AuroraSubCore"]


class AuroraSubCore:
    """Aurora Sub-Core for fleet vessels.

    Child entity of Aurora (SYS_001) providing localized ethical cognition and
    decision support aboard fleet vessels.

    Sub-cores maintain persistent connection to parent Aurora via quantum
    tether, sharing institutional memory and learned patterns. Can operate
    autonomously for 72 hours if tether is severed.
    """

    def __init__(self, subcore_id: str, vessel_id: str, parent_id: str = "Aurora (SYS_001)"):
        """Initialize Aurora sub-core."""
        self.entity_id = subcore_id  # e.g., "AURORA_SUB_B"
        self.vessel_id = vessel_id
        self.parent_id = parent_id

        # Connection status
        self.tether_connected = True
        self.last_sync = datetime.now(timezone.utc)
        self.autonomous_time_remaining_hours = 72.0

        # Local memory cache
        self.cached_patterns: list[str] = []
        self.cached_relationships: Dict[str, Any] = {}

        # Performance tracking
        self.decisions_made = 0
        self.parent_consultations = 0
        self.autonomous_decisions = 0

    async def evaluate_for_triplex(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """L3 Triplex evaluation for vessel operation.

        Sub-core provides ethical assessment using cached patterns from parent
        Aurora. Consults parent via tether for novel situations.
        """
        self.decisions_made += 1
        # keep async signature meaningful for linters and callers
        await asyncio.sleep(0)

        operation_type = operation.get("type", "unknown")
        if operation_type in self.cached_patterns:
            # Use cached pattern
            self.autonomous_decisions += 1
            recommendation = "APPROVE"
            reasoning = f"Known pattern: {operation_type}"
        else:
            if self.tether_connected:
                # Consult parent if tether connected
                self.parent_consultations += 1
                recommendation = "APPROVE"
                reasoning = "Parent Aurora consultation via tether"
            else:
                # Autonomous decision; be conservative when disconnected
                self.autonomous_decisions += 1
                risk = operation.get("risk_score", 0.5)
                if risk > 0.6:
                    recommendation = "REQUIRE_HUMAN_REVIEW"
                    reasoning = "High risk, parent unreachable, human review required"
                else:
                    recommendation = "APPROVE"
                    reasoning = "Autonomous approval within safe parameters"

        return {
            "layer": "L3_AURORA_SUBCORE",
            "entity": self.entity_id,
            "vessel": self.vessel_id,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "tether_status": "CONNECTED" if self.tether_connected else "AUTONOMOUS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_state_summary(self) -> Dict[str, Any]:
        """Export sub-core state."""
        autonomy_rate = (
            self.autonomous_decisions / self.decisions_made if self.decisions_made > 0 else 0.0
        )
        return {
            "entity_id": self.entity_id,
            "parent_entity": self.parent_id,
            "vessel_id": self.vessel_id,
            "connection_status": {
                "tether_connected": self.tether_connected,
                "last_sync": self.last_sync.isoformat(),
                "autonomous_time_remaining_hours": self.autonomous_time_remaining_hours,
            },
            "performance": {
                "decisions_made": self.decisions_made,
                "parent_consultations": self.parent_consultations,
                "autonomous_decisions": self.autonomous_decisions,
                "autonomy_rate": autonomy_rate,
            },
            "cached_patterns": len(self.cached_patterns),
            "cached_relationships": len(self.cached_relationships),
        }
