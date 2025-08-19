#!/usr/bin/env python3
"""
Comprehensive Python Syntax Error Fixer
========================================

Fixes common syntax errors in the Aurora CloudBank codebase that prevent
CodeQL scanning from working properly.
"""

import os
import re
import subprocess
import sys


def fix_js_style_syntax(file_path):
    """Fix JavaScript/Java-style syntax mixed into Python files"""
    print(f"🔧 Fixing JS-style syntax in {file_path}r")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix common JS/Java to Python conversions
    content = re.sub(r'function\s+(\w+)\s*\(([^)]*)\)\s*\{', r'def \1(\2):', content)
    content = re.sub(r'\)\s*\{', '):', content)  # ) { -> ):
    content = re.sub(r';$', '', content, flags=re.MULTILINE)  # Remove trailing semicolons
    content = re.sub(r'^\s*\}$', '', content, flags=re.MULTILINE)  # Remove standalone }
    content = re.sub(r'\bthis\.', 'self.', content)  # this. -> self.
    content = re.sub(r'^(\s*)//(.*)$', r'\1#\2', content, flags=re.MULTILINE)  # // -> #
    content = re.sub(r'\}\s*;', '}', content)  # }; -> }

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def fix_duplicate_encoding(file_path):
    """Fix duplicate encoding parameters in file operations"""
    print(f"🔧 Fixing duplicate encoding in {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix multiple duplicate encoding parameters
    content = re.sub(r'(, encoding="utf-8"){2,}', r', encoding="utf-8"', content)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def check_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', file_path],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)


def find_and_fix_python_files():
    """Find and fix all Python files with syntax errors"""
    print("🔍 Scanning for Python files with syntax errors...")

    # Find all Python files, excluding virtual environments
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and node_modules
        dirs[:] = [d for d in dirs if d not in ['.venv', 'venv', 'node_modules', '__pycache__']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    print(f"📁 Found {len(python_files)} Python files to check")

    files_fixed = 0
    syntax_errors = []

    for file_path in python_files:
        # Check initial syntax
        is_valid, error_msg = check_syntax(file_path)

        if not is_valid:
            print(f"❌ Syntax error in {file_path}")
            syntax_errors.append((file_path, error_msg))

            # Try to fix common issues
            fixed_js = fix_js_style_syntax(file_path)
            fixed_encoding = fix_duplicate_encoding(file_path)

            if fixed_js or fixed_encoding:
                # Check if fixes worked
                is_valid_after, _ = check_syntax(file_path)
                if is_valid_after:
                    print(f"✅ Fixed syntax errors in {file_path}")
                    files_fixed += 1
                    # Remove from error list
                    syntax_errors = [(f, e) for f, e in syntax_errors if f != file_path]
                else:
                    print(f"⚠️  Could not automatically fix {file_path}")

    print("\n📊 Summary:")
    print(f"   ✅ Files fixed: {files_fixed}")
    print(f"   ❌ Files still with errors: {len(syntax_errors)}")

    if syntax_errors:
        print("\n🚨 Remaining syntax errors:")
        for file_path, error_msg in syntax_errors:
            print(f"   {file_path}: {error_msg.strip()}")

    return len(syntax_errors) == 0


if __name__ == "__main__":
    print("🌟 Aurora CloudBank Syntax Error Fixer")
    print("=" * 50)

    success = find_and_fix_python_files()

    if success:
        print("\n🎉 All Python syntax errors fixed!")
        print("CodeQL scanning should now work properly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some syntax errors require manual intervention.")
        sys.exit(1)
