#!/usr/bin/env python3
"""GITWiz - Adaptive repo command node.

This consolidated script merges prior prototypes into a single tool capable of
performing environment diagnostics, linting, testing and deployment tasks. The
goal is to keep the repository stable while providing convenient automation for
developers.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class GITWiz:
    """Provide pre-checks, rapid fixes and deployment helpers."""

    def __init__(self, root: Optional[Path] = None) -> None:
        self.project_root = root or Path(__file__).resolve().parent.parent

    # ------------------------------------------------------------------ utils

    def _run(self, cmd: list[str], check: bool = False) -> bool:
        """Run a command in the project root and echo output."""
        print(f"+ {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            text=True,
            capture_output=True,
            shell=False,
            check=False,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")
        return result.returncode == 0

    def _run_python_script(self, script_name: str, *args: str) -> bool:
        script_path = self.project_root / "scripts" / script_name
        return self._run([sys.executable, str(script_path), *args])

    # ----------------------------------------------------------------- actions

    def status(self) -> bool:
        return self._run(["git", "status"])

    def lint_python(self) -> bool:
        """Run flake8 if available."""
        if shutil.which("flake8"):
            return self._run(["flake8"])
        print("flake8 not found; skipping Python lint")
        return True

    def lint_js(self) -> bool:
        if (self.project_root / "package.json").exists():
            return self._run(["npm", "run", "lint"])
        return True

    def test(self) -> bool:
        if (self.project_root / "tests").exists():
            return self._run(["pytest", "-q"])
        return True

    def precheck(self) -> bool:
        """Run repository status, lint and tests."""
        all_passed = True
        all_passed &= self.status()
        all_passed &= self.lint_python()
        all_passed &= self.lint_js()
        all_passed &= self.test()
        return all_passed

    def analyze(self) -> bool:
        """Generate the canonical repository health report."""
        return self._run_python_script("repo_health_monitor.py", "--output", "logs/repo_health_status.json")

    def report(self) -> bool:
        """Print the latest repository health report, generating it if needed."""
        report_path = self.project_root / "logs" / "repo_health_status.json"
        if not report_path.exists() and not self.analyze():
            return False
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print(f"Unable to read health report at {report_path}")
            return False
        print(json.dumps(report, indent=2))
        return True

    def branches(self) -> bool:
        """Run the canonical branch analysis report."""
        return self._run_python_script("branch_manager.py", "--analyze")

    def archives(self, threshold_mb: int = 50, execute: bool = False, archive_dir: str = "archive") -> bool:
        """Run ZIP archive analysis or consolidation through the canonical helper."""
        cmd = ["--threshold-mb", str(threshold_mb), "--archive-dir", archive_dir]
        if execute:
            cmd.append("--execute")
        return self._run_python_script("archive_large_files.py", *cmd)

    def dependencies(
        self,
        *,
        ensure_env: bool = False,
        upgrade_python: bool = False,
        apply: bool = False,
        include_optional: bool = False,
        check_outdated: bool = False,
        output: str = "logs/dependency_status.json",
    ) -> bool:
        """Run the canonical dependency health and upgrade helper."""

        cmd = ["--scan", "--output", output]
        if ensure_env:
            cmd.append("--ensure-env")
        if upgrade_python:
            cmd.append("--upgrade-python")
        if include_optional:
            cmd.append("--include-optional")
        if check_outdated:
            cmd.append("--check-outdated")
        if apply:
            cmd.append("--apply")
        return self._run_python_script("gitwiz_dependency_updater.py", *cmd)

    def optimize(
        self,
        *,
        ensure_python_env: bool = False,
        upgrade_python_deps: bool = False,
        include_optional: bool = False,
        check_outdated: bool = False,
    ) -> bool:
        """Run the canonical maintenance flow."""
        maintenance_script = self.project_root / "scripts" / "scheduled_maintenance.sh"
        cmd = [str(maintenance_script)]
        if ensure_python_env:
            cmd.append("--ensure-python-env")
        if upgrade_python_deps:
            cmd.append("--upgrade-python-deps")
        if include_optional:
            cmd.append("--include-optional")
        if check_outdated:
            cmd.append("--check-outdated")
        return self._run(cmd)

    def fix(self) -> bool:
        """Apply automatic formatting and lint fixes."""
        self._run(["black", "."])
        self._run(["isort", "."])
        if (self.project_root / "package.json").exists():
            self._run(["npx", "eslint", "src", "--fix"])
        return True

    def commit(self, message: str) -> bool:
        self._run(["git", "add", "."], check=True)
        return self._run(["git", "commit", "-m", message])

    def deploy(self) -> bool:
        """Run precheck, commit results and prepare for push."""
        self.precheck()
        self.commit("chore: gitwiz automated deploy")
        return True

    def push(self, branch: str = "main") -> bool:
        """Push the current branch to origin."""
        return self._run(["git", "push", "origin", branch])

    # ------------------------------------------------------------- branch utils

    def branch_list(self) -> bool:
        """List local and remote branches."""
        return self._run(["git", "branch", "-a"])

    def branch_create(self, name: str, base: str = "main") -> bool:
        """Create a new branch from the given base."""
        self._run(["git", "checkout", base], check=True)
        return self._run(["git", "checkout", "-b", name])

    def branch_checkout(self, name: str) -> bool:
        """Switch to the specified branch."""
        return self._run(["git", "checkout", name])

    def branch_delete(self, name: str) -> bool:
        """Delete the specified branch locally."""
        return self._run(["git", "branch", "-d", name])

    def branch_merge(self, source: str, target: str = "main") -> bool:
        """Merge source branch into target."""
        self.branch_checkout(target)
        return self._run(["git", "merge", source], check=True)

    # ------------------------------------------------------------------- PR util

    def create_pr(self, title: Optional[str] = None, body: Optional[str] = None) -> bool:
        """Create a pull request using GitHub CLI if available."""
        if shutil.which("gh"):
            cmd = ["gh", "pr", "create"]
            if title:
                cmd += ["--title", title]
            if body:
                cmd += ["--body", body]
            cmd.append("--fill")
            return self._run(cmd)
        print("GitHub CLI not found; please create the PR manually")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="GITWiz repo management tool")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status")
    sub.add_parser("precheck")
    sub.add_parser("fix")
    sub.add_parser("deploy")
    sub.add_parser("analyze")
    sub.add_parser("report")
    sub.add_parser("branches")
    optimize_p = sub.add_parser("optimize")
    optimize_p.add_argument("--ensure-python-env", action="store_true")
    optimize_p.add_argument("--upgrade-python-deps", action="store_true")
    optimize_p.add_argument("--include-optional", action="store_true")
    optimize_p.add_argument("--check-outdated", action="store_true")
    deps_p = sub.add_parser("dependencies")
    deps_p.add_argument("--ensure-env", action="store_true")
    deps_p.add_argument("--upgrade-python", action="store_true")
    deps_p.add_argument("--include-optional", action="store_true")
    deps_p.add_argument("--check-outdated", action="store_true")
    deps_p.add_argument("--apply", action="store_true")
    deps_p.add_argument("--output", default="logs/dependency_status.json")
    archives_p = sub.add_parser("archives")
    archives_p.add_argument("--threshold-mb", type=int, default=50)
    archives_p.add_argument("--archive-dir", default="archive")
    archives_p.add_argument("--execute", action="store_true")
    push_p = sub.add_parser("push")
    push_p.add_argument("branch", nargs="?", default="main")

    branch_p = sub.add_parser("branch")
    branch_sub = branch_p.add_subparsers(dest="branch_cmd")
    branch_sub.add_parser("list")
    c_p = branch_sub.add_parser("create")
    c_p.add_argument("name")
    c_p.add_argument("--base", default="main")
    co_p = branch_sub.add_parser("checkout")
    co_p.add_argument("name")
    d_p = branch_sub.add_parser("delete")
    d_p.add_argument("name")
    m_p = branch_sub.add_parser("merge")
    m_p.add_argument("source")
    m_p.add_argument("target", nargs="?", default="main")

    pr_p = sub.add_parser("pr")
    pr_p.add_argument("--title")
    pr_p.add_argument("--body")

    args = parser.parse_args()

    wiz = GITWiz()
    success = False

    if args.cmd == "status":
        success = wiz.status()
    elif args.cmd == "precheck":
        success = wiz.precheck()
    elif args.cmd == "fix":
        success = wiz.fix()
    elif args.cmd == "deploy":
        success = wiz.deploy()
    elif args.cmd == "analyze":
        success = wiz.analyze()
    elif args.cmd == "report":
        success = wiz.report()
    elif args.cmd == "branches":
        success = wiz.branches()
    elif args.cmd == "optimize":
        success = wiz.optimize(
            ensure_python_env=args.ensure_python_env,
            upgrade_python_deps=args.upgrade_python_deps,
            include_optional=args.include_optional,
            check_outdated=args.check_outdated,
        )
    elif args.cmd == "dependencies":
        success = wiz.dependencies(
            ensure_env=args.ensure_env,
            upgrade_python=args.upgrade_python,
            apply=args.apply,
            include_optional=args.include_optional,
            check_outdated=args.check_outdated,
            output=args.output,
        )
    elif args.cmd == "archives":
        success = wiz.archives(args.threshold_mb, args.execute, args.archive_dir)
    elif args.cmd == "push":
        success = wiz.push(args.branch)
    elif args.cmd == "branch":
        if args.branch_cmd == "list":
            success = wiz.branch_list()
        elif args.branch_cmd == "create":
            success = wiz.branch_create(args.name, args.base)
        elif args.branch_cmd == "checkout":
            success = wiz.branch_checkout(args.name)
        elif args.branch_cmd == "delete":
            success = wiz.branch_delete(args.name)
        elif args.branch_cmd == "merge":
            success = wiz.branch_merge(args.source, args.target)
        else:
            branch_p.print_help()
            return 1
    elif args.cmd == "pr":
        success = wiz.create_pr(args.title, args.body)
    else:
        parser.print_help()
        return 1

    return 0 if success else 1


if __name__ == "__main__":  # pragma: no cover - script entry point
    try:
        sys.exit(main())
    except RuntimeError as exc:  # Basic error handling to stop on failed cmd
        print(exc)
        sys.exit(1)
