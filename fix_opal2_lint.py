#!/usr/bin/env python3
import os

"""
Simple lint fixer for Opal2 files
Removes trailing whitespace and fixes basic issues
"""


def fix_file(file_path):
    pass
    """Fix basic lint issues in a file"""
    try:
    pass
        with open(file_path, "r", encoding="utf-8") as f:
    pass
            content = f.read()

        # Remove trailing whitespace
        lines = content.split("\n")
        fixed_lines = [line.rstrip() for line in lines]

        # Remove blank lines with only whitespace
        fixed_lines = [line if line.strip() else "" for line in fixed_lines]

        # Join back and ensure single newline at end
        fixed_content = "\n".join(fixed_lines)
        if fixed_content and not fixed_content.endswith("\n"):
    pass
            fixed_content += "\n"

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
    pass
            f.write(fixed_content)

        print("✅ Fixed {file_path}")
        return True

    except Exception as _:
    pass
        print("❌ Error fixing {file_path}: {e}")
        return False

def main():
    pass
    """Fix Opal2 files"""
    opal2_files = [
        "modules/opal2/glyph_core.py",
        "modules/opal2/glyph_cache.py",
        "test_opal2_integration.py",
        "test_opal2_simple.py",
        "opal2_pr_preparation.py",
    ]

    print("🧹 Fixing basic lint issues in Opal2 files...")

    for file_path in opal2_files:
    pass
        if os.path.exists(file_path):
    pass
            fix_file(file_path)
        else:
    pass
            print("⚠️  File not found: {file_path}")

    print("🎉 Basic lint fixes complete!")

if __name__ == "__main__":
    pass
    main()
