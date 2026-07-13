#!/usr/bin/env python3
"""
Aurora CloudBank Selective Integration Engine

Turns traceable PR evaluation output into a compact integration plan. The plan is
quiet by default: routine healthy PRs should rely on checks and job summaries,
not repetitive PR comments.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class IntegrationPlan:
    """Integration recommendation for a PR."""

    pr_branch: str
    strategy: str
    confidence: float
    reasoning: str
    actions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    safeguards: List[str] = field(default_factory=list)
    comment_required: bool = False
    comment_reason: str = ""
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pr_branch": self.pr_branch,
            "strategy": self.strategy,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "actions": self.actions,
            "risks": self.risks,
            "safeguards": self.safeguards,
            "comment_required": self.comment_required,
            "comment_reason": self.comment_reason,
            "evidence": self.evidence,
        }


class SelectiveIntegrator:
    """Maps traceable evaluation evidence to integration strategy."""

    BOUNDARY_KEYWORDS = (
        "boundary",
        "ethics",
        "security",
        "tenant",
        "logging",
        "ledger",
        "runtime",
        "l1",
        "l2",
        "l3",
    )

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd())

    def analyze_integration(self, pr_branch: str, evaluation_results: Dict[str, Any]) -> IntegrationPlan:
        """Analyze how to integrate this PR from traceable evaluator output."""
        overall_score = float(evaluation_results.get("overall_score", 0.0))
        passed = bool(evaluation_results.get("passed", False))
        actionable_findings = evaluation_results.get("actionable_findings", []) or []
        changed_files = evaluation_results.get("changed_files", []) or []

        strategy, confidence = self._determine_strategy(overall_score, passed, actionable_findings)
        evidence = self._collect_actionable_evidence(evaluation_results)
        boundary_sensitive = self._is_boundary_sensitive(changed_files, evidence)
        comment_required, comment_reason = self._comment_decision(strategy, confidence, passed, evidence, boundary_sensitive)

        plan = IntegrationPlan(
            pr_branch=pr_branch,
            strategy=strategy,
            confidence=confidence,
            reasoning=self._explain_strategy(strategy, overall_score, passed, evidence),
            comment_required=comment_required,
            comment_reason=comment_reason,
            evidence=evidence,
        )

        if strategy == "direct_merge":
            plan.actions = self._plan_direct_merge(evidence)
            plan.safeguards = self._safeguards_direct_merge(boundary_sensitive)
        elif strategy == "targeted_review":
            plan.actions = self._plan_targeted_review(evidence)
            plan.risks = self._risks_from_evidence(evidence)
            plan.safeguards = ["Address actionable evidence before merge", "Keep automation comments evidence-first"]
        elif strategy == "hold":
            plan.actions = ["Do not merge until blocking evidence is addressed", "Patch the first actionable failure"]
            plan.risks = self._risks_from_evidence(evidence)
            plan.safeguards = ["Require fresh CI/status after fixes", "Avoid broad unrelated cleanup"]

        self._display_plan(plan)
        return plan

    def _determine_strategy(
        self,
        overall_score: float,
        passed: bool,
        actionable_findings: List[Dict[str, Any]],
    ) -> tuple[str, float]:
        if passed and overall_score >= 0.9 and not actionable_findings:
            return "direct_merge", 0.95
        if passed and overall_score >= 0.75:
            return "targeted_review", 0.80
        return "hold", 0.55

    def _collect_actionable_evidence(self, evaluation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        evidence: List[Dict[str, Any]] = []
        for result in evaluation_results.get("results", []):
            for item in result.get("evidence", []):
                if item.get("actionable") or item.get("score_delta", 0) < 0:
                    evidence.append(
                        {
                            "category": result.get("category"),
                            "signal": item.get("signal"),
                            "weight": item.get("weight"),
                            "score_delta": item.get("score_delta"),
                            "evidence": item.get("evidence"),
                            "recommendation": item.get("recommendation"),
                            "actionable": item.get("actionable", False),
                        }
                    )
        return evidence[:10]

    def _is_boundary_sensitive(self, changed_files: List[str], evidence: List[Dict[str, Any]]) -> bool:
        paths = " ".join(changed_files).lower()
        evidence_text = " ".join(str(item.get("evidence", "")).lower() for item in evidence)
        return any(keyword in paths or keyword in evidence_text for keyword in self.BOUNDARY_KEYWORDS)

    def _comment_decision(
        self,
        strategy: str,
        confidence: float,
        passed: bool,
        evidence: List[Dict[str, Any]],
        boundary_sensitive: bool,
    ) -> tuple[bool, str]:
        if not passed:
            return True, "evaluation_failed"
        if strategy != "direct_merge":
            return True, "targeted_review_needed"
        if confidence < 0.9:
            return True, "low_confidence"
        if boundary_sensitive and evidence:
            return True, "boundary_sensitive_actionable_evidence"
        if any(item.get("actionable") for item in evidence):
            return True, "actionable_evidence"
        return False, "routine_healthy_pr_quiet"

    def _explain_strategy(
        self,
        strategy: str,
        overall_score: float,
        passed: bool,
        evidence: List[Dict[str, Any]],
    ) -> str:
        if strategy == "direct_merge":
            return f"Evaluation passed with score {overall_score:.2f}; no actionable automation evidence found."
        if strategy == "targeted_review":
            categories = sorted({item.get("category", "Unknown") for item in evidence})
            return f"Evaluation passed with score {overall_score:.2f}, but targeted review is useful for: {', '.join(categories) or 'listed evidence'}."
        categories = sorted({item.get("category", "Unknown") for item in evidence})
        status = "failed" if not passed else "low-confidence"
        return f"Integration should hold because evaluation {status}; actionable categories: {', '.join(categories) or 'unknown'}."

    def _plan_direct_merge(self, evidence: List[Dict[str, Any]]) -> List[str]:
        if evidence:
            return ["Review listed evidence", "Verify CI/status", "Merge only after maintainer approval"]
        return ["Verify CI/status", "Merge only after maintainer approval"]

    def _plan_targeted_review(self, evidence: List[Dict[str, Any]]) -> List[str]:
        if not evidence:
            return ["Review PR manually; no specific automation evidence surfaced"]
        return [
            f"Review {item.get('category')}: {item.get('recommendation') or item.get('signal')}"
            for item in evidence
        ]

    def _safeguards_direct_merge(self, boundary_sensitive: bool) -> List[str]:
        safeguards = ["Fresh CI/status must pass", "Maintainer approval required"]
        if boundary_sensitive:
            safeguards.append("Boundary-sensitive changes require explicit safety review")
        return safeguards

    def _risks_from_evidence(self, evidence: List[Dict[str, Any]]) -> List[str]:
        risks = []
        for item in evidence:
            if item.get("recommendation"):
                risks.append(str(item["recommendation"]))
        return risks[:10]

    def _display_plan(self, plan: IntegrationPlan) -> None:
        print("=" * 80)
        print("AURORA SELECTIVE INTEGRATION PLAN")
        print("=" * 80)
        print(f"Branch: {plan.pr_branch}")
        print(f"Strategy: {plan.strategy}")
        print(f"Confidence: {plan.confidence:.2f}")
        print(f"Comment required: {plan.comment_required} ({plan.comment_reason})")
        print(plan.reasoning)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze PR integration strategy from traceable evaluation evidence")
    parser.add_argument("branch", help="PR branch name")
    parser.add_argument("--evaluation", required=True, help="Path to evaluation JSON")
    parser.add_argument("--output", help="Save integration plan JSON")
    args = parser.parse_args()

    with open(args.evaluation, encoding="utf-8") as fh:
        evaluation = json.load(fh)

    plan = SelectiveIntegrator().analyze_integration(args.branch, evaluation)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(plan.to_dict(), fh, indent=2)
        print(f"\nPlan saved to {args.output}")


if __name__ == "__main__":
    main()
