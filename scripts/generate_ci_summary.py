#!/usr/bin/env python3
"""
CI Summary Report Generator
==========================

Generates comprehensive CI/CD summary reports for GitWiz quality gates.
Combines results from multiple tools and creates actionable insights.

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

def load_json_report(file_path: str) -> Dict[str, Any]:
    """Load JSON report if it exists."""
    if Path(file_path).exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load {file_path}: {e}")
    return {}

def generate_ci_summary():
    """Generate comprehensive CI summary report."""

    # Load available reports
    quality_report = load_json_report("quality_report.json")
    maintenance_report = load_json_report("maintenance_report.json")
    bandit_report = load_json_report("bandit_report.json")

    # Get current timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Start building the summary
    summary_lines = [
        "# 🔍 GitWiz Quality Gates Summary",
        f"**Generated:** {timestamp}",
        "",
        "## 📊 Quality Analysis Results",
        "",
    ]

    # Quality Report Section
    if quality_report:
        total_issues = quality_report.get("summary", {}).get("total_issues", 0)
        auto_fixable = quality_report.get("summary", {}).get("auto_fixable", 0)
        quality_score = quality_report.get("summary", {}).get("quality_score", 0)

        if total_issues == 0:
            summary_lines.extend(
                [
                    "### ✅ Code Quality: EXCELLENT",
                    "- No issues detected",
                    "- All quality checks passed",
                    "",
                ]
            )
        else:
            summary_lines.extend(
                [
                    f"### ⚠️ Code Quality: {total_issues} issues found",
                    f"- **Total Issues:** {total_issues}",
                    f"- **Auto-fixable:** {auto_fixable}",
                    f"- **Quality Score:** {quality_score}/100",
                    "",
                ]
            )

            # Add issue breakdown if available
            severity_breakdown = quality_report.get("summary", {}).get(
                "severity_breakdown", {}
            )
            if severity_breakdown:
                summary_lines.append("**Issue Breakdown:**")
                for severity, count in severity_breakdown.items():
                    emoji = (
                        "🔴"
                        if severity == "error"
                        else "🟡" if severity == "warning" else "🔵"
                    )
                    summary_lines.append(f"- {emoji} {severity.title()}: {count}")
                summary_lines.append("")

    # Security Report Section
    if bandit_report:
        security_issues = len(bandit_report.get("results", []))
        if security_issues == 0:
            summary_lines.extend(
                ["### 🛡️ Security: SECURE", "- No security vulnerabilities detected", ""]
            )
        else:
            summary_lines.extend(
                [
                    f"### 🚨 Security: {security_issues} issues found",
                    f"- **Vulnerabilities detected:** {security_issues}",
                    "- Review security scan results for details",
                    "",
                ]
            )

    # Maintenance Report Section
    if maintenance_report:
        total_fixes = maintenance_report.get("total_fixes", 0)
        if total_fixes > 0:
            summary_lines.extend(
                [
                    f"### 🔧 Maintenance: {total_fixes} fixes applied",
                    f"- **Automated fixes:** {total_fixes}",
                    "- Code quality improvements applied",
                    "",
                ]
            )

    # Recommendations Section
    summary_lines.extend(["## 💡 Recommendations", ""])

    recommendations = []

    if quality_report:
        if quality_report.get("summary", {}).get("total_issues", 0) > 0:
            recommendations.append(
                "- Run `python scripts/gitwiz_integrated_command.py quality-check --auto-fix` to resolve auto-fixable issues"
            )

        rec_list = quality_report.get("recommendations", [])
        recommendations.extend([f"- {rec}" for rec in rec_list])

    if bandit_report and len(bandit_report.get("results", [])) > 0:
        recommendations.append("- Review and address security vulnerabilities")

    if not recommendations:
        recommendations.append(
            "- ✅ No immediate actions required - code quality is excellent!"
        )

    summary_lines.extend(recommendations)

    # Tool Status Section
    summary_lines.extend(["", "## 🛠️ Tools Status", ""])

    if quality_report and "capabilities" in quality_report:
        lint_tools = quality_report["capabilities"].get("lint_tools", {})
        available_tools = [tool for tool, available in lint_tools.items() if available]
        summary_lines.extend(
            [
                f"**Available Tools:** {', '.join(available_tools)}",
                f"**Total Tools:** {len(available_tools)}/8",
                "",
            ]
        )

    # Performance Metrics
    if quality_report:
        execution_time = quality_report.get("execution_time", 0)
        summary_lines.extend(
            [
                "## ⚡ Performance Metrics",
                f"- **Analysis Time:** {execution_time:.2f} seconds",
                "",
            ]
        )

    # Footer
    summary_lines.extend(
        [
            "---",
            "**GitWiz Quality Gates** - Automated code quality management",
            "Generated by Aurora/ORION Core automation systems",
        ]
    )

    # Write summary to file
    summary_content = "\n".join(summary_lines)

    with open("ci_summary.md", "w", encoding="utf-8") as f:
        f.write(summary_content)

    # Also output to console
    print("=" * 60)
    print("CI SUMMARY REPORT GENERATED")
    print("=" * 60)
    print(summary_content)

    # Create JSON version for programmatic access
    json_summary = {
        "timestamp": timestamp,
        "quality_issues": (
            quality_report.get("summary", {}).get("total_issues", 0)
            if quality_report
            else 0
        ),
        "security_issues": (
            len(bandit_report.get("results", [])) if bandit_report else 0
        ),
        "maintenance_fixes": (
            maintenance_report.get("total_fixes", 0) if maintenance_report else 0
        ),
        "overall_status": (
            "PASS"
            if (
                (
                    quality_report.get("summary", {}).get("total_issues", 0) == 0
                    if quality_report
                    else True
                )
                and (
                    len(bandit_report.get("results", [])) == 0
                    if bandit_report
                    else True
                )
            )
            else "ATTENTION_REQUIRED"
        ),
        "recommendations": recommendations,
    }

    with open("ci_summary.json", "w", encoding="utf-8") as f:
        json.dump(json_summary, f, indent=2)

    print(f"\nSummary files generated:")
    print(f"- ci_summary.md (Markdown format)")
    print(f"- ci_summary.json (JSON format)")

    return json_summary["overall_status"] == "PASS"

if __name__ == "__main__":
    success = generate_ci_summary()
    sys.exit(0 if success else 1)
