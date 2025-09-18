#!/usr/bin/env python3
import os

"""
Final Blank Line Formatter - Fixes E302 and E305 blank line issues
Professional code formatting for function and class definitions
"""

import re


class BlankLineFormatter:
    pass
    def __init__(self):
    pass
        pass

    def fix_blank_lines_in_file(self, file_path: str) -> bool:
    pass
        """Fix blank line issues in a Python file."""
        try:
    pass
            with open(file_path, "r", encoding="utf-8") as f:
    pass
                content = f.read()

            original_content = content
            lines = content.split("\n")

            # Process lines to fix blank line issues
            fixed_lines = []
            i = 0
            while i < len(lines):
    pass
                line = lines[i]

                # Check if current line starts a function or class definition
                if re.match(r"^(def |class |async def )", line.strip()):
    pass
                    # Check how many blank lines we have before this line
                    blank_count = 0
                    j = len(fixed_lines) - 1
                    while j >= 0 and not fixed_lines[j].strip():
    pass
                        blank_count += 1
                        j -= 1

                    # Remove existing blank lines
                    while fixed_lines and not fixed_lines[-1].strip():
    pass
                        fixed_lines.pop()

                    # Add exactly 2 blank lines before function/class definitions
                    # (unless it's the first thing in the file)
                    if fixed_lines:  # Not the first line in file
                        fixed_lines.extend(["", ""])

                elif re.match(r"^[a-zA-Z_]", line.strip()) and i > 0:
    pass
                    # This might be after a function/class definition
                    prev_line_idx = i - 1
                    while prev_line_idx >= 0 and not lines[prev_line_idx].strip():
    pass
                        prev_line_idx -= 1

                    if prev_line_idx >= 0:
    pass
                        prev_line = lines[prev_line_idx].strip()
                        # Check if previous line ended a function or class
                        if (
                            not prev_line.endswith(":")
                            and not prev_line.startswith('"""')
                            and not prev_line.startswith("'''")
                            and prev_line
                            and len(fixed_lines) > 0
                        ):
    pass
                            # Count current blank lines
                            blank_count = 0
                            j = len(fixed_lines) - 1
                            while j >= 0 and not fixed_lines[j].strip():
    pass
                                blank_count += 1
                                j -= 1

                            # If we're starting something new after a function/class
                            # and don't have enough blank lines
                            if blank_count < 2 and j >= 0:
    pass
                                # Check if the previous non-blank line suggests end of function/class
                                prev_content = fixed_lines[j] if j >= 0 else ""
                                if (
                                    prev_content.strip()
                                    and not prev_content.strip().endswith(":")
                                    and not prev_content.strip().startswith("#")
                                ):
    pass
                                    # Remove existing blank lines
                                    while fixed_lines and not fixed_lines[-1].strip():
    pass
                                        fixed_lines.pop()

                                    # Add 2 blank lines
                                    fixed_lines.extend(["", ""])

                fixed_lines.append(line)
                i += 1

            new_content = "\n".join(fixed_lines)

            # Only write if content changed
            if new_content != original_content:
    pass
                with open(file_path, "w", encoding="utf-8") as f:
    pass
                    f.write(new_content)
                return True

            return False

        except Exception as _:
    pass
            print("Error processing {file_path}: {e}")
            return False

    def process_files(self, file_paths: list) -> None:
    pass
        """Process specific files for blank line fixes."""
        files_fixed = 0

        for file_path in file_paths:
    pass
            if os.path.exists(file_path) and self.fix_blank_lines_in_file(file_path):
    pass
                files_fixed += 1
                print("✓ Fixed blank lines in {file_path}")

        print("\n=== Blank Line Formatting Complete ===")
        print("Files Fixed: {files_fixed}")
        print("Files Processed: {len(file_paths)}")

def main():
    pass
    print("🔧 Final Blank Line Formatter")
    print("=" * 50)

    # Target the specific files we know have issues
    target_files = ["./.security/secure_helpers.py", "./aurora_adaptive_learning.py", "./aurora_api.py"]

    formatter = BlankLineFormatter()
    formatter.process_files(target_files)

if __name__ == "__main__":
    pass
    main()
