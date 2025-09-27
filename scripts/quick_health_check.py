#!/usr/bin/env python3
"""Quick repository health check"""

import subprocess
from datetime import datetime

def quick_health_check():
    print("🩺 Quick Repository Health Check")
    
    try:
        # Get branch count
        result = subprocess.run(
            ["git", "branch", "-r", "--format=%(refname:short)"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            branches = [b.strip() for b in result.stdout.strip().split('\n') 
                       if b.strip() and not b.startswith('origin/HEAD') and b.strip() != 'origin']
            branch_count = len(branches)
            
            print("   🌳 Current branches: %s", branch_count)
            
            if branch_count <= 30:
                print("   💚 Status: EXCELLENT (maintaining gains!)")
            elif branch_count <= 35:
                print("   🟡 Status: GOOD (minor growth)")
            elif branch_count <= 45:
                print("   🟠 Status: FAIR (needs attention)")
            else:
                print("   🔴 Status: CRITICAL (requires immediate action)")
            
            print("   📅 Check time: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
        else:
            print("   ❌ Could not retrieve branch information")
            
    except Exception as e:
        print("   💥 Error: %s", e)

if __name__ == "__main__":
    quick_health_check()
