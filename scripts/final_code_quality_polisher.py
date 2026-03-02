#!/usr/bin/env python3
"""
Aurora CloudBank Final Code Quality Polish
Resolves remaining edge case linting issues
"""

import os
import re
import subprocess
from pathlib import Path


class FinalCodeQualityPolisher:
    def __init__(self):
        self.fixes_applied = 0

    def fix_excessive_blank_lines(self, file_path: Path) -> bool:
        """Fix E303 - too many blank lines"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Replace 3+ consecutive blank lines with exactly 2
            content = re.sub(r"\n\n\n+", "\n\n", content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing blank lines in {file_path}: {e}")

        return False

    def fix_trailing_whitespace(self, file_path: Path) -> bool:
        """Fix W291 and W293 - trailing whitespace"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Remove trailing whitespace from all lines
            lines = content.split("\n")
            cleaned_lines = [line.rstrip() for line in lines]
            content = "\n".join(cleaned_lines)

            # Ensure file ends with single newline if not empty
            if content and not content.endswith("\n"):
                content += "\n"

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing whitespace in {file_path}: {e}")

        return False

    def fix_decorator_blank_lines(self, file_path: Path) -> bool:
        """Fix E304 - blank lines after decorator"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            lines = content.split("\n")
            new_lines = []

            i = 0
            while i < len(lines):
                line = lines[i]
                new_lines.append(line)

                # If this line is a decorator (@something)
                if line.strip().startswith("@") and i + 1 < len(lines):
                    # Remove any blank lines between decorator and function
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == "":
                        j += 1

                    # Skip to the function definition
                    if j < len(lines) and ("def " in lines[j] or "class " in lines[j]):
                        i = j - 1  # Will be incremented at end of loop

                i += 1

            new_content = "\n".join(new_lines)
            if new_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True

        except Exception as e:
            print(f"Error fixing decorators in {file_path}: {e}")

        return False

    def fix_bare_except(self, file_path: Path) -> bool:
        """Fix E722 - bare except clauses"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Replace bare except Exception: with except Exception:
            content = re.sub(r"except\s*:", "except Exception:", content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing bare except in {file_path}: {e}")

        return False

    def fix_comparison_to_true(self, file_path: Path) -> bool:
        """Fix E712 - comparison to True / False"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix is True and is False comparisons
            content = re.sub(r"==\s*True\b", "is True", content)
            content = re.sub(r"==\s*False\b", "is False", content)
            content = re.sub(r"!=\s*True\b", "is not True", content)
            content = re.sub(r"!=\s*False\b", "is not False", content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing comparisons in {file_path}: {e}")

        return False

    def fix_ambiguous_variable_names(self, file_path: Path) -> bool:
        """Fix E741 - ambiguous variable names"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Replace single-letter variable names in common patterns
            content = re.sub(r"\bl\s*=", "line =", content)
            content = re.sub(r"for\s+l\s+in", "for line in", content)
            content = re.sub(r"\bI\s*=", "idx =", content)
            content = re.sub(r"for\s+I\s+in", "for idx in", content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing variable names in {file_path}: {e}")

        return False

    def fix_escape_sequences(self, file_path: Path) -> bool:
        """Fix W605 - invalid escape sequences"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix common invalid escape sequences by making them raw strings
            content = re.sub(r"'([^']*\\[wsdWSD][^']*)'", r"r'\1'", content)
            content = re.sub(r'"([^"]*\\[wsdWSD][^"]*)"', r'r"\1"', content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing escape sequences in {file_path}: {e}")

        return False

    def fix_semicolons(self, file_path: Path) -> bool:
        """Fix E703 - statement ends with semicolon"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Remove semicolons at end of lines
            content = re.sub(r";(\s*\n)", r"\1", content)
            content = re.sub(r";(\s*)$", r"\1", content, flags=re.MULTILINE)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing semicolons in {file_path}: {e}")

        return False

    def fix_import_order(self, file_path: Path) -> bool:
        """Fix E402 - module level import not at top"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            lines = content.split("\n")

            # Find all imports and their line numbers
            imports = []
            non_imports = []
            docstring_ended = False

            for i, line in enumerate(lines):
                stripped = line.strip()

                # Skip shebang and encoding
                if i == 0 and stripped.startswith("#!"):
                    non_imports.append(line)
                    continue
                elif stripped.startswith("# -*- coding") or stripped.startswith("# coding"):
                    non_imports.append(line)
                    continue

                # Track docstring
                if not docstring_ended and ('"""' in stripped or "'''" in stripped):
                    non_imports.append(line)
                    if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                        docstring_ended = True
                    continue
                elif not docstring_ended and (stripped.startswith('"""') or stripped.startswith("'''")):
                    non_imports.append(line)
                    docstring_ended = True
                    continue
                elif not docstring_ended:
                    non_imports.append(line)
                    continue

                # After docstring, collect imports
                if stripped.startswith(("import ", "from ")) and "import" in stripped:
                    imports.append(line)
                else:
                    non_imports.append(line)

            # If we found imports to move, reconstruct the file
            if imports and any("import" in line for line in non_imports[3:]):
                # Find where docstring ends
                docstring_end = 0
                for i, line in enumerate(non_imports):
                    if '"""' in line or "'''" in line:
                        docstring_end = i + 1
                        break

                # Reconstruct: header + docstring + imports + rest
                new_lines = (
                    non_imports[:docstring_end]
                    + [""]
                    + imports
                    + [""]
                    + [
                        line
                        for line in non_imports[docstring_end:]
                        if not (line.strip().startswith(("import ", "from ")) and "import" in line)
                    ]
                )

                new_content = "\n".join(new_lines)
                if new_content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    return True

        except Exception as e:
            print(f"Error fixing imports in {file_path}: {e}")

        return False

    def process_file(self, file_path: Path) -> int:
        """Process a single file and count fixes applied"""
        fixes = 0

        if self.fix_trailing_whitespace(file_path):
            fixes += 1
        if self.fix_excessive_blank_lines(file_path):
            fixes += 1
        if self.fix_decorator_blank_lines(file_path):
            fixes += 1
        if self.fix_bare_except(file_path):
            fixes += 1
        if self.fix_comparison_to_true(file_path):
            fixes += 1
        if self.fix_ambiguous_variable_names(file_path):
            fixes += 1
        if self.fix_escape_sequences(file_path):
            fixes += 1
        if self.fix_semicolons(file_path):
            fixes += 1
        if self.fix_import_order(file_path):
            fixes += 1

        return fixes

    def run_final_polish(self) -> None:
        """Run final code quality polish"""
        print("✨ Aurora CloudBank Final Code Quality Polish")
        print("=" * 60)

        # Get all Python files
        py_files = list(Path(".").rglob("*.py"))

        # Filter out unwanted directories
        filtered_files = []
        for file_path in py_files:
            if not any(skip in str(file_path) for skip in [".git", "node_modules", "venv", "__pycache__"]):
                filtered_files.append(file_path)

        print(f"Polishing {len(filtered_files)} Python files...")

        files_fixed = 0
        for file_path in filtered_files:
            try:
                fixes = self.process_file(file_path)
                if fixes > 0:
                    self.fixes_applied += fixes
                    files_fixed += 1
                    print(f"  ✓ Polished {file_path} ({fixes} fixes)")

            except Exception as e:
                print(f"  ❌ Error polishing {file_path}: {e}")

        print("\n📊 Final Polish Summary:")
        print(f"Files Fixed: {files_fixed}")
        print(f"Total Fixes: {self.fixes_applied}")

        # Final validation
        self.run_final_validation()

    def run_final_validation(self) -> None:
        """Run final flake8 validation"""
        try:
            result = subprocess.run(
                ["python3", "-m", "flake8", "--statistics", "--count"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                print("\n🎉 ALL LINTING ISSUES RESOLVED!")
                print("Repository achieves perfect code quality standards!")
            else:
                lines = result.stdout.strip().split("\n")
                if lines and lines[-1].isdigit():
                    remaining = int(lines[-1])
                    print(f"\n📈 Progress: {remaining} issues remaining")
                    if remaining < 100:
                        print("Excellent progress! Repository is nearly perfect.")
                    else:
                        print("Good progress made, continuing polish...")

        except Exception as e:
            print(f"Could not run final validation: {e}")


def main():
    polisher = FinalCodeQualityPolisher()
    polisher.run_final_polish()


if __name__ == "__main__":
    main()
