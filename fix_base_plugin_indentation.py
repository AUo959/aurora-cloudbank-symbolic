#!/usr/bin/env python3
"""
Base Plugin Indentation Fixer
Fixes the systematic indentation issues in base_plugin.py
"""

import re


def fix_base_plugin_file():
    pass
    """Fix all indentation issues in base_plugin.py."""
    file_path = "modules/opal2/plugins/base_plugin.py"

    try:
    pass
        with open(file_path, "r", encoding="utf-8") as f:
    pass
            content = f.read()

        lines = content.split("\n")
        fixed_lines = []

        in_class = False
        for i, line in enumerate(lines):
    pass
            # Detect class definition
            if line.strip().startswith("class ") and ":" in line:
    pass
                in_class = True
                fixed_lines.append(line)
                continue

            # Fix method definitions inside class
            if in_class and line.strip().startswith("def ") and ":" in line:
    pass
                # Method should be indented with 4 spaces from class
                if not line.startswith("    def "):
    pass
                    line = "    " + line.strip()
                fixed_lines.append(line)
                continue

            # Fix method content (should be indented 8 spaces from class start)
            if in_class and line.strip() and not line.startswith("    "):
    pass
                # If it's not already properly indented and not a class/def line
                if not line.strip().startswith(("class ", "def ", "#", '"""', "'''")) and line.strip() != "":
    pass
                    # Make sure it has proper method indentation
                    if line.startswith(" ") and not line.startswith("        "):
    pass
                        # Already has some indentation, fix it to 8 spaces
                        line = "        " + line.strip()
                    elif not line.startswith(" "):
    pass
                        # No indentation, add 8 spaces for method content
                        line = "        " + line.strip()

            # Detect end of class
            if line.strip() and not line.startswith(" ") and not line.startswith("\t") and in_class:
    pass
                if not line.strip().startswith("#"):
    pass
                    in_class = False

            fixed_lines.append(line)

        # Join lines back together
        fixed_content = "\n".join(fixed_lines)

        # Additional specific fixes for common patterns
        patterns = [
            # Fix try/except blocks
            (r"(\s+)try:\n(\s*)(\w+)", r"\1try:\n\1    \3"),
            (r"(\s+)except([^:]*?):\n(\s*)(\w+)", r"\1except\2:\n\1    \4"),
            # Fix if statements
            (r"(\s+)if ([^:]+?):\n(\s*)return", r"\1if \2:\n\1    return"),
            (r"(\s+)if ([^:]+?):\n(\s*)raise", r"\1if \2:\n\1    raise"),
        ]

        for pattern, replacement in patterns:
    pass
            fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.MULTILINE)

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
    pass
            f.write(fixed_content)

        print("✅ Fixed indentation in {file_path}")
        return True

    except Exception as _:
    pass
        print("❌ Error fixing {file_path}: {e}")
        return False

if __name__ == "__main__":
    pass
    fix_base_plugin_file()
