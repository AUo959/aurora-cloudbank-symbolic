#!/usr/bin/env python3
"""
Quick fix for missing closing braces in Python files
"""
import os


def fix_missing_braces(filepath):
    """Fix missing closing braces in Python dictionaries"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Common pattern: dictionary definition with missing closing brace
    # Look for patterns like:
    # something = {
    #     'key': 'value',
    #     'key2': 'value2'
    #
    # followed by a line that should close the dict

    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)

        # Check if this line starts a dictionary that might be missing a closing brace
        if (line.strip().endswith(' = {') or
                line.strip().endswith('= {')):

            # Find the matching closing brace or where it should be
            j = i + 1
            indent_level = len(line) - len(line.lstrip())
            open_braces = 1

            while j < len(lines) and open_braces > 0:
                next_line = lines[j]

                # Skip empty lines and comments
                if not next_line.strip() or next_line.strip().startswith('#'):
                    fixed_lines.append(next_line)
                    j += 1
                    continue

                # Count braces
                open_braces += next_line.count('{')
                open_braces -= next_line.count('}')

                # If we find a line that starts at the same or lesser indentation
                # and we still have open braces, we need to close the dict
                next_indent = len(next_line) - len(next_line.lstrip())

                if (next_indent <= indent_level and
                    open_braces > 0 and
                    not next_line.strip().startswith('}') and
                    next_line.strip() and
                        not next_line.strip().startswith("'")):

                    # Add closing brace before this line
                    fixed_lines.append(' ' * (indent_level + 4) + '}')
                    open_braces = 0
                    # Don't increment j, we want to process this line normally
                    break
                else:
                    fixed_lines.append(next_line)
                    j += 1

            i = j
        else:
            i += 1

    # Write back the fixed content
    with open(filepath, 'w') as f:
        f.write('\n'.join(fixed_lines))

    print(f"Fixed: {filepath}")


# Fix the problematic files
files_to_fix = [
    '/workspaces/aurora-cloudbank-symbolic/src/output/multi_modal_output_coordination.py'
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        fix_missing_braces(filepath)
    else:
        print(f"File not found: {filepath}")

print("Done!")
