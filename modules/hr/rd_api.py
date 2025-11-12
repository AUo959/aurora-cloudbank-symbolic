"""R&D Productization Pipeline API

FastAPI router exposing the research-to-product transition lifecycle.

Endpoints follow Aurora security patterns:
 - State changing operations require CSRF verification via security dependency
 - Read-only operations rate-limited appropriately

Provides:
 - List/create projects
 - Advance project stage
 - Compute production readiness
 - Compute/update team coherence (using provided VSA vectors)
 - Capacity estimation per team member
 - Aggregate pipeline report

Data Seeding:
On import we attempt to load an initial seed file located at
`data/hr/rd_projects_seed.json` (optional). Missing file is ignored.

VSA Senior Team Vectors:
If `data/hr/senior_team_vsa.json` exists we load vectors for coherence
computations. Coherence calculation reuses RDProductizationPipeline logic.

All numeric scores are constrained to 0.0-1.0. Errors return structured
HTTPException responses with context tags for DLP lineage.
"""

from typing import Any, Dict, List, Tuple
from dataclasses import asdict
import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, Request

from pydantic import BaseModel, Field, field_validator

from modules.hr.rd_productization import (
    RDProductizationPipeline,
    ProjectStage,
    ProjectType,
)

# Aurora security + rate limiting (guard optional import failures gracefully)
try:
    from src.middleware.fastapi_security import security, verify_csrf_token, limiter
    SECURITY_AVAILABLE = True
except Exception:  # pragma: no cover - fallback path
    SECURITY_AVAILABLE = False
    class DummySec:  # minimal placeholder
        pass
    security = DummySec()  # type: ignore
    def verify_csrf_token(*args, **kwargs):  # type: ignore
        return True
    class DummyLimiter:  # minimal placeholder
        @staticmethod
        def limit(limit_str: str):
            def _decorator(func):
                return func
            return _decorator
    limiter = DummyLimiter()  # type: ignore

logger = logging.getLogger("rd_api")

router = APIRouter(prefix="/rd", tags=["rd-pipeline"])


# -------------------------
# Pydantic Models
# -------------------------
class CreateProjectRequest(BaseModel):
    project_id: str = Field(..., min_length=2, max_length=64)
    name: str = Field(..., min_length=2, max_length=120)
    project_type: ProjectType
    lead_researcher: str = Field(..., min_length=2, max_length=64)
    team_members: List[str] = Field(default_factory=list)
    key_technologies: List[str] = Field(default_factory=list)

    @field_validator("team_members", mode="before")
    @classmethod
    def _validate_member(cls, v: List[str]) -> List[str]:
        for member in v:
            if not member or len(member) > 64:
                raise ValueError("Invalid team member id length")
        return v


class AdvanceStageRequest(BaseModel):
    new_stage: ProjectStage
    milestone: str = Field(..., min_length=2, max_length=160)


class ReadinessRequest(BaseModel):
    code_quality: float = Field(..., ge=0.0, le=1.0)
    documentation: float = Field(..., ge=0.0, le=1.0)
    test_coverage: float = Field(..., ge=0.0, le=1.0)
    performance: float = Field(..., ge=0.0, le=1.0)
    security: float = Field(..., ge=0.0, le=1.0)


class CoherenceRequest(BaseModel):
    team_vectors: Dict[str, List[float]]

    @field_validator("team_vectors")
    @classmethod
    def _validate_vectors(cls, v: Dict[str, List[float]]) -> Dict[str, List[float]]:
        for member, vec in v.items():
            if not isinstance(vec, list) or not vec:
                raise ValueError(f"Vector for {member} must be a non-empty list")
            if any(not isinstance(x, (int, float)) for x in vec):
                raise ValueError(f"Vector for {member} contains non-numeric entries")
        return v


# -------------------------
# Pipeline Instance & Seed
# -------------------------
pipeline = RDProductizationPipeline()

SEED_PATH = Path("data/hr/rd_projects_seed.json")
SENIOR_VSA_PATH = Path("data/hr/senior_team_vsa.json")
L1_ROSTER_VSA_PATH = Path("data/hr/l1_roster_vsa.json")
ROSTER_MARKDOWN_PATH = Path("modules/hr/L1_ROSTER_QUANTUM_PROFILES_EXPANSION.md")
_SENIOR_VECTORS: Dict[str, List[float]] = {}
_L1_VECTORS: Dict[str, List[float]] = {}
_ANCHOR_MAP: Dict[str, str] = {}


