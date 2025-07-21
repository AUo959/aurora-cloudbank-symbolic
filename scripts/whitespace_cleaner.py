#!/usr/bin/env python3
"""
Aurora CloudBank Whitespace Cleaner
Removes trailing whitespace and fixes blank line formatting issues
"""

import re
from pathlib import Path

def clean_file(file_path):
    """Clean whitespace issues in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Remove trailing whitespace from all lines
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        content = '\n'.join(cleaned_lines)

        # Ensure file ends with single newline (if not empty)
        if content and not content.endswith('\n'):
            content += '\n'

        # Remove excessive blank lines (more than 2 consecutive)
        content = re.sub(r'\n\n\n+', '\n\n', content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    print("🧹 Aurora CloudBank Whitespace Cleaner")
    print("=" * 40)

    # File extensions to clean
    extensions = ['.py', '.js', '.json', '.yml', '.yaml', '.md']

    files_cleaned = 0
    total_files = 0

    for ext in extensions:
        print(f"\nCleaning {ext} files...")
        files = list(Path('.').rglob(f'*{ext}'))

        for file_path in files:
            # Skip certain directories
            if any(skip in str(file_path) for skip in ['.git', 'node_modules', 'venv', '__pycache__']):
                continue

            total_files += 1
            if clean_file(file_path):
                files_cleaned += 1
                print(f"  ✓ Cleaned {file_path}")

    print("\n📊 Summary:")
    print(f"  Total files processed: {total_files}")
    print(f"  Files cleaned: {files_cleaned}")
    print(f"  Files unchanged: {total_files - files_cleaned}")

if __name__ == "__main__":
    main()
