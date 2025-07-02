#!/usr/bin/env python3
"""
Aurora CloudBank - Repository Health Monitoring System
Continuous monitoring and alerting for repository health metrics.
"""

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import psutil


class RepositoryHealthMonitor:
    """Monitors repository health and triggers automated maintenance."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.config = self._load_monitoring_config()
        self.history_file = self.repo_path / ".gitwiz" / "health_history.jsonl"
        self.alerts_file = self.repo_path / ".gitwiz" / "alerts.json"

    def _load_monitoring_config(self) -> Dict:
        """Load monitoring configuration with thresholds."""
        return {
            'thresholds': {
                'repository_size_mb': 800,      # Alert if over 800MB
                'file_count': 30000,            # Alert if over 30k files
                'zip_file_count': 20,           # Alert if over 20 ZIP files
                'branch_count': 25,             # Alert if over 25 branches
                'cache_files': 100,             # Alert if over 100 cache files
                'temp_files': 50                # Alert if over 50 temp files
            },
            'monitoring_intervals': {
                'health_check': 3600,           # Every hour
                'branch_analysis': 86400,       # Daily
                'cleanup_scan': 21600,          # Every 6 hours
                'alert_check': 1800             # Every 30 minutes
            },
            'cleanup_triggers': {
                'auto_cleanup_threshold': 0.8,  # 80% of threshold
                'emergency_cleanup_threshold': 1.2  # 120% of threshold
            },
            'notification_channels': {
                'console': True,
                'file_log': True,
                'webhook': False  # Can be configured for Slack/Discord
            }
        }

    def collect_health_metrics(self) -> Dict:
        """Collect comprehensive repository health metrics."""
        metrics = {
            'timestamp': datetime.datetime.now().isoformat(),
            'repository_size_mb': 0,
            'file_count': 0,
            'file_types': {},
            'zip_files': {'count': 0, 'total_size_mb': 0, 'files': []},
            'branches': {'total': 0, 'stale': 0, 'categories': {}},
            'cache_files': {'pyc_count': 0, 'pycache_dirs': 0, 'so_files': 0},
            'temp_files': {'count': 0, 'patterns': {}},
            'git_metrics': {},
            'disk_usage': {},
            'health_score': 0.0
        }

        try:
            # Repository size
            metrics['repository_size_mb'] = self._get_repo_size_mb()

            # File analysis
            file_stats = self._analyze_files()
            metrics.update(file_stats)

            # Branch analysis
            branch_stats = self._analyze_branches()
            metrics['branches'] = branch_stats

            # Git metrics
            metrics['git_metrics'] = self._collect_git_metrics()

            # Disk usage
            metrics['disk_usage'] = self._get_disk_usage()

            # Calculate health score
            metrics['health_score'] = self._calculate_health_score(metrics)

        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error collecting metrics: {e}")
            metrics['error'] = str(e)

        return metrics

    def _get_repo_size_mb(self) -> float:
        """Get repository size in MB."""
        try:
            _ = subprocess.run(['du', '-sm', '.'],
                               capture_output=True, text=True, cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                return float(result.stdout.split()[0])
        except (OSError, ValueError, RuntimeError):
            pass
        return 0.0

    def _analyze_files(self) -> Dict:
        """Analyze file types and patterns."""
        file_stats = {
            'file_count': 0,
            'file_types': {},
            'zip_files': {'count': 0, 'total_size_mb': 0, 'files': []},
            'cache_files': {'pyc_count': 0, 'pycache_dirs': 0, 'so_files': 0},
            'temp_files': {'count': 0, 'patterns': {}}
        }

        try:
            # Count all files
            _ = subprocess.run(['find', '.', '-type', ''],
                               capture_output=True, text=True, cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                file_stats['file_count'] = len([f for f in files if f])

                # Analyze file types
                for file_path in files:
                    if not file_path:
                        continue

                    ext = Path(file_path).suffix.lower()
                    file_stats['file_types'][ext] = file_stats['file_types'].get(ext, 0) + 1

                    # Special pattern analysis
                    if ext == '.zip':
                        size_mb = self._get_file_size_mb(file_path)
                        file_stats['zip_files']['count'] += 1
                        file_stats['zip_files']['total_size_mb'] += size_mb
                        file_stats['zip_files']['files'].append({
                            'path': file_path,
                            'size_mb': size_mb
                        })

                    elif ext == '.pyc':
                        file_stats['cache_files']['pyc_count'] += 1

                    elif ext == '.so':
                        file_stats['cache_files']['so_files'] += 1

                    elif any(pattern in file_path.lower() for pattern in ['tmp', 'temp', 'backup', 'cache']):
                        file_stats['temp_files']['count'] += 1
                        pattern = next((p for p in ['tmp', 'temp', 'backup', 'cache']
                                        if p in file_path.lower()), 'other')
                        file_stats['temp_files']['patterns'][pattern] = \
                            file_stats['temp_files']['patterns'].get(pattern, 0) + 1

            # Count __pycache__ directories
            _ = subprocess.run(['find', '.', '-name', '__pycache__', '-type', 'd'],
                               capture_output=True, text=True, cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                dirs = [d for d in result.stdout.strip().split('\n') if d]
                file_stats['cache_files']['pycache_dirs'] = len(dirs)

        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error analyzing files: {e}")

        return file_stats

    def _get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB."""
        try:
            full_path = self.repo_path / file_path.lstrip('./')
            if full_path.exists():
                return full_path.stat().st_size / (1024 * 1024)
        except (OSError, ValueError, RuntimeError):
            pass
        return 0.0

    def _analyze_branches(self) -> Dict:
        """Analyze git branches."""
        branch_stats = {
            'total': 0,
            'stale': 0,
            'categories': {'codex': 0, 'dependabot': 0, 'alert-autofix': 0, 'backup': 0, 'other': 0}
        }

        try:
            _ = subprocess.run(['git', 'branch', '-r'],
                               capture_output=True, text=True, cwd=self.repo_path, shell=False, check=False)
            if result.returncode == 0:
                branches = [b.strip() for b in result.stdout.split('\n') if b.strip()]
                branch_stats['total'] = len(branches)

                for branch in branches:
                    if 'codex' in branch:
                        branch_stats['categories']['codex'] += 1
                    elif 'dependabot' in branch:
                        branch_stats['categories']['dependabot'] += 1
                    elif 'alert-autofix' in branch:
                        branch_stats['categories']['alert-autofix'] += 1
                    elif 'backup' in branch:
                        branch_stats['categories']['backup'] += 1
                    else:
                        branch_stats['categories']['other'] += 1

                # Count stale branches (simplified - could be enhanced)
                branch_stats['stale'] = branch_stats['categories']['codex'] + \
                    branch_stats['categories']['dependabot'] + \
                    branch_stats['categories']['alert-autofix']

        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error analyzing branches: {e}")

        return branch_stats

    def _collect_git_metrics(self) -> Dict:
        """Collect Git-specific metrics."""
        git_metrics = {
            'commits_today': 0,
            'commits_this_week': 0,
            'contributors': 0,
            'uncommitted_changes': False,
            'unpushed_commits': 0
        }

        try:
            # Check for uncommitted changes
            _ = subprocess.run(['git', 'status', '--porcelain'],
                               capture_output=True, text=True, cwd=self.repo_path, shell=False, check=False)
            git_metrics['uncommitted_changes'] = bool(result.stdout.strip())

            # Count recent commits
            today = datetime.date.today()
            week_ago = today - datetime.timedelta(days=7)

            _ = subprocess.run(['git', 'log', '--since', week_ago.isoformat(, shell=False, check=False), '--oneline'],
                               capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode == 0:
                git_metrics['commits_this_week'] = len(result.stdout.strip().split('\n'))

            _ = subprocess.run(['git', 'log', '--since', today.isoformat(, shell=False, check=False), '--oneline'],
                               capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode == 0:
                git_metrics['commits_today'] = len(result.stdout.strip().split('\n'))

        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error collecting git metrics: {e}")

        return git_metrics

    def _get_disk_usage(self) -> Dict:
        """Get disk usage information."""
        try:
            usage = psutil.disk_usage(str(self.repo_path))
            return {
                'total_gb': usage.total / (1024**3),
                'used_gb': usage.used / (1024**3),
                'free_gb': usage.free / (1024**3),
                'usage_percent': (usage.used / usage.total) * 100
            }
        except (OSError, ValueError, RuntimeError):
            return {}

    def _calculate_health_score(self, metrics: Dict) -> float:
        """Calculate overall repository health score (0-10)."""
        score = 10.0
        thresholds = self.config['thresholds']

        # Size penalties
        if metrics['repository_size_mb'] > thresholds['repository_size_mb']:
            score -= 1.5

        # File count penalties
        if metrics['file_count'] > thresholds['file_count']:
            score -= 1.0

        # ZIP file penalties
        if metrics['zip_files']['count'] > thresholds['zip_file_count']:
            score -= 1.0

        # Branch penalties
        if metrics['branches']['total'] > thresholds['branch_count']:
            score -= 1.0

        # Cache file penalties
        cache_total = (metrics['cache_files']['pyc_count'] +
                       metrics['cache_files']['pycache_dirs'] +
                       metrics['cache_files']['so_files'])
        if cache_total > thresholds['cache_files']:
            score -= 2.0

        # Temp file penalties
        if metrics['temp_files']['count'] > thresholds['temp_files']:
            score -= 0.5

        return max(0.0, min(10.0, score))

    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """Check for alert conditions and return alerts."""
        alerts = []
        thresholds = self.config['thresholds']

        # Size alert
        if metrics['repository_size_mb'] > thresholds['repository_size_mb']:
            alerts.append({
                'type': 'size_warning',
                'severity': 'medium',
                'message': f"Repository size ({metrics['repository_size_mb']:.1f}MB) exceeds threshold ({thresholds['repository_size_mb']}MB)",
                'timestamp': datetime.datetime.now().isoformat(),
                'metric': metrics['repository_size_mb'],
                'threshold': thresholds['repository_size_mb']
            })

        # File count alert
        if metrics['file_count'] > thresholds['file_count']:
            alerts.append({
                'type': 'file_count_warning',
                'severity': 'medium',
                'message': f"File count ({metrics['file_count']}) exceeds threshold ({thresholds['file_count']})",
                'timestamp': datetime.datetime.now().isoformat(),
                'metric': metrics['file_count'],
                'threshold': thresholds['file_count']
            })

        # Branch count alert
        if metrics['branches']['total'] > thresholds['branch_count']:
            alerts.append({
                'type': 'branch_warning',
                'severity': 'low',
                'message': f"Branch count ({metrics['branches']['total']}) exceeds threshold ({thresholds['branch_count']})",
                'timestamp': datetime.datetime.now().isoformat(),
                'metric': metrics['branches']['total'],
                'threshold': thresholds['branch_count']
            })

        # Cache files alert
        cache_total = (metrics['cache_files']['pyc_count'] +
                       metrics['cache_files']['pycache_dirs'])
        if cache_total > 0:
            alerts.append({
                'type': 'cache_warning',
                'severity': 'high',
                'message': f"Cache files detected: {cache_total} files/directories",
                'timestamp': datetime.datetime.now().isoformat(),
                'metric': cache_total,
                'threshold': 0
            })

        # Health score alert
        if metrics['health_score'] < 7.0:
            severity = 'high' if metrics['health_score'] < 5.0 else 'medium'
            alerts.append({
                'type': 'health_score_warning',
                'severity': severity,
                'message': f"Repository health score is low: {metrics['health_score']:.1f}/10",
                'timestamp': datetime.datetime.now().isoformat(),
                'metric': metrics['health_score'],
                'threshold': 7.0
            })

        return alerts

    def log_metrics(self, metrics: Dict):
        """Log metrics to history file."""
        try:
            os.makedirs(self.history_file.parent, exist_ok=True)
            with open(self.history_file, 'a', encoding="utf-8") as f:
                f.write(json.dumps(metrics) + '\n')
        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error logging metrics: {e}")

    def save_alerts(self, alerts: List[Dict]):
        """Save current alerts to file."""
        try:
            os.makedirs(self.alerts_file.parent, exist_ok=True)
            with open(self.alerts_file, 'w', encoding="utf-8") as f:
                json.dump({
                    'timestamp': datetime.datetime.now().isoformat(),
                    'alerts': alerts
                }, f, indent=2)
        except (OSError, ValueError, RuntimeError) as e:
            print(f"Error saving alerts: {e}")

    def generate_health_report(self, metrics: Dict, alerts: List[Dict]) -> str:
        """Generate a human-readable health report."""
        report = [
            "# Repository Health Monitoring Report",
            f"**Generated:** {metrics.get('timestamp', 'Unknown')}",
            f"**Health Score:** {metrics.get('health_score', 0):.1f}/10.0",
            "",
            "## Key Metrics",
            f"- **Repository Size:** {metrics.get('repository_size_mb', 0):.1f} MB",
            f"- **File Count:** {metrics.get('file_count', 0):,}",
            f"- **ZIP Files:** {metrics.get('zip_files', {}).get('count', 0)}",
            f"- **Branches:** {metrics.get('branches', {}).get('total', 0)}",
            f"- **Cache Files:** {metrics.get('cache_files', {}).get('pyc_count', 0)} .pyc + {metrics.get('cache_files', {}).get('pycache_dirs', 0)} dirs",
            ""
        ]

        if alerts:
            report.extend([
                "## 🚨 Active Alerts",
                ""
            ])

            for alert in alerts:
                severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}.get(alert['severity'], '⚪')
                report.append(f"- {severity_emoji} **{alert['type']}**: {alert['message']}")

            report.append("")
        else:
            report.extend([
                "## ✅ No Active Alerts",
                "Repository health is within acceptable parameters.",
                ""
            ])

        # Branch breakdown
        branches = metrics.get('branches', {})
        if branches.get('categories'):
            report.extend([
                "## Branch Analysis",
                ""
            ])
            for category, count in branches['categories'].items():
                if count > 0:
                    report.append(f"- **{category}**: {count} branches")
            report.append("")

        return "\n".join(report)

    def run_monitoring_cycle(self) -> Dict:
        """Run a complete monitoring cycle."""
        print("🔍 Running repository health monitoring cycle...")

        # Collect metrics
        metrics = self.collect_health_metrics()

        # Check for alerts
        alerts = self.check_alerts(metrics)

        # Log metrics
        self.log_metrics(metrics)

        # Save alerts
        self.save_alerts(alerts)

        # Generate report
        report = self.generate_health_report(metrics, alerts)

        # Save report
        report_path = self.repo_path / "repository_health_current.md"
        report_path.write_text(report)

        print(f"📊 Health Score: {metrics.get('health_score', 0):.1f}/10")
        print(f"🚨 Alerts: {len(alerts)}")
        print(f"📄 Report saved to: {report_path}")

        return {
            'metrics': metrics,
            'alerts': alerts,
            'report': report
        }


def main():
    """Main execution function."""
    monitor = RepositoryHealthMonitor()

    print("🔄 Aurora CloudBank - Repository Health Monitor")
    print("=" * 50)

    result = monitor.run_monitoring_cycle()

    # Print summary
    metrics = result['metrics']
    alerts = result['alerts']

    print("\n📈 Current Status:")
    print(f"   Repository: {metrics.get('repository_size_mb', 0):.1f} MB")
    print(f"   Files: {metrics.get('file_count', 0):,}")
    print(f"   Branches: {metrics.get('branches', {}).get('total', 0)}")
    print(f"   Health: {metrics.get('health_score', 0):.1f}/10")

    if alerts:
        print(f"\n⚠️  {len(alerts)} alerts require attention")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"   - {alert['type']}: {alert['message']}")
    else:
        print("\n✅ No alerts - repository health is good!")


if __name__ == "__main__":
    main()
