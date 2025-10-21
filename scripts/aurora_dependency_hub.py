#!/usr/bin/env python3
"""
Aurora CloudBank Comprehensive Dependency Setup & Management Hub

This is the master script that ensures all necessary dependencies are installed,
remain installed, and stay updated automatically. It provides a single entry point
for all dependency management tasks.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class AuroraDependencyHub:
    """Master dependency management hub for Aurora CloudBank"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.aurora_dir = self.project_root / ".aurora"
        self.config_file = self.aurora_dir / "dependency_hub_config.json"
        
        self._setup_logging()
        self._ensure_directories()
        self.config = self._load_config()
        
        # Track installation state
        self.installation_state = {
            "python_packages": {"installed": [], "failed": []},
            "node_packages": {"installed": [], "failed": []},
            "system_packages": {"installed": [], "failed": []}
        }
        
    def _setup_logging(self):
        """Set up comprehensive logging"""
        self.aurora_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.aurora_dir / "dependency_hub.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('AuroraDependencyHub')
        
    def _ensure_directories(self):
        """Create necessary directories"""
        dirs = [
            self.aurora_dir,
            self.aurora_dir / "persistence",
            self.aurora_dir / "persistence" / "backups",
            self.aurora_dir / "logs"
        ]
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _load_config(self) -> Dict[str, Any]:
        """Load master configuration"""
        default_config = {
            "critical_python_packages": [
                "fastapi>=0.100.0",
                "uvicorn>=0.20.0", 
                "pydantic>=2.0.0",
                "pandas>=2.0.0",
                "numpy>=1.24.0",
                "schedule>=1.2.0",  # Add schedule for the scheduler
                "requests>=2.25.0"
            ],
            "development_python_packages": [
                "black>=23.0.0",
                "flake8>=6.0.0", 
                "pytest>=8.0.0",
                "pytest-asyncio>=0.23.0"
            ],
            "optional_python_packages": [
                "qiskit>=1.0.0",
                "qiskit-aer>=0.14.0",
                "plotly>=5.0.0",
                "httpx>=0.24.0"
            ],
            "node_packages": [
                "express@^4.18.0",
                "socket.io@^4.7.0", 
                "helmet@^7.1.0",
                "express-rate-limit@^7.1.0"
            ],
            "installation_strategy": {
                "max_retries": 3,
                "timeout_per_package": 60,
                "fallback_indexes": True,
                "user_install": True,
                "force_upgrade": False
            },
            "automation": {
                "auto_persistence": True,
                "auto_scheduling": True,
                "health_monitoring": True,
                "auto_recovery": True
            }
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
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def install_python_package_robust(self, package_spec: str, is_critical: bool = True) -> bool:
        """Install Python package with robust error handling"""
        package_name = package_spec.split('>=')[0].split('==')[0].split('[')[0]
        
logger.info("Installing Python package: %s", str(package_spec)[:100])

        max_retries = self.config["installation_strategy"]["max_retries"]
        timeout = self.config["installation_strategy"]["timeout_per_package"]
        
        # Primary index
        indexes = ["https://pypi.org/simple/"]
        
        # Add fallback indexes if enabled
        if self.config["installation_strategy"]["fallback_indexes"]:
            indexes.extend([
                "https://pypi.python.org/simple/",
                "https://pypi.doubanio.com/simple/"
            ])
            
        for attempt in range(max_retries):
            for index in indexes:
                try:
                    cmd = [sys.executable, "-m", "pip", "install"]
                    
                    if self.config["installation_strategy"]["user_install"]:
                        cmd.append("--user")
                        
                    cmd.extend([
                        "--timeout", str(timeout),
                        "--index-url", index,
                        "--no-warn-script-location"
                    ])
                    
                    if self.config["installation_strategy"]["force_upgrade"]:
                        cmd.append("--upgrade")
                        
                    cmd.append(package_spec)
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout + 10
                    )
                    
                    if result.returncode == 0:
                        self.installation_state["python_packages"]["installed"].append(package_spec)
logger.info("✅ Successfully installed: %s", str(package_spec)[:100])
return True

                except subprocess.TimeoutExpired:
                    pass
logger.warning("Timeout installing %s with %s (attempt %s)", str(package_spec)[:100], str(index)[:100], str(attempt + 1)[:100])
continue
except Exception as e:
                    pass
