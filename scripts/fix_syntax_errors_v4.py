#!/usr/bin/env python3
"""
Fix remaining syntax errors - V4 Enhanced
Handles indentation, malformed print statements, and broken code blocks
"""
import logging

logger = logging.getLogger(__name__)

import re
import subprocess
from pathlib import Path
from typing import List, Set


def get_error_files() -> Set[str]:
    """Get list of files with E9/F63/F7/F82 errors"""
    result = subprocess.run(
        ["python3", "-m", "flake8", ".", "--select=E9,F63,F7,F82", "--format=%(path)s"],
        capture_output=True,
        text=True
    )
    files = set(line.strip() for line in result.stdout.splitlines() if line.strip())
    return files


def fix_indentation_after_try(content: str) -> tuple[str, int]:
    """Fix 'expected an indented block after try' errors"""
    changes = 0
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        
        # If we see a try statement, check if next line is unindented
        if line.strip().startswith('try:'):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Check if next line exists and isn't indented relative to try
                if next_line.strip() and not next_line.startswith(line[:len(line) - len(line.lstrip())] + '    '):
                    # Next line should be indented - if it starts with a valid keyword at same level, insert pass
                    if any(next_line.strip().startswith(kw) for kw in ['cmd =', 'result =', 'def ', 'class ', 'if ', 'for ']):
                        fixed_lines.append(line[:len(line) - len(line.lstrip())] + '    pass  # Placeholder')
                        changes += 1
    
    return '\n'.join(fixed_lines), changes


def fix_broken_print_lines(content: str) -> tuple[str, int]:
    """Fix print statements broken across lines with %s"""
    changes = 0
    
    # Pattern: print("...\n%s", ... split across lines
    # Look for lines ending with %s", followed by content on next line
    pattern = r'(print\(["\'].*?)(%s["\'])\s*,\s*\n\s*(\w+.*?\))'
    
    def replacer(match):
        nonlocal changes
        changes += 1
        prefix = match.group(1)
        fmt_end = match.group(2)
        args = match.group(3)
        # Reconstruct on one line
        return f'{prefix}{fmt_end}, {args}'
    
    content = re.sub(pattern, replacer, content)
    return content, changes


def fix_malformed_print_statements(content: str) -> tuple[str, int]:
    """Fix print statements with standalone %s on a line"""
    changes = 0
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for line that's just: %s", ...
        if re.match(r'^\s*%s["\'],\s*', line) and i > 0:
            # Merge with previous line if it's a print statement
            prev_line = fixed_lines[-1]
            if 'print(' in prev_line or 'print("' in prev_line:
                # Remove the previous line and merge
                fixed_lines.pop()
                # Reconstruct the print statement
                indent = ' ' * (len(prev_line) - len(prev_line.lstrip()))
                merged = prev_line.rstrip() + line.lstrip()
                fixed_lines.append(merged)
                changes += 1
                i += 1
                continue
        
        fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines), changes


def fix_unexpected_indentation(content: str) -> tuple[str, int]:
    """Fix unexpected indentation errors"""
    changes = 0
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if this line has unexpected indentation
        # Look for lines that start with extra spaces and don't follow a colon
        if i > 0 and line and line[0] == ' ':
            prev_line = fixed_lines[-1] if fixed_lines else ''
            
            # If previous line doesn't end with colon and current line is indented more than prev
            if prev_line and not prev_line.rstrip().endswith(':'):
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                curr_indent = len(line) - len(line.lstrip())
                
                # If current is indented more than 4 spaces beyond prev and prev doesn't end with colon
                if curr_indent > prev_indent + 4:
                    # De-indent to match previous line
                    fixed_line = ' ' * prev_indent + line.lstrip()
                    fixed_lines.append(fixed_line)
                    changes += 1
                    continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), changes


def fix_fstring_print_errors(content: str) -> tuple[str, int]:
    """Fix broken f-string print statements"""
    changes = 0
    
    # Fix: print("\n{'=' * 50}") -> print(f"\n{'=' * 50}")
    pattern = r'print\((["\'])([^"\']*\{[^}]+\}[^"\']*)\1\)'
    
    def replacer(match):
        nonlocal changes
        quote = match.group(1)
        text = match.group(2)
        if not text.startswith('f'):
            changes += 1
            return f'print(f{quote}{text}{quote})'
        return match.group(0)
    
    content = re.sub(pattern, replacer, content)
    return content, changes


def fix_unterminated_strings(content: str) -> tuple[str, int]:
    """Fix unterminated string literals"""
    changes = 0
    
    # Look for patterns like: print(" some text without closing quote
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check for print statements with unclosed strings
        if 'print(' in line:
            # Count quotes
            double_quotes = line.count('"') - line.count('\\"')
            single_quotes = line.count("'") - line.count("\\'")
            
            # If odd number of quotes, likely unterminated
            if double_quotes % 2 == 1:
                # Find the last quote and add closing quote before end of statement
                if line.rstrip().endswith(')'):
                    line = line.rstrip()[:-1] + '")'
                else:
                    line = line.rstrip() + '"'
                changes += 1
            elif single_quotes % 2 == 1:
                if line.rstrip().endswith(')'):
                    line = line.rstrip()[:-1] + "')"
                else:
                    line = line.rstrip() + "'"
                changes += 1
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), changes


def process_file(file_path: Path) -> int:
    """Process a single file and return number of fixes applied"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        total_changes = 0
        
        # Apply all fixes in sequence
        content, changes = fix_indentation_after_try(content)
        total_changes += changes
        
        content, changes = fix_broken_print_lines(content)
        total_changes += changes
        
        content, changes = fix_malformed_print_statements(content)
        total_changes += changes
        
        content, changes = fix_unexpected_indentation(content)
        total_changes += changes
        
        content, changes = fix_fstring_print_errors(content)
        total_changes += changes
        
        content, changes = fix_unterminated_strings(content)
        total_changes += changes
        
        # Only write if changes were made
        if total_changes > 0 and content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return total_changes
        
        return 0
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return 0


def main():
    print("🔍 Finding files with syntax errors...")
    error_files = get_error_files()
    print(f"📋 Found {len(error_files)} files with errors\n")
    
    total_fixes = 0
    fixed_files = 0
    
    for file_path_str in sorted(error_files):
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue
        
        print(f"Processing: {file_path}")
        fixes = process_file(file_path)
        
        if fixes > 0:
            fixed_files += 1
            total_fixes += fixes
            print(f"  ✅ Applied {fixes} fix(es)")
        else:
            print(f"  ⏭️  No automatic fixes available")
    
    print(f"\n{'='*60}")
    logger.info("Fixed {fixed_files} files ({total_fixes} total changes)")
    print(f"{'='*60}\n")
    
    # Re-check error count
    result = subprocess.run(
        ["python3", "-m", "flake8", ".", "--select=E9,F63,F7,F82", "--count"],
        capture_output=True,
        text=True
    )
    remaining = result.stdout.strip()
    print(f"📊 Remaining E9 errors: {remaining}")


if __name__ == "__main__":
    main()
