#!/usr/bin/env python3
"""
Stage 1 Lint Fixer: Whitespace and Formatting
Fixes W293 (blank line contains whitespace), E303 (too many blank lines), E302 (expected 2 blank lines)
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def fix_whitespace_issues(file_path: str) -> Tuple[bool, List[str]]:
    """
    Fix whitespace issues in a Python file.
    
    Returns:
        Tuple of (was_modified, list_of_fixes_applied)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Fix W293: blank line contains whitespace
        lines = content.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            if line.strip() == '' and line != '':  # Line has only whitespace
                fixed_lines.append('')  # Remove whitespace
                fixes_applied.append(f"Line {i+1}: Removed whitespace from blank line (W293)")
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix E303: too many blank lines (more than 2)
        # Replace 3+ consecutive blank lines with exactly 2
        content = re.sub(r'\n\n\n+', '\n\n\n', content)
        if content != '\n'.join(fixed_lines):
            fixes_applied.append("Fixed excessive blank lines (E303)")
        
        # Fix E302: expected 2 blank lines before class/function definitions at module level
        # This is more complex - we need to identify top-level class/function definitions
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a top-level class or function definition
            if (line.strip().startswith('class ') or line.strip().startswith('def ')) and not line.startswith(' ') and not line.startswith('\t'):
                # Check how many blank lines precede this
                blank_count = 0
                j = i - 1
                while j >= 0 and lines[j].strip() == '':
                    blank_count += 1
                    j -= 1
                
                # We need exactly 2 blank lines before top-level class/function definitions
                # unless it's at the beginning of the file or after imports/docstrings
                if j >= 0 and blank_count < 2:
                    # Check if previous non-blank line is an import, comment, or docstring
                    prev_line = lines[j].strip()
                    if not (prev_line.startswith('import ') or 
                           prev_line.startswith('from ') or 
                           prev_line.startswith('#') or
                           prev_line.startswith('"""') or
                           prev_line.endswith('"""') or
                           prev_line.startswith("'''") or
                           prev_line.endswith("'''")):
                        
                        # Add the missing blank lines
                        needed_blanks = 2 - blank_count
                        for _ in range(needed_blanks):
                            fixed_lines.append('')
                        fixes_applied.append(f"Line {i+1}: Added blank lines before {line.strip()[:30]}... (E302)")
            
            fixed_lines.append(line)
            i += 1
        
        content = '\n'.join(fixed_lines)
        
        # Write back if modified
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
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
        was_modified, fixes = fix_whitespace_issues(str(file_path))
        if was_modified:
            total_modified += 1
            total_fixes += len(fixes)
            print(f"✅ Fixed {file_path.relative_to(directory_path)}: {len(fixes)} fixes")
            for fix in fixes:
                print(f"   - {fix}")
        else:
            print(f"✨ Clean {file_path.relative_to(directory_path)}")
    
    print(f"\n📊 Stage 1 Summary for {directory}:")
    print(f"   Files modified: {total_modified}")
    print(f"   Total fixes applied: {total_fixes}")


def main():
    """Main function to process all target areas."""
    print("🧹 Stage 1: Whitespace and Formatting Cleanup")
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
        
    print("\n🎉 Stage 1 whitespace cleanup complete!")


if __name__ == "__main__":
    main()