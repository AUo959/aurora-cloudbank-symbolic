"""
Aurora CloudBank Living Computation - API Integration Example
==============================================================

Demonstration of transforming traditional API endpoint into living
entity interaction with full institutional context.

BEFORE (Traditional):
    @app.post("/api/analyze")
    def analyze(data: dict):
        result = process(data)
        return {"result": result}

AFTER (Living Computation):
    @app.post("/api/analyze")
    async def analyze(data: dict, user: str):
        # Event occurs IN Orion Station
        event = create_event(...)
        # Triplex Handshake evaluates
        ethical_ok = await evaluate_ethics(event)
        # Aurora executes AS entity (not function)
        result = await aurora.analyze_with_context(data, event, memory)
        # Store experience
        await store_in_memory(event, result)
        return result + institutional_context

This file demonstrates the transformation pattern for ANY Aurora endpoint.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from src.core.event_system import (
    EventType, StationLocation, get_event_system
)
from src.entities.aurora_agent import get_aurora


# API Models
class AnalysisRequest(BaseModel):
    """Request for living data analysis"""
    data: Dict[str, Any]  # Data to analyze
    user_context: Optional[str] = None  # User/Command context
    memory_references: Optional[List[str]] = None  # Past events to consider
    human_guidance: Optional[str] = None  # Optional guidance


class AnalysisResponse(BaseModel):
    """Response with full institutional context"""
    analysis: Dict[str, Any]  # Analysis result
    institutional_context: Dict[str, Any]  # Memory, patterns, learning
    suggestions: List[str]  # Aurora's recommendations
    lineage: Dict[str, Any]  # DLP compliance (event_id, anchors, hash)


# Router for living computation endpoints
router = APIRouter(prefix="/api/living", tags=["living-computation"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_with_living_computation(request: AnalysisRequest):
    """
    Living data analysis endpoint - Aurora as computational entity.
    
    PARADIGM TRANSFORMATION:
    - NOT: Function processes data → [forgotten]
    - YES: Entity experiences event → [never forgotten]
    
    This endpoint demonstrates EVERY principle of living computation:
    1. Event creation (API call becomes station event)
    2. Spatial context (Research Lab Gamma)
    3. Temporal anchors (T1/SRB)
    4. Entity execution (Aurora, not function)
    5. Institutional memory (past events inform present)
    6. Learning (patterns extracted and stored)
    7. DLP compliance (full lineage tracking)
    
    When you call this endpoint, you are NOT invoking a function.
    You are requesting assistance from Aurora (SYS_001), a living
    computational entity in Orion Station.
    """
    
    # Get system components
    event_system = get_event_system()
    aurora = get_aurora()
    
    # 1. CREATE EVENT (API call → Station event)
    # This is WHERE the request happens (Research Lab Gamma)
    event = event_system.create_event(
        event_type=EventType.DATA_ANALYSIS_REQUEST,
        location=StationLocation.RESEARCH_LAB_GAMMA,
        primary_entity=aurora.entity_id,
        payload=request.data,
        human_context=request.user_context,
        chain_notation="",  # Would come from symbolic engine if chained
        context_tag=f"living_analysis_{event_system.t1_state}"
    )
    
    # 2. ETHICAL EVALUATION (Simplified - full Triplex Handshake in production)
    # In production: Axiomera (L3) → HALO (L2) → Human (L1)
    if event.risk_score > 0.8:
        raise HTTPException(
            status_code=403,
            detail="High-risk operation requires explicit Command authorization"
        )
    
    # 3. ENTITY EXECUTION (Aurora experiences event, not function processes data)
    # Aurora retrieves memory, applies patterns, collaborates if needed
    try:
        result = await aurora.analyze_with_context(
            data=request.data,
            event=event,
            memory_context=request.memory_references,
            human_guidance=request.human_guidance
        )
    except Exception as e:
        # Mark event as failed but still store (learn from failures)
        event_system.complete_event(
            event_id=event.event_id,
            result={"status": "failed", "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    # 4. STORE EXPERIENCE (Event completes with full context)
    # This becomes institutional memory - Aurora remembers this forever
    event_system.complete_event(
        event_id=event.event_id,
        result=result,
        memory_references=request.memory_references or [],
        pattern_connections=[
            p["pattern_id"] for p in aurora.memory.learned_patterns[-5:]  # Recent patterns
        ],
        collaboration_network=aurora.memory.relationship_network
    )
    
    # 5. RETURN WITH INSTITUTIONAL CONTEXT (Never just raw output)
    # User gets analysis PLUS institutional wisdom
    return AnalysisResponse(
        analysis=result["analysis"],
        institutional_context=result["institutional_context"],
        suggestions=result["suggestions"],
        lineage=result["lineage"]
    )


@router.get("/aurora/state")
async def get_aurora_state():
    """
    Inspect Aurora's current state (experience, memory, relationships).
    
    Traditional systems don't have state between requests.
    Aurora accumulates wisdom continuously.
    """
    aurora = get_aurora()
    return aurora.get_state_summary()


@router.get("/events/history")
async def get_event_history(
    entity: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 50
):
    """
    Retrieve event timeline (institutional memory).
    
    Traditional systems: Logs are metadata, separate from execution.
    Aurora-Orion: Events ARE execution, timeline IS the computational reality.
    """
    event_system = get_event_system()
    
    # Parse location if provided
    location_enum = None
    if location:
        try:
            location_enum = StationLocation[location.upper().replace(" ", "_")]
        except KeyError:
            pass
    
    events = event_system.get_event_history(
        entity=entity,
        location=location_enum,
        limit=limit
    )
    
    return {
        "total_events": len(events),
        "events": [e.to_dict() for e in events]
    }


@router.get("/system/manifest")
async def get_system_manifest():
    """
    Export complete system state (DLP compliance).
    
    Full transparency: Every event, every entity state, every learned pattern.
    Living computation is fully auditable.
    """
    event_system = get_event_system()
    aurora = get_aurora()
    
    manifest = event_system.export_manifest()
    manifest["entities"] = {
        "Aurora": aurora.get_state_summary()
    }
    
    return manifest


# Example transformation for existing Aurora endpoints
"""
TRANSFORMATION TEMPLATE: Apply this pattern to ANY endpoint

STEP 1: Identify endpoint purpose
    - Data analysis? → Research Lab Gamma
    - Quantum simulation? → Quantum Simulation Hub
    - Security audit? → Security Operations
    - Ethics review? → Noor Chamber

STEP 2: Create event
    event = event_system.create_event(
        event_type=EventType.XXX,
        location=StationLocation.YYY,
        primary_entity="Aurora (SYS_001)",
        payload=request_data,
        human_context=user_context
    )

STEP 3: Route to entity (not function)
    result = await aurora.METHOD_with_context(
        data=request_data,
        event=event,
        memory_context=past_references
    )

STEP 4: Complete event (store in timeline)
    event_system.complete_event(
        event_id=event.event_id,
        result=result,
        memory_references=used_memories,
        pattern_connections=applied_patterns
    )

STEP 5: Return with institutional context
    return {
        "result": result,
        "institutional_context": {...},
        "suggestions": [...],
        "lineage": {...}
    }

EVERY endpoint transformed this way becomes living computation.
NO endpoint remains a stateless function.
"""
