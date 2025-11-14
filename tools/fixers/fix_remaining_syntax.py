#!/usr/bin/env python3
"""
Quick syntax fixer for remaining critical Python files
"""
import logging

logger = logging.getLogger(__name__)

import os
import subprocess

def fix_file(filepath):
    """Attempt to fix common syntax issues in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Common fixes
        original_content = content
        
        # Fix unterminated strings (common pattern)
        if 'print("' in content and content.count('print("') != content.count('")'):
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('print("') and not line.strip().endswith('")'):
                    if i + 1 < len(lines) and not lines[i + 1].strip():
                        lines[i] = line + '")'
            content = '\n'.join(lines)
        
        # Fix common indentation after try/except/if
        lines = content.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            if line.strip() in ['try:', 'except:', 'except Exception as e:', 'if True:', 'else:']:
                fixed_lines.append(line)
                # Add a pass statement if next line is not indented
                if i + 1 < len(lines):
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    if not next_line.strip() or not next_line.startswith('    '):
                        fixed_lines.append('    pass')
                else:
                    fixed_lines.append('    pass')
            else:
                fixed_lines.append(line)
        content = '\n'.join(fixed_lines)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Fixed: {filepath}")
            return True
        return False
        
    except Exception as e:
        logger.error("Error fixing {filepath}: {e}")
        return False

def main():
    """Fix critical Python syntax errors"""
    print("🔧 Fixing remaining Python syntax errors...")
    
    # Find Python files with syntax errors
    result = subprocess.run(['find', '.', '-name', '*.py', '-not', '-path', './.venv/*', '-not', '-path', './venv_opal2/*'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error("Could not find Python files")
        return
    
    files_to_check = result.stdout.strip().split('\n')[:20]  # Check first 20 files
    
    fixed_count = 0
    for filepath in files_to_check:
        if not filepath.strip():
            continue
        try:
            # Test compilation
            subprocess.run(['python3', '-m', 'py_compile', filepath], 
                          check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"🔧 Attempting to fix: {filepath}")
            if fix_file(filepath):
                fixed_count += 1
    
    print(f"🎉 Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
