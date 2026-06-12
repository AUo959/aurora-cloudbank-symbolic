#!/usr/bin/env python3
"""
Aurora CloudBank PR Evaluator

Evaluates PRs with traceable, evidence-backed score components. The evaluator
is intentionally lightweight for CI use: it produces machine-readable evidence
without turning routine PRs into noisy review comments.
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ScoreEvidence:
    """Traceable scoring input for one evaluation dimension."""

    signal: str
    weight: float
    score_delta: float
    evidence: str
    recommendation: str = ""
    actionable: bool = False


@dataclass
class EvaluationResult:
    """One scored PR evaluation dimension."""

    category: str
    passed: bool
    score: float
    weight: float = 1.0
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evidence: List[ScoreEvidence] = field(default_factory=list)

    @property
    def actionable(self) -> bool:
        return any(item.actionable for item in self.evidence) or bool(self.recommendations and not self.passed)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "passed": self.passed,
            "score": self.score,
            "weight": self.weight,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "actionable": self.actionable,
            "evidence": [item.__dict__ for item in self.evidence],
        }

    def __str__(self):
        status = "✅" if self.passed else "⚠️"
        return f"{status} {self.category}: {self.score:.2f}"


class PREvaluator:
    """Evaluates PRs for technical quality, safety, and Aurora continuity."""

    CATEGORY_WEIGHTS = {
        "Technical Quality": 0.35,
        "Boundary Safety": 0.25,
        "Traceability": 0.20,
        "Documentation Fit": 0.10,
        "Symbolic Integrity": 0.10,
    }

    RUNTIME_BOUNDARY_PATTERNS = (
        "src/monitoring/ethics_engine.py",
        "src/monitoring/ethics_gate.py",
        "src/subroutines/ethics_compliance_monitor.py",
        "modules/ethics_field/",
        "modules/symbolic_core/",
        "api/",
        ".github/workflows/",
    )

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd())

    def evaluate_pr(self, pr_number: Optional[int] = None, branch: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate a pull request and return traceable JSON."""
        print("=" * 80)
        print("AURORA PR EVALUATION")
        print("=" * 80)
        if pr_number:
            print(f"Evaluating PR #{pr_number}")
        elif branch:
            print(f"Evaluating branch: {branch}")
        else:
            print("Evaluating current changes")
        print()

        changed_files = self._changed_files()
        print(f"Changed files: {len(changed_files)}")

        results = [
            self._evaluate_technical_quality(),
            self._evaluate_boundary_safety(changed_files),
            self._evaluate_traceability(),
            self._evaluate_documentation_fit(changed_files),
            self._evaluate_symbolic_integrity(changed_files),
        ]

        weighted_total = sum(result.score * result.weight for result in results)
        weight_sum = sum(result.weight for result in results)
        overall_score = weighted_total / weight_sum if weight_sum else 0.0
        all_passed = all(result.passed for result in results)
        actionable_findings = [
            {
                "category": result.category,
                "recommendations": result.recommendations,
                "evidence": [item.__dict__ for item in result.evidence if item.actionable],
            }
            for result in results
            if result.actionable
        ]
        recommendation = self._generate_recommendation(overall_score, all_passed, actionable_findings)

        print("=" * 80)
        print("OVERALL ASSESSMENT")
        print("=" * 80)
        print(f"Score: {overall_score:.2f}/1.00")
        print(f"Status: {'APPROVED' if all_passed else 'NEEDS WORK'}")
        print(recommendation)

        return {
            "overall_score": overall_score,
            "passed": all_passed,
            "recommendation": recommendation,
            "changed_files": changed_files,
            "actionable_findings": actionable_findings,
            "results": [result.to_dict() for result in results],
            "score_model": {
                "version": "traceable-pr-evaluation-v2",
                "category_weights": self.CATEGORY_WEIGHTS,
                "quiet_comment_guidance": "Routine passing PRs should not receive large automation comments.",
            },
        }

    def _changed_files(self) -> List[str]:
        try:
            base_ref = os.environ.get("GITHUB_BASE_REF")
            if base_ref:
                subprocess.run(["git", "fetch", "origin", base_ref], cwd=self.workspace_root, check=False)
                cmd = ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"]
            else:
                cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]
            diff_result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.workspace_root, timeout=30)
            return [line.strip() for line in diff_result.stdout.splitlines() if line.strip()]
        except Exception:
            return []

    def _evaluate_technical_quality(self) -> EvaluationResult:
        findings: List[str] = []
        recommendations: List[str] = []
        evidence: List[ScoreEvidence] = []
        score = 1.0

        try:
            test_result = subprocess.run(
                ["python3", "-m", "pytest", "-q", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=90,
            )
            if test_result.returncode == 0:
                findings.append("Tests pass")
                evidence.append(ScoreEvidence("pytest", 0.6, 0.0, "pytest -q --tb=short exited 0"))
            else:
                findings.append("Tests failing")
                recommendations.append("Fix failing tests before merge")
                evidence.append(
                    ScoreEvidence(
                        "pytest",
                        0.6,
                        -0.35,
                        (test_result.stdout + test_result.stderr)[-1000:],
                        "Fix failing tests before merge",
                        True,
                    )
                )
                score -= 0.35
        except subprocess.TimeoutExpired:
            findings.append("Tests timed out")
            recommendations.append("Investigate long-running or hanging tests")
            evidence.append(ScoreEvidence("pytest_timeout", 0.6, -0.25, "pytest timed out", recommendations[-1], True))
            score -= 0.25
        except Exception as exc:
            findings.append(f"Could not run tests: {exc}")
            evidence.append(ScoreEvidence("pytest_error", 0.6, -0.1, str(exc), "Review test environment", True))
            score -= 0.1

        try:
            py_files = [
                str(path)
                for path in self.workspace_root.rglob("*.py")
                if not any(part in str(path) for part in [".venv", "__pycache__", "node_modules"])
            ]
            result = subprocess.run(
                ["python3", "-m", "py_compile", *py_files],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=45,
            )
            if result.returncode == 0:
                findings.append("No Python syntax errors")
                evidence.append(ScoreEvidence("py_compile", 0.3, 0.0, "py_compile exited 0"))
            else:
                findings.append("Python syntax errors present")
                recommendations.append("Fix Python syntax errors")
                evidence.append(
                    ScoreEvidence("py_compile", 0.3, -0.4, result.stderr[-1000:], "Fix Python syntax errors", True)
                )
                score -= 0.4
        except Exception as exc:
            evidence.append(ScoreEvidence("py_compile_error", 0.3, 0.0, str(exc)))

        try:
            lint_result = subprocess.run(
                ["flake8", "--count", "--select=E9,F63,F7,F82", "--show-source"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=30,
            )
            if lint_result.returncode == 0:
                findings.append("No critical lint errors")
                evidence.append(ScoreEvidence("critical_flake8", 0.1, 0.0, "flake8 critical check exited 0"))
            else:
                findings.append("Critical lint errors present")
                recommendations.append("Fix critical linting issues")
                evidence.append(
                    ScoreEvidence(
                        "critical_flake8",
                        0.1,
                        -0.2,
                        lint_result.stdout[-1000:],
                        "Fix critical linting issues",
                        True,
                    )
                )
                score -= 0.2
        except Exception as exc:
            evidence.append(ScoreEvidence("critical_flake8_unavailable", 0.1, 0.0, str(exc)))

        return EvaluationResult(
            category="Technical Quality",
            passed=score >= 0.7,
            score=max(0.0, score),
            weight=self.CATEGORY_WEIGHTS["Technical Quality"],
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
        )

    def _evaluate_boundary_safety(self, changed_files: List[str]) -> EvaluationResult:
        findings: List[str] = []
        recommendations: List[str] = []
        evidence: List[ScoreEvidence] = []
        score = 1.0
        boundary_files = [
            path for path in changed_files if any(path.startswith(pattern) for pattern in self.RUNTIME_BOUNDARY_PATTERNS)
        ]

        if boundary_files:
            findings.append(f"Boundary-sensitive files changed: {len(boundary_files)}")
            evidence.append(
                ScoreEvidence(
                    "boundary_sensitive_paths",
                    1.0,
                    -0.15,
                    ", ".join(boundary_files[:10]),
                    "Confirm tenant/logging/ethics/L1-L2-L3 impacts are covered by tests or docs",
                    True,
                )
            )
            recommendations.append("Confirm boundary-sensitive changes have explicit validation")
            score -= 0.15
        else:
            findings.append("No boundary-sensitive runtime paths changed")
            evidence.append(ScoreEvidence("boundary_sensitive_paths", 1.0, 0.0, "No configured boundary paths changed"))

        return EvaluationResult(
            category="Boundary Safety",
            passed=score >= 0.75,
            score=max(0.0, score),
            weight=self.CATEGORY_WEIGHTS["Boundary Safety"],
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
        )

    def _evaluate_traceability(self) -> EvaluationResult:
        findings: List[str] = []
        recommendations: List[str] = []
        evidence: List[ScoreEvidence] = []
        score = 1.0

        try:
            msg_result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=15,
            )
            commit_msg = msg_result.stdout.strip()
            has_issue_ref = "#" in commit_msg or "issue" in commit_msg.lower()
            has_functional_prefix = any(commit_msg.startswith(prefix) for prefix in ["fix:", "feat:", "docs:", "test:", "chore:"])
            if has_issue_ref:
                findings.append("Commit references issue/context")
                evidence.append(ScoreEvidence("issue_reference", 0.5, 0.0, commit_msg[:200]))
            else:
                findings.append("Commit lacks issue/context reference")
                recommendations.append("Reference the issue or rationale in commit/PR metadata")
                evidence.append(
                    ScoreEvidence(
                        "issue_reference",
                        0.5,
                        -0.15,
                        commit_msg[:200],
                        "Reference the issue or rationale in commit/PR metadata",
                        True,
                    )
                )
                score -= 0.15

            if has_functional_prefix:
                findings.append("Commit has functional prefix")
                evidence.append(ScoreEvidence("functional_prefix", 0.5, 0.0, commit_msg.splitlines()[0][:120]))
            else:
                findings.append("Commit lacks conventional functional prefix")
                recommendations.append("Use a functional prefix such as fix:, feat:, docs:, test:, or chore:")
                evidence.append(
                    ScoreEvidence(
                        "functional_prefix",
                        0.5,
                        -0.1,
                        commit_msg.splitlines()[0][:120],
                        "Use a functional commit prefix",
                        False,
                    )
                )
                score -= 0.1
        except Exception as exc:
            findings.append("Could not inspect commit message")
            evidence.append(ScoreEvidence("commit_message_error", 1.0, -0.05, str(exc), "Review commit metadata", True))
            score -= 0.05

        return EvaluationResult(
            category="Traceability",
            passed=score >= 0.7,
            score=max(0.0, score),
            weight=self.CATEGORY_WEIGHTS["Traceability"],
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
        )

    def _evaluate_documentation_fit(self, changed_files: List[str]) -> EvaluationResult:
        findings: List[str] = []
        evidence: List[ScoreEvidence] = []
        docs = [path for path in changed_files if path.endswith(('.md', '.json', '.yml', '.yaml'))]
        tests = [path for path in changed_files if path.startswith("tests/")]
        code = [path for path in changed_files if path.endswith(".py") and not path.startswith("tests/")]
        score = 1.0
        recommendations: List[str] = []

        if code and not tests:
            findings.append("Code changed without tests")
            recommendations.append("Add or identify validation for changed runtime code")
            evidence.append(
                ScoreEvidence("code_without_tests", 1.0, -0.25, ", ".join(code[:10]), recommendations[-1], True)
            )
            score -= 0.25
        else:
            findings.append("Documentation/test fit is acceptable")
            evidence.append(
                ScoreEvidence(
                    "doc_test_fit",
                    1.0,
                    0.0,
                    f"docs/config files={len(docs)}, tests={len(tests)}, runtime code={len(code)}",
                )
            )

        return EvaluationResult(
            category="Documentation Fit",
            passed=score >= 0.75,
            score=max(0.0, score),
            weight=self.CATEGORY_WEIGHTS["Documentation Fit"],
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
        )

    def _evaluate_symbolic_integrity(self, changed_files: List[str]) -> EvaluationResult:
        findings: List[str] = []
        recommendations: List[str] = []
        evidence: List[ScoreEvidence] = []
        score = 1.0
        critical_patterns = (
            "ethics_field",
            "geometric_ethics",
            "field_curvature",
            "aurora_seed_prompt",
            "LAYER_BOUNDARY_REFERENCE",
            "recovered_protocol",
        )
        critical_changes = [path for path in changed_files if any(pattern in path for pattern in critical_patterns)]

        if critical_changes:
            findings.append(f"Symbolic/ethics continuity files changed: {len(critical_changes)}")
            evidence.append(
                ScoreEvidence(
                    "symbolic_continuity_paths",
                    1.0,
                    -0.05,
                    ", ".join(critical_changes[:10]),
                    "Confirm canon posture and runtime boundaries are explicit",
                    True,
                )
            )
            recommendations.append("Confirm canon posture and runtime boundaries are explicit")
            score -= 0.05
        else:
            findings.append("No symbolic continuity hotspots changed")
            evidence.append(ScoreEvidence("symbolic_continuity_paths", 1.0, 0.0, "No configured symbolic hotspots changed"))

        return EvaluationResult(
            category="Symbolic Integrity",
            passed=score >= 0.75,
            score=max(0.0, score),
            weight=self.CATEGORY_WEIGHTS["Symbolic Integrity"],
            findings=findings,
            recommendations=recommendations,
            evidence=evidence,
        )

    def _generate_recommendation(
        self,
        overall_score: float,
        all_passed: bool,
        actionable_findings: List[Dict[str, Any]],
    ) -> str:
        if all_passed and overall_score >= 0.9 and not actionable_findings:
            return "No blocking automation findings. Keep PR comments quiet unless reviewer/CI evidence changes."
        if all_passed and overall_score >= 0.8:
            return "No blocking findings; review the listed actionable evidence before merge."
        if actionable_findings:
            categories = ", ".join(item["category"] for item in actionable_findings)
            return f"Needs targeted review in: {categories}."
        return "Needs review before merge. Check score evidence for details."


def main():
    """CLI interface for PR evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate Aurora PR with traceable scoring evidence")
    parser.add_argument('--pr', type=int, help='PR number to evaluate')
    parser.add_argument('--branch', help='Branch name to evaluate')
    parser.add_argument('--output', help='Save results to JSON file')

    args = parser.parse_args()

    evaluator = PREvaluator()
    results = evaluator.evaluate_pr(pr_number=args.pr, branch=args.branch)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")

    exit(0 if results['passed'] else 1)


if __name__ == "__main__":
    main()
