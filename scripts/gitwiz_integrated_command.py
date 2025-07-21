#!/usr/bin/env python3
"""

            import traceback

GitWiz Integrated Command Interface
==================================

Unified command interface for GitWiz Enhanced with integrated lint cleanup automation.
Provides seamless access to all GitWiz capabilities including the new lint cleanup manager.

Usage:
    python gitwiz_integrated_command.py --help
    python gitwiz_integrated_command.py quality-check --auto-fix
    python gitwiz_integrated_command.py maintenance --aggressive
    python gitwiz_integrated_command.py lint-scan --detailed
    python gitwiz_integrated_command.py workflow --enhanced

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""


# Configure logging
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import GitWiz components
try:

    ENHANCED_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhanced GitWiz not available: {e}")
    ENHANCED_AVAILABLE = False

try:

    LINT_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Lint Cleanup Manager not available: {e}")
    LINT_MANAGER_AVAILABLE = False

try:

    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Workflow Orchestrator not available: {e}")
    ORCHESTRATOR_AVAILABLE = False

class GitWizIntegratedCommand:
    """Unified command interface for all GitWiz capabilities."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.enhanced_gitwiz = None
        self.lint_manager = None
        self.orchestrator = None

        # Initialize available components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize available GitWiz components."""
        try:
            if ENHANCED_AVAILABLE:
                self.enhanced_gitwiz = EnhancedGITWiz(self.project_root)
                logger.info("✅ Enhanced GitWiz initialized")

            if LINT_MANAGER_AVAILABLE:
                self.lint_manager = LintCleanupManager(self.project_root)
                logger.info("✅ Lint Cleanup Manager initialized")

            if ORCHESTRATOR_AVAILABLE:
                self.orchestrator = GITWizWorkflowOrchestrator(self.project_root)
                logger.info("✅ Workflow Orchestrator initialized")

        except Exception as e:
            logger.error(f"Component initialization error: {e}")

    def quality_check(
        self, auto_fix: bool = False, dry_run: bool = True, output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code quality check.

        Args:
            auto_fix: Whether to automatically fix issues
            dry_run: If True, only analyze without making changes
            output_format: Output format (json, markdown, summary)

        Returns:
            Dictionary containing quality check results
        """
        logger.info("🔍 Starting comprehensive quality check...")
        start_time = datetime.utcnow()

        results = {
            "command": "quality-check",
            "timestamp": start_time.isoformat(),
            "auto_fix": auto_fix,
            "dry_run": dry_run,
            "components_used": [],
            "results": {},
            "summary": {},
            "recommendations": [],
        }

        # Use Enhanced GitWiz if available
        if self.enhanced_gitwiz and hasattr(
            self.enhanced_gitwiz, "comprehensive_code_quality_check"
        ):
            try:
                enhanced_results = (
                    self.enhanced_gitwiz.comprehensive_code_quality_check(
                        auto_fix=auto_fix, dry_run=dry_run
                    )
                )
                results["results"]["enhanced_gitwiz"] = enhanced_results
                results["components_used"].append("enhanced_gitwiz")
                logger.info("✅ Enhanced GitWiz quality check completed")
            except Exception as e:
                logger.error(f"Enhanced GitWiz quality check failed: {e}")
                results["results"]["enhanced_gitwiz"] = {"error": str(e)}

        # Use Lint Manager directly if Enhanced GitWiz not available
        elif self.lint_manager:
            try:
                # Run comprehensive scan
                scan_results = self.lint_manager.comprehensive_lint_scan()
                results["results"]["lint_scan"] = scan_results

                # Run automated fixes if requested
                if auto_fix:
                    fix_results = self.lint_manager.automated_fix_workflow(
                        dry_run=dry_run
                    )
                    results["results"]["automated_fixes"] = fix_results

                results["components_used"].append("lint_manager")
                logger.info("✅ Direct lint manager quality check completed")
            except Exception as e:
                logger.error(f"Lint manager quality check failed: {e}")
                results["results"]["lint_manager"] = {"error": str(e)}

        # Generate summary
        results["summary"] = self._generate_quality_summary(results["results"])
        results["recommendations"] = self._generate_quality_recommendations(
            results["results"]
        )

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        results["execution_time"] = execution_time

        logger.info(f"✅ Quality check completed in {execution_time:.2f}s")

        # Format output
        if output_format == "markdown":
            return self._format_markdown_output(results)
        elif output_format == "summary":
            return self._format_summary_output(results)
        else:
            return results

    def maintenance_workflow(
        self, aggressive: bool = False, dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Execute comprehensive maintenance workflow.

        Args:
            aggressive: Whether to apply aggressive optimizations
            dry_run: If True, only analyze without making changes

        Returns:
            Dictionary containing maintenance results
        """
        logger.info("🔧 Starting maintenance workflow...")
        start_time = datetime.utcnow()

        results = {
            "command": "maintenance",
            "timestamp": start_time.isoformat(),
            "aggressive": aggressive,
            "dry_run": dry_run,
            "components_used": [],
            "stages": {},
            "summary": {},
        }

        # Use Enhanced GitWiz maintenance if available
        if self.enhanced_gitwiz and hasattr(
            self.enhanced_gitwiz, "intelligent_maintenance_workflow"
        ):
            try:
                maintenance_results = (
                    self.enhanced_gitwiz.intelligent_maintenance_workflow(
                        aggressive=aggressive
                    )
                )
                results["stages"]["enhanced_maintenance"] = maintenance_results
                results["components_used"].append("enhanced_gitwiz")
                logger.info("✅ Enhanced GitWiz maintenance completed")
            except Exception as e:
                logger.error(f"Enhanced GitWiz maintenance failed: {e}")
                results["stages"]["enhanced_maintenance"] = {"error": str(e)}

        # Use Workflow Orchestrator if available
        elif self.orchestrator:
            try:
                # Use the enhanced quality workflow
                if hasattr(self.orchestrator, "execute_enhanced_quality_workflow"):
                    orchestrator_results = (
                        self.orchestrator.execute_enhanced_quality_workflow(
                            aggressive=aggressive, dry_run=dry_run
                        )
                    )
                else:
                    # Fallback to full optimization workflow
                    orchestrator_results = (
                        self.orchestrator.execute_full_optimization_workflow(
                            dry_run=dry_run
                        )
                    )

                results["stages"]["orchestrator"] = orchestrator_results
                results["components_used"].append("orchestrator")
                logger.info("✅ Workflow orchestrator maintenance completed")
            except Exception as e:
                logger.error(f"Workflow orchestrator maintenance failed: {e}")
                results["stages"]["orchestrator"] = {"error": str(e)}

        # Fallback to lint manager maintenance
        elif self.lint_manager:
            try:
                lint_results = self.lint_manager.automated_fix_workflow(dry_run=dry_run)
                results["stages"]["lint_maintenance"] = lint_results
                results["components_used"].append("lint_manager")
                logger.info("✅ Lint manager maintenance completed")
            except Exception as e:
                logger.error(f"Lint manager maintenance failed: {e}")
                results["stages"]["lint_maintenance"] = {"error": str(e)}

        # Generate summary
        results["summary"] = self._generate_maintenance_summary(results["stages"])

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        results["execution_time"] = execution_time

        logger.info(f"✅ Maintenance workflow completed in {execution_time:.2f}s")

        return results

    def lint_scan(
        self, detailed: bool = False, target_paths: list = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive lint scanning.

        Args:
            detailed: Whether to include detailed analysis
            target_paths: Specific paths to scan

        Returns:
            Dictionary containing scan results
        """
        logger.info("🔍 Starting lint scan...")
        start_time = datetime.utcnow()

        results = {
            "command": "lint-scan",
            "timestamp": start_time.isoformat(),
            "detailed": detailed,
            "target_paths": target_paths or [str(self.project_root)],
            "scan_results": {},
            "summary": {},
        }

        if self.lint_manager:
            try:
                scan_results = self.lint_manager.comprehensive_lint_scan(target_paths)
                results["scan_results"] = scan_results

                if detailed:
                    # Add detailed analysis
                    results["detailed_analysis"] = {
                        "issue_breakdown": self._analyze_issues_detailed(scan_results),
                        "tool_comparison": self._compare_tool_results(scan_results),
                        "priority_analysis": self._analyze_issue_priorities(
                            scan_results
                        ),
                    }

                logger.info("✅ Lint scan completed")
            except Exception as e:
                logger.error(f"Lint scan failed: {e}")
                results["scan_results"] = {"error": str(e)}
        else:
            results["scan_results"] = {"error": "Lint manager not available"}

        # Generate summary
        results["summary"] = self._generate_scan_summary(results["scan_results"])

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        results["execution_time"] = execution_time

        logger.info(f"✅ Lint scan completed in {execution_time:.2f}s")

        return results

    def workflow_execution(
        self,
        workflow_type: str = "enhanced",
        aggressive: bool = False,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute specific workflow type.

        Args:
            workflow_type: Type of workflow (enhanced, standard, optimization)
            aggressive: Whether to apply aggressive settings
            dry_run: If True, only analyze without making changes

        Returns:
            Dictionary containing workflow results
        """
        logger.info(f"🚀 Starting {workflow_type} workflow...")
        start_time = datetime.utcnow()

        results = {
            "command": "workflow",
            "timestamp": start_time.isoformat(),
            "workflow_type": workflow_type,
            "aggressive": aggressive,
            "dry_run": dry_run,
            "workflow_results": {},
            "summary": {},
        }

        if workflow_type == "enhanced" and self.orchestrator:
            try:
                if hasattr(self.orchestrator, "execute_enhanced_quality_workflow"):
                    workflow_results = (
                        self.orchestrator.execute_enhanced_quality_workflow(
                            aggressive=aggressive, dry_run=dry_run
                        )
                    )
                else:
                    workflow_results = (
                        self.orchestrator.execute_full_optimization_workflow(
                            dry_run=dry_run
                        )
                    )
                results["workflow_results"] = workflow_results
                logger.info("✅ Enhanced workflow completed")
            except Exception as e:
                logger.error(f"Enhanced workflow failed: {e}")
                results["workflow_results"] = {"error": str(e)}

        elif workflow_type == "optimization" and self.enhanced_gitwiz:
            try:
                optimization_results = (
                    self.enhanced_gitwiz.intelligent_maintenance_workflow(
                        aggressive=aggressive
                    )
                )
                results["workflow_results"] = optimization_results
                logger.info("✅ Optimization workflow completed")
            except Exception as e:
                logger.error(f"Optimization workflow failed: {e}")
                results["workflow_results"] = {"error": str(e)}

        else:
            # Standard workflow fallback
            if self.lint_manager:
                try:
                    standard_results = self.lint_manager.automated_fix_workflow(
                        dry_run=dry_run
                    )
                    results["workflow_results"] = standard_results
                    logger.info("✅ Standard workflow completed")
                except Exception as e:
                    logger.error(f"Standard workflow failed: {e}")
                    results["workflow_results"] = {"error": str(e)}
            else:
                results["workflow_results"] = {
                    "error": "No workflow components available"
                }

        # Generate summary
        results["summary"] = self._generate_workflow_summary(
            results["workflow_results"]
        )

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        results["execution_time"] = execution_time

        logger.info(f"✅ {workflow_type} workflow completed in {execution_time:.2f}s")

        return results

    def status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report."""
        logger.info("📊 Generating status report...")

        report = {
            "command": "status",
            "timestamp": datetime.utcnow().isoformat(),
            "project_root": str(self.project_root),
            "components": {},
            "capabilities": {},
            "system_info": {},
        }

        # Component availability
        report["components"]["enhanced_gitwiz"] = ENHANCED_AVAILABLE
        report["components"]["lint_manager"] = LINT_MANAGER_AVAILABLE
        report["components"]["orchestrator"] = ORCHESTRATOR_AVAILABLE

        # Capability assessment
        if self.lint_manager:
            try:
                tool_availability = self.lint_manager.available_tools
                report["capabilities"]["lint_tools"] = tool_availability
            except Exception as e:
                report["capabilities"]["lint_tools"] = {"error": str(e)}

        # System info
        report["system_info"]["python_version"] = sys.version
        report["system_info"]["project_structure"] = self._analyze_project_structure()

        logger.info("✅ Status report generated")

        return report

    def _generate_quality_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for quality check results."""
        summary = {
            "total_issues": 0,
            "auto_fixable": 0,
            "quality_score": 0,
            "tools_used": [],
        }

        # Extract from Enhanced GitWiz results
        if "enhanced_gitwiz" in results:
            enhanced_data = results["enhanced_gitwiz"]
            if "scan_results" in enhanced_data:
                scan_summary = enhanced_data["scan_results"].get("summary", {})
                summary["total_issues"] = scan_summary.get("total_issues", 0)
                summary["auto_fixable"] = scan_summary.get("auto_fixable", 0)

            summary["quality_score"] = enhanced_data.get("quality_score", 0)

        # Extract from direct lint manager results
        elif "lint_scan" in results:
            scan_data = results["lint_scan"]
            scan_summary = scan_data.get("summary", {})
            summary["total_issues"] = scan_summary.get("total_issues", 0)
            summary["auto_fixable"] = scan_summary.get("auto_fixable", 0)

        return summary

    def _generate_quality_recommendations(self, results: Dict[str, Any]) -> list:
        """Generate recommendations based on quality check results."""
        recommendations = []

        # Extract issue counts
        total_issues = 0
        auto_fixable = 0

        for component_results in results.values():
            if isinstance(component_results, dict):
                if "scan_results" in component_results:
                    summary = component_results["scan_results"].get("summary", {})
                    total_issues += summary.get("total_issues", 0)
                    auto_fixable += summary.get("auto_fixable", 0)

        # Generate recommendations based on issue counts
        if total_issues == 0:
            recommendations.append("✅ No issues detected - code quality is excellent")
        elif total_issues < 10:
            recommendations.append("🟢 Low issue count - minor cleanup recommended")
        elif total_issues < 50:
            recommendations.append("🟡 Moderate issues - consider automated fixing")
        else:
            recommendations.append("🔴 High issue count - immediate attention needed")

        if auto_fixable > 20:
            recommendations.append(
                f"🔧 {auto_fixable} auto-fixable issues - run with --auto-fix"
            )

        if not recommendations:
            recommendations.append("ℹ️ Analysis complete - review detailed results")

        return recommendations

    def _generate_maintenance_summary(self, stages: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for maintenance workflow results."""
        summary = {
            "stages_completed": 0,
            "total_stages": len(stages),
            "success_rate": 0,
            "total_fixes": 0,
        }

        successful_stages = 0
        total_fixes = 0

        for stage_name, stage_data in stages.items():
            if isinstance(stage_data, dict) and "error" not in stage_data:
                successful_stages += 1

                # Extract fix counts
                if "total_fixes" in stage_data:
                    total_fixes += stage_data["total_fixes"]
                elif "fix_results" in stage_data:
                    fix_data = stage_data["fix_results"]
                    if isinstance(fix_data, dict) and "total_fixes" in fix_data:
                        total_fixes += fix_data["total_fixes"]

        summary["stages_completed"] = successful_stages
        summary["success_rate"] = (
            (successful_stages / len(stages) * 100) if stages else 0
        )
        summary["total_fixes"] = total_fixes

        return summary

    def _generate_scan_summary(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for lint scan results."""
        summary = {"issues_by_tool": {}, "severity_breakdown": {}, "file_count": 0}

        if "summary" in scan_results:
            scan_summary = scan_results["summary"]
            summary["issues_by_tool"] = scan_summary.get("tool_breakdown", {})
            summary["severity_breakdown"] = scan_summary.get("severity_breakdown", {})

        return summary

    def _generate_workflow_summary(
        self, workflow_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary for workflow execution results."""
        summary = {
            "overall_success": False,
            "execution_time": 0,
            "improvements_made": [],
        }

        if isinstance(workflow_results, dict):
            summary["overall_success"] = workflow_results.get("overall_success", False)
            summary["execution_time"] = workflow_results.get("execution_time", 0)

            # Extract improvements
            if "stages" in workflow_results:
                for stage_name, stage_data in workflow_results["stages"].items():
                    if isinstance(stage_data, dict) and "error" not in stage_data:
                        summary["improvements_made"].append(stage_name)

        return summary

    def _analyze_issues_detailed(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Provide detailed analysis of discovered issues."""
        # This would implement detailed issue analysis
        return {"analysis": "detailed", "placeholder": True}

    def _compare_tool_results(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare results across different tools."""
        # This would implement tool comparison
        return {"comparison": "tool_results", "placeholder": True}

    def _analyze_issue_priorities(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze issue priorities and recommendations."""
        # This would implement priority analysis
        return {"priority_analysis": "placeholder", "placeholder": True}

    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze and report on project structure."""
        structure = {
            "python_files": len(list(self.project_root.rglob("*.py"))),
            "markdown_files": len(list(self.project_root.rglob("*.md"))),
            "javascript_files": len(list(self.project_root.rglob("*.js")))
            + len(list(self.project_root.rglob("*.ts"))),
            "total_files": len(list(self.project_root.rglob("*"))),
            "directories": len([p for p in self.project_root.rglob("*") if p.is_dir()]),
        }
        return structure

    def _format_markdown_output(self, results: Dict[str, Any]) -> str:
        """Format results as markdown."""
        lines = [
            "# GitWiz Quality Check Report",
            f"Generated: {results['timestamp']}",
            "",
            "## Summary",
            f"- Command: {results['command']}",
            f"- Execution Time: {results.get('execution_time', 0):.2f}s",
            f"- Components Used: {', '.join(results.get('components_used', []))}",
            "",
        ]

        if "recommendations" in results and results["recommendations"]:
            lines.extend(["## Recommendations", ""])
            for rec in results["recommendations"]:
                lines.append(f"- {rec}")

        return "\n".join(lines)

    def _format_summary_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results as concise summary."""
        return {
            "command": results["command"],
            "timestamp": results["timestamp"],
            "execution_time": results.get("execution_time", 0),
            "summary": results.get("summary", {}),
            "recommendations": results.get("recommendations", [])[:3],  # Top 3
        }

def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="GitWiz Integrated Command Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s quality-check --auto-fix --output markdown
  %(prog)s maintenance --aggressive --no-dry-run
  %(prog)s lint-scan --detailed --target scripts/
  %(prog)s workflow --type enhanced --aggressive
  %(prog)s status
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Quality check command
    quality_parser = subparsers.add_parser(
        "quality-check", help="Perform comprehensive quality check"
    )
    quality_parser.add_argument(
        "--auto-fix", action="store_true", help="Automatically fix issues"
    )
    quality_parser.add_argument(
        "--no-dry-run", action="store_true", help="Apply changes (not dry run)"
    )
    quality_parser.add_argument(
        "--output",
        choices=["json", "markdown", "summary"],
        default="json",
        help="Output format",
    )

    # Maintenance command
    maintenance_parser = subparsers.add_parser(
        "maintenance", help="Execute maintenance workflow"
    )
    maintenance_parser.add_argument(
        "--aggressive", action="store_true", help="Apply aggressive optimizations"
    )
    maintenance_parser.add_argument(
        "--no-dry-run", action="store_true", help="Apply changes (not dry run)"
    )

    # Lint scan command
    lint_parser = subparsers.add_parser(
        "lint-scan", help="Perform comprehensive lint scan"
    )
    lint_parser.add_argument(
        "--detailed", action="store_true", help="Include detailed analysis"
    )
    lint_parser.add_argument("--target", action="append", help="Target paths to scan")

    # Workflow command
    workflow_parser = subparsers.add_parser(
        "workflow", help="Execute specific workflow"
    )
    workflow_parser.add_argument(
        "--type",
        choices=["enhanced", "standard", "optimization"],
        default="enhanced",
        help="Workflow type",
    )
    workflow_parser.add_argument(
        "--aggressive", action="store_true", help="Apply aggressive settings"
    )
    workflow_parser.add_argument(
        "--no-dry-run", action="store_true", help="Apply changes (not dry run)"
    )

    # Status command
    subparsers.add_parser("status", help="Generate status report")

    # Global options
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output")

    args = parser.parse_args()

    # Configure logging based on verbosity
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize command interface
    try:
        cmd_interface = GitWizIntegratedCommand(args.project_root)
    except Exception as e:
        logger.error(f"Failed to initialize GitWiz: {e}")
        sys.exit(1)

    # Execute command
    try:
        if args.command == "quality-check":
            results = cmd_interface.quality_check(
                auto_fix=args.auto_fix,
                dry_run=not args.no_dry_run,
                output_format=args.output,
            )

        elif args.command == "maintenance":
            results = cmd_interface.maintenance_workflow(
                aggressive=args.aggressive, dry_run=not args.no_dry_run
            )

        elif args.command == "lint-scan":
            results = cmd_interface.lint_scan(
                detailed=args.detailed, target_paths=args.target
            )

        elif args.command == "workflow":
            results = cmd_interface.workflow_execution(
                workflow_type=args.type,
                aggressive=args.aggressive,
                dry_run=not args.no_dry_run,
            )

        elif args.command == "status":
            results = cmd_interface.status_report()

        else:
            parser.print_help()
            sys.exit(1)

        # Output results
        if args.command == "quality-check" and args.output == "markdown":
            print(results)  # Already formatted as markdown
        elif args.command == "quality-check" and args.output == "summary":
            print(json.dumps(results, indent=2))
        else:
            print(json.dumps(results, indent=2, default=str))

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        if args.verbose:

            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
