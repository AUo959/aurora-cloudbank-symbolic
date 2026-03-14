#!/usr/bin/env python3
"""Lightweight repository health monitor with safe defaults for local maintenance runs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def run_text(command: List[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, shell=False, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def get_repo_size_mb(repo_root: Path) -> int:
    output = run_text(["du", "-sm", str(repo_root)])
    if not output:
        return 0
    try:
        return int(output.split()[0])
    except (IndexError, ValueError):
        return 0


def get_file_count(repo_root: Path) -> int:
    return sum(1 for path in repo_root.rglob("*") if path.is_file())


def get_zip_count(repo_root: Path) -> int:
    return sum(1 for path in repo_root.rglob("*.zip") if path.is_file())


def get_branch_count(repo_root: Path) -> int:
    output = run_text(["git", "-C", str(repo_root), "branch", "-r"])
    return len([line for line in output.splitlines() if line.strip() and "origin/HEAD" not in line])


def normalize_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).strip().lower()


def parse_declared_packages(repo_root: Path) -> set[str]:
    packages: set[str] = set()
    for file_name in ("requirements.txt", "requirements-optional.txt"):
        path = repo_root / file_name
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("-r "):
                continue
            match = re.match(r"([A-Za-z0-9_.-]+)", line)
            if match:
                packages.add(normalize_package_name(match.group(1)))
    return packages


def resolve_python_path(repo_root: Path) -> str:
    ensure_script = repo_root / "scripts" / "ensure_python.sh"
    if ensure_script.exists():
        resolved = run_text([str(ensure_script), "--print-path"])
        if resolved:
            return resolved
    fallback = repo_root / ".venv" / "bin" / "python"
    return str(fallback) if fallback.exists() else ""


def inspect_python_environment(repo_root: Path) -> Dict[str, object]:
    declared_packages = parse_declared_packages(repo_root)
    python_path = resolve_python_path(repo_root)
    report: Dict[str, object] = {
        "interpreter_path": python_path,
        "python_version": "",
        "fastapi_required": "fastapi" in declared_packages,
        "fastapi_installed": False,
        "fastapi_version": "",
        "uvicorn_installed": False,
        "uvicorn_version": "",
        "status": "missing_interpreter" if not python_path else "unknown",
    }

    if not python_path:
        return report

    probe_script = """
import json
import sys
from importlib.metadata import PackageNotFoundError, version

payload = {"python_version": sys.version.split()[0]}
for name in ("fastapi", "uvicorn"):
    key = name.replace("-", "_")
    try:
        payload[f"{key}_version"] = version(name)
    except PackageNotFoundError:
        payload[f"{key}_version"] = ""

print(json.dumps(payload))
""".strip()
    probe = run_text([python_path, "-c", probe_script])
    if not probe:
        report["status"] = "probe_failed"
        return report

    try:
        payload = json.loads(probe)
    except json.JSONDecodeError:
        report["status"] = "probe_failed"
        return report

    report["python_version"] = payload.get("python_version", "")
    report["fastapi_version"] = payload.get("fastapi_version", "")
    report["uvicorn_version"] = payload.get("uvicorn_version", "")
    report["fastapi_installed"] = bool(report["fastapi_version"])
    report["uvicorn_installed"] = bool(report["uvicorn_version"])
    report["status"] = "ready" if report["fastapi_required"] and report["fastapi_installed"] else "fastapi_missing"
    return report


def build_report(repo_root: Path) -> Dict[str, object]:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "repo_size_mb": get_repo_size_mb(repo_root),
        "file_count": get_file_count(repo_root),
        "zip_count": get_zip_count(repo_root),
        "branch_count": get_branch_count(repo_root),
        "python_env": inspect_python_environment(repo_root),
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Lightweight repository health monitor")
    parser.add_argument(
        "--output",
        default="repo_health_status.json",
        help="Path to write the JSON report (default: repo_health_status.json)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    report = build_report(repo_root)
    output_path = (repo_root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"[repo-health-monitor] Report written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
