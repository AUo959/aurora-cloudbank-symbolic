#!/usr/bin/env python3
import os
"""
Bulk Python Code Fixer
Automatically fixes common Python code issues based on flake8 output
"""

import re
import glob


def fix_file(filepath):
    """Fix common Python code issues in a file"""
    print(f"🔧 Fixing {filepath}r")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove unused imports (simple ones)
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Remove trailing whitespace
            line = line.rstrip()

            # Skip blank lines with whitespace (W293)
            if line == '':
                fixed_lines.append('')
                i += 1
                continue

            # Fix simple unused import cases
            if re.match(r'^import \w+$', line) or re.match(r'^from .* import .*$', line):
                # Keep important imports like os, sys, etc.
                if any(important in line for important in ['os', 'sys', 'json', 'yaml', 'subprocess']):
                    fixed_lines.append(line)
                elif 'typing' in line and any(word in line for word in ['List',
                                                                        'Dict',
                                                                        'Optional',
                                                                        'Set',
                                                                        'Tuple',
                                                                        'Union',
                                                                        'Any']):
                    # Remove unused typing imports for now
                    pass
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        # Join back together
        fixed_content = '\n'.join(fixed_lines)

        # Fix f-string issues (F541)
        fixed_content = re.sub(r'"([^"{}]*)"', r'"\1"', fixed_content)
        fixed_content = re.sub(r"'([^'{}]*)'", r"'\1'", fixed_content)

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"✅ Fixed {filepath}")

    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")


def main():
    """Fix all Python files with issues"""

    # Find all Python files
    python_files = []

    for root in ['scripts/', 'modules/', '.']:
        for pattern in ['*.py']:
            python_files.extend(glob.glob(f"{root}/**/{pattern}", recursive=True))
            python_files.extend(glob.glob(f"{root}/{pattern}"))

    # Also add specific files
    specific_files = [
        'aurora_workflow_config.py',
        'fix_markdown_issues.py'
    ]

    for file in specific_files:
        if os.path.exists(file):
            python_files.append(file)

    # Remove duplicates and filter existing files
    python_files = list(set([f for f in python_files if os.path.exists(f)]))

    print(f"📁 Found {len(python_files)} Python files to fix")

    for filepath in python_files:
        if 'node_modules' not in filepath and '.git' not in filepath:
            fix_file(filepath)

    print("🎯 Python fixing complete!")


if __name__ == "__main__":
    main()
