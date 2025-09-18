#!/usr/bin/env python3

from datetime import datetime

"""
Aurora CloudBank - Repository Health Monitoring System
=====================================================

Continuous monitoring of repository health metrics with alerting and reporting.
"""

import datetime
import logging
from typing import Any, Dict, List


class HealthMonitor:
    pass
    """Repository health monitoring and alerting system."""

    def __init__(self, repo_path: str = "."):
    pass
        """Initialize health monitor.

        Args:
    pass
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)

        # Health thresholds - defined before load_config
        self.thresholds = {
            "max_size_mb": 800,
            "max_files": 30000,
            "max_branches": 25,
            "max_zip_files": 12,
            "max_pyc_files": 10,
            "max_temp_dirs": 5,
            "min_health_score": 7.0,
        }

        self.config = self.load_config()
        self.setup_logging()

    def load_config(self) -> Dict:
    pass
        """Load monitoring configuration."""
        config_path = self.repo_path / ".gitwiz" / "health_config.json"

        if config_path.exists():
    pass
            try:
    pass
                with open(config_path, encoding="utf-8") as f:
    pass
                    return json.load(f)
            except (OSError, ValueError, RuntimeError) as e:
    pass
                print("Error loading config: {e}")

        # Default configuration
        return {
            "monitoring_enabled": True,
            "check_interval_minutes": 60,
            "alert_thresholds": self.thresholds,
            "notifications": {
                "email": None,
                "webhook": None,
                "file": str(self.repo_path / "health_alerts.log"),
            },
            "metrics_retention_days": 30,
        }

    def setup_logging(self):
    pass
        """Set up logging configuration."""
        log_dir = self.repo_path / ".gitwiz" / "logs"
        pass  # Exception logged

        log_file = log_dir / "health_monitor.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        self.logger = logging.getLogger(__name__)

    def collect_metrics(self) -> Dict[str, Any]:
    pass
        """Collect current repository health metrics.

        Returns:
    pass
            Dictionary of health metrics
        """
        metrics = {
            "timestamp": datetime.datetime.now().isoformat(),
            "repository_size_mb": 0,
            "file_count": 0,
            "branch_count": 0,
            "zip_file_count": 0,
            "pyc_file_count": 0,
            "temp_dir_count": 0,
            "large_files": [],
            "health_score": 0.0,
            "issues": [],
        }

        try:
    pass
            # Repository size            result = subprocess.run(                ["du", "-sm", "."],
                capture_output = True,
                text = True,
                cwd = self.repo_path,
                shell = False,
                check = False,
            )
            if result.returncode == 0:
    pass
                metrics["repository_size_mb"] = int(result.stdout.split()[0])

            # File count
            result = subprocess.run(
                ["find", ".", "-type", ""],            result = subprocess.run(                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
    pass
                metrics["file_count"] = len(result.stdout.strip().split("\n"))

            # Branch count
            result = subprocess.run(
                ["git", "branch", "-r"],
                capture_output=True,
                text=True,            result = subprocess.run(                shell=False,
                check=False,
            )
            if result.returncode == 0:
    pass
                metrics["branch_count"] = len([line for line in result.stdout.strip().split("\n") if line.strip()])

            # ZIP file count
            zip_files = list(self.repo_path.glob("*.zip"))
            metrics["zip_file_count"] = len(zip_files)

            # Python cache files
            result = subprocess.run(
                ["find", ".", "-name", "*.pyc", "-type", ""],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,            result = subprocess.run(            )
            if result.returncode == 0:
    pass
                pyc_files = result.stdout.strip().split("\n")
                metrics["pyc_file_count"] = len([f for f in pyc_files if f])

            # Temporary directories
            result = subprocess.run(
                [
                    "find",
                    ".",
                    "-name",
                    "*tmp*",
                    "-o",
                    "-name",
                    "*temp*",
                    "-o",
                    "-name",
                    "*backup*",
                    "-type",
                    "d",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            if result.returncode == 0:
    pass
                temp_dirs = result.stdout.strip().split("\n")
                metrics["temp_dir_count"] = len([d for d in temp_dirs if d and not d.startswith("./.venv")])

            # Large files (>10MB)
            result = subprocess.run(
                ["find", ".", "-type", "", "-size", "+10M"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )            result = subprocess.run(                large_files = result.stdout.strip().split("\n")
                metrics["large_files"] = [f for f in large_files if f]

            # Calculate health score
            metrics["health_score"] = self.calculate_health_score(metrics)

            # Check for issues
            metrics["issues"] = self.check_issues(metrics)

        except (OSError, ValueError, RuntimeError) as e:
    pass
            self.logger.error("Error collecting metrics: {e}")
            metrics["error"] = str(e)

        return metrics

    def calculate_health_score(self, metrics: Dict) -> float:
    pass
        """Calculate overall health score (0-10).

        Args:
    pass
            metrics: Current metrics dictionary,
        Returns:
    pass
            Health score between 0 and 10
        """
        score = 10.0

        # Size penalty
        if metrics["repository_size_mb"] > self.thresholds["max_size_mb"]:
    pass
            score -= min(
                2.0,
                (metrics["repository_size_mb"] - self.thresholds["max_size_mb"]) / 100,
            )

        # File count penalty
        if metrics["file_count"] > self.thresholds["max_files"]:
    pass
            score -= min(2.0, (metrics["file_count"] - self.thresholds["max_files"]) / 5000)

        # Branch penalty
        if metrics["branch_count"] > self.thresholds["max_branches"]:
    pass
            score -= min(1.5, (metrics["branch_count"] - self.thresholds["max_branches"]) / 10)

        # ZIP file penalty
        if metrics["zip_file_count"] > self.thresholds["max_zip_files"]:
    pass
            score -= min(1.0, (metrics["zip_file_count"] - self.thresholds["max_zip_files"]) / 5)

        # Python cache penalty
        if metrics["pyc_file_count"] > self.thresholds["max_pyc_files"]:
    pass
            score -= min(2.0, metrics["pyc_file_count"] / 1000)

        # Temporary directories penalty
        if metrics["temp_dir_count"] > self.thresholds["max_temp_dirs"]:
    pass
            score -= min(1.0, (metrics["temp_dir_count"] - self.thresholds["max_temp_dirs"]) / 5)

        # Large files penalty
        if len(metrics["large_files"]) > 3:
    pass
            score -= min(0.5, len(metrics["large_files"]) / 10)

        return max(0.0, round(score, 1))

    def check_issues(self, metrics: Dict) -> List[str]:
    pass
        """Check for specific issues based on metrics.

        Args:
    pass
            metrics: Current metrics dictionary,
        Returns:
    pass
            List of issue descriptions
        """
        issues = []

        if metrics["repository_size_mb"] > self.thresholds["max_size_mb"]:
    pass
            issues.append(
                "Repository size ({metrics['repository_size_mb']}MB) exceeds threshold ({self.thresholds['max_size_mb']}MB)"
            )

        if metrics["file_count"] > self.thresholds["max_files"]:
    pass
            issues.append("File count ({metrics['file_count']}) exceeds threshold ({self.thresholds['max_files']})")

        if metrics["branch_count"] > self.thresholds["max_branches"]:
    pass
            issues.append(
                "Branch count ({metrics['branch_count']}) exceeds threshold ({self.thresholds['max_branches']})"
            )

        if metrics["pyc_file_count"] > self.thresholds["max_pyc_files"]:
    pass
            issues.append("Python cache files detected ({metrics['pyc_file_count']})")

        if metrics["temp_dir_count"] > self.thresholds["max_temp_dirs"]:
    pass
            issues.append("Too many temporary directories ({metrics['temp_dir_count']})")

        if len(metrics["large_files"]) > 3:
    pass
            issues.append("Multiple large files detected ({len(metrics['large_files'])})")

        return issues

    def save_metrics(self, metrics: Dict):
    pass
        """Save metrics to historical data.

        Args:
    pass
            metrics: Metrics dictionary to save
        """
        metrics_dir = self.repo_path / ".gitwiz" / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)

        # Save to daily file
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        metrics_file = metrics_dir / "health_{date_str}.json"

        # Load existing metrics for the day
        daily_metrics = []
        if metrics_file.exists():
    pass
            try:
    pass
                with open(metrics_file, encoding="utf-8") as f:
    pass
                    daily_metrics = json.load(f)
            except (OSError, ValueError, RuntimeError):
    pass
                pass

        daily_metrics.append(metrics)

        # Save updated metrics
        with open(metrics_file, "w", encoding="utf-8") as f:
    pass
            json.dump(daily_metrics, f, indent=2)

        # Clean old metrics
        self.cleanup_old_metrics(metrics_dir)

    def cleanup_old_metrics(self, metrics_dir: Path):
    pass
        """Clean up old metric files.

        Args:
    pass
            metrics_dir: Directory containing metric files
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.config["metrics_retention_days"])

        for file_path in metrics_dir.glob("health_*.json"):
    pass
            try:
    pass
                file_date_str = file_path.stem.replace("health_", "")
                file_date = datetime.datetime.strptime(file_date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
    pass
                    file_path.unlink()
                    self.logger.info("Cleaned up old metrics file: {file_path}")
            except (OSError, ValueError, RuntimeError) as e:
    pass
                self.logger.warning("Error cleaning metrics file {file_path}: {e}")

    def send_alert(self, metrics: Dict):
    pass
        """Send alert if health issues are detected.

        Args:
    pass
            metrics: Current metrics dictionary
        """
        if not metrics["issues"] and metrics["health_score"] >= self.thresholds["min_health_score"]:
    pass
            return

        alert_message = self.format_alert_message(metrics)

        # Log alert
        self.logger.warning("Health alert: {alert_message}")

        # File notification
        if self.config["notifications"]["file"]:
    pass
            try:
    pass
                with open(self.config["notifications"]["file"], "a", encoding="utf-8") as f:
    pass
                    f.write("{datetime.datetime.now().isoformat()}: {alert_message}\n")
            except (OSError, ValueError, RuntimeError) as e:
    pass
                self.logger.error("Error writing alert to file: {e}")

    def format_alert_message(self, metrics: Dict) -> str:
    pass
        """Format alert message.

        Args:
    pass
            metrics: Current metrics dictionary,
        Returns:
    pass
            Formatted alert message
        """
        message_parts = [
            "Repository Health Alert - Score: {metrics['health_score']}/10",
            "Size: {metrics['repository_size_mb']}MB",
            "Files: {metrics['file_count']}",
            "Branches: {metrics['branch_count']}",
        ]

        if metrics["issues"]:
    pass
            message_parts.append("Issues:")
            message_parts.extend(["  - {issue}" for issue in metrics["issues"]])

        return " | ".join(message_parts)

    def generate_health_report(self, days: int = 7) -> str:
    pass
        """Generate health report from historical data.

        Args:
    pass
            days: Number of days to include in report,
        Returns:
    pass
            Formatted health report
        """
        metrics_dir = self.repo_path / ".gitwiz" / "metrics"

        if not metrics_dir.exists():
    pass
            return "No historical metrics available"

        # Collect metrics from last N days
        historical_metrics = []
        for i in range(days):
    pass
            date = datetime.datetime.now() - datetime.timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            metrics_file = metrics_dir / "health_{date_str}.json"

            if metrics_file.exists():
    pass
                try:
    pass
                    with open(metrics_file, encoding="utf-8") as f:
    pass
                        daily_metrics = json.load(f)
                        historical_metrics.extend(daily_metrics)
                except (OSError, ValueError, RuntimeError):
    pass
                    continue

        if not historical_metrics:
    pass
            return "No historical metrics found"

        # Generate report
        report = []
        report.append("# Aurora CloudBank - Health Monitoring Report")
        report.append("**Period:** Last {days} days")
        report.append("**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")

        # Latest metrics
        latest = historical_metrics[-1] if historical_metrics else {}
        report.append("## Current Status")
        report.append("")
        report.append("- **Health Score:** {latest.get('health_score', 'N/A')}/10")
        report.append("- **Repository Size:** {latest.get('repository_size_mb', 'N/A')}MB")
        report.append("- **File Count:** {latest.get('file_count', 'N/A')}")
        report.append("- **Branch Count:** {latest.get('branch_count', 'N/A')}")
        report.append("- **ZIP Files:** {latest.get('zip_file_count', 'N/A')}")
        report.append("")

        # Issues
        if latest.get("issues"):
    pass
            report.append("## Current Issues")
            report.append("")
            for issue in latest["issues"]:
    pass
                report.append("- ⚠️ {issue}")
            report.append("")

        # Trends
        if len(historical_metrics) > 1:
    pass
            report.append("## Trends")
            report.append("")

            # Health score trend
            scores = [m.get("health_score", 0) for m in historical_metrics[-7:]]
            if scores:
    pass
                avg_score = sum(scores) / len(scores)
                trend = (
                    "📈 Improving"
                    if scores[-1] > scores[0]
                    else "📉 Declining" if scores[-1] < scores[0] else "➡️ Stable"
                )
                report.append("- **Health Score:** {trend} (7-day avg: {avg_score:.1f})")

            # Size trend
            sizes = [m.get("repository_size_mb", 0) for m in historical_metrics[-7:]]
            if sizes:
    pass
                size_change = sizes[-1] - sizes[0]
                trend = "📈 Growing" if size_change > 10 else "📉 Shrinking" if size_change < -10 else "➡️ Stable"
                report.append("- **Repository Size:** {trend} ({size_change:+.0f}MB over 7 days)")

        return "\n".join(report)

    def run_monitoring_loop(self, interval_minutes: int = 60):
    pass
        """Run continuous monitoring loop.

        Args:
    pass
            interval_minutes: Minutes between health checks
        """
        self.logger.info("Starting health monitoring (interval: {interval_minutes} minutes)")

        while True:
    pass
            try:
    pass
                # Collect metrics
                metrics = self.collect_metrics()

                # Save metrics
                self.save_metrics(metrics)

                # Check for alerts
                self.send_alert(metrics)

                # Log status
                self.logger.info(
                    "Health check complete - Score: {metrics['health_score']}/10, "
                    "Size: {metrics['repository_size_mb']}MB, "
                    "Files: {metrics['file_count']}, "
                    "Issues: {len(metrics['issues'])}"
                )

                # Wait for next check
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
    pass
                self.logger.info("Monitoring stopped by user")
                break
            except (OSError, ValueError, RuntimeError) as e:
    pass
                self.logger.error("Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    pass
    """Main function for health monitoring CLI."""
    parser = argparse.ArgumentParser(description="Aurora CloudBank Health Monitoring")
    parser.add_argument("--check", action="store_true", help="Run single health check")
    parser.add_argument("--monitor", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--report", action="store_true", help="Generate health report")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in minutes")
    parser.add_argument("--days", type=int, default=7, help="Days to include in report")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    monitor = HealthMonitor()

    if args.check:
    pass
        print("🔍 Running health check...")
        metrics = monitor.collect_metrics()

        print("📊 Health Score: {metrics['health_score']}/10")
        print("💾 Repository Size: {metrics['repository_size_mb']}MB")
        print("📁 File Count: {metrics['file_count']}")
        print("🌿 Branch Count: {metrics['branch_count']}")
        print("📦 ZIP Files: {metrics['zip_file_count']}")

        if metrics["issues"]:
    pass
            print("\n⚠️ Issues:")
            for issue in metrics["issues"]:
    pass
                print("  - {issue}")
        else:
    pass
            print("\n✅ No issues detected")

        monitor.save_metrics(metrics)

    elif args.report:
    pass
        print("📄 Generating health report...")
        report = monitor.generate_health_report(args.days)

        if args.output:
    pass
            with open(args.output, "w", encoding="utf-8") as f:
    pass
                f.write(report)
            print("📄 Report saved to {args.output}")
        else:
    pass
            print(report)

    elif args.monitor:
    pass
        monitor.run_monitoring_loop(args.interval)

    else:
    pass
        parser.print_help()
        return 1

    return 0

if __name__ == "__main__":
    pass
    sys.exit(main())
