#!/usr/bin/env python3
"""
Automated Print Formatting Fixer
Converts incorrect print("...%s", var) to f-strings print(f"...{var}")
"""

import re
import os
import sys
from pathlib import Path
from typing import List, Tuple

class PrintFormattingFixer:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.files_modified = 0
        self.total_fixes = 0
        self.errors = []

    def fix_line(self, line: str) -> Tuple[str, int]:
        """Fix a single line's print formatting issues."""
        fixes_made = 0
        original_line = line

        # Pattern to match print("...", var1, var2, ...) where string contains %s
        # This handles both single and double quotes
        pattern = r'print\((["\'])([^"\']*?)\1,\s*(.+?)\)(?=\s*(?:#|$))'

        def replace_print(match):
            nonlocal fixes_made
            quote = match.group(1)
            format_str = match.group(2)
            args_str = match.group(3)

            # Count %s in format string
            percent_s_count = format_str.count('%s')

            if percent_s_count == 0:
                # No %s, return as-is
                return match.group(0)

            # Split arguments
            args = self._split_args(args_str)

            if len(args) != percent_s_count:
                # Mismatch - skip this one
                return match.group(0)

            # Build f-string
            result = format_str
            for arg in args:
                # Replace first %s with {arg}
                result = result.replace('%s', '{' + arg.strip() + '}', 1)

            fixes_made += 1
            return f'print(f"{result}")'

        # Apply the fix
        fixed_line = re.sub(pattern, replace_print, line)

        return fixed_line, fixes_made

    def _split_args(self, args_str: str) -> List[str]:
        """Split comma-separated arguments, respecting parentheses and quotes."""
        args = []
        current = ""
        paren_depth = 0
        in_string = False
        string_char = None

        for char in args_str:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
                current += char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
                current += char
            elif char == '(' and not in_string:
                paren_depth += 1
                current += char
            elif char == ')' and not in_string:
                paren_depth -= 1
                current += char
            elif char == ',' and paren_depth == 0 and not in_string:
                args.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            args.append(current.strip())

        return args

    def fix_file(self, filepath: str) -> bool:
        """Fix all print formatting issues in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            modified = False
            new_lines = []
            file_fixes = 0

            for line in lines:
                fixed_line, fixes = self.fix_line(line)
                new_lines.append(fixed_line)
                if fixes > 0:
                    modified = True
                    file_fixes += fixes

            if modified:
                if not self.dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)

                self.files_modified += 1
                self.total_fixes += file_fixes
                return True

            return False

        except Exception as e:
            self.errors.append(f"{filepath}: {e}")
            return False

    def scan_and_fix(self, target_files: List[str] = None):
        """Scan and fix files."""
        if target_files:
            files_to_fix = target_files
        else:
            # Scan all Python files
            files_to_fix = []
            for root, dirs, files in os.walk('.'):
                skip_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.backup', 'extractions'}
                dirs[:] = [d for d in dirs if d not in skip_dirs]

                for file in files:
                    if file.endswith('.py'):
                        files_to_fix.append(os.path.join(root, file))

        print(f"{'🔍 DRY RUN' if self.dry_run else '🔧 FIXING'} - Print Formatting Issues")
        print("=" * 70)
        print(f"Files to scan: {len(files_to_fix)}")
        print()

        for filepath in files_to_fix:
            before_count = self.total_fixes
            if self.fix_file(filepath):
                fixes = self.total_fixes - before_count
                status = "Would fix" if self.dry_run else "Fixed"
                print(f"  ✓ {status} {fixes:2d} issues - {filepath}")

        print()
        print("=" * 70)
        print(f"📊 Summary:")
        print(f"  Files modified: {self.files_modified}")
        print(f"  Total fixes: {self.total_fixes}")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  - {error}")

        return self.total_fixes > 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Fix print() formatting issues')
    parser.add_argument('--apply', action='store_true', help='Apply fixes (default is dry-run)')
    parser.add_argument('--files', nargs='+', help='Specific files to fix')
    parser.add_argument('--top', type=int, help='Fix only top N files with most issues')

    args = parser.parse_args()

    # Determine which files to fix
    target_files = None
    if args.files:
        target_files = args.files
    elif args.top:
        # Get top N files with most issues
        print(f"🔍 Identifying top {args.top} files with most issues...")
        # Run analysis to get file list
        import subprocess
        result = subprocess.run(
            ['python3', '-c', '''
import re
import os
from collections import defaultdict

pattern = re.compile(r"print\\(([\\"\'])([^\\"\']*?%s[^\\"\']*?)\\1,\\s*(.+?)\\)")
issues_by_file = defaultdict(list)

for root, dirs, files in os.walk("."):
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".backup", "extractions"}
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    if matches:
                        issues_by_file[filepath] = len(matches)
            except:
                pass

sorted_files = sorted(issues_by_file.items(), key=lambda x: x[1], reverse=True)
for filepath, count in sorted_files[:''' + str(args.top) + ''']:
    print(filepath)
'''],
            capture_output=True,
            text=True
        )
        target_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        print(f"  Found {len(target_files)} files to fix")
        print()

    fixer = PrintFormattingFixer(dry_run=not args.apply)
    fixer.scan_and_fix(target_files)

    if fixer.total_fixes > 0 and not args.apply:
        print()
        print("💡 To apply these fixes, run with --apply flag")
        print(f"   Example: python {sys.argv[0]} --apply")


if __name__ == '__main__':
    main()
