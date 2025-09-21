#!/usr/bin/env python3
"""
Stage 1 whitespace/formatting fixer

Actions (safe, mechanical):
- Strip trailing whitespace on non-string lines
- Collapse >2 consecutive blank lines to 2 (outside triple-quoted strings)
- Ensure 2 blank lines before top-level def/class (column 0), without touching strings

Usage:
  python3 scripts/whitespace_fix_stage1.py modules/opal2
"""
from __future__ import annotations

import os
import sys
import io
import tokenize
from typing import Set, List


def detect_string_line_spans(src: str) -> Set[int]:
    """Return a set of 1-based line numbers that are part of multi-line string tokens."""
    string_lines: Set[int] = set()
    reader = io.StringIO(src).readline
    try:
        for tok in tokenize.generate_tokens(reader):
            tok_type, tok_str, start, end, _ = tok
            if tok_type == tokenize.STRING:
                srow, _ = start
                erow, _ = end
                # Mark only if spans multiple lines (likely triple-quoted)
                if erow > srow:
                    for ln in range(srow, erow + 1):
                        string_lines.add(ln)
    except tokenize.TokenError:
        # Best-effort; if tokenization fails, treat as no protected string lines
        pass
    return string_lines


def fix_content(src: str) -> str:
    string_lines = detect_string_line_spans(src)
    lines = src.splitlines()

    # Pass 1: strip trailing whitespace on non-string lines
    for i, line in enumerate(lines):
        ln = i + 1
        if ln not in string_lines:
            lines[i] = line.rstrip('\t \r')

    # Pass 2: ensure two blank lines before top-level def/class (non-string lines only)
    def is_top_level_def_or_class(idx: int) -> bool:
        line = lines[idx]
        # safeguard: skip if inside string
        if (idx + 1) in string_lines:
            return False
        return (line.startswith('def ') or line.startswith('class '))

    i = 0
    out: List[str] = []
    while i < len(lines):
        if is_top_level_def_or_class(i):
            # Count existing blank lines immediately above (not in string lines)
            j = len(out) - 1
            blanks = 0
            while j >= 0 and out[j] == '':
                blanks += 1
                j -= 1
            # Normalize to exactly 2 blank lines (but not at file start)
            need = 2 - blanks
            if len(out) == 0:
                # If at file very start, don't inject leading blanks
                need = 0
            for _ in range(max(0, need)):
                out.append('')
            # If there were more than 2, trim extras by popping
            while blanks > 2:
                # remove extra blanks already appended
                # (can't pop from out without careful accounting; instead, drop from source side)
                # We'll simply not copy excess blanks from the source by skipping them below.
                break
        out.append(lines[i])
        i += 1

    lines = out

    # Pass 3: collapse runs of >2 blank lines to 2, skipping string lines
    collapsed: List[str] = []
    run = 0
    for idx, line in enumerate(lines):
        ln = idx + 1
        if ln in string_lines:
            run = 0
            collapsed.append(line)
            continue
        if line == '':
            run += 1
            if run <= 2:
                collapsed.append('')
        else:
            run = 0
            collapsed.append(line)

    return '\n'.join(collapsed) + ('\n' if src.endswith('\n') else '')


def process_file(path: str) -> bool:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            src = f.read()
        fixed = fix_content(src)
        if fixed != src:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return True
        return False
    except Exception as e:
        print(f"[stage1] Skip {path}: {e}")
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/whitespace_fix_stage1.py <dir or file> [<dir or file> ...]")
        return 2
    targets = sys.argv[1:]
    changed = 0
    for t in targets:
        if os.path.isdir(t):
            for root, _, files in os.walk(t):
                for fn in files:
                    if fn.endswith('.py'):
                        path = os.path.join(root, fn)
                        if process_file(path):
                            changed += 1
        elif t.endswith('.py') and os.path.exists(t):
            if process_file(t):
                changed += 1
    print(f"[stage1] Files modified: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
