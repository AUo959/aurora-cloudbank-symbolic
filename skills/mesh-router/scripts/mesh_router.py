"""Wrapper script for the mesh-router skill."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    repo_root = Path(__file__).resolve().parents[3]
    cli_path = repo_root / "mesh_cli.py"
    command = [sys.executable, str(cli_path), *args]
    completed = subprocess.run(command, cwd=repo_root, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
