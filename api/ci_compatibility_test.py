#!/usr/bin/env python3
"""
Quick CI compatibility test to verify basic Python functionality
"""

import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


def test_basic_imports():
    """Test that critical modules can be imported without syntax errors"""
    critical_files = [
        "aurora_api.py",
        "aurora_api_server.py",
        "setup_aurora_branches.py",
        "security_verification.py",
        "aurora_realworld_integration.py",
        "aurora_gui_cloudhub_fastapi.py",
    ]

    passed = 0
    failed = 0

    print("🧪 Testing critical file imports...")

    for file in critical_files:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", file],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info("%s", file)
                passed += 1
            else:
                logger.error("%s: %s", file, result.stderr.strip())
                failed += 1
        except subprocess.TimeoutExpired:
            print(f"⏰ {file}: Timeout")
            failed += 1
        except Exception as exc:
            print(f"💥 {file}: {exc}")
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_basic_functionality():
    """Test basic Python and system functionality"""
    print("🔧 Testing basic functionality...")

    try:
        # Test basic Python operations
        result = 2 + 2
        assert result == 4, "Basic math failed"
        logger.info("Basic math works")

        # Test subprocess
        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
        assert result.returncode == 0, "Python version check failed"
        logger.info("Python subprocess works")

        return True
    except Exception as exc:
        logger.error("Basic functionality test failed: %s", exc)
        return False


def main():
    """Run CI compatibility tests"""
    print("🚀 Aurora CloudBank CI Compatibility Test")
    print("=" * 50)

    basic_test = test_basic_functionality()
    import_test = test_basic_imports()

    if basic_test and import_test:
        print("\n🎉 All tests passed! CI should work.")
        return 0
    else:
        print("\n❌ Some tests failed. Check CI configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())