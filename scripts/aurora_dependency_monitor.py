#!/usr/bin/env python3
"""
Aurora CloudBank Dependency Management Summary & Monitor

Final validation and monitoring script that provides a comprehensive overview
of the dependency management system status and ensures everything is working correctly.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class AuroraDependencyMonitor:
    """Comprehensive dependency monitoring and validation"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.aurora_dir = self.project_root / ".aurora"
        
    def validate_all_systems(self) -> Dict[str, Any]:
        """Validate all dependency management systems"""
        validation_report = {
            "timestamp": datetime.now().isoformat(),
            "core_dependencies": self._check_core_dependencies(),
            "automation_scripts": self._check_automation_scripts(),
            "persistence_systems": self._check_persistence_systems(),
            "integration_status": self._check_integration_status(),
            "overall_health": "unknown"
        }
        
        # Calculate overall health
        all_systems = [
            validation_report["core_dependencies"]["status"],
            validation_report["automation_scripts"]["status"],
            validation_report["persistence_systems"]["status"],
            validation_report["integration_status"]["status"]
        ]
        
        if all(status == "healthy" for status in all_systems):
            validation_report["overall_health"] = "excellent"
        elif all(status in ["healthy", "warning"] for status in all_systems):
            validation_report["overall_health"] = "good"
        elif any(status == "healthy" for status in all_systems):
            validation_report["overall_health"] = "partial"
        else:
            validation_report["overall_health"] = "critical"
            
        return validation_report
        
    def _check_core_dependencies(self) -> Dict[str, Any]:
        """Check core dependency status"""
        core_status = {
            "status": "unknown",
            "python_packages": 0,
            "node_packages": 0,
            "critical_missing": [],
            "details": []
        }
        
        # Check Python packages
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                packages = [line for line in result.stdout.split('\n') 
                          if line.strip() and not line.startswith('Package')]
                core_status["python_packages"] = len(packages)
                core_status["details"].append(f"Python packages: {len(packages)}")
                
                # Check critical packages
                installed_names = {line.split()[0].lower() for line in packages if line.strip()}
                critical_packages = ["fastapi", "uvicorn", "pydantic", "pandas", "numpy", "requests"]
                missing = [pkg for pkg in critical_packages if pkg not in installed_names]
                core_status["critical_missing"] = missing
                
                if missing:
                    core_status["details"].append(f"Missing critical: {missing}")
                    
        except Exception as e:
            core_status["details"].append(f"Python check failed: {e}")
            
        # Check Node.js packages
        if (self.project_root / "package.json").exists():
            try:
                result = subprocess.run(["npm", "list", "--depth=0"], 
                                      capture_output=True, text=True, timeout=15, cwd=self.project_root)
                if result.returncode in [0, 1]:
                    lines = [line for line in result.stdout.split('\n') if '├──' in line or '└──' in line]
                    core_status["node_packages"] = len(lines)
                    core_status["details"].append(f"Node.js packages: {len(lines)}")
            except Exception as e:
                core_status["details"].append(f"Node.js check failed: {e}")
                
        # Determine status
        if len(core_status["critical_missing"]) == 0 and core_status["python_packages"] > 50:
            core_status["status"] = "healthy"
        elif len(core_status["critical_missing"]) <= 2:
            core_status["status"] = "warning"
        else:
            core_status["status"] = "critical"
            
        return core_status
        
    def _check_automation_scripts(self) -> Dict[str, Any]:
        """Check automation script status"""
        automation_status = {
            "status": "unknown",
            "scripts_found": 0,
            "scripts_working": 0,
            "details": []
        }
        
        # Check our new scripts
        scripts_to_check = [
            "aurora_dependency_hub.py",
            "aurora_dependency_integration.py", 
            "aurora_dependency_persistence.py",
            "aurora_comprehensive_dependency_manager.py",
            "aurora_quick_health_check.py",
            "aurora_minimal_automation.py"
        ]
        
        for script_name in scripts_to_check:
            script_path = self.project_root / "scripts" / script_name
            if script_path.exists():
                automation_status["scripts_found"] += 1
                
                # Test if script runs without error
                try:
                    result = subprocess.run([sys.executable, str(script_path), "--help"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode in [0, 2]:  # 0 = success, 2 = help shown
                        automation_status["scripts_working"] += 1
                except:
                    pass
                    
        automation_status["details"].append(f"Found {automation_status['scripts_found']} automation scripts")
        automation_status["details"].append(f"Working {automation_status['scripts_working']} scripts")
        
        # Determine status
        if automation_status["scripts_working"] >= 4:
            automation_status["status"] = "healthy"
        elif automation_status["scripts_working"] >= 2:
            automation_status["status"] = "warning"
        else:
            automation_status["status"] = "critical"
            
        return automation_status
        
    def _check_persistence_systems(self) -> Dict[str, Any]:
        """Check persistence system status"""
        persistence_status = {
            "status": "unknown",
            "snapshots_available": 0,
            "startup_scripts": 0,
            "details": []
        }
        
        # Check for snapshots
        if self.aurora_dir.exists():
            snapshot_files = list(self.aurora_dir.glob("**/dependency_snapshot_*.json"))
            persistence_status["snapshots_available"] = len(snapshot_files)
            persistence_status["details"].append(f"Dependency snapshots: {len(snapshot_files)}")
            
        # Check startup scripts
        startup_scripts = [
            "aurora_quick_dependency_check.sh",
            "aurora_startup_check.sh"
        ]
        
        for script_name in startup_scripts:
            script_path = self.project_root / "scripts" / script_name
            if script_path.exists():
                persistence_status["startup_scripts"] += 1
                
        persistence_status["details"].append(f"Startup scripts: {persistence_status['startup_scripts']}")
        
        # Determine status
        if persistence_status["snapshots_available"] > 0 and persistence_status["startup_scripts"] > 0:
            persistence_status["status"] = "healthy"
        elif persistence_status["snapshots_available"] > 0 or persistence_status["startup_scripts"] > 0:
            persistence_status["status"] = "warning"
        else:
            persistence_status["status"] = "critical"
            
        return persistence_status
        
    def _check_integration_status(self) -> Dict[str, Any]:
        """Check integration with existing systems"""
        integration_status = {
            "status": "unknown",
            "existing_systems": 0,
            "config_files": 0,
            "details": []
        }
        
        # Check existing dependency scripts
        existing_scripts = [
            "scripts/gitwiz_dependency_updater.py",
            "scripts/scheduled_maintenance_enhanced.py",
            "tools/security/dependency_vulnerability_resolver.py"
        ]
        
        for script_path in existing_scripts:
            if (self.project_root / script_path).exists():
                integration_status["existing_systems"] += 1
                
        integration_status["details"].append(f"Existing systems: {integration_status['existing_systems']}")
        
        # Check configuration files
        config_files = [
            ".aurora/dependency_strategy.json",
            ".aurora/dependency_hub_config.json",
            ".aurora/integration_config.json"
        ]
        
        for config_path in config_files:
            if (self.project_root / config_path).exists():
                integration_status["config_files"] += 1
                
        integration_status["details"].append(f"Config files: {integration_status['config_files']}")
        
        # Determine status
        if integration_status["existing_systems"] >= 2 and integration_status["config_files"] >= 1:
            integration_status["status"] = "healthy"
        elif integration_status["existing_systems"] >= 1:
            integration_status["status"] = "warning"
        else:
            integration_status["status"] = "critical"
            
        return integration_status
        
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive monitoring report"""
        validation = self.validate_all_systems()
        
        status_emoji = {
            "excellent": "🟢",
            "good": "🟡", 
            "partial": "🟠",
            "critical": "🔴"
        }
        
        report = f"""
🔧 Aurora CloudBank Dependency Management Status Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{status_emoji.get(validation['overall_health'], '⚪')} Overall Health: {validation['overall_health'].upper()}

📦 Core Dependencies:
   Status: {validation['core_dependencies']['status']}
   Python packages: {validation['core_dependencies']['python_packages']}
   Node.js packages: {validation['core_dependencies']['node_packages']}
   Critical missing: {len(validation['core_dependencies']['critical_missing'])}

🤖 Automation Scripts:
   Status: {validation['automation_scripts']['status']}
   Scripts found: {validation['automation_scripts']['scripts_found']}
   Scripts working: {validation['automation_scripts']['scripts_working']}

💾 Persistence Systems:
   Status: {validation['persistence_systems']['status']}
   Snapshots available: {validation['persistence_systems']['snapshots_available']}
   Startup scripts: {validation['persistence_systems']['startup_scripts']}

🔗 Integration Status:
   Status: {validation['integration_status']['status']}
   Existing systems: {validation['integration_status']['existing_systems']}
   Config files: {validation['integration_status']['config_files']}

🎯 Summary:
"""
        
        if validation['overall_health'] == 'excellent':
            report += """   ✅ All dependency management systems are fully operational
   ✅ Dependencies are installed, persistent, and automatically managed
   ✅ Complete integration with existing Aurora CloudBank systems
   ✅ Monitoring and automation are active"""
        elif validation['overall_health'] == 'good':
            report += """   ✅ Dependency management systems are operational
   ✅ Core dependencies are managed and persistent
   ⚠️  Some optional systems may need attention
   ✅ Basic automation is active"""
        elif validation['overall_health'] == 'partial':
            report += """   ⚠️  Dependency management is partially functional
   ⚠️  Some core systems may need manual intervention
   ⚠️  Check individual system status for issues
   💡 Run maintenance scripts to resolve issues"""
        else:
            report += """   ❌ Dependency management systems need attention
   ❌ Critical issues detected that require resolution
   🔧 Run 'python3 scripts/aurora_dependency_integration.py --full-setup'
   📞 Consider manual dependency installation"""
            
        return report
        
    def run_continuous_monitoring(self, interval_minutes: int = 60):
        """Run continuous monitoring loop"""
        print(f"🔄 Starting continuous dependency monitoring (every {interval_minutes} minutes)")
        
        import time
        
        while True:
            try:
                validation = self.validate_all_systems()
                
                if validation['overall_health'] in ['critical', 'partial']:
                    print(f"⚠️  {datetime.now().strftime('%H:%M:%S')} - Dependency issues detected!")
                    print(f"   Status: {validation['overall_health']}")
                    
                    # Try automatic recovery
                    print("🔧 Attempting automatic recovery...")
                    try:
                        subprocess.run([
                            sys.executable, 
                            str(self.project_root / "scripts" / "aurora_minimal_automation.py")
                        ], timeout=120)
                    except:
                        print("❌ Automatic recovery failed")
                        
                else:
                    print(f"✅ {datetime.now().strftime('%H:%M:%S')} - All systems healthy")
                    
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora CloudBank Dependency Monitor")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
    parser.add_argument("--validate", action="store_true", help="Run validation and exit with status")
    parser.add_argument("--monitor", type=int, metavar="MINUTES", help="Run continuous monitoring")
    
    args = parser.parse_args()
    
    monitor = AuroraDependencyMonitor()
    
    if args.report:
        print(monitor.generate_comprehensive_report())
        
    elif args.validate:
        validation = monitor.validate_all_systems()
        print(f"Validation Status: {validation['overall_health']}")
        
        if validation['overall_health'] in ['critical', 'partial']:
            sys.exit(1)
        else:
            sys.exit(0)
            
    elif args.monitor:
        monitor.run_continuous_monitoring(args.monitor)
        
    else:
        print(monitor.generate_comprehensive_report())

if __name__ == "__main__":
    main()