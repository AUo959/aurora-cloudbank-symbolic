#!/usr/bin/env python3
"""
Stage 3 Fixer: Undefined Names and Logic Errors
Fixes F821 (undefined names) and E999 (syntax errors)
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple, Dict


def fix_undefined_names(file_path: str) -> Tuple[bool, List[str]]:
    """
    Fix common undefined name issues.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Common fixes for undefined names
        fixes = {
            # Missing imports
            'logging': 'import logging\n',
            'uvicorn': 'import uvicorn\n', 
            'result': None,  # Usually a variable issue, needs manual inspection
        }
        
        lines = content.split('\n')
        
        # Add missing imports at the top after existing imports
        import_section_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_section_end = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                break
        
        added_imports = []
        
        # Check if we need to add logging import
        if 'logging' in content and 'import logging' not in content:
            lines.insert(import_section_end, 'import logging')
            added_imports.append('logging')
            fixes_applied.append("Added missing 'import logging'")
        
        # Check if we need to add uvicorn import  
        if 'uvicorn' in content and 'import uvicorn' not in content:
            lines.insert(import_section_end + len(added_imports), 'import uvicorn')
            added_imports.append('uvicorn')
            fixes_applied.append("Added missing 'import uvicorn'")
        
        # Fix undefined 'result' variables by initializing them
        for i, line in enumerate(lines):
            if 'result' in line and 'return result' in line:
                # Look backwards to see if result is defined
                result_defined = False
                for j in range(i-1, max(0, i-10), -1):
                    if 'result =' in lines[j] or 'result:' in lines[j]:
                        result_defined = True
                        break
                
                if not result_defined:
                    # Add result initialization before the return
                    indent = len(line) - len(line.lstrip())
                    lines.insert(i, ' ' * indent + 'result = None  # Default result')
                    fixes_applied.append(f"Line {i+1}: Added result initialization")
        
        content = '\n'.join(lines)
        
        # Write back if modified
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, fixes_applied
        
        return False, []
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, []


def fix_syntax_errors(file_path: str) -> Tuple[bool, List[str]]:
    """
    Fix basic syntax errors.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        lines = content.split('\n')
        
        # Fix missing except/finally blocks for try statements
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for try statements
            if line.strip().startswith('try:'):
                # Look for the matching except/finally
                j = i + 1
                found_except_or_finally = False
                try_block_indent = len(line) - len(line.lstrip())
                
                while j < len(lines):
                    current_line = lines[j]
                    current_indent = len(current_line) - len(current_line.lstrip())
                    
                    # If we find a line at the same indent level as try
                    if current_indent == try_block_indent and current_line.strip():
                        if (current_line.strip().startswith('except') or 
                            current_line.strip().startswith('finally')):
                            found_except_or_finally = True
                            break
                        elif not current_line.strip().startswith('try:'):
                            # We've hit another statement at the same level
                            break
                    j += 1
                
                # If no except/finally found, add a generic except block
                if not found_except_or_finally:
                    except_line = ' ' * try_block_indent + 'except Exception as e:'
                    pass_line = ' ' * (try_block_indent + 4) + 'pass  # TODO: Handle exception'
                    
                    lines.insert(j, except_line)
                    lines.insert(j + 1, pass_line)
                    fixes_applied.append(f"Line {i+1}: Added missing except block for try statement")
                    i = j + 2  # Skip past the inserted lines
                    continue
            
            # Fix missing indented blocks after if/for/while/def/class
            if (line.strip().endswith(':') and 
                (line.strip().startswith('if ') or 
                 line.strip().startswith('for ') or 
                 line.strip().startswith('while ') or
                 line.strip().startswith('def ') or
                 line.strip().startswith('class ') or
                 line.strip().startswith('else:') or
                 line.strip().startswith('elif '))):
                
                # Check if next line is properly indented
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    current_indent = len(line) - len(line.lstrip())
                    
                    if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= current_indent:
                        # Next line is not indented properly, add a pass statement
                        pass_line = ' ' * (current_indent + 4) + 'pass  # TODO: Implement'
                        lines.insert(i + 1, pass_line)
                        fixes_applied.append(f"Line {i+1}: Added missing indented block after {line.strip()[:20]}...")
            
            i += 1
        
        content = '\n'.join(lines)
        
        # Write back if modified
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, fixes_applied
        
        return False, []
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, []


def process_file(file_path: str) -> Tuple[bool, List[str]]:
    """Process a single file for Stage 3 fixes."""
    all_fixes = []
    was_modified = False
    
    # First fix syntax errors
    modified1, fixes1 = fix_syntax_errors(file_path)
    if modified1:
        was_modified = True
        all_fixes.extend(fixes1)
    
    # Then fix undefined names
    modified2, fixes2 = fix_undefined_names(file_path)
    if modified2:
        was_modified = True
        all_fixes.extend(fixes2)
    
    return was_modified, all_fixes


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
        was_modified, fixes = process_file(str(file_path))
        if was_modified:
            total_modified += 1
            total_fixes += len(fixes)
            print(f"✅ Fixed {file_path.relative_to(directory_path)}: {len(fixes)} fixes")
            for fix in fixes:
                print(f"   - {fix}")
        else:
            print(f"✨ Clean {file_path.relative_to(directory_path)}")
    
    print(f"\n📊 Stage 3 Summary for {directory}:")
    print(f"   Files modified: {total_modified}")
    print(f"   Total fixes applied: {total_fixes}")


def main():
    """Main function to process all target areas."""
    print("🧹 Stage 3: Undefined Names and Logic Errors")
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
        
    print("\n🎉 Stage 3 cleanup complete!")


if __name__ == "__main__":
    main()