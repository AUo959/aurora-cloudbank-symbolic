#!/usr/bin/env python3
"""
Test script to validate security fixes applied
"""
import re
import os
import subprocess
from pathlib import Path

def test_log_injection_fix():
    """Test that f-string logging is fixed"""
    aif_hub_path = "services/aif_hub.py"
    with open(aif_hub_path, 'r') as f:
        content = f.read()
    
    # Check that f-string logging is replaced with parameterized logging
    if 'logger.info("Generated AIF_TOKEN: %s"' in content:
        print("✅ Log injection fix applied in services/aif_hub.py")
        return True
    else:
        print("❌ Log injection fix not found in services/aif_hub.py")
        return False

def test_shell_injection_fix():
    """Test that shell=True is replaced with shell=False"""
    files_to_check = [
        "scripts/aurora_codeql_diagnostics.py",
        "scripts/phase4b_value_extractor.py", 
        "scripts/phase3b_conflict_resolver.py",
        "scripts/ssmt_v2_2_architectural_sonar.py"
    ]
    
    fixes_found = 0
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            if 'shell=False' in content and 'shlex.split' in content:
                print(f"✅ Shell injection fix applied in {file_path}")
                fixes_found += 1
            else:
                print(f"❌ Shell injection fix not complete in {file_path}")
    
    return fixes_found >= 3

def test_html_sanitization_fix():
    """Test that HTML sanitization is improved"""
    web_test_path = "tests/web/test-web-components.js"
    if os.path.exists(web_test_path):
        with open(web_test_path, 'r') as f:
            content = f.read()
        
        # Check for comprehensive sanitization
        if 'script[^>]*>[\\s\\S]*?<\\/script>' in content and 'style[^>]*>[\\s\\S]*?<\\/style>' in content:
            print("✅ HTML sanitization fix applied in tests/web/test-web-components.js")
            return True
        else:
            print("❌ HTML sanitization fix not complete in tests/web/test-web-components.js")
    return False

def test_url_validation_fix():
    """Test that URL validation is added"""
    middleware_path = "middleware/aurora-security-middleware.js"
    if os.path.exists(middleware_path):
        with open(middleware_path, 'r') as f:
            content = f.read()
        
        if 'validateURLScheme' in content and 'allowedSchemes' in content:
            print("✅ URL validation fix applied in middleware/aurora-security-middleware.js")
            return True
        else:
            print("❌ URL validation fix not found in middleware/aurora-security-middleware.js")
    return False

def main():
    """Run all security fix validation tests"""
    print("🔍 Validating Security Fixes Applied")
    print("=" * 50)
    
    tests = [
        ("Log Injection Fix", test_log_injection_fix),
        ("Shell Injection Fix", test_shell_injection_fix), 
        ("HTML Sanitization Fix", test_html_sanitization_fix),
        ("URL Validation Fix", test_url_validation_fix)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        if test_func():
            passed += 1
    
    print(f"\n📊 Summary: {passed}/{total} security fixes validated")
    if passed == total:
        print("🎉 All security fixes successfully applied!")
        return True
    else:
        print("⚠️  Some security fixes may need review")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)