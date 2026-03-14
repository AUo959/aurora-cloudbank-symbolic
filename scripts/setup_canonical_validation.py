#!/usr/bin/env python3
"""Diagnostic-first setup for the canonical validation toolchain."""

from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_PACKAGES = ["watchdog", "pyyaml"]
VALIDATION_SCRIPTS = [
    REPO_ROOT / "scripts" / "canonical_validator.py",
    REPO_ROOT / "scripts" / "git_pre_commit_hook.py",
    REPO_ROOT / "scripts" / "continuous_validator.py",
]
HOOK_CONTENT = """#!/bin/bash
python3 scripts/git_pre_commit_hook.py
"""


def check_package(package: str) -> bool:
    try:
        __import__(package.replace("-", "_"))
        return True
    except ImportError:
        return False


def diagnose() -> None:
    print("Aurora Canonical Validation Setup")
    print("=================================")
    for package in REQUIRED_PACKAGES:
        print(f"  - {package}: {'installed' if check_package(package) else 'missing'}")
    print(f"  - git repo: {'yes' if (REPO_ROOT / '.git').exists() else 'no'}")
    for script in VALIDATION_SCRIPTS:
        print(f"  - {script.name}: {'present' if script.exists() else 'missing'}")
    print("[setup-canonical-validation] Dry-run complete. Re-run with --execute to install hooks and dependencies.")


def install_missing_packages() -> bool:
    missing = [package for package in REQUIRED_PACKAGES if not check_package(package)]
    if not missing:
        return True
    command = [sys.executable, "-m", "pip", "install", *missing]
    print(f"[setup-canonical-validation] + {' '.join(command)}")
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode == 0


def ensure_validation_scripts_executable() -> bool:
    ok = True
    for script in VALIDATION_SCRIPTS:
        if not script.exists():
            print(f"[setup-canonical-validation] missing: {script}")
            ok = False
            continue
        mode = script.stat().st_mode
        script.chmod(mode | stat.S_IXUSR)
    return ok


def ensure_directories() -> None:
    for directory in ("config", "logs", "reports"):
        (REPO_ROOT / directory).mkdir(exist_ok=True)


def install_git_hook(force_hook: bool) -> bool:
    git_dir = REPO_ROOT / ".git"
    if not git_dir.exists():
        print("[setup-canonical-validation] Not a git repository; skipping hook installation")
        return True

    hook_path = git_dir / "hooks" / "pre-commit"
    if hook_path.exists() and not force_hook:
        print("[setup-canonical-validation] pre-commit hook already exists; pass --force-hook to replace it")
        return True

    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(HOOK_CONTENT, encoding="utf-8")
    hook_path.chmod(0o755)
    print(f"[setup-canonical-validation] Installed hook at {hook_path}")
    return True


def smoke_test() -> bool:
    validator = REPO_ROOT / "scripts" / "canonical_validator.py"
    if not validator.exists():
        return False
    command = [sys.executable, str(validator), "--help"]
    print(f"[setup-canonical-validation] + {' '.join(command)}")
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up canonical validation for the Aurora repository")
    parser.add_argument("--execute", action="store_true", help="Install dependencies, hooks, and directories")
    parser.add_argument("--force-hook", action="store_true", help="Replace an existing pre-commit hook")
    args = parser.parse_args()

    if not args.execute:
        diagnose()
        return 0

    ok = install_missing_packages()
    ensure_directories()
    ok &= ensure_validation_scripts_executable()
    ok &= install_git_hook(args.force_hook)
    ok &= smoke_test()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
