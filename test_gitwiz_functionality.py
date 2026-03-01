#!/usr/bin/env python3
"""
Quick test script for GITWiz Enhanced functionality
"""

import subprocess
import sys
from pathlib import Path


def test_command(cmd, description):
    """Test a command and report results."""
    print(f"\n🧪 Testing: {description}")
    print(f"Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            if result.stdout:
                print(f"Output: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}")
        else:
            print(f"❌ FAILED: {description}")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}{'...' if len(result.stderr) > 200 else ''}")
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {description}")
    except Exception as e:
        print(f"❌ ERROR: {description} - {str(e)}")


def main():
    print("🚀 GITWiz Enhanced - Functionality Test Suite")
    print("=" * 60)

    # Test 1: Original GITWiz
    test_command([sys.executable, "scripts/gitwiz.py", "status"], "Original GITWiz Status")

    # Test 2: Enhanced GITWiz (if available)
    if Path("scripts/gitwiz_enhanced.py").exists():
        test_command(
            [
                sys.executable,
                "-c",
                "from scripts.gitwiz_enhanced import EnhancedGITWiz; print('✅ Enhanced GITWiz import successful')",
            ],
            "Enhanced GITWiz Import",
        )

    # Test 3: Dependency Updater
    if Path("scripts/gitwiz_dependency_updater.py").exists():
        test_command(
            [sys.executable, "scripts/gitwiz_dependency_updater.py", "--help"],
            "Dependency Updater Help",
        )
        test_command(
            [sys.executable, "scripts/gitwiz_dependency_updater.py", "--scan"],
            "Dependency Scanner",
        )

    # Test 4: Workflow Orchestrator
    if Path("scripts/gitwiz_workflow_orchestrator.py").exists():
        test_command(
            [sys.executable, "scripts/gitwiz_workflow_orchestrator.py", "--help"],
            "Workflow Orchestrator Help",
        )

    # Test 5: Demo Script
    if Path("gitwiz_enhanced_demo.py").exists():
        test_command([sys.executable, "gitwiz_enhanced_demo.py"], "Enhanced Demo Analysis")

    # Test 6: HDE++ Integration
    if Path("hdeplusplus.py").exists():
        test_command(
            [
                sys.executable,
                "hdeplusplus.py",
                "recommend",
                "--context",
                '{"weights": {"logic":3}}',
            ],
            "HDE++ Recommendation",
        )

    print("\n" + "=" * 60)
    print("🎯 Test Suite Complete!")
    print("If all tests show ✅ SUCCESS, GITWiz Enhanced is fully operational!")


if __name__ == "__main__":
    main()
