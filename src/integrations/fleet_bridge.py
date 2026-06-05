"""Fleet Bridge: Python-to-JavaScript integration layer.

Exposes Python fleet entities (vessels, probes, drones) via FastAPI endpoints
for consumption by Node.js flight control module.
"""
from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import fleet registries with graceful degradation
try:
    from src.entities.fleet import (
        get_constancy_oppy,
        get_helios_oppy,
        get_liora_oppy,
        get_archimedes_oppy,
        get_pioneer_oppy,
        get_lacewing_oppy,
    )
    FLEET_AVAILABLE = True
except ImportError:
    FLEET_AVAILABLE = False


# Pydantic models for API responses
class CraftProfile(BaseModel):
    """Craft profile matching JS station_types.js schema."""
    id: str
    craft_class: str  # Maps to "class" in JS
    dimensions: Dict[str, float]  # {length, width, height}
    mass_kg: float
    port_type: str
    fuel_type: str
    max_rcs: float
    capabilities: List[str]
    status: str
    maintenance_due_at: Optional[int] = None


class FleetStatus(BaseModel):
    """Overall fleet status summary."""
    total_craft: int
    active_vessels: int
    available_for_ops: int
    in_maintenance: int
    timestamp: str


router = APIRouter(prefix="/api/fleet", tags=["fleet-bridge"])


def _map_vessel_to_craft(vessel_id: str, oppy) -> CraftProfile:
    """Map Python OPPYNavigator to JS CraftProfile schema."""
    # Vessel class mapping based on ID prefix
    vessel_classes = {
        "ORF": "ORS-FRIGATE-CONSTANCY",
        "ORS-01": "ORS-SHUTTLE-XL",
        "ORS-02": "ORS-SHUTTLE-M",
        "ORA": "ORS-SHUTTLE-L",
        "ORP": "ORS-PROBE-SURVEYOR",
        "ORD": "ORS-DRONE-SCOUT",
    }
    
    craft_class = "ORS-SHUTTLE-XL"  # Default
    for prefix, cls in vessel_classes.items():
        if vessel_id.startswith(prefix):
            craft_class = cls
            break
    
    # Dimension/mass defaults by class
    class_specs = {
        "ORS-FRIGATE-CONSTANCY": {"length": 120, "width": 40, "height": 25, "mass": 85000},
        "ORS-SHUTTLE-XL": {"length": 32, "width": 11, "height": 7, "mass": 21000},
        "ORS-SHUTTLE-M": {"length": 24, "width": 9, "height": 6, "mass": 15000},
        "ORS-SHUTTLE-L": {"length": 18, "width": 7, "height": 5, "mass": 9000},
        "ORS-PROBE-SURVEYOR": {"length": 8, "width": 3, "height": 3, "mass": 1200},
        "ORS-DRONE-SCOUT": {"length": 4, "width": 2, "height": 2, "mass": 450},
    }
    specs = class_specs.get(craft_class, class_specs["ORS-SHUTTLE-XL"])
    
    capabilities = ["autodock", "mesh-nav"]
    if hasattr(oppy, "autonomous_mode") and oppy.autonomous_mode:
        capabilities.append("autonomous")
    if hasattr(oppy, "specializations"):
        if oppy.specializations.get("fleet_coordination", 0) > 0.9:
            capabilities.append("relay")
    
    status = "DOCKED"
    if hasattr(oppy, "active_maneuver") and oppy.active_maneuver:
        status = "ACTIVE"
    elif hasattr(oppy, "current_plan") and oppy.current_plan:
        status = "PLANNED"
    
    return CraftProfile(
        id=vessel_id,
        craft_class=craft_class,
        dimensions={
            "length": specs["length"],
            "width": specs["width"],
            "height": specs["height"],
        },
        mass_kg=specs["mass"],
        port_type="RING",
        fuel_type="LH2",
        max_rcs=4000,
        capabilities=capabilities,
        status=status,
        maintenance_due_at=None,
    )


@router.get("/craft", response_model=List[CraftProfile])
async def get_all_craft() -> List[CraftProfile]:
    """Get all registered craft profiles.
    
    Returns craft data compatible with JS station_types.js CraftProfile schema.
    """
    if not FLEET_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Fleet registry unavailable"
        )
    
    craft_list = []
    
    # Map all registered vessels
    vessel_getters = [
        ("ORF-01", get_constancy_oppy),
        ("ORS-01", get_helios_oppy),
        ("ORS-02", get_liora_oppy),
        ("ORA-01", get_archimedes_oppy),
        ("ORP-01", get_pioneer_oppy),
        ("ORD-01", get_lacewing_oppy),
    ]
    
    for vessel_id, getter in vessel_getters:
        try:
            oppy = getter()
            craft = _map_vessel_to_craft(vessel_id, oppy)
            craft_list.append(craft)
        except Exception:
            # Log but continue - partial fleet data is better than none
            # Silently skip failed vessels to avoid log injection
            continue
    
    return craft_list


@router.get("/craft/{craft_id}", response_model=CraftProfile)
async def get_craft_by_id(craft_id: str) -> CraftProfile:
    """Get specific craft profile by ID."""
    if not FLEET_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Fleet registry unavailable"
        )
    
    # Map craft_id to getter
    vessel_map = {
        "ORF-01": get_constancy_oppy,
        "ORS-01": get_helios_oppy,
        "ORS-02": get_liora_oppy,
        "ORA-01": get_archimedes_oppy,
        "ORP-01": get_pioneer_oppy,
        "ORD-01": get_lacewing_oppy,
    }
    
    getter = vessel_map.get(craft_id)
    if not getter:
        raise HTTPException(
            status_code=404,
            detail=f"Craft {craft_id} not found in registry"
        )
    
    try:
        oppy = getter()
        return _map_vessel_to_craft(craft_id, oppy)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


@router.get("/status", response_model=FleetStatus)
async def get_fleet_status() -> FleetStatus:
    """Get overall fleet status summary."""
    if not FLEET_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Fleet registry unavailable"
        )
    
    try:
        all_craft = await get_all_craft()
        active = sum(1 for c in all_craft if c.status in ["ACTIVE", "APPROACH"])
        available = sum(1 for c in all_craft if c.status == "DOCKED")
        maintenance = sum(1 for c in all_craft if c.maintenance_due_at)
        
        return FleetStatus(
            total_craft=len(all_craft),
            active_vessels=active,
            available_for_ops=available,
            in_maintenance=maintenance,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# Export router for FastAPI app.include_router()
__all__ = ["router"]
