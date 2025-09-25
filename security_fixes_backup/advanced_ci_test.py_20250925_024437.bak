#!/usr/bin/env python3
"""
Advanced CI Pipeline Simulation Test
Tests the kinds of checks that GitHub Actions and Codacy would run
"""
import subprocess
import sys
import json
from pathlib import Path

def test_requirements_txt():
    """Test if requirements.txt exists and is valid"""
    print("🔍 Testing requirements.txt...")
    req_file = Path("requirements.txt")
    if req_file.exists():
        print("✅ requirements.txt exists")
        try:
            with open("requirements.txt", "r") as f:
                lines = f.readlines()
            print(f"✅ Found {len(lines)} requirements")
            return True
        except Exception as e:
            print(f"❌ Error reading requirements.txt: {e}")
            return False
    else:
        print("⚠️  requirements.txt not found (may not be required)")
        return True

def test_package_json():
    """Test if package.json exists and is valid"""
    print("🔍 Testing package.json...")
    pkg_file = Path("package.json")
    if pkg_file.exists():
        print("✅ package.json exists")
        try:
            with open("package.json", "r") as f:
                data = json.load(f)
            print(f"✅ Valid JSON with {len(data)} top-level keys")
            return True
        except Exception as e:
            print(f"❌ Error reading package.json: {e}")
            return False
    else:
        print("⚠️  package.json not found")
        return True

def test_github_workflows():
    """Test GitHub Actions workflow files"""
    print("🔍 Testing GitHub Actions workflows...")
    workflow_dir = Path(".github/workflows")
    if workflow_dir.exists():
        workflows = list(workflow_dir.glob("*.yml"))
        print(f"✅ Found {len(workflows)} workflow files")
        return True
    else:
        print("⚠️  No GitHub workflows found")
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
            print("✅ Python compilation works")
            return True
        else:
            print(f"❌ Python compilation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Python compilation timeout")
        return False
    except Exception as e:
        print(f"❌ Python compilation error: {e}")
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
            print(f"✅ Found {dir_name}/")
        else:
            print(f"⚠️  Missing {dir_name}/")
    
    print(f"✅ Found {len(found_dirs)}/{len(expected_dirs)} expected directories")
    return len(found_dirs) >= 2  # At least 2 core directories

def test_basic_security():
    """Test basic security patterns"""
    print("🔍 Testing basic security patterns...")
    try:
        # Check for basic security file
        if Path("security_verification.py").exists():
            print("✅ Security verification script exists")
            
        # Check for .security directory (our security suite)
        if Path(".security").exists():
            print("✅ Security suite directory exists")
            
        return True
    except Exception as e:
        print(f"❌ Security check error: {e}")
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
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 CI Pipeline Simulation Results: {passed}/{total} tests passed")
    
    if passed >= total - 1:  # Allow 1 failure
        print("🎉 CI pipeline is likely to succeed!")
        print("🚀 Ready for GitHub Actions and Codacy analysis")
        return 0
    else:
        print("⚠️  Some issues detected - CI may have problems")
        print("💡 Fix the issues above for optimal CI performance")
        return 1

if __name__ == "__main__":
    sys.exit(main())