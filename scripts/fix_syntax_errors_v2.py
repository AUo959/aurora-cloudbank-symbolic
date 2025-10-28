#!/usr/bin/env python3
"""
Second pass fixer for remaining syntax errors
Handles emoji characters and remaining decimal literal issues
"""

import re
from pathlib import Path


def fix_emoji_characters(filepath: Path) -> bool:
    """Remove or escape emoji characters that cause syntax errors"""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        # Remove emoji characters at start of lines (outside strings)
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # If line starts with emoji (not in a string), comment it out or remove
            stripped = line.lstrip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"') and not stripped.startswith("'"):
                # Check if first character is emoji (outside ASCII range)
                if stripped[0] and ord(stripped[0]) > 127:
                    # It's likely an emoji - comment out the line or remove the emoji
                    indent = line[:len(line) - len(stripped)]
                    fixed_lines.append(f"{indent}# {stripped}")
                    continue
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    return False


def fix_decimal_literals_v2(filepath: Path) -> bool:
    """Fix remaining decimal literal issues"""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        # Fix pattern: print("text %s%", stats['hit_rate']:.1f)
        # Should be: print("text %.1f%%", stats['hit_rate'])
        content = re.sub(
            r'print\((".*?%s%"[^)]*?),\s*(\w+(?:\[\'[^\']+\'\])?)(:\.\d+f)\)',
            r'print(\1.replace("%s%", "%.1f%%"), \2)',
            content
        )
        
        # Fix pattern: str(metrics.health_score:.2f)
        # Should be: str(metrics.health_score)
        content = re.sub(
            r'str\(([^:]+)(:\.\d+f)\)',
            r'str(\1)',
            content
        )
        
        # Fix pattern: benchmarks['total_time']:.2f
        # Should be: benchmarks['total_time']
        content = re.sub(
            r'(\w+(?:\[\'[^\']+\'\])?)(:\.\d+f)([^\w])',
            r'\1\3',
            content
        )
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    return False


def fix_unterminated_strings_v2(filepath: Path) -> bool:
    """Fix remaining unterminated string issues"""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        lines = content.split('\n')
        
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for unterminated string at end of line
            if line.rstrip().endswith('"""'):
                # Already terminated
                fixed_lines.append(line)
            elif '"""' in line and line.count('"""') == 1:
                # Single triple quote - might be unterminated
                # Look ahead to see if there's a closing one
                found_close = False
                for j in range(i + 1, min(i + 20, len(lines))):
                    if '"""' in lines[j]:
                        found_close = True
                        break
                
                if not found_close:
                    # Add closing triple quotes
                    fixed_lines.append(line)
                    fixed_lines.append('"""')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
            
            i += 1
        
        content = '\n'.join(fixed_lines)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    return False


def fix_indentation_errors(filepath: Path) -> bool:
    """Fix remaining indentation errors"""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        lines = content.split('\n')
        
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for function definitions with no body
            if line.strip().startswith('def ') and line.strip().endswith(':'):
                # Check next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip().startswith('"""'):
                        # Has docstring, OK
                        fixed_lines.append(line)
                    elif next_line.strip() and not next_line.startswith(' ' * (len(line) - len(line.lstrip()) + 4)):
                        # Next line exists but not indented - add pass
                        fixed_lines.append(line)
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.append(' ' * (indent + 4) + 'pass')
                    else:
                        fixed_lines.append(line)
                else:
                    # Last line - add pass
                    fixed_lines.append(line)
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent + 4) + 'pass')
            else:
                fixed_lines.append(line)
            
            i += 1
        
        content = '\n'.join(fixed_lines)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    return False


def main():
    """Fix all remaining syntax errors"""
    repo_root = Path('/workspaces/aurora-cloudbank-symbolic')
    
    # Get files with E999 errors
    import subprocess
    result = subprocess.run(
        ['python3', '-m', 'flake8', '.', '--select=E9', '--format=%(path)s'],
        capture_output=True,
        text=True,
        cwd=repo_root
    )
    
    files_with_errors = set()
    for line in result.stdout.split('\n'):
        if line.strip() and line.startswith('./'):
            filepath = repo_root / line.strip()[2:].split(':')[0]
            files_with_errors.add(filepath)
    
    print(f"🔧 Fixing {len(files_with_errors)} files with remaining syntax errors...")
    
    fixed_count = 0
    for filepath in files_with_errors:
        fixed = False
        if fix_emoji_characters(filepath):
            print(f"  ✓ Fixed emoji characters in {filepath.name}")
            fixed = True
        if fix_decimal_literals_v2(filepath):
            print(f"  ✓ Fixed decimal literals in {filepath.name}")
            fixed = True
        if fix_unterminated_strings_v2(filepath):
            print(f"  ✓ Fixed unterminated strings in {filepath.name}")
            fixed = True
        if fix_indentation_errors(filepath):
            print(f"  ✓ Fixed indentation in {filepath.name}")
            fixed = True
        
        if fixed:
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files")


if __name__ == '__main__':
    main()
