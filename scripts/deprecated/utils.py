#!/usr/bin/env python3
"""
Shared utility functions for deprecated scripts.

This module provides common helper functions that can be reused across
multiple scripts in the deprecated folder to reduce code duplication.
"""
import sys
from pathlib import Path


def find_git_root(start_path=None):
    """
    Find the root of the git repository by traversing up from the current directory.
    
    Args:
        start_path: Starting path for the search. Defaults to current working directory.
        
    Returns:
        Path: The repository root path
        
    Raises:
        SystemExit: If not in a git repository
    """
    repo_root = start_path if start_path else Path.cwd()
    
    while not (repo_root / ".git").exists():
        if repo_root == repo_root.parent:
            print("❌ Not in a git repository")
            sys.exit(1)
        repo_root = repo_root.parent
    
    return repo_root
