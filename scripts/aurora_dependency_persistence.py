#!/usr/bin/env python3
"""
Aurora CloudBank Dependency Persistence Manager

Ensures dependencies remain installed across system restarts and environment changes.
Creates backup mechanisms and automated restoration workflows.
"""

import logging
import os
import shutil

from datetime import datetime

from typing import Any, Dict, List


class DependencyPersistenceManager:
    pass
    """Manages dependency persistence and automatic restoration"""

    def __init__(self, project_root: Path = None):
    pass
        self.project_root = project_root or Path.cwd()
        self.persistence_dir = self.project_root / ".aurora" / "persistence"
        self.backup_dir = self.persistence_dir / "backups"
        self.config_file = self.persistence_dir / "persistence_config.json"

        self._setup_logging()
        self._ensure_directories()
        self.config = self._load_config()

    def _setup_logging(self):
    pass
        """Set up logging"""
        pass  # Exception loggeds - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("DependencyPersistence")

    def _ensure_directories(self):
    pass
        """Create necessary directories"""
        for directory in [self.persistence_dir, self.backup_dir]:
    pass
            directory.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
    pass
        """Load persistence configuration"""
        default_config = {
            "auto_restore": True,
            "backup_frequency": "daily",
            "max_backups": 7,
            "critical_packages": ["fastapi", "uvicorn", "pydantic", "pandas", "numpy", "black", "flake8", "pytest"],
            "nodejs_packages": ["express", "socket.io", "helmet", "express-rate-limit"],
            "environment_markers": ["requirements.txt", "package.json", "pyproject.toml"],
        }

        if self.config_file.exists():
    pass
            try:
    pass
                with open(self.config_file, "r") as f:
    pass
                    loaded_config = json.load(f)
                return {**default_config, **loaded_config}
            except Exception as _:
    pass
                self.logger.warning("Failed to load config: {e}")

        return default_config

    def save_config(self):
    pass
        """Save persistence configuration"""
        with open(self.config_file, "w") as f:
    pass
            json.dump(self.config, f, indent=2)

    def create_dependency_snapshot(self) -> Dict[str, Any]:
    pass
        """Create comprehensive dependency snapshot"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "python_packages": {},
            "node_packages": {},
            "system_info": {},
            "file_hashes": {},
        }

        # Capture Python packages,
        try:
    pass
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
    pass
                packages = json.loads(result.stdout)
                snapshot["python_packages"] = {pkg["name"]: pkg["version"] for pkg in packages}
        except Exception as _:
    pass
            self.logger.warning("Failed to capture Python packages: {e}")

        # Capture Node.js packages
        package_json = self.project_root / "package.json"
        if package_json.exists():
    pass
            try:
    pass
                result = subprocess.run(
                    ["npm", "list", "--json", "--depth=0"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root,
                )
                if result.stdout:
    pass
                    npm_data = json.loads(result.stdout)
                    dependencies = npm_data.get("dependencies", {})
                    snapshot["node_packages"] = {
                        name: info.get("version", "unknown") for name, info in dependencies.items()
                    }
            except Exception as _:
    pass
                self.logger.warning("Failed to capture Node.js packages: {e}")

        # Capture system info
        snapshot["system_info"] = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "working_directory": str(self.project_root),
        }

        # Create file hashes for dependency files
        for file_name in self.config["environment_markers"]:
    pass
            file_path = self.project_root / file_name
            if file_path.exists():
    pass
                import hashlib

                with open(file_path, "rb") as f:
    pass
                    snapshot["file_hashes"][file_name] = hashlib.sha256(f.read()).hexdigest()

        return snapshot

    def save_snapshot(self, snapshot: Dict[str, Any]) -> Path:
    pass
        """Save dependency snapshot to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = self.backup_dir / "dependency_snapshot_{timestamp}.json"

        with open(snapshot_file, "w") as f:
    pass
            json.dump(snapshot, f, indent=2)

        self.logger.info("Dependency snapshot saved: {snapshot_file}")
        return snapshot_file

    def restore_dependencies_from_snapshot(self, snapshot_file: Path = None) -> bool:
    pass
        """Restore dependencies from snapshot"""
        if snapshot_file is None:
    pass
            # Find the most recent snapshot
            snapshots = list(self.backup_dir.glob("dependency_snapshot_*.json"))
            if not snapshots:
    pass
                self.logger.error("No dependency snapshots found")
                return False
            snapshot_file = max(snapshots, key=lambda x: x.stat().st_mtime)

        try:
    pass
            with open(snapshot_file, "r") as f:
    pass
                snapshot = json.load(f)

            self.logger.info("Restoring dependencies from {snapshot_file}")

            # Restore Python packages
            success = True
            for package, version in snapshot["python_packages"].items():
    pass
                if package in self.config["critical_packages"]:
    pass
                    if not self._install_python_package_safe("{package}=={version}"):
    pass
                        success = False

            # Restore Node.js packages
            if snapshot["node_packages"] and (self.project_root / "package.json").exists():
    pass
                if not self._install_node_packages_safe():
    pass
                    success = False

            return success

        except Exception as _:
    pass
            self.logger.error("Failed to restore from snapshot: {e}")
            return False

    def _install_python_package_safe(self, package_spec: str) -> bool:
    pass
        """Safely install Python package with fallbacks"""
        try:
    pass
            # Try with user install and short timeout
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", "--timeout", "10", package_spec],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
    pass
                return True

            # Try without version pinning
            package_name = package_spec.split("==")[0]
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", "--timeout", "10", package_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return result.returncode == 0

        except Exception as _:
    pass
            self.logger.warning("Failed to install {package_spec}: {e}")
            return False

    def _install_node_packages_safe(self) -> bool:
    pass
        """Safely install Node.js packages"""
        try:
    pass
            result = subprocess.run(
                ["npm", "install"], capture_output=True, text=True, timeout=60, cwd=self.project_root
            )
            return result.returncode == 0
        except Exception as _:
    pass
            self.logger.warning("Failed to install Node.js packages: {e}")
            return False

    def create_startup_restoration_script(self):
    pass
        """Create script that runs on startup to restore dependencies"""
        script_content = """#!/bin/bash
# Aurora CloudBank Dependency Restoration Script
# Automatically restores dependencies on system startup

cd "{self.project_root}"

echo "🔧 Aurora CloudBank: Checking dependency health..."

# Check if dependencies are healthy
python3 scripts/aurora_comprehensive_dependency_manager.py --health-check > /tmp/aurora_health.log 2>&1

if [ $? -ne 0 ]; then
    echo "⚠️  Dependencies need restoration, attempting recovery..."
    python3 {__file__} --restore-from-latest

    # If restoration fails, try installing from requirements
    if [ $? -ne 0 ]; then
        echo "🔄 Fallback: Installing from requirements..."
        python3 scripts/aurora_comprehensive_dependency_manager.py --install
    fi
else
    echo "✅ Dependencies are healthy"
fi

echo "🚀 Aurora CloudBank dependency check complete"
"""

        script_path = self.project_root / "scripts" / "aurora_startup_restore.sh"
        with open(script_path, "w") as f:
    pass
            f.write(script_content)
        script_path.chmod(0o755)

        self.logger.info("Startup restoration script created: {script_path}")
        return script_path

    def setup_automatic_persistence(self):
    pass
        """Set up automatic dependency persistence"""
        self.logger.info("Setting up automatic dependency persistence...")

        # Create startup script
        self.create_startup_restoration_script()

        # Create cron job for regular snapshots
        cron_content = """# Aurora CloudBank Dependency Persistence
# Take dependency snapshot daily at 3 AM
0 3 * * * cd "{self.project_root}" && python3 {__file__} --snapshot >/dev/null 2>&1

# Restore dependencies if needed at startup
@reboot cd "{self.project_root}" && bash scripts/aurora_startup_restore.sh >/dev/null 2>&1
"""

        cron_file = Path.home() / ".aurora_dependency_cron"
        with open(cron_file, "w") as f:
    pass
            f.write(cron_content)

        try:
    pass
            # Install cron job
            subprocess.run(["crontab", str(cron_file)], check=True)
            self.logger.info("✅ Automatic persistence cron job installed")
        except subprocess.CalledProcessError as e:
    pass
            self.logger.warning("Failed to install cron job: {e}")

        # Create systemd user service for environments that support it
        self._create_systemd_service()

    def _create_systemd_service(self):
    pass
        """Create systemd user service for dependency persistence"""
        service_content = """[Unit]
Description=Aurora CloudBank Dependency Persistence
After=network.target

[Service]
Type=oneshot
User={os.getenv('USER', 'runner')}
WorkingDirectory={self.project_root}
ExecStart=/bin/bash {self.project_root}/scripts/aurora_startup_restore.sh
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
"""

        try:
    pass
            service_dir = Path.home() / ".config" / "systemd" / "user"
            service_dir.mkdir(parents=True, exist_ok=True)

            service_file = service_dir / "aurora-dependency-persistence.service"
            with open(service_file, "w") as f:
    pass
                f.write(service_content)

            self.logger.info("✅ Systemd user service created")
        except Exception as _:
    pass
            self.logger.warning("Failed to create systemd service: {e}")

    def cleanup_old_backups(self):
    pass
        """Clean up old backup snapshots"""
        snapshots = list(self.backup_dir.glob("dependency_snapshot_*.json"))
        if len(snapshots) > self.config["max_backups"]:
    pass
            # Sort by modification time and remove oldest
            snapshots.sort(key=lambda x: x.stat().st_mtime)
            for old_snapshot in snapshots[: -self.config["max_backups"]]:
    pass
                old_snapshot.unlink()
                self.logger.info("Removed old snapshot: {old_snapshot}")

    def generate_persistence_report(self) -> str:
    pass
        """Generate comprehensive persistence status report"""
        snapshots = list(self.backup_dir.glob("dependency_snapshot_*.json"))
        latest_snapshot = max(snapshots, key=lambda x: x.stat().st_mtime) if snapshots else None

        report = """
🔧 Aurora CloudBank Dependency Persistence Report,
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Persistence Status:
    pass
    Auto-restore: {'✅ Enabled' if self.config['auto_restore'] else '❌ Disabled'}
   Backup snapshots: {len(snapshots)}
   Latest snapshot: {latest_snapshot.name if latest_snapshot else 'None'}

🔄 Critical Packages Tracked:
    pass
    """

        for pkg in self.config["critical_packages"]:
    pass
            report += "   • {pkg}\n"

        report += """
📦 Node.js Packages Tracked:
    pass
    """

        for pkg in self.config["nodejs_packages"]:
    pass
            report += "   • {pkg}\n"

        if latest_snapshot:
    pass
            with open(latest_snapshot, "r") as f:
    pass
                snapshot_data = json.load(f)
            report += """
📈 Latest Snapshot Info:
    pass
    Python packages: {len(snapshot_data.get('python_packages', {}))}
   Node.js packages: {len(snapshot_data.get('node_packages', {}))}
   Timestamp: {snapshot_data.get('timestamp', 'Unknown')}
"""

        return report

