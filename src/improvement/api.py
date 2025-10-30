"""
FastAPI Router for Code Improvement Engine

Provides REST API for code analysis and improvement suggestions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
from enum import Enum

from src.improvement import (
    get_improvement_engine,
    ImprovementCategory,
    ImprovementSeverity
)


router = APIRouter(prefix="/improvements", tags=["Code Improvements"])


# Pydantic models
class ImprovementCategoryEnum(str, Enum):
    """API representation of improvement category"""
    REFACTORING = "refactoring"
    PERFORMANCE = "performance"
    SECURITY = "security"
    READABILITY = "readability"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"


class ImprovementSeverityEnum(str, Enum):
    """API representation of improvement severity"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalyzeFileRequest(BaseModel):
    """Request to analyze a single file"""
    file_path: str = Field(..., description="Path to file to analyze")


class AnalyzeDirectoryRequest(BaseModel):
    """Request to analyze a directory"""
    directory: str = Field(..., description="Directory to scan")
    file_patterns: List[str] = Field(
        default=["*.py"],
        description="File patterns to match"
    )
    min_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold"
    )
    categories: Optional[List[ImprovementCategoryEnum]] = Field(
        None,
        description="Filter by categories"
    )
    severities: Optional[List[ImprovementSeverityEnum]] = Field(
        None,
        description="Filter by severities"
    )


class SuggestionResponse(BaseModel):
    """Single improvement suggestion"""
    file_path: str
    line_number: int
    category: str
    severity: str
    description: str
    rationale: str
    suggested_fix: Optional[str]
    automated_fix_available: bool
    safe_to_auto_apply: bool
    confidence_score: float


class AnalysisReportResponse(BaseModel):
    """Complete analysis report"""
    total_files_analyzed: int
    total_suggestions: int
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    automated_fix_available: int
    safe_to_auto_apply: int
    suggestions: Dict[str, List[Dict[str, Any]]]


@router.post("/analyze-file", response_model=List[SuggestionResponse])
async def analyze_file(request: AnalyzeFileRequest):
    """
    Analyze a single file for improvement opportunities
    
    Returns list of suggestions for the specified file.
    """
    engine = get_improvement_engine()
    requested_path = Path(request.file_path)
    # Compute the full, normalized path under the SAFE_ROOT
    full_path = (SAFE_ROOT / requested_path).resolve()

    # Ensure the resolved path is inside SAFE_ROOT
    if not str(full_path).startswith(str(SAFE_ROOT)):
        raise HTTPException(status_code=403, detail="Access to this path is not allowed.")

    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

    if not full_path.is_file():
        raise HTTPException(status_code=400, detail=f"Not a file: {request.file_path}")

    suggestions = engine.analyze_file(full_path)
    return [s.to_dict() for s in suggestions]


@router.post("/analyze-directory", response_model=AnalysisReportResponse)
async def analyze_directory(request: AnalyzeDirectoryRequest):
    """
    Analyze a directory for improvement opportunities
    
    Scans directory with specified patterns and generates comprehensive report.
    """
    engine = get_improvement_engine()
    directory = Path(request.directory)
    
    if not directory.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {request.directory}")
    
    if not directory.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {request.directory}")
    
    # Analyze directory
    results = engine.analyze_directory(directory, request.file_patterns)
    
    # Apply filters
    if request.categories or request.severities or request.min_confidence > 0.5:
        categories = {ImprovementCategory(c.value) for c in request.categories} if request.categories else None
        severities = {ImprovementSeverity(s.value) for s in request.severities} if request.severities else None
        
        filtered_results = {}
        for file_path, suggestions in results.items():
            filtered = engine.filter_suggestions(
                suggestions,
                min_confidence=request.min_confidence,
                categories=categories,
                severities=severities
            )
            if filtered:
                filtered_results[file_path] = filtered
        
        results = filtered_results
    
    # Generate report
    report = engine.generate_report(results)
    return report


@router.get("/categories", response_model=List[str])
async def list_categories():
    """
    List all available improvement categories
    
    Returns list of category identifiers.
    """
    return [cat.value for cat in ImprovementCategory]


@router.get("/severities", response_model=List[str])
async def list_severities():
    """
    List all available severity levels
    
    Returns list of severity identifiers.
    """
    return [sev.value for sev in ImprovementSeverity]


@router.get("/patterns", response_model=List[Dict[str, str]])
async def list_patterns():
    """
    List all registered improvement patterns
    
    Returns information about active detection patterns.
    """
    engine = get_improvement_engine()
    return [
        {
            "name": pattern.name,
            "category": pattern.category.value,
            "severity": pattern.severity.value
        }
        for pattern in engine._patterns
    ]


@router.get("/health", response_model=Dict[str, Any])
async def engine_health():
    """
    Get improvement engine health status
    
    Returns engine configuration and status.
    """
    engine = get_improvement_engine()
    
    return {
        "status": "operational",
        "patterns_registered": len(engine._patterns),
        "categories_available": len(list(ImprovementCategory)),
        "severities_available": len(list(ImprovementSeverity))
    }
