import subprocess

# !/usr/bin/env python3
"""

    import argparse
from datetime import datetime
from pathlib import Path
import json
import schedule
import sys
import threading
import time

GitWiz Automated Maintenance Scheduler
=====================================

Advanced scheduling system for automated code quality maintenance.
Supports daily, weekly, and event-triggered maintenance runs.

Features:
- Configurable schedule patterns
- Background execution
- Comprehensive logging
- Health monitoring
- Integration with GitWiz ecosystem

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""


import json
import logging
import sys
import time

# Configure logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/workspaces/aurora-cloudbank-symbolic/.gitwiz/scheduler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class GitWizScheduler:
    """Advanced scheduler for GitWiz maintenance operations."""

    def __init__(self, project_root: str = "/workspaces/aurora-cloudbank-symbolic"):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / ".gitwiz" / "scheduler_config.json"
        self.status_file = self.project_root / ".gitwiz" / "scheduler_status.json"
        self.log_file = self.project_root / ".gitwiz" / "scheduler.log"

        self.config = self._load_config()
        self.is_running = False
        self.last_run_times = {}
        self.execution_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "avg_execution_time": 0.0,
        }

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load scheduler configuration."""
        default_config = {
            "enabled": True,
            "schedules": {
                "daily_light_maintenance": {
                    "enabled": True,
                    "time": "02:00",
                    "commands": ["status", "lint-scan --target scripts/"],
                    "notify_on_issues": True,
                },
                "weekly_comprehensive": {
                    "enabled": True,
                    "day": "sunday",
                    "time": "03:00",
                    "commands": [
                        "quality-check --auto-fix --output json",
                        "maintenance --aggressive",
                        "workflow --type enhanced",
                    ],
                    "generate_report": True,
                },
                "pre_commit_validation": {
                    "enabled": True,
                    "trigger": "git_hook",
                    "commands": ["lint-scan --detailed"],
                    "fail_on_errors": True,
                },
            },
            "notifications": {
                "enabled": True,
                "methods": ["log", "file"],
                "severity_threshold": "warning",
            },
            "backup": {"enabled": True, "retention_days": 30},
            "performance": {"max_concurrent_jobs": 2, "timeout_minutes": 30},
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **loaded_config}
            except Exception as e:
                logger.warning(f"Failed to load config, using defaults: {e}")

        # Save default config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _save_status(self):
        """Save current scheduler status."""
        status = {
            "is_running": self.is_running,
            "last_update": datetime.utcnow().isoformat(),
            "last_run_times": self.last_run_times,
            "execution_stats": self.execution_stats,
            "next_scheduled_runs": self._get_next_runs(),
        }

        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2)

    def _get_next_runs(self) -> Dict[str, str]:
        """Get next scheduled run times."""
        next_runs = {}
        for job in schedule.jobs:
            next_runs[str(job.job_func)] = str(job.next_run)
        return next_runs

    def _execute_gitwiz_command(self, command: str) -> Dict[str, Any]:
        """Execute a GitWiz command and return results."""
        start_time = datetime.utcnow()

        try:
            # Construct full command
            cmd = [
                sys.executable,
                str(self.project_root / "scripts" / "gitwiz_integrated_command.py"),
            ] + command.split()

            logger.info(f"Executing: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config["performance"]["timeout_minutes"] * 60,
                cwd=self.project_root,
                shell=False,
                check=False,
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            if result.returncode == 0:
                logger.info(f"Command completed successfully in {execution_time:.2f}s")
                return {
                    "success": True,
                    "output": result.stdout,
                    "execution_time": execution_time,
                    "command": command,
                }
            else:
                logger.error(f"Command failed with code {result.returncode}: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "execution_time": execution_time,
                    "command": command,
                }

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return {
                "success": False,
                "error": "Command timed out",
                "execution_time": self.config["performance"]["timeout_minutes"] * 60,
                "command": command,
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "command": command,
            }

    def _run_scheduled_job(self, job_name: str, job_config: Dict[str, Any]):
        """Execute a scheduled maintenance job."""
        logger.info(f"🔄 Starting scheduled job: {job_name}")
        job_start = datetime.utcnow()

        job_results = {
            "job_name": job_name,
            "start_time": job_start.isoformat(),
            "commands": [],
            "overall_success": True,
        }

        # Execute each command in the job
        for command in job_config.get("commands", []):
            cmd_result = self._execute_gitwiz_command(command)
            job_results["commands"].append(cmd_result)

            if not cmd_result["success"]:
                job_results["overall_success"] = False
                if job_config.get("fail_on_errors", False):
                    logger.error(f"Job {job_name} failed on command: {command}")
                    break

        # Update statistics
        execution_time = (datetime.utcnow() - job_start).total_seconds()
        job_results["execution_time"] = execution_time
        job_results["end_time"] = datetime.utcnow().isoformat()

        self.execution_stats["total_runs"] += 1
        if job_results["overall_success"]:
            self.execution_stats["successful_runs"] += 1
        else:
            self.execution_stats["failed_runs"] += 1

        # Update average execution time
        self.execution_stats["avg_execution_time"] = (
            self.execution_stats["avg_execution_time"] * (self.execution_stats["total_runs"] - 1) + execution_time
        ) / self.execution_stats["total_runs"]

        self.last_run_times[job_name] = datetime.utcnow().isoformat()

        # Generate report if requested
        if job_config.get("generate_report", False):
            self._generate_job_report(job_results)

        # Send notifications if configured
        if job_config.get("notify_on_issues", False) and not job_results["overall_success"]:
            self._send_notification(f"Job {job_name} completed with issues", job_results)

        self._save_status()
        logger.info(f"✅ Job {job_name} completed in {execution_time:.2f}s")

    def _generate_job_report(self, job_results: Dict[str, Any]):
        """Generate a detailed report for a job."""
        report_path = (
            self.project_root
            / ".gitwiz"
            / "reports"
            / f"job_{job_results['job_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(job_results, f, indent=2)

        logger.info(f"📊 Job report saved: {report_path}")

    def _send_notification(self, message: str, details: Dict[str, Any]):
        """Send notification about job status."""
        if not self.config["notifications"]["enabled"]:
            return

        timestamp = datetime.utcnow().isoformat()
        notification = {"timestamp": timestamp, "message": message, "details": details}

        # Log notification
        if "log" in self.config["notifications"]["methods"]:
            logger.warning(f"NOTIFICATION: {message}")

        # File notification
        if "file" in self.config["notifications"]["methods"]:
            notif_path = self.project_root / ".gitwiz" / "notifications.json"
            notifications = []

            if notif_path.exists():
                try:
                    with open(notif_path, "r", encoding="utf-8") as f:
                        notifications = json.load(f)
                except (OSError, ValueError, RuntimeError):
                    pass

            notifications.append(notification)

            # Keep only last 100 notifications
            notifications = notifications[-100:]

            with open(notif_path, "w", encoding="utf-8") as f:
                json.dump(notifications, f, indent=2)

    def setup_schedules(self):
        """Set up all configured schedules."""
        if not self.config["enabled"]:
            logger.info("Scheduler is disabled in configuration")
            return

        schedule.clear()  # Clear any existing schedules

        for job_name, job_config in self.config["schedules"].items():
            if not job_config.get("enabled", False):
                continue

            if "time" in job_config:
                # Daily schedule
                schedule.every().day.at(job_config["time"]).do(self._run_scheduled_job, job_name, job_config)
                logger.info(f"📅 Scheduled daily job '{job_name}' at {job_config['time']}")

            elif "day" in job_config and "time" in job_config:
                # Weekly schedule
                day = job_config["day"].lower()
                time = job_config["time"]

                if day == "monday":
                    schedule.every().monday.at(time).do(self._run_scheduled_job, job_name, job_config)
                elif day == "tuesday":
                    schedule.every().tuesday.at(time).do(self._run_scheduled_job, job_name, job_config)
                elif day == "wednesday":
                    schedule.every().wednesday.at(time).do(self._run_scheduled_job, job_name, job_config)
                elif day == "thursday":
                    schedule.every().thursday.at(time).do(self._run_scheduled_job, job_name, job_config)
                elif day == "friday":
                    schedule.every().friday.at(time).do(self._run_scheduled_job, job_name, job_config)
                elif day == "saturday":
                    schedule.every().saturday.at(time).do(self._run_scheduled_job, job_name, job_config)
                elif day == "sunday":
                    schedule.every().sunday.at(time).do(self._run_scheduled_job, job_name, job_config)

                logger.info(f"📅 Scheduled weekly job '{job_name}' on {day} at {time}")

    def start(self):
        """Start the scheduler in background mode."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        logger.info("🚀 Starting GitWiz Maintenance Scheduler...")
        self.is_running = True
        self.setup_schedules()

        def run_scheduler():
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    time.sleep(60)

        # Start in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

        self._save_status()
        logger.info("✅ Scheduler started successfully")

    def stop(self):
        """Stop the scheduler."""
        logger.info("🛑 Stopping GitWiz Maintenance Scheduler...")
        self.is_running = False
        schedule.clear()
        self._save_status()
        logger.info("✅ Scheduler stopped successfully")

    def run_job_now(self, job_name: str):
        """Run a specific job immediately."""
        if job_name not in self.config["schedules"]:
            logger.error(f"Job '{job_name}' not found in configuration")
            return False

        job_config = self.config["schedules"][job_name]
        self._run_scheduled_job(job_name, job_config)
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            "is_running": self.is_running,
            "config_loaded": bool(self.config),
            "scheduled_jobs": len([j for j in self.config["schedules"].values() if j.get("enabled", False)]),
            "execution_stats": self.execution_stats,
            "last_run_times": self.last_run_times,
            "next_runs": self._get_next_runs(),
        }


def main():
    """Main entry point for the scheduler."""

    parser = argparse.ArgumentParser(description="GitWiz Automated Maintenance Scheduler")
    parser.add_argument("command", choices=["start", "stop", "status", "run"], help="Scheduler command")
    parser.add_argument("--job", help="Job name for 'run' command")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode (for 'start' command)")

    args = parser.parse_args()

    scheduler = GitWizScheduler()

    if args.command == "start":
        scheduler.start()
        if args.daemon:
            try:
                while scheduler.is_running:
                    time.sleep(10)
            except KeyboardInterrupt:
                scheduler.stop()
        else:
            logger.info("Scheduler started in background mode")

    elif args.command == "stop":
        scheduler.stop()

    elif args.command == "status":
        status = scheduler.get_status()
        print(json.dumps(status, indent=2))

    elif args.command == "run":
        if not args.job:
            logger.error("Job name required for 'run' command")
            sys.exit(1)
        scheduler.run_job_now(args.job)


if __name__ == "__main__":
    main()
