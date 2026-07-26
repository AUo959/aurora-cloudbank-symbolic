"""
FastAPI Router for Code Improvement Engine

Provides REST API for code analysis and improvement suggestions.
"""

import os
from enum import Enum
from pathlib import Path, PurePath
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.improvement import (
    ImprovementCategory,
    ImprovementSeverity,
    get_improvement_engine,
)


SAFE_ROOT = Path(__file__).parent.parent.parent.resolve()


def _safe_root() -> Path:
    """Return the configured analysis root.

    The filesystem root is deliberately rejected: this administrative
    inspection surface must retain a meaningful containment boundary.
    """
    override = os.environ.get("AURORA_IMPROVEMENT_ROOT", "")
    root = Path(override).resolve() if override else SAFE_ROOT
    if root.parent == root:
        raise RuntimeError("AURORA_IMPROVEMENT_ROOT must not be the filesystem root")
    return root


def _request_parts(user_path: str, safe_root: Path) -> tuple[str, ...]:
    """Convert a request value to lexical root-relative lookup components.

    Request components are used only for equality comparisons with names
    returned by trusted directory enumeration. They are never joined to a
    filesystem path.
    """
    requested = PurePath(user_path)
    root_key = PurePath(str(safe_root))

    if requested.is_absolute():
        try:
            requested = requested.relative_to(root_key)
        except ValueError as exc:
            raise HTTPException(
                status_code=403,
                detail="Access to this path is not allowed.",
            ) from exc
    elif ".." in requested.parts:
        raise HTTPException(
            status_code=400,
            detail="Parent directory references ('..') are not allowed.",
        )

    parts = tuple(part for part in requested.parts if part not in ("", "."))
    return parts


def _trusted_child(directory: Path, requested_name: str, safe_root: Path) -> Path:
    """Select one child by comparing a request component to trusted names."""
    try:
        children = directory.iterdir()
        child = next((entry for entry in children if entry.name == requested_name), None)
    except OSError as exc:
        raise HTTPException(status_code=404, detail="Path not found.") from exc

    if child is None:
        raise HTTPException(status_code=404, detail="Path not found.")

    resolved = child.resolve()
    if resolved != safe_root and safe_root not in resolved.parents:
        raise HTTPException(
            status_code=403,
            detail="Access to this path is not allowed.",
        )
    return resolved


def _resolve_request_path(user_path: str) -> Path:
    """Resolve a logical lookup key through trusted directory enumeration.

    Every returned path originates from ``Path.iterdir()`` beneath the trusted
    root. Remote input participates only in string equality checks, breaking
    the remote-input-to-filesystem-path data flow entirely.
    """
    safe_root = _safe_root()
    current = safe_root

    for component in _request_parts(user_path, safe_root):
        if not current.is_dir():
            raise HTTPException(status_code=404, detail=f"Path not found: {user_path}")
        current = _trusted_child(current, component, safe_root)

    return current


router = APIRouter(prefix="/improvements", tags=["Code Improvements"])


class ImprovementCategoryEnum(str, Enum):
    """API representation of improvement category."""

    REFACTORING = "refactoring"
    PERFORMANCE = "performance"
    SECURITY = "security"
    READABILITY = "readability"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"


class ImprovementSeverityEnum(str, Enum):
    """API representation of improvement severity."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalyzeFileRequest(BaseModel):
    """Request to analyze a single file."""

    file_path: str = Field(
        ...,
        description="File lookup key, root-relative or an absolute path contained within the configured analysis root",
    )


class AnalyzeDirectoryRequest(BaseModel):
    """Request to analyze a directory."""

    directory: str = Field(
        ...,
        description="Directory lookup key, root-relative or an absolute path contained within the configured analysis root",
    )
    file_patterns: List[str] = Field(default=["*.py"], description="File patterns to match")
    min_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold",
    )
    categories: Optional[List[ImprovementCategoryEnum]] = Field(
        None,
        description="Filter by categories",
    )
    severities: Optional[List[ImprovementSeverityEnum]] = Field(
        None,
        description="Filter by severities",
    )


class SuggestionResponse(BaseModel):
    """Single improvement suggestion."""

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
    """Complete analysis report."""

    total_files_analyzed: int
    total_suggestions: int
    by_category: Dict[str, int]
    by_severity: Dict[str, int]
    automated_fix_available: int
    safe_to_auto_apply: int
    suggestions: Dict[str, List[Dict[str, Any]]]


@router.post("/analyze-file", response_model=List[SuggestionResponse])
async def analyze_file(request: AnalyzeFileRequest):
    """Analyze a single trusted, root-enumerated file."""
    engine = get_improvement_engine()
    full_path = _resolve_request_path(request.file_path)

    if not full_path.is_file():
        raise HTTPException(status_code=400, detail=f"Not a file: {request.file_path}")

    suggestions = engine.analyze_file(full_path)
    return [suggestion.to_dict() for suggestion in suggestions]


@router.post("/analyze-directory", response_model=AnalysisReportResponse)
async def analyze_directory(request: AnalyzeDirectoryRequest):
    """Analyze a trusted, root-enumerated directory."""
    engine = get_improvement_engine()
    full_path = _resolve_request_path(request.directory)

    if not full_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {request.directory}")

    results = engine.analyze_directory(full_path, request.file_patterns)

    if request.categories or request.severities or request.min_confidence > 0.5:
        categories = (
            {ImprovementCategory(category.value) for category in request.categories}
            if request.categories
            else None
        )
        severities = (
            {ImprovementSeverity(severity.value) for severity in request.severities}
            if request.severities
            else None
        )

        filtered_results = {}
        for file_path, suggestions in results.items():
            filtered = engine.filter_suggestions(
                suggestions,
                min_confidence=request.min_confidence,
                categories=categories,
                severities=severities,
            )
            if filtered:
                filtered_results[file_path] = filtered
        results = filtered_results

    return engine.generate_report(results)


@router.get("/categories", response_model=List[str])
async def list_categories():
    """List all available improvement category identifiers."""
    return [category.value for category in ImprovementCategory]


@router.get("/severities", response_model=List[str])
async def list_severities():
    """List all available severity identifiers."""
    return [severity.value for severity in ImprovementSeverity]


@router.get("/patterns", response_model=List[Dict[str, str]])
async def list_patterns():
    """List all registered improvement patterns."""
    engine = get_improvement_engine()
    return [
        {
            "name": pattern.name,
            "category": pattern.category.value,
            "severity": pattern.severity.value,
        }
        for pattern in engine._patterns
    ]


@router.get("/health", response_model=Dict[str, Any])
async def engine_health():
    """Get improvement engine health and configuration status."""
    engine = get_improvement_engine()
    return {
        "status": "operational",
        "patterns_registered": len(engine._patterns),
        "categories_available": len(list(ImprovementCategory)),
        "severities_available": len(list(ImprovementSeverity)),
    }
