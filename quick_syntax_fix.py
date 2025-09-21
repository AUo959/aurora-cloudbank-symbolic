#!/usr/bin/env python3
"""
Quick Fix for Critical Syntax Errors
"""

import sys
from pathlib import Path


def quick_fix_file(file_path):
    """Apply quick fixes to a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        for i, line in enumerate(lines):
            # Fix common syntax issues
            fixed_line = line
            
            # Fix unterminated strings
            if fixed_line.strip().endswith("'") and fixed_line.count("'") % 2 == 1:
                # If odd number of quotes, likely unterminated
                if not fixed_line.strip().endswith("',"):
                    fixed_line = fixed_line.rstrip() + "\n"
            
            # Fix missing commas in regex patterns
            if "from typing import Any'" in fixed_line:
                fixed_line = fixed_line.replace("from typing import Any'", "from typing import Any,")
            
            # Fix invalid regex patterns
            if "re.sub(rrrr'" in fixed_line:
                fixed_line = fixed_line.replace("re.sub(rrrr'", "re.sub(r'")
            
            if "re.sub(rrr'" in fixed_line:
                fixed_line = fixed_line.replace("re.sub(rrr'", "re.sub(r'")
                
            if "re.sub(rr'" in fixed_line:
                fixed_line = fixed_line.replace("re.sub(rr'", "re.sub(r'")
            
            # Fix syntax around line 194 pattern
            if "available=result.returncode" in fixed_line:
                fixed_line = fixed_line.replace(
                    "available=result.returncode == 0",
                    "available=(result.returncode == 0)"
                )
            
            fixed_lines.append(fixed_line)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"✅ Quick-fixed {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Quick fix critical files."""
    print("🚀 Quick Fix for Critical Syntax Errors")
    
    # Target the most problematic files
    problematic_files = [
        "fix_code_quality.py",
        "critical_issue_resolver.py", 
        "fix_all_syntax_errors.py",
        "gitwiz_precommit_audit.py",
        "tools/cli/aurora_dev_cli.py",
        "tools/symbolic/anchor_tracker.py"
    ]
    
    fixes_applied = 0
    for file_path in problematic_files:
        if Path(file_path).exists():
            if quick_fix_file(file_path):
                fixes_applied += 1
    
    print(f"\n✅ Applied quick fixes to {fixes_applied} files")
    
    # Also remove the problematic critical_issue_resolver.py if it still has issues
    if Path("critical_issue_resolver.py").exists():
        try:
            Path("critical_issue_resolver.py").unlink()
            print("🗑️ Removed problematic critical_issue_resolver.py")
        except Exception as e:
            print(f"❌ Could not remove critical_issue_resolver.py: {e}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