logger.warning("Error installing %s: %s", str(package_spec)[:100], str(e)[:100])
continue

            # Wait before retry
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        self.installation_state["python_packages"]["failed"].append(package_spec)
        
        if is_critical:
logger.error("❌ CRITICAL: Failed to install %s", str(package_spec)[:100])
else:
logger.warning("⚠️  Failed to install optional package: %s", str(package_spec)[:100])

        return False
        
    def install_node_package_robust(self, package_spec: str) -> bool:
        """Install Node.js package with robust error handling"""
logger.info("Installing Node.js package: %s", str(package_spec)[:100])

        registries = [
            "https://registry.npmjs.org/",
            "https://registry.npm.taobao.org/"
        ]
        
        for registry in registries:
            try:
                cmd = ["npm", "install", "--registry", registry, package_spec]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    self.installation_state["node_packages"]["installed"].append(package_spec)
logger.info("✅ Successfully installed Node.js package: %s", str(package_spec)[:100])
return True

            except Exception as e:
                pass
logger.warning("Failed to install %s with %s: %s", str(package_spec)[:100], str(registry)[:100], str(e)[:100])
continue

        self.installation_state["node_packages"]["failed"].append(package_spec)
logger.warning("⚠️  Failed to install Node.js package: %s", str(package_spec)[:100])
return False

    def install_all_dependencies(self) -> Dict[str, Any]:
        """Install all dependencies systematically"""
        self.logger.info("🚀 Starting comprehensive dependency installation...")
        
        results = {
            "start_time": datetime.now().isoformat(),
            "critical_python": {"total": 0, "installed": 0, "failed": 0},
            "development_python": {"total": 0, "installed": 0, "failed": 0}, 
            "optional_python": {"total": 0, "installed": 0, "failed": 0},
            "node_packages": {"total": 0, "installed": 0, "failed": 0},
            "overall_success": False
        }
        
        # Install critical Python packages
        critical_packages = self.config["critical_python_packages"]
        results["critical_python"]["total"] = len(critical_packages)
        
logger.info("📦 Installing %s critical Python packages...", str(len(critical_packages))[:100])
for package in critical_packages:
            if self.install_python_package_robust(package, is_critical=True):
                results["critical_python"]["installed"] += 1
            else:
                results["critical_python"]["failed"] += 1
                
        # Install development Python packages
        dev_packages = self.config["development_python_packages"]
        results["development_python"]["total"] = len(dev_packages)
        
logger.info("🛠️  Installing %s development Python packages...", str(len(dev_packages))[:100])
for package in dev_packages:
            if self.install_python_package_robust(package, is_critical=False):
                results["development_python"]["installed"] += 1
            else:
                results["development_python"]["failed"] += 1
                
        # Install optional Python packages (continue on failure)
        optional_packages = self.config["optional_python_packages"]
        results["optional_python"]["total"] = len(optional_packages)
        
logger.info("🔬 Installing %s optional Python packages...", str(len(optional_packages))[:100])
for package in optional_packages:
            if self.install_python_package_robust(package, is_critical=False):
                results["optional_python"]["installed"] += 1
            else:
                results["optional_python"]["failed"] += 1
                
        # Install Node.js packages
        node_packages = self.config["node_packages"]
        results["node_packages"]["total"] = len(node_packages)
        
        if node_packages and (self.project_root / "package.json").exists():
logger.info("📦 Installing %s Node.js packages...", str(len(node_packages))[:100])
for package in node_packages:
                if self.install_node_package_robust(package):
                    results["node_packages"]["installed"] += 1
                else:
                    results["node_packages"]["failed"] += 1
        else:
            self.logger.info("📦 Skipping Node.js packages (no package.json found)")
            
        # Calculate overall success
        critical_success_rate = results["critical_python"]["installed"] / max(results["critical_python"]["total"], 1)
        results["overall_success"] = critical_success_rate >= 0.8
        
        results["end_time"] = datetime.now().isoformat()
        
