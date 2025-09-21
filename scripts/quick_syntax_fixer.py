#!/usr/bin/env python3
"""
Quick syntax fixer for indentation issues
"""

import re
from pathlib import Path


def fix_indentation_issues(file_path: str) -> bool:
    """Fix common indentation issues in Python files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Fix function definitions that are incorrectly indented
            if re.match(r'^\s+def\s+', line) and i > 0:
                # Check if previous line ends with colon (class or function definition)
                prev_line = lines[i-1].strip()
                if prev_line.endswith(':') and not line.startswith('        def'):
                    # Ensure proper indentation for method definitions inside classes
                    if 'class ' in '\n'.join(lines[:i]):
                        # Fix method indentation to 4 spaces
                        line = '    ' + line.strip()
            
            # Fix lines that should be indented after try/if/for/while/class/def
            if i > 0:
                prev_line = lines[i-1].strip()
                if (prev_line.endswith(':') and 
                    (prev_line.startswith('try') or prev_line.startswith('if ') or 
                     prev_line.startswith('for ') or prev_line.startswith('while ') or
                     prev_line.startswith('class ') or prev_line.startswith('def ') or
                     prev_line.startswith('async def '))):
                    
                    # Next line should be indented
                    if line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                        # Count current indentation
                        current_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                        if current_indent == 0:
                            line = '    ' + line.strip()  # Top level needs 4 spaces
                        else:
                            line = ' ' * (current_indent + 4) + line.strip()
            
            fixed_lines.append(line)
            i += 1
        
        fixed_content = '\n'.join(fixed_lines)
        
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed indentation in {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    files_to_fix = [
        "modules/opal2/plugin_system.py",
        "modules/opal2/plugins/base_plugin.py"
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            fix_indentation_issues(file_path)


if __name__ == "__main__":
    main()