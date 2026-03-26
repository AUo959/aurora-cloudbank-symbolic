"""Repository wrapper for the Aurora mesh CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    cli_path = repo_root / "src" / "aurora" / "cli" / "mesh_cli.py"
    completed = subprocess.run([sys.executable, str(cli_path), *sys.argv[1:]], cwd=repo_root, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
