#!/usr/bin/env python3
"""
Aurora CloudBank - Automated Maintenance System
==============================================

Scheduled maintenance workflows for repository optimization and cleanup.
"""

import argparse
import datetime
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import schedule


class MaintenanceScheduler:
    """Automated maintenance and cleanup scheduler."""

    def __init__(self, repo_path: str = "."):
        """Initialize maintenance scheduler.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
        self.setup_logging()
        self.config = self.load_config()

        # Maintenance tasks
        self.tasks = {
            "cleanup_cache": {
                "function": self.cleanup_python_cache,
                "description": "Clean Python cache files",
                "schedule": "daily",
            },
            "cleanup_temp": {
                "function": self.cleanup_temp_files,
                "description": "Clean temporary files and directories",
                "schedule": "daily",
            },
            "optimize_git": {
                "function": self.optimize_git_repo,
                "description": "Optimize git repository (gc, prune)",
                "schedule": "weekly",
            },
            "health_check": {
                "function": self.run_health_check,
                "description": "Run comprehensive health check",
                "schedule": "daily",
            },
            "branch_cleanup": {
                "function": self.cleanup_stale_branches,
                "description": "Clean up stale branches",
                "schedule": "weekly",
            },
            "dependency_check": {
                "function": self.check_dependencies,
                "description": "Check for dependency updates",
                "schedule": "weekly",
            },
            "security_scan": {
                "function": self.security_scan,
                "description": "Run security vulnerability scan",
                "schedule": "weekly",
            },
        }

    def setup_logging(self):
        """Set up logging configuration."""
        log_dir = self.repo_path / ".gitwiz" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "maintenance.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        self.logger = logging.getLogger(__name__)

    def load_config(self) -> Dict:
        """Load maintenance configuration."""
        config_path = self.repo_path / ".gitwiz" / "maintenance_config.json"

        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.error(f"Error loading config: {e}")

        # Default configuration
        default_config = {
            "enabled": True,
            "schedules": {
                "cleanup_cache": "02:00",
                "cleanup_temp": "02:15",
                "health_check": "03:00",
                "optimize_git": "sunday 03:30",
                "branch_cleanup": "sunday 04:00",
                "dependency_check": "monday 09:00",
                "security_scan": "friday 10:00",
            },
            "notifications": {
                "email": None,
                "webhook": None,
                "file": str(self.repo_path / "maintenance.log"),
            },
            "retention": {"logs_days": 30, "reports_days": 90},
        }

        # Save default config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def cleanup_python_cache(self) -> Dict:
        """Clean Python cache files and directories.

        Returns:
            Task result dictionary
        """
        self.logger.info("Starting Python cache cleanup")
        result = {"task": "cleanup_cache", "status": "success", "details": {}}

        try:
            # Find and count .pyc files
            pyc_result = subprocess.run(
                ["find", ".", "-name", "*.pyc", "-type", ""],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            pyc_files = [f for f in pyc_result.stdout.strip().split("\n") if f]
            pyc_count = len(pyc_files)

            # Remove .pyc files
            if pyc_count > 0:
                subprocess.run(
                    ["find", ".", "-name", "*.pyc", "-delete"],
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

            # Find and remove __pycache__ directories
            pycache_result = subprocess.run(
                ["find", ".", "-name", "__pycache__", "-type", "d"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            pycache_dirs = [d for d in pycache_result.stdout.strip().split("\n") if d]
            pycache_count = len(pycache_dirs)

            if pycache_count > 0:
                subprocess.run(
                    [
                        "find",
                        ".",
                        "-name",
                        "__pycache__",
                        "-type",
                        "d",
                        "-exec",
                        "rm",
                        "-r",
                        "{}",
                        "+",
                    ],
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

            result["details"] = {
                "pyc_files_removed": pyc_count,
                "pycache_dirs_removed": pycache_count,
            }

            self.logger.info(
                f"Python cache cleanup complete: {pyc_count} .pyc files, {pycache_count} __pycache__ dirs"
            )

        except (OSError, ValueError, RuntimeError) as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Error in Python cache cleanup: {e}")

        return result

    def cleanup_temp_files(self) -> Dict:
        """Clean temporary files and directories.

        Returns:
            Task result dictionary
        """
        self.logger.info("Starting temporary file cleanup")
        result = {"task": "cleanup_temp", "status": "success", "details": {}}

        try:
            temp_patterns = ["*tmp*", "*temp*", "*.tmp", "*.bak", "*~"]
            removed_count = 0

            for pattern in temp_patterns:
                # Find temp files
                find_result = subprocess.run(
                    [
                        "find",
                        ".",
                        "-name",
                        pattern,
                        "-type",
                        "",
                        "!",
                        "-path",
                        "./.venv/*",
                        "!",
                        "-path",
                        "./.git/*",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

                temp_files = [f for f in find_result.stdout.strip().split("\n") if f]

                # Remove temp files (with confirmation for safety)
                for temp_file in temp_files:
                    temp_path = self.repo_path / temp_file.lstrip("./")
                    if (
                        temp_path.exists()
                        and temp_path.stat().st_size < 100 * 1024 * 1024
                    ):  # Only remove files < 100MB
                        temp_path.unlink()
                        removed_count += 1

            result["details"] = {"temp_files_removed": removed_count}
            self.logger.info(
                f"Temporary file cleanup complete: {removed_count} files removed"
            )

        except (OSError, ValueError, RuntimeError) as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Error in temporary file cleanup: {e}")

        return result

    def optimize_git_repo(self) -> Dict:
        """Optimize git repository with gc and prune.

        Returns:
            Task result dictionary
        """
        self.logger.info("Starting git repository optimization")
        result = {"task": "optimize_git", "status": "success", "details": {}}

        try:
            # Git garbage collection
            gc_result = subprocess.run(
                ["git", "gc", "--aggressive", "--prune=now"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            # Git prune
            prune_result = subprocess.run(
                ["git", "remote", "prune", "origin"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            # Get repository size after optimization
            du_result = subprocess.run(
                ["du", "-sm", ".git"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            git_size_mb = (
                int(du_result.stdout.split()[0]) if du_result.returncode == 0 else 0
            )

            result["details"] = {
                "git_size_mb": git_size_mb,
                "gc_output": gc_result.stdout if gc_result.stdout else "No output",
                "prune_output": (
                    prune_result.stdout if prune_result.stdout else "No output"
                ),
            }

            self.logger.info(f"Git optimization complete: .git size = {git_size_mb}MB")

        except (OSError, ValueError, RuntimeError) as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Error in git optimization: {e}")

        return result

    def run_health_check(self) -> Dict:
        """Run comprehensive health check.

        Returns:
            Task result dictionary
        """
        self.logger.info("Running health check")
        result = {"task": "health_check", "status": "success", "details": {}}

        try:
            # Run health monitor
            health_script = self.repo_path / "scripts" / "aurora_health_monitor.py"

            if health_script.exists():
                health_result = subprocess.run(
                    ["python3", str(health_script, shell=False, check=False), "--check"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                )

                result["details"] = {
                    "health_output": health_result.stdout,
                    "health_score": self.extract_health_score(health_result.stdout),
                }
            else:
                # Basic health check
                size_result = subprocess.run(
                    ["du", "-sm", "."],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )
                files_result = subprocess.run(
                    ["find", ".", "-type", ""],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

                repo_size = (
                    int(size_result.stdout.split()[0])
                    if size_result.returncode == 0
                    else 0
                )
                file_count = (
                    len(files_result.stdout.strip().split("\n"))
                    if files_result.returncode == 0
                    else 0
                )

                result["details"] = {
                    "repository_size_mb": repo_size,
                    "file_count": file_count,
                }

            self.logger.info("Health check complete")

        except (OSError, ValueError, RuntimeError) as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Error in health check: {e}")

        return result

    def cleanup_stale_branches(self) -> Dict:
        """Clean up stale branches.

        Returns:
            Task result dictionary
        """
        self.logger.info("Starting branch cleanup")
        result = {"task": "branch_cleanup", "status": "success", "details": {}}

        try:
            branch_script = self.repo_path / "scripts" / "aurora_branch_manager.py"

            if branch_script.exists():
                # Run branch analysis
                branch_result = subprocess.run(
                    ["python3", str(branch_script, shell=False, check=False), "--analyze"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                )

                result["details"] = {
                    "analysis_output": (
                        branch_result.stdout[:1000] + "..."
                        if len(branch_result.stdout) > 1000
                        else branch_result.stdout
                    )
                }
            else:
                # Basic branch count
                branch_result = subprocess.run(
                    ["git", "branch", "-r"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

                branch_count = len(
                    [
                        line
                        for line in branch_result.stdout.strip().split("\n")
                        if line.strip()
                    ]
                )
                result["details"] = {"branch_count": branch_count}

            self.logger.info("Branch cleanup analysis complete")

        except (OSError, ValueError, RuntimeError) as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Error in branch cleanup: {e}")

        return result

    def check_dependencies(self) -> Dict:
        """Check for dependency updates.

        Returns:
            Task result dictionary
        """
        self.logger.info("Checking dependencies")
        result = {"task": "dependency_check", "status": "success", "details": {}}

        try:
            # Check Python dependencies
            if (self.repo_path / "requirements.txt").exists():
                pip_result = subprocess.run(
                    ["pip", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

                if pip_result.returncode == 0:
                    try:
                        outdated = json.loads(pip_result.stdout)
                        result["details"]["python_outdated"] = len(outdated)
                    except json.JSONDecodeError:
                        result["details"]["python_outdated"] = 0

            # Check Node.js dependencies
            if (self.repo_path / "package.json").exists():
                npm_result = subprocess.run(
                    ["npm", "outdated", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

                # npm outdated returns non-zero when outdated packages exist
                if npm_result.stdout:
                    try:
                        outdated = json.loads(npm_result.stdout)
                        result["details"]["node_outdated"] = len(outdated)
                    except json.JSONDecodeError:
                        result["details"]["node_outdated"] = 0

            self.logger.info("Dependency check complete")

        except (OSError, ValueError, RuntimeError) as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Error in dependency check: {e}")

        return result

    def security_scan(self) -> Dict:
        """Run security vulnerability scan.

        Returns:
            Task result dictionary
        """
        self.logger.info("Running security scan")
        result = {"task": "security_scan", "status": "success", "details": {}}

        try:
            # Python security scan with safety
            if (self.repo_path / "requirements.txt").exists():
                safety_result = subprocess.run(
                    ["pip", "install", "safety"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

                if safety_result.returncode == 0:
                    scan_result = subprocess.run(
                        ["safety", "check", "--json"],
                        capture_output=True,
                        text=True,
                        cwd=self.repo_path,
                        shell=False,
                        check=False,
                    )

                    if scan_result.stdout:
                        try:
                            vulnerabilities = json.loads(scan_result.stdout)
                            result["details"]["python_vulnerabilities"] = len(
                                vulnerabilities
                            )
                        except json.JSONDecodeError:
                            result["details"]["python_vulnerabilities"] = 0

            # Node.js security scan with audit
            if (self.repo_path / "package.json").exists():
                audit_result = subprocess.run(
                    ["npm", "audit", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )

                if audit_result.stdout:
                    try:
                        audit_data = json.loads(audit_result.stdout)
                        result["details"]["node_vulnerabilities"] = (
                            audit_data.get("metadata", {})
                            .get("vulnerabilities", {})
                            .get("total", 0)
                        )
                    except json.JSONDecodeError:
                        result["details"]["node_vulnerabilities"] = 0

            self.logger.info("Security scan complete")

        except (OSError, ValueError, RuntimeError) as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.logger.error(f"Error in security scan: {e}")

        return result

    def extract_health_score(self, output: str) -> float:
        """Extract health score from health check output.

        Args:
            output: Health check output text

        Returns:
            Health score or 0.0 if not found
        """
        import re

        match = re.search(r"Health Score: ([\d.]+)/10", output)
        return float(match.group(1)) if match else 0.0

    def run_task(self, task_name: str) -> Dict:
        """Run a specific maintenance task.

        Args:
            task_name: Name of task to run

        Returns:
            Task result dictionary
        """
        if task_name not in self.tasks:
            return {"task": task_name, "status": "error", "error": "Task not found"}

        task = self.tasks[task_name]
        self.logger.info(f"Running task: {task['description']}")

        start_time = datetime.datetime.now()
        result = task["function"]()
        end_time = datetime.datetime.now()

        result["start_time"] = start_time.isoformat()
        result["end_time"] = end_time.isoformat()
        result["duration_seconds"] = (end_time - start_time).total_seconds()

        # Save task result
        self.save_task_result(result)

        return result

    def save_task_result(self, result: Dict):
        """Save task result to history.

        Args:
            result: Task result dictionary
        """
        results_dir = self.repo_path / ".gitwiz" / "maintenance_results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Save to daily file
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        results_file = results_dir / f"maintenance_{date_str}.json"

        # Load existing results
        daily_results = []
        if results_file.exists():
            try:
                with open(results_file, encoding="utf-8") as f:
                    daily_results = json.load(f)
            except (OSError, ValueError, RuntimeError):
                pass

        daily_results.append(result)

        # Save updated results
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(daily_results, f, indent=2)

    def setup_schedules(self):
        """Set up scheduled tasks."""
        self.logger.info("Setting up maintenance schedules")

        for task_name, task_info in self.tasks.items():
            if task_name not in self.config["schedules"]:
                continue

            schedule_str = self.config["schedules"][task_name]

            if schedule_str == "daily":
                schedule.every().day.at("02:00").do(self.run_task, task_name)
            elif schedule_str.startswith("sunday"):
                time_part = schedule_str.split()[1]
                schedule.every().sunday.at(time_part).do(self.run_task, task_name)
            elif schedule_str.startswith("monday"):
                time_part = schedule_str.split()[1]
                schedule.every().monday.at(time_part).do(self.run_task, task_name)
            elif schedule_str.startswith("friday"):
                time_part = schedule_str.split()[1]
                schedule.every().friday.at(time_part).do(self.run_task, task_name)
            elif ":" in schedule_str:  # Time format
                schedule.every().day.at(schedule_str).do(self.run_task, task_name)

        self.logger.info(f"Scheduled {len(schedule.jobs)} maintenance tasks")

    def run_scheduler(self):
        """Run the maintenance scheduler."""
        self.setup_schedules()

        self.logger.info("Starting maintenance scheduler")

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("Scheduler stopped by user")
                break
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.error(f"Error in scheduler: {e}")
                time.sleep(60)


def main():
    """Main function for maintenance CLI."""
    parser = argparse.ArgumentParser(description="Aurora CloudBank Maintenance System")
    parser.add_argument("--run-task", help="Run specific maintenance task")
    parser.add_argument(
        "--schedule", action="store_true", help="Start maintenance scheduler"
    )
    parser.add_argument(
        "--list-tasks", action="store_true", help="List available tasks"
    )
    parser.add_argument(
        "--test", action="store_true", help="Run all tasks once for testing"
    )

    args = parser.parse_args()

    scheduler = MaintenanceScheduler()

    if args.list_tasks:
        print("Available maintenance tasks:")
        for task_name, task_info in scheduler.tasks.items():
            print(
                f"  {task_name}: {task_info['description']} ({task_info['schedule']})"
            )
        return 0

    elif args.run_task:
        if args.run_task not in scheduler.tasks:
            print(f"Error: Task '{args.run_task}' not found")
            return 1

        print(f"Running task: {args.run_task}")
        result = scheduler.run_task(args.run_task)

        print(f"Status: {result['status']}")
        if result["status"] == "error":
            print(f"Error: {result['error']}")
        else:
            print(f"Details: {result['details']}")

        return 0 if result["status"] == "success" else 1

    elif args.test:
        print("Running all maintenance tasks for testing...")

        for task_name in scheduler.tasks.keys():
            print(f"\n--- Running {task_name} ---")
            result = scheduler.run_task(task_name)
            print(f"Status: {result['status']}")

            if result["status"] == "error":
                print(f"Error: {result['error']}")
            else:
                print(f"Duration: {result['duration_seconds']:.1f}s")

        return 0

    elif args.schedule:
        scheduler.run_scheduler()
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
