#!/usr/bin/env python3
"""
Aurora CloudBank - Repository Health Monitoring System
=====================================================

Continuous monitoring of repository health metrics with alerting and reporting.
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


class HealthMonitor:
    """Repository health monitoring and alerting system."""

    def __init__(self, repo_path: str = "."):
        """Initialize health monitor.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)
        self.config = self.load_config()
        self.setup_logging()

        # Health thresholds
        self.thresholds = {
            'max_size_mb': 800,
            'max_files': 30000,
            'max_branches': 25,
            'max_zip_files': 12,
            'max_pyc_files': 10,
            'max_temp_dirs': 5,
            'min_health_score': 7.0
        }

    def load_config(self) -> Dict:
        """Load monitoring configuration."""
        config_path = self.repo_path / '.gitwiz' / 'health_config.json'

        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, ValueError, RuntimeError) as e:
                print(f"Error loading config: {e}")

        # Default configuration
        return {
            'monitoring_enabled': True,
            'check_interval_minutes': 60,
            'alert_thresholds': self.thresholds,
            'notifications': {
                'email': None,
                'webhook': None,
                'file': str(self.repo_path / 'health_alerts.log')
            },
            'metrics_retention_days': 30
        }

    def setup_logging(self):
        """Set up logging configuration."""
        log_dir = self.repo_path / '.gitwiz' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / 'health_monitor.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current repository health metrics.

        Returns:
            Dictionary of health metrics
        """
        metrics = {
            'timestamp': datetime.datetime.now().isoformat(),
            'repository_size_mb': 0,
            'file_count': 0,
            'branch_count': 0,
            'zip_file_count': 0,
            'pyc_file_count': 0,
            'temp_dir_count': 0,
            'large_files': [],
            'health_score': 0.0,
            'issues': []
        }

        try:
            # Repository size
            result = subprocess.run(
                ['du', '-sm', '.'],
                capture_output=True,
                text=True,
                cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                metrics['repository_size_mb'] = int(result.stdout.split()[0])

            # File count
            result = subprocess.run(
                ['find', '.', '-type', ''],
                capture_output=True,
                text=True,
                cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                metrics['file_count'] = len(result.stdout.strip().split('\n'))

            # Branch count
            result = subprocess.run(
                ['git', 'branch', '-r'],
                capture_output=True,
                text=True,
                cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                metrics['branch_count'] = len([line for line in result.stdout.strip().split('\n') if line.strip()])

            # ZIP file count
            zip_files = list(self.repo_path.glob('*.zip'))
            metrics['zip_file_count'] = len(zip_files)

            # Python cache files
            result = subprocess.run(
                ['find', '.', '-name', '*.pyc', '-type', ''],
                capture_output=True,
                text=True,
                cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                pyc_files = result.stdout.strip().split('\n')
                metrics['pyc_file_count'] = len([f for f in pyc_files if f])

            # Temporary directories
            result = subprocess.run(
                ['find', '.', '-name', '*tmp*', '-o', '-name', '*temp*', '-o', '-name', '*backup*', '-type', 'd'],
                capture_output=True,
                text=True,
                cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                temp_dirs = result.stdout.strip().split('\n')
                metrics['temp_dir_count'] = len([d for d in temp_dirs if d and not d.startswith('./.venv')])

            # Large files (>10MB)
            result = subprocess.run(
                ['find', '.', '-type', '', '-size', '+10M'],
                capture_output=True,
                text=True,
                cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                large_files = result.stdout.strip().split('\n')
                metrics['large_files'] = [f for f in large_files if f]

            # Calculate health score
            metrics['health_score'] = self.calculate_health_score(metrics)

            # Check for issues
            metrics['issues'] = self.check_issues(metrics)

        except (OSError, ValueError, RuntimeError) as e:
            self.logger.error(f"Error collecting metrics: {e}")
            metrics['error'] = str(e)

        return metrics

    def calculate_health_score(self, metrics: Dict) -> float:
        """Calculate overall health score (0-10).

        Args:
            metrics: Current metrics dictionary

        Returns:
            Health score between 0 and 10
        """
        score = 10.0

        # Size penalty
        if metrics['repository_size_mb'] > self.thresholds['max_size_mb']:
            score -= min(2.0, (metrics['repository_size_mb'] - self.thresholds['max_size_mb']) / 100)

        # File count penalty
        if metrics['file_count'] > self.thresholds['max_files']:
            score -= min(2.0, (metrics['file_count'] - self.thresholds['max_files']) / 5000)

        # Branch penalty
        if metrics['branch_count'] > self.thresholds['max_branches']:
            score -= min(1.5, (metrics['branch_count'] - self.thresholds['max_branches']) / 10)

        # ZIP file penalty
        if metrics['zip_file_count'] > self.thresholds['max_zip_files']:
            score -= min(1.0, (metrics['zip_file_count'] - self.thresholds['max_zip_files']) / 5)

        # Python cache penalty
        if metrics['pyc_file_count'] > self.thresholds['max_pyc_files']:
            score -= min(2.0, metrics['pyc_file_count'] / 1000)

        # Temporary directories penalty
        if metrics['temp_dir_count'] > self.thresholds['max_temp_dirs']:
            score -= min(1.0, (metrics['temp_dir_count'] - self.thresholds['max_temp_dirs']) / 5)

        # Large files penalty
        if len(metrics['large_files']) > 3:
            score -= min(0.5, len(metrics['large_files']) / 10)

        return max(0.0, round(score, 1))

    def check_issues(self, metrics: Dict) -> List[str]:
        """Check for specific issues based on metrics.

        Args:
            metrics: Current metrics dictionary

        Returns:
            List of issue descriptions
        """
        issues = []

        if metrics['repository_size_mb'] > self.thresholds['max_size_mb']:
            issues.append(f"Repository size ({metrics['repository_size_mb']}MB) exceeds threshold ({self.thresholds['max_size_mb']}MB)")

        if metrics['file_count'] > self.thresholds['max_files']:
            issues.append(f"File count ({metrics['file_count']}) exceeds threshold ({self.thresholds['max_files']})")

        if metrics['branch_count'] > self.thresholds['max_branches']:
            issues.append(f"Branch count ({metrics['branch_count']}) exceeds threshold ({self.thresholds['max_branches']})")

        if metrics['pyc_file_count'] > self.thresholds['max_pyc_files']:
            issues.append(f"Python cache files detected ({metrics['pyc_file_count']})")

        if metrics['temp_dir_count'] > self.thresholds['max_temp_dirs']:
            issues.append(f"Too many temporary directories ({metrics['temp_dir_count']})")

        if len(metrics['large_files']) > 3:
            issues.append(f"Multiple large files detected ({len(metrics['large_files'])})")

        return issues

    def save_metrics(self, metrics: Dict):
        """Save metrics to historical data.

        Args:
            metrics: Metrics dictionary to save
        """
        metrics_dir = self.repo_path / '.gitwiz' / 'metrics'
        metrics_dir.mkdir(parents=True, exist_ok=True)

        # Save to daily file
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        metrics_file = metrics_dir / f'health_{date_str}.json'

        # Load existing metrics for the day
        daily_metrics = []
        if metrics_file.exists():
            try:
                with open(metrics_file, encoding="utf-8") as f:
                    daily_metrics = json.load(f)
            except (OSError, ValueError, RuntimeError):
                pass

        daily_metrics.append(metrics)

        # Save updated metrics
        with open(metrics_file, 'w', encoding="utf-8") as f:
            json.dump(daily_metrics, f, indent=2)

        # Clean old metrics
        self.cleanup_old_metrics(metrics_dir)

    def cleanup_old_metrics(self, metrics_dir: Path):
        """Clean up old metric files.

        Args:
            metrics_dir: Directory containing metric files
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(
            days=self.config['metrics_retention_days']
        )

        for file_path in metrics_dir.glob('health_*.json'):
            try:
                file_date_str = file_path.stem.replace('health_', '')
                file_date = datetime.datetime.strptime(file_date_str, '%Y-%m-%d')

                if file_date < cutoff_date:
                    file_path.unlink()
                    self.logger.info(f"Cleaned up old metrics file: {file_path}")
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.warning(f"Error cleaning metrics file {file_path}: {e}")

    def send_alert(self, metrics: Dict):
        """Send alert if health issues are detected.

        Args:
            metrics: Current metrics dictionary
        """
        if not metrics['issues'] and metrics['health_score'] >= self.thresholds['min_health_score']:
            return

        alert_message = self.format_alert_message(metrics)

        # Log alert
        self.logger.warning(f"Health alert: {alert_message}")

        # File notification
        if self.config['notifications']['file']:
            try:
                with open(self.config['notifications']['file'], 'a', encoding="utf-8") as f:
                    f.write(f"{datetime.datetime.now().isoformat()}: {alert_message}\n")
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.error(f"Error writing alert to file: {e}")

    def format_alert_message(self, metrics: Dict) -> str:
        """Format alert message.

        Args:
            metrics: Current metrics dictionary

        Returns:
            Formatted alert message
        """
        message_parts = [
            f"Repository Health Alert - Score: {metrics['health_score']}/10",
            f"Size: {metrics['repository_size_mb']}MB",
            f"Files: {metrics['file_count']}",
            f"Branches: {metrics['branch_count']}"
        ]

        if metrics['issues']:
            message_parts.append("Issues:")
            message_parts.extend([f"  - {issue}" for issue in metrics['issues']])

        return " | ".join(message_parts)

    def generate_health_report(self, days: int = 7) -> str:
        """Generate health report from historical data.

        Args:
            days: Number of days to include in report

        Returns:
            Formatted health report
        """
        metrics_dir = self.repo_path / '.gitwiz' / 'metrics'

        if not metrics_dir.exists():
            return "No historical metrics available"

        # Collect metrics from last N days
        historical_metrics = []
        for i in range(days):
            date = datetime.datetime.now() - datetime.timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            metrics_file = metrics_dir / f'health_{date_str}.json'

            if metrics_file.exists():
                try:
                    with open(metrics_file, encoding="utf-8") as f:
                        daily_metrics = json.load(f)
                        historical_metrics.extend(daily_metrics)
                except (OSError, ValueError, RuntimeError):
                    continue

        if not historical_metrics:
            return "No historical metrics found"

        # Generate report
        report = []
        report.append("# Aurora CloudBank - Health Monitoring Report")
        report.append(f"**Period:** Last {days} days")
        report.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append("")

        # Latest metrics
        latest = historical_metrics[-1] if historical_metrics else {}
        report.append("## Current Status")
        report.append("")
        report.append(f"- **Health Score:** {latest.get('health_score', 'N/A')}/10")
        report.append(f"- **Repository Size:** {latest.get('repository_size_mb', 'N/A')}MB")
        report.append(f"- **File Count:** {latest.get('file_count', 'N/A')}")
        report.append(f"- **Branch Count:** {latest.get('branch_count', 'N/A')}")
        report.append(f"- **ZIP Files:** {latest.get('zip_file_count', 'N/A')}")
        report.append("")

        # Issues
        if latest.get('issues'):
            report.append("## Current Issues")
            report.append("")
            for issue in latest['issues']:
                report.append(f"- ⚠️ {issue}")
            report.append("")

        # Trends
        if len(historical_metrics) > 1:
            report.append("## Trends")
            report.append("")

            # Health score trend
            scores = [m.get('health_score', 0) for m in historical_metrics[-7:]]
            if scores:
                avg_score = sum(scores) / len(scores)
                trend = "📈 Improving" if scores[-1] > scores[0] else "📉 Declining" if scores[-1] < scores[0] else "➡️ Stable"
                report.append(f"- **Health Score:** {trend} (7-day avg: {avg_score:.1f})")

            # Size trend
            sizes = [m.get('repository_size_mb', 0) for m in historical_metrics[-7:]]
            if sizes:
                size_change = sizes[-1] - sizes[0]
                trend = "📈 Growing" if size_change > 10 else "📉 Shrinking" if size_change < -10 else "➡️ Stable"
                report.append(f"- **Repository Size:** {trend} ({size_change:+.0f}MB over 7 days)")

        return "\n".join(report)

    def run_monitoring_loop(self, interval_minutes: int = 60):
        """Run continuous monitoring loop.

        Args:
            interval_minutes: Minutes between health checks
        """
        self.logger.info(f"Starting health monitoring (interval: {interval_minutes} minutes)")

        while True:
            try:
                # Collect metrics
                metrics = self.collect_metrics()

                # Save metrics
                self.save_metrics(metrics)

                # Check for alerts
                self.send_alert(metrics)

                # Log status
                self.logger.info(
                    f"Health check complete - Score: {metrics['health_score']}/10, "
                    f"Size: {metrics['repository_size_mb']}MB, "
                    f"Files: {metrics['file_count']}, "
                    f"Issues: {len(metrics['issues'])}"
                )

                # Wait for next check
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


