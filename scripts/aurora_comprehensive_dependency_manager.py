#!/usr/bin/env python3
"""
Aurora CloudBank Comprehensive Dependency Manager

Ensures all necessary dependencies are installed, remain installed, and stay updated automatically.
Provides robust error handling, offline capabilities, and comprehensive monitoring.

Features:
- Network timeout handling with retry logic
- Offline dependency caching
- Automated scheduling for updates
- Health monitoring and alerting
- Integration with existing GitWiz systems
- Symbolic anchor continuity support
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import logging
import hashlib

# Aurora CloudBank specific imports with fallback
try:
    from modules.symbolic_core.geometric_algebra import GeometricAlgebra
    from src.core.native_dlp_export import NativeDLPTracker
    AURORA_IMPORTS_AVAILABLE = True
except ImportError:
    AURORA_IMPORTS_AVAILABLE = False

class AuroraComprehensiveDependencyManager:
    """Comprehensive dependency management system for Aurora CloudBank"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.config_file = self.project_root / ".aurora" / "dependency_config.json"
        self.cache_dir = self.project_root / ".aurora" / "dependency_cache"
        self.log_file = self.project_root / ".aurora" / "dependency_manager.log"
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize configuration
        self.config = self._load_config()
        
        # Initialize Aurora DLP tracking if available
        self.dlp_tracker = None
        if AURORA_IMPORTS_AVAILABLE:
            self.dlp_tracker = NativeDLPTracker()
        
        # Dependency state tracking
        self.installed_packages = set()
        self.failed_packages = set()
        self.update_history = []
        
        # Create necessary directories
        self._ensure_directories()
        
    def _setup_logging(self):
        """Set up comprehensive logging"""
        log_dir = self.project_root / ".aurora"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('AuroraDependencyManager')
        
    def _load_config(self) -> Dict[str, Any]:
        """Load or create dependency configuration"""
        default_config = {
            "dependency_sources": {
                "python": {
                    "primary_index": "https://pypi.org/simple/",
                    "backup_indexes": [
                        "https://pypi.python.org/simple/",
                        "https://pypi.doubanio.com/simple/"
                    ],
                    "timeout": 30,
                    "retries": 3,
                    "offline_cache": True
                },
                "node": {
                    "registry": "https://registry.npmjs.org/",
                    "backup_registries": [
                        "https://registry.npm.taobao.org/"
                    ],
                    "timeout": 30,
                    "retries": 3,
                    "offline_cache": True
                }
            },
            "update_schedule": {
                "enabled": True,
                "daily_check": "02:00",
                "weekly_update": "Sunday 01:00",
                "emergency_update": True
            },
            "security": {
                "vulnerability_check": True,
                "auto_fix": True,
                "security_sources": ["pip-audit", "npm audit", "safety"]
            },
            "monitoring": {
                "health_checks": True,
                "alert_threshold": 3,
                "log_retention_days": 30
            },
            "aurora_integration": {
                "symbolic_anchoring": True,
                "dlp_tracking": True,
                "memory_sealing": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**default_config, **loaded_config}
            except Exception as e:
                pass
logger.warning("Failed to load config: %s, using defaults", str(e)[:100])

        return default_config
        
    def _save_config(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def _ensure_directories(self):
        """Create necessary directories"""
        dirs = [
            self.project_root / ".aurora",
            self.cache_dir,
            self.cache_dir / "python",
            self.cache_dir / "node"
        ]
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _create_symbolic_anchor(self, operation_type: str, data: Dict[str, Any]) -> Optional[str]:
        """Create symbolic anchor for dependency operations"""
        if not self.dlp_tracker or not self.config["aurora_integration"]["symbolic_anchoring"]:
            return None
            
        try:
            tag_id = self.dlp_tracker.tag_symbolic_operation(data)
            tag = self.dlp_tracker.tags[tag_id]
            tag.add_anchor_protocol("T1_DEPENDENCY_ANCHOR")
            tag.add_anchor_protocol("SRB_DEPENDENCY_RESOLUTION")
            tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
            tag.metadata.update({
                'operation_type': operation_type,
                'dlp_level': 'DLP_L1_OK',
                'symbolic_hash_validation': True,
                'context_tag': f'dependency_{operation_type}',
                'state_tag': f'dependency_state_{datetime.now().isoformat()}'
            })
            return tag_id
        except Exception as e:
            pass
logger.warning("Failed to create symbolic anchor: %s", str(e)[:100])
return None

    def robust_install_package(self, package_spec: str, package_type: str = "python") -> bool:
        """Install package with robust error handling and retry logic"""
        anchor_id = self._create_symbolic_anchor("install", {
            "package": package_spec,
            "type": package_type
        })
        
        max_retries = self.config["dependency_sources"][package_type]["retries"]
        timeout = self.config["dependency_sources"][package_type]["timeout"]
        
        for attempt in range(max_retries):
            try:
                pass
logger.info("Installing %s (attempt %s/%s)", str(package_spec)[:100], str(attempt + 1)[:100], str(max_retries)[:100])

                if package_type == "python":
                    result = self._install_python_package(package_spec, timeout)
                elif package_type == "node":
                    result = self._install_node_package(package_spec, timeout)
                else:
                    raise ValueError(f"Unknown package type: {package_type}")
                    
                if result:
                    self.installed_packages.add(package_spec)
logger.info("Successfully installed %s", str(package_spec)[:100])
return True

            except subprocess.TimeoutExpired:
                pass
logger.warning("Timeout installing %s (attempt %s)", str(package_spec)[:100], str(attempt + 1)[:100])
if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                pass
logger.error("Error installing %s: %s", str(package_spec)[:100], str(e)[:100])
if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
        self.failed_packages.add(package_spec)
logger.error("Failed to install %s after %s attempts", str(package_spec)[:100], str(max_retries)[:100])
return False

    def _install_python_package(self, package_spec: str, timeout: int) -> bool:
        """Install Python package with fallback to backup indexes"""
        indexes = [
            self.config["dependency_sources"]["python"]["primary_index"]
        ] + self.config["dependency_sources"]["python"]["backup_indexes"]
        
        for index in indexes:
            try:
                cmd = [
                    sys.executable, "-m", "pip", "install", 
                    "--user", "--timeout", str(timeout),
                    "--index-url", index,
                    package_spec
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout + 10,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    return True
                    
            except subprocess.TimeoutExpired:
                pass
logger.warning("Timeout with index %s", str(index)[:100])
continue
except Exception as e:
                pass
logger.warning("Failed with index %s: %s", str(index)[:100], str(e)[:100])
continue

        return False
        
    def _install_node_package(self, package_spec: str, timeout: int) -> bool:
        """Install Node.js package with fallback to backup registries"""
        registries = [
            self.config["dependency_sources"]["node"]["registry"]
        ] + self.config["dependency_sources"]["node"]["backup_registries"]
        
        for registry in registries:
            try:
                cmd = ["npm", "install", "--registry", registry, package_spec]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout + 10,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    return True
                    
            except subprocess.TimeoutExpired:
                pass
logger.warning("Timeout with registry %s", str(registry)[:100])
continue
except Exception as e:
                pass
logger.warning("Failed with registry %s: %s", str(registry)[:100], str(e)[:100])
continue

        return False
        
    def install_requirements(self, requirements_file: str = "requirements.txt") -> Dict[str, Any]:
        """Install all requirements from file with comprehensive error handling"""
        results = {
            "installed": [],
            "failed": [],
            "skipped": [],
            "total": 0,
            "success_rate": 0.0
        }
        
        requirements_path = self.project_root / requirements_file
        if not requirements_path.exists():
logger.error("Requirements file not found: %s", str(requirements_file)[:100])
return results

        with open(requirements_path, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        results["total"] = len(requirements)
logger.info("Installing %s packages from %s", str(results['total'])[:100], str(requirements_file)[:100])

        for requirement in requirements:
            if self.robust_install_package(requirement, "python"):
                results["installed"].append(requirement)
            else:
                results["failed"].append(requirement)
                
        results["success_rate"] = len(results["installed"]) / results["total"] if results["total"] > 0 else 0
        
logger.info("Installation complete: %s/%s packages installed", str(len(results['installed']))[:100], str(results['total'])[:100])
return results

    def check_dependency_health(self) -> Dict[str, Any]:
        """Comprehensive dependency health check"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "python": {"status": "unknown", "issues": [], "packages": 0},
            "node": {"status": "unknown", "issues": [], "packages": 0},
            "security": {"vulnerabilities": 0, "issues": []},
            "overall_health": "unknown"
        }
        
        # Check Python dependencies
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
            capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                python_packages = len([line for line in result.stdout.split('\n') if line.strip() and not line.startswith('Package')])
                health_report["python"]["packages"] = python_packages
                health_report["python"]["status"] = "healthy"
            else:
                health_report["python"]["issues"].append("pip list failed")
                health_report["python"]["status"] = "unhealthy"
        except Exception as e:
            health_report["python"]["issues"].append(f"Python check failed: {e}")
            health_report["python"]["status"] = "error"
            
        # Check Node.js dependencies
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(["npm", "list", "--depth=0"], 
                capture_output=True, text=True, timeout=30, cwd=self.project_root)
                # npm list returns non-zero for missing packages, but that's ok
                node_packages = len([line for line in result.stdout.split('\n') if '├──' in line or '└──' in line])
                health_report["node"]["packages"] = node_packages
                health_report["node"]["status"] = "healthy" if result.returncode in [0, 1] else "unhealthy"
            except Exception as e:
                health_report["node"]["issues"].append(f"Node check failed: {e}")
                health_report["node"]["status"] = "error"
        else:
            health_report["node"]["status"] = "not_applicable"
            
        # Security vulnerability check
        if self.config["security"]["vulnerability_check"]:
            health_report["security"] = self._check_security_vulnerabilities()
            
        # Calculate overall health
        statuses = [health_report["python"]["status"], health_report["node"]["status"]]
        if "error" in statuses:
            health_report["overall_health"] = "critical"
        elif "unhealthy" in statuses:
            health_report["overall_health"] = "degraded"
        elif health_report["security"]["vulnerabilities"] > 0:
            health_report["overall_health"] = "vulnerable"
        else:
            health_report["overall_health"] = "healthy"
            
        return health_report
        
    def _check_security_vulnerabilities(self) -> Dict[str, Any]:
        """Check for security vulnerabilities"""
        security_report = {"vulnerabilities": 0, "issues": [], "tools_used": []}
        
        # Check Python with pip-audit if available
        try:
            result = subprocess.run([sys.executable, "-m", "pip_audit", "--format=json"], 
            capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                security_report["vulnerabilities"] += len(audit_data.get("vulnerabilities", []))
                security_report["tools_used"].append("pip-audit")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
            
        # Check Node.js with npm audit
        if (self.project_root / "package.json").exists():
            try:
                result = subprocess.run(["npm", "audit", "--json"], 
                capture_output=True, text=True, timeout=60, cwd=self.project_root)
                if result.stdout:
                    audit_data = json.loads(result.stdout)
                    security_report["vulnerabilities"] += audit_data.get("metadata", {}).get("vulnerabilities", {}).get("total", 0)
                    security_report["tools_used"].append("npm-audit")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
                pass
                
        return security_report
        
    def automated_update_check(self) -> Dict[str, Any]:
        """Check for available updates"""
        update_report = {
            "timestamp": datetime.now().isoformat(),
            "python_outdated": [],
            "node_outdated": [],
            "update_recommendations": []
        }
        
        # Check outdated Python packages
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list", "--outdated", "--format=json"], 
            capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                outdated_data = json.loads(result.stdout)
                update_report["python_outdated"] = outdated_data
        except Exception as e:
            pass
logger.warning("Failed to check outdated Python packages: %s", str(e)[:100])

        # Check outdated Node.js packages
        if (self.project_root / "package.json").exists():
            try:
                result = subprocess.run(["npm", "outdated", "--json"], 
                capture_output=True, text=True, timeout=60, cwd=self.project_root)
                if result.stdout:
                    outdated_data = json.loads(result.stdout)
                    update_report["node_outdated"] = list(outdated_data.keys())
            except Exception as e:
                pass
logger.warning("Failed to check outdated Node.js packages: %s", str(e)[:100])

        # Generate recommendations
        total_outdated = len(update_report["python_outdated"]) + len(update_report["node_outdated"])
        if total_outdated > 0:
            update_report["update_recommendations"].append(f"Found {total_outdated} outdated packages")
            update_report["update_recommendations"].append("Run automated update to resolve")
            
        return update_report
        
    def execute_comprehensive_update(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute comprehensive dependency update workflow"""
        workflow_result = {
            "start_time": datetime.now().isoformat(),
            "dry_run": dry_run,
            "backup_created": False,
            "health_check": {},
            "update_check": {},
            "security_fixes": {},
            "installation_results": {},
            "final_health": {},
            "success": False,
            "errors": []
        }
        
        try:
            pass
logger.info("🚀 Starting comprehensive dependency update (dry_run=%s)", str(dry_run)[:100])

            # Step 1: Health check
            self.logger.info("📊 Performing initial health check...")
            workflow_result["health_check"] = self.check_dependency_health()
            
            # Step 2: Update check
            self.logger.info("🔍 Checking for available updates...")
            workflow_result["update_check"] = self.automated_update_check()
            
            # Step 3: Security fixes
            if self.config["security"]["auto_fix"] and not dry_run:
                self.logger.info("🔒 Applying security fixes...")
                workflow_result["security_fixes"] = self._apply_security_fixes()
                
            # Step 4: Install/update requirements
            if not dry_run:
                self.logger.info("⬆️ Installing/updating requirements...")
                workflow_result["installation_results"] = self.install_requirements()
            else:
                self.logger.info("🔍 DRY RUN: Would install/update requirements")
                
            # Step 5: Final health check
            self.logger.info("🏥 Performing final health check...")
            workflow_result["final_health"] = self.check_dependency_health()
            
            workflow_result["success"] = True
            self.logger.info("✅ Comprehensive dependency update completed successfully!")
            
        except Exception as e:
            workflow_result["errors"].append(str(e))
logger.error("❌ Comprehensive update failed: %s", str(e)[:100])

        workflow_result["end_time"] = datetime.now().isoformat()
        return workflow_result
        
    def _apply_security_fixes(self) -> Dict[str, Any]:
        """Apply automated security fixes"""
        security_result = {"python_fixes": [], "node_fixes": [], "errors": []}
        
        # Apply Python security fixes
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--user", "pip"], 
            capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                security_result["python_fixes"].append("Updated pip to latest version")
        except Exception as e:
            security_result["errors"].append(f"Failed to update pip: {e}")
            
        # Apply Node.js security fixes
        if (self.project_root / "package.json").exists():
            try:
                result = subprocess.run(["npm", "audit", "fix"], 
                capture_output=True, text=True, timeout=120, cwd=self.project_root)
                if result.returncode == 0:
                    security_result["node_fixes"].append("Applied npm audit fix")
            except Exception as e:
                security_result["errors"].append(f"Failed npm audit fix: {e}")
                
        return security_result
        
    def schedule_automated_updates(self):
        """Set up automated update scheduling"""
        if not self.config["update_schedule"]["enabled"]:
            self.logger.info("Automated updates are disabled")
            return
            
        self.logger.info("Setting up automated update scheduling...")
        
        # Create systemd service file for Linux systems
        service_content = f"""[Unit]
Description=Aurora CloudBank Dependency Manager
After=network.target

[Service]
Type=oneshot
User={os.getenv('USER', 'runner')}
WorkingDirectory={self.project_root}
ExecStart={sys.executable} {__file__} --automated-update
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
"""

        timer_content = f"""[Unit]
Description=Aurora CloudBank Dependency Manager Timer
Requires=aurora-dependency-manager.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
"""

        try:
            service_dir = Path.home() / ".config" / "systemd" / "user"
            service_dir.mkdir(parents=True, exist_ok=True)
            
            (service_dir / "aurora-dependency-manager.service").write_text(service_content)
            (service_dir / "aurora-dependency-manager.timer").write_text(timer_content)
            
            self.logger.info("✅ Automated update scheduling configured")
        except Exception as e:
            pass
logger.warning("Failed to set up automated scheduling: %s", str(e)[:100])

    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        health = self.check_dependency_health()
        updates = self.automated_update_check()
        
        report = f"""
# 🔧 Aurora CloudBank Dependency Manager Status Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 📊 Overall Health: {health['overall_health'].upper()}

# 🐍 Python Dependencies:
   Status: {health['python']['status']}
   Packages: {health['python']['packages']}
   Outdated: {len(updates['python_outdated'])}

# 📦 Node.js Dependencies:
   Status: {health['node']['status']}
   Packages: {health['node']['packages']}
   Outdated: {len(updates['node_outdated'])}

# 🔒 Security:
   Vulnerabilities: {health['security']['vulnerabilities']}
   
# 💡 Recommendations:
"""

        for rec in updates['update_recommendations']:
            report += f"   • {rec}\n"
            
        if health['overall_health'] != 'healthy':
            report += "\n⚠️  Action required: Run 'python scripts/aurora_comprehensive_dependency_manager.py --update' to resolve issues\n"
        else:
            report += "\n✅ All dependencies are healthy and up to date\n"
            
        return report

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora CloudBank Comprehensive Dependency Manager")
    parser.add_argument("--install", action="store_true", help="Install all requirements")
    parser.add_argument("--update", action="store_true", help="Update all dependencies")
    parser.add_argument("--health-check", action="store_true", help="Perform health check")
    parser.add_argument("--status", action="store_true", help="Show status report")
    parser.add_argument("--schedule", action="store_true", help="Set up automated scheduling")
    parser.add_argument("--automated-update", action="store_true", help="Run automated update (for cron/systemd)")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without actual changes")
    
    args = parser.parse_args()
    
    manager = AuroraComprehensiveDependencyManager()
    
    if args.install:
        print("🔧 Installing dependencies...")
        results = manager.install_requirements()
        print(f"✅ Installed %s/{results[", len(results['installed']))
        
    elif args.update:
        print("⬆️ Updating dependencies...")
        results = manager.execute_comprehensive_update(dry_run=args.dry_run)
        if results['success']:
            print("✅ Update completed successfully!")
        else:
            print("❌ Update completed with errors")
            for error in results['errors']:
                print(f"   Error: {error}")
                
    elif args.health_check:
        print("🏥 Performing health check...")
        health = manager.check_dependency_health()
        print(f"Overall Health: {health['overall_health'].upper(}"))
        
    elif args.status:
        print(manager.generate_status_report())
        
    elif args.schedule:
        print("⏰ Setting up automated scheduling...")
        manager.schedule_automated_updates()
        
    elif args.automated_update:
        # This is called by the scheduler
        results = manager.execute_comprehensive_update(dry_run=False)
        if not results['success']:
            sys.exit(1)
            
    else:
        print(manager.generate_status_report())

if __name__ == "__main__":
    main()