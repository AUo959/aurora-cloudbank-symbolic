#!/usr/bin/env python3
"""Aurora CloudBank Minimal Automation Wrapper"""

import subprocess
import sys
import time
from pathlib import Path

def run_health_check():
    """Run quick health check"""
    try:
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent / "aurora_quick_health_check.py")
        ], timeout=30)
        return result.returncode == 0
    except:
        return False

def run_maintenance():
    """Run basic maintenance"""
    print("🔧 Running Aurora CloudBank maintenance...")
    
    if run_health_check():
        print("✅ Health check passed")
    else:
        print("⚠️  Health check failed, consider manual review")
        
    # Try to use existing GitWiz if available
    gitwiz_path = Path(__file__).parent / "gitwiz_dependency_updater.py"
    if gitwiz_path.exists():
        try:
            subprocess.run([sys.executable, str(gitwiz_path), "--status"], timeout=60)
        except:
            pass
            
    print("🚀 Maintenance complete")

if __name__ == "__main__":
    run_maintenance()
