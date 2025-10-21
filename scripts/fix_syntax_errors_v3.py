#!/usr/bin/env python3
"""
Fix remaining syntax errors in Aurora CloudBank project.
Targets the 55 remaining E9 errors in scripts and test files.
"""

import os
import re
import sys
from pathlib import Path


def fix_broken_print_statements(content):
    """Fix broken print statements with %s format specifiers."""
    changes = 0
    
    # Pattern 1: print("...\n%s", ...) -> print(f"...\n{'='*60}")
    pattern1 = r'print\(""\s*\n%s",\s*([^)]+)\)'
    if re.search(pattern1, content):
        content = re.sub(pattern1, r'print("\n" + str(\1))', content)
        changes += 1
    
    # Pattern 2: print("   text: %s", value) on separate lines
    pattern2 = r'print\("([^"]*?):\s*%s",\s*([^)]+)\)'
    matches = list(re.finditer(pattern2, content))
    for match in matches:
        text = match.group(1)
        value = match.group(2).strip()
        replacement = f'print(f"{text}: {{{value}}}")'
        content = content.replace(match.group(0), replacement)
        changes += 1
    
    # Pattern 3: print("text: %s%", value) -> print(f"text: {value:.1f}%")
    pattern3 = r'print\("([^"]*?):\s*%s%",\s*\(([^)]+)\)\.?:?\.?1?f?\)'
    if re.search(pattern3, content):
        content = re.sub(pattern3, r'print(f"\1: {\2:.1f}%")', content)
        changes += 1
    
    return content, changes

def fix_invalid_decimal_literals(content):
    """Fix invalid decimal literals like 'variable:.1f'."""
    changes = 0
    
    # Pattern: %s", (expression):.1f) -> {expression:.1f}")
    pattern = r'%s",\s*\(([^)]+)\):\.1f\)'
    if re.search(pattern, content):
        content = re.sub(pattern, r'{{\1:.1f}}")', content)
        changes += 1
    
    return content, changes

def fix_unterminated_strings(content):
    """Fix unterminated string literals."""
    changes = 0
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check for standalone %s on a line
        if re.match(r'^\s*%s"\s*,', line):
            # Previous line should be completed
            if i > 0 and fixed_lines:
                prev = fixed_lines[-1]
                if prev.strip().endswith('print("'):
                    # Merge with previous line
                    fixed_lines[-1] = prev.rstrip() + line.lstrip()
                    changes += 1
                    continue
        
        fixed_lines.append(line)
    
    if changes > 0:
        content = '\n'.join(fixed_lines)
    
    return content, changes

def fix_undefined_imports(content, filename):
    """Add missing imports for commonly undefined names."""
    changes = 0
    
    # Check if shlex is used but not imported
    if 'shlex' in content and 'import shlex' not in content:
        # Add import at the top after other imports
        lines = content.split('\n')
        import_section_end = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_section_end = i + 1
        
        lines.insert(import_section_end, 'import shlex')
        content = '\n'.join(lines)
        changes += 1
    
    return content, changes

def fix_file(filepath):
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        content = original_content
        total_changes = 0
        
        # Apply all fixes
        content, changes = fix_broken_print_statements(content)
        total_changes += changes
        
        content, changes = fix_invalid_decimal_literals(content)
        total_changes += changes
        
        content, changes = fix_unterminated_strings(content)
        total_changes += changes
        
        content, changes = fix_undefined_imports(content, filepath)
        total_changes += changes
        
        # Only write if changes were made
        if total_changes > 0 and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, total_changes
        
        return False, 0
    
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False, 0

def main():
    """Main function to fix all files with syntax errors."""
    # Get list of files with E9 errors
    import subprocess
    
    result = subprocess.run(
        ['python3', '-m', 'flake8', '.', '--select=E9,F63,F7,F82', '--format=%(path)s'],
        capture_output=True,
        text=True,
        cwd='/workspaces/aurora-cloudbank-symbolic'
    )
    
    files_with_errors = sorted(set(result.stdout.strip().split('\n')))
    files_with_errors = [f for f in files_with_errors if f and os.path.exists(f)]
    
    print(f"🔧 Found {len(files_with_errors)} files with syntax errors")
    print(f"🔧 Attempting to fix...\n")
    
    fixed_count = 0
    total_changes = 0
    
    for filepath in files_with_errors:
        if not filepath or not os.path.exists(filepath):
            continue
        
        print(f"Processing: {filepath}")
        was_fixed, changes = fix_file(filepath)
        
        if was_fixed:
            fixed_count += 1
            total_changes += changes
            print(f"  ✅ Fixed {changes} issues")
        else:
            print(f"  ⏭️  No automatic fix available")
    
    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_count} files ({total_changes} total changes)")
    print(f"{'='*60}\n")
    
    # Re-run flake8 to see remaining errors
    result = subprocess.run(
        ['python3', '-m', 'flake8', '.', '--select=E9,F63,F7,F82', '--count'],
        capture_output=True,
        text=True,
        cwd='/workspaces/aurora-cloudbank-symbolic'
    )
    
    remaining = result.stdout.strip().split('\n')[-1] if result.stdout.strip() else "0"
    print(f"📊 Remaining E9 errors: {remaining}\n")

if __name__ == '__main__':
    main()
