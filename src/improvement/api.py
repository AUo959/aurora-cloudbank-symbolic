"""
FastAPI Router for Code Improvement Engine

Provides REST API for code analysis and improvement suggestions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum
import os
from src.improvement import (
    get_improvement_engine,
    ImprovementCategory,
    ImprovementSeverity
)



# Define SAFE_ROOT as the workspace root directory for path security validation
SAFE_ROOT = Path(__file__).parent.parent.parent.resolve()


def _safe_root() -> Path:
    """The directory analysis is confined to.

    Overridable via AURORA_IMPROVEMENT_ROOT so the test-suite can point it at a
    fixture directory. That override replaces a carve-out which admitted any
    absolute path under a system temp directory and skipped the containment
    check entirely — a bypass CodeQL reported as py/path-injection. Being under
    a temp root is a location test, not an authorization decision, so it could
    not be made sound; pointing the root at the directory instead keeps every
    path subject to the same containment check.
    """
    override = os.environ.get("AURORA_IMPROVEMENT_ROOT", "")
    return Path(override).resolve() if override else SAFE_ROOT


def _resolve_request_path(user_path: str) -> Path:
    """Validate and resolve *user_path* to an absolute path within the safe root.

    Applies CodeQL's recommended ``startswith``-based containment pattern:

    * Absolute inputs are first checked lexically via ``relative_to()`` (a pure
      string operation, no filesystem access) so that ``.resolve()`` is never
      called on unvalidated caller data.
    * Relative inputs are joined with the trusted root before resolving.
    * The resolved path is re-checked against the safe root to catch symlinks
      that would otherwise escape containment.
    * Cross-drive paths on Windows fail closed (different drive letters produce
      no common prefix, so ``startswith`` returns False).

    Raises HTTPException 400 on traversal attempts and 403 on containment
    failures; callers add the 404/400 existence/type checks they need.
    """
    safe_root = _safe_root()
    safe_root_str = str(safe_root)
    requested = Path(user_path)

    if requested.is_absolute():
        # Lexical containment check before any filesystem access.
        # relative_to() raises ValueError if the path is not under safe_root,
        # which we convert to a 403.  We then reconstruct from the trusted root
        # so that .resolve() is not called directly on caller-supplied data.
        try:
            rel = requested.relative_to(safe_root)
        except ValueError:
            raise HTTPException(status_code=403, detail="Access to this path is not allowed.")
        full_path = (safe_root / rel).resolve()
    else:
        if ".." in requested.parts:
            raise HTTPException(
                status_code=400,
                detail="Parent directory references ('..') are not allowed.",
            )
        # Join with the trusted root before resolving (CodeQL recommended pattern).
        full_path = (safe_root / requested).resolve()

    # Guard: resolved path must sit within safe_root.
    # startswith() is CodeQL's recognised containment barrier; os.sep ensures
    # that /safe/root does not accidentally match /safe/rootother.
    full_path_str = str(full_path)
    if not (full_path_str == safe_root_str
            or full_path_str.startswith(safe_root_str + os.sep)):
        raise HTTPException(status_code=403, detail="Access to this path is not allowed.")

    return full_path


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
    full_path = _resolve_request_path(request.file_path)

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
    full_path = _resolve_request_path(request.directory)

    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {request.directory}")

    if not full_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {request.directory}")

    # Analyze directory
    results = engine.analyze_directory(full_path, request.file_patterns)
    
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
