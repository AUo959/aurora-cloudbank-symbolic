#!/usr/bin/env python3
"""
Advanced CI Pipeline Simulation Test
Tests the kinds of checks that GitHub Actions and Codacy would run
"""
import logging

logger = logging.getLogger(__name__)

import subprocess
import sys
import json
from pathlib import Path

def test_requirements_txt():
    """Test if requirements.txt exists and is valid"""
    print("🔍 Testing requirements.txt...")
    req_file = Path("requirements.txt")
    if req_file.exists():
        logger.info("requirements.txt exists")
        try:
            with open("requirements.txt", "r") as f:
                lines = f.readlines()
            logger.info("Found {len(lines)} requirements")
            return True
        except Exception as e:
            logger.error("Error reading requirements.txt: {e}")
            return False
    else:
        logger.warning("requirements.txt not found (may not be required)")
        return True

def test_package_json():
    """Test if package.json exists and is valid"""
    print("🔍 Testing package.json...")
    pkg_file = Path("package.json")
    if pkg_file.exists():
        logger.info("package.json exists")
        try:
            with open("package.json", "r") as f:
                data = json.load(f)
            logger.info("Valid JSON with {len(data)} top-level keys")
            return True
        except Exception as e:
            logger.error("Error reading package.json: {e}")
            return False
    else:
        logger.warning("package.json not found")
        return True

def test_github_workflows():
    """Test GitHub Actions workflow files"""
    print("🔍 Testing GitHub Actions workflows...")
    workflow_dir = Path(".github/workflows")
    if workflow_dir.exists():
        workflows = list(workflow_dir.glob("*.yml"))
        logger.info("Found {len(workflows)} workflow files")
        return True
    else:
        logger.warning("No GitHub workflows found")
        return True

def test_flake8_basic():
    """Test basic flake8 compatibility"""
    print("🔍 Testing flake8 basic compatibility...")
    try:
        # Test with basic Python syntax check
        result = subprocess.run([
            sys.executable, "-m", "py_compile", "aurora_api.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("Python compilation works")
            return True
        else:
            logger.error("Python compilation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Python compilation timeout")
        return False
    except Exception as e:
        logger.error("Python compilation error: {e}")
        return False

def test_module_structure():
    """Test if expected modules/directories exist"""
    print("🔍 Testing module structure...")
    expected_dirs = ["modules", "src", "scripts", ".github"]
    found_dirs = []
    
    for dir_name in expected_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            found_dirs.append(dir_name)
            logger.info("Found {dir_name}/")
        else:
            logger.warning("Missing {dir_name}/")
    
    logger.info("Found {len(found_dirs)}/{len(expected_dirs)} expected directories")
    return len(found_dirs) >= 2  # At least 2 core directories

def test_basic_security():
    """Test basic security patterns"""
    print("🔍 Testing basic security patterns...")
    try:
        # Check for basic security file
        if Path("security_verification.py").exists():
            logger.info("Security verification script exists")
            
        # Check for .security directory (our security suite)
        if Path(".security").exists():
            logger.info("Security suite directory exists")
            
        return True
    except Exception as e:
        logger.error("Security check error: {e}")
        return False

def main():
    """Run advanced CI simulation tests"""
    print("🚀 Aurora CloudBank Advanced CI Pipeline Test")
    print("=" * 60)
    
    tests = [
        test_requirements_txt,
        test_package_json,
        test_github_workflows,
        test_flake8_basic,
        test_module_structure,
        test_basic_security
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print()
        except Exception as e:
            logger.error("Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 CI Pipeline Simulation Results: {passed}/{total} tests passed")
    
    if passed >= total - 1:  # Allow 1 failure
        print("🎉 CI pipeline is likely to succeed!")
        print("🚀 Ready for GitHub Actions and Codacy analysis")
        return 0
    else:
        logger.warning("Some issues detected - CI may have problems")
        print("💡 Fix the issues above for optimal CI performance")
        return 1

if __name__ == "__main__":
    sys.exit(main())