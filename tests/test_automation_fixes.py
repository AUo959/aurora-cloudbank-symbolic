#!/usr/bin/env python3
"""
Integration test for automation fixes
Validates that all critical fixes are working correctly
"""

import subprocess
import sys
import os
from pathlib import Path

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

    assert returncode in (0, 1), f"Unexpected exit code {returncode}"  # 0 = pass, 1 = warnings only
    assert "Critical Issues: 0" in stdout, f"Critical issues detected: {stdout}"

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


def normalize_workflow_definition(workflow):
    """Normalize GitHub workflow YAML so the `on` key survives YAML 1.1 parsing."""
    workflow = dict(workflow or {})
    if True in workflow and "on" not in workflow:
        workflow["on"] = workflow.pop(True)
    return workflow


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
