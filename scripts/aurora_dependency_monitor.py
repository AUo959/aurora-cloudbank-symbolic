#!/usr/bin/env python3
"""
Aurora CloudBank Dependency Management Summary & Monitor

Final validation and monitoring script that provides a comprehensive overview
of the dependency management system status and ensures everything is working correctly.
"""

import os

from datetime import datetime

from typing import Any, Dict


class AuroraDependencyMonitor:
    pass
    """Comprehensive dependency monitoring and validation"""

    def __init__(self, project_root: Path = None):
    pass
        self.project_root = project_root or Path.cwd()
        self.aurora_dir = self.project_root / ".aurora"

    def validate_all_systems(self) -> Dict[str, Any]:
    pass
        """Validate all dependency management systems"""
        validation_report = {
            "timestamp": datetime.now().isoformat(),
            "core_dependencies": self._check_core_dependencies(),
            "automation_scripts": self._check_automation_scripts(),
            "persistence_systems": self._check_persistence_systems(),
            "integration_status": self._check_integration_status(),
            "overall_health": "unknown",
        }

        # Calculate overall health
        all_systems = [
            validation_report["core_dependencies"]["status"],
            validation_report["automation_scripts"]["status"],
            validation_report["persistence_systems"]["status"],
            validation_report["integration_status"]["status"],
        ]

        if all(status == "healthy" for status in all_systems):
    pass
            validation_report["overall_health"] = "excellent"
        elif all(status in ["healthy", "warning"] for status in all_systems):
    pass
            validation_report["overall_health"] = "good"
        elif any(status == "healthy" for status in all_systems):
    pass
            validation_report["overall_health"] = "partial"
        else:
    pass
            validation_report["overall_health"] = "critical"

        return validation_report

    def _check_core_dependencies(self) -> Dict[str, Any]:
    pass
        """Check core dependency status"""
        core_status = {
            "status": "unknown",
            "python_packages": 0,
            "node_packages": 0,
            "critical_missing": [],
            "details": [],
        }

        # Check Python packages,
        try:
    pass
            result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
    pass
                packages = [
                    line for line in result.stdout.split("\n") if line.strip() and not line.startswith("Package")
                ]
                core_status["python_packages"] = len(packages)
                core_status["details"].append("Python packages: {len(packages)}")

                # Check critical packages
                installed_names = {line.split()[0].lower() for line in packages if line.strip()}
                critical_packages = ["fastapi", "uvicorn", "pydantic", "pandas", "numpy", "requests"]
                missing = [pkg for pkg in critical_packages if pkg not in installed_names]
                core_status["critical_missing"] = missing

                if missing:
    pass
                    core_status["details"].append("Missing critical: {missing}")

        except Exception as _:
    pass
            core_status["details"].append("Python check failed: {e}")

        # Check Node.js packages
        if (self.project_root / "package.json").exists():
    pass
            try:
    pass
                result = subprocess.run(
                    ["npm", "list", "--depth=0"], capture_output=True, text=True, timeout=15, cwd=self.project_root
                )
                if result.returncode in [0, 1]:
    pass
                    lines = [line for line in result.stdout.split("\n") if "├──" in line or "└──" in line]
                    core_status["node_packages"] = len(lines)
                    core_status["details"].append("Node.js packages: {len(lines)}")
            except Exception as _:
    pass
                core_status["details"].append("Node.js check failed: {e}")

        # Determine status
        if len(core_status["critical_missing"]) == 0 and core_status["python_packages"] > 50:
    pass
            core_status["status"] = "healthy"
        elif len(core_status["critical_missing"]) <= 2:
    pass
            core_status["status"] = "warning"
        else:
    pass
            core_status["status"] = "critical"

        return core_status

    def _check_automation_scripts(self) -> Dict[str, Any]:
    pass
        """Check automation script status"""
        automation_status = {"status": "unknown", "scripts_found": 0, "scripts_working": 0, "details": []}

        # Check our new scripts
        scripts_to_check = [
            "aurora_dependency_hub.py",
            "aurora_dependency_integration.py",
            "aurora_dependency_persistence.py",
            "aurora_comprehensive_dependency_manager.py",
            "aurora_quick_health_check.py",
            "aurora_minimal_automation.py",
        ]

        for script_name in scripts_to_check:
    pass
            script_path = self.project_root / "scripts" / script_name
            if script_path.exists():
    pass
                automation_status["scripts_found"] += 1

                # Test if script runs without error,
                try:
    pass
                    result = subprocess.run(
                        [sys.executable, str(script_path), "--help"], capture_output=True, text=True, timeout=10
                    )
                    if result.returncode in [0, 2]:  # 0 = success, 2 = help shown
                        automation_status["scripts_working"] += 1,
                except BaseException:
    pass
                    pass

        automation_status["details"].append("Found {automation_status['scripts_found']} automation scripts")
        automation_status["details"].append("Working {automation_status['scripts_working']} scripts")

        # Determine status
        if automation_status["scripts_working"] >= 4:
    pass
            automation_status["status"] = "healthy"
        elif automation_status["scripts_working"] >= 2:
    pass
            automation_status["status"] = "warning"
        else:
    pass
            automation_status["status"] = "critical"

        return automation_status

    def _check_persistence_systems(self) -> Dict[str, Any]:
    pass
        """Check persistence system status"""
        persistence_status = {"status": "unknown", "snapshots_available": 0, "startup_scripts": 0, "details": []}

        # Check for snapshots
        if self.aurora_dir.exists():
    pass
            snapshot_files = list(self.aurora_dir.glob("**/dependency_snapshot_*.json"))
            persistence_status["snapshots_available"] = len(snapshot_files)
            persistence_status["details"].append("Dependency snapshots: {len(snapshot_files)}")

        # Check startup scripts
        startup_scripts = ["aurora_quick_dependency_check.sh", "aurora_startup_check.sh"]

        for script_name in startup_scripts:
    pass
            script_path = self.project_root / "scripts" / script_name
            if script_path.exists():
    pass
                persistence_status["startup_scripts"] += 1

        persistence_status["details"].append("Startup scripts: {persistence_status['startup_scripts']}")

        # Determine status
        if persistence_status["snapshots_available"] > 0 and persistence_status["startup_scripts"] > 0:
    pass
            persistence_status["status"] = "healthy"
        elif persistence_status["snapshots_available"] > 0 or persistence_status["startup_scripts"] > 0:
    pass
            persistence_status["status"] = "warning"
        else:
    pass
            persistence_status["status"] = "critical"

        return persistence_status

    def _check_integration_status(self) -> Dict[str, Any]:
    pass
        """Check integration with existing systems"""
        integration_status = {"status": "unknown", "existing_systems": 0, "config_files": 0, "details": []}

        # Check existing dependency scripts
        existing_scripts = [
            "scripts/gitwiz_dependency_updater.py",
            "scripts/scheduled_maintenance_enhanced.py",
            "tools/security/dependency_vulnerability_resolver.py",
        ]

        for script_path in existing_scripts:
    pass
            if (self.project_root / script_path).exists():
    pass
                integration_status["existing_systems"] += 1

        integration_status["details"].append("Existing systems: {integration_status['existing_systems']}")

        # Check configuration files
        config_files = [
            ".aurora/dependency_strategy.json",
            ".aurora/dependency_hub_config.json",
            ".aurora/integration_config.json",
        ]

        for config_path in config_files:
    pass
            if (self.project_root / config_path).exists():
    pass
                integration_status["config_files"] += 1

        integration_status["details"].append("Config files: {integration_status['config_files']}")

        # Determine status
        if integration_status["existing_systems"] >= 2 and integration_status["config_files"] >= 1:
    pass
            integration_status["status"] = "healthy"
        elif integration_status["existing_systems"] >= 1:
    pass
            integration_status["status"] = "warning"
        else:
    pass
            integration_status["status"] = "critical"

        return integration_status

    def generate_comprehensive_report(self) -> str:
    pass
        """Generate comprehensive monitoring report"""
        validation = self.validate_all_systems()

        status_emoji = {"excellent": "🟢", "good": "🟡", "partial": "🟠", "critical": "🔴"}

        report = """
🔧 Aurora CloudBank Dependency Management Status Report,
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{status_emoji.get(validation['overall_health'], '⚪')} Overall Health: {validation['overall_health'].upper()}

📦 Core Dependencies:
    pass
    Status: {validation['core_dependencies']['status']}
   Python packages: {validation['core_dependencies']['python_packages']}
   Node.js packages: {validation['core_dependencies']['node_packages']}
   Critical missing: {len(validation['core_dependencies']['critical_missing'])}

🤖 Automation Scripts:
    pass
    Status: {validation['automation_scripts']['status']}
   Scripts found: {validation['automation_scripts']['scripts_found']}
   Scripts working: {validation['automation_scripts']['scripts_working']}

💾 Persistence Systems:
    pass
    Status: {validation['persistence_systems']['status']}
   Snapshots available: {validation['persistence_systems']['snapshots_available']}
   Startup scripts: {validation['persistence_systems']['startup_scripts']}

🔗 Integration Status:
    pass
    Status: {validation['integration_status']['status']}
   Existing systems: {validation['integration_status']['existing_systems']}
   Config files: {validation['integration_status']['config_files']}

🎯 Summary:
    pass
    """

        if validation["overall_health"] == "excellent":
    pass
            report += """   ✅ All dependency management systems are fully operational
   ✅ Dependencies are installed, persistent, and automatically managed
   ✅ Complete integration with existing Aurora CloudBank systems
   ✅ Monitoring and automation are active"""
        elif validation["overall_health"] == "good":
    pass
            report += """   ✅ Dependency management systems are operational
   ✅ Core dependencies are managed and persistent
   ⚠️  Some optional systems may need attention
   ✅ Basic automation is active"""
        elif validation["overall_health"] == "partial":
    pass
            report += """   ⚠️  Dependency management is partially functional
   ⚠️  Some core systems may need manual intervention
   ⚠️  Check individual system status for issues
   💡 Run maintenance scripts to resolve issues"""
        else:
    pass
            report += """   ❌ Dependency management systems need attention
   ❌ Critical issues detected that require resolution
   🔧 Run 'python3 scripts/aurora_dependency_integration.py --full-setup'
   📞 Consider manual dependency installation"""

        return report

    def run_continuous_monitoring(self, interval_minutes: int = 60):
    pass
        """Run continuous monitoring loop"""
        print("🔄 Starting continuous dependency monitoring (every {interval_minutes} minutes)")

        import time

        while True:
    pass
            try:
    pass
                validation = self.validate_all_systems()

                if validation["overall_health"] in ["critical", "partial"]:
    pass
                    print("⚠️  {datetime.now().strftime('%H:%M:%S')} - Dependency issues detected!")
                    print("   Status: {validation['overall_health']}")

                    # Try automatic recovery
                    print("🔧 Attempting automatic recovery...")
                    try:
    pass
                        subprocess.run(
                            [sys.executable, str(self.project_root / "scripts" / "aurora_minimal_automation.py")],
                            timeout=120,
                        )
                    except BaseException:
    pass
                        print("❌ Automatic recovery failed")

                else:
    pass
                    print("✅ {datetime.now().strftime('%H:%M:%S')} - All systems healthy")

                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
    pass
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as _:
    pass
                print("❌ Monitoring error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    pass
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Aurora CloudBank Dependency Monitor")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
    parser.add_argument("--validate", action="store_true", help="Run validation and exit with status")
    parser.add_argument("--monitor", type=int, metavar="MINUTES", help="Run continuous monitoring")

    args = parser.parse_args()

    monitor = AuroraDependencyMonitor()

    if args.report:
    pass
        print(monitor.generate_comprehensive_report())

    elif args.validate:
    pass
        validation = monitor.validate_all_systems()
        print("Validation Status: {validation['overall_health']}")

        if validation["overall_health"] in ["critical", "partial"]:
    pass
            sys.exit(1)
        else:
    pass
            sys.exit(0)

    elif args.monitor:
    pass
        monitor.run_continuous_monitoring(args.monitor)

    else:
    pass
        print(monitor.generate_comprehensive_report())

if __name__ == "__main__":
    pass
    main()
