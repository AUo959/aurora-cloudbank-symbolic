#!/usr/bin/env python3
"""
Aurora CloudBank - Repository Health Monitoring System
Continuous monitoring and alerting for repository health metrics.
"""

import argparse
import datetime
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional


class RepositoryHealthMonitor:

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.config = {
            "thresholds": {
                "max_size_mb": 800,  # Repository size limit
                "max_files": 35000,  # File count limit
                "max_branches": 25,  # Active branch limit
                "max_zip_files": 12,  # ZIP file limit
                "max_cache_files": 100,  # Cache file limit (.pyc, etc.)
            },
            "alerts": {
                "size_growth_rate": 10,  # MB per day growth limit
                "file_growth_rate": 1000,  # Files per day growth limit
            },
            "monitoring_interval": 3600,  # 1 hour in seconds
            "history_days": 30,  # Days to keep history
        }
        self.history_file = self.repo_path / ".gitwiz" / "health_history.json"
        self.ensure_gitwiz_dir()

    def ensure_gitwiz_dir(self):
        """Ensure .gitwiz directory exists."""
        gitwiz_dir = self.repo_path / ".gitwiz"
        gitwiz_dir.mkdir(exist_ok=True)

    def get_repository_metrics(self) -> Dict:
        """Collect current repository health metrics."""
        metrics = {
            "timestamp": datetime.datetime.now().isoformat(),
            "size_mb": 0,
            "file_count": 0,
            "branch_count": 0,
            "zip_count": 0,
            "cache_files": 0,
            "large_files": [],
            "git_status": "clean",
        }

        try:
            # Repository size
            result = subprocess.run(
                ["du", "-sm", "."],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
                metrics["size_mb"] = int(result.stdout.split()[0])

            # File count
            result = subprocess.run(
                ["find", ".", "-type", ""],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
                metrics["file_count"] = len(result.stdout.strip().split("\n"))

            # Branch count
            result = subprocess.run(
                ["git", "branch", "-r"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
                metrics["branch_count"] = len([line for line in result.stdout.strip().split("\n") if line.strip()])

            # ZIP file count
            result = subprocess.run(
                ["find", ".", "-name", "*.zip", "-type", ""],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
                zip_files = result.stdout.strip().split("\n")
                metrics["zip_count"] = len([f for f in zip_files if f])

            # Cache files (.pyc, __pycache__)
            pyc_result = subprocess.run(
                ["find", ".", "-name", "*.pyc", "-type", ""],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            cache_result = subprocess.run(
                ["find", ".", "-name", "__pycache__", "-type", "d"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )

            pyc_count = (
                len([f for f in pyc_result.stdout.strip().split("\n") if f]) if pyc_result.returncode == 0 else 0
            )
            cache_count = (
                len([f for f in cache_result.stdout.strip().split("\n") if f]) if cache_result.returncode == 0 else 0
            )
            metrics["cache_files"] = pyc_count + cache_count

            # Large files (>10MB)
            result = subprocess.run(
                ["find", ".", "-type", "", "-size", "+10M"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
                metrics["large_files"] = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

            # Git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
                metrics["git_status"] = "dirty" if result.stdout.strip() else "clean"

        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error collecting metrics: {e}")

        return metrics

    def load_history(self) -> List[Dict]:
        """Load historical metrics data."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

            # Clean old entries
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.config["history_days"])
            history = [entry for entry in history if datetime.datetime.fromisoformat(entry["timestamp"]) > cutoff_date]

            return history
        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error loading history: {e}")
            return []

    def save_history(self, history: List[Dict]):
        """Save historical metrics data."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error saving history: {e}")

    def analyze_trends(self, history: List[Dict]) -> Dict:
        """Analyze trends from historical data."""
        if len(history) < 2:
            return {"trends": "insufficient_data"}

        current = history[-1]
        previous = history[-2]

        trends = {
            "size_change_mb": current["size_mb"] - previous["size_mb"],
            "file_change": current["file_count"] - previous["file_count"],
            "branch_change": current["branch_count"] - previous["branch_count"],
            "zip_change": current["zip_count"] - previous["zip_count"],
            "cache_change": current["cache_files"] - previous["cache_files"],
        }

        # Calculate daily rates if we have enough history
        if len(history) >= 7:
            week_ago = history[-7]
            days_diff = 7

            trends["daily_size_growth"] = (current["size_mb"] - week_ago["size_mb"]) / days_diff
            trends["daily_file_growth"] = (current["file_count"] - week_ago["file_count"]) / days_diff

        return trends

    def check_thresholds(self, metrics: Dict, trends: Dict) -> List[Dict]:
        """Check if any thresholds are exceeded."""
        alerts = []

        # Size threshold
        if metrics["size_mb"] > self.config["thresholds"]["max_size_mb"]:
            alerts.append(
                {
                    "type": "size_exceeded",
                    "severity": "warning",
                    "message": f"Repository size ({metrics['size_mb']}MB) exceeds threshold ({self.config['thresholds']['max_size_mb']}MB)",
                    "metric": metrics["size_mb"],
                    "threshold": self.config["thresholds"]["max_size_mb"],
                }
            )

        # File count threshold
        if metrics["file_count"] > self.config["thresholds"]["max_files"]:
            alerts.append(
                {
                    "type": "file_count_exceeded",
                    "severity": "warning",
                    "message": f"File count ({metrics['file_count']}) exceeds threshold ({self.config['thresholds']['max_files']})",
                    "metric": metrics["file_count"],
                    "threshold": self.config["thresholds"]["max_files"],
                }
            )

        # Branch count threshold
        if metrics["branch_count"] > self.config["thresholds"]["max_branches"]:
            alerts.append(
                {
                    "type": "branch_count_exceeded",
                    "severity": "info",
                    "message": f"Branch count ({metrics['branch_count']}) exceeds threshold ({self.config['thresholds']['max_branches']})",
                    "metric": metrics["branch_count"],
                    "threshold": self.config["thresholds"]["max_branches"],
                }
            )

        # Cache files threshold
        if metrics["cache_files"] > self.config["thresholds"]["max_cache_files"]:
            alerts.append(
                {
                    "type": "cache_files_detected",
                    "severity": "error",
                    "message": f"Cache files detected ({metrics['cache_files']}), should be cleaned",
                    "metric": metrics["cache_files"],
                    "threshold": self.config["thresholds"]["max_cache_files"],
                }
            )

        # Growth rate alerts
        if "daily_size_growth" in trends and trends["daily_size_growth"] > self.config["alerts"]["size_growth_rate"]:
            alerts.append(
                {
                    "type": "rapid_size_growth",
                    "severity": "warning",
                    "message": f"Repository growing rapidly ({trends['daily_size_growth']:.1f}MB/day)",
                    "metric": trends["daily_size_growth"],
                    "threshold": self.config["alerts"]["size_growth_rate"],
                }
            )

        return alerts

    def generate_health_report(self, metrics: Dict, trends: Dict, alerts: List[Dict]) -> str:
        """Generate a comprehensive health report."""
        report = []
        report.append("# Aurora CloudBank - Repository Health Report")
        report.append(f"**Generated:** {datetime.datetime.now().isoformat()}")
        report.append("")

        # Health score calculation
        score = 10.0
        for alert in alerts:
            if alert["severity"] == "error":
                score -= 2.0
            elif alert["severity"] == "warning":
                score -= 1.0
            elif alert["severity"] == "info":
                score -= 0.5

        score = max(0.0, score)
        health_status = "EXCELLENT" if score >= 9 else "GOOD" if score >= 7 else "MODERATE" if score >= 5 else "POOR"

        report.append(f"## Overall Health Score: {health_status} ({score:.1f}/10)")
        report.append("")

        # Current metrics
        report.append("## Current Metrics")
        report.append("")
        report.append(f"- **Repository Size**: {metrics['size_mb']}MB")
        report.append(f"- **File Count**: {metrics['file_count']:,}")
        report.append(f"- **Active Branches**: {metrics['branch_count']}")
        report.append(f"- **ZIP Files**: {metrics['zip_count']}")
        report.append(f"- **Cache Files**: {metrics['cache_files']}")
        report.append(f"- **Git Status**: {metrics['git_status']}")
        report.append("")

        # Trends
        if trends and "size_change_mb" in trends:
            report.append("## Recent Changes")
            report.append("")
            report.append(f"- **Size Change**: {trends['size_change_mb']:+d}MB")
            report.append(f"- **File Change**: {trends['file_change']:+d}")
            report.append(f"- **Branch Change**: {trends['branch_change']:+d}")
            report.append(f"- **ZIP Change**: {trends['zip_change']:+d}")

            if "daily_size_growth" in trends:
                report.append(f"- **Daily Growth Rate**: {trends['daily_size_growth']:+.1f}MB/day")
            report.append("")

        # Alerts
        if alerts:
            report.append("## Alerts")
            report.append("")
            for alert in alerts:
                severity_emoji = {"error": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(alert["severity"], "")
                report.append(f"- {severity_emoji} **{alert['type'].replace('_', ' ').title()}**: {alert['message']}")
            report.append("")

        # Large files
        if metrics.get("large_files"):
            report.append("## Large Files (>10MB)")
            report.append("")
            for file_path in metrics["large_files"][:10]:  # Limit to top 10
                report.append(f"- `{file_path}`")
            report.append("")

        return "\n".join(report)

    def run_health_check(self, save_report: bool = True) -> Dict:
        """Run a complete health check."""
        print("🔍 Running repository health check...")

        # Collect current metrics
        metrics = self.get_repository_metrics()

        # Load and update history
        history = self.load_history()
        history.append(metrics)
        self.save_history(history)

        # Analyze trends
        trends = self.analyze_trends(history)

        # Check thresholds
        alerts = self.check_thresholds(metrics, trends)

        # Generate report
        report = self.generate_health_report(metrics, trends, alerts)

        if save_report:
            report_path = self.repo_path / "REPOSITORY_HEALTH_MONITOR.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Health report saved to: {report_path}")

        # Print summary
        print("\n📊 Health Check Summary:")
        print(f"  Repository Size: {metrics['size_mb']}MB")
        print(f"  File Count: {metrics['file_count']:,}")
        print(f"  Active Branches: {metrics['branch_count']}")
        print(f"  Alerts: {len(alerts)}")

        if alerts:
            print("\n🚨 Active Alerts:")
            for alert in alerts:
                severity_emoji = {"error": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(alert["severity"], "")
                print(f"  {severity_emoji} {alert['message']}")

        return {
            "metrics": metrics,
            "trends": trends,
            "alerts": alerts,
            "report": report,
        }

    def monitor_continuously(self, interval: Optional[int] = None):
        """Run continuous monitoring."""
        interval = interval or self.config["monitoring_interval"]
        print(f"🔄 Starting continuous monitoring (interval: {interval}s)")

        try:
            while True:
                self.run_health_check()
                print(f"💤 Sleeping for {interval} seconds...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")


def main():
    parser = argparse.ArgumentParser(description="Aurora CloudBank Repository Health Monitor")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=3600, help="Monitoring interval in seconds")
    parser.add_argument("--no-report", action="store_true", help="Skip saving report file")

    args = parser.parse_args()

    monitor = RepositoryHealthMonitor()

    if args.monitor:
        monitor.monitor_continuously(args.interval)
    else:
        monitor.run_health_check(save_report=not args.no_report)


if __name__ == "__main__":
    main()
