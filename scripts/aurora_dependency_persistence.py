#!/usr/bin/env python3
"""
Aurora CloudBank Dependency Persistence Manager

Ensures dependencies remain installed across system restarts and environment changes.
Creates backup mechanisms and automated restoration workflows.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging

class DependencyPersistenceManager:
    """Manages dependency persistence and automatic restoration"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.persistence_dir = self.project_root / ".aurora" / "persistence"
        self.backup_dir = self.persistence_dir / "backups"
        self.config_file = self.persistence_dir / "persistence_config.json"
        
        self._setup_logging()
        self._ensure_directories()
        self.config = self._load_config()
        
    def _setup_logging(self):
        """Set up logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DependencyPersistence')
        
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [self.persistence_dir, self.backup_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _load_config(self) -> Dict[str, Any]:
        """Load persistence configuration"""
        default_config = {
            "auto_restore": True,
            "backup_frequency": "daily",
            "max_backups": 7,
            "critical_packages": [
                "fastapi", "uvicorn", "pydantic", "pandas", "numpy",
                "black", "flake8", "pytest"
            ],
            "nodejs_packages": [
                "express", "socket.io", "helmet", "express-rate-limit"
            ],
            "environment_markers": [
                "requirements.txt", "package.json", "pyproject.toml"
            ]
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                return {**default_config, **loaded_config}
            except Exception as e:
                pass
logger.warning("Failed to load config: %s", str(e)[:100])

        return default_config
        
    def save_config(self):
        """Save persistence configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def create_dependency_snapshot(self) -> Dict[str, Any]:
        """Create comprehensive dependency snapshot"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "python_packages": {},
            "node_packages": {},
            "system_info": {},
            "file_hashes": {}
        }
        
        # Capture Python packages
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], 
            capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                snapshot["python_packages"] = {pkg["name"]: pkg["version"] for pkg in packages}
        except Exception as e:
            pass
logger.warning("Failed to capture Python packages: %s", str(e)[:100])

        # Capture Node.js packages
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(["npm", "list", "--json", "--depth=0"], 
                capture_output=True, text=True, timeout=30, cwd=self.project_root)
                if result.stdout:
                    npm_data = json.loads(result.stdout)
                    dependencies = npm_data.get("dependencies", {})
                    snapshot["node_packages"] = {name: info.get("version", "unknown") for name, info in dependencies.items()}
            except Exception as e:
                pass
logger.warning("Failed to capture Node.js packages: %s", str(e)[:100])

        # Capture system info
        snapshot["system_info"] = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "working_directory": str(self.project_root)
        }
        
        # Create file hashes for dependency files
        for file_name in self.config["environment_markers"]:
            file_path = self.project_root / file_name
            if file_path.exists():
                import hashlib
                with open(file_path, 'rb') as f:
                    snapshot["file_hashes"][file_name] = hashlib.sha256(f.read()).hexdigest()
                    
        return snapshot
        
    def save_snapshot(self, snapshot: Dict[str, Any]) -> Path:
        """Save dependency snapshot to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = self.backup_dir / f"dependency_snapshot_{timestamp}.json"
        
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
            
logger.info("Dependency snapshot saved: %s", str(snapshot_file)[:100])
return snapshot_file

    def restore_dependencies_from_snapshot(self, snapshot_file: Path = None) -> bool:
        """Restore dependencies from snapshot"""
        if snapshot_file is None:
            # Find the most recent snapshot
            snapshots = list(self.backup_dir.glob("dependency_snapshot_*.json"))
            if not snapshots:
                self.logger.error("No dependency snapshots found")
                return False
            snapshot_file = max(snapshots, key=lambda x: x.stat().st_mtime)
            
        try:
            with open(snapshot_file, 'r') as f:
                snapshot = json.load(f)
                
logger.info("Restoring dependencies from %s", str(snapshot_file)[:100])

            # Restore Python packages
            success = True
            for package, version in snapshot["python_packages"].items():
                if package in self.config["critical_packages"]:
                    if not self._install_python_package_safe(f"{package}=={version}"):
                        success = False
                        
            # Restore Node.js packages
            if snapshot["node_packages"] and (self.project_root / "package.json").exists():
                if not self._install_node_packages_safe():
                    success = False
                    
            return success
            
        except Exception as e:
            pass
