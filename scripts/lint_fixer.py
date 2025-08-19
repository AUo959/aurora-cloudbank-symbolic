#!/usr/bin/env python3
"""
Comprehensive Python Lint Issue Fixer
=====================================

Fixes common Python linting issues that automated tools miss.
"""

import re
import sys
from pathlib import Path


def fix_encoding_specifications(file_path: str) -> bool:
    """Add encoding specification to file open statements."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix open() calls without encoding
    patterns = [
        (r"open\(([^)]+)\)", r'open(\1, encoding="utf-8")'),
        (r'open\(([^,]+),\s*([\'"]r[\'"])\)', r'open(\1, \2, encoding="utf-8")'),
        (r'open\(([^,]+),\s*([\'"]w[\'"])\)', r'open(\1, \2, encoding="utf-8")'),
        (r'open\(([^,]+),\s*([\'"]a[\'"])\)', r'open(\1, \2, encoding="utf-8")r'),
    ]

    for pattern, replacement in patterns:
        # Only apply if encoding not already specified
        if "encoding=" not in content:
            content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def fix_subprocess_calls(file_path: str) -> bool:
    """Add shell=False and check=True to subprocess calls."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix subprocess.run() calls

    def fix_subprocess_run(match):
        args = match.group(1)
        if "shell=" not in args and "check=" not in args:
            return "subprocess.run({args}, shell=False, check=False)"
        return match.group(0)

    def fix_subprocess_call(match):
        args = match.group(1)
        if "shell=" not in args:
            return "subprocess.call({args}, shell=False)"
        return match.group(0)

    patterns = [
        (r"subprocess\.run\(([^)]+)\)", fix_subprocess_run),
        (r"subprocess\.call\(([^)]+)\)", fix_subprocess_call),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def fix_broad_exceptions(file_path: str) -> bool:
    """Replace broad exception catches with specific ones."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Replace bare except (OSError, ValueError, RuntimeError): with except (OSError, ValueError, RuntimeError):
    content = re.sub(
        r"except\s*:", "except (OSError, ValueError, RuntimeError):", content
    )

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def remove_trailing_whitespace(file_path: str) -> bool:
    """Remove trailing whitespace from all lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = [line.rstrip() + "\n" for line in lines]

    # Remove trailing newline if it creates an empty line at the end
    if fixed_lines and fixed_lines[-1].strip() == "":
        fixed_lines = fixed_lines[:-1]

    # Ensure file ends with exactly one newline
    if fixed_lines and not fixed_lines[-1].endswith("\n"):
        fixed_lines[-1] += "\n"

    if lines != fixed_lines:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)
        return True
    return False


def fix_unused_imports(file_path: str) -> bool:
    """Remove obvious unused imports."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    lines = content.split("\n")

    # Track imports and their usage
    imports = {}
    import_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            import_lines.append(i)
            # Extract imported names
            if stripped.startswith("import "):
                module = (
                    stripped.replace("import ", "")
                    .split(" as ")[0]
                    .split(",")[0]
                    .strip()
                )
                imports[module] = i
            elif stripped.startswith("from "):
                if " import " in stripped:
                    names = stripped.split(" import ")[1].split(",")
                    for name in names:
                        name = name.strip().split(" as ")[0]
                        imports[name] = i

    # Check which imports are actually used
    used_imports = set()
    for module in imports:
        if module in content.replace("import {module}", "").replace(
            "from {module}", ""
        ):
            used_imports.add(module)

    # Remove unused import lines (be conservative)
    lines_to_remove = []
    for module, line_num in imports.items():
        if (
            module not in used_imports and len(module) > 2
        ):  # Don't remove single-letter imports
            line_content = lines[line_num].strip()
            # Only remove if it's a single import, not multiple imports on one line
            if "," not in line_content and " as " not in line_content:
                lines_to_remove.append(line_num)

    # Remove lines in reverse order to maintain indices
    for line_num in sorted(lines_to_remove, reverse=True):
        del lines[line_num]

    new_content = "\n".join(lines)
    if new_content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def process_file(file_path: str) -> Dict[str, bool]:
    """Process a single Python file to fix linting issues."""
    fixes = {}

    try:
        fixes["trailing_whitespace"] = remove_trailing_whitespace(file_path)
        fixes["encoding"] = fix_encoding_specifications(file_path)
        fixes["subprocess"] = fix_subprocess_calls(file_path)
        fixes["broad_exceptions"] = fix_broad_exceptions(file_path)
        # fixes['unused_imports'] = fix_unused_imports(file_path)  # Disabled for safety

    except (OSError, ValueError, RuntimeError) as e:
        print("Error processing {file_path}: {e}")
        return {}

    return fixes


def main():
    """Main function to process all Python files in scripts directory."""
    print("Starting lint fixer...")
    scripts_dir = Path("scripts")
    print("Looking for scripts directory: {scripts_dir.absolute()}")

    if not scripts_dir.exists():
        print("Scripts directory not found!")
        return 1

    python_files = list(scripts_dir.glob("*.py"))
    total_fixes = {}

    for py_file in python_files:
        print("Processing {py_file}...")
        file_fixes = process_file(str(py_file))

        for fix_type, applied in file_fixes.items():
            if fix_type not in total_fixes:
                total_fixes[fix_type] = 0
            if applied:
                total_fixes[fix_type] += 1

    print("\nFix Summary:")
    print("=" * 40)
    for fix_type, count in total_fixes.items():
        print("{fix_type.replace('_', ' ').title()}: {count} files")

    print("\nProcessed {len(python_files)} Python files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
