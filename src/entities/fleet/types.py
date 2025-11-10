"""Shared dataclasses for fleet telemetry and navigation plans."""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


__all__ = ["FleetTelemetry", "NavigationPlan"]


@dataclass
class FleetTelemetry:
    """Real-time telemetry from fleet vessel."""
    vessel_id: str
    timestamp: datetime
    position: Dict[str, float]
    velocity: Dict[str, float]
    acceleration: Dict[str, float]
    anchor_drift: float
    power_status: Dict[str, Any]
    life_support_status: Dict[str, Any]
    crew_status: Dict[str, Any]


@dataclass
class NavigationPlan:
    """OPPY navigation plan for vessel maneuver."""
    plan_id: str
    vessel_id: str
    maneuver_type: str
    delta_v_ms: float
    burn_duration_s: float
    fuel_cost_kg: float
    anchor_impact: float
    risk_assessment: float
    triplex_status: Dict[str, Any]
