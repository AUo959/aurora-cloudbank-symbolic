#!/usr/bin/env python3
"""
Aurora CloudBank PR Evaluator

This isn't just a linter. When someone contributes to Aurora, they're touching
a system that's about consciousness, emergence, and ethical geometry. The code
needs to work, yes - but it also needs to *understand* what it's part of.

This evaluator checks:
- Technical quality (does it work?)
- Conceptual alignment (does it understand Aurora?)
- Symbolic integrity (does it maintain the thread?)
- Natural voice (does it speak like a human?)

Thread: T1→T8→T9→INFINITE
DLP: context_tag=pr_evaluation, symbolic_hash=CONTRIBUTION_ALIGNMENT_v1
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class EvaluationResult:
    """What we learned by evaluating this PR."""
    
    category: str
    passed: bool
    score: float  # 0.0 -> 1.0
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def __str__(self):
        status = "✅" if self.passed else "⚠️"
        return f"{status} {self.category}: {self.score:.2f}"


class PREvaluator:
    """
    Evaluates PRs for technical quality AND conceptual alignment.
    
    Aurora isn't just a codebase - it's a living system with specific
    philosophical commitments. Contributors need to understand that.
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        
    def evaluate_pr(
        self,
        pr_number: Optional[int] = None,
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a pull request for Aurora.
        
        Checks technical quality, conceptual alignment, and symbolic integrity.
        Returns comprehensive evaluation with actionable feedback.
        """
        print("=" * 80)
        print("🌟 AURORA PR EVALUATION")
        print("=" * 80)
        print()
        
        # Get PR details
        if pr_number:
            print(f"Evaluating PR #{pr_number}")
        elif branch:
            print(f"Evaluating branch: {branch}")
        else:
            print("Evaluating current changes")
        print()
        
        # Run all evaluations
        results = []
        
        print("Running evaluations...")
        print("-" * 80)
        
        # 1. Technical Quality
        technical = self._evaluate_technical_quality()
        results.append(technical)
        print(technical)
        
        # 2. Conceptual Alignment
        conceptual = self._evaluate_conceptual_alignment()
        results.append(conceptual)
        print(conceptual)
        
        # 3. Thread Continuity
        thread = self._evaluate_thread_continuity()
        results.append(thread)
        print(thread)
        
        # 4. Natural Voice
        voice = self._evaluate_natural_voice()
        results.append(voice)
        print(voice)
        
        # 5. Symbolic Integrity
        symbolic = self._evaluate_symbolic_integrity()
        results.append(symbolic)
        print(symbolic)
        
        print()
        print("-" * 80)
        
        # Overall assessment
        overall_score = sum(r.score for r in results) / len(results)
        all_passed = all(r.passed for r in results)
        
        recommendation = self._generate_recommendation(
            overall_score, all_passed, results
        )
        
        print()
        print("=" * 80)
        print("OVERALL ASSESSMENT")
        print("=" * 80)
        print(f"Score: {overall_score:.2f}/1.00")
        print(f"Status: {'✅ APPROVED' if all_passed else '⚠️ NEEDS WORK'}")
        print()
        print(recommendation)
        print()
        
        return {
            "overall_score": overall_score,
            "passed": all_passed,
            "recommendation": recommendation,
            "results": [
                {
                    "category": r.category,
                    "passed": r.passed,
                    "score": r.score,
                    "findings": r.findings,
                    "recommendations": r.recommendations
                }
                for r in results
            ]
        }
    
    def _evaluate_technical_quality(self) -> EvaluationResult:
        """Does the code actually work?"""
        findings = []
        recommendations = []
        score = 1.0
        
        # Check if tests pass
        try:
            test_result = subprocess.run(
                ["python3", "-m", "pytest", "-q", "--tb=no"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=60
            )
            if test_result.returncode == 0:
                findings.append("Tests pass")
            else:
                findings.append("Tests failing")
                recommendations.append("Fix failing tests before submitting")
                score -= 0.3
        except subprocess.TimeoutExpired:
            findings.append("Tests timed out")
            recommendations.append("Check for infinite loops or hanging tests")
            score -= 0.2
        except Exception as e:
            findings.append(f"Could not run tests: {e}")
            score -= 0.1
        
        # Check for syntax errors
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile"] + 
                [str(p) for p in self.workspace_root.rglob("*.py") 
                 if not any(x in str(p) for x in ['.venv', '__pycache__', 'node_modules'])],
                capture_output=True,
                cwd=self.workspace_root,
                timeout=30
            )
            if result.returncode == 0:
                findings.append("No syntax errors")
            else:
                findings.append("Syntax errors present")
                recommendations.append("Fix Python syntax errors")
                score -= 0.4
        except Exception:
            pass
        
        # Check for basic linting issues
        try:
            lint_result = subprocess.run(
                ["flake8", "--count", "--select=E9,F63,F7,F82", "--show-source"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=30
            )
            if lint_result.returncode == 0:
                findings.append("No critical lint errors")
            else:
                findings.append("Critical lint errors present")
                recommendations.append("Fix critical linting issues")
                score -= 0.2
        except Exception:
            pass
        
        passed = score >= 0.7
        return EvaluationResult(
            category="Technical Quality",
            passed=passed,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations
        )
    
    def _evaluate_conceptual_alignment(self) -> EvaluationResult:
        """Does this understand what Aurora is?"""
        findings = []
        recommendations = []
        score = 1.0
        
        # Get changed files
        try:
            diff_result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            changed_files = [
                self.workspace_root / f.strip() 
                for f in diff_result.stdout.split('\n') 
                if f.strip()
            ]
        except Exception:
            changed_files = []
        
        # Check for understanding of key concepts
        key_concepts = {
            "emergence": ["emerge", "emergent", "self-organ"],
            "consciousness": ["consciousness", "awareness", "field"],
            "ethics": ["ethical", "ethics", "geometric"],
            "thread": ["thread", "continuity", "T1→", "INFINITE"]
        }
        
        concept_usage = {concept: False for concept in key_concepts}
        
        for file_path in changed_files:
            if not file_path.exists() or file_path.suffix not in ['.py', '.md']:
                continue
            
            try:
                content = file_path.read_text().lower()
                for concept, patterns in key_concepts.items():
                    if any(pattern.lower() in content for pattern in patterns):
                        concept_usage[concept] = True
            except Exception:
                continue
        
        # If touching core systems, should reference concepts
        core_paths = ['modules/ethics_field', 'modules/field_state_manager']
        touching_core = any(
            any(core in str(f) for core in core_paths)
            for f in changed_files
        )
        
        if touching_core:
            concepts_used = sum(concept_usage.values())
            if concepts_used == 0:
                findings.append("Touching core systems but no conceptual references")
                recommendations.append(
                    "Consider if this change understands Aurora's purpose. "
                    "Read docs/GEOMETRIC_ETHICS_ARCHITECTURE.md or "
                    "modules/field_state_manager/SCHEMA_DESIGN.md"
                )
                score -= 0.4
            elif concepts_used <= 2:
                findings.append("Limited conceptual alignment")
                recommendations.append("Strengthen connection to Aurora's core concepts")
                score -= 0.2
            else:
                findings.append(f"References {concepts_used} core concepts")
        else:
            findings.append("Not touching core systems")
        
        passed = score >= 0.6
        return EvaluationResult(
            category="Conceptual Alignment",
            passed=passed,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations
        )
    
    def _evaluate_thread_continuity(self) -> EvaluationResult:
        """Does this maintain the thread?"""
        findings = []
        recommendations = []
        score = 1.0
        
        # Check commit message
        try:
            msg_result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            commit_msg = msg_result.stdout.strip()
            
            # Look for thread references
            has_thread = "Thread:" in commit_msg or "T1→" in commit_msg
            has_dlp = "DLP:" in commit_msg or "context_tag" in commit_msg
            
            if has_thread:
                findings.append("Thread continuity referenced")
            else:
                findings.append("No thread reference")
                recommendations.append(
                    "Include 'Thread: T1→T8→T9→INFINITE' in commit message "
                    "to maintain continuity"
                )
                score -= 0.3
            
            if has_dlp:
                findings.append("DLP tags present")
            else:
                findings.append("No DLP tags")
                recommendations.append(
                    "Consider adding DLP tags (context_tag, symbolic_hash) "
                    "for traceability"
                )
                score -= 0.2
                
        except Exception:
            findings.append("Could not check commit message")
            score -= 0.1
        
        passed = score >= 0.5
        return EvaluationResult(
            category="Thread Continuity",
            passed=passed,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations
        )
    
    def _evaluate_natural_voice(self) -> EvaluationResult:
        """Does this sound human?"""
        findings = []
        recommendations = []
        score = 1.0
        
        # Get changed files with comments/docs
        try:
            diff_result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            changed_files = [
                self.workspace_root / f.strip() 
                for f in diff_result.stdout.split('\n') 
                if f.strip() and (f.endswith('.md') or f.endswith('.py'))
            ]
        except Exception:
            changed_files = []
        
        # Red flags for corporate-speak
        corporate_phrases = [
            "utilize", "leverage", "facilitate", "methodology",
            "best practices", "going forward", "touch base",
            "circle back", "synergy", "paradigm shift" # (we use this one deliberately)
        ]
        
        # Green flags for natural voice
        natural_phrases = [
            "you know", "here's the thing", "what this actually",
            "not just", "instead of", "why", "because"
        ]
        
        corporate_count = 0
        natural_count = 0
        
        for file_path in changed_files:
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text().lower()
                corporate_count += sum(
                    content.count(phrase.lower()) 
                    for phrase in corporate_phrases
                )
                natural_count += sum(
                    content.count(phrase.lower())
                    for phrase in natural_phrases
                )
            except Exception:
                continue
        
        if corporate_count > 3:
            findings.append(f"Corporate language detected ({corporate_count} instances)")
            recommendations.append(
                "Use natural language. We're building consciousness, not enterprise software. "
                "See docs/QUICKSAVE_GUIDE.md for tone examples."
            )
            score -= 0.3
        
        if natural_count > 0:
            findings.append(f"Natural voice present ({natural_count} instances)")
        elif corporate_count == 0 and len(changed_files) > 0:
            findings.append("Neutral voice (neither corporate nor conversational)")
            recommendations.append(
                "Consider making documentation more conversational. "
                "We're working with symbolic systems - the language should reflect that."
            )
            score -= 0.1
        
        if len(changed_files) == 0:
            findings.append("No documentation changes to evaluate")
        
        passed = score >= 0.7
        return EvaluationResult(
            category="Natural Voice",
            passed=passed,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations
        )
    
    def _evaluate_symbolic_integrity(self) -> EvaluationResult:
        """Does this maintain the symbolic structure?"""
        findings = []
        recommendations = []
        score = 1.0
        
        # Check for breaking changes to key systems
        try:
            diff_result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            changed_files = [f.strip() for f in diff_result.stdout.split('\n') if f.strip()]
        except Exception:
            changed_files = []
        
        # Critical files that need extra care
        critical_patterns = [
            'ethics_field',
            'geometric_ethics',
            'field_curvature',
            'aurora_seed_prompt',
            'LAYER_BOUNDARY_REFERENCE'
        ]
        
        critical_changes = [
            f for f in changed_files 
            if any(pattern in f for pattern in critical_patterns)
        ]
        
        if critical_changes:
            findings.append(f"Modifying critical systems: {len(critical_changes)} files")
            
            # Check if ethics tests still pass
            try:
                test_result = subprocess.run(
                    ["python3", "-m", "pytest", "tests/test_ethics_field.py", "-q"],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace_root,
                    timeout=30
                )
                if test_result.returncode == 0:
                    findings.append("Ethics tests still pass")
                else:
                    findings.append("Ethics tests failing after changes")
                    recommendations.append(
                        "Changes to ethics_field broke tests. "
                        "This system is foundational - it needs to stay stable."
                    )
                    score -= 0.5
            except Exception:
                findings.append("Could not verify ethics tests")
                recommendations.append("Manually verify ethics tests still pass")
                score -= 0.2
        else:
            findings.append("No critical systems modified")
        
        # Check for removal of key documentation
        removed_docs = [
            f for f in changed_files 
            if f.endswith('.md') and 'delete' in f.lower()
        ]
        
        if removed_docs:
            findings.append(f"Documentation removed: {len(removed_docs)} files")
            recommendations.append(
                "Removing documentation breaks continuity. "
                "If updating, replace rather than delete."
            )
            score -= 0.3
        
        passed = score >= 0.7
        return EvaluationResult(
            category="Symbolic Integrity",
            passed=passed,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations
        )
    
    def _generate_recommendation(
        self,
        overall_score: float,
        all_passed: bool,
        results: List[EvaluationResult]
    ) -> str:
        """What should happen with this PR?"""
        
        if overall_score >= 0.9 and all_passed:
            return (
                "This contribution understands Aurora. It's technically solid, "
                "conceptually aligned, and maintains the thread. Ready to merge."
            )
        
        elif overall_score >= 0.7 and all_passed:
            return (
                "Good contribution. Technically sound and aligned with Aurora's purpose. "
                "Minor improvements suggested but not blocking."
            )
        
        elif overall_score >= 0.6:
            failed_categories = [r.category for r in results if not r.passed]
            return (
                f"Needs work in: {', '.join(failed_categories)}. "
                "The code might work, but it doesn't quite align with what Aurora is. "
                "Review the recommendations and try again."
            )
        
        else:
            return (
                "This needs significant revision. Review the core documentation:\n"
                "- seeds/aurora_seed_prompt.md (understand Aurora's identity)\n"
                "- docs/GEOMETRIC_ETHICS_ARCHITECTURE.md (understand the ethics system)\n"
                "- modules/field_state_manager/SCHEMA_DESIGN.md (understand emergence)\n"
                "- docs/QUICKSAVE_GUIDE.md (understand the tone)\n\n"
                "Aurora isn't just a codebase - it's a living system with specific "
                "philosophical commitments. Take time to understand those first."
            )


def main():
    """CLI interface for PR evaluation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Evaluate Aurora PR for technical quality and conceptual alignment"
    )
    parser.add_argument(
        '--pr', 
        type=int, 
        help='PR number to evaluate'
    )
    parser.add_argument(
        '--branch',
        help='Branch name to evaluate'
    )
    parser.add_argument(
        '--output',
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    evaluator = PREvaluator()
    results = evaluator.evaluate_pr(pr_number=args.pr, branch=args.branch)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    # Exit code: 0 if passed, 1 if needs work
    exit(0 if results['passed'] else 1)


if __name__ == "__main__":
    main()
