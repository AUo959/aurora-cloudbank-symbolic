#!/usr/bin/env python3
"""Canonical dependency scanner and updater for the Aurora workspace."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


REQUIREMENTS_FILES = ("requirements.txt", "requirements-optional.txt")
CRITICAL_PYTHON_PACKAGES = ("fastapi", "uvicorn", "pytest-asyncio")


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_package_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).strip().lower()


def run_command(command: list[str], cwd: Path, env: Optional[dict[str, str]] = None) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    return CommandResult(
        command=command,
        returncode=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )


def parse_requirement_names(lines: Iterable[str]) -> dict[str, str]:
    packages: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-r "):
            continue
        match = re.match(r"([A-Za-z0-9_.-]+)", line)
        if not match:
            continue
        requirement_name = match.group(1)
        packages[normalize_package_name(requirement_name)] = line
    return packages


class DependencyAutoUpdater:
    """Manage dependency diagnostics and optional upgrades from one canonical entrypoint."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.script_dir = self.project_root / "scripts"
        self.ensure_python_script = self.script_dir / "ensure_python.sh"
        self.setup_dependencies_script = self.script_dir / "setup_dependencies.sh"
        self.uv_bin = self._resolve_uv_bin()

    def _resolve_uv_bin(self) -> Optional[str]:
        override = os.environ.get("AURORA_UV_BIN", "").strip()
        if override:
            return override
        discovered = shutil.which("uv")
        if discovered:
            return discovered
        candidate = Path.home() / ".local" / "bin" / "uv"
        if candidate.exists():
            return str(candidate)
        return None

    def _uv_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("UV_CACHE_DIR", "/tmp/uv-cache")
        return env

    def _declared_python_packages(self) -> dict[str, str]:
        packages: dict[str, str] = {}
        for file_name in REQUIREMENTS_FILES:
            requirements_path = self.project_root / file_name
            if not requirements_path.exists():
                continue
            packages.update(parse_requirement_names(requirements_path.read_text(encoding="utf-8").splitlines()))
        return packages

    def resolve_python(self) -> dict[str, Any]:
        if self.ensure_python_script.exists():
            result = run_command([str(self.ensure_python_script), "--print-path"], cwd=self.project_root)
            if result.ok and result.stdout:
                return {"path": result.stdout, "source": "ensure_python.sh", "error": ""}
            if result.stderr:
                return {"path": "", "source": "ensure_python.sh", "error": result.stderr}

        fallback = self.project_root / ".venv" / "bin" / "python"
        if fallback.exists():
            return {"path": str(fallback), "source": "repo_.venv", "error": ""}
        return {"path": "", "source": "missing", "error": "No compatible Python interpreter found."}

    def python_version(self, python_path: str) -> str:
        result = run_command(
            [python_path, "-c", "import sys; print(sys.version.split()[0])"],
            cwd=self.project_root,
        )
        return result.stdout if result.ok else ""

    def list_python_packages(self, python_path: str, outdated: bool = False) -> dict[str, Any]:
        if self.uv_bin:
            command = [self.uv_bin, "pip", "list", "--python", python_path, "--format", "json"]
            if outdated:
                command.append("--outdated")
            result = run_command(command, cwd=self.project_root, env=self._uv_env())
        else:
            command = [python_path, "-m", "pip", "list", "--format=json"]
            if outdated:
                command.insert(-1, "--outdated")
            result = run_command(command, cwd=self.project_root)

        if not result.ok:
            return {
                "available": False,
                "count": 0,
                "packages": [],
                "error": result.stderr or result.stdout or "package listing failed",
            }

        try:
            packages = json.loads(result.stdout or "[]")
        except json.JSONDecodeError as exc:
            return {
                "available": False,
                "count": 0,
                "packages": [],
                "error": f"Invalid package listing JSON: {exc}",
            }

        return {
            "available": True,
            "count": len(packages),
            "packages": packages,
            "error": "",
        }

    def scan_python_environment(self, check_outdated: bool = False) -> dict[str, Any]:
        declared_packages = self._declared_python_packages()
        resolved_python = self.resolve_python()
        python_path = resolved_python["path"]
        scan: dict[str, Any] = {
            "requirements_files": [name for name in REQUIREMENTS_FILES if (self.project_root / name).exists()],
            "declared_packages": declared_packages,
            "declared_package_count": len(declared_packages),
            "interpreter_path": python_path,
            "interpreter_source": resolved_python["source"],
            "interpreter_error": resolved_python["error"],
            "python_version": "",
            "package_manager": "uv" if self.uv_bin else "pip",
            "package_manager_path": self.uv_bin or "",
            "package_listing": {"available": False, "count": 0, "packages": [], "error": ""},
            "required_packages": {},
            "fastapi_ready": False,
        }

        if not python_path:
            for package_name in CRITICAL_PYTHON_PACKAGES:
                normalized = normalize_package_name(package_name)
                scan["required_packages"][normalized] = {
                    "declared": normalized in declared_packages,
                    "installed": False,
                    "installed_version": "",
                    "declared_spec": declared_packages.get(normalized, ""),
                }
            scan["status"] = "missing_interpreter"
            return scan

        scan["python_version"] = self.python_version(python_path)
        installed_listing = self.list_python_packages(python_path)
        scan["package_listing"] = installed_listing

        installed_versions: dict[str, str] = {}
        if installed_listing["available"]:
            for package in installed_listing["packages"]:
                name = normalize_package_name(str(package.get("name", "")))
                version = str(package.get("version", ""))
                if name:
                    installed_versions[name] = version

        for package_name in CRITICAL_PYTHON_PACKAGES:
            normalized = normalize_package_name(package_name)
            scan["required_packages"][normalized] = {
                "declared": normalized in declared_packages,
                "installed": normalized in installed_versions,
                "installed_version": installed_versions.get(normalized, ""),
                "declared_spec": declared_packages.get(normalized, ""),
            }

        fastapi_state = scan["required_packages"]["fastapi"]
        scan["fastapi_ready"] = bool(fastapi_state["declared"] and fastapi_state["installed"])

        if check_outdated:
            scan["outdated"] = self.list_python_packages(python_path, outdated=True)

        if scan["fastapi_ready"]:
            scan["status"] = "ready"
        elif fastapi_state["declared"]:
            scan["status"] = "fastapi_missing_from_environment"
        else:
            scan["status"] = "fastapi_not_declared"
        return scan

    def scan_node_environment(self) -> dict[str, Any]:
        package_json = self.project_root / "package.json"
        npm_path = shutil.which("npm") or ""
        return {
            "package_json_present": package_json.exists(),
            "npm_available": bool(npm_path),
            "npm_path": npm_path,
        }

    def ensure_python_environment(self, apply: bool, include_optional: bool) -> dict[str, Any]:
        command = [str(self.setup_dependencies_script), "--execute", "--install-python"]
        if include_optional:
            command.append("--include-optional")

        result: dict[str, Any] = {
            "requested": True,
            "applied": apply,
            "command": command,
            "status": "planned" if not apply else "failed",
            "stdout": "",
            "stderr": "",
        }
        if not apply:
            return result

        run_result = run_command(command, cwd=self.project_root, env=self._uv_env())
        result["stdout"] = run_result.stdout
        result["stderr"] = run_result.stderr
        result["status"] = "completed" if run_result.ok else "failed"
        return result

    def upgrade_python_dependencies(self, python_path: str, apply: bool, include_optional: bool) -> dict[str, Any]:
        if not python_path:
            return {
                "requested": True,
                "applied": apply,
                "status": "failed",
                "stdout": "",
                "stderr": "No compatible Python interpreter available for upgrades.",
                "commands": [],
            }

        commands: list[list[str]] = []
        if self.uv_bin:
            commands.append(
                [self.uv_bin, "pip", "install", "--python", python_path, "--upgrade", "-r", "requirements.txt"]
            )
            if include_optional and (self.project_root / "requirements-optional.txt").exists():
                commands.append(
                    [
                        self.uv_bin,
                        "pip",
                        "install",
                        "--python",
                        python_path,
                        "--upgrade",
                        "-r",
                        "requirements-optional.txt",
                    ]
                )
        else:
            commands.append([python_path, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"])
            if include_optional and (self.project_root / "requirements-optional.txt").exists():
                commands.append(
                    [python_path, "-m", "pip", "install", "--upgrade", "-r", "requirements-optional.txt"]
                )

        result: dict[str, Any] = {
            "requested": True,
            "applied": apply,
            "status": "planned" if not apply else "completed",
            "commands": commands,
            "runs": [],
        }
        if not apply:
            return result

        for command in commands:
            run_result = run_command(command, cwd=self.project_root, env=self._uv_env())
            result["runs"].append(
                {
                    "command": command,
                    "returncode": run_result.returncode,
                    "stdout": run_result.stdout,
                    "stderr": run_result.stderr,
                }
            )
            if not run_result.ok:
                result["status"] = "failed"
                return result

        return result

    def build_report(
        self,
        *,
        check_outdated: bool,
        ensure_env: bool,
        upgrade_python: bool,
        apply: bool,
        include_optional: bool,
    ) -> dict[str, Any]:
        python_scan = self.scan_python_environment(check_outdated=check_outdated)
        actions: dict[str, Any] = {}

        if ensure_env:
            actions["ensure_env"] = self.ensure_python_environment(apply=apply, include_optional=include_optional)
            python_scan = self.scan_python_environment(check_outdated=check_outdated)

        if upgrade_python:
            actions["upgrade_python"] = self.upgrade_python_dependencies(
                python_scan.get("interpreter_path", ""),
                apply=apply,
                include_optional=include_optional,
            )
            if apply and actions["upgrade_python"]["status"] == "completed":
                python_scan = self.scan_python_environment(check_outdated=check_outdated)

        recommended_actions: list[str] = []
        if not python_scan.get("interpreter_path"):
            recommended_actions.append("Run scripts/setup_dependencies.sh --execute --install-python")
        if not python_scan.get("fastapi_ready"):
            recommended_actions.append("Ensure the repo .venv is present and FastAPI is installed from requirements.txt")
        if check_outdated and python_scan.get("outdated", {}).get("error"):
            recommended_actions.append("Retry outdated dependency checks when network access to package indexes is available")
        if not actions:
            recommended_actions.append("Use --ensure-env to rebuild the canonical Python environment if drift is detected")
            recommended_actions.append("Use --upgrade-python --apply to refresh Python packages against requirements.txt")

        return {
            "generated_at_utc": utcnow(),
            "repo_root": str(self.project_root),
            "python": python_scan,
            "node": self.scan_node_environment(),
            "actions": actions,
            "recommended_actions": recommended_actions,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Aurora dependency scanner and updater")
    parser.add_argument("--scan", action="store_true", help="Collect dependency status (default action)")
    parser.add_argument("--ensure-env", action="store_true", help="Rebuild the canonical Python environment")
    parser.add_argument("--upgrade-python", action="store_true", help="Upgrade Python packages from requirements files")
    parser.add_argument("--include-optional", action="store_true", help="Include requirements-optional.txt when mutating")
    parser.add_argument("--check-outdated", action="store_true", help="Attempt network-backed outdated package checks")
    parser.add_argument("--apply", action="store_true", help="Apply requested mutations instead of reporting the plan")
    parser.add_argument("--output", help="Write the JSON report to this path")
    args = parser.parse_args()

    updater = DependencyAutoUpdater(Path(__file__).resolve().parent.parent)
    report = updater.build_report(
        check_outdated=args.check_outdated,
        ensure_env=args.ensure_env,
        upgrade_python=args.upgrade_python,
        apply=args.apply,
        include_optional=args.include_optional,
    )

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = updater.project_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))

    if not args.apply:
        return 0

    for action in report["actions"].values():
        if action.get("status") == "failed":
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
