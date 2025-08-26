#!/usr/bin/env python3
"""
Aurora CloudBank - Continuous Canonical Validation Monitor
Real-time monitoring and validation of file changes against canonical specifications

This monitor:
1. Watches for file changes in the workspace
2. Automatically validates changes against ORION CORE canonical spec
3. Applies auto-fixes when safe
4. Alerts users to violations requiring attention
5. Maintains continuous canonical compliance
"""

import argparse
from watchdog.observers import Observer
from pathlib import Path
import time
import datetime
import json
import sys
import threading
from watchdog.events import FileSystemEventHandler
import yaml


# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from canonical_validator import CanonicalValidator
except ImportError:
    print("❌ Error: Could not import canonical_validator")
    sys.exit(1)


class CanonicalValidationHandler(FileSystemEventHandler):
    """File system event handler for canonical validation"""

    def __init__(self, validator, config):
        self.validator = validator
        self.config = config
        self.validation_queue = []
        self.processing_lock = threading.Lock()
        self.last_validation = {}
        self.debounce_delay = config.get("debounce_delay", 2.0)

    def should_validate_file(self, file_path):
        """Check if file should be validated"""
        path = Path(file_path)

        # Check if file exists and is a file
        if not path.exists() or not path.is_file():
            return False

        # Check file extension
        validatable_extensions = {".md", ".txt", ".js", ".ts", ".py", ".json", ".yaml", ".yml"}
        if path.suffix not in validatable_extensions:
            return False

        # Check exclude patterns
        exclude_patterns = self.config.get("exclude_patterns", [])
        for pattern in exclude_patterns:
            if path.match(pattern):
                return False

        return True

    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return

        file_path = event.src_path
        if self.should_validate_file(file_path):
            self.schedule_validation(file_path)

    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return

        file_path = event.src_path
        if self.should_validate_file(file_path):
            self.schedule_validation(file_path)

    def schedule_validation(self, file_path):
        """Schedule validation with debouncing"""
        with self.processing_lock:
            # Update last modification time
            self.last_validation[file_path] = time.time()

            # Schedule validation after debounce delay
            timer = threading.Timer(self.debounce_delay, self.validate_file, [file_path])
            timer.start()

    def validate_file(self, file_path):
        """Validate a specific file"""
        with self.processing_lock:
            # Check if file was modified again during debounce period
            last_mod = self.last_validation.get(file_path, 0)
            if time.time() - last_mod < self.debounce_delay:
                return  # Skip validation, file was modified again

        try:
            print("🔍 Validating: {Path(file_path).name}")
            results = self.validator.validate_file(file_path)

            if results:
                self.process_validation_results(file_path, results)
            else:
                print("  ✅ {Path(file_path).name} - No issues detected")

        except Exception as e:
            print("  ❌ Error validating {file_path}: {e}")

    def process_validation_results(self, file_path, results):
        """Process validation results and take appropriate actions"""
        auto_fixes = [r for r in results if r.status == "AUTO_FIXED"]
        escalations = [r for r in results if r.status == "ESCALATE"]
        critical = [r for r in escalations if r.severity == "CRITICAL"]
        high = [r for r in escalations if r.severity == "HIGH"]

        file_name = Path(file_path).name

        # Report auto-fixes
        if auto_fixes:
            print("  🔧 {file_name} - {len(auto_fixes)} auto-fixes applied")
            for fix in auto_fixes[:2]:  # Show first 2
                print("    ✅ {fix.message}")

        # Report critical issues
        if critical:
            print("  🚨 {file_name} - {len(critical)} CRITICAL issues!")
            for issue in critical:
                print("    ❗ {issue.message}")
                print("      Fix: {issue.suggested_fix}")
            self.alert_user(file_path, critical, "CRITICAL")

        # Report high priority issues
        elif high:
            print("  🔴 {file_name} - {len(high)} high priority issues")
            for issue in high[:1]:  # Show first issue
                print("    🔴 {issue.message}")
            if len(high) > 1:
                print("    ... and {len(high) - 1} more")

        # Log validation event
        self.log_validation_event(file_path, results)

    def alert_user(self, file_path, critical_issues, severity):
        """Generate user alert for critical issues"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_file = "CANONICAL_ALERT_{severity}_{timestamp.replace(':', '-').replace(' ', '_')}.md"

        with open(alert_file, "w", encoding="utf-8") as f:
            f.write("# Aurora CloudBank Canonical Alert - {severity}\n\n")
            f.write("**Timestamp**: {timestamp}\n")
            f.write("**File**: {file_path}\n")
            f.write("**Issues Detected**: {len(critical_issues)}\n\n")

            for i, issue in enumerate(critical_issues, 1):
                f.write("## Issue {i}: {issue.check_name}\n")
                f.write("**Severity**: {issue.severity}\n")
                f.write("**Message**: {issue.message}\n")
                f.write("**Suggested Fix**: {issue.suggested_fix}\n\n")

            f.write("## Immediate Actions Required\n")
            f.write("1. Stop current development work\n")
            f.write("2. Address critical canonical violations\n")
            f.write("3. Re-validate file after fixes\n")
            f.write("4. Delete this alert file when resolved\n")

        print("  📋 Alert generated: {alert_file}")

    def log_validation_event(self, file_path, results):
        """Log validation events for tracking"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "total_checks": len(results),
            "auto_fixes": len([r for r in results if r.status == "AUTO_FIXED"]),
            "escalations": len([r for r in results if r.status == "ESCALATE"]),
            "critical": len([r for r in results if r.status == "ESCALATE" and r.severity == "CRITICAL"]),
            "issues": [
                {"check": r.check_name, "status": r.status, "severity": r.severity, "message": r.message}
                for r in results
                if r.status != "PASS"
            ],
        }

        # Append to validation log
        log_file = "canonical_validation.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")


