#!/usr/bin/env python3
"""
Integration test for automation fixes
Validates that all critical fixes are working correctly
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, timeout=30):
    """Run a command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
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
    
    if returncode != 0:
        print(f"  ❌ FAILED: Exit code {returncode}")
        print(f"  stderr: {stderr}")
        return False
    
    if "Single-run (CI)" not in stdout:
        print("  ❌ FAILED: Not running in single-run mode")
        return False
    
    if "shutting down" not in stdout:
        print("  ❌ FAILED: Agent did not shut down properly")
        return False
    
    print("  ✅ PASSED: Agent runs and exits cleanly in CI mode")
    return True


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
        env=env
    )
    
    if "Warning: GITHUB_TOKEN not set" not in result.stdout:
        print("  ❌ FAILED: Token warning not shown")
        return False
    
    if result.returncode != 0:
        print(f"  ❌ FAILED: Exit code {result.returncode} (should be 0)")
        return False
    
    print("  ✅ PASSED: Agent handles missing token gracefully")
    return True


def test_makefile_no_warnings():
    """Test Makefile runs without warnings"""
    print("🧪 Testing Makefile...")
    
    returncode, stdout, stderr = run_command("make help")
    
    if returncode != 0:
        print(f"  ❌ FAILED: Exit code {returncode}")
        return False
    
    if "warning: overriding recipe" in stderr:
        print("  ❌ FAILED: Duplicate target warnings detected")
        print(f"  stderr: {stderr}")
        return False
    
    if "Aurora CloudBank Symbolic System" not in stdout:
        print("  ❌ FAILED: Help output not correct")
        return False
    
    print("  ✅ PASSED: Makefile runs without warnings")
    return True


def test_audit_tool():
    """Test automation audit tool"""
    print("🧪 Testing automation audit tool...")
    
    returncode, stdout, stderr = run_command(
        "python scripts/automation_audit.py",
        timeout=60
    )
    
    if returncode not in (0, 1):  # 0 = pass, 1 = warnings only
        print(f"  ❌ FAILED: Unexpected exit code {returncode}")
        return False
    
    if "Critical Issues: 0" not in stdout:
        print("  ❌ FAILED: Critical issues detected")
        print(f"  stdout: {stdout}")
        return False
    
    if "Overall Status: ✅ PASS" not in stdout:
        print("  ⚠️ WARNING: Status not PASS (may have warnings)")
    
    print("  ✅ PASSED: Audit tool runs and reports no critical issues")
    return True


def test_log_files_created():
    """Test that log files are created correctly"""
    print("🧪 Testing log file creation...")
    
    log_file = Path("logs/aurora_agent.log")
    
    # Run agent to create log
    run_command("python .github/agents/aurora_agent_final.py", timeout=10)
    
    if not log_file.exists():
        print("  ❌ FAILED: Log file not created")
        return False
    
    with open(log_file, 'r') as f:
        content = f.read()
        
    if "Aurora Agent" not in content:
        print("  ❌ FAILED: Log content invalid")
        return False
    
    print("  ✅ PASSED: Log files created correctly")
    return True


def main():
    """Run all tests"""
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
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append(False)
        print()
    
    # Summary
    print("="*60)
    print("📊 Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n✅ All tests PASSED - Automation fixes validated!")
        return 0
    else:
        print("\n❌ Some tests FAILED - Review output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
