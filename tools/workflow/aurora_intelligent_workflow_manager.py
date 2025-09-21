#!/usr/bin/env python3
"""
Aurora CloudBank Intelligent Workflow Manager
Master orchestrator that integrates workflow validation and optimization.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class IntelligentWorkflowManager:
    """Master workflow manager that prevents failures and optimizes performance."""

    def __init__(self) -> None:
        self.tools_dir = Path("tools/workflow")
        self.failure_prevention_tool = self.tools_dir / "aurora_failure_prevention_system.py"
        self.optimization_tool = self.tools_dir / "aurora_workflow_optimization_manager.py"

    def run_intelligent_workflow_cycle(self, operation_name: str = "workflow") -> Dict:
        """Run complete intelligent workflow cycle."""
        print("🧠 Aurora Intelligent Workflow Manager")
        print("=" * 50)
        print(f"🎯 Operation: {operation_name}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        cycle_start = datetime.now()
        results: Dict = {
            "operation": operation_name,
            "timestamp": cycle_start.isoformat(),
            "phases": {},
            "total_time_saved_minutes": 0,
            "execution_ready": False,
            "summary": {},
        }

        # Phase 1: Pre-flight validation
        print("\n🚁 Phase 1: Pre-flight Validation")
        print("-" * 30)
        preflight_result = self.run_preflight_checks()
        results["phases"]["preflight"] = preflight_result

        # Phase 2: Workflow optimization (if needed)
        if not preflight_result.get("execution_ready", False):
            print("\n⚡ Phase 2: Workflow Optimization")
            print("-" * 30)
            optimization_result = self.run_workflow_optimization()
            results["phases"]["optimization"] = optimization_result

            # Re-run pre-flight after optimization
            print("\n🔄 Phase 2b: Post-optimization Validation")
            print("-" * 30)
            post_opt_result = self.run_preflight_checks()
            results["phases"]["post_optimization_check"] = post_opt_result
            results["execution_ready"] = post_opt_result.get("execution_ready", False)
        else:
            results["execution_ready"] = True

        # Phase 3: Generate execution recommendations
        print("\n🎯 Phase 3: Execution Planning")
        print("-" * 30)
        execution_plan = self.generate_execution_plan(results)
        results["phases"]["execution_plan"] = execution_plan

        # Calculate total benefits
        total_time_saved = 0
        for phase_result in results["phases"].values():
            if isinstance(phase_result, dict):
                phase_time_saved = phase_result.get("time_saved_minutes", 0)
                if isinstance(phase_time_saved, (int, float)):
                    total_time_saved += phase_time_saved
        results["total_time_saved_minutes"] = total_time_saved

        # Generate summary
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        results["summary"] = {
            "cycle_duration_seconds": cycle_duration,
            "execution_ready": results["execution_ready"],
            "total_time_saved_minutes": total_time_saved,
            "roi_ratio": total_time_saved / max(cycle_duration / 60, 0.1),
            "recommendation": "PROCEED" if results["execution_ready"] else "FIX_ISSUES",
        }

        self.print_cycle_summary(results)
        return results

    def run_preflight_checks(self) -> Dict:
        """Run pre-flight validation checks."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.failure_prevention_tool)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            output_lines = result.stdout.splitlines()
            time_saved = 0
            execution_ready = result.returncode == 0
            for line in output_lines:
                if "Estimated Time Saved:" in line:
                    try:
                        time_saved = int(line.split(":")[1].strip().split()[0])
                    except (ValueError, IndexError):
                        pass
            return {
                "status": "SUCCESS" if result.returncode == 0 else "ISSUES_FOUND",
                "execution_ready": execution_ready,
                "time_saved_minutes": time_saved,
                "output": result.stdout,
                "details": "Pre-flight validation completed",
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "TIMEOUT",
                "execution_ready": False,
                "time_saved_minutes": 0,
                "details": "Pre-flight check timed out",
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "execution_ready": False,
                "time_saved_minutes": 0,
                "details": f"Pre-flight check failed: {e}",
            }

    def run_workflow_optimization(self) -> Dict:
        """Run comprehensive workflow optimization."""
        try:
            result = subprocess.run(
                [sys.executable, str(self.optimization_tool)],
                capture_output=True,
                text=True,
                timeout=180,
            )
            output_lines = result.stdout.splitlines()
            time_saved = 0
            optimizations_applied = 0
            for line in output_lines:
                if "Time Saved per Run:" in line:
                    try:
                        time_saved = int(line.split("~")[1].strip().split()[0])
                    except (ValueError, IndexError):
                        pass
                elif "Optimizations Applied:" in line:
                    try:
                        optimizations_applied = int(line.split(":")[1].strip().split("/")[0])
                    except (ValueError, IndexError):
                        pass
            return {
                "status": "SUCCESS" if result.returncode == 0 else "ISSUES_FOUND",
                "optimizations_applied": optimizations_applied,
                "time_saved_minutes": time_saved,
                "output": result.stdout,
                "details": f"Applied {optimizations_applied} workflow optimizations",
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "TIMEOUT",
                "optimizations_applied": 0,
                "time_saved_minutes": 0,
                "details": "Workflow optimization timed out",
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "optimizations_applied": 0,
                "time_saved_minutes": 0,
                "details": f"Workflow optimization failed: {e}",
            }

    def generate_execution_plan(self, results: Dict) -> Dict:
        """Generate intelligent execution plan based on analysis results."""
        plan = {
            "recommendation": "UNKNOWN",
            "confidence": 0,
            "next_steps": [],
            "risk_assessment": "UNKNOWN",
            "estimated_success_rate": 0,
        }

        execution_ready = results.get("execution_ready", False)
        total_time_saved = results.get("total_time_saved_minutes", 0)

        if execution_ready:
            plan.update(
                {
                    "recommendation": "PROCEED_WITH_CONFIDENCE",
                    "confidence": 95,
                    "risk_assessment": "LOW",
                    "estimated_success_rate": 95,
                    "next_steps": [
                        "🚀 Execute planned workflow/operation",
                        "📊 Monitor execution metrics",
                        "🔄 Apply lessons learned for future runs",
                    ],
                }
            )
        elif total_time_saved > 30:
            plan.update(
                {
                    "recommendation": "FIX_CRITICAL_THEN_PROCEED",
                    "confidence": 80,
                    "risk_assessment": "MEDIUM",
                    "estimated_success_rate": 70,
                    "next_steps": [
                        "🔧 Address critical issues identified",
                        "✅ Re-run pre-flight validation",
                        "🚀 Proceed when validation passes",
                    ],
                }
            )
        else:
            plan.update(
                {
                    "recommendation": "MANUAL_REVIEW_REQUIRED",
                    "confidence": 60,
                    "risk_assessment": "HIGH",
                    "estimated_success_rate": 40,
                    "next_steps": [
                        "👀 Manual review of identified issues",
                        "🛠️  Apply targeted fixes",
                        "🔄 Re-run intelligent workflow cycle",
                    ],
                }
            )

        return plan

    def print_cycle_summary(self, results: Dict) -> None:
        """Print comprehensive cycle summary."""
        print(f"\n{'=' * 50}")
        print("🧠 INTELLIGENT WORKFLOW CYCLE SUMMARY")
        print(f"{'=' * 50}")

        summary = results["summary"]
        execution_plan = results["phases"].get("execution_plan", {})

        status_icon = "🟢" if results["execution_ready"] else "🟡"
        print(f"{status_icon} Execution Ready: {'YES' if results['execution_ready'] else 'NEEDS_ATTENTION'}")
        print(f"⏱️  Cycle Duration: {summary['cycle_duration_seconds']:.1f}s")
        print(f"💰 Time Saved: {summary['total_time_saved_minutes']} minutes")
        print(f"📊 ROI Ratio: {summary['roi_ratio']:.1f}x")

        if execution_plan:
            print("\n🎯 EXECUTION PLAN:")
            print(f"   Recommendation: {execution_plan.get('recommendation', 'N/A')}")
            print(f"   Confidence: {execution_plan.get('confidence', 0)}%")
            print(f"   Success Rate: {execution_plan.get('estimated_success_rate', 0)}%")
            print(f"   Risk Level: {execution_plan.get('risk_assessment', 'N/A')}")

        if execution_plan.get("next_steps"):
            print("\n📋 NEXT STEPS:")
            for step in execution_plan["next_steps"]:
                print(f"   {step}")

        print("\n💡 TIME SAVINGS ANALYSIS:")
        for phase_name, phase_result in results["phases"].items():
            if isinstance(phase_result, dict) and "time_saved_minutes" in phase_result:
                time_saved = phase_result["time_saved_minutes"]
                if time_saved > 0:
                    print(f"   {phase_name.title()}: {time_saved} minutes")

        print("\n🎉 Intelligent workflow cycle complete!")

        report_file = f"intelligent_workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"📄 Detailed report saved to: {report_file}")


