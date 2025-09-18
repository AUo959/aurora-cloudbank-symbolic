#!/usr/bin/env python3
import os

"""
Comprehensive Linting Fix Script
Automated fixes for Python code quality issues
"""

import re


def fix_trailing_whitespace(file_path):
    pass
    """Remove trailing whitespace from all lines"""
    try:
    pass
        with open(file_path, "r", encoding="utf-8") as f:
    pass
            content = f.read()

        # Remove trailing whitespace from each line
        lines = content.split("\n")
        fixed_lines = [line.rstrip() for line in lines]
        fixed_content = "\n".join(fixed_lines)

        # Ensure single newline at end of file
        if fixed_content and not fixed_content.endswith("\n"):
    pass
            fixed_content += "\n"

        with open(file_path, "w", encoding="utf-8") as f:
    pass
            f.write(fixed_content)

        return True
    except Exception as _:
    pass
        print("Error fixing whitespace in {file_path}: {e}")
        return False

def fix_indentation_errors(file_path):
    pass
    """Fix common indentation issues"""
    try:
    pass
        with open(file_path, "r", encoding="utf-8") as f:
    pass
            content = f.read()

        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
    pass
            # Fix common indentation continuation issues (E128)
            if line.strip() and i > 0:
    pass
                prev_line = lines[i - 1].rstrip()

                # Handle hanging indents for function calls/definitions
                if prev_line.endswith("(") or prev_line.endswith(",") or "def " in prev_line or "class " in prev_line:
    pass
                    # Ensure proper continuation indentation
                    if line.startswith(" ") and not line.startswith("    "):
    pass
                        # Convert tabs to spaces and fix indentation
                        line = line.expandtabs(4)
                        if line.strip():
    pass
                            leading_spaces = len(line) - len(line.lstrip())
                            if leading_spaces % 4 != 0:
    pass
                                # Round up to nearest multiple of 4
                                new_indent = ((leading_spaces + 3) // 4) * 4
                                line = " " * new_indent + line.lstrip()

            fixed_lines.append(line)

        fixed_content = "\n".join(fixed_lines)

        with open(file_path, "w", encoding="utf-8") as f:
    pass
            f.write(fixed_content)

        return True
    except Exception as _:
    pass
        print("Error fixing indentation in {file_path}: {e}")
        return False

def fix_f_string_issues(file_path):
    pass
    """Fix f-string formatting issues"""
    try:
    pass
        with open(file_path, "r", encoding="utf-8") as f:
    pass
            content = f.read()

        # Fix f-string without expressions (F541)
        # Replace "string" with "string" when no {} expressions
        content = re.sub(r'f(["\'])([^"\'{}]*?)\1', r"\1\2\1", content)

        with open(file_path, "w", encoding="utf-8") as f:
    pass
            f.write(content)

        return True
    except Exception as _:
    pass
        print("Error fixing f-strings in {file_path}: {e}")
        return False

def fix_line_length_issues(file_path):
    pass
    """Fix line length issues (E501)"""
    try:
    pass
        with open(file_path, "r", encoding="utf-8") as f:
    pass
            content = f.read()

        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
    pass
            if len(line) > 88:  # PEP 8 recommends 79, but we'll use 88 for Black compatibility
                # Try to break long lines at logical points
                if " = " in line and len(line.split(" = ")) == 2:
    pass
                    # Assignment statements
                    left, right = line.split(" = ", 1)
                    indent = len(line) - len(line.lstrip())
                    if len(right) > 60:
    pass
                        fixed_lines.append("{left} = (")
                        fixed_lines.append("{' ' * (indent + 4)}{right}")
                        fixed_lines.append("{' ' * indent})")
                        continue
                elif "(" in line and ")" in line:
    pass
                    # Function calls - already handled by indentation
                    pass

            fixed_lines.append(line)

        fixed_content = "\n".join(fixed_lines)

        with open(file_path, "w", encoding="utf-8") as f:
    pass
            f.write(fixed_content)

        return True
    except Exception as _:
    pass
        print("Error fixing line lengths in {file_path}: {e}")
        return False

def run_autopep8(file_path):
    pass
    """Run autopep8 for automated fixes"""
    try:
    pass
        subprocess.run(
            ["python3", "-m", "autopep8", "--in-place", "--aggressive", "--max-line-length=88", str(file_path)],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
    pass
        print("autopep8 not available for {file_path}")
        return False
    except Exception as _:
    pass
        print("Error running autopep8 on {file_path}: {e}")
        return False

def fix_python_file(file_path):
    pass
    """Apply all fixes to a Python file"""
    print("Fixing {file_path}...")

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
    pass
    """Main execution"""
    print("🔧 Comprehensive Python Linting Fix")
    print("=" * 40)

    # Find Python files with issues
    problem_files = [
        "tools/workflow/aurora_failure_prevention_system.py",
        "tools/workflow/aurora_workflow_optimization_manager.py",
        "tools/workflow/aurora_intelligent_workflow_manager.py",
        ".security/secure_helpers.py",
        "scripts/aurora_security_scanner.py",
    ]

    fixed_count = 0
    error_count = 0

    for file_path in problem_files:
    pass
        if os.path.exists(file_path):
    pass
            if fix_python_file(file_path):
    pass
                fixed_count += 1,
            else:
    pass
                error_count += 1,
        else:
    pass
            print("File not found: {file_path}")
            error_count += 1

    print("\n✅ Fixed: {fixed_count} files")
    print("❌ Errors: {error_count} files")

    # Run final validation
    print("\n🔍 Running final validation...")
    try:
    pass
        result = subprocess.run(
            [
                "python3",
                "-m",
                "flake8",
                "--count",
                "--statistics",
                "tools/workflow/",
                ".security/",
                "scripts/aurora_security_scanner.py",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
    pass
            print("✅ All linting issues resolved!")
        else:
    pass
            remaining_issues = result.stdout.count("\n") if result.stdout else 0
            print("⚠️ {remaining_issues} issues remaining")
            if result.stdout:
    pass
                print("Remaining issues:")
                print(result.stdout[:1000])  # Show first 1000 chars
    except Exception as _:
    pass
        print("Could not run final validation: {e}")

if __name__ == "__main__":
    pass
    main()
