#!/usr/bin/env python3
"""Codespace/bootstrap helper with diagnostic-first defaults.

Diagnostic mode: local runs print readiness details without mutating the environment.
Guidance: pass --execute, or rely on explicit Codespaces auto-execute, to run bootstrap steps.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_step(step_name: str, command: list[str], cwd: Path = REPO_ROOT) -> bool:
    print(f"[{step_name}] + {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode == 0:
        print(f"[{step_name}] success")
        return True
    print(f"[{step_name}] failed with exit code {result.returncode}")
    return False


def detect_codespaces() -> bool:
    return os.environ.get("CODESPACES", "").lower() == "true" or bool(
        os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
    )


def diagnose() -> None:
    print("[codespace-init] Repository:", REPO_ROOT)
    print("[codespace-init] Codespaces detected:", "yes" if detect_codespaces() else "no")
    for tool in ("python3", "npm", "node", "git"):
        resolved = shutil.which(tool)
        print(f"[codespace-init] {tool}: {resolved or 'not installed'}")
    print("[codespace-init] requirements.txt:", "present" if (REPO_ROOT / "requirements.txt").exists() else "missing")
    print("[codespace-init] package.json:", "present" if (REPO_ROOT / "package.json").exists() else "missing")
    print(
        "[codespace-init] startup hook:",
        "present" if (REPO_ROOT / "scripts" / "dev" / "on_startup.sh").exists() else "missing",
    )
    print("[codespace-init] Diagnostic mode: dry-run complete.")
    print("[codespace-init] Guidance: re-run with --execute for local bootstrap.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Aurora dependencies in Codespaces or local dev")
    parser.add_argument("--execute", action="store_true", help="Run the bootstrap steps locally")
    parser.add_argument("--include-optional", action="store_true", help="Install optional Python requirements")
    parser.add_argument("--skip-node", action="store_true", help="Skip npm install")
    parser.add_argument("--skip-startup", action="store_true", help="Skip scripts/dev/on_startup.sh")
    args = parser.parse_args()

    execute = args.execute or detect_codespaces() or os.environ.get("AURORA_CODESPACE_AUTO_EXECUTE") == "1"
    if not execute:
        diagnose()
        return 0

    success = True
    setup_cmd = [str(REPO_ROOT / "scripts" / "setup_dependencies.sh"), "--execute", "--install-python"]
    if args.include_optional:
        setup_cmd.append("--include-optional")
    success &= run_step("Python bootstrap", setup_cmd)

    if not args.skip_node and (REPO_ROOT / "package.json").exists():
        if shutil.which("npm"):
            success &= run_step("Node bootstrap", ["npm", "install"])
        else:
            print("[codespace-init] npm not installed; skipping Node bootstrap")

    startup_script = REPO_ROOT / "scripts" / "dev" / "on_startup.sh"
    if not args.skip_startup and startup_script.exists():
        success &= run_step("Startup hook", ["bash", str(startup_script)])

    if success:
        print("[codespace-init] Environment initialization complete")
        return 0

    print("[codespace-init] Bootstrap completed with failures")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
