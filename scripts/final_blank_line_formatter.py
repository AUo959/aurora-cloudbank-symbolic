#!/usr/bin/env python3
"""
Final Blank Line Formatter - Fixes E302 and E305 blank line issues
Professional code formatting for function and class definitions
"""

import os
import re


class BlankLineFormatter:
    def __init__(self):
        pass

    def fix_blank_lines_in_file(self, file_path: str) -> bool:
        """Fix blank line issues in a Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            lines = content.split("\n")

            # Process lines to fix blank line issues
            fixed_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]

                # Check if current line starts a function or class definition
                if re.match(r"^(def |class |async def )", line.strip()):
                    # Check how many blank lines we have before this line
                    blank_count = 0
                    j = len(fixed_lines) - 1
                    while j >= 0 and not fixed_lines[j].strip():
                        blank_count += 1
                        j -= 1

                    # Remove existing blank lines
                    while fixed_lines and not fixed_lines[-1].strip():
                        fixed_lines.pop()

                    # Add exactly 2 blank lines before function/class definitions
                    # (unless it's the first thing in the file)
                    if fixed_lines:  # Not the first line in file
                        fixed_lines.extend(["", ""])

                elif re.match(r"^[a-zA-Z_]", line.strip()) and i > 0:
                    # This might be after a function/class definition
                    prev_line_idx = i - 1
                    while prev_line_idx >= 0 and not lines[prev_line_idx].strip():
                        prev_line_idx -= 1

                    if prev_line_idx >= 0:
                        prev_line = lines[prev_line_idx].strip()
                        # Check if previous line ended a function or class
                        if (
                            not prev_line.endswith(":")
                            and not prev_line.startswith('"""')
                            and not prev_line.startswith("'''")
                            and prev_line
                            and len(fixed_lines) > 0
                        ):

                            # Count current blank lines
                            blank_count = 0
                            j = len(fixed_lines) - 1
                            while j >= 0 and not fixed_lines[j].strip():
                                blank_count += 1
                                j -= 1

                            # If we're starting something new after a function/class
                            # and don't have enough blank lines
                            if blank_count < 2 and j >= 0:
                                # Check if the previous non-blank line suggests end of function/class
                                prev_content = fixed_lines[j] if j >= 0 else ""
                                if (
                                    prev_content.strip()
                                    and not prev_content.strip().endswith(":")
                                    and not prev_content.strip().startswith("#")
                                ):

                                    # Remove existing blank lines
                                    while fixed_lines and not fixed_lines[-1].strip():
                                        fixed_lines.pop()

                                    # Add 2 blank lines
                                    fixed_lines.extend(["", ""])

                fixed_lines.append(line)
                i += 1

            new_content = "\n".join(fixed_lines)

            # Only write if content changed
            if new_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True

            return False

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False

    def process_files(self, file_paths: list) -> None:
        """Process specific files for blank line fixes."""
        files_fixed = 0

        for file_path in file_paths:
            if os.path.exists(file_path) and self.fix_blank_lines_in_file(file_path):
                files_fixed += 1
                print(f"✓ Fixed blank lines in {file_path}")

        print("\n=== Blank Line Formatting Complete ===")
        print(f"Files Fixed: {files_fixed}")
        print(f"Files Processed: {len(file_paths)}")


def main():
    print("🔧 Final Blank Line Formatter")
    print("=" * 50)

    # Target the specific files we know have issues
    target_files = ["./.security/secure_helpers.py", "./aurora_adaptive_learning.py", "./aurora_api.py"]

    formatter = BlankLineFormatter()
    formatter.process_files(target_files)


if __name__ == "__main__":
    main()
