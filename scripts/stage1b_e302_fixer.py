#!/usr/bin/env python3
"""
Stage 1B: Enhanced Whitespace Fixer  
More aggressive fixing of E302 issues
"""

import re
from pathlib import Path
from typing import List, Tuple


def fix_e302_issues(file_path: str) -> Tuple[bool, List[str]]:
    """
    Fix E302 issues (expected 2 blank lines before top-level definitions).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        fixed_lines = []
        fixes_applied = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a top-level class or function definition
            if (line.strip().startswith('class ') or 
                line.strip().startswith('def ') or 
                line.strip().startswith('async def ')) and not line.startswith(' ') and not line.startswith('\t'):
                
                # Count blank lines before this definition
                blank_count = 0
                j = i - 1
                while j >= 0 and lines[j].strip() == '':
                    blank_count += 1
                    j -= 1
                
                # Check what the previous non-blank line is
                if j >= 0:
                    prev_line = lines[j].strip()
                    
                    # Skip adding blanks if previous line is:
                    # - Import statement
                    # - Module docstring
                    # - Comment
                    # - Another function/class definition at top level
                    if not (prev_line.startswith('import ') or 
                           prev_line.startswith('from ') or 
                           prev_line.startswith('#') or
                           prev_line.startswith('"""') or 
                           prev_line.endswith('"""') or
                           prev_line.startswith("'''") or 
                           prev_line.endswith("'''")):
                        
                        # We need exactly 2 blank lines
                        if blank_count < 2:
                            needed_blanks = 2 - blank_count
                            # Add the missing blank lines
                            for _ in range(needed_blanks):
                                fixed_lines.append('')
                            fixes_applied.append(f"Line {i+1}: Added {needed_blanks} blank lines before {line.strip()[:30]}... (E302)")
                        elif blank_count > 2:
                            # Remove excess blank lines
                            excess = blank_count - 2
                            # Remove the excess from what we've already added
                            for _ in range(excess):
                                if fixed_lines and fixed_lines[-1] == '':
                                    fixed_lines.pop()
                            fixes_applied.append(f"Line {i+1}: Removed {excess} excess blank lines before {line.strip()[:30]}... (E302)")
            
            fixed_lines.append(line)
            i += 1
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Write back if modified
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True, fixes_applied
        
        return False, []
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, []


def process_directory(directory: str) -> None:
    """Process all Python files in a directory."""
    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"⚠️  Directory not found: {directory}")
        return
    
    python_files = list(directory_path.rglob("*.py"))
    if not python_files:
        print(f"⚠️  No Python files found in {directory}")
        return
    
    print(f"🔧 Processing {len(python_files)} Python files in {directory}...")
    
    total_modified = 0
    total_fixes = 0
    
    for file_path in python_files:
        was_modified, fixes = fix_e302_issues(str(file_path))
        if was_modified:
            total_modified += 1
            total_fixes += len(fixes)
            print(f"✅ Fixed {file_path.relative_to(directory_path)}: {len(fixes)} fixes")
            for fix in fixes:
                print(f"   - {fix}")
        else:
            print(f"✨ Clean {file_path.relative_to(directory_path)}")
    
    print(f"\n📊 Stage 1B Summary for {directory}:")
    print(f"   Files modified: {total_modified}")
    print(f"   Total E302 fixes applied: {total_fixes}")


def main():
    """Main function to process all target areas."""
    print("🧹 Stage 1B: Enhanced E302 Fixes")
    print("=" * 50)
    
    target_areas = [
        "modules/opal2",
        "modules/cask", 
        "src/core",
        "src/bridges",
        "src/servers"
    ]
    
    for area in target_areas:
        print(f"\n🎯 Processing {area}...")
        process_directory(area)
        
    print("\n🎉 Stage 1B E302 cleanup complete!")


if __name__ == "__main__":
    main()