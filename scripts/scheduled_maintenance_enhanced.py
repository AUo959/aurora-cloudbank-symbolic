#!/usr/bin/env python3
"""
Aurora CloudBank - Scheduled Maintenance System
Automated repository maintenance with intelligent scheduling
"""

import datetime
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

import schedule


@dataclass
class MaintenanceTask:
    """Maintenance task definition"""
    name: str
    description: str
    function: Callable
    schedule_type: str  # 'daily', 'weekly', 'monthly'
    schedule_time: str  # '02:00', 'sunday', etc.
    enabled: bool = True
    last_run: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0


class ScheduledMaintenanceSystem:
    """Comprehensive scheduled maintenance system"""

    def __init__(self, config_path: str = "config/maintenance.json"):
        self.config = self._load_config(config_path)
        self.log_file = "logs/maintenance.log"
        self.tasks = self._initialize_tasks()
        self._setup_schedules()

    def _load_config(self, config_path: str) -> Dict:
        """Load maintenance configuration"""
        try:
            with open(config_path, 'r', encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_config()

    def _default_config(self) -> Dict:
        """Default maintenance configuration"""
        return {
            "tasks": {
                "cache_cleanup": {"enabled": True, "schedule": "daily@02:00"},
                "branch_analysis": {"enabled": True, "schedule": "daily@03:00"},
                "health_check": {"enabled": True, "schedule": "daily@04:00"},
                "dependency_check": {"enabled": True, "schedule": "weekly@sunday@01:00"},
                "large_file_audit": {"enabled": True, "schedule": "weekly@monday@02:00"},
                "backup_cleanup": {"enabled": True, "schedule": "monthly@1st@03:00"}
            },
            "limits": {
                "max_cache_files": 50,
                "max_branches_to_analyze": 20,
                "max_old_backups": 5
            },
            "notifications": {
                "email_on_failure": True,
                "slack_webhook": None
            }
        }

    def _initialize_tasks(self) -> Dict[str, MaintenanceTask]:
        """Initialize maintenance tasks"""
        tasks = {}

        # Cache cleanup task
        tasks['cache_cleanup'] = MaintenanceTask(
            name="Cache Cleanup",
            description="Remove Python cache files and temporary build artifacts",
            function=self._task_cache_cleanup,
            schedule_type="daily",
            schedule_time="02:00"
        )

        # Branch analysis task
        tasks['branch_analysis'] = MaintenanceTask(
            name="Branch Analysis",
            description="Analyze and report on stale branches",
            function=self._task_branch_analysis,
            schedule_type="daily",
            schedule_time="03:00"
        )

        # Health check task
        tasks['health_check'] = MaintenanceTask(
            name="Health Check",
            description="Comprehensive repository health assessment",
            function=self._task_health_check,
            schedule_type="daily",
            schedule_time="04:00"
        )

        # Dependency check task
        tasks['dependency_check'] = MaintenanceTask(
            name="Dependency Check",
            description="Check for outdated dependencies and security issues",
            function=self._task_dependency_check,
            schedule_type="weekly",
            schedule_time="sunday"
        )

        # Large file audit task
        tasks['large_file_audit'] = MaintenanceTask(
            name="Large File Audit",
            description="Identify and report large files that should be archived",
            function=self._task_large_file_audit,
            schedule_type="weekly",
            schedule_time="monday"
        )

        # Backup cleanup task
        tasks['backup_cleanup'] = MaintenanceTask(
            name="Backup Cleanup",
            description="Clean up old backup files and temporary directories",
            function=self._task_backup_cleanup,
            schedule_type="monthly",
            schedule_time="1st"
        )

        return tasks

    def _setup_schedules(self):
        """Set up scheduled tasks"""
        for task_name, task in self.tasks.items():
            if not task.enabled:
                continue

            if task.schedule_type == "daily":
                schedule.every().day.at(task.schedule_time).do(
                    self._run_task, task_name
                )
            elif task.schedule_type == "weekly":
                day = task.schedule_time.lower()
                getattr(schedule.every(), day).at("02:00").do(
                    self._run_task, task_name
                )
            elif task.schedule_type == "monthly":
                # For monthly tasks, we'll check daily and run on the first day
                schedule.every().day.at("01:00").do(
                    self._check_monthly_task, task_name
                )

    def _run_task(self, task_name: str):
        """Run a specific maintenance task"""
        task = self.tasks[task_name]
        start_time = datetime.datetime.now()

        self._log(f"Starting task: {task.name}")

        try:
            result = task.function()
            task.success_count += 1
            task.last_run = start_time.isoformat()

            duration = (datetime.datetime.now() - start_time).total_seconds()
            self._log(f"Task completed successfully: {task.name} ({duration:.1f}s)")

            return True

        except (OSError, ValueError, RuntimeError) as e:
            task.failure_count += 1
            error_msg = f"Task failed: {task.name} - {str(e)}"
            self._log(error_msg)
            self._send_failure_notification(task.name, str(e))

            return False

    def _check_monthly_task(self, task_name: str):
        """Check if monthly task should run"""
        now = datetime.datetime.now()
        if now.day == 1:  # First day of month
            self._run_task(task_name)

    def _task_cache_cleanup(self) -> Dict:
        """Clean up cache files and temporary artifacts"""
        results = {
            'pyc_files_removed': 0,
            'pycache_dirs_removed': 0,
            'temp_files_removed': 0,
            'space_freed_mb': 0.0
        }

        # Get initial size
        initial_size = self._get_dir_size('.')

        # Remove .pyc files
        try:
            _ = subprocess.run(['find', '.', '-name', '*.pyc', '-delete'],
                               capture_output=True, text=True, shell=False, check=False)
            if result.returncode == 0:
                # Count would need to be tracked differently since files are deleted
                results['pyc_files_removed'] = "unknown"
        except subprocess.CalledProcessError:
            pass

        # Remove __pycache__ directories
        try:
            _ = subprocess.run(['find', '.', '-name', '__pycache__', '-type', 'd',
                                '-exec', 'rm', '-r', '{}', '+'],
                               capture_output=True, text=True, shell=False, check=False)
            if result.returncode == 0:
                results['pycache_dirs_removed'] = "cleaned"
        except subprocess.CalledProcessError:
            pass

        # Remove temporary files
        temp_patterns = ['*.tmp', '*.temp', '*~', '.DS_Store']
        for pattern in temp_patterns:
            try:
                subprocess.run(['find', '.', '-name', pattern, '-delete'],
                               capture_output=True, shell=False, check=False)
            except subprocess.CalledProcessError:
                pass

        # Calculate space freed
        final_size = self._get_dir_size('.')
        results['space_freed_mb'] = max(0, (initial_size - final_size) / (1024 * 1024))

        self._log(f"Cache cleanup completed: {results['space_freed_mb']:.1f}MB freed")
        return results

    def _task_branch_analysis(self) -> Dict:
        """Analyze branches and identify cleanup candidates"""
        results = {
            'total_branches': 0,
            'stale_branches': 0,
            'merged_branches': 0,
            'recommendations': []
        }

        try:
            # Get branch information
            cmd = ['git', 'branch', '-r']
            _ = subprocess.run(cmd, capture_output=True, text=True, check=True)

            branches = [line.strip() for line in result.stdout.split('\n')
                        if line.strip() and 'origin/HEAD' not in line]
            results['total_branches'] = len(branches)

            # Analyze each branch (simplified version)
            stale_count = 0
            merged_count = 0

            for branch in branches[:20]:  # Limit analysis
                branch_name = branch.replace('origin/', '')

                # Check if merged (simplified)
                try:
                    merge_check = subprocess.run([
                        'git', 'merge-base', '--is-ancestor',
                        branch, 'origin/main'
                    ], capture_output=True, shell=False, check=False)

                    if merge_check.returncode == 0:
                        merged_count += 1

                        # Check if old
                        age_check = subprocess.run([
                            'git', 'log', '-1', '--format=%ct', branch
                        ], capture_output=True, text=True, shell=False, check=False)

                        if age_check.returncode == 0:
                            commit_time = int(age_check.stdout.strip())
                            age_days = (time.time() - commit_time) / (24 * 3600)

                            if age_days > 7:  # Merged and older than a week
                                stale_count += 1
                                results['recommendations'].append(
                                    f"Consider deleting merged branch: {branch_name}"
                                )

                except subprocess.CalledProcessError:
                    continue

            results['stale_branches'] = stale_count
            results['merged_branches'] = merged_count

        except subprocess.CalledProcessError as e:
            self._log(f"Branch analysis failed: {e}")

        return results

    def _task_health_check(self) -> Dict:
        """Run comprehensive health check"""
        results = {
            'repo_size_mb': 0,
            'file_count': 0,
            'health_score': 0.0,
            'issues': []
        }

        # Get repository size
        try:
            _ = subprocess.run(['du', '-sm', '.'], capture_output=True, text=True, shell=False, check=False)
            results['repo_size_mb'] = float(result.stdout.split()[0])
        except (subprocess.CalledProcessError, ValueError):
            results['repo_size_mb'] = 0

        # Get file count
        try:
            _ = subprocess.run(['find', '.', '-type', ''], capture_output=True, text=True, shell=False, check=False)
            results['file_count'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        except subprocess.CalledProcessError:
            results['file_count'] = 0

        # Calculate basic health score
        score = 10.0

        if results['repo_size_mb'] > 800:
            score -= 2.0
            results['issues'].append("Repository size is large")

        if results['file_count'] > 30000:
            score -= 1.5
            results['issues'].append("High file count")

        results['health_score'] = max(0, score)

        return results

    def _task_dependency_check(self) -> Dict:
        """Check dependencies for updates and security issues"""
        results = {
            'outdated_packages': [],
            'security_issues': [],
            'recommendations': []
        }

        # Check Python dependencies
        if os.path.exists('requirements.txt'):
            try:
                # This would typically use pip-audit or safety
                _ = subprocess.run(['pip', 'list', '--outdated'],
                                   capture_output=True, text=True, shell=False, check=False)
                if result.returncode == 0 and result.stdout.strip():
                    results['outdated_packages'] = ["Some packages are outdated"]
                    results['recommendations'].append("Review and update Python packages")
            except subprocess.CalledProcessError:
                pass

        # Check Node.js dependencies
        if os.path.exists('package.json'):
            try:
                _ = subprocess.run(['npm', 'outdated'],
                                   capture_output=True, text=True, shell=False, check=False)
                if result.returncode != 0:  # npm outdated returns non-zero if outdated packages exist
                    results['outdated_packages'].append("Some npm packages are outdated")
                    results['recommendations'].append("Review and update npm packages")
            except subprocess.CalledProcessError:
                pass

        return results

    def _task_large_file_audit(self) -> Dict:
        """Audit large files that should be archived"""
        results = {
            'large_files': [],
            'total_size_mb': 0.0,
            'recommendations': []
        }

        try:
            # Find files larger than 50MB
            cmd = ['find', '.', '-type', '', '-size', '+50M']
            _ = subprocess.run(cmd, capture_output=True, text=True, shell=False, check=False)

            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue

                # Get file size
                try:
                    size_result = subprocess.run(['du', '-m', line],
                                                 capture_output=True, text=True, shell=False, check=False)
                    size_mb = float(size_result.stdout.split()[0])

                    results['large_files'].append({
                        'path': line,
                        'size_mb': size_mb
                    })
                    results['total_size_mb'] += size_mb

                except (subprocess.CalledProcessError, ValueError):
                    continue

            if results['large_files']:
                results['recommendations'].append(
                    f"Consider archiving {len(results['large_files'])} large files "
                    f"({results['total_size_mb']:.1f}MB total)"
                )

        except subprocess.CalledProcessError:
            pass

        return results

    def _task_backup_cleanup(self) -> Dict:
        """Clean up old backup files and directories"""
        results = {
            'backup_files_removed': 0,
            'backup_dirs_cleaned': 0,
            'space_freed_mb': 0.0
        }

        # This would implement backup cleanup logic
        # For now, just return empty results
        results['backup_files_removed'] = 0
        results['backup_dirs_cleaned'] = 0
        results['space_freed_mb'] = 0.0

        return results

    def _get_dir_size(self, path: str) -> int:
        """Get directory size in bytes"""
        try:
            _ = subprocess.run(['du', '-sb', path], capture_output=True, text=True, shell=False, check=False)
            return int(result.stdout.split()[0])
        except (subprocess.CalledProcessError, ValueError):
            return 0

    def _log(self, message: str):
        """Log maintenance message"""
        timestamp = datetime.datetime.now().isoformat()
        log_message = f"[{timestamp}] {message}"

        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        with open(self.log_file, 'a', encoding="utf-8") as f:
            f.write(log_message + '\n')

        print(log_message)

    def _send_failure_notification(self, task_name: str, error: str):
        """Send notification for task failure"""
        if self.config.get('notifications', {}).get('email_on_failure'):
            # Would implement email notification
            self._log(f"Would send email notification for failed task: {task_name}")

    def run_scheduler(self):
        """Run the maintenance scheduler"""
        self._log("🔄 Starting maintenance scheduler...")

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self._log("👋 Maintenance scheduler stopped by user")
                break
            except (OSError, ValueError, RuntimeError) as e:
                self._log(f"❌ Scheduler error: {e}")
                time.sleep(60)

    def run_task_now(self, task_name: str):
        """Run a specific task immediately"""
        if task_name not in self.tasks:
            print(f"❌ Unknown task: {task_name}")
            return False

        return self._run_task(task_name)

    def get_task_status(self) -> Dict:
        """Get status of all maintenance tasks"""
        status = {}
        for name, task in self.tasks.items():
            status[name] = {
                'enabled': task.enabled,
                'last_run': task.last_run,
                'success_count': task.success_count,
                'failure_count': task.failure_count,
                'description': task.description
            }
        return status


def main():
    """Main maintenance function"""
    import argparse

    parser = argparse.ArgumentParser(description='Scheduled maintenance system')
    parser.add_argument('--daemon', action='store_true',
                        help='Run as daemon (continuous scheduling)')
    parser.add_argument('--run-task', type=str,
                        help='Run specific task now')
    parser.add_argument('--status', action='store_true',
                        help='Show task status')

    args = parser.parse_args()

    maintenance = ScheduledMaintenanceSystem()

    if args.status:
        status = maintenance.get_task_status()
        print("\n📊 Maintenance Task Status:")
        print("=" * 50)
        for name, info in status.items():
            print(f"\n{name}:")
            print(f"  Enabled: {info['enabled']}")
            print(f"  Last Run: {info['last_run'] or 'Never'}")
            print(f"  Success/Failures: {info['success_count']}/{info['failure_count']}")
            print(f"  Description: {info['description']}")

    elif args.run_task:
        print(f"🔧 Running task: {args.run_task}")
        success = maintenance.run_task_now(args.run_task)
        if success:
            print("✅ Task completed successfully")
        else:
            print("❌ Task failed")

    elif args.daemon:
        maintenance.run_scheduler()

    else:
        print("Use --daemon to start scheduler, --run-task to run specific task, or --status to check status")


if __name__ == "__main__":
    main()
