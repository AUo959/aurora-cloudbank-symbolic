#!/usr/bin/env python3
"""Compatibility wrapper delegating Aurora branch management to branch_manager.py."""

from __future__ import annotations

try:
    from .branch_manager import BranchManager, main as _main
except ImportError:
    from branch_manager import BranchManager, main as _main

__all__ = ["BranchManager", "main"]


def main() -> int:
    result = _main()
    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main())
