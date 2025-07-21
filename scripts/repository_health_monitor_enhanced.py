#!/usr/bin/env python3
"""
Aurora CloudBank - Repository Health Monitoring System
Continuous monitoring with alerts and automated remediation
"""

import datetime
import json
import os
import smtplib
import subprocess
import time
from dataclasses import asdict, dataclass
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional

@dataclass
class HealthMetrics:
    """Repository health metrics container"""

    timestamp: str
    repo_size_mb: float
    file_count: int
    branch_count: int
    zip_file_count: int
    cache_files: int
    large_files: List[Dict]
    health_score: float
    issues: List[str]
    recommendations: List[str]

class RepositoryHealthMonitor:
    """Comprehensive repository health monitoring system"""

    def __init__(self, config_path: str = "config/health_monitor.json"):
        self.config = self._load_config(config_path)
        self.thresholds = self.config.get("thresholds", self._default_thresholds())
        self.alerts = self.config.get("alerts", {})
        self.history_file = "logs/health_history.json"

    def _load_config(self, config_path: str) -> Dict:
        """Load monitoring configuration"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_config()

    def _default_config(self) -> Dict:
        """Default monitoring configuration"""
        return {
            "thresholds": self._default_thresholds(),
            "alerts": {
                "email_enabled": False,
                "webhook_url": None,
                "alert_recipients": [],
            },
            "monitoring": {"check_interval_minutes": 60, "history_retention_days": 30},
        }

    def _default_thresholds(self) -> Dict:
        """Default health thresholds"""
        return {
            "repo_size_mb_warning": 800,
            "repo_size_mb_critical": 1200,
            "file_count_warning": 30000,
            "file_count_critical": 50000,
            "branch_count_warning": 25,
            "branch_count_critical": 40,
            "zip_file_warning": 12,
            "zip_file_critical": 20,
            "cache_files_warning": 100,
            "cache_files_critical": 1000,
            "large_file_mb": 50,
        }

    def collect_metrics(self) -> HealthMetrics:
        """Collect comprehensive repository health metrics"""
        print("📊 Collecting repository health metrics...")

        # Repository size
        repo_size_mb = self._get_repo_size()

        # File counts
        file_count = self._get_file_count()
        branch_count = self._get_branch_count()
        zip_file_count = self._get_zip_file_count()
        cache_files = self._get_cache_file_count()

        # Large files
        large_files = self._find_large_files()

        # Calculate health score and issues
        health_score, issues, recommendations = self._calculate_health_score(
            repo_size_mb,
            file_count,
            branch_count,
            zip_file_count,
            cache_files,
            large_files,
        )

        return HealthMetrics(
            timestamp=datetime.datetime.now().isoformat(),
            repo_size_mb=repo_size_mb,
            file_count=file_count,
            branch_count=branch_count,
            zip_file_count=zip_file_count,
            cache_files=cache_files,
            large_files=large_files,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
        )

    def _get_repo_size(self) -> float:
        """Get repository size in MB"""
        try:
            _ = subprocess.run(
                ["du", "-sm", "."],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            return float(result.stdout.split()[0])
        except (subprocess.CalledProcessError, ValueError):
            return 0.0

    def _get_file_count(self) -> int:
        """Get total file count"""
        try:
            _ = subprocess.run(
                ["find", ".", "-type", ""],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            return (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )
        except subprocess.CalledProcessError:
            return 0

    def _get_branch_count(self) -> int:
        """Get remote branch count"""
        try:
            _ = subprocess.run(
                ["git", "branch", "-r"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            return len(
                [
                    line
                    for line in result.stdout.strip().split("\n")
                    if line.strip() and "origin/HEAD" not in line
                ]
            )
        except subprocess.CalledProcessError:
            return 0

    def _get_zip_file_count(self) -> int:
        """Get ZIP file count"""
        try:
            _ = subprocess.run(
                ["find", ".", "-name", "*.zip", "-type", ""],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            return (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )
        except subprocess.CalledProcessError:
            return 0

    def _get_cache_file_count(self) -> int:
        """Get cache file count"""
        try:
            _ = subprocess.run(
                ["find", ".", "-name", "*.pyc", "-o", "-name", "__pycache__"],
                capture_output=True,
                text=True,
                shell=False,
                check=False,
            )
            return (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )
        except subprocess.CalledProcessError:
            return 0

    def _find_large_files(self) -> List[Dict]:
        """Find files larger than threshold"""
        try:
            threshold_mb = self.thresholds["large_file_mb"]
            cmd = ["find", ".", "-type", "", "-size", f"+{threshold_mb}M"]
            _ = subprocess.run(
                cmd, capture_output=True, text=True, shell=False, check=False
            )

            large_files = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                try:
                    # Get file size
                    stat_result = subprocess.run(
                        ["du", "-m", line],
                        capture_output=True,
                        text=True,
                        shell=False,
                        check=False,
                    )
                    size_mb = float(stat_result.stdout.split()[0])

                    large_files.append({"path": line, "size_mb": size_mb})
                except (subprocess.CalledProcessError, ValueError):
                    continue

            return sorted(large_files, key=lambda x: x["size_mb"], reverse=True)

        except subprocess.CalledProcessError:
            return []

    def _calculate_health_score(
        self,
        repo_size_mb: float,
        file_count: int,
        branch_count: int,
        zip_count: int,
        cache_files: int,
        large_files: List,
    ) -> tuple:
        """Calculate overall health score and identify issues"""
        score = 10.0
        issues = []
        recommendations = []

        # Repository size check
        if repo_size_mb > self.thresholds["repo_size_mb_critical"]:
            score -= 2.0
            issues.append(
                f"CRITICAL: Repository size {repo_size_mb}MB exceeds critical threshold"
            )
            recommendations.append(
                "Immediate cleanup of large files and archives required"
            )
        elif repo_size_mb > self.thresholds["repo_size_mb_warning"]:
            score -= 1.0
            issues.append(
                f"WARNING: Repository size {repo_size_mb}MB approaching limits"
            )
            recommendations.append("Consider archiving old files and cleaning up")

        # File count check
        if file_count > self.thresholds["file_count_critical"]:
            score -= 1.5
            issues.append(
                f"CRITICAL: File count {file_count} exceeds critical threshold"
            )
            recommendations.append("Remove cache files and temporary artifacts")
        elif file_count > self.thresholds["file_count_warning"]:
            score -= 0.8
            issues.append(f"WARNING: File count {file_count} is high")
            recommendations.append("Review and clean unnecessary files")

        # Branch count check
        if branch_count > self.thresholds["branch_count_critical"]:
            score -= 1.2
            issues.append(f"CRITICAL: Branch count {branch_count} is too high")
            recommendations.append("Immediate branch cleanup required")
        elif branch_count > self.thresholds["branch_count_warning"]:
            score -= 0.6
            issues.append(f"WARNING: Branch count {branch_count} needs attention")
            recommendations.append("Schedule branch cleanup")

        # ZIP file check
        if zip_count > self.thresholds["zip_file_critical"]:
            score -= 1.0
            issues.append(f"CRITICAL: Too many ZIP files ({zip_count})")
            recommendations.append("Archive old ZIP files externally")
        elif zip_count > self.thresholds["zip_file_warning"]:
            score -= 0.5
            issues.append(f"WARNING: Many ZIP files ({zip_count})")
            recommendations.append("Review and consolidate ZIP files")

        # Cache files check
        if cache_files > self.thresholds["cache_files_critical"]:
            score -= 1.5
            issues.append(f"CRITICAL: Excessive cache files ({cache_files})")
            recommendations.append("Clean all cache files immediately")
        elif cache_files > self.thresholds["cache_files_warning"]:
            score -= 0.8
            issues.append(f"WARNING: Cache files present ({cache_files})")
            recommendations.append("Regular cache cleanup needed")

        # Large files check
        if large_files:
            score -= min(1.0, len(large_files) * 0.2)
            issues.append(f"Large files detected: {len(large_files)} files")
            recommendations.append("Review and archive large files")

        return max(0.0, score), issues, recommendations

    def save_metrics(self, metrics: HealthMetrics):
        """Save metrics to history file"""
        history_path = Path(self.history_file)
        history_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing history
        history = []
        if history_path.exists():
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                history = []

        # Add new metrics
        history.append(asdict(metrics))

        # Clean old entries (keep last 30 days)
        cutoff_date = datetime.datetime.now() - datetime.timedelta(
            days=self.config.get("monitoring", {}).get("history_retention_days", 30)
        )
        history = [
            entry
            for entry in history
            if datetime.datetime.fromisoformat(entry["timestamp"]) > cutoff_date
        ]

        # Save history
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def check_alerts(self, metrics: HealthMetrics):
        """Check if alerts should be triggered"""
        if metrics.health_score < 7.0:
            self._send_alert(metrics)

    def _send_alert(self, metrics: HealthMetrics):
        """Send health alert"""
        alert_message = self._format_alert_message(metrics)

        # Email alert
        if self.alerts.get("email_enabled"):
            self._send_email_alert(alert_message)

        # Webhook alert
        if self.alerts.get("webhook_url"):
            self._send_webhook_alert(alert_message)

        print(f"🚨 HEALTH ALERT TRIGGERED - Score: {metrics.health_score:.1f}/10")
        print(alert_message)

    def _format_alert_message(self, metrics: HealthMetrics) -> str:
        """Format alert message"""
        lines = [
            "🚨 REPOSITORY HEALTH ALERT",
            f"Timestamp: {metrics.timestamp}",
            f"Health Score: {metrics.health_score:.1f}/10",
            "",
            "ISSUES DETECTED:",
        ]

        for issue in metrics.issues:
            lines.append(f"- {issue}")

        lines.extend(
            [
                "",
                "RECOMMENDATIONS:",
            ]
        )

        for rec in metrics.recommendations:
            lines.append(f"- {rec}")

        lines.extend(
            [
                "",
                "CURRENT METRICS:",
                f"- Repository Size: {metrics.repo_size_mb:.1f}MB",
                f"- File Count: {metrics.file_count:,}",
                f"- Branch Count: {metrics.branch_count}",
                f"- ZIP Files: {metrics.zip_file_count}",
                f"- Cache Files: {metrics.cache_files}",
            ]
        )

        return "\n".join(lines)

    def _send_email_alert(self, message: str):
        """Send email alert"""
        # Implementation would depend on SMTP configuration
        print("📧 Email alert would be sent here")

    def _send_webhook_alert(self, message: str):
        """Send webhook alert"""
        # Implementation would depend on webhook service
        print("🔗 Webhook alert would be sent here")

    def generate_health_report(self, metrics: HealthMetrics) -> str:
        """Generate comprehensive health report"""
        report_lines = [
            "# Repository Health Report",
            f"**Generated:** {metrics.timestamp}",
            f"**Health Score:** {metrics.health_score:.1f}/10",
            "",
            "## Current Metrics",
            "",
            f"- **Repository Size**: {metrics.repo_size_mb:.1f}MB",
            f"- **File Count**: {metrics.file_count:,}",
            f"- **Branch Count**: {metrics.branch_count}",
            f"- **ZIP Files**: {metrics.zip_file_count}",
            f"- **Cache Files**: {metrics.cache_files}",
            "",
        ]

        if metrics.large_files:
            report_lines.extend(["## Large Files", ""])
            for file_info in metrics.large_files[:10]:
                report_lines.append(
                    f"- {file_info['path']} ({file_info['size_mb']:.1f}MB)"
                )

            if len(metrics.large_files) > 10:
                report_lines.append(f"- ... and {len(metrics.large_files) - 10} more")

            report_lines.append("")

        if metrics.issues:
            report_lines.extend(["## Issues Detected", ""])
            for issue in metrics.issues:
                report_lines.append(f"- {issue}")
            report_lines.append("")

        if metrics.recommendations:
            report_lines.extend(["## Recommendations", ""])
            for rec in metrics.recommendations:
                report_lines.append(f"- {rec}")

        return "\n".join(report_lines)

    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        print(f"🔍 Starting health check at {datetime.datetime.now()}")

        # Collect metrics
        metrics = self.collect_metrics()

        # Save to history
        self.save_metrics(metrics)

        # Check for alerts
        self.check_alerts(metrics)

        # Generate report
        report = self.generate_health_report(metrics)

        # Save report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"logs/health_report_{timestamp}.md"

        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📊 Health Score: {metrics.health_score:.1f}/10")
        print(f"📄 Report saved to: {report_file}")

        return metrics

def main():
    """Main monitoring function"""
    import argparse

    parser = argparse.ArgumentParser(description="Repository health monitor")
    parser.add_argument(
        "--continuous", action="store_true", help="Run continuous monitoring"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in minutes (default: 60)",
    )

    args = parser.parse_args()

    monitor = RepositoryHealthMonitor()

    if args.continuous:
        print("🔄 Starting continuous monitoring...")
        while True:
            try:
                monitor.run_monitoring_cycle()
                print(f"💤 Sleeping for {args.interval} minutes...")
                time.sleep(args.interval * 60)
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
            except (OSError, ValueError, RuntimeError) as e:
                print(f"❌ Error in monitoring cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    else:
        # Single run
        monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()
