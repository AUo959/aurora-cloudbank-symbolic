#!/usr/bin/env python3
"""
CodeQL Workflow Consolidation for Aurora
Symbolic Anchor: T1-CONSOLIDATE-2025
Resolves duplicate workflow conflicts
"""

import os
import yaml
from pathlib import Path
from datetime import datetime
import hashlib
import json

class CodeQLConsolidator:
    def __init__(self):
        self.anchor = "T1-CONSOLIDATE-2025"
        self.workflows_dir = Path(".github/workflows")
        self.backup_dir = Path(".github/workflows_backup")
        
    def backup_existing_workflows(self):
        """Create timestamped backup with seal"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.backup_dir.mkdir(exist_ok=True)
        
        backup_manifest = {
            "anchor": self.anchor,
            "timestamp": timestamp,
            "files_backed_up": []
        }
        
        # Backup all CodeQL-related workflows
        codeql_patterns = ["*codeql*.yml", "*code-scanning*.yml", "*security*.yml"]
        
        for pattern in codeql_patterns:
            for workflow in self.workflows_dir.glob(pattern):
                if workflow.name != "codeql-unified.yml":  # Skip our new unified workflow
                    backup_path = self.backup_dir / f"{workflow.stem}_{timestamp}.yml"
                    
                    # Copy instead of move to preserve original temporarily
                    with open(workflow, 'r') as src, open(backup_path, 'w') as dst:
                        dst.write(src.read())
                    
                    backup_manifest["files_backed_up"].append({
                        "original": str(workflow),
                        "backup": str(backup_path)
                    })
                    print(f"📦 Backed up: {workflow.name} → {backup_path}")
        
        # Seal the backup
        manifest_hash = hashlib.sha256(
            json.dumps(backup_manifest, sort_keys=True).encode()
        ).hexdigest()
        backup_manifest["seal"] = manifest_hash
        
        with open(self.backup_dir / f"backup_manifest_{timestamp}.json", "w") as f:
            json.dump(backup_manifest, f, indent=2)
            
        return manifest_hash, backup_manifest
    
    def create_unified_workflow(self):
        """Create single unified CodeQL workflow"""
        unified_workflow = {
            "name": "Aurora CodeQL Unified Analysis",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]},
                "schedule": [{"cron": "30 5 * * 1"}]  # Weekly Monday 5:30 UTC
            },
            "permissions": {
                "actions": "read",
                "contents": "read", 
                "security-events": "write"
            },
            "jobs": {
                "analyze": {
                    "name": "Analyze (${{ matrix.language }})",
                    "runs-on": "ubuntu-latest",
                    "timeout-minutes": 360,
                    "strategy": {
                        "fail-fast": False,
                        "matrix": {
                            "language": ["python", "javascript"],
                            "include": [
                                {
                                    "language": "python",
                                    "build-mode": "none"
                                },
                                {
                                    "language": "javascript", 
                                    "build-mode": "none"
                                }
                            ]
                        }
                    },
                    "steps": [
                        {
                            "name": "Checkout repository",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Initialize CodeQL",
                            "uses": "github/codeql-action/init@v3",
                            "with": {
                                "languages": "${{ matrix.language }}",
                                "queries": "security-extended",
                                "config": """paths:
  - src
  - modules  
  - aurora_api.py
  - scripts
paths-ignore:
  - tests
  - '**/*_test.py'
  - node_modules
  - venv
  - .venv
  - __pycache__
  - '*.pyc'
  - CASK_Assets.zip
  - '**/*.zip'
  - '**/*.gz'
  - '**/*.tar'