def main() -> None:
    """CLI interface for intelligent workflow manager."""
    parser = argparse.ArgumentParser(description="Aurora Intelligent Workflow Manager")
    parser.add_argument(
        "operation", nargs="?", default="general", help='Operation name (e.g., "deploy", "test", "build")'
    )
    parser.add_argument("--quick", action="store_true", help="Run quick validation only")
    parser.add_argument("--force-optimize", action="store_true", help="Force optimization even if pre-flight passes")
    args = parser.parse_args()

    iwm = IntelligentWorkflowManager()
    print("🧠 Aurora Intelligent Workflow Manager")
    print("   Preventing failed runs, optimizing performance")
    print()

    if args.quick:
        print("🚁 Quick validation mode")
        quick = iwm.run_preflight_checks()
        if quick.get("execution_ready"):
            print("✅ Quick validation passed - you're good to go!")
            sys.exit(0)
        else:
            print("❌ Quick validation failed - run full cycle for optimization")
            sys.exit(1)

    results = iwm.run_intelligent_workflow_cycle(args.operation)
    if results.get("execution_ready"):
        print(f"\n✅ Ready to proceed with '{args.operation}' operation")
        sys.exit(0)
    else:
        print(f"\n⚠️  '{args.operation}' operation needs attention before proceeding")
        sys.exit(1)


if __name__ == "__main__":
    main()
