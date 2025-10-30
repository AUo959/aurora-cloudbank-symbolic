#!/usr/bin/env python3
"""
Fix Git merge conflict markers in Python files
Automatically resolves conflicts by keeping the HEAD version (current changes)
"""
from pathlib import Path
from typing import List, Tuple


def find_conflict_files() -> List[Path]:
    """Find all Python files with merge conflict markers"""
    repo_root = Path.cwd()
    conflict_files = []

    for py_file in repo_root.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            if '<<<<<<< HEAD' in content:
                conflict_files.append(py_file)
        except Exception:
            continue

    return conflict_files


def resolve_conflicts(content: str) -> Tuple[str, int]:
    """
    Resolve merge conflicts by keeping HEAD version
    Returns (fixed_content, num_conflicts_resolved)
    """
    conflicts_fixed = 0
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        if lines[i].startswith('<<<<<<< HEAD'):
            # Mark the start of a potential conflict
            conflict_start = i
            i += 1
            head_content = []

            # Collect HEAD content until we find the separator
            while i < len(lines) and lines[i] != '=======':
                head_content.append(lines[i])
                i += 1

            # Check if we found the separator
            if i < len(lines) and lines[i] == '=======':
                separator_index = i
                i += 1
                origin_content = []

                # Collect origin content while looking for end marker
                while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                    origin_content.append(lines[i])
                    i += 1

                # Check if we found the end marker
                if i < len(lines) and lines[i].startswith('>>>>>>>'):
                    # Complete conflict block found, keep HEAD content
                    result.extend(head_content)
                    conflicts_fixed += 1
                    i += 1  # Skip the >>>>>>> line
                else:
                    # Incomplete conflict block (no end marker), preserve everything
                    result.append(lines[conflict_start])
                    result.extend(head_content)
                    result.append(lines[separator_index])
                    result.extend(origin_content)
            else:
                # No separator found, preserve everything we've seen
                result.append(lines[conflict_start])
                result.extend(head_content)
        else:
            result.append(lines[i])
            i += 1

    return '\n'.join(result), conflicts_fixed


def main():
    print("🔍 Searching for merge conflict markers...")
    conflict_files = find_conflict_files()

    if not conflict_files:
        print("✅ No merge conflicts found!")
        return

    print(f"\n📋 Found {len(conflict_files)} files with merge conflicts\n")

    total_conflicts = 0
    fixed_files = 0

    for file_path in conflict_files:
        try:
            original_content = file_path.read_text(encoding='utf-8')
            fixed_content, num_conflicts = resolve_conflicts(original_content)

            if num_conflicts > 0:
                file_path.write_text(fixed_content, encoding='utf-8')
                fixed_files += 1
                total_conflicts += num_conflicts
                print(f"✅ {file_path.relative_to(Path.cwd())}: Fixed {num_conflicts} conflict(s)")

        except Exception as e:
            print(f"❌ {file_path.relative_to(Path.cwd())}: {e}")

    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_files} files ({total_conflicts} total conflicts)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
