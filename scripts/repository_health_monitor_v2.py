#!/usr/bin/env python3
"""
Repository Health Monitor v2.0 - Advanced Repository Health Monitoring
Continuous monitoring, alerting, and automated maintenance for git repositories
Created for Aurora CloudBank Symbolic - July 2025
"""

from __future__ import annotations

import argparse
import datetime
import json
import time
from dataclasses import dataclass
from typing import Dict, Optional
from typing import List
from typing import Any
import logging
import subprocess
import sys
from dataclasses import asdict
import hashlib
from pathlib import Path
from typing import Callable
import threading
try:
    import psutil as ps
except ImportError:
    ps = None
import sched
from datetime import timedelta
from collections import defaultdict


# Optional imports
HAS_PSUTIL = ps is not None

try:
    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RepoHealthMonitor")


@dataclass
class HealthMetrics:
    """Repository health metrics snapshot."""

    timestamp: str
    repository_size_mb: float = 0.0
    file_count: int = 0
    git_size_mb: float = 0.0
    branch_count: int = 0
    stale_branches: int = 0
    cache_files_count: int = 0
    temp_files_count: int = 0
    large_files_count: int = 0
    duplicate_files_count: int = 0
    commit_frequency_7d: int = 0
    contributor_count: int = 0
    disk_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    health_score: float = 0.0
    alerts: List[str] = None

    def __post_init__(self):
        if self.alerts is None:
            self.alerts = []


@dataclass
class AlertRule:
    """Health monitoring alert rule."""

    name: str
    condition: Callable[[HealthMetrics], bool]
    severity: str  # 'info', 'warning', 'error', 'critical'
    message: str
    cooldown_minutes: int = 60
    last_triggered: Optional[datetime] = None


