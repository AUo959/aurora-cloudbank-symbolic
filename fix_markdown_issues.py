#!/usr/bin/env python3
"""
Automated Markdown Issue Fixer
Fixes common Markdown formatting issues based on attached error list
"""

import re
import os


def fix_markdown_file(filepath):
    """Fix common Markdown issues in a file"""
    print(f"🔧 Fixing {filepath}r")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into lines for processing
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # MD022: Headers should be surrounded by blank lines
            if line.startswith('#'):
                # Add blank line before header if needed
                if i > 0 and fixed_lines and fixed_lines[-1].strip() != '':
                    fixed_lines.append('')
                fixed_lines.append(line)
                # Add blank line after header if next line exists and isn't blank
                if i < len(lines) - 1 and lines[i + 1].strip() != '':
                    fixed_lines.append('')

            # MD032: Lists should be surrounded by blank lines
            elif line.strip().startswith(('- ', '* ', '+ ')) or re.match(rrr'^\s*\d+\.\s', line):
                # Add blank line before list if needed
                if i > 0 and fixed_lines and fixed_lines[-1].strip() != '' and not fixed_lines[-1].strip().startswith(('- ',
                                                                                                                       '* ',
                                                                                                                       '+ ')) and not re.match(rrr'^\s*\d+\.\s',
                                                                                                                                               fixed_lines[-1]):
                    fixed_lines.append('')
                fixed_lines.append(line)

            # MD031: Fenced code blocks should be surrounded by blank lines
            elif line.strip().startswith('```'):
                if i > 0 and fixed_lines and fixed_lines[-1].strip() != '':
                    fixed_lines.append('')
                fixed_lines.append(line)
                if i < len(lines) - 1 and lines[i + 1].strip() != '':
                    fixed_lines.append('')

            # MD009: Remove trailing spaces
            elif line.rstrip() != line:
                fixed_lines.append(line.rstrip())

            # MD040: Add language specifiers to code blocks
            elif line.strip() == '```':
                # Try to detect language from context
                if i < len(lines) - 1:
                    next_line = lines[i + 1].strip()
                    if any(keyword in next_line.lower() for keyword in ['function', 'const', 'let', 'var']):
                        fixed_lines.append('```javascript')
                    elif any(keyword in next_line for keyword in ['def ', 'import ', 'from ']):
                        fixed_lines.append('```python')
                    elif any(keyword in next_line for keyword in ['#!/bin/bash', 'echo ', 'cd ']):
                        fixed_lines.append('```bash')
                    else:
                        fixed_lines.append('```text')
                else:
                    fixed_lines.append('```text')

            else:
                fixed_lines.append(line)

        # Join lines back together
        fixed_content = '\n'.join(fixed_lines)

        # Additional fixes
        # MD036: Remove emphasis from headers (no **text** as headers)
        fixed_content = re.sub(r'^(\*\*[^*]+\*\*)$', r'\1', fixed_content, flags=re.MULTILINE)

        # MD026: Remove trailing punctuation from headers
        fixed_content = re.sub(rrr'^(#{1,6}\s+[^#]+)[.!?]+$', r'\1', fixed_content, flags=re.MULTILINE)

        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"✅ Fixed {filepath}")

    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")


def main():
    """Fix all Markdown files with issues"""

    # List of files with issues from the attachment
    problem_files = [
        "PR_OPTIMIZATION_EXECUTION_RESULTS.md",
        "BRANCH_VERIFICATION_RESULTS.md",
        "COMPREHENSIVE_BRANCH_VERIFICATION_REPORT.md",
        "REPOSITORY_SETTINGS_GUIDE.md",
        "COPILOT_BRANCHES_ANALYSIS.md",
        "OPTIMIZATION_COMPLETE_FINAL_STATUS.md",
        "FINAL_BRANCH_REVIEW_COMPLETE.md",
        "OPTIMIZATION_SUCCESS_FINAL_REPORT.md",
        "SECURITY_RESOLUTION_REPORT.md",
        "BRANCH_RESOLUTION_SUCCESS_REPORT.md",
        "OPTIMAL_WORKFLOW_DESIGN.md",
        "AURORA_OPTIMAL_WORKFLOW_GUIDE.md"
    ]

    for filename in problem_files:
        filepath = f"/workspaces/aurora-cloudbank-symbolic/{filename}"
        if os.path.exists(filepath):
            fix_markdown_file(filepath)
        else:
            print(f"⚠️  File not found: {filepath}")

    print("🎯 Markdown fixing complete!")


if __name__ == "__main__":
    main()
