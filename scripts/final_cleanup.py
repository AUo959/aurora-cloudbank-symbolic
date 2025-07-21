#!/usr/bin/env python3
"""
Final Cleanup Pass - Address Remaining Issues
============================================

Comprehensive fix for remaining linting issues.
"""

import os
import re
import sys
from pathlib import Path

def fix_logging_fstrings(file_path: str) -> bool:
    """Fix f-string interpolation in logging calls."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Simple fix: just remove f from f-strings in logging calls for now
    patterns = [
        (r'\.info\(f"([^"]+)"\)', r'.info("\1")'),
        (r'\.error\(f"([^"]+)"\)', r'.error("\1")'),
        (r'\.warning\(f"([^"]+)"\)', r'.warning("\1")'),
        (r'\.debug\(f"([^"]+)"\)', r'.debug("\1")'),
    ]

    for pattern, replacement in patterns:
        # Only replace if no { } brackets (no actual interpolation)
        matches = re.finditer(pattern, content)
        for match in matches:
            if "{" not in match.group(1) and "}" not in match.group(1):
                content = content.replace(
                    match.group(0), replacement.replace(r"\1", match.group(1))
                )

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

def fix_unused_variables(file_path: str) -> bool:
    """Fix unused variables by prefixing with underscore."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix specific unused variables
    patterns = [
        (r"(\s+)task_info = ", r"\1_task_info = "),
        (r"(\s+)dirnames = ", r"\1_dirnames = "),
        (r"(\s+)file_hash = ", r"\1_file_hash = "),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

def fix_line_lengths(file_path: str) -> bool:
    """Fix long lines by breaking them up."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    original_lines = lines[:]
    fixed_lines = []

    for line in lines:
        if len(line.strip()) > 120:
            # Simple fix: try to break at obvious points
            if "subprocess.run([" in line and len(line, shell=False, check=False) > 120:
                # Break subprocess calls
                indent = len(line) - len(line.lstrip())
                parts = line.split("subprocess.run([", shell=False, check=False)
                if len(parts) == 2:
                    fixed_lines.append(
                        parts[0] + "subprocess.run([\n", shell=False, check=False
                    )
                    fixed_lines.append(" " * (indent + 4) + parts[1])
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    if fixed_lines != original_lines:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)
        return True
    return False

def clean_unused_imports(file_path: str) -> bool:
    """Remove unused imports more carefully."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    lines = content.split("\n")

    # Remove specific unused imports
    import_removals = [
        ("import os", "os."),
        ("import json", "json."),
        ("import pickle", "pickle."),
        ("from typing import List", "List["),
        ("from typing import Tuple", "Tuple["),
        ("from typing import Any", "Any"),
    ]

    for import_line, usage_pattern in import_removals:
        if import_line in content:
            # Check if the import is actually used
            content_without_import = content.replace(import_line, "")
            if usage_pattern not in content_without_import:
                # Remove the import line
                lines = [line for line in lines if line.strip() != import_line.strip()]

    new_content = "\n".join(lines)
    if new_content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

def process_file_final(file_path: str) -> dict:
    """Process a file with final cleanup fixes."""
    fixes = {}

    try:
        fixes["logging_fstrings"] = fix_logging_fstrings(file_path)
        fixes["unused_variables"] = fix_unused_variables(file_path)
        fixes["line_lengths"] = fix_line_lengths(file_path)
        fixes["unused_imports"] = clean_unused_imports(file_path)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}

    return fixes

def main():
    """Main function to process all Python files."""
    scripts_dir = Path("scripts")

    if not scripts_dir.exists():
        print("Scripts directory not found!")
        return 1

    python_files = list(scripts_dir.glob("*.py"))
    total_fixes = {}

    for py_file in python_files:
        print(f"Processing {py_file}...")
        file_fixes = process_file_final(str(py_file))

        for fix_type, applied in file_fixes.items():
            if fix_type not in total_fixes:
                total_fixes[fix_type] = 0
            if applied:
                total_fixes[fix_type] += 1

    print("\nFinal Cleanup Summary:")
    print("=" * 40)
    for fix_type, count in total_fixes.items():
        print(f"{fix_type.replace('_', ' ').title()}: {count} files")

    print(f"\nProcessed {len(python_files)} Python files.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
