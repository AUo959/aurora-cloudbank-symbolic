#!/usr/bin/env python3
"""
Quick CI compatibility test to verify basic Python functionality
"""
import sys
import subprocess

def test_basic_imports():
    """Test that critical modules can be imported without syntax errors"""
    critical_files = [
        'aurora_api.py',
        'aurora_api_server.py', 
        'setup_aurora_branches.py',
        'security_verification.py',
        'aurora_realworld_integration.py',
        'aurora_gui_cloudhub_fastapi.py'
    ]
    
    passed = 0
    failed = 0
    
    print("🧪 Testing critical file imports...")
    
    for file in critical_files:
        try:
            result = subprocess.run([sys.executable, '-m', 'py_compile', file], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {file}")
                passed += 1
            else:
                print(f"❌ {file}: {result.stderr.strip()}")
                failed += 1
        except subprocess.TimeoutExpired:
            print(f"⏰ {file}: Timeout")
            failed += 1
        except Exception as e:
            print(f"💥 {file}: {e}")
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
        print("✅ Basic math works")
        
        # Test subprocess
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, "Python version check failed"
        print("✅ Python subprocess works")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
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