class RepositoryHealthMonitor:
    """Advanced repository health monitoring system."""

    def __init__(self, repo_path: str = ".", config_file: Optional[str] = None):
        """Initialize health monitor."""
        self.repo_path = Path(repo_path).resolve()
        self.git_dir = self.repo_path / ".git"
        self.monitor_dir = self.repo_path / ".repohealth"

        # Ensure monitor directory exists
        self.monitor_dir.mkdir(exist_ok=True)

        # Configuration
        self.config = self._load_config(config_file)
        self.thresholds = self.config["thresholds"]

        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics_history: List[HealthMetrics] = []
        self.alert_rules = self._setup_alert_rules()

        # Validate git repository
        if not self.git_dir.exists():
            raise ValueError("Not a git repository: {self.repo_path}")

        logger.info("Repository Health Monitor initialized for: {self.repo_path}")

    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load monitoring configuration."""
        if config_file:
            config_path = Path(config_file)
        else:
            config_path = self.monitor_dir / "config.json"

        default_config = {
            "thresholds": {
                "repository_size_mb": 1000,
                "file_count": 50000,
                "git_size_mb": 500,
                "branch_count": 30,
                "stale_branches": 5,
                "cache_files": 200,
                "temp_files": 100,
                "large_files": 20,
                "disk_usage_percent": 85,
                "memory_usage_mb": 1000,
                "cpu_usage_percent": 80,
                "health_score_min": 0.7,
            },
            "monitoring": {
                "enabled": True,
                "interval_minutes": 30,
                "history_retention_days": 30,
                "auto_cleanup": True,
                "cleanup_threshold_percent": 90,
            },
            "alerts": {
                "enabled": True,
                "console_output": True,
                "log_file": True,
                "webhook_url": None,
                "email_notifications": False,
            },
            "auto_actions": {
                "cleanup_cache_files": True,
                "cleanup_temp_files": True,
                "prune_git_objects": False,
                "archive_old_logs": True,
            },
        }

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                # Deep merge with defaults
                self._deep_merge_config(default_config, user_config)
            except Exception as e:
                logger.warning("Failed to load config from {config_path}: {e}")

        # Save current config
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _deep_merge_config(self, base: Dict, update: Dict) -> None:
        """Deep merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_config(base[key], value)
            else:
                base[key] = value

    def _setup_alert_rules(self) -> List[AlertRule]:
        """Setup monitoring alert rules."""
        rules = [
            AlertRule(
                name="repository_size_exceeded",
                condition=lambda m: m.repository_size_mb > self.thresholds["repository_size_mb"],
                severity="warning",
                message="Repository size exceeded {self.thresholds['repository_size_mb']}MB",
                cooldown_minutes=120,
            ),
            AlertRule(
                name="too_many_files",
                condition=lambda m: m.file_count > self.thresholds["file_count"],
                severity="warning",
                message="File count exceeded {self.thresholds['file_count']}",
                cooldown_minutes=240,
            ),
            AlertRule(
                name="git_size_large",
                condition=lambda m: m.git_size_mb > self.thresholds["git_size_mb"],
                severity="info",
                message="Git directory size exceeded {self.thresholds['git_size_mb']}MB",
                cooldown_minutes=180,
            ),
            AlertRule(
                name="too_many_branches",
                condition=lambda m: m.branch_count > self.thresholds["branch_count"],
                severity="info",
                message="Branch count exceeded {self.thresholds['branch_count']}",
                cooldown_minutes=360,
            ),
            AlertRule(
                name="stale_branches_detected",
                condition=lambda m: m.stale_branches > self.thresholds["stale_branches"],
                severity="info",
                message="Too many stale branches: {self.thresholds['stale_branches']}+",
                cooldown_minutes=720,
            ),
            AlertRule(
                name="high_disk_usage",
                condition=lambda m: m.disk_usage_percent > self.thresholds["disk_usage_percent"],
                severity="error",
                message="Disk usage exceeded {self.thresholds['disk_usage_percent']}%",
                cooldown_minutes=60,
            ),
            AlertRule(
                name="high_memory_usage",
                condition=lambda m: m.memory_usage_mb > self.thresholds["memory_usage_mb"],
                severity="warning",
                message="Memory usage exceeded {self.thresholds['memory_usage_mb']}MB",
                cooldown_minutes=30,
            ),
            AlertRule(
                name="low_health_score",
                condition=lambda m: m.health_score < self.thresholds["health_score_min"],
                severity="warning",
                message="Health score below {self.thresholds['health_score_min']}",
                cooldown_minutes=240,
            ),
            AlertRule(
                name="excessive_cache_files",
                condition=lambda m: m.cache_files_count > self.thresholds["cache_files"],
                severity="info",
                message="Cache files exceeded {self.thresholds['cache_files']}",
                cooldown_minutes=120,
            ),
        ]
        return rules

    def collect_health_metrics(self) -> HealthMetrics:
        """Collect comprehensive health metrics."""
        logger.debug("Collecting health metrics...")

        metrics = HealthMetrics(timestamp=datetime.now().isoformat())

        try:
            # Repository metrics
            metrics.repository_size_mb = self._get_directory_size(self.repo_path) / (1024 * 1024)
            metrics.file_count = self._count_files()
            metrics.git_size_mb = self._get_directory_size(self.git_dir) / (1024 * 1024)

            # Git metrics
            git_metrics = self._collect_git_metrics()
            metrics.branch_count = git_metrics["branch_count"]
            metrics.stale_branches = git_metrics["stale_branches"]
            metrics.commit_frequency_7d = git_metrics["recent_commits"]
            metrics.contributor_count = git_metrics["contributors"]

            # File analysis
            file_metrics = self._analyze_files()
            metrics.cache_files_count = file_metrics["cache_files"]
            metrics.temp_files_count = file_metrics["temp_files"]
            metrics.large_files_count = file_metrics["large_files"]
            metrics.duplicate_files_count = file_metrics["duplicates"]

            # System metrics
            system_metrics = self._collect_system_metrics()
            metrics.disk_usage_percent = system_metrics["disk_usage_percent"]
            metrics.memory_usage_mb = system_metrics["memory_usage_mb"]
            metrics.cpu_usage_percent = system_metrics["cpu_usage_percent"]

            # Calculate health score
            metrics.health_score = self._calculate_health_score(metrics)

            # Check alerts
            metrics.alerts = self._check_alerts(metrics)

        except Exception as e:
            logger.error("Error collecting metrics: {e}")
            metrics.alerts.append("Metrics collection error: {e}")

        return metrics

    def _get_directory_size(self, path: Path) -> int:
        """Calculate directory size in bytes."""
        total_size = 0
        try:
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        continue
        except Exception as e:
            logger.warning("Error calculating size for {path}: {e}")
        return total_size

    def _count_files(self) -> int:
        """Count total files in repository."""
        count = 0
        try:
            for file_path in self.repo_path.rglob("*"):
                if file_path.is_file() and not self._should_ignore_path(file_path):
                    count += 1
        except Exception as e:
            logger.warning("Error counting files: {e}")
        return count

    def _should_ignore_path(self, path: Path) -> bool:
        """Check if path should be ignored."""
        rel_path = str(path.relative_to(self.repo_path))
        ignore_patterns = [".git/", "__pycache__/", ".pytest_cache/", "node_modules/"]
        return any(pattern in rel_path for pattern in ignore_patterns)

    def _collect_git_metrics(self) -> Dict[str, Any]:
        """Collect git-specific metrics."""
        metrics = {"branch_count": 0, "stale_branches": 0, "recent_commits": 0, "contributors": 0}

        try:
            # Branch count
            result = subprocess.run(
                ["git", "-C", str(self.repo_path, shell=False, check=False), "branch", "-a"],
                capture_output=True,
                text=True,
                check=True,
            )
            metrics["branch_count"] = len([line for line in result.stdout.strip().split("\n") if line.strip()])

            # Stale branches (no activity in 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            stale_count = 0

            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.repo_path, shell=False, check=False),
                    "for-each-re",
                    "--format=%(refname:short) %(committerdate:iso8601)",
                    "refs/heads/",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.strip().split(" ", 1)
                    if len(parts) == 2:
                        try:
                            commit_date = datetime.fromisoformat(parts[1].replace(" +", "+"))
                            if commit_date.replace(tzinfo=None) < cutoff_date:
                                stale_count += 1
                        except (ValueError, IndexError):
                            continue

            metrics["stale_branches"] = stale_count

            # Recent commits (last 7 days)
            since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.repo_path, shell=False, check=False),
                    "rev-list",
                    "--count",
                    "--since={since_date}",
                    "HEAD",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            metrics["recent_commits"] = int(result.stdout.strip() or 0)

            # Contributors
            result = subprocess.run(
                ["git", "-C", str(self.repo_path, shell=False, check=False), "shortlog", "-sn", "--all"],
                capture_output=True,
                text=True,
                check=True,
            )
            metrics["contributors"] = len([line for line in result.stdout.strip().split("\n") if line.strip()])

        except Exception as e:
            logger.warning("Error collecting git metrics: {e}")

        return metrics

    def _analyze_files(self) -> Dict[str, int]:
        """Analyze files for various categories."""
        analysis = {"cache_files": 0, "temp_files": 0, "large_files": 0, "duplicates": 0}

        file_hashes = defaultdict(list)
        large_file_threshold = 10 * 1024 * 1024  # 10MB

        try:
            for file_path in self.repo_path.rglob("*"):
                if not file_path.is_file() or self._should_ignore_path(file_path):
                    continue

                try:
                    size = file_path.stat().st_size

                    # Large files
                    if size > large_file_threshold:
                        analysis["large_files"] += 1

                    # Cache files
                    if self._is_cache_file(file_path):
                        analysis["cache_files"] += 1

                    # Temp files
                    if self._is_temp_file(file_path):
                        analysis["temp_files"] += 1

                    # Calculate hash for duplicates (only for files > 1KB)
                    if size > 1024:
                        file_hash = self._calculate_file_hash(file_path)
                        if file_hash:
                            file_hashes[file_hash].append(file_path)

                except (OSError, PermissionError):
                    continue

            # Count duplicate groups
            analysis["duplicates"] = sum(1 for paths in file_hashes.values() if len(paths) > 1)

        except Exception as e:
            logger.warning("Error analyzing files: {e}")

        return analysis

    def _is_cache_file(self, file_path: Path) -> bool:
        """Check if file is a cache file."""
        cache_patterns = [".pyc", ".pyo", ".so", ".dylib", ".DS_Store", "Thumbs.db"]
        cache_dirs = ["__pycache__", ".pytest_cache", "node_modules", ".cache"]

        # Check file extension
        if any(str(file_path).endswith(pattern) for pattern in cache_patterns):
            return True

        # Check if in cache directory
        return any(cache_dir in file_path.parts for cache_dir in cache_dirs)

    def _is_temp_file(self, file_path: Path) -> bool:
        """Check if file is a temporary file."""
        temp_patterns = [".tmp", ".temp", ".bak", ".swp", "~"]
        return any(str(file_path).endswith(pattern) for pattern in temp_patterns)

    def _calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate file hash for duplicate detection."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb", encoding="utf-8") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, PermissionError):
            return None

    def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect system resource metrics."""
        metrics = {"disk_usage_percent": 0.0, "memory_usage_mb": 0.0, "cpu_usage_percent": 0.0}

        if not HAS_PSUTIL:
            logger.warning("psutil not available, using basic system metrics")
            return metrics

        try:
            # Disk usage
            disk_usage = ps.disk_usage(str(self.repo_path))
            metrics["disk_usage_percent"] = (disk_usage.used / disk_usage.total) * 100

            # Memory usage
            memory = ps.virtual_memory()
            metrics["memory_usage_mb"] = memory.used / (1024 * 1024)

            # CPU usage
            metrics["cpu_usage_percent"] = ps.cpu_percent(interval=1)

        except Exception as e:
            logger.warning("Error collecting system metrics: {e}")

        return metrics

    def _calculate_health_score(self, metrics: HealthMetrics) -> float:
        """Calculate overall health score (0-1)."""
        score = 1.0

        # Size penalties
        if metrics.repository_size_mb > self.thresholds["repository_size_mb"]:
            score -= 0.15

        if metrics.git_size_mb > self.thresholds["git_size_mb"]:
            score -= 0.1

        # File count penalty
        if metrics.file_count > self.thresholds["file_count"]:
            score -= 0.1

        # Branch penalties
        if metrics.branch_count > self.thresholds["branch_count"]:
            score -= 0.05

        if metrics.stale_branches > self.thresholds["stale_branches"]:
            score -= 0.1

        # Cache and temp file penalties
        if metrics.cache_files_count > self.thresholds["cache_files"]:
            score -= 0.05

        if metrics.temp_files_count > self.thresholds["temp_files"]:
            score -= 0.05

        # System resource penalties
        if metrics.disk_usage_percent > self.thresholds["disk_usage_percent"]:
            score -= 0.2

        if metrics.memory_usage_mb > self.thresholds["memory_usage_mb"]:
            score -= 0.1

        if metrics.cpu_usage_percent > self.thresholds["cpu_usage_percent"]:
            score -= 0.1

        return max(0.0, score)

    def _check_alerts(self, metrics: HealthMetrics) -> List[str]:
        """Check alert conditions and return triggered alerts."""
        triggered_alerts = []
        current_time = datetime.now()

        for rule in self.alert_rules:
            # Check cooldown
            if rule.last_triggered and current_time - rule.last_triggered < timedelta(minutes=rule.cooldown_minutes):
                continue

            # Check condition
            if rule.condition(metrics):
                triggered_alerts.append("[{rule.severity.upper()}] {rule.message}")
                rule.last_triggered = current_time

                # Log alert
                if self.config["alerts"]["console_output"]:
                    logger.warning("ALERT: {rule.message}")

                # Execute auto-actions if applicable
                self._handle_auto_actions(rule.name, metrics)

        return triggered_alerts

    def _handle_auto_actions(self, alert_name: str, metrics: HealthMetrics) -> None:
        """Handle automatic actions based on alerts."""
        auto_actions = self.config["auto_actions"]

        try:
            if alert_name == "excessive_cache_files" and auto_actions.get("cleanup_cache_files"):
                self._cleanup_cache_files()
                logger.info("Auto-action: Cleaned up cache files")

            elif alert_name == "high_disk_usage" and auto_actions.get("archive_old_logs"):
                self._archive_old_logs()
                logger.info("Auto-action: Archived old logs")

            elif alert_name == "git_size_large" and auto_actions.get("prune_git_objects"):
                self._prune_git_objects()
                logger.info("Auto-action: Pruned git objects")

        except Exception as e:
            logger.error("Auto-action failed for {alert_name}: {e}")

    def _cleanup_cache_files(self) -> None:
        """Clean up cache files."""
        try:
            for file_path in self.repo_path.rglob("*"):
                if file_path.is_file() and self._is_cache_file(file_path):
                    file_path.unlink()
        except Exception as e:
            logger.error("Cache cleanup failed: {e}")

    def _archive_old_logs(self) -> None:
        """Archive old log files."""
        try:
            log_patterns = ["*.log", "*.log.*"]
            cutoff_date = datetime.now() - timedelta(days=7)

            for pattern in log_patterns:
                for log_file in self.repo_path.rglob(pattern):
                    if log_file.is_file():
                        mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if mod_time < cutoff_date:
                            archive_path = log_file.with_suffix(log_file.suffix + ".archived")
                            log_file.rename(archive_path)
        except Exception as e:
            logger.error("Log archiving failed: {e}")

    def _prune_git_objects(self) -> None:
        """Prune git objects."""
        try:
            subprocess.run(
                ["git", "-C", str(self.repo_path, shell=False, check=False), "gc", "--prune=now"],
                capture_output=True,
                check=True,
            )
        except Exception as e:
            logger.error("Git pruning failed: {e}")

    def start_monitoring(self) -> None:
        """Start continuous monitoring."""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return

        if not HAS_SCHEDULE:
            logger.error("Schedule module not available. Install with: pip install schedule")
            return

        self.is_monitoring = True
        logger.info("Starting repository health monitoring...")

        # Setup scheduled monitoring
        interval_minutes = self.config["monitoring"]["interval_minutes"]
        sched.every(interval_minutes).minutes.do(self._monitoring_cycle)

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        # Initial metrics collection
        self._monitoring_cycle()

    def stop_monitoring(self) -> None:
        """Stop continuous monitoring."""
        if not self.is_monitoring:
            return

        logger.info("Stopping repository health monitoring...")
        self.is_monitoring = False

        if HAS_SCHEDULE:
            sched.clear()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        if not HAS_SCHEDULE:
            return

        while self.is_monitoring:
            try:
                sched.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error("Monitoring loop error: {e}")
                time.sleep(60)

    def _monitoring_cycle(self) -> None:
        """Single monitoring cycle."""
        try:
            # Collect metrics
            metrics = self.collect_health_metrics()

            # Add to history
            self.metrics_history.append(metrics)

            # Save metrics
            self._save_metrics(metrics)

            # Trim history
            self._trim_history()

            logger.debug("Monitoring cycle complete. Health score: {metrics.health_score:.2f}")

        except Exception as e:
            logger.error("Monitoring cycle failed: {e}")

    def _save_metrics(self, metrics: HealthMetrics) -> None:
        """Save metrics to file."""
        try:
            metrics_file = self.monitor_dir / "metrics_history.jsonl"
            with open(metrics_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(metrics)) + "\n")
        except Exception as e:
            logger.error("Failed to save metrics: {e}")

    def _trim_history(self) -> None:
        """Trim metrics history based on retention policy."""
        retention_days = self.config["monitoring"]["history_retention_days"]
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        # Trim in-memory history
        self.metrics_history = [m for m in self.metrics_history if datetime.fromisoformat(m.timestamp) > cutoff_date]

        # Trim file history
        try:
            metrics_file = self.monitor_dir / "metrics_history.jsonl"
            if metrics_file.exists():
                temp_file = metrics_file.with_suffix(".tmp")

                with (
                    open(metrics_file, "r", encoding="utf-8") as infile,
                    open(temp_file, "w", encoding="utf-8") as outfile,
                ):
                    for line in infile:
                        try:
                            data = json.loads(line.strip())
                            if datetime.fromisoformat(data["timestamp"]) > cutoff_date:
                                outfile.write(line)
                        except (json.JSONDecodeError, KeyError):
                            continue

                temp_file.replace(metrics_file)
        except Exception as e:
            logger.error("Failed to trim history: {e}")

    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        current_metrics = self.collect_health_metrics()

        # Calculate trends if we have history
        trends = {}
        if len(self.metrics_history) > 1:
            trends = self._calculate_trends()

        report = {
            "timestamp": datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
            "monitor_version": "2.0.0",
            "current_metrics": asdict(current_metrics),
            "trends": trends,
            "health_status": self._determine_health_status(current_metrics.health_score),
            "recommendations": self._generate_recommendations(current_metrics),
            "monitoring_config": self.config,
            "alert_rules": [
                {
                    "name": rule.name,
                    "severity": rule.severity,
                    "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None,
                }
                for rule in self.alert_rules
            ],
        }

        return report

    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate health trends from history."""
        if len(self.metrics_history) < 2:
            return {}

        # Get metrics from 24 hours ago and now
        now = datetime.now()
        day_ago = now - timedelta(hours=24)

        recent_metrics = [m for m in self.metrics_history if datetime.fromisoformat(m.timestamp) > day_ago]

        if len(recent_metrics) < 2:
            return {}

        first = recent_metrics[0]
        last = recent_metrics[-1]

        trends = {
            "repository_size_trend": last.repository_size_mb - first.repository_size_mb,
            "file_count_trend": last.file_count - first.file_count,
            "health_score_trend": last.health_score - first.health_score,
            "branch_count_trend": last.branch_count - first.branch_count,
            "cache_files_trend": last.cache_files_count - first.cache_files_count,
        }

        return trends

    def _determine_health_status(self, health_score: float) -> str:
        """Determine health status from score."""
        if health_score >= 0.9:
            return "excellent"
        elif health_score >= 0.7:
            return "good"
        elif health_score >= 0.5:
            return "fair"
        elif health_score >= 0.3:
            return "poor"
        else:
            return "critical"

    def _generate_recommendations(self, metrics: HealthMetrics) -> List[Dict[str, Any]]:
        """Generate health improvement recommendations."""
        recommendations = []

        if metrics.repository_size_mb > self.thresholds["repository_size_mb"]:
            recommendations.append(
                {
                    "type": "size_optimization",
                    "priority": "high",
                    "description": "Repository size is above threshold",
                    "action": "Consider archiving old files or using Git LFS for large files",
                }
            )

        if metrics.cache_files_count > self.thresholds["cache_files"]:
            recommendations.append(
                {
                    "type": "cleanup",
                    "priority": "medium",
                    "description": "Found {metrics.cache_files_count} cache files",
                    "action": "Run cache cleanup to free space",
                }
            )

        if metrics.stale_branches > self.thresholds["stale_branches"]:
            recommendations.append(
                {
                    "type": "branch_management",
                    "priority": "low",
                    "description": "Found {metrics.stale_branches} stale branches",
                    "action": "Consider removing unused branches",
                }
            )

        if metrics.health_score < 0.7:
            recommendations.append(
                {
                    "type": "general_health",
                    "priority": "high",
                    "description": "Overall health score is below recommended threshold",
                    "action": "Review and address specific health issues",
                }
            )

        return recommendations