logger.error("Failed to restore from snapshot: %s", str(e)[:100])
return False

    def _install_python_package_safe(self, package_spec: str) -> bool:
        """Safely install Python package with fallbacks"""
        try:
            # Try with user install and short timeout
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--user", 
                "--timeout", "10", package_spec
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True
                
            # Try without version pinning
            package_name = package_spec.split('==')[0]
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--user", 
                "--timeout", "10", package_name
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            pass
logger.warning("Failed to install %s: %s", str(package_spec)[:100], str(e)[:100])
return False

    def _install_node_packages_safe(self) -> bool:
        """Safely install Node.js packages"""
        try:
            result = subprocess.run(["npm", "install"], 
            capture_output=True, text=True, timeout=60, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            pass
logger.warning("Failed to install Node.js packages: %s", str(e)[:100])
return False

    def create_startup_restoration_script(self):
        """Create script that runs on startup to restore dependencies"""
        script_content = f'''#!/bin/bash
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
'''

        script_path = self.project_root / "scripts" / "aurora_startup_restore.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        script_path.chmod(0o755)
        
logger.info("Startup restoration script created: %s", str(script_path)[:100])
return script_path

    def setup_automatic_persistence(self):
        """Set up automatic dependency persistence"""
        self.logger.info("Setting up automatic dependency persistence...")
        
        # Create startup script
        self.create_startup_restoration_script()
        
        # Create cron job for regular snapshots
        cron_content = f"""# Aurora CloudBank Dependency Persistence
# Take dependency snapshot daily at 3 AM
0 3 * * * cd "{self.project_root}" && python3 {__file__} --snapshot >/dev/null 2>&1

# Restore dependencies if needed at startup
@reboot cd "{self.project_root}" && bash scripts/aurora_startup_restore.sh >/dev/null 2>&1
"""

        cron_file = Path.home() / ".aurora_dependency_cron"
        with open(cron_file, 'w') as f:
            f.write(cron_content)
            
        try:
            # Install cron job
            subprocess.run(["crontab", str(cron_file)], check=True)
            self.logger.info("✅ Automatic persistence cron job installed")
        except subprocess.CalledProcessError as e:
            pass
logger.warning("Failed to install cron job: %s", str(e)[:100])

        # Create systemd user service for environments that support it
        self._create_systemd_service()
        
    def _create_systemd_service(self):
        """Create systemd user service for dependency persistence"""
        service_content = f"""[Unit]
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
            service_dir = Path.home() / ".config" / "systemd" / "user"
            service_dir.mkdir(parents=True, exist_ok=True)
            
            service_file = service_dir / "aurora-dependency-persistence.service"
            with open(service_file, 'w') as f:
                f.write(service_content)
                
            self.logger.info("✅ Systemd user service created")
        except Exception as e:
            pass
logger.warning("Failed to create systemd service: %s", str(e)[:100])

    def cleanup_old_backups(self):
        """Clean up old backup snapshots"""
        snapshots = list(self.backup_dir.glob("dependency_snapshot_*.json"))
        if len(snapshots) > self.config["max_backups"]:
            # Sort by modification time and remove oldest
            snapshots.sort(key=lambda x: x.stat().st_mtime)
            for old_snapshot in snapshots[:-self.config["max_backups"]]:
                old_snapshot.unlink()
logger.info("Removed old snapshot: %s", str(old_snapshot)[:100])

    def generate_persistence_report(self) -> str:
        """Generate comprehensive persistence status report"""
        snapshots = list(self.backup_dir.glob("dependency_snapshot_*.json"))
        latest_snapshot = max(snapshots, key=lambda x: x.stat().st_mtime) if snapshots else None
        
        report = f"""
# 🔧 Aurora CloudBank Dependency Persistence Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 📊 Persistence Status:
   Auto-restore: {'✅ Enabled' if self.config['auto_restore'] else '❌ Disabled'}
   Backup snapshots: {len(snapshots)}
   Latest snapshot: {latest_snapshot.name if latest_snapshot else 'None'}

# 🔄 Critical Packages Tracked:
"""

        for pkg in self.config["critical_packages"]:
            report += f"   • {pkg}\n"
            
        report += f"""
# 📦 Node.js Packages Tracked:
"""

        for pkg in self.config["nodejs_packages"]:
            report += f"   • {pkg}\n"
            
        if latest_snapshot:
            with open(latest_snapshot, 'r') as f:
                snapshot_data = json.load(f)
            report += f"""
# 📈 Latest Snapshot Info:
   Python packages: {len(snapshot_data.get('python_packages', {}))}
   Node.js packages: {len(snapshot_data.get('node_packages', {}))}
   Timestamp: {snapshot_data.get('timestamp', 'Unknown')}
"""

        return report

def main():
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
        print("📸 Creating dependency snapshot...")
        snapshot = manager.create_dependency_snapshot()
        snapshot_file = manager.save_snapshot(snapshot)
        print(f"✅ Snapshot saved: {snapshot_file}")
        
    elif args.restore_from_latest:
        print("🔄 Restoring dependencies from latest snapshot...")
        if manager.restore_dependencies_from_snapshot():
            print("✅ Dependencies restored successfully")
        else:
            print("❌ Failed to restore dependencies")
            sys.exit(1)
            
    elif args.setup_persistence:
        print("⚙️ Setting up automatic dependency persistence...")
        manager.setup_automatic_persistence()
        print("✅ Automatic persistence configured")
        
    elif args.cleanup_backups:
        print("🧹 Cleaning up old backup snapshots...")
        manager.cleanup_old_backups()
        print("✅ Backup cleanup complete")
        
    elif args.status:
        print(manager.generate_persistence_report())
        
    else:
        print(manager.generate_persistence_report())

if __name__ == "__main__":
    main()