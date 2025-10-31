#!/usr/bin/env python3
"""
Comprehensive System Audit for Aurora CloudBank Symbolic
Performs dependency audit and MCP server audit as requested in priorities.

This script combines:
1. Dependency audit (Python and Node.js packages)
2. MCP server audit (configuration, routing, security)
3. Security scan validation

Includes DLP tracking and generates a comprehensive audit report.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class ComprehensiveSystemAuditor:
    """Comprehensive auditor for Aurora system dependencies and MCP server"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.timestamp = datetime.now().isoformat()
        self.context_tag = f"system_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def run_full_audit(self) -> Dict[str, Any]:
        """Execute complete system audit"""
        print("🔍 Starting Comprehensive System Audit...")
        print(f"📋 Context Tag: {self.context_tag}")
        print(f"⏰ Timestamp: {self.timestamp}")
        print("=" * 80)
        
        audit_report = {
            "audit_metadata": {
                "timestamp": self.timestamp,
                "context_tag": self.context_tag,
                "audit_version": "1.0.0",
                "project_root": str(self.project_root)
            },
            "dependency_audit": self._audit_dependencies(),
            "mcp_server_audit": self._audit_mcp_server(),
            "security_scan_status": self._check_security_scans(),
            "recommendations": [],
            "overall_status": "unknown"
        }
        
        # Generate recommendations and determine overall status
        audit_report["recommendations"] = self._generate_recommendations(audit_report)
        audit_report["overall_status"] = self._determine_overall_status(audit_report)
        
        return audit_report
        
    def _audit_dependencies(self) -> Dict[str, Any]:
        """Audit Python and Node.js dependencies"""
        print("\n📦 PRIORITY 2: Dependency Audit")
        print("-" * 80)
        
        dep_audit = {
            "python_dependencies": self._audit_python_deps(),
            "nodejs_dependencies": self._audit_nodejs_deps(),
            "requirements_files": self._check_requirements_files(),
            "dependency_conflicts": self._check_dependency_conflicts(),
            "status": "unknown"
        }
        
        # Determine status
        python_ok = dep_audit["python_dependencies"]["status"] == "healthy"
        nodejs_ok = dep_audit["nodejs_dependencies"]["status"] in ["healthy", "not_applicable"]
        conflicts = dep_audit["dependency_conflicts"]["conflicts_found"]
        
        if python_ok and nodejs_ok and not conflicts:
            dep_audit["status"] = "healthy"
        elif python_ok or nodejs_ok:
            dep_audit["status"] = "warning"
        else:
            dep_audit["status"] = "critical"
            
        return dep_audit
        
    def _audit_python_deps(self) -> Dict[str, Any]:
        """Audit Python package dependencies"""
        print("  🐍 Auditing Python dependencies...")
        
        python_audit = {
            "installed_packages": 0,
            "critical_packages": [],
            "missing_critical": [],
            "outdated_packages": [],
            "status": "unknown",
            "details": []
        }
        
        # Get installed packages
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                packages = [line for line in result.stdout.split('\n') 
                           if line.strip() and not line.startswith('Package')]
                python_audit["installed_packages"] = len(packages)
                installed_names = {line.split()[0].lower() for line in packages if line.strip()}
                
                # Check critical packages
                critical_packages = [
                    "fastapi", "uvicorn", "pydantic", "pandas", 
                    "numpy", "requests", "httpx", "pytest"
                ]
                
                for pkg in critical_packages:
                    if pkg in installed_names:
                        python_audit["critical_packages"].append(pkg)
                    else:
                        python_audit["missing_critical"].append(pkg)
                        
                print(f"     ✓ Installed packages: {len(packages)}")
                print(f"     ✓ Critical packages present: {len(python_audit['critical_packages'])}")
                if python_audit["missing_critical"]:
                    print(f"     ⚠ Missing critical: {', '.join(python_audit['missing_critical'])}")
                    
        except Exception as e:
            python_audit["details"].append(f"Error checking packages: {e}")
            print(f"     ✗ Error: {e}")
            
        # Check for outdated packages
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                outdated = [line for line in result.stdout.split('\n')
                           if line.strip() and not line.startswith('Package')]
                python_audit["outdated_packages"] = len(outdated)
                if outdated:
                    print(f"     ℹ Outdated packages: {len(outdated)}")
                    
        except Exception as e:
            python_audit["details"].append(f"Error checking outdated: {e}")
            
        # Determine status
        if len(python_audit["missing_critical"]) == 0:
            python_audit["status"] = "healthy"
        elif len(python_audit["critical_packages"]) > len(python_audit["missing_critical"]):
            python_audit["status"] = "warning"
        else:
            python_audit["status"] = "critical"
            
        return python_audit
        
    def _audit_nodejs_deps(self) -> Dict[str, Any]:
        """Audit Node.js package dependencies"""
        print("  📦 Auditing Node.js dependencies...")
        
        nodejs_audit = {
            "installed_packages": 0,
            "package_json_exists": False,
            "vulnerabilities": 0,
            "status": "not_applicable",
            "details": []
        }
        
        package_json = self.project_root / "package.json"
        if not package_json.exists():
            print("     ℹ package.json not found - skipping Node.js audit")
            return nodejs_audit
            
        nodejs_audit["package_json_exists"] = True
        
        try:
            result = subprocess.run(
                ["npm", "list", "--depth=0"],
                capture_output=True, text=True, timeout=30,
                cwd=self.project_root
            )
            
            if result.returncode in [0, 1]:
                lines = [line for line in result.stdout.split('\n') 
                        if '├──' in line or '└──' in line]
                nodejs_audit["installed_packages"] = len(lines)
                print(f"     ✓ Installed packages: {len(lines)}")
                nodejs_audit["status"] = "healthy"
                
        except FileNotFoundError:
            nodejs_audit["details"].append("npm not found")
            print("     ⚠ npm not found")
            nodejs_audit["status"] = "not_applicable"
        except Exception as e:
            nodejs_audit["details"].append(f"Error: {e}")
            print(f"     ✗ Error: {e}")
            nodejs_audit["status"] = "error"
            
        return nodejs_audit
        
    def _check_requirements_files(self) -> Dict[str, Any]:
        """Check status of requirements files"""
        print("  📄 Checking requirements files...")
        
        req_files = {
            "files_found": [],
            "files_missing": [],
            "status": "unknown"
        }
        
        expected_files = [
            "requirements.txt",
            "requirements-lock.txt",
            "requirements-test.txt",
            "requirements-dev.txt"
        ]
        
        for filename in expected_files:
            filepath = self.project_root / filename
            if filepath.exists():
                req_files["files_found"].append(filename)
                print(f"     ✓ {filename}")
            else:
                req_files["files_missing"].append(filename)
                print(f"     ✗ {filename} (missing)")
                
        if len(req_files["files_found"]) >= 2:
            req_files["status"] = "healthy"
        elif len(req_files["files_found"]) >= 1:
            req_files["status"] = "warning"
        else:
            req_files["status"] = "critical"
            
        return req_files
        
    def _check_dependency_conflicts(self) -> Dict[str, Any]:
        """Check for dependency conflicts"""
        print("  🔍 Checking for dependency conflicts...")
        
        conflicts = {
            "conflicts_found": False,
            "conflict_details": [],
            "status": "unknown"
        }
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                conflicts["status"] = "healthy"
                print("     ✓ No dependency conflicts detected")
            else:
                conflicts["conflicts_found"] = True
                conflicts["status"] = "warning"
                conflicts["conflict_details"] = result.stdout.strip().split('\n')
                print(f"     ⚠ Conflicts detected: {len(conflicts['conflict_details'])}")
                
        except Exception as e:
            conflicts["conflict_details"].append(f"Error: {e}")
            conflicts["status"] = "error"
            print(f"     ✗ Error: {e}")
            
        return conflicts
        
    def _audit_mcp_server(self) -> Dict[str, Any]:
        """Audit MCP (Message Control Protocol) server configuration and components"""
        print("\n🌉 PRIORITY 3: MCP Server Audit")
        print("-" * 80)
        
        mcp_audit = {
            "mcp_bridge_config": self._check_mcp_bridge_config(),
            "mcp_command_router": self._check_mcp_command_router(),
            "mcp_security": self._check_mcp_security(),
            "mcp_integration_points": self._check_mcp_integration(),
            "status": "unknown"
        }
        
        # Determine overall MCP status
        statuses = [
            mcp_audit["mcp_bridge_config"]["status"],
            mcp_audit["mcp_command_router"]["status"],
            mcp_audit["mcp_security"]["status"]
        ]
        
        if all(s == "healthy" for s in statuses):
            mcp_audit["status"] = "healthy"
        elif any(s == "healthy" for s in statuses):
            mcp_audit["status"] = "warning"
        else:
            mcp_audit["status"] = "critical"
            
        return mcp_audit
        
    def _check_mcp_bridge_config(self) -> Dict[str, Any]:
        """Check MCP Bridge Core configuration"""
        print("  🌉 Checking MCP Bridge Core configuration...")
        
        bridge_config = {
            "config_file_exists": False,
            "config_valid": False,
            "config_content": None,
            "status": "unknown"
        }
        
        config_path = self.project_root / "modules" / "symbolic_core" / "mcp_bridge_core.json"
        
        if config_path.exists():
            bridge_config["config_file_exists"] = True
            print(f"     ✓ Config file found: {config_path}")
            
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    bridge_config["config_content"] = config
                    bridge_config["config_valid"] = True
                    
                    # Check essential fields
                    if "governance_layer" in config:
                        print(f"     ✓ Governance layer: {config['governance_layer']}")
                    if "core_functions" in config:
                        print(f"     ✓ Core functions: {len(config['core_functions'])} defined")
                        
                    bridge_config["status"] = "healthy"
                    
            except json.JSONDecodeError as e:
                bridge_config["status"] = "error"
                print(f"     ✗ Invalid JSON: {e}")
            except Exception as e:
                bridge_config["status"] = "error"
                print(f"     ✗ Error reading config: {e}")
        else:
            bridge_config["status"] = "missing"
            print(f"     ✗ Config file not found: {config_path}")
            
        return bridge_config
        
    def _check_mcp_command_router(self) -> Dict[str, Any]:
        """Check MCP Command Router component"""
        print("  🔀 Checking MCP Command Router...")
        
        router_check = {
            "router_file_exists": False,
            "router_importable": False,
            "router_functional": False,
            "status": "unknown"
        }
        
        router_path = self.project_root / "modules" / "symbolic_core" / "mcp_command_router.py"
        
        if router_path.exists():
            router_check["router_file_exists"] = True
            print(f"     ✓ Router file found: {router_path}")
            
            # Try to import and test the router
            try:
                sys.path.insert(0, str(self.project_root))
                from modules.symbolic_core.mcp_command_router import MCPCommandRouter
                
                router_check["router_importable"] = True
                print("     ✓ Router is importable")
                
                # Test basic functionality
                router = MCPCommandRouter()
                test_result = router.route("test_command")
                
                if test_result and "status" in test_result:
                    router_check["router_functional"] = True
                    print(f"     ✓ Router functional (status: {test_result['status']})")
                    router_check["status"] = "healthy"
                    
            except ImportError as e:
                router_check["status"] = "error"
                print(f"     ⚠ Import error: {e}")
            except Exception as e:
                router_check["status"] = "error"
                print(f"     ⚠ Runtime error: {e}")
        else:
            router_check["status"] = "missing"
            print(f"     ✗ Router file not found: {router_path}")
            
        return router_check
        
    def _check_mcp_security(self) -> Dict[str, Any]:
        """Check MCP Security component"""
        print("  🔒 Checking MCP Security...")
        
        security_check = {
            "security_file_exists": False,
            "security_importable": False,
            "status": "unknown"
        }
        
        security_path = self.project_root / "modules" / "symbolic_core" / "mcp_security.py"
        
        if security_path.exists():
            security_check["security_file_exists"] = True
            print(f"     ✓ Security file found: {security_path}")
            
            try:
                sys.path.insert(0, str(self.project_root))
                from modules.symbolic_core.mcp_security import MCPSecurity
                
                security_check["security_importable"] = True
                print("     ✓ Security module is importable")
                security_check["status"] = "healthy"
                
            except ImportError as e:
                security_check["status"] = "error"
                print(f"     ⚠ Import error: {e}")
            except Exception as e:
                security_check["status"] = "error"
                print(f"     ⚠ Error: {e}")
        else:
            security_check["status"] = "missing"
            print(f"     ✗ Security file not found: {security_path}")
            
        return security_check
        
    def _check_mcp_integration(self) -> Dict[str, Any]:
        """Check MCP integration points in the main application"""
        print("  🔗 Checking MCP integration points...")
        
        integration = {
            "api_integration": False,
            "integration_files": [],
            "status": "unknown"
        }
        
        # Check main API file for MCP integration
        api_file = self.project_root / "aurora_gui_cloudhub_fastapi.py"
        if api_file.exists():
            try:
                with open(api_file, 'r') as f:
                    content = f.read()
                    if "MCPCommandRouter" in content:
                        integration["api_integration"] = True
                        integration["integration_files"].append("aurora_gui_cloudhub_fastapi.py")
                        print("     ✓ MCP integrated in FastAPI application")
                        
            except Exception as e:
                print(f"     ⚠ Error checking API integration: {e}")
                
        if integration["api_integration"]:
            integration["status"] = "healthy"
        else:
            integration["status"] = "warning"
            print("     ℹ MCP integration not detected in main API")
            
        return integration
        
    def _check_security_scans(self) -> Dict[str, Any]:
        """Check security scan log status (Priority 1 related)"""
        print("\n🔒 PRIORITY 1: Security Scan Status")
        print("-" * 80)
        
        scan_status = {
            "scan_log_exists": False,
            "total_scans": 0,
            "latest_scan": None,
            "recent_issues": 0,
            "status": "unknown"
        }
        
        scan_log_path = self.project_root / ".security" / "scan_log.json"
        
        if scan_log_path.exists():
            scan_status["scan_log_exists"] = True
            print(f"  ✓ Security scan log found: {scan_log_path}")
            
            try:
                with open(scan_log_path, 'r') as f:
                    scan_data = json.load(f)
                    
                    if "scans" in scan_data:
                        scans = scan_data["scans"]
                        scan_status["total_scans"] = len(scans)
                        print(f"  ✓ Total scans recorded: {len(scans)}")
                        
                        if scans:
                            # Get latest scan
                            latest = scans[-1]
                            scan_status["latest_scan"] = {
                                "timestamp": latest.get("timestamp"),
                                "status": latest.get("status"),
                                "files_scanned": latest.get("files_scanned", 0)
                            }
                            print(f"  ✓ Latest scan: {latest.get('timestamp')}")
                            print(f"  ✓ Status: {latest.get('status')}")
                            
                            # Count recent issues (last 5 scans)
                            recent_scans = scans[-5:]
                            scan_status["recent_issues"] = sum(
                                1 for s in recent_scans 
                                if s.get("status") == "ISSUES_FOUND"
                            )
                            
                            if scan_status["recent_issues"] > 0:
                                print(f"  ⚠ Recent scans with issues: {scan_status['recent_issues']}/5")
                                scan_status["status"] = "warning"
                            else:
                                print("  ✓ No issues in recent scans")
                                scan_status["status"] = "healthy"
                        else:
                            scan_status["status"] = "warning"
                            
            except Exception as e:
                scan_status["status"] = "error"
                print(f"  ✗ Error reading scan log: {e}")
        else:
            scan_status["status"] = "missing"
            print(f"  ✗ Security scan log not found: {scan_log_path}")
            
        return scan_status
        
    def _generate_recommendations(self, audit_report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on audit findings"""
        recommendations = []
        
        # Dependency recommendations
        dep_audit = audit_report["dependency_audit"]
        python_deps = dep_audit["python_dependencies"]
        
        if python_deps["missing_critical"]:
            recommendations.append(
                f"Install missing critical Python packages: {', '.join(python_deps['missing_critical'])}"
            )
            recommendations.append(
                "Run: pip install " + " ".join(python_deps["missing_critical"])
            )
            
        if dep_audit["dependency_conflicts"]["conflicts_found"]:
            recommendations.append(
                "Resolve dependency conflicts detected by 'pip check'"
            )
            
        # MCP recommendations
        mcp_audit = audit_report["mcp_server_audit"]
        
        if mcp_audit["mcp_bridge_config"]["status"] != "healthy":
            recommendations.append(
                "Review and validate MCP Bridge Core configuration"
            )
            
        if mcp_audit["mcp_command_router"]["status"] != "healthy":
            recommendations.append(
                "Verify MCP Command Router implementation and dependencies"
            )
            
        # Security recommendations
        sec_status = audit_report["security_scan_status"]
        
        if sec_status["recent_issues"] > 0:
            recommendations.append(
                f"Address security issues found in recent scans ({sec_status['recent_issues']} scans with issues)"
            )
            
        if not recommendations:
            recommendations.append("All systems operational - no immediate actions required")
            
        return recommendations
        
    def _determine_overall_status(self, audit_report: Dict[str, Any]) -> str:
        """Determine overall system status"""
        statuses = [
            audit_report["dependency_audit"]["status"],
            audit_report["mcp_server_audit"]["status"],
            audit_report["security_scan_status"]["status"]
        ]
        
        if all(s == "healthy" for s in statuses):
            return "excellent"
        elif all(s in ["healthy", "warning"] for s in statuses):
            return "good"
        elif any(s == "healthy" for s in statuses):
            return "needs_attention"
        else:
            return "critical"
            
    def save_report(self, audit_report: Dict[str, Any], output_path: Path = None):
        """Save audit report to JSON file with DLP tracking"""
        if output_path is None:
            output_path = self.project_root / "audit_reports" / f"system_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add DLP metadata
        audit_report["dlp_metadata"] = {
            "context_tag": self.context_tag,
            "export_timestamp": datetime.now().isoformat(),
            "symbolic_hash_validation": self._compute_validation_hash(audit_report)
        }
        
        with open(output_path, 'w') as f:
            json.dump(audit_report, f, indent=2)
            
        print(f"\n📄 Audit report saved: {output_path}")
        return output_path
        
    def _compute_validation_hash(self, data: Dict[str, Any]) -> str:
        """Compute symbolic hash for validation (simplified)"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
        
    def print_summary(self, audit_report: Dict[str, Any]):
        """Print a formatted summary of the audit"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE SYSTEM AUDIT SUMMARY")
        print("=" * 80)
        
        # Overall status
        status = audit_report["overall_status"]
        status_emoji = {
            "excellent": "✅",
            "good": "🟢",
            "needs_attention": "🟡",
            "critical": "🔴"
        }.get(status, "❓")
        
        print(f"\n{status_emoji} Overall Status: {status.upper()}")
        
        # Dependencies
        print("\n📦 Dependencies:")
        dep_status = audit_report["dependency_audit"]["status"]
        print(f"   Status: {dep_status}")
        python_deps = audit_report["dependency_audit"]["python_dependencies"]
        print(f"   Python packages: {python_deps['installed_packages']}")
        print(f"   Critical missing: {len(python_deps['missing_critical'])}")
        
        # MCP Server
        print("\n🌉 MCP Server:")
        mcp_status = audit_report["mcp_server_audit"]["status"]
        print(f"   Status: {mcp_status}")
        
        # Security
        print("\n🔒 Security Scans:")
        sec_status = audit_report["security_scan_status"]["status"]
        print(f"   Status: {sec_status}")
        if audit_report["security_scan_status"]["latest_scan"]:
            latest = audit_report["security_scan_status"]["latest_scan"]
            print(f"   Latest scan: {latest['status']}")
            
        # Recommendations
        print("\n💡 Recommendations:")
        for i, rec in enumerate(audit_report["recommendations"], 1):
            print(f"   {i}. {rec}")
            
        print("\n" + "=" * 80)
        print(f"🏷️  Context Tag: {self.context_tag}")
        print(f"⏰ Audit completed: {self.timestamp}")
        print("=" * 80)


def main():
    """Main execution function"""
    print("🚀 Aurora CloudBank Symbolic - Comprehensive System Audit")
    print("   Executing all three priorities as requested")
    print()
    
    # Initialize auditor
    project_root = Path.cwd()
    auditor = ComprehensiveSystemAuditor(project_root)
    
    # Run full audit
    audit_report = auditor.run_full_audit()
    
    # Save report
    report_path = auditor.save_report(audit_report)
    
    # Print summary
    auditor.print_summary(audit_report)
    
    # Return exit code based on status
    if audit_report["overall_status"] in ["excellent", "good"]:
        return 0
    elif audit_report["overall_status"] == "needs_attention":
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
