#!/usr/bin/env python3
"""
Integration test for automation fixes
Validates that all critical fixes are working correctly
"""

import subprocess
import sys
import os
import json
from pathlib import Path
import yaml

# Always run commands from the repository root, independent of current CWD
REPO_ROOT = Path(__file__).resolve().parent.parent


def run_command(cmd, timeout=30):
    """Run a command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO_ROOT,
            env={**os.environ, 'CI': 'true'}
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def load_yaml_file(path: Path):
    """Load YAML content from disk."""
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def normalize_workflow_definition(workflow):
    """Normalize GitHub workflow YAML so the `on` key survives YAML 1.1 parsing."""
    workflow = dict(workflow or {})
    if True in workflow and "on" not in workflow:
        workflow["on"] = workflow.pop(True)
    return workflow


def load_aurora_workflow():
    """Load the Aurora Agent runner workflow."""
    workflow_path = REPO_ROOT / ".github" / "workflows" / "aurora_agent_runner.yml"
    workflow = normalize_workflow_definition(load_yaml_file(workflow_path))
    return workflow_path, workflow


def test_aurora_agent_ci_mode():
    """Test Aurora Agent runs correctly in CI mode"""
    print("🧪 Testing Aurora Agent in CI mode...")

    returncode, stdout, stderr = run_command(
        "python .github/agents/aurora_agent_final.py",
        timeout=10
    )

    assert returncode == 0, f"Exit code {returncode}, stderr: {stderr}"
    assert "Single-run (CI)" in stdout, "Not running in single-run mode"
    assert "shutting down" in stdout, "Agent did not shut down properly"

    print("  ✅ PASSED: Agent runs and exits cleanly in CI mode")


def test_aurora_agent_token_handling():
    """Test Aurora Agent handles missing token gracefully"""
    print("🧪 Testing Aurora Agent token handling...")

    # Ensure no token is set
    env = {**os.environ, 'CI': 'true'}
    if 'GITHUB_TOKEN' in env:
        del env['GITHUB_TOKEN']

    result = subprocess.run(
        "python .github/agents/aurora_agent_final.py",
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO_ROOT,
        env=env
    )

    assert "Warning: GITHUB_TOKEN not set" in result.stdout, "Token warning not shown"
    assert result.returncode == 0, f"Exit code {result.returncode} (should be 0)"

    print("  ✅ PASSED: Agent handles missing token gracefully")


def test_makefile_no_warnings():
    """Test Makefile runs without warnings"""
    print("🧪 Testing Makefile...")

    returncode, stdout, stderr = run_command("make help")

    assert returncode == 0, f"Exit code {returncode}"
    assert "warning: overriding recipe" not in stderr, f"Duplicate target warnings detected: {stderr}"
    assert "Aurora CloudBank Symbolic System" in stdout, "Help output not correct"

    print("  ✅ PASSED: Makefile runs without warnings")


def test_audit_tool():
    """Test automation audit tool"""
    print("🧪 Testing automation audit tool...")

    returncode, stdout, stderr = run_command(
        "python scripts/automation_audit.py",
        timeout=60
    )
    report_path = REPO_ROOT / "automation_audit_report.json"

    assert returncode in (0, 1), f"Unexpected exit code {returncode}"  # 0 = pass, 1 = warnings only
    assert "Critical Issues: 0" in stdout, f"Critical issues detected: {stdout}"
    assert report_path.exists(), "Automation audit report was not created"

    with open(report_path, "r", encoding="utf-8") as handle:
        report = json.load(handle)

    aurora_warnings = [warning for warning in report.get("warnings", []) if "aurora_agent_runner.yml" in warning]
    assert not aurora_warnings, f"Aurora workflow warnings detected: {aurora_warnings}"

    if "Overall Status: ✅ PASS" not in stdout:
        print("  ⚠️ WARNING: Status not PASS (may have warnings)")

    print("  ✅ PASSED: Audit tool runs and reports no critical issues")


def test_log_files_created():
    """Test that log files are created correctly"""
    print("🧪 Testing log file creation...")

    log_file = REPO_ROOT / "logs" / "aurora_agent.log"

    # Run agent to create log
    run_command("python .github/agents/aurora_agent_final.py", timeout=10)

    assert log_file.exists(), "Log file not created"

    with open(log_file, 'r') as f:
        content = f.read()

    assert "Aurora Agent" in content, "Log content invalid"

    print("  ✅ PASSED: Log files created correctly")


def test_aurora_workflow_is_scheduled_and_enabled():
    """Test Aurora Agent workflow is runnable on schedule and by hand."""
    print("🧪 Testing Aurora Agent workflow triggers...")

    workflow_path, workflow = load_aurora_workflow()
    triggers = workflow.get("on", {})
    jobs = workflow.get("jobs", {})

    assert workflow_path.exists(), "Aurora workflow file missing"
    assert "schedule" in triggers, "Workflow is missing a schedule trigger"
    assert triggers["schedule"], "Workflow schedule trigger is empty"
    assert "workflow_dispatch" in triggers, "Workflow is missing manual dispatch support"
    assert jobs, "Workflow does not define any jobs"
    assert all(job.get("if") not in (False, "false") for job in jobs.values()), "Workflow jobs are disabled"

    print("  ✅ PASSED: Workflow is scheduled, manually triggerable, and enabled")


def test_aurora_workflow_permissions_and_artifacts():
    """Test Aurora Agent workflow keeps the required permissions and log archival."""
    print("🧪 Testing Aurora Agent workflow permissions and artifacts...")

    _, workflow = load_aurora_workflow()
    permissions = workflow.get("permissions", {})
    aurora_job = workflow.get("jobs", {}).get("aurora-agent", {})
    steps = aurora_job.get("steps", [])
    uses_values = [step.get("uses", "") for step in steps if isinstance(step, dict)]

    for scope in ("contents", "issues", "pull-requests"):
        assert permissions.get(scope) == "write", f"Workflow permission {scope} is not write"

    assert any(uses.startswith("actions/checkout@") for uses in uses_values), "Workflow does not check out the repo"
    assert any(uses.startswith("actions/setup-python@") for uses in uses_values), "Workflow does not set up Python"
    assert any(
        uses.startswith("actions/upload-artifact@") for uses in uses_values
    ), "Workflow does not archive Aurora logs"

    print("  ✅ PASSED: Workflow permissions and log archival are configured")


def main():
    """Run all tests (for standalone execution)"""
    print("\n" + "="*60)
    print("🌟 Aurora CloudBank - Automation Fixes Validation")
    print("="*60 + "\n")

    # Change to repo root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)

    tests = [
        test_aurora_agent_ci_mode,
        test_aurora_agent_token_handling,
        test_makefile_no_warnings,
        test_audit_tool,
        test_log_files_created,
        test_aurora_workflow_is_scheduled_and_enabled,
        test_aurora_workflow_permissions_and_artifacts,
    ]

    failed_count = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"  ❌ ASSERTION FAILED: {e}")
            failed_count += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed_count += 1
        print()

    # Summary
    print("="*60)
    print("📊 Test Summary")
    print("="*60)
    passed = len(tests) - failed_count
    total = len(tests)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed_count}/{total}")

    if failed_count == 0:
        print("\n✅ All tests PASSED - Automation fixes validated!")
        return 0
    else:
        print("\n❌ Some tests FAILED - Review output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
