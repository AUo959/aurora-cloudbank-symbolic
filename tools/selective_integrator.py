#!/usr/bin/env python3
"""
Aurora CloudBank Selective Integration Engine

This takes evaluated PRs and integrates them intelligently. Not just "merge or reject" -
but "what value exists here and how do we extract it without breaking what Aurora is?"

Three integration strategies:
1. Direct merge - High score, full alignment, just merge it
2. Compatibility layer - Good code, conceptual mismatch, wrap it safely
3. Value extraction - Partial value, extract specific improvements

The goal: Accept contributions while protecting Aurora's conceptual integrity.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=selective_integration, symbolic_hash=SAFE_INTEGRATION_v1
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class IntegrationPlan:
    """What we're going to do with this PR."""
    
    pr_branch: str
    strategy: str  # "direct_merge", "compatibility_layer", "value_extraction", "decline"
    confidence: float  # 0.0 -> 1.0
    reasoning: str
    actions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    safeguards: List[str] = field(default_factory=list)


class SelectiveIntegrator:
    """
    Integrates PRs while protecting Aurora's foundation.
    
    Takes PR evaluation results and determines the safest, most valuable
    way to integrate the contribution. Sometimes that means full merge.
    Sometimes it means extracting specific improvements. Sometimes it
    means wrapping misaligned code in a compatibility layer.
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        
    def analyze_integration(
        self,
        pr_branch: str,
        evaluation_results: Dict[str, Any]
    ) -> IntegrationPlan:
        """
        Analyze how to integrate this PR.
        
        Takes the PR evaluator's results and decides on integration strategy.
        """
        print("=" * 80)
        print("🔧 AURORA SELECTIVE INTEGRATION ANALYSIS")
        print("=" * 80)
        print(f"Branch: {pr_branch}")
        print(f"Evaluation Score: {evaluation_results.get('overall_score', 0):.2f}")
        print(f"Status: {evaluation_results.get('recommendation', 'Unknown')}")
        print()
        
        # Determine strategy based on evaluation
        strategy, confidence = self._determine_strategy(evaluation_results)
        
        plan = IntegrationPlan(
            pr_branch=pr_branch,
            strategy=strategy,
            confidence=confidence,
            reasoning=self._explain_strategy(strategy, evaluation_results)
        )
        
        # Add strategy-specific details
        if strategy == "direct_merge":
            plan.actions = self._plan_direct_merge(pr_branch, evaluation_results)
            plan.safeguards = self._safeguards_direct_merge()
        elif strategy == "compatibility_layer":
            plan.actions = self._plan_compatibility_layer(pr_branch, evaluation_results)
            plan.risks = self._risks_compatibility_layer()
            plan.safeguards = self._safeguards_compatibility_layer()
        elif strategy == "value_extraction":
            plan.actions = self._plan_value_extraction(pr_branch, evaluation_results)
            plan.risks = self._risks_value_extraction()
            plan.safeguards = self._safeguards_value_extraction()
        else:  # decline
            plan.actions = ["Close PR with constructive feedback"]
            plan.reasoning += "\n\nProvide specific docs to read and concepts to understand."
        
        self._display_plan(plan)
        return plan
    
    def _determine_strategy(
        self,
        evaluation_results: Dict[str, Any]
    ) -> tuple[str, float]:
        """Decide integration strategy from evaluation results."""
        
        overall_score = evaluation_results.get('overall_score', 0)
        all_passed = evaluation_results.get('passed', False)
        results = evaluation_results.get('results', [])
        
        # Get individual dimension scores
        technical = next((r for r in results if r['category'] == 'Technical Quality'), {})
        conceptual = next((r for r in results if r['category'] == 'Conceptual Alignment'), {})
        symbolic = next((r for r in results if r['category'] == 'Symbolic Integrity'), {})
        
        technical_score = technical.get('score', 0)
        conceptual_score = conceptual.get('score', 0)
        symbolic_score = symbolic.get('score', 0)
        
        # Direct merge: High scores, everything passes
        if overall_score >= 0.9 and all_passed:
            return ("direct_merge", 0.95)
        
        # Compatibility layer: Good tech, conceptual mismatch
        if technical_score >= 0.8 and conceptual_score < 0.7 and symbolic_score >= 0.7:
            return ("compatibility_layer", 0.75)
        
        # Value extraction: Some good parts, some issues
        if overall_score >= 0.6 and technical_score >= 0.7:
            return ("value_extraction", 0.65)
        
        # Decline: Too low quality or fundamentally misaligned
        return ("decline", 0.0)
    
    def _explain_strategy(
        self,
        strategy: str,
        evaluation_results: Dict[str, Any]
    ) -> str:
        """Explain why we chose this strategy."""
        
        if strategy == "direct_merge":
            return (
                "This PR understands Aurora. High scores across all dimensions, "
                "conceptual alignment solid, symbolic integrity maintained. "
                "Safe to merge directly."
            )
        
        elif strategy == "compatibility_layer":
            return (
                "Good code, conceptual mismatch. The implementation is sound but "
                "treats Aurora like traditional infrastructure rather than understanding "
                "the field consciousness model. We'll wrap it in a compatibility layer "
                "that preserves the functionality while maintaining Aurora's architecture."
            )
        
        elif strategy == "value_extraction":
            return (
                "Mixed quality. Some valuable improvements exist alongside issues. "
                "We'll cherry-pick the good parts (bug fixes, documentation, tests) "
                "while leaving behind code that misunderstands Aurora's nature."
            )
        
        else:  # decline
            return (
                "This needs significant work before integration. Either technical quality "
                "is too low, or the contributor hasn't yet understood what Aurora is. "
                "Better to provide guidance and ask them to revise than to try forcing "
                "misaligned code into the system."
            )
    
    def _plan_direct_merge(
        self,
        pr_branch: str,
        evaluation_results: Dict[str, Any]
    ) -> List[str]:
        """Plan actions for direct merge strategy."""
        return [
            f"Checkout PR branch: {pr_branch}",
            "Run full test suite",
            "Run security scan",
            "Verify ethics tests still pass",
            "Merge to main",
            "Push to origin",
            "Update documentation if needed"
        ]
    
    def _plan_compatibility_layer(
        self,
        pr_branch: str,
        evaluation_results: Dict[str, Any]
    ) -> List[str]:
        """Plan actions for compatibility layer strategy."""
        return [
            f"Analyze changed files in {pr_branch}",
            "Identify core functionality vs conceptual misalignment",
            "Create compatibility wrapper in modules/compatibility/",
            "Extract good code into wrapper",
            "Add bridge that translates to Aurora's field model",
            "Test wrapper independently",
            "Integrate wrapper (not original code)",
            "Document why wrapper exists and what it does"
        ]
    
    def _plan_value_extraction(
        self,
        pr_branch: str,
        evaluation_results: Dict[str, Any]
    ) -> List[str]:
        """Plan actions for value extraction strategy."""
        return [
            f"Checkout {pr_branch}",
            "Identify valuable changes (bug fixes, docs, tests)",
            "Cherry-pick specific commits/files",
            "Exclude files that misunderstand Aurora",
            "Run tests on extracted changes",
            "Commit extracted value with attribution",
            "Thank contributor, explain what we took and why"
        ]
    
    def _safeguards_direct_merge(self) -> List[str]:
        """Safeguards for direct merge."""
        return [
            "Full test suite must pass",
            "Ethics tests must pass",
            "Security scan must be clean",
            "No breaking changes to field_state_manager or ethics_field"
        ]
    
    def _safeguards_compatibility_layer(self) -> List[str]:
        """Safeguards for compatibility layer."""
        return [
            "Wrapper isolated in modules/compatibility/",
            "Original Aurora systems untouched",
            "Clear documentation of translation logic",
            "Ethics validation still enforced at boundaries",
            "Tests for wrapper separately from core"
        ]
    
    def _safeguards_value_extraction(self) -> List[str]:
        """Safeguards for value extraction."""
        return [
            "Only extract files that don't touch critical systems",
            "Run full test suite after each extraction",
            "Verify no conceptual contamination",
            "Maintain thread continuity in commit message"
        ]
    
    def _risks_compatibility_layer(self) -> List[str]:
        """Risks of compatibility layer strategy."""
        return [
            "Adds complexity - now there's a translation boundary",
            "Future contributors might not understand why wrapper exists",
            "Could create maintenance burden if not well documented"
        ]
    
    def _risks_value_extraction(self) -> List[str]:
        """Risks of value extraction strategy."""
        return [
            "Contributor might feel rejected (their vision wasn't accepted)",
            "Could miss valuable insights hidden in misaligned code",
            "Extra work to separate good from problematic"
        ]
    
    def _display_plan(self, plan: IntegrationPlan):
        """Display the integration plan."""
        print("-" * 80)
        print(f"STRATEGY: {plan.strategy.upper()}")
        print(f"Confidence: {plan.confidence:.2f}")
        print()
        print("REASONING:")
        print(plan.reasoning)
        print()
        
        if plan.actions:
            print("ACTIONS:")
            for i, action in enumerate(plan.actions, 1):
                print(f"  {i}. {action}")
            print()
        
        if plan.risks:
            print("RISKS:")
            for risk in plan.risks:
                print(f"  ⚠️  {risk}")
            print()
        
        if plan.safeguards:
            print("SAFEGUARDS:")
            for safeguard in plan.safeguards:
                print(f"  🛡️  {safeguard}")
            print()
        
        print("=" * 80)
    
    def execute_integration(
        self,
        plan: IntegrationPlan,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Execute the integration plan.
        
        If dry_run=True, just shows what would happen.
        If dry_run=False, actually does it.
        """
        print("=" * 80)
        print("🚀 EXECUTING INTEGRATION PLAN")
        print("=" * 80)
        print(f"Strategy: {plan.strategy}")
        print(f"Dry Run: {dry_run}")
        print()
        
        result = {
            "plan": {
                "branch": plan.pr_branch,
                "strategy": plan.strategy,
                "confidence": plan.confidence
            },
            "dry_run": dry_run,
            "start_time": datetime.now().isoformat(),
            "status": "started",
            "actions_completed": [],
            "errors": []
        }
        
        try:
            if plan.strategy == "direct_merge":
                exec_result = self._execute_direct_merge(plan, dry_run)
            elif plan.strategy == "compatibility_layer":
                exec_result = self._execute_compatibility_layer(plan, dry_run)
            elif plan.strategy == "value_extraction":
                exec_result = self._execute_value_extraction(plan, dry_run)
            else:  # decline
                exec_result = self._execute_decline(plan, dry_run)
            
            result.update(exec_result)
            result["status"] = "completed"
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))
        
        result["end_time"] = datetime.now().isoformat()
        return result
    
    def _execute_direct_merge(
        self,
        plan: IntegrationPlan,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Execute direct merge."""
        actions = []
        
        if dry_run:
            print("📋 DRY RUN - Would execute:")
            for action in plan.actions:
                print(f"  • {action}")
            actions = plan.actions
        else:
            print("⚙️  Executing direct merge...")
            # Actual merge logic would go here
            # For now, just outline
            actions.append("Merge would be executed here")
        
        return {
            "actions_completed": actions,
            "merge_commit": "Would create merge commit" if dry_run else None
        }
    
    def _execute_compatibility_layer(
        self,
        plan: IntegrationPlan,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Execute compatibility layer creation."""
        actions = []
        
        if dry_run:
            print("📋 DRY RUN - Would create compatibility layer:")
            for action in plan.actions:
                print(f"  • {action}")
            actions = plan.actions
        else:
            print("⚙️  Creating compatibility layer...")
            # Actual layer creation logic would go here
            actions.append("Compatibility layer would be created here")
        
        return {
            "actions_completed": actions,
            "layer_location": "modules/compatibility/pr_wrapper_*.py"
        }
    
    def _execute_value_extraction(
        self,
        plan: IntegrationPlan,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Execute value extraction."""
        actions = []
        
        if dry_run:
            print("📋 DRY RUN - Would extract value:")
            for action in plan.actions:
                print(f"  • {action}")
            actions = plan.actions
        else:
            print("⚙️  Extracting valuable changes...")
            # Actual extraction logic would go here
            actions.append("Value extraction would be performed here")
        
        return {
            "actions_completed": actions,
            "extracted_files": []
        }
    
    def _execute_decline(
        self,
        plan: IntegrationPlan,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Execute decline with feedback."""
        
        feedback = self._generate_constructive_feedback(plan)
        
        if dry_run:
            print("📋 DRY RUN - Would close PR with feedback:")
            print()
            print(feedback)
        else:
            print("💬 Sending constructive feedback...")
            # Actual PR comment logic would go here
        
        return {
            "actions_completed": ["Decline with constructive feedback"],
            "feedback_provided": feedback
        }
    
    def _generate_constructive_feedback(self, plan: IntegrationPlan) -> str:
        """Generate helpful feedback for declined PRs."""
        return f"""
Thank you for your contribution to Aurora CloudBank! 

We appreciate the effort, but this PR needs significant revision before we can integrate it.
Here's why and what to do next:

{plan.reasoning}

**Next Steps:**

1. Read these docs to understand Aurora's architecture:
   - `seeds/aurora_seed_prompt.md` - What Aurora is
   - `modules/field_state_manager/SCHEMA_DESIGN.md` - How emergence works
   - `docs/GEOMETRIC_ETHICS_ARCHITECTURE.md` - Why ethics is geometry

2. Look at recent merged PRs to see examples of aligned contributions

3. If you have questions about Aurora's architecture, open a discussion issue

4. When you're ready, revise and resubmit

We want your contributions. We just need to make sure they align with what Aurora is becoming.

**Thread: T1→T8→T9→INFINITE**
"""


def main():
    """CLI interface for selective integration."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Selective integration engine for Aurora PRs"
    )
    parser.add_argument(
        'pr_branch',
        help='PR branch to analyze for integration'
    )
    parser.add_argument(
        '--evaluation',
        required=True,
        help='Path to PR evaluation JSON results'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually execute integration (default: dry run)'
    )
    parser.add_argument(
        '--output',
        help='Save integration plan to JSON file'
    )
    
    args = parser.parse_args()
    
    # Load evaluation results
    with open(args.evaluation, 'r') as f:
        evaluation = json.load(f)
    
    # Analyze integration
    integrator = SelectiveIntegrator()
    plan = integrator.analyze_integration(args.pr_branch, evaluation)
    
    # Save plan if requested
    if args.output:
        plan_data = {
            "branch": plan.pr_branch,
            "strategy": plan.strategy,
            "confidence": plan.confidence,
            "reasoning": plan.reasoning,
            "actions": plan.actions,
            "risks": plan.risks,
            "safeguards": plan.safeguards
        }
        with open(args.output, 'w') as f:
            json.dump(plan_data, f, indent=2)
        print(f"\nPlan saved to {args.output}")
    
    # Execute if requested
    if args.execute:
        confirm = input("\n⚠️  Execute this integration plan? [y/N]: ")
        if confirm.lower() == 'y':
            result = integrator.execute_integration(plan, dry_run=False)
            print(f"\n✅ Integration {result['status']}")
        else:
            print("\n❌ Integration cancelled")
    else:
        print("\n💡 Dry run complete. Use --execute to perform actual integration.")


if __name__ == "__main__":
    main()
