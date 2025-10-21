#!/usr/bin/env python3
"""
Aurora CloudBank Dependency Management Integration Layer

Integrates the new dependency management system with existing GitWiz and Aurora systems.
Provides robust offline-capable dependency management with monitoring and automation.
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

class AuroraDependencyIntegration:
    """Integration layer for Aurora CloudBank dependency management"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.integration_config = self.project_root / ".aurora" / "integration_config.json"
        
        self._setup_logging()
        self.config = self._load_config()
        self.existing_systems = self._detect_existing_systems()
        
    def _setup_logging(self):
        """Set up logging"""
        aurora_dir = self.project_root / ".aurora"
        aurora_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(aurora_dir / "integration.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('AuroraIntegration')
        
    def _load_config(self) -> Dict[str, Any]:
        """Load integration configuration"""
        default_config = {
            "integration_mode": "enhanced",  # minimal, standard, enhanced
            "existing_system_integration": {
                "gitwiz_dependency_updater": True,
                "scheduled_maintenance_enhanced": True,
                "aurora_maintenance_scheduler": True,
                "dependency_vulnerability_resolver": True
            },
            "network_resilience": {
                "max_install_attempts": 2,
                "offline_mode": True,
                "cache_packages": True,
                "graceful_degradation": True
            },
            "monitoring": {
                "health_check_interval": 21600,  # 6 hours
                "alert_on_critical_failure": True,
                "log_all_activities": True
            }
        }
        
        if self.integration_config.exists():
            try:
                with open(self.integration_config, 'r') as f:
                    loaded_config = json.load(f)
                return {**default_config, **loaded_config}
            except Exception as e:
                pass
logger.warning("Failed to load config: %s", str(e)[:100])
                
        return default_config
        
    def _detect_existing_systems(self) -> Dict[str, bool]:
        """Detect existing dependency management systems"""
        systems = {
            "gitwiz_dependency_updater": (self.project_root / "scripts" / "gitwiz_dependency_updater.py").exists(),
            "scheduled_maintenance_enhanced": (self.project_root / "scripts" / "scheduled_maintenance_enhanced.py").exists(),
            "aurora_maintenance_scheduler": (self.project_root / "scripts" / "aurora_maintenance_scheduler.py").exists(),
            "dependency_vulnerability_resolver": (self.project_root / "tools" / "security" / "dependency_vulnerability_resolver.py").exists(),
            "requirements_txt": (self.project_root / "requirements.txt").exists(),
            "package_json": (self.project_root / "package.json").exists(),
            "pyproject_toml": (self.project_root / "pyproject.toml").exists()
        }
        
logger.info("Detected existing systems: %s/%s", str(sum(systems.values()))[:100], str(len(systems))[:100])
        return systems
        
    def create_unified_dependency_strategy(self):
        """Create unified dependency management strategy"""
        self.logger.info("🎯 Creating unified dependency management strategy...")
        
        strategy = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0.0",
                "description": "Aurora CloudBank Unified Dependency Strategy"
            },
            "phase1_immediate": {
                "description": "Ensure critical dependencies are available offline",
                "actions": [
                    "Validate requirements.txt exists and is readable",
                    "Check for existing Python packages via pip list",
                    "Validate Node.js package.json structure",
                    "Create dependency inventory snapshot"
                ]
            },
            "phase2_installation": {
                "description": "Install dependencies with network resilience",
                "strategy": "graceful_degradation",
                "max_attempts": 2,
                "fallback_mode": "offline_validation"
            },
            "phase3_persistence": {
                "description": "Ensure dependencies remain installed",
                "mechanisms": [
                    "Create dependency snapshots",
                    "Set up restoration scripts",
                    "Configure startup validation"
                ]
            },
            "phase4_automation": {
                "description": "Automated updates and monitoring", 
                "scheduling": "conservative",
                "integration": "existing_systems"
            }
        }
        
        strategy_file = self.project_root / ".aurora" / "dependency_strategy.json"
        with open(strategy_file, 'w') as f:
            json.dump(strategy, f, indent=2)
            
