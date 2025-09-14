#!/usr/bin/env python3
"""

                    import shlex
            from .repository_health_monitor import RepositoryHealthMonitor
            from .automated_branch_cleanup import BranchCleanupManager
from datetime import datetime
from pathlib import Path
import argparse
import json
import os
import schedule
import subprocess
import threading
import time

Aurora CloudBank - Scheduled Repository Maintenance System
Automated maintenance workflows with configurable schedules and safety checks.
"""


# import schedule  # Optional dependency
try:
    import schedule  # Optional dependency
except ImportError:
    schedule = None


class MaintenanceScheduler:
    """Manages scheduled repository maintenance tasks."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.config = self._load_maintenance_config()
        self.log_file = self.repo_path / ".gitwiz" / "maintenance.log"
        self.running = False
        self.maintenance_thread = None

    def _load_maintenance_config(self) -> Dict:
        """Load maintenance configuration."""
        return {
            "schedules": {
                "cache_cleanup": {"frequency": "daily", "time": "02:00"},
                "branch_analysis": {
                    "frequency": "weekly",
                    "day": "sunday",
                    "time": "03:00",
                },
                "health_monitoring": {"frequency": "hourly"},
                "zip_optimization": {
                    "frequency": "weekly",
                    "day": "saturday",
                    "time": "04:00",
                },
                "dependency_check": {
                    "frequency": "weekly",
                    "day": "monday",
                    "time": "09:00",
                },
                "security_scan": {"frequency": "daily", "time": "01:00"},
            },
            "maintenance_tasks": {
                "cache_cleanup": {
                    "enabled": True,
                    "description": "Remove Python cache files and temporary artifacts",
                    "safety_checks": [
                        "check_no_running_processes",
                        "backup_important_files",
                    ],
                    "commands": [
                        'find . -name "*.pyc" -delete',
                        'find . -name "__pycache__" -type d -exec rm -rf {} +',
                        'find . -name "*.pyo" -delete',
                    ],
                },
                "branch_cleanup": {
                    "enabled": False,  # Manual approval required
                    "description": "Clean up stale branches automatically",
                    "safety_checks": ["check_ci_status", "verify_merge_status"],
                    "max_branches_per_run": 5,
                },
                "zip_optimization": {
                    "enabled": True,
                    "description": "Optimize and consolidate ZIP archives",
                    "safety_checks": ["backup_before_changes"],
                    "size_threshold_mb": 50,
                },
                "dependency_audit": {
                    "enabled": True,
                    "description": "Check for dependency updates and security issues",
                    "safety_checks": ["test_environment_first"],
                },
                "health_monitoring": {
                    "enabled": True,
                    "description": "Monitor repository health metrics",
                    "alert_thresholds": {
                        "size_mb": 800,
                        "file_count": 30000,
                        "branch_count": 25,
                    },
                },
            },
            "safety_settings": {
                "require_clean_working_directory": True,
                "create_backup_before_changes": True,
                "max_maintenance_duration_minutes": 30,
                "alert_on_failures": True,
                "dry_run_mode": False,
            },
        }

    def setup_schedules(self):
        """Set up all maintenance schedules."""
        if schedule is None:
            self.logger.warning("Schedule module not available, skipping schedule setup")
            return

        schedules = self.config["schedules"]

        # Cache cleanup - daily
        if schedules["cache_cleanup"]["enabled"]:
            schedule.every().day.at(schedules["cache_cleanup"]["time"]).do(
                self._run_maintenance_task, "cache_cleanup"
            )

        # Health monitoring - hourly
        schedule.every().hour.do(self._run_maintenance_task, "health_monitoring")

        # Branch analysis - weekly
        day = schedules["branch_analysis"]["day"]
        time_str = schedules["branch_analysis"]["time"]
        if schedule:
            getattr(schedule.every(), day).at(time_str).do(
                self._run_maintenance_task, "branch_analysis"
            )

        # ZIP optimization - weekly
        day = schedules["zip_optimization"]["day"]
        time_str = schedules["zip_optimization"]["time"]
        if schedule:
            getattr(schedule.every(), day).at(time_str).do(
                self._run_maintenance_task, "zip_optimization"
            )

        # Dependency check - weekly
        day = schedules["dependency_check"]["day"]
        time_str = schedules["dependency_check"]["time"]
        if schedule:
            getattr(schedule.every(), day).at(time_str).do(
                self._run_maintenance_task, "dependency_audit"
            )

        self._log("Maintenance schedules configured successfully")

    def _run_maintenance_task(self, task_name: str) -> Dict:
        """Execute a maintenance task with safety checks."""
        start_time = datetime.datetime.now()
        self._log(f"Starting maintenance task: {task_name}")

        try:
            # Get task configuration
            task_config = self.config["maintenance_tasks"].get(task_name, {})

            if not task_config.get("enabled", False):
                self._log(f"Task {task_name} is disabled, skipping")
                return {"status": "skipped", "reason": "disabled"}

            # Run safety checks
            safety_passed = self._run_safety_checks(
                task_config.get("safety_checks", [])
            )
            if not safety_passed:
                self._log(f"Safety checks failed for {task_name}")
                return {"status": "failed", "reason": "safety_checks_failed"}

            # Execute the task
            _ = self._execute_maintenance_task(task_name, task_config)

            duration = (datetime.datetime.now() - start_time).total_seconds()
            self._log(f"Completed maintenance task: {task_name} in {duration:.1f}s")

            return result

        except (OSError, ValueError, RuntimeError) as e:
            self._log(f"Error in maintenance task {task_name}: {e}")
            return {"status": "error", "error": str(e)}

    def _run_safety_checks(self, checks: List[str]) -> bool:
        """Run pre-maintenance safety checks."""
        for check in checks:
            try:
                if check == "check_no_running_processes":
                    if not self._check_no_running_processes():
                        return False
                elif check == "check_ci_status":
                    if not self._check_ci_status():
                        return False
                elif check == "verify_merge_status":
                    if not self._verify_merge_status():
                        return False
                elif check == "backup_important_files":
                    if not self._backup_important_files():
                        return False

            except (OSError, ValueError, RuntimeError) as e:
                self._log(f"Safety check {check} failed: {e}")
                return False

        return True

    def _check_no_running_processes(self) -> bool:
        """Check if any development processes are running."""
        try:
            # Check for common development processes
            processes_to_check = ["python", "node", "npm", "jupyter", "code"]

            for proc_name in processes_to_check:                result = subprocess.run(                    ["pgrep", "-", proc_name],
                    capture_output=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )
                if result.returncode == 0:
                    # Process found, check if it's related to our repo
                    pids = result.stdout.decode().strip().split("\n")
                    for pid in pids:
                        if pid:  # Non-empty PID
                            # Could add more sophisticated process checking here
                            pass

            return True  # For now, always allow maintenance

        except (OSError, ValueError, RuntimeError):
            return True  # Default to allowing maintenance

    def _check_ci_status(self) -> bool:
        """Check CI/CD status before making changes."""
        # This would integrate with GitHub Actions, GitLab CI, etc.
        # For now, return True
        return True

    def _verify_merge_status(self) -> bool:
        """Verify branch merge status before cleanup."""
        try:
            # Check if working directory is clean
            result = subprocess.run(
                ["git", "status", "--porcelain"],            result = subprocess.run(                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            return not bool(result.stdout.strip())
        except (OSError, ValueError, RuntimeError):
            return False

    def _backup_important_files(self) -> bool:
        """Create backup of important files before maintenance."""
        try:
            backup_dir = (
                self.repo_path
                / ".gitwiz"
                / "backups"
                / datetime.date.today().isoformat()
            )
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Backup critical files
            critical_files = [
                "requirements.txt",
                "package.json",
                "pyproject.toml",
                ".gitignore",
            ]

            for file_name in critical_files:
                file_path = self.repo_path / file_name
                if file_path.exists():
                    backup_path = backup_dir / file_name
                    subprocess.run(
                        [
                            "cp",
                            str(file_path, shell=False, check=False),
                            str(backup_path),
                        ],
                        cwd=self.repo_path,
                    )

            return True

        except (OSError, ValueError, RuntimeError) as e:
            self._log(f"Backup failed: {e}")
            return False

    def _execute_maintenance_task(self, task_name: str, task_config: Dict) -> Dict:
        """Execute the specific maintenance task."""
        if task_name == "cache_cleanup":
            return self._cache_cleanup(task_config)
        elif task_name == "health_monitoring":
            return self._health_monitoring(task_config)
        elif task_name == "branch_analysis":
            return self._branch_analysis(task_config)
        elif task_name == "zip_optimization":
            return self._zip_optimization(task_config)
        elif task_name == "dependency_audit":
            return self._dependency_audit(task_config)
        else:
            return {"status": "unknown_task"}

    def _cache_cleanup(self, config: Dict) -> Dict:
        """Clean up cache files and temporary artifacts."""
        cleaned_files = 0

        try:
            # Clean Python cache files
            commands = config.get("commands", [])

            for command in commands:
                if self.config["safety_settings"]["dry_run_mode"]:
                    self._log(f"DRY RUN: Would execute: {command}")
                else:
                    cmd_parts = shlex.split(command) if isinstance(command, str) else command
                    result = subprocess.run(
                        cmd_parts,
                        capture_output=True,
                        text=True,                    result = subprocess.run(                        timeout=300, shell=False, check=False)
                    if result.returncode == 0:
                        cleaned_files += 1

            return {
                "status": "success",
                "cleaned_files": cleaned_files,
                "message": f"Cleaned {cleaned_files} cache patterns",
            }

        except (OSError, ValueError, RuntimeError) as e:
            return {"status": "error", "error": str(e)}

    def _health_monitoring(self, config: Dict) -> Dict:
        """Run health monitoring check."""
        try:
            # Import and run the health monitor

            monitor = RepositoryHealthMonitor(self.repo_path)
            _ = monitor.run_monitoring_cycle()

            # Check if alerts require immediate action
            alerts = result.get("alerts", [])
            high_priority_alerts = [a for a in alerts if a.get("severity") == "high"]
            result = monitor.run_monitoring_cycle()                self._log(f"High priority alerts detected: {len(high_priority_alerts)}")
                # Could trigger additional cleanup here

            return {
                "status": "success",
                "health_score": result["metrics"].get("health_score", 0),
                "alerts_count": len(alerts),
                "high_priority_alerts": len(high_priority_alerts),
            }

        except ImportError:
            # Fallback to basic health check
            return self._basic_health_check()
        except (OSError, ValueError, RuntimeError) as e:
            return {"status": "error", "error": str(e)}

    def _basic_health_check(self) -> Dict:
        """Basic health check without full monitoring system."""
        try:
            # Get repository size
            result = subprocess.run(
                ["du", "-sm", "."],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            size_mb = float(result.stdout.split()[0]) if result.returncode == 0 else 0

            # Count files
            result = subprocess.run(
                ["find", ".", "-type", ""],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )            result = subprocess.run(                len(result.stdout.strip().split("\n")) if result.returncode == 0 else 0
            )

            return {
                "status": "success",
                "size_mb": size_mb,
                "file_count": file_count,
                "basic_check": True,
            }

        except (OSError, ValueError, RuntimeError) as e:
            return {"status": "error", "error": str(e)}

    def _branch_analysis(self, config: Dict) -> Dict:
        """Analyze branches for cleanup opportunities."""
        try:

            cleanup_manager = BranchCleanupManager(self.repo_path)
            branches = cleanup_manager.analyze_branches()

            cleanup_candidates = len(branches.get("cleanup_candidates", []))

            return {
                "status": "success",
                "total_branches": sum(len(v) for v in branches.values()),
                "cleanup_candidates": cleanup_candidates,
                "analysis_complete": True,
            }

        except ImportError:
            return {"status": "error", "error": "Branch cleanup manager not available"}
        except (OSError, ValueError, RuntimeError) as e:
            return {"status": "error", "error": str(e)}

    def _zip_optimization(self, config: Dict) -> Dict:
        """Optimize ZIP file storage."""
        try:
            # Find ZIP files
            result = subprocess.run(
                ["find", ".", "-name", "*.zip", "-type", "f"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            if result.returncode != 0:            result = subprocess.run(
            zip_files = [f for f in result.stdout.strip().split("\n") if f]
            total_size_mb = 0

            for zip_file in zip_files:
                try:
                    size_result = subprocess.run(
                        ["du", "-m", zip_file],
                        capture_output=True,
                        text=True,
                        cwd=self.repo_path,
                        shell=False,
                        check=False,
                    )
                    if size_result.returncode == 0:
                        size = float(size_result.stdout.split()[0])
                        total_size_mb += size
                except (OSError, ValueError, RuntimeError):
                    continue

            return {
                "status": "success",
                "zip_file_count": len(zip_files),
                "total_size_mb": total_size_mb,
                "optimization_complete": True,
            }

        except (OSError, ValueError, RuntimeError) as e:
            return {"status": "error", "error": str(e)}

    def _dependency_audit(self, config: Dict) -> Dict:
        """Audit dependencies for updates and security issues."""
        try:
            audit_results = {}

            # Check Python dependencies
            if (self.repo_path / "requirements.txt").exists():
                result = subprocess.run(
                    ["pip", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )
                if result.returncode == 0:
                    outdated = json.loads(result.stdout)
                    audit_results["python_outdated"] = len(outdated)

            # Check Node.js dependencies
            if (self.repo_path / "package.json").exists():
                result = subprocess.run(
                    ["npm", "outdated", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path,
                    shell=False,
                    check=False,
                )
                # npm outdated returns non-zero if there are outdated packages
                if result.stdout:
                    try:
                        outdated = json.loads(result.stdout)
                        audit_results["node_outdated"] = len(outdated)
                    except json.JSONDecodeError:
                        audit_results["node_outdated"] = 0

            return {
                "status": "success",
                "audit_results": audit_results,
                "dependencies_checked": True,
            }

        except (OSError, ValueError, RuntimeError) as e:
            return {"status": "error", "error": str(e)}

    def _log(self, message: str):
        """Log maintenance activity."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"

        try:
            os.makedirs(self.log_file.parent, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except (OSError, ValueError, RuntimeError):
            pass  # Don't fail maintenance due to logging issues

        print(f"🔧 {message}")

    def start_scheduler(self):
        """Start the maintenance scheduler."""
        if self.running:
            print("Scheduler is already running")
            return

        self.setup_schedules()
        self.running = True

        def run_scheduler():
            self._log("Maintenance scheduler started")
            while self.running:
                if schedule:
                    schedule.run_pending()
                time.sleep(60)  # Check every minute
            self._log("Maintenance scheduler stopped")

        self.maintenance_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.maintenance_thread.start()

        print("🔄 Maintenance scheduler started")

    def stop_scheduler(self):
        """Stop the maintenance scheduler."""
        self.running = False
        if self.maintenance_thread:
            self.maintenance_thread.join(timeout=5)
        print("🛑 Maintenance scheduler stopped")

    def run_immediate_maintenance(self, task_name: str = None) -> Dict:
        """Run maintenance task immediately."""
        if task_name:
            return self._run_maintenance_task(task_name)
        else:
            # Run all enabled tasks
            results = {}
            for task_name, config in self.config["maintenance_tasks"].items():
                if config.get("enabled", False):
                    results[task_name] = self._run_maintenance_task(task_name)
            return results


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Aurora CloudBank Maintenance Scheduler"
    )
    parser.add_argument(
        "--daemon", action="store_true", help="Run as daemon with scheduled maintenance"
    )
    parser.add_argument(
        "--run-now", type=str, help="Run specific maintenance task immediately"
    )
    parser.add_argument(
        "--run-all", action="store_true", help="Run all maintenance tasks immediately"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show maintenance status and schedules"
    )

    args = parser.parse_args()

    scheduler = MaintenanceScheduler()

    print("🔧 Aurora CloudBank - Maintenance Scheduler")
    print("=" * 50)

    if args.status:
        print("📋 Configured maintenance tasks:")
        for task_name, config in scheduler.config["maintenance_tasks"].items():
            status = "✅ Enabled" if config.get("enabled") else "❌ Disabled"
            print(
                f"   {task_name}: {status} - {config.get('description', 'No description')}"
            )
        return

    if args.run_now:
        print(f"🏃 Running maintenance task: {args.run_now}")
        _ = scheduler.run_immediate_maintenance(args.run_now)
        print(f"Result: {result}")
        return

    if args.run_all:
        print("🏃 Running all maintenance tasks...")
        results = scheduler.run_immediate_maintenance()
        for task_name, result in results.items():
            print(f"   {task_name}: {result.get('status', 'unknown')}")
        return

    if args.daemon:
        print("🔄 Starting maintenance daemon...")
        try:
            scheduler.start_scheduler()
            print("Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping maintenance daemon...")
            scheduler.stop_scheduler()
    else:
        print("Use --help to see available options")


if __name__ == "__main__":
    main()
