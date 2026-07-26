#!/usr/bin/env python3
"""
Integration test for automation fixes.

Validates that all critical fixes are working correctly.
"""

import os
import shlex
import subprocess
import sys
from pathlib import Path

# Always run commands from the repository root, independent of current CWD
REPO_ROOT = Path(__file__).resolve().parent.parent

# These legacy integration checks run through shell=True. Quote the active
# interpreter according to the platform shell: shlex.quote emits POSIX single
# quotes, while Windows cmd.exe requires subprocess.list2cmdline semantics.
PYTHON = (
    subprocess.list2cmdline([sys.executable])
    if os.name == "nt"
    else shlex.quote(sys.executable)
)


def run_command(cmd, timeout=30):
    """Run a command and return its exit code, stdout, and stderr."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO_ROOT,
            env={**os.environ, "CI": "true"},
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def test_aurora_agent_ci_mode():
    """Test Aurora Agent runs correctly in CI mode."""
    print("🧪 Testing Aurora Agent in CI mode...")

    returncode, stdout, stderr = run_command(
        f"{PYTHON} .github/agents/aurora_agent_final.py",
        timeout=10,
    )

    assert returncode == 0, f"Exit code {returncode}, stderr: {stderr}"
    assert "Single-run (CI)" in stdout, "Not running in single-run mode"
    assert "shutting down" in stdout, "Agent did not shut down properly"

    print("  ✅ PASSED: Agent runs and exits cleanly in CI mode")


def test_aurora_agent_token_handling():
    """Test Aurora Agent handles missing token gracefully."""
    print("🧪 Testing Aurora Agent token handling...")

    env = {**os.environ, "CI": "true"}
    env.pop("GITHUB_TOKEN", None)

    result = subprocess.run(
        f"{PYTHON} .github/agents/aurora_agent_final.py",
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPO_ROOT,
        env=env,
    )

    assert "Warning: GITHUB_TOKEN not set" in result.stdout, "Token warning not shown"
    assert result.returncode == 0, f"Exit code {result.returncode} (should be 0)"

    print("  ✅ PASSED: Agent handles missing token gracefully")


def test_makefile_no_warnings():
    """Test Makefile runs without warnings."""
    print("🧪 Testing Makefile...")

    returncode, stdout, stderr = run_command("make help")

    assert returncode == 0, f"Exit code {returncode}"
    assert "warning: overriding recipe" not in stderr, f"Duplicate target warnings detected: {stderr}"
    assert "Aurora CloudBank Symbolic System" in stdout, "Help output not correct"

    print("  ✅ PASSED: Makefile runs without warnings")


def test_audit_tool():
    """Test automation audit tool."""
    print("🧪 Testing automation audit tool...")

    returncode, stdout, stderr = run_command(
        f"{PYTHON} scripts/automation_audit.py",
        timeout=60,
    )

    assert returncode in (0, 1), f"Unexpected exit code {returncode}"
    assert "Critical Issues: 0" in stdout, f"Critical issues detected: {stdout}"

    if "Overall Status: ✅ PASS" not in stdout:
        print("  ⚠️ WARNING: Status not PASS (may have warnings)")

    print("  ✅ PASSED: Audit tool runs and reports no critical issues")


def test_log_files_created():
    """Test that log files are created correctly."""
    print("🧪 Testing log file creation...")

    log_file = REPO_ROOT / "logs" / "aurora_agent.log"
    run_command(f"{PYTHON} .github/agents/aurora_agent_final.py", timeout=10)

    assert log_file.exists(), "Log file not created"

    with open(log_file, "r", encoding="utf-8") as handle:
        content = handle.read()

    assert "Aurora Agent" in content, "Log content invalid"

    print("  ✅ PASSED: Log files created correctly")


def normalize_workflow_definition(workflow):
    """Normalize GitHub workflow YAML so the `on` key survives YAML 1.1 parsing."""
    workflow = dict(workflow or {})
    if True in workflow and "on" not in workflow:
        workflow["on"] = workflow.pop(True)
    return workflow


def main():
    """Run all tests for standalone execution."""
    print("\n" + "=" * 60)
    print("🌟 Aurora CloudBank - Automation Fixes Validation")
    print("=" * 60 + "\n")

    os.chdir(REPO_ROOT)

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
        except AssertionError as exc:
            print(f"  ❌ ASSERTION FAILED: {exc}")
            failed_count += 1
        except Exception as exc:
            print(f"  ❌ ERROR: {exc}")
            failed_count += 1
        print()

    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    passed = len(tests) - failed_count
    total = len(tests)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {failed_count}/{total}")

    if failed_count == 0:
        print("\n✅ All tests PASSED - Automation fixes validated!")
        return 0

    print("\n❌ Some tests FAILED - Review output above")
    return 1


if __name__ == "__main__":
    sys.exit(main())