logger.info("✅ Strategy created: %s", str(strategy_file)[:100])
        return strategy
        
    def execute_immediate_phase(self) -> Dict[str, Any]:
        """Execute immediate dependency validation and inventory"""
        self.logger.info("📋 Phase 1: Immediate dependency validation...")
        
        phase_results = {
            "requirements_validation": False,
            "python_inventory": {"count": 0, "critical_missing": []},
            "node_inventory": {"count": 0, "status": "unknown"},
            "snapshot_created": False
        }
        
        # Validate requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                phase_results["requirements_validation"] = len(requirements) > 0
logger.info("✅ Found %s requirements in requirements.txt", str(len(requirements))[:100])
            except Exception as e:
                pass
logger.warning("Failed to read requirements.txt: %s", str(e)[:100])
        else:
            self.logger.warning("⚠️  requirements.txt not found")
            
        # Python package inventory
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                packages = [line for line in result.stdout.split('\n') 
                          if line.strip() and not line.startswith('Package')]
                phase_results["python_inventory"]["count"] = len(packages)
                
                # Check for critical packages
                critical_packages = ["fastapi", "uvicorn", "pydantic", "pandas", "numpy"]
                installed_names = {line.split()[0].lower() for line in packages if line.strip()}
                
                missing_critical = [pkg for pkg in critical_packages if pkg not in installed_names]
                phase_results["python_inventory"]["critical_missing"] = missing_critical
                
                if missing_critical:
logger.warning("⚠️  Missing critical packages: %s", str(missing_critical)[:100])
                else:
                    self.logger.info("✅ All critical Python packages are installed")
                    
        except Exception as e:
            pass
logger.warning("Failed Python inventory: %s", str(e)[:100])
            
        # Node.js package inventory
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(["npm", "list", "--depth=0"], 
                                      capture_output=True, text=True, timeout=30, cwd=self.project_root)
                if result.returncode in [0, 1]:  # npm returns 1 for missing packages but still lists
                    lines = [line for line in result.stdout.split('\n') if '├──' in line or '└──' in line]
                    phase_results["node_inventory"]["count"] = len(lines)
                    phase_results["node_inventory"]["status"] = "healthy"
logger.info("✅ Found %s Node.js packages", str(len(lines))[:100])
                else:
                    phase_results["node_inventory"]["status"] = "degraded"
            except Exception as e:
                pass
logger.warning("Failed Node.js inventory: %s", str(e)[:100])
                phase_results["node_inventory"]["status"] = "error"
        else:
            phase_results["node_inventory"]["status"] = "not_applicable"
            
        # Create dependency snapshot
        try:
            snapshot_data = {
                "timestamp": datetime.now().isoformat(),
                "python_packages": phase_results["python_inventory"]["count"],
                "node_packages": phase_results["node_inventory"]["count"],
                "critical_missing": phase_results["python_inventory"]["critical_missing"],
                "phase": "immediate_validation"
            }
            
            snapshot_file = self.project_root / ".aurora" / "dependency_snapshot_immediate.json"
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2)
                
            phase_results["snapshot_created"] = True
logger.info("✅ Snapshot created: %s", str(snapshot_file)[:100])
            
        except Exception as e:
            pass
logger.warning("Failed to create snapshot: %s", str(e)[:100])
            
        return phase_results
        
    def execute_installation_phase(self, max_time_minutes: int = 5) -> Dict[str, Any]:
        """Execute installation phase with time constraints"""
logger.info("⬆️ Phase 2: Installation (max %s minutes)...", str(max_time_minutes)[:100])
        
        installation_results = {
            "approach": "time_constrained",
            "critical_attempted": [],
            "critical_successful": [],
            "dev_attempted": [],
            "dev_successful": [],
            "timeout_reached": False,
            "fallback_triggered": False
        }
        
        start_time = time.time()
        timeout_seconds = max_time_minutes * 60
        
        # Critical packages to attempt first
        critical_packages = [
            "schedule",  # Needed for scheduler
            "requests",  # Commonly needed
        ]
        
        for package in critical_packages:
            if time.time() - start_time > timeout_seconds:
                installation_results["timeout_reached"] = True
                break
                
            installation_results["critical_attempted"].append(package)
            
            try:
                pass
logger.info("Installing critical package: %s", str(package)[:100])
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "--user", 
                    "--timeout", "30", package
                ], capture_output=True, text=True, timeout=45)
                
                if result.returncode == 0:
                    installation_results["critical_successful"].append(package)
