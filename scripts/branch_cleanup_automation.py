#!/usr/bin/env python3
"""Compatibility wrapper delegating to automated_branch_cleanup.py."""

from automated_branch_cleanup import BranchCleanupManager, main

__all__ = ["BranchCleanupManager", "main"]

if __name__ == "__main__":
    raise SystemExit(main())