def main():
    """Main CLI interface."""

    parser = argparse.ArgumentParser(description="Repository Health Monitor v2.0")
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--action", choices=["monitor", "report", "check"], default="check", help="Action to perform")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument(
        "--output",
        default="logs/repo_health_status.json",
        help="Output path for the generated JSON report",
    )

    args = parser.parse_args()
    repo_root = Path(args.repo).resolve()
    output_path = Path(args.output)
    canonical_script = Path(__file__).resolve().with_name("repo_health_monitor.py")

    def run_once() -> int:
        result = subprocess.run(
            [sys.executable, str(canonical_script), "--output", str(output_path)],
            cwd=repo_root,
            shell=False,
            check=False,
        )
        return result.returncode

    try:
        if args.config:
            logger.warning("Custom config loading is not supported in compatibility mode; ignoring %s", args.config)

        if args.action == "monitor" and args.daemon:
            logger.info("Running canonical health monitor in daemon mode. Press Ctrl+C to stop.")
            while True:
                exit_code = run_once()
                if exit_code != 0:
                    return exit_code
                time.sleep(30 * 60)
        else:
            exit_code = run_once()
            if exit_code != 0:
                return exit_code

        resolved_output = output_path if output_path.is_absolute() else (repo_root / output_path)
        if resolved_output.exists():
            report = json.loads(resolved_output.read_text(encoding="utf-8"))
        else:
            report = {}

        if args.action == "report":
            print(json.dumps(report, indent=2))
        elif args.action in {"check", "monitor"}:
            print("✅ Health Check Complete")
            print(f"📁 Files: {report.get('file_count', 0)}")
            print(f"💾 Size: {report.get('repo_size_mb', 0)}MB")
            print(f"🌿 Branches: {report.get('branch_count', 0)}")

    except Exception as e:
        logger.error("Health monitor operation failed: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