def main():
    """Main function for health monitoring CLI."""
    parser = argparse.ArgumentParser(description='Aurora CloudBank Health Monitoring')
    parser.add_argument('--check', action='store_true', help='Run single health check')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--report', action='store_true', help='Generate health report')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in minutes')
    parser.add_argument('--days', type=int, default=7, help='Days to include in report')
    parser.add_argument('--output', help='Output file for report')

    args = parser.parse_args()

    monitor = HealthMonitor()

    if args.check:
        print("🔍 Running health check...")
        metrics = monitor.collect_metrics()

        print(f"📊 Health Score: {metrics['health_score']}/10")
        print(f"💾 Repository Size: {metrics['repository_size_mb']}MB")
        print(f"📁 File Count: {metrics['file_count']}")
        print(f"🌿 Branch Count: {metrics['branch_count']}")
        print(f"📦 ZIP Files: {metrics['zip_file_count']}")

        if metrics['issues']:
            print("\n⚠️ Issues:")
            for issue in metrics['issues']:
                print(f"  - {issue}")
        else:
            print("\n✅ No issues detected")

        monitor.save_metrics(metrics)

    elif args.report:
        print("📄 Generating health report...")
        report = monitor.generate_health_report(args.days)

        if args.output:
            with open(args.output, 'w', encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Report saved to {args.output}")
        else:
            print(report)

    elif args.monitor:
        monitor.run_monitoring_loop(args.interval)

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