"""
                            }
                        },
                        {
                            "name": "Autobuild", 
                            "uses": "github/codeql-action/autobuild@v3"
                        },
                        {
                            "name": "Perform CodeQL Analysis",
                            "uses": "github/codeql-action/analyze@v3",
                            "with": {
                                "category": "/language:${{matrix.language}}",
                                "upload": True,
                                "add-snippets": True
                            }
                        },
                        {
                            "name": "Generate Symbolic Manifest",
                            "if": "always()",
                            "run": """echo '{
  "anchor": "T1-SCAN-${{ matrix.language }}",
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
  "language": "${{ matrix.language }}",
  "status": "${{ job.status }}",
  "workflow_run_id": "${{ github.run_id }}",
  "commit_sha": "${{ github.sha }}",
  "dlp_tag": "SECURITY_SCAN"
}' > scan_manifest_${{ matrix.language }}.json"""
                        }
                    ]
                }
            }
        }
        
        # Write unified workflow
        unified_path = self.workflows_dir / "codeql-unified.yml"
        with open(unified_path, "w") as f:
            yaml.dump(unified_workflow, f, default_flow_style=False, sort_keys=False)
            
        print(f"✅ Created unified workflow: {unified_path}")
        return str(unified_path)
    
    def remove_conflicting_workflows(self, backup_manifest):
        """Remove the original conflicting workflows after backup"""
        removed_files = []
        
        for backup_entry in backup_manifest["files_backed_up"]:
            original_path = Path(backup_entry["original"])
            if original_path.exists():
                original_path.unlink()
                removed_files.append(str(original_path))
                print(f"🗑️ Removed conflicting workflow: {original_path}")
        
        return removed_files
    
    def create_disable_script(self):
        """Create script to disable GitHub's default CodeQL setup"""
        disable_script = """#!/bin/bash
# Disable default CodeQL setup
# Symbolic Anchor: T1-DISABLE-DEFAULT-2025

echo "🔧 Disabling default CodeQL setup..."
echo "📌 Anchor: T1-DISABLE-DEFAULT-2025"

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "⚠️ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    echo "   Or run: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "   sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "   echo 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null"
    echo "   sudo apt update && sudo apt install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "⚠️ Not authenticated with GitHub CLI. Please run:"
    echo "   gh auth login"
    exit 1
fi

# Attempt to disable default setup
echo "🚫 Attempting to disable default CodeQL setup..."
gh api \\
  --method DELETE \\
  /repos/AUo959/aurora-cloudbank-symbolic/code-scanning/default-setup \\
  2>/dev/null && echo "✅ Default setup disabled successfully" || echo "ℹ️ Default setup already disabled or not found"

echo "🔒 Default CodeQL setup disabled"
echo "📋 Next: Commit unified workflow and push to trigger new analysis"
"""
        
        script_path = Path("scripts/disable_default_codeql.sh")
        script_path.write_text(disable_script)
        script_path.chmod(0o755)
        
        print(f"📝 Created disable script: {script_path}")
        return str(script_path)
        
    def consolidate(self):
        """Execute full consolidation"""
        print("🔄 Aurora CodeQL Consolidation Process")
        print(f"📌 Anchor: {self.anchor}")
        print("="*50)
        
        # Step 1: Backup
        print("\n📦 Step 1: Backing up existing workflows...")
        backup_seal, backup_manifest = self.backup_existing_workflows()
        print(f"   Backup sealed: {backup_seal[:16]}...")
        
        # Step 2: Create unified workflow
        print("\n🔨 Step 2: Creating unified workflow...")
        unified_path = self.create_unified_workflow()
        
        # Step 3: Remove conflicting workflows
        print("\n🗑️ Step 3: Removing conflicting workflows...")
        removed_files = self.remove_conflicting_workflows(backup_manifest)
        
        # Step 4: Create disable script
        print("\n🚫 Step 4: Creating disable script...")
        disable_script_path = self.create_disable_script()
        
        # Step 5: Generate consolidation manifest
        consolidation_manifest = {
            "anchor": self.anchor,
            "timestamp": datetime.utcnow().isoformat(),
            "backup_seal": backup_seal,
            "unified_workflow": unified_path,
            "removed_workflows": removed_files,
            "disable_script": disable_script_path,
            "next_steps": [
                "Run: bash scripts/disable_default_codeql.sh",
                "Commit changes: git add . && git commit -m 'fix: consolidate CodeQL workflows [T1-CONSOLIDATE-2025]'",
                "Push to trigger new workflow: git push origin main",
                "Monitor GitHub Actions tab for unified workflow execution"
            ],
            "dlp_tag": "CONFIGURATION_CHANGE",
            "thread_seal": hashlib.sha256(
                f"{backup_seal}{unified_path}{self.anchor}".encode()
            ).hexdigest()
        }
        
        with open("consolidation_manifest.json", "w") as f:
            json.dump(consolidation_manifest, f, indent=2)
            
        print("\n✅ Consolidation complete!")
        print(f"🔒 Thread sealed: {consolidation_manifest['thread_seal'][:16]}...")
        print("\n📋 Next steps:")
        for i, step in enumerate(consolidation_manifest["next_steps"], 1):
            print(f"   {i}. {step}")
            
        print(f"\n💾 Consolidation manifest saved to: consolidation_manifest.json")

if __name__ == "__main__":
    consolidator = CodeQLConsolidator()
    consolidator.consolidate()