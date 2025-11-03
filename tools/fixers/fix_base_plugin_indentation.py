#!/usr/bin/env python3
"""
Base Plugin Indentation Fixer
Fixes the systematic indentation issues in base_plugin.py
"""

import re


def fix_base_plugin_file():
    """Fix all indentation issues in base_plugin.py."""
    file_path = "modules/opal2/plugins/base_plugin.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        fixed_lines = []
        
        in_class = False
        for i, line in enumerate(lines):
            # Detect class definition
            if line.strip().startswith('class ') and ':' in line:
                in_class = True
                fixed_lines.append(line)
                continue
            
            # Fix method definitions inside class
            if in_class and line.strip().startswith('def ') and ':' in line:
                # Method should be indented with 4 spaces from class
                if not line.startswith('    def '):
                    line = '    ' + line.strip()
                fixed_lines.append(line)
                continue
            
            # Fix method content (should be indented 8 spaces from class start)
            if in_class and line.strip() and not line.startswith('    '):
                # If it's not already properly indented and not a class/def line
                if not line.strip().startswith(('class ', 'def ', '#', '"""', "'''")) and line.strip() != '':
                    # Make sure it has proper method indentation
                    if line.startswith(' ') and not line.startswith('        '):
                        # Already has some indentation, fix it to 8 spaces
                        line = '        ' + line.strip()
                    elif not line.startswith(' '):
                        # No indentation, add 8 spaces for method content
                        line = '        ' + line.strip()
            
            # Detect end of class
            if line.strip() and not line.startswith(' ') and not line.startswith('\t') and in_class:
                if not line.strip().startswith('#'):
                    in_class = False
            
            fixed_lines.append(line)
        
        # Join lines back together
        fixed_content = '\n'.join(fixed_lines)
        
        # Additional specific fixes for common patterns
        patterns = [
            # Fix try/except blocks
            (r'(\s+)try:\n(\s*)(\w+)', r'\1try:\n\1    \3'),
            (r'(\s+)except([^:]*?):\n(\s*)(\w+)', r'\1except\2:\n\1    \4'),
            # Fix if statements
            (r'(\s+)if ([^:]+?):\n(\s*)return', r'\1if \2:\n\1    return'),
            (r'(\s+)if ([^:]+?):\n(\s*)raise', r'\1if \2:\n\1    raise'),
        ]
        
        for pattern, replacement in patterns:
            fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.MULTILINE)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Fixed indentation in {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


if __name__ == "__main__":
    fix_base_plugin_file()
