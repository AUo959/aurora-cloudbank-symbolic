#!/usr/bin/env python3
"""
Aurora CloudBank Symbolic - Automation Audit Script
Systematically audits all automation systems for failures and errors
"""

import os
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class AutomationAuditor:
    """Comprehensive automation system auditor"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.issues = []
        self.warnings = []
        self.info = []
        
        # Try to determine repository name from git config
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract owner/repo from URL - validate GitHub URL format
                if url.startswith('https://github.com/') or url.startswith('git@github.com:'):
                    parts = url.rstrip('.git').split('/')
                    self.repo_name = f"{parts[-2]}/{parts[-1]}"
                else:
                    self.repo_name = "Unknown Repository"
            else:
                self.repo_name = "Unknown Repository"
        except Exception:
            self.repo_name = "Unknown Repository"

    @staticmethod
    def _normalize_workflow_definition(workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize workflow YAML so the `on` key survives YAML 1.1 parsing."""
        workflow = dict(workflow or {})
        if True in workflow and "on" not in workflow:
            workflow["on"] = workflow.pop(True)
        return workflow

    @staticmethod
    def _job_is_disabled(job_config: Any) -> bool:
        """Return True when a GitHub Actions job is intentionally disabled."""
        if not isinstance(job_config, dict):
            return False
        condition = job_config.get("if")
        if isinstance(condition, bool):
            return condition is False
        if isinstance(condition, str):
            return condition.strip().lower() == "false"
        return False
        
    def audit_workflows(self) -> Dict[str, Any]:
        """Audit GitHub Actions workflows"""
        print("🔍 Auditing GitHub Actions Workflows...")
        workflow_dir = self.repo_root / ".github" / "workflows"
        workflows = []
        workflow_issues = []
        
        if not workflow_dir.exists():
            self.issues.append("GitHub workflows directory not found")
            return {"status": "ERROR", "issues": workflow_issues}
        
        for workflow_file in workflow_dir.glob("*.yml"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow = self._normalize_workflow_definition(yaml.safe_load(f))

                workflow_on = workflow.get("on", {}) if isinstance(workflow, dict) else {}
                workflow_jobs = workflow.get("jobs", {}) if isinstance(workflow, dict) else {}
                disabled_jobs = [
                    job_name for job_name, job_config in workflow_jobs.items() if self._job_is_disabled(job_config)
                ]
                    
                workflow_info = {
                    "name": workflow_file.name,
                    "title": workflow.get("name", "Unknown"),
                    "triggers": list(workflow_on.keys()),
                    "jobs": list(workflow_jobs.keys()),
                    "disabled_jobs": disabled_jobs,
                }
                workflows.append(workflow_info)
                
                # Check for common issues
                if "schedule" in workflow_on:
                    cron = workflow_on["schedule"]
                    workflow_info["scheduled"] = True
                    workflow_info["cron"] = cron
                     
                if "permissions" not in workflow:
                    self.warnings.append(
                        f"⚠️ {workflow_file.name}: No permissions defined"
                    )

                if workflow_jobs and len(disabled_jobs) == len(workflow_jobs):
                    workflow_issues.append({
                        "file": workflow_file.name,
                        "severity": "HIGH",
                        "error": "All jobs are disabled"
                    })
                    self.warnings.append(
                        f"⚠️ {workflow_file.name}: All jobs are disabled"
                    )

                if workflow_file.name == "aurora_agent_runner.yml":
                    missing_triggers = [
                        trigger for trigger in ("schedule", "workflow_dispatch") if trigger not in workflow_on
                    ]
                    if missing_triggers:
                        workflow_issues.append({
                            "file": workflow_file.name,
                            "severity": "HIGH",
                            "error": f"Missing required triggers: {', '.join(missing_triggers)}"
                        })
                        self.warnings.append(
                            f"⚠️ {workflow_file.name}: Missing triggers {', '.join(missing_triggers)}"
                        )

                    aurora_permissions = workflow.get("permissions", {})
                    missing_permissions = [
                        scope for scope in ("contents", "issues", "pull-requests")
                        if aurora_permissions.get(scope) != "write"
                    ]
                    if missing_permissions:
                        workflow_issues.append({
                            "file": workflow_file.name,
                            "severity": "HIGH",
                            "error": f"Missing Aurora permissions: {', '.join(missing_permissions)}"
                        })
                        self.warnings.append(
                            f"⚠️ {workflow_file.name}: Missing write permissions for {', '.join(missing_permissions)}"
                        )

                    aurora_steps = workflow_jobs.get("aurora-agent", {}).get("steps", [])
                    if not any(
                        isinstance(step, dict) and str(step.get("uses", "")).startswith("actions/upload-artifact@")
                        for step in aurora_steps
                    ):
                        workflow_issues.append({
                            "file": workflow_file.name,
                            "severity": "MEDIUM",
                            "error": "Aurora logs are not uploaded as workflow artifacts"
                        })
                        self.warnings.append(
                            f"⚠️ {workflow_file.name}: Aurora logs are not archived"
                        )
                     
            except Exception as e:
                workflow_issues.append({
                    "file": workflow_file.name,
                    "error": str(e)
                })
                self.issues.append(
                    f"❌ {workflow_file.name}: Failed to parse - {e}"
                )
        
        return {
            "status": "OK" if not workflow_issues else "ERROR",
            "total_workflows": len(workflows),
            "workflows": workflows,
            "issues": workflow_issues
        }
    
    def audit_aurora_agent(self) -> Dict[str, Any]:
        """Audit Aurora Agent implementation"""
        print("🤖 Auditing Aurora Agent...")
        agent_file = self.repo_root / ".github" / "agents" / "aurora_agent_final.py"
        issues = []
        
        if not agent_file.exists():
            self.issues.append("❌ Aurora Agent file not found")
            return {"status": "ERROR", "issues": ["File not found"]}
        
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check for infinite loop issue
        if "while True:" in content and "single_run" not in content:
            lines = content.split('\n')
            loop_line = next((i for i, line in enumerate(lines, 1) if 'while True:' in line), None)
            issues.append({
                "severity": "CRITICAL",
                "issue": "Infinite loop detected in agent",
                "description": "Agent uses 'while True:' which blocks in GitHub Actions",
                "line": loop_line
            })
            self.issues.append(
                "❌ Aurora Agent: Infinite loop causes workflow to hang"
            )
        elif "single_run" in content and "while True:" in content:
            self.info.append(
                "✅ Aurora Agent: Fixed - Now supports single-run mode for CI"
            )
        
        # Check for API authentication
        if "YOUR_TOKEN_HERE" in content:
            issues.append({
                "severity": "HIGH",
                "issue": "Placeholder token in code",
                "description": "Token placeholder not replaced with env var properly"
            })
            self.issues.append(
                "❌ Aurora Agent: Token placeholder may cause auth failures"
            )
        elif 'TOKEN = os.getenv("GITHUB_TOKEN", "")' in content:
            self.info.append(
                "✅ Aurora Agent: Token properly handled with environment variable"
            )
        
        # Check log file path handling
        if "logs/" in content and "ensure_log_dir" in content:
            self.info.append("✅ Aurora Agent: Log directory handling present")
        else:
            self.warnings.append(
                "⚠️ Aurora Agent: Log directory handling may be incomplete"
            )
        
        return {
            "status": "ERROR" if any(i["severity"] == "CRITICAL" for i in issues) else "WARNING",
            "issues": issues
        }
    
    def audit_makefile(self) -> Dict[str, Any]:
        """Audit Makefile for issues"""
        print("📝 Auditing Makefile...")
        makefile = self.repo_root / "Makefile"
        issues = []
        
        if not makefile.exists():
            self.issues.append("❌ Makefile not found")
            return {"status": "ERROR", "issues": ["File not found"]}
        
        with open(makefile, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check for duplicate targets
        targets = {}
        for i, line in enumerate(lines, 1):
            if line and not line.startswith('\t') and ':' in line:
                target = line.split(':')[0].strip()
                if target in targets:
                    issues.append({
                        "severity": "MEDIUM",
                        "issue": f"Duplicate target: {target}",
                        "lines": [targets[target], i]
                    })
                    self.warnings.append(
                        f"⚠️ Makefile: Duplicate target '{target}' at lines {targets[target]} and {i}"
                    )
                targets[target] = i
        
        # Check for shell compatibility issues
        if "source " in content:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Using 'source' which is bash-specific",
                "description": "May fail on systems where /bin/sh is not bash"
            })
            self.warnings.append(
                "⚠️ Makefile: Uses 'source' command (bash-specific, may fail with /bin/sh)"
            )
        
        return {
            "status": "WARNING" if issues else "OK",
            "issues": issues
        }
    
    def audit_scripts(self) -> Dict[str, Any]:
        """Audit automation scripts"""
        print("📜 Auditing Scripts...")
        scripts_dir = self.repo_root / "scripts"
        issues = []
        script_count = 0
        
        if not scripts_dir.exists():
            self.warnings.append("⚠️ Scripts directory not found")
            return {"status": "WARNING", "issues": ["Directory not found"]}
        
        # Check for executable permissions
        for script in scripts_dir.glob("*.sh"):
            script_count += 1
            if not os.access(script, os.X_OK):
                self.warnings.append(
                    f"⚠️ {script.name}: Not executable"
                )
        
        # Check for Python scripts
        for script in scripts_dir.glob("*.py"):
            script_count += 1
            try:
                with open(script, 'r') as f:
                    content = f.read()
                    # Check for shebang
                    if not content.startswith("#!"):
                        self.info.append(
                            f"ℹ️ {script.name}: No shebang line"
                        )
            except Exception as e:
                issues.append({
                    "file": script.name,
                    "error": str(e)
                })
        
        return {
            "status": "OK" if not issues else "WARNING",
            "total_scripts": script_count,
            "issues": issues
        }
    
    def check_log_files(self) -> Dict[str, Any]:
        """Check for existing log files and errors"""
        print("📋 Checking Log Files...")
        log_patterns = ["*error*", "*failure*", "*log*"]
        found_logs = []
        
        for pattern in log_patterns:
            for log_file in self.repo_root.rglob(pattern):
                # Exclude common directories
                if any(x in str(log_file) for x in ['.git', 'node_modules', '.venv']):
                    continue
                    
                if log_file.is_file() and log_file.stat().st_size > 0:
                    found_logs.append({
                        "path": str(log_file.relative_to(self.repo_root)),
                        "size": log_file.stat().st_size,
                        "modified": datetime.fromtimestamp(
                            log_file.stat().st_mtime
                        ).isoformat()
                    })
        
        self.info.append(f"ℹ️ Found {len(found_logs)} log files")
        
        return {
            "status": "OK",
            "log_files": found_logs
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        print("\n" + "="*60)
        print("🌟 Aurora CloudBank Symbolic - Automation Audit Report")
        print("="*60 + "\n")
        
        # Run all audits
        workflow_results = self.audit_workflows()
        agent_results = self.audit_aurora_agent()
        makefile_results = self.audit_makefile()
        scripts_results = self.audit_scripts()
        logs_results = self.check_log_files()
        
        # Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "repository": self.repo_name,
            "auditor": "automation_audit.py v1.0",
            "summary": {
                "total_issues": len(self.issues),
                "total_warnings": len(self.warnings),
                "total_info": len(self.info)
            },
            "results": {
                "workflows": workflow_results,
                "aurora_agent": agent_results,
                "makefile": makefile_results,
                "scripts": scripts_results,
                "logs": logs_results
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "info": self.info
        }
        
        # Print summary
        print("\n📊 Summary:")
        print(f"   Critical Issues: {len(self.issues)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Info: {len(self.info)}")
        
        if self.issues:
            print("\n❌ Critical Issues:")
            for issue in self.issues:
                print(f"   {issue}")
        
        if self.warnings:
            print("\n⚠️ Warnings:")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
        
        print("\n" + "="*60)
        
        return report


def main():
    """Main execution"""
    auditor = AutomationAuditor()
    report = auditor.generate_report()
    
    # Save report
    output_file = "automation_audit_report.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Full report saved to: {output_file}")
    print(f"📈 Overall Status: {'✅ PASS' if not report['issues'] else '❌ FAIL'}")
    
    return 0 if not report['issues'] else 1


if __name__ == "__main__":
    exit(main())
