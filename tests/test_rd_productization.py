import math
from datetime import datetime, timedelta

from modules.hr.rd_productization import (
    RDProductizationPipeline,
    ProjectStage,
    ProjectType,
)


def test_create_and_advance_project():
    pipeline = RDProductizationPipeline()
    proj = pipeline.create_project(
        project_id="P1",
        name="Coherence Monitor",
        project_type=ProjectType.MICROSERVICE,
        lead_researcher="Priya Sharma",
        team_members=["Kai Chen", "Marcus Webb"],
        key_technologies=["python", "fastapi"],
        target_completion=datetime.now() + timedelta(days=90),
    )

    assert proj.project_id == "P1"
    assert proj.stage == ProjectStage.RESEARCH
    assert abs(proj.completion_percentage - 0.0) < 1e-9

    proj = pipeline.advance_stage("P1", ProjectStage.PROTOTYPE, "Prototype complete")
    assert proj.stage == ProjectStage.PROTOTYPE
    assert math.isclose(proj.completion_percentage, 0.50)


def test_production_readiness_and_report():
    pipeline = RDProductizationPipeline()
    pipeline.create_project(
        project_id="P2",
        name="NLI Ethics Plugin",
        project_type=ProjectType.TOOL,
        lead_researcher="Tobias Qin",
        team_members=["Elena Sorensen"],
        key_technologies=["python"],
    )

    readiness = pipeline.calculate_production_readiness(
        "P2",
        code_quality=0.8,
        documentation=0.7,
        test_coverage=0.6,
        performance=0.9,
        security=0.75,
    )
    assert 0.0 <= readiness <= 1.0

    # Coherence with simple vectors (3D)
    profiles = {
        "Tobias Qin": [1.0, 0.0, 0.0],
        "Elena Sorensen": [0.0, 1.0, 0.0],
    }
    coh = pipeline.calculate_team_coherence("P2", profiles)
    # orthogonal vectors -> cosine 0.0 average
    assert math.isclose(coh, 0.0, abs_tol=1e-8)

    # Update with partially aligned vectors
    profiles = {
        "Tobias Qin": [1.0, 0.0, 0.0],
        "Elena Sorensen": [0.6, 0.8, 0.0],
    }
    coh = pipeline.calculate_team_coherence("P2", profiles)
    assert coh > 0.0

    report = pipeline.generate_pipeline_report()
    assert "projects_by_stage" in report
    assert "aggregate_metrics" in report


def test_parallel_capacity():
    pipeline = RDProductizationPipeline()
    pipeline.create_project(
        project_id="A",
        name="CASK Enhancements",
        project_type=ProjectType.MODULE,
        lead_researcher="Priya Sharma",
        team_members=["Kai Chen"],
        key_technologies=["python"],
    )
    pipeline.create_project(
        project_id="B",
        name="VSA Library",
        project_type=ProjectType.ALGORITHM,
        lead_researcher="Kai Chen",
        team_members=["Priya Sharma"],
        key_technologies=["python"],
    )

    cap = pipeline.get_parallel_project_capacity("Priya Sharma")
    assert cap["active_projects"] >= 2
    assert cap["available_capacity"] >= 0.0
