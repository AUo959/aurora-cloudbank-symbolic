#!/usr/bin/env python3
"""
Aurora CodeQL Diagnostic & Resolution Module
Symbolic Anchor: T1-DIAG-2025
Team: Aurora Core
Version: 1.0.0
Entropy State: Monitoring Active
"""

import json
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("⚠️ PyYAML not available, using basic YAML parsing")
    yaml = None

class CodeQLSymbolicDiagnostic:
    """
    Diagnostic module for CodeQL issues with symbolic anchor tracking
    and entropy-state awareness for Aurora CloudBank.
    """
    
    def __init__(self):
        self.anchor_seed = "EOS_SEED_ORION"
        self.diagnostic_tag = "T1-DIAG-2025"
        self.entropy_state = {"level": "nominal", "drift": 0.0}
        self.sealed_states = []
        self.diagnostic_manifest = {
            "anchor": self.diagnostic_tag,
            "seed": self.anchor_seed,
            "timestamp": datetime.utcnow().isoformat(),
            "team": "Aurora Core",
            "version": "1.0.0",
            "dlp_tag": "INTERNAL_DIAGNOSTIC"
        }
        
    def seal_diagnostic_state(self, state_data: Dict) -> str:
        """
        Seal current diagnostic state with SHA256
        Returns: Hash of sealed state
        """
        state_json = json.dumps(state_data, sort_keys=True)
        state_hash = hashlib.sha256(state_json.encode()).hexdigest()
        
        sealed_state = {
            "hash": state_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "anchor": self.diagnostic_tag,
            "data": state_data
        }
        
        self.sealed_states.append(sealed_state)
        return state_hash
    
    def diagnose_duplicate_workflows(self) -> str:
        """
        Identify and diagnose duplicate workflow configurations
        Symbolic Reference: SRB-WORKFLOW-001
        """
        workflows_path = Path(".github/workflows")
        codeql_workflows = []
        
        if workflows_path.exists():
            for workflow_file in workflows_path.glob("*codeql*.yml"):
                try:
                    with open(workflow_file, 'r') as f:
                        content = f.read()
                        workflow_data = {"name": "Unknown", "on": {}}
                        
                        if yaml:
                            workflow_data = yaml.safe_load(content)
                        else:
                            # Basic name extraction without YAML
                            for line in content.split('\n'):
                                if line.strip().startswith('name:'):
                                    workflow_data["name"] = line.split(':', 1)[1].strip().strip('"\'')
                                    break
                        
                        codeql_workflows.append({
                            "file": str(workflow_file),
                            "name": workflow_data.get("name", "Unknown"),
                            "triggers": workflow_data.get("on", {}),
                            "anchor_tag": f"WF-{workflow_file.stem.upper()}"
                        })
                except Exception as e:
                    print(f"⚠️ Error parsing {workflow_file}: {e}")
        
        # Also check for generic workflow files that might contain CodeQL
        for workflow_file in workflows_path.glob("*.yml"):
            if "codeql" not in workflow_file.name.lower():
                try:
                    with open(workflow_file, 'r') as f:
                        content = f.read()
                        if "codeql" in content.lower() or "code-scanning" in content.lower():
                            workflow_data = {"name": "Unknown", "on": {}}
                            
                            if yaml:
                                workflow_data = yaml.safe_load(content)
                            else:
                                # Basic name extraction
                                for line in content.split('\n'):
                                    if line.strip().startswith('name:'):
                                        workflow_data["name"] = line.split(':', 1)[1].strip().strip('"\'')
                                        break
                                        
                            codeql_workflows.append({
                                "file": str(workflow_file),
                                "name": workflow_data.get("name", "Unknown"),
                                "triggers": workflow_data.get("on", {}),
                                "anchor_tag": f"WF-{workflow_file.stem.upper()}",
                                "type": "EMBEDDED_CODEQL"
                            })
                except Exception as e:
                    continue
        
        # Detect conflicts
        conflicts = []
        if len(codeql_workflows) > 1:
            conflicts.append({
                "type": "DUPLICATE_WORKFLOWS",
                "severity": "HIGH",
                "count": len(codeql_workflows),
                "resolution": "Consolidate to single workflow",
                "symbolic_ref": "CONFLICT-WF-001"
            })
            
        diagnostic_result = {
            "workflows_found": len(codeql_workflows),
            "workflows": codeql_workflows,
            "conflicts": conflicts,
            "entropy_drift": 0.15 * len(conflicts)  # Each conflict increases entropy
        }
        
        # Update entropy state
        self.entropy_state["drift"] += diagnostic_result["entropy_drift"]
        
        return self.seal_diagnostic_state(diagnostic_result)
    
    def analyze_scan_failures(self) -> Dict:
        """
        Analyze why scans are completing but showing warnings
        Symbolic Reference: SRB-SCAN-002
        """
        common_issues = []
        
        # Check for common Python issues
        python_checks = [
            ("yaml.load without Loader", "find . -name '*.py' -exec grep -l 'yaml.load(' {} \\;", "HIGH"),
            ("Hardcoded secrets", "find . -name '*.py' -exec grep -l -E '(password|token|secret)\\s*=\\s*[\"\\'][^\"\\']+[\"\\']' {} \\;", "CRITICAL"),
            ("SQL injection risks", "find . -name '*.py' -exec grep -l '\\.execute.*%' {} \\;", "HIGH"),
            ("Subprocess shell=True", "find . -name '*.py' -exec grep -l 'shell=True' {} \\;", "MEDIUM"),
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
            ("Eval usage", "find . -name '*.py' -exec grep -l 'eval(' {} \\;", "HIGH"),
        # CRITICAL SECURITY: exec() usage detected - high code injection risk
            ("Exec usage", "find . -name '*.py' -exec grep -l 'exec(' {} \\;", "HIGH"),
        ]
        
        for issue_name, command, severity in python_checks:
            try:
                # SECURITY FIX: Replace shell=True with secure array-based command execution
                import shlex
                command_args = shlex.split(command)
                result = subprocess.run(command_args, capture_output=True, text=True, shell=False)
                if result.stdout.strip():
                    files = result.stdout.strip().split('\n')
                    occurrences = len(files)
                    common_issues.append({
                        "issue": issue_name,
                        "severity": severity,
                        "occurrences": occurrences,
                        "anchor_ref": f"ISSUE-{issue_name.replace(' ', '_').upper()}",
                        "files_affected": files[:5]  # First 5 files
                    })
            except Exception as e:
                print(f"Error checking {issue_name}: {e}")
        
        return {
            "scan_issues": common_issues,
            "total_issues": sum(i["occurrences"] for i in common_issues),
            "critical_count": sum(1 for i in common_issues if i["severity"] == "CRITICAL"),
            "entropy_impact": sum(0.1 for i in common_issues) 
        }
    
    def generate_resolution_manifest(self) -> Dict:
        """
        Generate a complete resolution manifest with symbolic anchors
        """
        duplicate_hash = self.diagnose_duplicate_workflows()
        scan_analysis = self.analyze_scan_failures()
        
        resolution_manifest = {
            "manifest_version": "1.0.0",
            "anchor_seed": self.anchor_seed,
            "diagnostic_tag": self.diagnostic_tag,
            "timestamp": datetime.utcnow().isoformat(),
            "entropy_state": self.entropy_state,
            "diagnostics": {
                "duplicate_workflows_hash": duplicate_hash,
                "scan_failures": scan_analysis
            },
            "recommended_actions": [
                {
                    "priority": 1,
                    "action": "CONSOLIDATE_WORKFLOWS",
                    "anchor": "ACTION-001",
                    "command": "python3 scripts/consolidate_codeql.py"
                },
                {
                    "priority": 2,
                    "action": "FIX_SECURITY_ISSUES",
                    "anchor": "ACTION-002", 
                    "command": "python3 scripts/fix_codeql_issues.py"
                },
                {
                    "priority": 3,
                    "action": "REMOVE_DEFAULT_SETUP",
                    "anchor": "ACTION-003",
                    "command": "bash scripts/disable_default_codeql.sh"
                }
            ],
            "dlp_classification": "INTERNAL_USE",
            "team": "Aurora Core",
            "thread_seal": hashlib.sha256(
                json.dumps(self.sealed_states, sort_keys=True).encode()
            ).hexdigest()
        }
        
        # Save manifest
        with open("codeql_diagnostic_manifest.json", "w") as f:
            json.dump(resolution_manifest, f, indent=2)
            
        return resolution_manifest
    
    def run_full_diagnostic(self):
        """
        Execute complete diagnostic with traceable output
        """
        print("🔬 Aurora CodeQL Diagnostic Module")
        print(f"📌 Anchor: {self.diagnostic_tag}")
        print(f"🌱 Seed: {self.anchor_seed}")
        print("="*50)
        
        manifest = self.generate_resolution_manifest()
        
        print("\n📊 Diagnostic Results:")
        print(f"  Entropy State: {self.entropy_state}")
        print(f"  Thread Seal: {manifest['thread_seal'][:16]}...")
        
        print(f"\n🔍 Workflow Analysis:")
        sealed_state = None
        for state in self.sealed_states:
            if 'workflows_found' in state['data']:
                sealed_state = state['data']
                break
                
        if sealed_state:
            print(f"  Workflows Found: {sealed_state['workflows_found']}")
            for workflow in sealed_state['workflows']:
                print(f"    - {workflow['name']} ({workflow['file']})")
            
            if sealed_state['conflicts']:
                print(f"  ⚠️ Conflicts: {len(sealed_state['conflicts'])}")
                for conflict in sealed_state['conflicts']:
                    print(f"    - {conflict['type']}: {conflict['resolution']}")
        
        print("\n⚠️ Security Issues Found:")
        scan_issues = manifest["diagnostics"]["scan_failures"]["scan_issues"]
        if scan_issues:
            for issue in scan_issues:
                print(f"  - {issue['issue']}: {issue['occurrences']} occurrences [{issue['severity']}]")
        else:
            print("  ✅ No critical security patterns detected")
        
        print("\n✅ Recommended Actions:")
        for action in manifest["recommended_actions"]:
            print(f"  {action['priority']}. {action['action']} (Anchor: {action['anchor']})")
            print(f"     Command: {action['command']}")
        
        print(f"\n💾 Manifest saved to: codeql_diagnostic_manifest.json")
        print(f"🔒 Diagnostic sealed with hash: {manifest['thread_seal'][:32]}...")

if __name__ == "__main__":
    diagnostic = CodeQLSymbolicDiagnostic()
    diagnostic.run_full_diagnostic()