#!/usr/bin/env python3
"""
Test suite for dependency conflict detector

This can be run standalone (python3 tests/test_dependency_conflict_detector.py)
or via pytest. Designed to work without pytest installed for basic validation.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from dependency_conflict_detector import (
    DependencyConflictDetector,
    DependencyConflict,
    DependencyReport
)


def test_parse_requirements_file():
    """Test requirements file parsing"""
    print("🧪 Testing requirements file parsing...")
    
    detector = DependencyConflictDetector()
    packages = detector.parse_requirements_file(
        Path(__file__).parent.parent / 'requirements-lock.txt'
    )
    
    assert len(packages) > 0, "Should parse at least one package"
    assert 'fastapi' in packages, "Should find fastapi"
    assert 'starlette' in packages, "Should find starlette"
    
    print(f"   ✅ Parsed {len(packages)} packages")
    return True


def test_parse_version_spec():
    """Test version specification parsing"""
    print("🧪 Testing version spec parsing...")
    
    detector = DependencyConflictDetector()
    
    # Test case 1
    pkg, lower, upper = detector.parse_version_spec("starlette<0.49.0,>=0.40.0")
    assert pkg == "starlette", f"Expected 'starlette', got '{pkg}'"
    assert lower == "0.40.0", f"Expected '0.40.0', got '{lower}'"
    assert upper == "0.49.0", f"Expected '0.49.0', got '{upper}'"
    
    # Test case 2
    pkg, lower, upper = detector.parse_version_spec("httpcore>=1.0.0")
    assert pkg == "httpcore", f"Expected 'httpcore', got '{pkg}'"
    assert lower == "1.0.0", f"Expected '1.0.0', got '{lower}'"
    assert upper == "", f"Expected '', got '{upper}'"
    
    print("   ✅ Version spec parsing works correctly")
    return True


def test_check_version_compatibility():
    """Test version compatibility checking"""
    print("🧪 Testing version compatibility...")
    
    detector = DependencyConflictDetector()
    
    # Should be compatible
    assert detector.check_version_compatibility("0.48.0", "0.40.0", "0.49.0"), \
        "0.48.0 should be compatible with >=0.40.0,<0.49.0"
    
    # Should NOT be compatible (too high)
    assert not detector.check_version_compatibility("0.49.1", "0.40.0", "0.49.0"), \
        "0.49.1 should NOT be compatible with >=0.40.0,<0.49.0"
    
    # Should NOT be compatible (too low)
    assert not detector.check_version_compatibility("0.39.0", "0.40.0", "0.49.0"), \
        "0.39.0 should NOT be compatible with >=0.40.0,<0.49.0"
    
    print("   ✅ Version compatibility checking works correctly")
    return True


def test_generate_report():
    """Test report generation"""
    print("🧪 Testing report generation...")
    
    detector = DependencyConflictDetector()
    report = detector.generate_report()
    
    assert isinstance(report, DependencyReport), "Should return DependencyReport"
    assert report.total_packages > 0, "Should count packages"
    assert report.health_status in ['healthy', 'warning', 'critical'], \
        f"Invalid health status: {report.health_status}"
    
    print(f"   ✅ Generated report: {report.total_packages} packages, "
          f"{report.conflict_count} conflicts, status={report.health_status}")
    return True


def test_export_report():
    """Test report export"""
    print("🧪 Testing report export...")
    
    detector = DependencyConflictDetector()
    report = detector.generate_report()
    
    # Export to temp file (cross-platform)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        output_file = Path(tmp.name)
    
    try:
        result_file = detector.export_report(report, output_file)
        
        assert result_file.exists(), "Export file should exist"
        
        # Read back and validate
        with open(result_file) as f:
            data = json.load(f)
        
        assert 'timestamp' in data, "Should have timestamp"
        assert 'conflicts' in data, "Should have conflicts"
        assert 'health_status' in data, "Should have health_status"
        
        print("   ✅ Report export works correctly")
        return True
    finally:
        # Cleanup
        output_file.unlink(missing_ok=True)


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🔬 Testing Dependency Conflict Detector")
    print("="*70 + "\n")
    
    tests = [
        test_parse_requirements_file,
        test_parse_version_spec,
        test_check_version_compatibility,
        test_generate_report,
        test_export_report,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
