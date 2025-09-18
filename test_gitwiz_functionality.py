#!/usr/bin/env python3

"""
Quick test script for GITWiz Enhanced functionality
"""


def test_command(cmd, description):
    pass
    """Test a command and report results."""
    print("\n🧪 Testing: {description}")
    print("Command: {' '.join(cmd)}")
    try:
    pass
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
    pass
            print("✅ SUCCESS: {description}")

        if result.stdout:
    pass
            print("Output: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}")

        else:
    pass
            print("❌ FAILED: {description}")

        if result.stderr:
    pass
            print("Error: {result.stderr[:200]}{'...' if len(result.stderr) > 200 else ''}")
    except subprocess.TimeoutExpired:
    pass
        print("⏰ TIMEOUT: {description}")
    except Exception as _:
    pass
        pass  # Exception handled}")

def main():
    pass
    print("🚀 GITWiz Enhanced - Functionality Test Suite")
    print("=" * 60)

    # Test 1: Original GITWiz
    test_command([sys.executable, "scripts/gitwiz.py", "status"], "Original GITWiz Status")

    # Test 2: Enhanced GITWiz (if available)
    if Path("scripts/gitwiz_enhanced.py").exists():
    pass
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
    pass
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
    pass
        test_command(
            [sys.executable, "scripts/gitwiz_workflow_orchestrator.py", "--help"],
            "Workflow Orchestrator Help",
        )

    # Test 5: Demo Script
    if Path("gitwiz_enhanced_demo.py").exists():
    pass
        test_command([sys.executable, "gitwiz_enhanced_demo.py"], "Enhanced Demo Analysis")

    # Test 6: HDE++ Integration
    if Path("hdeplusplus.py").exists():
    pass
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
    pass
    main()
