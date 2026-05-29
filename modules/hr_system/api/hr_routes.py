"""HR System API Routes

FastAPI endpoints for staffing analysis and character generation.

Anchor: T1-HRS-001
DLP Context: hr_system_api
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses


class StaffingNeedRequest(BaseModel):
    """Request model for staffing need analysis"""
    department: str = Field(..., description="Department name")
    context_tag: Optional[str] = Field(None, description="DLP context tag")


class StaffingNeedResponse(BaseModel):
    """Response model for staffing need analysis"""
    department: str
    current_staff: int
    recommended_staff: int
    gap_analysis: Dict[str, int]
    priority: str
    rationale: str


class CharacterGenerationRequest(BaseModel):
    """Request model for character generation"""
    role: str = Field(..., description="Role/position")
    department: str = Field(..., description="Department")
    skills_required: Optional[List[str]] = Field(None, description="Required skills")
    context_tag: Optional[str] = Field(None, description="DLP context tag")


class CharacterProfile(BaseModel):
    """Character profile response"""
    name: str
    role: str
    department: str
    skills: List[str]
    background: str
    personality_traits: List[str]
    quantum_properties: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    module: str
    version: str


# Create router
router = APIRouter(prefix="/hr_system", tags=["HR System"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for HR System module"""
    return {
        "status": "operational",
        "module": "hr_system",
        "version": "1.0.0"
    }


@router.post("/analyze_staffing", response_model=StaffingNeedResponse)
async def analyze_staffing_needs(request: StaffingNeedRequest):
    """Analyze staffing needs for a department
    
    Returns staffing gap analysis and recommendations.
    """
    try:
        from modules.hr_system.core.staffing_analyzer import StaffingAnalyzer

        analyzer = StaffingAnalyzer()
        result = analyzer.analyze_department_needs(
            department=request.department,
            context_tag=request.context_tag
        )

        return result

    except (ImportError, NotImplementedError) as exc:
        # #761: degraded-fallback contract -- response carries explicit
        # flags so callers can detect they're getting mock data and
        # NOT, e.g., accidentally pipe it into a real staffing decision.
        logger.warning("StaffingAnalyzer unavailable (%s); returning flagged mock data", exc)
        return {
            "department": request.department,
            "current_staff": 10,
            "recommended_staff": 12,
            "gap_analysis": {"general": 2},
            "priority": "MEDIUM",
            "rationale": "Staffing analyzer not yet fully implemented",
            "degraded": True,
            "_implementation_status": "mock_fallback",
            "_unavailable_reason": str(exc),
        }
    except Exception as e:
        logger.error("Staffing analysis failed: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_character", response_model=CharacterProfile)
async def generate_character(request: CharacterGenerationRequest):
    """Generate a quantum-symbolic character profile
    
    Creates crew member profile with skills, background, and personality.
    """
    try:
        from modules.hr_system.core.character_generator import CharacterGenerator
        
        generator = CharacterGenerator()
        character = generator.generate_profile(
            role=request.role,
            department=request.department,
            skills_required=request.skills_required or [],
            context_tag=request.context_tag
        )
        
        return character
        
    except (ImportError, NotImplementedError) as exc:
        # #761: degraded-fallback contract -- same explicit flags as the
        # other HR routes so clients can detect mock responses.
        logger.warning("CharacterGenerator unavailable (%s); returning flagged mock data", exc)
        return {
            "name": f"Officer_{request.role[:3].upper()}",
            "role": request.role,
            "department": request.department,
            "skills": request.skills_required or ["Leadership", "Problem Solving"],
            "background": "Experienced professional with diverse background",
            "personality_traits": ["Analytical", "Team-oriented", "Adaptive"],
            "quantum_properties": {
                "coherence": 0.85,
                "entanglement_potential": 0.72,
                "symbolic_resonance": "high"
            },
            "degraded": True,
            "_implementation_status": "mock_fallback",
            "_unavailable_reason": str(exc),
        }
    except Exception as e:
        logger.error("Character generation failed: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organizational_intel")
async def get_organizational_intelligence(
    department: Optional[str] = Query(None, description="Filter by department")
):
    """Get organizational intelligence and capacity planning
    
    Returns department structure, capacity, and staffing insights.
    """
    try:
        from modules.hr_system.core.organizational_intelligence import OrganizationalIntelligence
        
        intel = OrganizationalIntelligence()
        data = intel.get_capacity_analysis(department=department)
        
        return data
        
    except (ImportError, NotImplementedError) as exc:
        # #761: OrganizationalIntelligence is shipped as a stub
        # (modules/hr_system/core/organizational_intelligence.py) that
        # raises NotImplementedError; the catch covers the legacy
        # ImportError case too. The response is flagged so clients
        # never treat the mock as authoritative capacity data.
        logger.warning(
            "OrganizationalIntelligence unavailable (%s); returning flagged mock data", exc
        )
        return {
            "departments": ["Security", "Engineering", "Science", "Medical", "Operations"],
            "total_capacity": 100,
            "current_utilization": 0.78,
            "growth_trajectory": "expanding",
            "recommendation": "Organizational intelligence system not yet fully implemented",
            "degraded": True,
            "_implementation_status": "mock_fallback",
            "_unavailable_reason": str(exc),
        }
    except Exception as e:
        logger.error("Organizational intelligence query failed: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