class ContinuousValidator:
    """Main continuous validation system"""

    def __init__(self, workspace_path="."):
        self.workspace_path = Path(workspace_path)
        self.validator = CanonicalValidator(workspace_path)
        self.config = self.load_config()
        self.observer = None
        self.running = False

    def load_config(self):
        """Load validation configuration"""
        config_file = self.workspace_path / "config" / "canonical_validation.yaml"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("integration", {}).get("file_watcher", {})

        # Default configuration
        return {
            "enabled": True,
            "watch_patterns": ["*.md", "*.js", "*.py", "*.json"],
            "debounce_delay": 2000,  # milliseconds
            "exclude_patterns": ["node_modules/**", ".git/**", "*.log", "*.tmp", "build/**", "dist/**"],
        }

    def start(self):
        """Start continuous validation monitoring"""
        if not self.config.get("enabled", True):
            print("📴 Continuous validation is disabled in configuration")
            return

        print("🛰️ Aurora CloudBank Continuous Canonical Validation")
        print("=" * 55)
        print("📁 Monitoring workspace: {self.workspace_path.absolute()}")
        print("⏱️ Debounce delay: {self.config.get('debounce_delay', 2000)}ms")
        print("🔍 Watching for file changes...\n")

        # Create event handler
        handler = CanonicalValidationHandler(
            self.validator, {**self.config, "debounce_delay": self.config.get("debounce_delay", 2000) / 1000}
        )

        # Set up file system observer
        self.observer = Observer()
        self.observer.schedule(handler, str(self.workspace_path), recursive=True)

        # Start monitoring
        self.observer.start()
        self.running = True

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop continuous validation monitoring"""
        if self.observer:
            print("\n🛑 Stopping continuous validation monitor...")
            self.observer.stop()
            self.observer.join()
            self.running = False
            print("✅ Monitor stopped")

    def validate_workspace_once(self):
        """Run one-time validation of entire workspace"""
        print("🔍 Running one-time workspace validation...")
        results = self.validator.validate_workspace()

        # Generate report
        report = self.validator.generate_report()
        print(report)

        # Save report
        self.validator.save_report("CONTINUOUS_VALIDATION_REPORT.md")
        return results


def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(description="Aurora CloudBank Continuous Canonical Validation Monitor")
    parser.add_argument("--once", action="store_true", help="Run validation once instead of continuous monitoring")
    parser.add_argument("--workspace", default=".", help="Workspace path to monitor (default: current directory)")

    args = parser.parse_args()

    # Initialize validator
    monitor = ContinuousValidator(args.workspace)

    if args.once:
        # Run one-time validation
        monitor.validate_workspace_once()
    else:
        # Start continuous monitoring
        monitor.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print("❌ Error: {e}")
        sys.exit(1)
