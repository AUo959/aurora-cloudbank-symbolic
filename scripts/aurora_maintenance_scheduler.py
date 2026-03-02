#!/usr/bin/env python3
"""
Aurora CloudBank Maintenance Scheduler
Automated maintenance workflows and scheduling system
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import time
from datetime import datetime
from typing import List
import threading
try:
    import schedule
except ImportError:
    schedule = None


class MaintenanceScheduler:
    """Automated maintenance scheduling and execution system"""

    def __init__(self, config_file: str = "maintenance_config.json"):
        self.config_file = config_file
        self.running = False
        self.load_config()

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Register maintenance tasks
        self.register_tasks()

    def load_config(self):
        """Load maintenance configuration"""
        default_config = {
            "schedules": {
                "daily_cleanup": {
                    "time": "02:00",
                    "enabled": True,
                    "tasks": ["cleanup_cache", "check_health"],
                },
                "weekly_optimization": {
                    "day": "sunday",
                    "time": "01:00",
                    "enabled": True,
                    "tasks": [
                        "branch_cleanup",
                        "zip_optimization",
                        "memory_compression",
                    ],
                },
                "monthly_audit": {
                    "day": 1,
                    "time": "00:00",
                    "enabled": True,
                    "tasks": ["full_audit", "dependency_update", "health_report"],
                },
            },
            "thresholds": {
                "cache_file_limit": 100,
                "branch_age_days": 90,
                "zip_file_limit": 15,
                "repo_size_limit_mb": 800,
            },
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Save maintenance configuration"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def register_tasks(self):
        """Register scheduled maintenance tasks"""
        if schedule is None:
            self.logger.warning("schedule package not installed; scheduled mode disabled")
            return

        # Daily cleanup at 2 AM
        if self.config["schedules"]["daily_cleanup"]["enabled"]:
            schedule.every().day.at(self.config["schedules"]["daily_cleanup"]["time"]).do(self.run_daily_cleanup)

        # Weekly optimization on Sunday at 1 AM
        if self.config["schedules"]["weekly_optimization"]["enabled"]:
            schedule.every().sunday.at(self.config["schedules"]["weekly_optimization"]["time"]).do(
                self.run_weekly_optimization
            )

        # Monthly audit on the 1st at midnight
        if self.config["schedules"]["monthly_audit"]["enabled"]:
            schedule.every().day.at(self.config["schedules"]["monthly_audit"]["time"]).do(self._run_monthly_if_due)

    def _run_monthly_if_due(self):
        """Run monthly audit only when today's day matches configured monthly day."""
        target_day = int(self.config["schedules"]["monthly_audit"].get("day", 1))
        if datetime.now().day == target_day:
            self.run_monthly_audit()

    def run_daily_cleanup(self):
        """Execute daily cleanup tasks"""
        self.logger.info("Starting daily cleanup maintenance")

        tasks = [
            ("Cleanup Python cache files", self.cleanup_cache_files),
            ("Check repository health", self.check_repository_health),
            ("Remove temporary files", self.cleanup_temp_files),
            ("Update gitignore", self.update_gitignore),
        ]

        results = []
        for task_name, task_func in tasks:
            try:
                self.logger.info(f"Executing: {task_name}")
                result = task_func()
                results.append(f"✅ {task_name}: {result}")
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.error(f"Failed {task_name}: {e}")
                results.append(f"❌ {task_name}: {e}")

        self.log_maintenance_results("Daily Cleanup", results)

    def run_weekly_optimization(self):
        """Execute weekly optimization tasks"""
        self.logger.info("Starting weekly optimization maintenance")

        tasks = [
            ("Branch cleanup", self.cleanup_stale_branches),
            ("ZIP file optimization", self.optimize_zip_files),
            ("Memory compression", self.run_memory_compression),
            ("Dependency audit", self.audit_dependencies),
        ]

        results = []
        for task_name, task_func in tasks:
            try:
                self.logger.info(f"Executing: {task_name}")
                result = task_func()
                results.append(f"✅ {task_name}: {result}")
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.error(f"Failed {task_name}: {e}")
                results.append(f"❌ {task_name}: {e}")

        self.log_maintenance_results("Weekly Optimization", results)

    def run_monthly_audit(self):
        """Execute monthly audit tasks"""
        self.logger.info("Starting monthly audit maintenance")

        tasks = [
            ("Full repository audit", self.full_repository_audit),
            ("Dependency updates", self.update_dependencies),
            ("Health report generation", self.generate_health_report),
            ("Security scan", self.run_security_scan),
        ]

        results = []
        for task_name, task_func in tasks:
            try:
                self.logger.info(f"Executing: {task_name}")
                result = task_func()
                results.append(f"✅ {task_name}: {result}")
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.error(f"Failed {task_name}: {e}")
                results.append(f"❌ {task_name}: {e}")

        self.log_maintenance_results("Monthly Audit", results)

    def cleanup_cache_files(self) -> str:
        """Clean up Python cache files"""
        try:
            # Find and count cache files
            result = subprocess.run(
                ["find", ".", "-name", "*.pyc"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            cache_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

            if cache_files:
                # Remove cache files
                subprocess.run(["find", ".", "-name", "*.pyc", "-delete"], check=True)

            # Remove __pycache__ directories
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
                check=True,
            )

            return f"Removed {len(cache_files)} cache files"
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def check_repository_health(self) -> str:
        """Check current repository health"""
        try:
            # Get repository size
            result = subprocess.run(
                ["du", "-sm", "."],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            size_mb = float(result.stdout.split()[0])

            # Get file count
            result = subprocess.run(
                ["find", ".", "-type", "f"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            file_count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

            # Check against thresholds
            alerts = []
            if size_mb > self.config["thresholds"]["repo_size_limit_mb"]:
                alerts.append(f"Size ({size_mb}MB) exceeds limit")

            if alerts:
                return f"Health check: {len(alerts)} alerts - {', '.join(alerts)}"
            else:
                return f"Health check: OK ({size_mb}MB, {file_count} files)"
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def cleanup_temp_files(self) -> str:
        """Clean up temporary files"""
        try:
            temp_patterns = ["*.tmp", "*.temp", "*~", ".DS_Store", "Thumbs.db"]
            removed_count = 0

            for pattern in temp_patterns:
                result = subprocess.run(
                    ["find", ".", "-name", pattern],
                    capture_output=True,
                    text=True,
                    shell=False,
                    check=False,
                )
                temp_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

                if temp_files:
                    subprocess.run(["find", ".", "-name", pattern, "-delete"], check=True)
                    removed_count += len(temp_files)

            return f"Removed {removed_count} temporary files"
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def cleanup_stale_branches(self) -> str:
        """Clean up stale branches"""
        try:
            # Use the branch manager script
            result = subprocess.run(
                ["python3", "scripts/branch_manager.py", "--cleanup", "--dry-run"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )

            if result.returncode == 0:
                return "Branch cleanup analysis completed"
            else:
                return f"Branch cleanup failed: {result.stderr}"
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def optimize_zip_files(self) -> str:
        """Optimize ZIP files"""
        try:
            # Count current ZIP files
            result = subprocess.run(
                ["find", ".", "-name", "*.zip"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            zip_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

            return f"Found {len(zip_files)} ZIP files for optimization"
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def run_memory_compression(self) -> str:
        """Run memory compression optimization"""
        try:
            # This would run memory compression if script exists
            if os.path.exists("scripts/memory_compression_optimizer.py"):
                result = subprocess.run(
                    ["python3", "scripts/memory_compression_optimizer.py", "--analyze"],
                    capture_output=True,
                    text=True,
                    shell=False,
                    check=False,
                )
                return "Memory compression analysis completed"
            else:
                return "Memory compression script not found"
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def update_gitignore(self) -> str:
        """Update .gitignore with new patterns"""
        try:
            new_patterns = [
                "# Maintenance generated",
                "maintenance_*.log",
                "health_*.json",
                "*.maintenance",
                "# Additional cache patterns",
                "*.pid",
                "*.lock",
            ]

            # Read current .gitignore
            gitignore_path = ".gitignore"
            if os.path.exists(gitignore_path):
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    current_content = f.read()

                # Add new patterns if not already present
                added_count = 0
                for pattern in new_patterns:
                    if pattern not in current_content:
                        current_content += f"\n{pattern}"
                        added_count += 1

                if added_count > 0:
                    with open(gitignore_path, "w", encoding="utf-8") as f:
                        f.write(current_content)
                    return f"Added {added_count} new gitignore patterns"
                else:
                    return "Gitignore up to date"
            else:
                return "No .gitignore file found"
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def full_repository_audit(self) -> str:
        """Perform full repository audit"""
        try:
            tracked = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            tracked_count = len(tracked.stdout.strip().split("\n")) if tracked.stdout.strip() else 0

            dirty = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            dirty_count = len(dirty.stdout.strip().split("\n")) if dirty.stdout.strip() else 0

            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            branch_name = branch.stdout.strip() if branch.returncode == 0 else "unknown"

            health_summary = self.check_repository_health()
            return (
                f"Repository audit complete: branch={branch_name}, tracked_files={tracked_count}, "
                f"dirty_files={dirty_count}, {health_summary}"
            )
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def update_dependencies(self) -> str:
        """Update dependencies"""
        try:
            manifests = []
            req_count = 0
            npm_count = 0

            if os.path.exists("requirements.txt"):
                manifests.append("requirements.txt")
                with open("requirements.txt", "r", encoding="utf-8") as f:
                    req_count = len([line for line in f if line.strip() and not line.strip().startswith("#")])

            if os.path.exists("package.json"):
                manifests.append("package.json")
                with open("package.json", "r", encoding="utf-8") as f:
                    package = json.load(f)
                npm_count = len(package.get("dependencies", {})) + len(package.get("devDependencies", {}))

            tools = [tool for tool in ["python3", "pip", "npm"] if shutil.which(tool)]
            return (
                f"Dependency metadata refreshed: manifests={len(manifests)} "
                f"({', '.join(manifests) if manifests else 'none'}), "
                f"python_requirements={req_count}, npm_dependencies={npm_count}, tools={','.join(tools) or 'none'}"
            )
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def generate_health_report(self) -> str:
        """Generate comprehensive health report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = ".maintenance"
            os.makedirs(report_dir, exist_ok=True)

            report = {
                "generated_at": datetime.now().isoformat(),
                "repository_health": self.check_repository_health(),
                "dependency_audit": self.audit_dependencies(),
                "thresholds": self.config.get("thresholds", {}),
            }

            report_path = os.path.join(report_dir, f"health_report_{timestamp}.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            return f"Health report generated: {report_path}"
        except (OSError, ValueError, RuntimeError) as e:
            return f"Error: {e}"

    def run_security_scan(self) -> str:
        """Run security scan"""
        try:
            scan_script = "scripts/security_audit.sh"
            if os.path.exists(scan_script):
                result = subprocess.run(
                    ["bash", scan_script],
                    capture_output=True,
                    text=True,
                    shell=False,
                    check=False,
                    timeout=300,
                )
                if result.returncode == 0:
                    return "Security scan completed successfully"
                stderr = result.stderr.strip().splitlines()
                tail = stderr[-1] if stderr else "no error output"
                return f"Security scan failed (exit={result.returncode}): {tail}"

            baseline_files = [
                "SECURITY.md",
                ".github/codeql/codeql-config.yml",
                ".security/security_policy.json",
            ]
            present = [path for path in baseline_files if os.path.exists(path)]
            return f"Security baseline check complete: script_missing, baseline_assets={len(present)}"
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as e:
            return f"Error: {e}"

    def audit_dependencies(self) -> str:
        """Audit dependencies for security issues"""
        try:
            results = []

            if shutil.which("python3"):
                pip_check = subprocess.run(
                    ["python3", "-m", "pip", "check"],
                    capture_output=True,
                    text=True,
                    shell=False,
                    check=False,
                )
                if pip_check.returncode == 0:
                    results.append("pip_check=ok")
                else:
                    stderr = pip_check.stderr.strip().splitlines()
                    tail = stderr[-1] if stderr else "dependency issues detected"
                    results.append(f"pip_check=issues({tail})")
            else:
                results.append("pip_check=skipped(no_python3)")

            if os.path.exists("package.json"):
                if shutil.which("npm") and os.path.exists("node_modules"):
                    npm_check = subprocess.run(
                        ["npm", "ls", "--depth=0", "--json"],
                        capture_output=True,
                        text=True,
                        shell=False,
                        check=False,
                    )
                    status = "ok" if npm_check.returncode == 0 else f"issues(exit={npm_check.returncode})"
                    results.append(f"npm_tree={status}")
                else:
                    results.append("npm_tree=skipped(node_modules_missing_or_no_npm)")

            return "Dependency audit complete: " + ", ".join(results)
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as e:
            return f"Error: {e}"

    def log_maintenance_results(self, maintenance_type: str, results: List[str]):
        """Log maintenance results to file"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": maintenance_type,
            "results": results,
        }

        log_file = "maintenance_log.json"

        # Load existing log or create new
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        else:
            log_data = []

        log_data.append(log_entry)

        # Keep only last 100 entries
        log_data = log_data[-100:]

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

        self.logger.info(f"Logged {maintenance_type} results to {log_file}")

    def start_scheduler(self):
        """Start the maintenance scheduler"""
        if schedule is None:
            raise RuntimeError("schedule package is required for --start mode")

        self.running = True
        self.logger.info("Starting maintenance scheduler")

        def scheduler_loop():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()

        return scheduler_thread

    def stop_scheduler(self):
        """Stop the maintenance scheduler"""
        self.running = False
        self.logger.info("Stopping maintenance scheduler")


def main():

    parser = argparse.ArgumentParser(description="Aurora CloudBank Maintenance Scheduler")
    parser.add_argument("--start", action="store_true", help="Start scheduled maintenance")
    parser.add_argument("--daily", action="store_true", help="Run daily cleanup now")
    parser.add_argument("--weekly", action="store_true", help="Run weekly optimization now")
    parser.add_argument("--monthly", action="store_true", help="Run monthly audit now")
    parser.add_argument("--config", help="Configuration file path")

    args = parser.parse_args()

    config_file = args.config or "maintenance_config.json"
    scheduler = MaintenanceScheduler(config_file=config_file)

    if args.daily:
        scheduler.run_daily_cleanup()
    elif args.weekly:
        scheduler.run_weekly_optimization()
    elif args.monthly:
        scheduler.run_monthly_audit()
    elif args.start:
        scheduler.start_scheduler()
        try:
            print("Maintenance scheduler started. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop_scheduler()
            print("Maintenance scheduler stopped.")


if __name__ == "__main__":
    main()