logger.info("🏁 Installation complete. Success rate: %s", str(critical_success_rate:.1%)[:100])
return results

    def setup_automated_systems(self):
        """Set up all automated dependency management systems"""
        self.logger.info("⚙️ Setting up automated dependency management systems...")
        
        success_count = 0
        total_systems = 4
        
        # 1. Set up persistence system
        try:
            persistence_script = self.project_root / "scripts" / "aurora_dependency_persistence.py"
            if persistence_script.exists():
                result = subprocess.run([
                    sys.executable, str(persistence_script), "--setup-persistence"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.logger.info("✅ Persistence system configured")
                    success_count += 1
                else:
                    self.logger.warning("⚠️  Persistence system setup failed")
            else:
                self.logger.warning("⚠️  Persistence script not found")
        except Exception as e:
            pass
logger.warning("Persistence setup failed: %s", str(e)[:100])

        # 2. Set up automated scheduler
        try:
            scheduler_script = self.project_root / "scripts" / "aurora_automated_update_scheduler.py"
            if scheduler_script.exists():
                result = subprocess.run([
                    sys.executable, str(scheduler_script), "--setup"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.logger.info("✅ Automated scheduler configured")
                    success_count += 1
                else:
                    self.logger.warning("⚠️  Scheduler setup failed")
            else:
                self.logger.warning("⚠️  Scheduler script not found")
        except Exception as e:
            pass
logger.warning("Scheduler setup failed: %s", str(e)[:100])

        # 3. Create startup script
        try:
            self._create_startup_script()
            self.logger.info("✅ Startup script created")
            success_count += 1
        except Exception as e:
            pass
logger.warning("Startup script creation failed: %s", str(e)[:100])

        # 4. Set up health monitoring
        try:
            self._setup_health_monitoring()
            self.logger.info("✅ Health monitoring configured")
            success_count += 1
        except Exception as e:
            pass
logger.warning("Health monitoring setup failed: %s", str(e)[:100])

logger.info("🎯 Automated systems setup: %s/%s successful", str(success_count)[:100], str(total_systems)[:100])
return success_count == total_systems

    def _create_startup_script(self):
        """Create comprehensive startup script"""
        script_content = f'''#!/bin/bash
# Aurora CloudBank Comprehensive Dependency Management Startup Script
# Ensures all dependencies are healthy on system startup

set -e

PROJECT_ROOT="{self.project_root}"
cd "$PROJECT_ROOT"

echo "🔧 Aurora CloudBank: Starting dependency health check..."

# Function to log with timestamp
log_message() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}}

# Check if dependency hub exists
if [ ! -f "scripts/aurora_dependency_hub.py" ]; then
    log_message "❌ Dependency hub not found"
    exit 1
fi

# Run health check
log_message "🏥 Running dependency health check..."
if python3 scripts/aurora_dependency_hub.py --health-check; then
    log_message "✅ Dependencies are healthy"
else
    log_message "⚠️  Dependencies need attention, attempting recovery..."
    
    # Try automatic recovery
    if python3 scripts/aurora_dependency_hub.py --install; then
        log_message "✅ Dependency recovery successful"
    else
        log_message "❌ Dependency recovery failed, manual intervention required"
        exit 1
    fi
fi

log_message "🚀 Aurora CloudBank dependency startup check complete"
'''

        script_path = self.project_root / "scripts" / "aurora_startup_check.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        script_path.chmod(0o755)
        
    def _setup_health_monitoring(self):
        """Set up health monitoring cron job"""
        cron_content = f'''# Aurora CloudBank Dependency Health Monitoring
# Check dependency health every 6 hours
0 */6 * * * cd "{self.project_root}" && python3 scripts/aurora_dependency_hub.py --health-check >/dev/null 2>&1

# Run startup check on reboot
@reboot cd "{self.project_root}" && bash scripts/aurora_startup_check.sh >/dev/null 2>&1
'''

        cron_file = Path.home() / ".aurora_dependency_monitoring"
        with open(cron_file, 'w') as f:
            f.write(cron_content)
            
        try:
            subprocess.run(["crontab", str(cron_file)], check=True, timeout=30)
        except subprocess.CalledProcessError:
            # Cron might not be available, that's ok
            pass
            
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive dependency health check"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "python_status": "unknown",
            "node_status": "unknown", 
            "critical_packages": {"missing": [], "outdated": []},
            "overall_health": "unknown",
            "recommendations": []
        }
        
        # Check Python packages
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
            capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                installed_packages = {line.split()[0].lower() for line in result.stdout.split('\n') 
                if line.strip() and not line.startswith('Package')}
                
                missing_critical = []
                for package_spec in self.config["critical_python_packages"]:
                    package_name = package_spec.split('>=')[0].split('==')[0].lower()
                    if package_name not in installed_packages:
                        missing_critical.append(package_name)
                        
                health_report["critical_packages"]["missing"] = missing_critical
                health_report["python_status"] = "healthy" if not missing_critical else "degraded"
            else:
                health_report["python_status"] = "error"
        except Exception as e:
            health_report["python_status"] = "error"
            
        # Check Node.js packages
        if (self.project_root / "package.json").exists():
            try:
                result = subprocess.run(["npm", "list", "--depth=0"], 
                capture_output=True, text=True, timeout=30, cwd=self.project_root)
                health_report["node_status"] = "healthy" if result.returncode in [0, 1] else "degraded"
            except Exception:
                health_report["node_status"] = "error"
        else:
            health_report["node_status"] = "not_applicable"
            
        # Calculate overall health
        if health_report["python_status"] == "error":
            health_report["overall_health"] = "critical"
        elif health_report["critical_packages"]["missing"]:
            health_report["overall_health"] = "degraded"
        else:
            health_report["overall_health"] = "healthy"
            
        # Generate recommendations
        if health_report["critical_packages"]["missing"]:
            health_report["recommendations"].append("Install missing critical packages")
        if health_report["overall_health"] != "healthy":
            health_report["recommendations"].append("Run 'python3 scripts/aurora_dependency_hub.py --install' to fix issues")
            
        return health_report
        
    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        health = self.health_check()
        
        report = f"""
# 🔧 Aurora CloudBank Dependency Management Hub
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 📊 Overall Health: {health['overall_health'].upper()}

# 🐍 Python Dependencies:
   Status: {health['python_status']}
   Critical packages: {len(self.config['critical_python_packages'])}
   Missing critical: {len(health['critical_packages']['missing'])}

# 📦 Node.js Dependencies:
   Status: {health['node_status']}
   Configured packages: {len(self.config['node_packages'])}

# 🤖 Automation Status:
   Auto persistence: {'✅ Enabled' if self.config['automation']['auto_persistence'] else '❌ Disabled'}
   Auto scheduling: {'✅ Enabled' if self.config['automation']['auto_scheduling'] else '❌ Disabled'}
   Health monitoring: {'✅ Enabled' if self.config['automation']['health_monitoring'] else '❌ Disabled'}

# 💡 Recommendations:
"""

        for rec in health['recommendations']:
            report += f"   • {rec}\n"
            
        if health['overall_health'] == 'healthy':
            report += "   ✅ All systems operational\n"
            
        return report

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora CloudBank Dependency Management Hub")
    parser.add_argument("--install", action="store_true", help="Install all dependencies")
    parser.add_argument("--setup-automation", action="store_true", help="Set up automated systems")
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument("--status", action="store_true", help="Show status report")
    parser.add_argument("--full-setup", action="store_true", help="Complete setup (install + automation)")
    
    args = parser.parse_args()
    
    hub = AuroraDependencyHub()
    
    if args.install:
        print("🔧 Installing all dependencies...")
        results = hub.install_all_dependencies()
        if results['overall_success']:
            print("✅ Dependency installation completed successfully!")
        else:
            print("⚠️  Dependency installation completed with some issues")
            
    elif args.setup_automation:
        print("⚙️ Setting up automated systems...")
        if hub.setup_automated_systems():
            print("✅ Automated systems configured successfully!")
        else:
            print("⚠️  Some automated systems failed to configure")
            
    elif args.health_check:
        health = hub.health_check()
        print(f"Health Status: {health['overall_health'].upper(}"))
        if health['overall_health'] != 'healthy':
            sys.exit(1)
            
    elif args.status:
        print(hub.generate_status_report())
        
    elif args.full_setup:
        print("🚀 Running complete Aurora CloudBank dependency setup...")
        
        # Install dependencies
        print("\n📦 Phase 1: Installing dependencies...")
        install_results = hub.install_all_dependencies()
        
        # Set up automation
        print("\n⚙️ Phase 2: Setting up automation...")
        automation_success = hub.setup_automated_systems()
        
        # Final report
        print("\n📊 Setup Summary:")
        print(f"   Dependencies: {'✅ Success' if install_results['overall_success'] else '⚠️  Partial'}")
        print(f"   Automation: {'✅ Success' if automation_success else '⚠️  Partial'}")
        
        if install_results['overall_success'] and automation_success:
            print("\n🎉 Complete setup successful! Aurora CloudBank dependencies are fully managed.")
        else:
            print("\n⚠️  Setup completed with some issues. Check logs for details.")
            
    else:
        print(hub.generate_status_report())

if __name__ == "__main__":
    main()