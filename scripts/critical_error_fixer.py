# !/usr/bin/env python3
from pathlib import Path
from typing import List
import subprocess
import sys
"""
Critical Error Fixer - Repair Broken Scripts
==========================================

Fixes critical undefined variable errors caused by overly aggressive lint fixes.
"""

import re
import sys
from pathlib import Path


def fix_undefined_result_variables(file_path: str) -> bool:
    """Fix undefined 'result' variables in subprocess calls."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Pattern to find where result is used but not defined
    lines = content.split("\n")
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for subprocess calls that were changed to '_'
        if "_ = subprocess.run(" in line:
            # Change back to result =
            line = line.replace(
                "_ = subprocess.run(",
                "result = subprocess.run(",
                shell=False,
                check=False,
            )

        # Look for other subprocess patterns
        elif "_scheduler_thread = " in line:
            line = line.replace("_scheduler_thread = ", "scheduler_thread = ")

        fixed_lines.append(line)
        i += 1

    new_content = "\n".join(fixed_lines)

    if new_content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def fix_syntax_errors(file_path: str) -> bool:
    """Fix obvious syntax errors."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix common syntax issues
    patterns = [
        # Fix malformed exception handling
        (
            r"except \(OSError, ValueError, RuntimeError\) as e:",
            "except (OSError, ValueError, RuntimeError) as e:",
        ),
        (
            r"except \(OSError, ValueError, RuntimeError\):",
            "except (OSError, ValueError, RuntimeError):",
        ),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def add_missing_imports(file_path: str) -> bool:
    """Add missing critical imports."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Check for yaml usage without import
    if "yaml." in content and "import yaml" not in content:
        # Find import section and add yaml
        lines = content.split("\n")
        import_section_end = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_section_end = i + 1

        if import_section_end > 0:
            lines.insert(import_section_end, "import yaml")
            content = "\n".join(lines)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def remove_unused_imports(file_path: str) -> bool:
    """Remove unused imports that are causing warnings."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Remove obvious unused imports
    patterns = [
        (r"import pickle\n" if "pickle." not in content.replace("import pickle", "") else None),
        r"from typing import.*List.*\n" if "List[" not in content else None,
    ]

    for pattern in patterns:
        if pattern and pattern in content:
            content = content.replace(pattern, "")

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def process_file_critical(file_path: str) -> dict:
    """Process a single Python file with critical fixes."""
    fixes = {}

    try:
        fixes["undefined_result"] = fix_undefined_result_variables(file_path)
        fixes["syntax_errors"] = fix_syntax_errors(file_path)
        fixes["missing_imports"] = add_missing_imports(file_path)
        fixes["unused_imports"] = remove_unused_imports(file_path)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}

    return fixes


def main():
    """Main function to process problematic Python files."""
    scripts_dir = Path("scripts")

    if not scripts_dir.exists():
        print("Scripts directory not found!")
        return 1

    # Focus on the most problematic files first
    problem_files = [
        "aurora_maintenance_scheduler.py",
        "maintenance_scheduler.py",
        "aurora_health_monitor.py",
        "health_monitor.py",
        "aurora_branch_manager.py",
        "branch_cleanup_automation.py",
        "automated_branch_cleanup.py",
        "repository_health_monitor.py",
        "precommit_optimizer.py",
        "branch_cleanup.py",
    ]

    total_fixes = {}

    for filename in problem_files:
        file_path = scripts_dir / filename
        if file_path.exists():
            print(f"Processing {file_path}...")
            file_fixes = process_file_critical(str(file_path))

            for fix_type, applied in file_fixes.items():
                if fix_type not in total_fixes:
                    total_fixes[fix_type] = 0
                if applied:
                    total_fixes[fix_type] += 1

    print("\nCritical Fix Summary:")
    print("=" * 40)
    for fix_type, count in total_fixes.items():
        print(f"{fix_type.replace('_', ' ').title()}: {count} files")

    print(f"\nProcessed {len(problem_files)} critical Python files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
