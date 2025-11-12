"""
R&D Productization Pipeline

Purpose: Manage research-to-product transitions, track parallel projects,
compute readiness and team coherence, and generate pipeline health reports.

- No external dependencies required (numpy optional; pure-Python fallbacks used)
- Designed for integration with HR wellness and quantum coherence systems
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import math


class ProjectStage(Enum):
    """Research-to-product pipeline stages."""

    RESEARCH = "research"
    PROOF_OF_CONCEPT = "proof_of_concept"
    PROTOTYPE = "prototype"
    ALPHA = "alpha"
    BETA = "beta"
    PRODUCTION = "production"
    MAINTENANCE = "maintenance"


class ProjectType(Enum):
    """Types of R&D projects."""

    MICROSERVICE = "microservice"
    MODULE = "module"
    TOOL = "tool"
    ALGORITHM = "algorithm"
    FRAMEWORK = "framework"
    RESEARCH_PAPER = "research_paper"


@dataclass
class ResearchProject:
    """Research project with productization tracking."""

    project_id: str
    name: str
    project_type: ProjectType
    stage: ProjectStage

    # Team
    lead_researcher: str
    team_members: List[str]

    # Progress tracking
    start_date: datetime
    target_completion: Optional[datetime]
    current_milestone: str
    completion_percentage: float  # 0.0 - 1.0

    # Technical details
    repository_path: Optional[str]
    documentation_path: Optional[str]
    key_technologies: List[str]

    # Productization
    production_readiness: float  # 0.0 - 1.0
    deployment_complexity: str  # "low", "medium", "high", "unknown"
    maintenance_requirements: str

    # Success metrics
    research_impact: float  # 0.0 - 1.0
    product_viability: float  # 0.0 - 1.0
    innovation_score: float  # 0.0 - 1.0

    # Quantum attributes
    team_coherence: float  # 0.0 - 1.0
    project_entanglements: Dict[str, float]  # Cross-project dependencies


class RDProductizationPipeline:
    """Research-to-product pipeline management."""

    def __init__(self) -> None:
        self.active_projects: Dict[str, ResearchProject] = {}
        self.completed_projects: List[ResearchProject] = []

    def _require_project(self, project_id: str) -> ResearchProject:
        """Internal helper to fetch project or raise ValueError if not found."""
        if project_id not in self.active_projects:
            raise ValueError(f"Project '{project_id}' not found")
        return self.active_projects[project_id]

    # ----------------------
    # Project lifecycle
    # ----------------------
    def create_project(
        self,
        project_id: str,
        name: str,
        project_type: ProjectType,
        lead_researcher: str,
        team_members: List[str],
        key_technologies: List[str],
        *,
        target_completion: Optional[datetime] = None,
    ) -> ResearchProject:
        """Initialize a new R&D project and add it to the active set."""
        if project_id in self.active_projects:
            raise ValueError(f"Project '{project_id}' already exists")

        project = ResearchProject(
            project_id=project_id,
            name=name,
            project_type=project_type,
            stage=ProjectStage.RESEARCH,
            lead_researcher=lead_researcher,
            team_members=list(team_members),
            start_date=datetime.now(),
            target_completion=target_completion,
            current_milestone="Initial research phase",
            completion_percentage=0.0,
            repository_path=None,
            documentation_path=None,
            key_technologies=list(key_technologies),
            production_readiness=0.0,
            deployment_complexity="unknown",
            maintenance_requirements="TBD",
            research_impact=0.0,
            product_viability=0.0,
            innovation_score=0.0,
            team_coherence=0.0,
            project_entanglements={},
        )

        self.active_projects[project_id] = project
        return project

    def advance_stage(self, project_id: str, new_stage: ProjectStage, milestone: str) -> ResearchProject:
        """Move project to next stage and update completion percentage."""
        project = self._require_project(project_id)
        project.stage = new_stage
        project.current_milestone = milestone

        stage_progress = {
            ProjectStage.RESEARCH: 0.15,
            ProjectStage.PROOF_OF_CONCEPT: 0.30,
            ProjectStage.PROTOTYPE: 0.50,
            ProjectStage.ALPHA: 0.70,
            ProjectStage.BETA: 0.85,
            ProjectStage.PRODUCTION: 1.0,
            ProjectStage.MAINTENANCE: 1.0,
        }
        project.completion_percentage = stage_progress[new_stage]
        return project

    # ----------------------
    # Scores & metrics
    # ----------------------
    def calculate_production_readiness(
        self,
        project_id: str,
        *,
        code_quality: float,
        documentation: float,
        test_coverage: float,
        performance: float,
        security: float,
    ) -> float:
        """Calculate a weighted production readiness score."""
        self._validate_score(code_quality)
        self._validate_score(documentation)
        self._validate_score(test_coverage)
        self._validate_score(performance)
        self._validate_score(security)

        weights = {
            "code_quality": 0.25,
            "documentation": 0.20,
            "test_coverage": 0.20,
            "performance": 0.20,
            "security": 0.15,
        }
        readiness = (
            code_quality * weights["code_quality"]
            + documentation * weights["documentation"]
            + test_coverage * weights["test_coverage"]
            + performance * weights["performance"]
            + security * weights["security"]
        )

        project = self._require_project(project_id)
        project.production_readiness = readiness
        return readiness

    def calculate_team_coherence(
        self,
        project_id: str,
        team_member_profiles: Dict[str, List[float]],
    ) -> float:
        """Calculate average pairwise cosine similarity for team VSA vectors.

        - Expects normalized or non-normalized vectors (we normalize internally)
        - Returns 0.0 if <2 vectors available
        """
        project = self._require_project(project_id)
        team = [project.lead_researcher] + project.team_members
        vectors = [team_member_profiles.get(member) for member in team]
        vectors = [v for v in vectors if v is not None]
        if len(vectors) < 2:
            project.team_coherence = 0.0
            return 0.0

        # Normalize vectors and compute mean pairwise cosine similarity
        normed = [self._normalize(v) for v in vectors if self._norm(v) > 0]
        if len(normed) < 2:
            project.team_coherence = 0.0
            return 0.0

        sims: List[float] = []
        for i in range(len(normed)):
            for j in range(i + 1, len(normed)):
                sims.append(self._cosine(normed[i], normed[j]))

        team_coherence = sum(sims) / len(sims)
        project.team_coherence = float(team_coherence)
        return project.team_coherence

    # ----------------------
    # Capacity & reporting
    # ----------------------
    def get_parallel_project_capacity(self, team_member: str) -> Dict[str, object]:
        """Estimate a team member's parallel project load and available capacity."""
        member_projects = [
            p for p in self.active_projects.values() if team_member in ([p.lead_researcher] + p.team_members)
        ]
        current_load = sum(1.0 if p.lead_researcher == team_member else 0.3 for p in member_projects)
        max_capacity = 2.5  # Lead up to 2 + support 1–2 others
        return {
            "team_member": team_member,
            "active_projects": len(member_projects),
            "current_load": current_load,
            "max_capacity": max_capacity,
            "available_capacity": max(0.0, max_capacity - current_load),
            "projects": [p.project_id for p in member_projects],
        }

    def generate_pipeline_report(self) -> Dict[str, object]:
        """Generate a comprehensive pipeline status report."""
        by_stage: Dict[str, List[ResearchProject]] = {s.value: [] for s in ProjectStage}
        for p in self.active_projects.values():
            by_stage[p.stage.value].append(p)

        total = len(self.active_projects)
        avg_completion = sum(p.completion_percentage for p in self.active_projects.values()) / total if total else 0.0
        avg_readiness = sum(p.production_readiness for p in self.active_projects.values()) / total if total else 0.0

        coherence_values = [p.team_coherence for p in self.active_projects.values() if p.team_coherence > 0]
        avg_coherence = (sum(coherence_values) / len(coherence_values)) if coherence_values else 0.0

        return {
            "timestamp": datetime.now().isoformat(),
            "total_active_projects": total,
            "completed_projects": len(self.completed_projects),
            "projects_by_stage": {stage: len(projects) for stage, projects in by_stage.items()},
            "aggregate_metrics": {
                "average_completion": round(avg_completion, 4),
                "average_production_readiness": round(avg_readiness, 4),
                "average_team_coherence": round(avg_coherence, 4),
            },
            "pipeline_health": self._calculate_pipeline_health(),
            "bottlenecks": self._identify_bottlenecks(),
        }

    # ----------------------
    # Internals
    # ----------------------
    def _calculate_pipeline_health(self) -> str:
        if not self.active_projects:
            return "idle"

        stalled = sum(
            1
            for p in self.active_projects.values()
            if p.completion_percentage < 0.2 and self._age_days(p) > 90
        )
        low_coherence = sum(1 for p in self.active_projects.values() if p.team_coherence < 0.60)
        total = len(self.active_projects)

        if stalled > total * 0.3:
            return "critical"
        if low_coherence > total * 0.4:
            return "degraded"
        if stalled > 0 or low_coherence > 0:
            return "warning"
        return "healthy"

    def _identify_bottlenecks(self) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        stage_thresholds: Dict[ProjectStage, int] = {
            ProjectStage.RESEARCH: 90,
            ProjectStage.PROOF_OF_CONCEPT: 60,
            ProjectStage.PROTOTYPE: 90,
            ProjectStage.ALPHA: 60,
            ProjectStage.BETA: 45,
        }
        for p in self.active_projects.values():
            days = self._age_days(p)
            threshold = stage_thresholds.get(p.stage, 180)
            if days > threshold:
                results.append(
                    {
                        "project_id": p.project_id,
                        "project_name": p.name,
                        "stage": p.stage.value,
                        "days_in_stage": days,
                        "threshold": threshold,
                        "recommendation": self._get_bottleneck_recommendation(p),
                    }
                )
        return results

    def _get_bottleneck_recommendation(self, project: ResearchProject) -> str:
        if project.team_coherence < 0.60:
            return "Low team coherence - consider team restructuring or mediation"
        if project.production_readiness < 0.50 and project.stage in {ProjectStage.ALPHA, ProjectStage.BETA}:
            return "Low production readiness - improve code quality, docs, tests"
        if project.completion_percentage < 0.30:
            return "Low completion - reassess scope or allocate more resources"
        return "Schedule review meeting with lead researcher and HR"

    @staticmethod
    def _age_days(project: ResearchProject) -> int:
        return max(0, (datetime.now() - project.start_date).days)

    @staticmethod
    def _validate_score(value: float) -> None:
        if not (0.0 <= value <= 1.0):
            raise ValueError("Scores must be between 0.0 and 1.0")

    @staticmethod
    def _norm(v: List[float]) -> float:
        return math.sqrt(sum(x * x for x in v))

    @classmethod
    def _normalize(cls, v: List[float]) -> List[float]:
        n = cls._norm(v)
        return [x / n for x in v] if n > 0 else v[:]

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        # Assumes both a and b are normalized
        m = min(len(a), len(b))
        if m == 0:
            return 0.0
        return sum(a[i] * b[i] for i in range(m))