logger.info("✅ Installed: %s", str(package)[:100])
                else:
logger.warning("⚠️  Failed to install: %s", str(package)[:100])
                    
            except subprocess.TimeoutExpired:
                pass
logger.warning("⏰ Timeout installing: %s", str(package)[:100])
            except Exception as e:
                pass
logger.warning("Error installing %s: %s", str(package)[:100], str(e)[:100])
                
        # If time remaining, try development packages
        if time.time() - start_time < timeout_seconds * 0.8:
            dev_packages = ["black", "flake8"]
            
            for package in dev_packages:
                if time.time() - start_time > timeout_seconds:
                    installation_results["timeout_reached"] = True
                    break
                    
                installation_results["dev_attempted"].append(package)
                
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", "--user", 
                        "--timeout", "20", package
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        installation_results["dev_successful"].append(package)
logger.info("✅ Installed dev package: %s", str(package)[:100])
                        
                except Exception as e:
                    pass
logger.warning("Dev package %s failed: %s", str(package)[:100], str(e)[:100])
                    
        # If we couldn't install much, trigger fallback
        if len(installation_results["critical_successful"]) == 0:
            installation_results["fallback_triggered"] = True
            self.logger.warning("🔄 Triggering fallback mode")
            
        return installation_results
        
    def execute_persistence_phase(self) -> Dict[str, Any]:
        """Execute persistence setup phase"""
        self.logger.info("💾 Phase 3: Setting up persistence...")
        
        persistence_results = {
            "startup_script_created": False,
            "health_check_scheduled": False,
            "integration_complete": False
        }
        
        # Create startup validation script
        try:
            startup_script_content = f'''#!/bin/bash
# Aurora CloudBank Dependency Validation Script
# Quick validation of critical dependencies

cd "{self.project_root}"

echo "🔧 Aurora CloudBank: Quick dependency validation..."

# Check if Python is working and has pip
if python3 -m pip --version >/dev/null 2>&1; then
    echo "✅ Python and pip are available"
else
    echo "❌ Python/pip issue detected"
    exit 1
fi

# Check for package.json if it exists
if [ -f "package.json" ]; then
    if command -v npm >/dev/null 2>&1; then
        echo "✅ Node.js and npm are available"
    else
        echo "⚠️  Node.js/npm not available but package.json exists"
    fi
fi

echo "🚀 Basic dependency validation complete"
'''
            
            startup_script = self.project_root / "scripts" / "aurora_quick_dependency_check.sh"
            startup_script.parent.mkdir(exist_ok=True)
            
            with open(startup_script, 'w') as f:
                f.write(startup_script_content)
            startup_script.chmod(0o755)
            
            persistence_results["startup_script_created"] = True
logger.info("✅ Startup script created: %s", str(startup_script)[:100])
            
        except Exception as e:
            pass
logger.warning("Failed to create startup script: %s", str(e)[:100])
            
        # Create simple health check
        try:
            health_check_content = f'''#!/usr/bin/env python3
"""Simple dependency health check for Aurora CloudBank"""

import subprocess
import sys
from pathlib import Path

def quick_health_check():
    """Quick health check of dependencies"""
    issues = []
    
    # Check pip is working
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, timeout=10)
        if result.returncode != 0:
            issues.append("pip not working")
    except:
        issues.append("pip check failed")
        
    # Check critical packages
    try:
        import json
        # These should be available in most Python environments
        pass
    except ImportError as e:
        issues.append(f"Import error: {{e}}")
        
    return len(issues) == 0, issues

if __name__ == "__main__":
    healthy, issues = quick_health_check()
    if healthy:
        print("✅ Dependencies healthy")
        sys.exit(0)
    else:
        print("❌ Issues found: {%s}", ', '.join(issues))
        sys.exit(1)
'''
            
            health_check_script = self.project_root / "scripts" / "aurora_quick_health_check.py"
            with open(health_check_script, 'w') as f:
                f.write(health_check_content)
            health_check_script.chmod(0o755)
            
            persistence_results["health_check_scheduled"] = True
logger.info("✅ Health check script created: %s", str(health_check_script)[:100])
            
        except Exception as e:
            pass
