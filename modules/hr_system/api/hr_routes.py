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
        
    except ImportError:
        # Graceful degradation if core module not available
        logger.warning("StaffingAnalyzer not available, returning degraded response")
        return {
            "department": request.department,
            "current_staff": 0,
            "recommended_staff": 0,
            "gap_analysis": {},
            "priority": "UNKNOWN",
            "rationale": "Staffing analyzer module unavailable",
            "degraded": True,
            "degraded_reason": "StaffingAnalyzer could not be imported",
        }
    except Exception as e:
        logger.error("Staffing analysis failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate_character", response_model=CharacterProfile)
async def generate_character(request: CharacterGenerationRequest):
    """Generate a quantum-symbolic character profile
    
    Creates crew member profile with skills, background, and personality.
    """
    try:
        from modules.hr_system.core.character_generator import (
            CharacterGenerator,
            Department as CGDepartment,
            Rank,
        )

        generator = CharacterGenerator()
        dept_map = {d.value.lower(): d for d in CGDepartment}
        dept_enum = dept_map.get(request.department.lower(), CGDepartment.OPERATIONS)
        candidates = generator.generate_character(
            role=request.role,
            department=dept_enum,
            rank=Rank.LIEUTENANT,
            specializations=request.skills_required or [],
        )
        char_dict = candidates[0].to_dict()
        return {
            "name": char_dict["name"],
            "role": request.role,
            "department": char_dict["department"],
            "skills": char_dict["specializations"],
            "background": char_dict["background"]["story"],
            "personality_traits": char_dict["personality"]["traits"],
            "quantum_properties": char_dict.get("quantum_profile", {}),
        }
        
    except ImportError:
        # Graceful degradation if core module not available
        logger.warning("CharacterGenerator not available, returning degraded response")
        return {
            "name": "UNAVAILABLE",
            "role": request.role,
            "department": request.department,
            "skills": [],
            "background": "Character generator module unavailable",
            "personality_traits": [],
            "quantum_properties": {},
            "degraded": True,
            "degraded_reason": "CharacterGenerator could not be imported",
        }
    except Exception as e:
        logger.error("Character generation failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


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
        
    except ImportError:
        # Graceful degradation
        logger.warning("OrganizationalIntelligence not available, returning degraded response")
        return {
            "departments": [],
            "total_capacity": 0,
            "current_utilization": 0.0,
            "growth_trajectory": "unknown",
            "degraded": True,
            "degraded_reason": "OrganizationalIntelligence could not be imported",
        }
    except Exception as e:
        logger.error("Organizational intelligence query failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