def _load_seed_projects() -> None:
    if not SEED_PATH.exists():
        logger.info("RD seed file not found - skipping seed load")
        return
    try:
        data = json.loads(SEED_PATH.read_text())
        for item in data.get("projects", []):
            try:
                pipeline.create_project(
                    project_id=item["project_id"],
                    name=item["name"],
                    project_type=ProjectType(item["project_type"]),
                    lead_researcher=item["lead_researcher"],
                    team_members=item.get("team_members", []),
                    key_technologies=item.get("key_technologies", []),
                )
            except Exception as e:  # pragma: no cover - seed errors logged only
                logger.warning("Failed to seed project %s: %s", item.get("project_id"), e)
        logger.info("RD seed projects loaded: %d", len(pipeline.active_projects))
    except Exception as e:  # pragma: no cover
        logger.error("Failed to parse RD seed file: %s", e)


def _load_senior_vectors() -> None:
    global _SENIOR_VECTORS
    if not SENIOR_VSA_PATH.exists():
        logger.info("Senior VSA vector file not found - coherence API will rely on request payloads")
        return
    try:
        data = json.loads(SENIOR_VSA_PATH.read_text())
        vectors = data.get("vectors", {})
        _SENIOR_VECTORS = {
            k: v for k, v in vectors.items() if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v)
        }
        logger.info("Senior team VSA vectors loaded: %d", len(_SENIOR_VECTORS))
    except Exception as e:  # pragma: no cover
        logger.error("Failed to parse senior team VSA file: %s", e)


def _load_l1_roster_vectors() -> None:
    """Load extended L1 roster vectors if present.

    File format: {"vectors": {"id": [v1,v2,v3,v4,v5], ...}}
    """
    global _L1_VECTORS
    if not L1_ROSTER_VSA_PATH.exists():
        logger.info("L1 roster VSA vector file not found - skipping full coherence preload")
        return
    try:
        data = json.loads(L1_ROSTER_VSA_PATH.read_text())
        vectors = data.get("vectors", {})
        _L1_VECTORS = {
            k: v
            for k, v in vectors.items()
            if isinstance(v, list) and len(v) == 5 and all(isinstance(x, (int, float)) for x in v)
        }
        logger.info("L1 roster VSA vectors loaded: %d", len(_L1_VECTORS))
    except Exception as e:  # pragma: no cover
        logger.error("Failed to parse L1 roster VSA file: %s", e)


def _extract_anchors_from_markdown() -> None:
    """Parse roster markdown and populate `_ANCHOR_MAP` with member -> anchor.

    Refactored for lower cyclomatic complexity: delegates responsibilities to
    small helpers and uses a single simple loop.
    """
    if not ROSTER_MARKDOWN_PATH.exists():
        return

    def _iter_lines(path: Path):
        for line in path.read_text().splitlines():
            yield line

    def _is_header(line: str) -> bool:
        return line.startswith("### ")

    def _normalize_header(line: str) -> str:
        return line[4:].partition("(")[0].strip().lower().replace(" ", "_")

    def _anchor_from_line(line: str) -> str | None:
        if 'Anchor' not in line and 'anchor' not in line:
            return None
        if '"' not in line:
            return None
        parts = line.split('"')
        if len(parts) < 3:
            return None
        token = parts[-2]
        return token if token else None

    current_id: str | None = None
    for raw in _iter_lines(ROSTER_MARKDOWN_PATH):
        if _is_header(raw):
            current_id = _normalize_header(raw)
            continue
        if not current_id:
            continue
        anchor = _anchor_from_line(raw)
        if anchor:
            _ANCHOR_MAP[current_id] = anchor

    if _ANCHOR_MAP:
        logger.info("Extracted %d anchor recommendations from roster markdown", len(_ANCHOR_MAP))


_load_seed_projects()
_load_senior_vectors()
_load_l1_roster_vectors()
_extract_anchors_from_markdown()


# -------------------------
# Endpoints
# -------------------------
@router.get("/projects")
@limiter.limit("120/minute")
def list_projects(request: Request) -> Dict[str, Any]:
    """List all active R&D projects with basic metadata."""
    projects = [asdict(p) for p in pipeline.active_projects.values()]
    return {
        "success": True,
        "count": len(projects),
        "projects": projects,
        "context_tag": "rd_list_projects",
    }


