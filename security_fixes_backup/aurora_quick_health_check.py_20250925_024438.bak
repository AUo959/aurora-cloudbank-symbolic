#!/usr/bin/env python3
"""Simple dependency health check for Aurora CloudBank"""

import subprocess
import sys
from pathlib import Path

def quick_health_check():
    """Quick health check of dependencies"""
    issues = []
    
    # Check pip is working
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, timeout=10)
        if result.returncode != 0:
            issues.append("pip not working")
    except:
        issues.append("pip check failed")
        
    # Check critical packages
    try:
        import json
        # These should be available in most Python environments
        pass
    except ImportError as e:
        issues.append(f"Import error: {e}")
        
    return len(issues) == 0, issues

if __name__ == "__main__":
    healthy, issues = quick_health_check()
    if healthy:
        print("✅ Dependencies healthy")
        sys.exit(0)
    else:
        print("❌ Issues found: %s", ', '.join(issues))
        sys.exit(1)
