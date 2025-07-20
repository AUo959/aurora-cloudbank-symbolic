#!/usr/bin/env python3
"""
GitWiz Pre-commit Hooks Audit Tool
==================================

Comprehensive audit tool to analyze and test the GitWiz Quality Gates system
and pre-commit hooks functionality.

This script:
1. Tests GitWiz functionality
2. Analyzes pre-commit hook configurations
3. Tests actual hook execution
4. Provides detailed audit report
5. Identifies configuration issues

Author: GitHub Copilot for Aurora CloudBank
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

class GitWizPrecommitAuditor:
    """Comprehensive auditor for GitWiz pre-commit system."""
    
    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(self.repo_path),
            "components": {},
            "configurations": {},
            "functionality_tests": {},
            "issues": [],
            "recommendations": []
        }
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Execute complete audit of GitWiz pre-commit system."""
        print("🔍 Starting GitWiz Pre-commit Hooks Audit...")
        print("=" * 60)
        
        # 1. Test GitWiz Components
        print("\n1️⃣ Testing GitWiz Components...")
        self._test_gitwiz_components()
        
        # 2. Analyze Pre-commit Configurations
        print("\n2️⃣ Analyzing Pre-commit Configurations...")
        self._analyze_precommit_configs()
        
        # 3. Test Lint Tool Availability
        print("\n3️⃣ Testing Lint Tool Availability...")
        self._test_lint_tools()
        
        # 4. Test GitWiz Functionality
        print("\n4️⃣ Testing GitWiz Functionality...")
        self._test_gitwiz_functionality()
        
        # 5. Test GitHub Workflow
        print("\n5️⃣ Analyzing GitHub Workflow...")
        self._analyze_github_workflow()
        
        # 6. Test Actual Hook Execution
        print("\n6️⃣ Testing Hook Execution...")
        self._test_hook_execution()
        
        # 7. Generate Report
        print("\n7️⃣ Generating Audit Report...")
        self._generate_audit_report()
        
        return self.audit_results
    
    def _test_gitwiz_components(self):
        """Test availability and functionality of GitWiz components."""
        components = {}
        
        # Test GitWiz Enhanced
        try:
            from scripts.gitwiz_enhanced import EnhancedGITWiz
            gitwiz = EnhancedGITWiz(self.repo_path)
            components["enhanced_gitwiz"] = {
                "available": True,
                "class": "EnhancedGITWiz",
                "methods": [m for m in dir(gitwiz) if not m.startswith('_')]
            }
            print("  ✅ GitWiz Enhanced - Available")
        except Exception as e:
            components["enhanced_gitwiz"] = {"available": False, "error": str(e)}
            print(f"  ❌ GitWiz Enhanced - Failed: {e}")
        
        # Test Lint Cleanup Manager
        try:
            from scripts.gitwiz_lint_cleanup_manager import LintCleanupManager
            manager = LintCleanupManager(self.repo_path)
            components["lint_manager"] = {
                "available": True,
                "tools": manager.available_tools
            }
            print("  ✅ Lint Cleanup Manager - Available")
        except Exception as e:
            components["lint_manager"] = {"available": False, "error": str(e)}
            print(f"  ❌ Lint Cleanup Manager - Failed: {e}")
        
        # Test Workflow Orchestrator
        try:
            from scripts.gitwiz_workflow_orchestrator import GITWizWorkflowOrchestrator
            orchestrator = GITWizWorkflowOrchestrator(self.repo_path)
            components["orchestrator"] = {"available": True}
            print("  ✅ Workflow Orchestrator - Available")
        except Exception as e:
            components["orchestrator"] = {"available": False, "error": str(e)}
            print(f"  ❌ Workflow Orchestrator - Failed: {e}")
        
        self.audit_results["components"] = components
    
    def _analyze_precommit_configs(self):
        """Analyze pre-commit configuration files."""
        configs = {}
        
        # Check .pre-commit-config.yaml
        precommit_config = self.repo_path / ".pre-commit-config.yaml"
        if precommit_config.exists():
            try:
                import yaml
                with open(precommit_config) as f:
                    config_data = yaml.safe_load(f)
                configs["pre_commit_config"] = {
                    "exists": True,
                    "repos": len(config_data.get("repos", [])),
                    "hooks": sum(len(repo.get("hooks", [])) for repo in config_data.get("repos", [])),
                    "config": config_data
                }
                print(f"  ✅ .pre-commit-config.yaml - {configs['pre_commit_config']['hooks']} hooks configured")
            except Exception as e:
                configs["pre_commit_config"] = {"exists": True, "error": str(e)}
                print(f"  ❌ .pre-commit-config.yaml - Parse error: {e}")
        else:
            configs["pre_commit_config"] = {"exists": False}
            print("  ⚠️ .pre-commit-config.yaml - Not found")
        
        # Check optimized config
        optimized_config = self.repo_path / ".pre-commit-config-optimized.yaml"
        if optimized_config.exists():
            configs["optimized_config"] = {"exists": True}
            print("  ✅ .pre-commit-config-optimized.yaml - Found")
        else:
            configs["optimized_config"] = {"exists": False}
            print("  ⚠️ .pre-commit-config-optimized.yaml - Not found")
        
        # Check husky
        husky_dir = self.repo_path / ".husky"
        if husky_dir.exists():
            hooks = list(husky_dir.glob("*"))
            configs["husky"] = {"exists": True, "hooks": [h.name for h in hooks]}
            print(f"  ✅ Husky - {len(hooks)} hooks found")
        else:
            configs["husky"] = {"exists": False}
            print("  ⚠️ Husky - Not found")
        
        # Check package.json scripts
        package_json = self.repo_path / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                package_data = json.load(f)
            scripts = package_data.get("scripts", {})
            configs["package_json"] = {
                "exists": True,
                "pre_commit_script": "pre-commit" in scripts,
                "scripts": scripts
            }
            print(f"  ✅ package.json - {'pre-commit' in scripts and '✓' or '✗'} pre-commit script")
        else:
            configs["package_json"] = {"exists": False}
            print("  ⚠️ package.json - Not found")
        
        self.audit_results["configurations"] = configs
    
    def _test_lint_tools(self):
        """Test availability of lint tools."""
        tools = {
            "python": ["flake8", "pylint", "black", "isort", "autopep8", "bandit"],
            "javascript": ["eslint", "prettier"],
            "markdown": ["markdownlint"],
            "generic": ["pre-commit"]
        }
        
        tool_results = {}
        
        for category, tool_list in tools.items():
            tool_results[category] = {}
            for tool in tool_list:
                try:
                    result = subprocess.run([tool, "--version"], 
                                         capture_output=True, text=True, timeout=10)
                    available = result.returncode == 0
                    tool_results[category][tool] = {
                        "available": available,
                        "version": result.stdout.strip() if available else None,
                        "error": result.stderr.strip() if result.stderr else None
                    }
                    status = "✅" if available else "❌"
                    print(f"  {status} {tool} - {'Available' if available else 'Not available'}")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    tool_results[category][tool] = {"available": False, "error": "Not found"}
                    print(f"  ❌ {tool} - Not found")
        
        self.audit_results["lint_tools"] = tool_results
    
    def _test_gitwiz_functionality(self):
        """Test core GitWiz functionality."""
        tests = {}
        
        # Test GitWiz status
        try:
            result = subprocess.run([
                sys.executable, "scripts/gitwiz_integrated_command.py", "status"
            ], capture_output=True, text=True, timeout=30, cwd=self.repo_path)
            
            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                tests["status"] = {"success": True, "data": status_data}
                print("  ✅ GitWiz Status - Working")
            else:
                tests["status"] = {"success": False, "error": result.stderr}
                print(f"  ❌ GitWiz Status - Failed: {result.stderr}")
        except Exception as e:
            tests["status"] = {"success": False, "error": str(e)}
            print(f"  ❌ GitWiz Status - Exception: {e}")
        
        # Test GitWiz quality check
        try:
            result = subprocess.run([
                sys.executable, "scripts/gitwiz_integrated_command.py", 
                "quality-check", "--output", "summary"
            ], capture_output=True, text=True, timeout=60, cwd=self.repo_path)
            
            if result.returncode == 0:
                quality_data = json.loads(result.stdout)
                tests["quality_check"] = {"success": True, "data": quality_data}
                print("  ✅ GitWiz Quality Check - Working")
            else:
                tests["quality_check"] = {"success": False, "error": result.stderr}
                print(f"  ❌ GitWiz Quality Check - Failed: {result.stderr}")
        except Exception as e:
            tests["quality_check"] = {"success": False, "error": str(e)}
            print(f"  ❌ GitWiz Quality Check - Exception: {e}")
        
        self.audit_results["functionality_tests"] = tests
    
    def _analyze_github_workflow(self):
        """Analyze GitHub workflow configuration."""
        workflow_path = self.repo_path / ".github/workflows/gitwiz-quality-gates.yml"
        
        if workflow_path.exists():
            try:
                import yaml
                with open(workflow_path) as f:
                    workflow_data = yaml.safe_load(f)
                
                self.audit_results["github_workflow"] = {
                    "exists": True,
                    "jobs": list(workflow_data.get("jobs", {}).keys()),
                    "triggers": workflow_data.get("on", {}),
                    "config": workflow_data
                }
                print(f"  ✅ GitHub Workflow - {len(workflow_data.get('jobs', {}))} jobs configured")
            except Exception as e:
                self.audit_results["github_workflow"] = {"exists": True, "error": str(e)}
                print(f"  ❌ GitHub Workflow - Parse error: {e}")
        else:
            self.audit_results["github_workflow"] = {"exists": False}
            print("  ⚠️ GitHub Workflow - Not found")
    
    def _test_hook_execution(self):
        """Test actual pre-commit hook execution."""
        hook_tests = {}
        
        # Test pre-commit hook directly
        precommit_hook = self.repo_path / ".husky/pre-commit"
        if precommit_hook.exists():
            try:
                # Create a test file
                test_file = self.repo_path / "test_hook.txt"
                test_file.write_text("Test content for hook execution")
                
                # Stage the file
                subprocess.run(["git", "add", str(test_file)], cwd=self.repo_path, check=True)
                
                # Try to run the hook
                result = subprocess.run([
                    "bash", str(precommit_hook)
                ], capture_output=True, text=True, timeout=30, cwd=self.repo_path)
                
                hook_tests["husky_hook"] = {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr
                }
                
                # Clean up
                subprocess.run(["git", "reset", "HEAD", str(test_file)], cwd=self.repo_path)
                test_file.unlink(missing_ok=True)
                
                status = "✅" if result.returncode == 0 else "❌"
                print(f"  {status} Husky Hook Test - {'Passed' if result.returncode == 0 else 'Failed'}")
                
            except Exception as e:
                hook_tests["husky_hook"] = {"success": False, "error": str(e)}
                print(f"  ❌ Husky Hook Test - Exception: {e}")
        else:
            hook_tests["husky_hook"] = {"success": False, "error": "Hook not found"}
            print("  ⚠️ Husky Hook - Not found")
        
        # Test npm pre-commit script
        try:
            result = subprocess.run([
                "npm", "run", "pre-commit"
            ], capture_output=True, text=True, timeout=30, cwd=self.repo_path)
            
            hook_tests["npm_precommit"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
            status = "✅" if result.returncode == 0 else "❌"
            print(f"  {status} NPM Pre-commit - {'Passed' if result.returncode == 0 else 'Failed'}")
            
        except Exception as e:
            hook_tests["npm_precommit"] = {"success": False, "error": str(e)}
            print(f"  ❌ NPM Pre-commit - Exception: {e}")
        
        self.audit_results["hook_tests"] = hook_tests
    
    def _generate_audit_report(self):
        """Generate comprehensive audit report with issues and recommendations."""
        issues = []
        recommendations = []
        
        # Analyze results and identify issues
        
        # GitWiz Components Issues
        components = self.audit_results.get("components", {})
        if not components.get("enhanced_gitwiz", {}).get("available"):
            issues.append({
                "severity": "HIGH",
                "category": "GitWiz Components",
                "description": "GitWiz Enhanced not available",
                "impact": "Quality gates may not function properly"
            })
            recommendations.append("Fix GitWiz Enhanced import/initialization issues")
        
        # Lint Tools Issues
        lint_tools = self.audit_results.get("lint_tools", {})
        unavailable_tools = []
        for category, tools in lint_tools.items():
            for tool, info in tools.items():
                if not info.get("available"):
                    unavailable_tools.append(tool)
        
        if unavailable_tools:
            issues.append({
                "severity": "MEDIUM",
                "category": "Lint Tools",
                "description": f"Missing lint tools: {', '.join(unavailable_tools)}",
                "impact": "Reduced code quality checking capabilities"
            })
            recommendations.append(f"Install missing lint tools: {', '.join(unavailable_tools)}")
        
        # Configuration Issues
        configs = self.audit_results.get("configurations", {})
        if not configs.get("husky", {}).get("exists"):
            issues.append({
                "severity": "MEDIUM",
                "category": "Pre-commit Setup",
                "description": "Husky not properly configured",
                "impact": "Pre-commit hooks may not execute automatically"
            })
            recommendations.append("Set up Husky for automatic pre-commit hook execution")
        
        # Functionality Issues
        func_tests = self.audit_results.get("functionality_tests", {})
        if not func_tests.get("quality_check", {}).get("success"):
            issues.append({
                "severity": "HIGH",
                "category": "GitWiz Functionality",
                "description": "GitWiz quality check not working",
                "impact": "Quality gates are non-functional"
            })
            recommendations.append("Debug and fix GitWiz quality check functionality")
        
        # Hook Execution Issues
        hook_tests = self.audit_results.get("hook_tests", {})
        if not hook_tests.get("husky_hook", {}).get("success"):
            issues.append({
                "severity": "MEDIUM",
                "category": "Hook Execution",
                "description": "Husky pre-commit hook not executing properly",
                "impact": "Pre-commit validation not happening"
            })
            recommendations.append("Fix Husky pre-commit hook execution")
        
        self.audit_results["issues"] = issues
        self.audit_results["recommendations"] = recommendations
        
        # Print summary
        print(f"\n📊 Audit Summary:")
        print(f"  Issues found: {len(issues)}")
        print(f"  Recommendations: {len(recommendations)}")
        
        # Print critical issues
        critical_issues = [i for i in issues if i["severity"] == "HIGH"]
        if critical_issues:
            print(f"\n🚨 Critical Issues ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"  ❗ {issue['description']}")
        
        # Print top recommendations
        if recommendations:
            print(f"\n💡 Key Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")

def main():
    """Run the comprehensive GitWiz pre-commit audit."""
    auditor = GitWizPrecommitAuditor()
    results = auditor.run_comprehensive_audit()
    
    # Save audit report
    report_path = Path("gitwiz_precommit_audit_report.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Full audit report saved to: {report_path}")
    
    # Return appropriate exit code
    issues = results.get("issues", [])
    critical_issues = [i for i in issues if i["severity"] == "HIGH"]
    
    if critical_issues:
        print(f"\n🚨 Audit completed with {len(critical_issues)} critical issues!")
        return 1
    elif issues:
        print(f"\n⚠️ Audit completed with {len(issues)} non-critical issues.")
        return 0
    else:
        print(f"\n✅ Audit completed successfully - no issues found!")
        return 0

if __name__ == "__main__":
    sys.exit(main())