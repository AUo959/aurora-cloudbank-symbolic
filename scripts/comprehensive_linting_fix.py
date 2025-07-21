#!/usr/bin/env python3
"""
Comprehensive Linting Fix Script
Automated fixes for Python code quality issues
"""

import os
import re
import subprocess

def fix_trailing_whitespace(file_path):
    """Remove trailing whitespace from all lines"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove trailing whitespace from each line
        lines = content.split('\n')
        fixed_lines = [line.rstrip() for line in lines]
        fixed_content = '\n'.join(fixed_lines)

        # Ensure single newline at end of file
        if fixed_content and not fixed_content.endswith('\n'):
            fixed_content += '\n'

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        return True
    except Exception as e:
        print(f"Error fixing whitespace in {file_path}: {e}")
        return False

def fix_indentation_errors(file_path):
    """Fix common indentation issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # Fix common indentation continuation issues (E128)
            if line.strip() and i > 0:
                prev_line = lines[i-1].rstrip()

                # Handle hanging indents for function calls/definitions
                if (prev_line.endswith('(') or prev_line.endswith(',') or
                        'def ' in prev_line or 'class ' in prev_line):

                    # Ensure proper continuation indentation
                    if line.startswith(' ') and not line.startswith('    '):
                        # Convert tabs to spaces and fix indentation
                        line = line.expandtabs(4)
                        if line.strip():
                            leading_spaces = len(line) - len(line.lstrip())
                            if leading_spaces % 4 != 0:
                                # Round up to nearest multiple of 4
                                new_indent = ((leading_spaces + 3) // 4) * 4
                                line = ' ' * new_indent + line.lstrip()

            fixed_lines.append(line)

        fixed_content = '\n'.join(fixed_lines)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        return True
    except Exception as e:
        print(f"Error fixing indentation in {file_path}: {e}")
        return False

def fix_f_string_issues(file_path):
    """Fix f-string formatting issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix f-string without expressions (F541)
        # Replace f"string" with "string" when no {} expressions
        content = re.sub(r'f(["\'])([^"\'{}]*?)\1', r'\1\2\1', content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"Error fixing f-strings in {file_path}: {e}")
        return False

def fix_line_length_issues(file_path):
    """Fix line length issues (E501)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            if len(line) > 88:  # PEP 8 recommends 79, but we'll use 88 for Black compatibility
                # Try to break long lines at logical points
                if ' = ' in line and len(line.split(' = ')) == 2:
                    # Assignment statements
                    left, right = line.split(' = ', 1)
                    indent = len(line) - len(line.lstrip())
                    if len(right) > 60:
                        fixed_lines.append(f"{left} = (")
                        fixed_lines.append(f"{' ' * (indent + 4)}{right}")
                        fixed_lines.append(f"{' ' * indent})")
                        continue
                elif '(' in line and ')' in line:
                    # Function calls - already handled by indentation
                    pass

            fixed_lines.append(line)

        fixed_content = '\n'.join(fixed_lines)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        return True
    except Exception as e:
        print(f"Error fixing line lengths in {file_path}: {e}")
        return False

def run_autopep8(file_path):
    """Run autopep8 for automated fixes"""
    try:
        subprocess.run([
            'python3', '-m', 'autopep8', '--in-place', '--aggressive',
            '--max-line-length=88', str(file_path)
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        print(f"autopep8 not available for {file_path}")
        return False
    except Exception as e:
        print(f"Error running autopep8 on {file_path}: {e}")
        return False

def fix_python_file(file_path):
    """Apply all fixes to a Python file"""
    print(f"Fixing {file_path}...")

    success = True

    # Apply fixes in order
    success &= fix_trailing_whitespace(file_path)
    success &= fix_f_string_issues(file_path)
    success &= fix_indentation_errors(file_path)
    success &= fix_line_length_issues(file_path)

    # Try autopep8 as final pass
    run_autopep8(file_path)

    return success

def main():
    """Main execution"""
    print("🔧 Comprehensive Python Linting Fix")
    print("=" * 40)

    # Find Python files with issues
    problem_files = [
        'tools/workflow/aurora_failure_prevention_system.py',
        'tools/workflow/aurora_workflow_optimization_manager.py',
        'tools/workflow/aurora_intelligent_workflow_manager.py',
        '.security/secure_helpers.py',
        'scripts/aurora_security_scanner.py'
    ]

    fixed_count = 0
    error_count = 0

    for file_path in problem_files:
        if os.path.exists(file_path):
            if fix_python_file(file_path):
                fixed_count += 1
            else:
                error_count += 1
        else:
            print(f"File not found: {file_path}")
            error_count += 1

    print(f"\n✅ Fixed: {fixed_count} files")
    print(f"❌ Errors: {error_count} files")

    # Run final validation
    print("\n🔍 Running final validation...")
    try:
        result = subprocess.run([
            'python3', '-m', 'flake8', '--count', '--statistics',
            'tools/workflow/', '.security/', 'scripts/aurora_security_scanner.py'
        ], capture_output=True, text=True, check=False)

        if result.returncode == 0:
            print("✅ All linting issues resolved!")
        else:
            remaining_issues = result.stdout.count('\n') if result.stdout else 0
            print(f"⚠️ {remaining_issues} issues remaining")
            if result.stdout:
                print("Remaining issues:")
                print(result.stdout[:1000])  # Show first 1000 chars
    except Exception as e:
        print(f"Could not run final validation: {e}")

if __name__ == "__main__":
    main()