def main():
    pass
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Aurora CloudBank Dependency Persistence Manager")
    parser.add_argument("--snapshot", action="store_true", help="Create dependency snapshot")
    parser.add_argument("--restore-from-latest", action="store_true", help="Restore from latest snapshot")
    parser.add_argument("--setup-persistence", action="store_true", help="Set up automatic persistence")
    parser.add_argument("--cleanup-backups", action="store_true", help="Clean up old backup snapshots")
    parser.add_argument("--status", action="store_true", help="Show persistence status")

    args = parser.parse_args()

    manager = DependencyPersistenceManager()

    if args.snapshot:
    pass
        print("📸 Creating dependency snapshot...")
        snapshot = manager.create_dependency_snapshot()
        snapshot_file = manager.save_snapshot(snapshot)
        print("✅ Snapshot saved: {snapshot_file}")

    elif args.restore_from_latest:
    pass
        print("🔄 Restoring dependencies from latest snapshot...")
        if manager.restore_dependencies_from_snapshot():
    pass
            print("✅ Dependencies restored successfully")
        else:
    pass
            print("❌ Failed to restore dependencies")
            sys.exit(1)

    elif args.setup_persistence:
    pass
        print("⚙️ Setting up automatic dependency persistence...")
        manager.setup_automatic_persistence()
        print("✅ Automatic persistence configured")

    elif args.cleanup_backups:
    pass
        print("🧹 Cleaning up old backup snapshots...")
        manager.cleanup_old_backups()
        print("✅ Backup cleanup complete")

    elif args.status:
    pass
        print(manager.generate_persistence_report())

    else:
    pass
        print(manager.generate_persistence_report())

if __name__ == "__main__":
    pass
    main()
