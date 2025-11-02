#!/usr/bin/env python3
"""
Parse code quality report and output summary.
Used by GitHub Actions workflow to reduce duplication.
Part of Issue #258 implementation.
"""

import json
import sys
from pathlib import Path


def parse_and_display_summary(report_path: str) -> None:
    """
    Parse code quality report and display formatted summary.
    
    Args:
        report_path: Path to the code quality report JSON file
    """
    report_file = Path(report_path)
    
    if not report_file.exists():
        print("⚠️ No code quality report generated")
        return
    
    with open(report_file) as f:
        report = json.load(f)
    
    summary = report.get('analysis_summary', {})
    severity = summary.get('severity_breakdown', {})
    
    passed = summary.get('passed', False)
    total_violations = summary.get('total_violations', 0)
    
    print(f"**Status:** {'✅ Passed' if passed else '❌ Failed'}")
    print(f"**Total Violations:** {total_violations}")
    print()
    print('### Severity Breakdown')
    print(f"- 🔴 Critical: {severity.get('critical', 0)}")
    print(f"- 🟠 High: {severity.get('high', 0)}")
    print(f"- 🟡 Medium: {severity.get('medium', 0)}")
    print(f"- 🟢 Low: {severity.get('low', 0)}")


def check_quality_gate(report_path: str) -> int:
    """
    Check if quality gate passes or fails.
    
    Args:
        report_path: Path to the code quality report JSON file
        
    Returns:
        0 if passed, 1 if failed
    """
    report_file = Path(report_path)
    
    if not report_file.exists():
        print("⚠️ No report to evaluate")
        return 1
    
    with open(report_file) as f:
        report = json.load(f)
    
    passed = report.get('analysis_summary', {}).get('passed', False)
    
    if not passed:
        print('❌ Quality gate FAILED - Critical violations detected')
        return 1
    else:
        print('✅ Quality gate PASSED')
        return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: parse_code_quality_report.py <report_path> [--check-gate]")
        sys.exit(1)
    
    report_path = sys.argv[1]
    check_gate = len(sys.argv) > 2 and sys.argv[2] == '--check-gate'
    
    if check_gate:
        sys.exit(check_quality_gate(report_path))
    else:
        parse_and_display_summary(report_path)