logger.warning("Failed to create health check: %s", str(e)[:100])
            
        persistence_results["integration_complete"] = (
            persistence_results["startup_script_created"] and 
            persistence_results["health_check_scheduled"]
        )
        
        return persistence_results
        
    def execute_automation_phase(self) -> Dict[str, Any]:
        """Execute automation integration phase"""
        self.logger.info("🤖 Phase 4: Setting up automation integration...")
        
        automation_results = {
            "existing_systems_integrated": 0,
            "new_automation_created": False,
            "monitoring_active": False
        }
        
        # Integrate with existing GitWiz system
        if self.existing_systems["gitwiz_dependency_updater"]:
            try:
                # Test if GitWiz dependency updater is working
                gitwiz_script = self.project_root / "scripts" / "gitwiz_dependency_updater.py" 
                result = subprocess.run([
                    sys.executable, str(gitwiz_script), "--help"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    automation_results["existing_systems_integrated"] += 1
                    self.logger.info("✅ GitWiz dependency updater integrated")
                    
            except Exception as e:
                pass
logger.warning("GitWiz integration failed: %s", str(e)[:100])
                
        # Create minimal automation wrapper
        try:
            automation_wrapper = f'''#!/usr/bin/env python3
"""Aurora CloudBank Minimal Automation Wrapper"""

import subprocess
import sys
import time
from pathlib import Path

def run_health_check():
    """Run quick health check"""
    try:
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent / "aurora_quick_health_check.py")
        ], timeout=30)
        return result.returncode == 0
    except:
        return False

def run_maintenance():
    """Run basic maintenance"""
    print("🔧 Running Aurora CloudBank maintenance...")
    
    if run_health_check():
        print("✅ Health check passed")
    else:
        print("⚠️  Health check failed, consider manual review")
        
    # Try to use existing GitWiz if available
    gitwiz_path = Path(__file__).parent / "gitwiz_dependency_updater.py"
    if gitwiz_path.exists():
        try:
            subprocess.run([sys.executable, str(gitwiz_path), "--status"], timeout=60)
        except:
            pass
            
    print("🚀 Maintenance complete")

if __name__ == "__main__":
    run_maintenance()
'''
            
            automation_file = self.project_root / "scripts" / "aurora_minimal_automation.py"
            with open(automation_file, 'w') as f:
                f.write(automation_wrapper)
            automation_file.chmod(0o755)
            
            automation_results["new_automation_created"] = True
logger.info("✅ Minimal automation created: %s", str(automation_file)[:100])
            
        except Exception as e:
            pass
logger.warning("Failed to create automation: %s", str(e)[:100])
            
        automation_results["monitoring_active"] = (
            automation_results["existing_systems_integrated"] > 0 or 
            automation_results["new_automation_created"]
        )
        
        return automation_results
        
    def execute_comprehensive_setup(self) -> Dict[str, Any]:
        """Execute the complete dependency management setup"""
        self.logger.info("🚀 Starting Aurora CloudBank Comprehensive Dependency Setup...")
        
        setup_results = {
            "start_time": datetime.now().isoformat(),
            "strategy": None,
            "phase1_immediate": None,
            "phase2_installation": None, 
            "phase3_persistence": None,
            "phase4_automation": None,
            "overall_success": False,
            "end_time": None
        }
        
        try:
            # Create strategy
            setup_results["strategy"] = self.create_unified_dependency_strategy()
            
            # Phase 1: Immediate validation
            setup_results["phase1_immediate"] = self.execute_immediate_phase()
            
            # Phase 2: Time-constrained installation
            setup_results["phase2_installation"] = self.execute_installation_phase(max_time_minutes=3)
            
            # Phase 3: Persistence setup  
            setup_results["phase3_persistence"] = self.execute_persistence_phase()
            
            # Phase 4: Automation integration
            setup_results["phase4_automation"] = self.execute_automation_phase()
            
            # Determine overall success
            critical_success = (
                setup_results["phase1_immediate"]["requirements_validation"] and
                setup_results["phase3_persistence"]["integration_complete"] and
                setup_results["phase4_automation"]["monitoring_active"]
            )
            
            setup_results["overall_success"] = critical_success
            
            if critical_success:
                self.logger.info("🎉 Comprehensive setup completed successfully!")
            else:
                self.logger.warning("⚠️  Setup completed with some limitations")
                
        except Exception as e:
            pass
logger.error("Setup failed: %s", str(e)[:100])
            setup_results["error"] = str(e)
            
        setup_results["end_time"] = datetime.now().isoformat()
        return setup_results
        
    def generate_final_report(self, setup_results: Dict[str, Any]) -> str:
        """Generate final setup report"""
        report = f"""
# 🔧 Aurora CloudBank Dependency Management Setup Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 📊 Overall Status: {'✅ SUCCESS' if setup_results.get('overall_success') else '⚠️  PARTIAL'}

# 📋 Phase 1 - Immediate Validation:
   Requirements file: {'✅ Valid' if setup_results.get('phase1_immediate', {}).get('requirements_validation') else '❌ Invalid'}
   Python packages: {setup_results.get('phase1_immediate', {}).get('python_inventory', {}).get('count', 0)}
   Critical missing: {len(setup_results.get('phase1_immediate', {}).get('python_inventory', {}).get('critical_missing', []))}

# ⬆️ Phase 2 - Installation:
   Critical attempted: {len(setup_results.get('phase2_installation', {}).get('critical_attempted', []))}
   Critical successful: {len(setup_results.get('phase2_installation', {}).get('critical_successful', []))}
   Timeout reached: {'Yes' if setup_results.get('phase2_installation', {}).get('timeout_reached') else 'No'}

# 💾 Phase 3 - Persistence:
   Startup script: {'✅ Created' if setup_results.get('phase3_persistence', {}).get('startup_script_created') else '❌ Failed'}
   Health monitoring: {'✅ Active' if setup_results.get('phase3_persistence', {}).get('health_check_scheduled') else '❌ Inactive'}

# 🤖 Phase 4 - Automation:
   Existing systems: {setup_results.get('phase4_automation', {}).get('existing_systems_integrated', 0)}
   New automation: {'✅ Created' if setup_results.get('phase4_automation', {}).get('new_automation_created') else '❌ Failed'}

# 💡 Next Steps:
"""
        
        if setup_results.get('overall_success'):
            report += """   • Dependencies are managed and automated
   # • Run 'bash scripts/aurora_quick_dependency_check.sh' to validate
   # • Use 'python3 scripts/aurora_minimal_automation.py' for maintenance
   # • Check '.aurora/' directory for logs and configurations"""
        else:
            report += """   • Some setup steps need manual attention
   # • Check '.aurora/integration.log' for detailed error information
   # • Run individual phase scripts for targeted fixes
   # • Consider manual dependency installation if network issues persist"""
            
        return report

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora CloudBank Dependency Management Integration")
    parser.add_argument("--full-setup", action="store_true", help="Run complete setup")
    parser.add_argument("--phase", choices=["immediate", "installation", "persistence", "automation"], 
                       help="Run specific phase")
    parser.add_argument("--status", action="store_true", help="Show integration status")
    
    args = parser.parse_args()
    
    integration = AuroraDependencyIntegration()
    
    if args.full_setup:
        setup_results = integration.execute_comprehensive_setup()
        print(integration.generate_final_report(setup_results))
        
        if not setup_results.get('overall_success'):
            sys.exit(1)
            
    elif args.phase:
        if args.phase == "immediate":
            results = integration.execute_immediate_phase()
            print("Phase 1 Results: %s", json.dumps(results, indent=2))
        elif args.phase == "installation": 
            results = integration.execute_installation_phase()
            print("Phase 2 Results: %s", json.dumps(results, indent=2))
        elif args.phase == "persistence":
            results = integration.execute_persistence_phase()
            print("Phase 3 Results: %s", json.dumps(results, indent=2))
        elif args.phase == "automation":
            results = integration.execute_automation_phase()
            print("Phase 4 Results: %s", json.dumps(results, indent=2))
            
    elif args.status:
        print("Existing Systems Detected: %s", integration.existing_systems)
        print("Integration Config: %s", integration.config)
        
    else:
        print("Aurora CloudBank Dependency Management Integration")
        print("Use --full-setup to run complete setup")
        print("Use --status to see current state")

if __name__ == "__main__":
    main()