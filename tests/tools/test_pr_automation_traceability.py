"""Tests for traceable PR automation scoring and quiet comment decisions."""

from __future__ import annotations

from tools.selective_integrator import SelectiveIntegrator


def test_direct_merge_plan_stays_quiet_without_actionable_evidence() -> None:
    evaluation = {
        "overall_score": 0.96,
        "passed": True,
        "changed_files": ["tests/example_test.py"],
        "actionable_findings": [],
        "results": [
            {
                "category": "Technical Quality",
                "score": 1.0,
                "passed": True,
                "evidence": [
                    {
                        "signal": "pytest",
                        "weight": 0.6,
                        "score_delta": 0.0,
                        "evidence": "pytest exited 0",
                        "recommendation": "",
                        "actionable": False,
                    }
                ],
            }
        ],
    }

    plan = SelectiveIntegrator().analyze_integration("test/direct", evaluation)

    assert plan.strategy == "direct_merge"
    assert plan.comment_required is False
    assert plan.comment_reason == "routine_healthy_pr_quiet"


def test_actionable_evidence_requires_compact_comment() -> None:
    evaluation = {
        "overall_score": 0.82,
        "passed": True,
        "changed_files": ["src/monitoring/ethics_gate.py"],
        "actionable_findings": [
            {
                "category": "Boundary Safety",
                "recommendations": ["Confirm boundary-sensitive changes have explicit validation"],
                "evidence": [
                    {
                        "signal": "boundary_sensitive_paths",
                        "weight": 1.0,
                        "score_delta": -0.15,
                        "evidence": "src/monitoring/ethics_gate.py",
                        "recommendation": "Confirm boundary-sensitive changes have explicit validation",
                        "actionable": True,
                    }
                ],
            }
        ],
        "results": [
            {
                "category": "Boundary Safety",
                "score": 0.85,
                "passed": True,
                "evidence": [
                    {
                        "signal": "boundary_sensitive_paths",
                        "weight": 1.0,
                        "score_delta": -0.15,
                        "evidence": "src/monitoring/ethics_gate.py",
                        "recommendation": "Confirm boundary-sensitive changes have explicit validation",
                        "actionable": True,
                    }
                ],
            }
        ],
    }

    plan = SelectiveIntegrator().analyze_integration("test/boundary", evaluation)

    assert plan.strategy == "targeted_review"
    assert plan.comment_required is True
    assert plan.comment_reason == "targeted_review_needed"
    assert plan.evidence
    assert plan.evidence[0]["category"] == "Boundary Safety"