@router.post("/projects", dependencies=[Depends(security), Depends(verify_csrf_token)] if SECURITY_AVAILABLE else [])
@limiter.limit("30/minute")
def create_project(request: Request, body: CreateProjectRequest):
    """Create new R&D project with DLP tracking."""
    try:
        project = pipeline.create_project(
            project_id=body.project_id,
            name=body.name,
            project_type=body.project_type,
            lead_researcher=body.lead_researcher,
            team_members=body.team_members,
            key_technologies=body.key_technologies,
        )
        return {
            "success": True,
            "project": asdict(project),
            "context_tag": "rd_create_project",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/projects/{project_id}/advance",
    dependencies=[Depends(security), Depends(verify_csrf_token)] if SECURITY_AVAILABLE else []
)
@limiter.limit("30/minute")
def advance_stage(request: Request, project_id: str, body: AdvanceStageRequest):
    """Advance project to next stage with milestone tracking."""
    try:
        project = pipeline.advance_stage(project_id, body.new_stage, body.milestone)
        return {
            "success": True,
            "project": asdict(project),
            "context_tag": "rd_advance_stage",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/projects/{project_id}/readiness",
    dependencies=[Depends(security), Depends(verify_csrf_token)] if SECURITY_AVAILABLE else []
)
@limiter.limit("45/minute")
def update_readiness(request: Request, project_id: str, body: ReadinessRequest):
    """Calculate production readiness score for project."""
    try:
        score = pipeline.calculate_production_readiness(
            project_id,
            code_quality=body.code_quality,
            documentation=body.documentation,
            test_coverage=body.test_coverage,
            performance=body.performance,
            security=body.security,
        )
        return {
            "success": True,
            "production_readiness": round(score, 4),
            "context_tag": "rd_update_readiness",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/projects/{project_id}/coherence",
    dependencies=[Depends(security), Depends(verify_csrf_token)] if SECURITY_AVAILABLE else []
)
@limiter.limit("45/minute")
def update_coherence(request: Request, project_id: str, body: CoherenceRequest):
    """Calculate team coherence score using VSA vectors."""
    # Merge provided vectors with senior baseline if available
    merged = dict(_SENIOR_VECTORS)
    merged.update(body.team_vectors)
    try:
        coherence = pipeline.calculate_team_coherence(project_id, merged)
        return {
            "success": True,
            "team_coherence": round(coherence, 4),
            "context_tag": "rd_update_coherence",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/capacity/{team_member}")
@limiter.limit("120/minute")
def capacity(team_member: str, request: Request) -> Dict[str, Any]:
    info = pipeline.get_parallel_project_capacity(team_member)
    info["context_tag"] = "rd_capacity_query"
    info["success"] = True
    return info


@router.get("/report")
@limiter.limit("60/minute")
def report(request: Request) -> Dict[str, Any]:
    data = pipeline.generate_pipeline_report()
    data["success"] = True
    data["context_tag"] = "rd_pipeline_report"
    return data


# -------------------------
# Extended Coherence Endpoints
# -------------------------
def _cosine(a: List[float], b: List[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    val = dot / (na * nb)
    # clamp for floating edge cases
    return max(0.0, min(1.0, val))


def _aggregate_full_vectors() -> Dict[str, List[float]]:
    # Senior baseline + extended roster (excluding duplicates; roster overrides if collision)
    combined = dict(_SENIOR_VECTORS)
    for k, v in _L1_VECTORS.items():
        if k not in combined:
            combined[k] = v
    return combined


@router.get("/coherence/full")
@limiter.limit("60/minute")
def full_coherence(request: Request) -> Dict[str, Any]:
    vectors = _aggregate_full_vectors()
    ids = list(vectors.keys())
    pair_values: List[float] = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            pair_values.append(_cosine(vectors[ids[i]], vectors[ids[j]]))
    avg = sum(pair_values) / len(pair_values) if pair_values else 0.0
    return {
        "success": True,
        "vector_count": len(vectors),
        "pairwise_samples": len(pair_values),
        "average_coherence": round(avg, 4),
        "context_tag": "rd_full_coherence",
    }


@router.get("/coherence/mediation")
@limiter.limit("60/minute")
def coherence_mediation(request: Request, threshold: float = 0.55, limit: int = 25) -> Dict[str, Any]:
    """Return low-coherence pairs with anchor suggestions.

    Complexity kept low via small dedicated helper steps.
    """
    vectors = _aggregate_full_vectors()
    ids = list(vectors.keys())

    def _pair_scores() -> List[Tuple[str, str, float]]:
        out: List[Tuple[str, str, float]] = []
        for i, ida in enumerate(ids):
            for idb in ids[i + 1:]:
                score = _cosine(vectors[ida], vectors[idb])
                if score < threshold:
                    out.append((ida, idb, score))
        return out

    def _select_anchor(a: str, b: str) -> str:
        for key in (a, b):
            val = _ANCHOR_MAP.get(key)
            if val and val.startswith("T1:"):
                return val
        for key in (a, b):
            val = _ANCHOR_MAP.get(key)
            if val and val.startswith("SRB:"):
                return val
        return "T1:focused_alignment_breath"

    pairs = sorted(_pair_scores(), key=lambda x: x[2])[:limit]
    recommendations = [
        {
            "member_a": a,
            "member_b": b,
            "coherence": round(score, 4),
            "recommended_anchor": _select_anchor(a, b),
        }
        for a, b, score in pairs
    ]
    return {
        "success": True,
        "threshold": threshold,
        "pair_count": len(recommendations),
        "pairs": recommendations,
        "context_tag": "rd_coherence_mediation",
    }


# Simple health endpoint for readiness in integration tests
@router.get("/health")
@limiter.limit("120/minute")
def rd_health(request: Request) -> Dict[str, Any]:
    return {
        "status": "healthy",
        "active_projects": len(pipeline.active_projects),
        "context_tag": "rd_health",
    }
