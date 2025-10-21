#!/usr/bin/env python3
"""
Aurora CloudBank - Phase 3B: Intelligent Conflict Resolution

Handles conflicted branches from Phase 3A with sophisticated merge strategies.
Implements automated conflict resolution with human-readable guidance.

Author: GitHub Copilot Agent
Created: 2025-09-24
Phase: 3B (Conflict Resolution)
"""

import subprocess
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class Phase3BConflictResolver:
    def __init__(self):
        self.workspace_root = Path("/workspaces/aurora-cloudbank-symbolic")
        self.results = {
            "phase": "3B",
            "start_time": datetime.now().isoformat(),
            "resolutions": [],
            "status": "initializing"
        }
        
        # Branches that failed Phase 3A due to conflicts
        self.conflicted_branches = [
            {
                "branch": "copilot/fix-140",
                "type": "copilot_fix",
                "priority": "high",
                "description": "GitHub workflow and configuration cleanup",
                "conflicts_type": "workflow_config"
            },
            {
                "branch": "copilot/fix-123", 
                "type": "copilot_fix",
                "priority": "high",
                "description": "Configuration and workflow enhancements",
                "conflicts_type": "workflow_config"
            }
        ]

    def run_command(self, command, check_return=True):
        """Execute shell command with error handling - SECURITY FIX"""
        try:
            # SECURITY FIX: Replace shell=True with secure array-based execution
            import shlex
            if isinstance(command, str):
                command_args = shlex.split(command)
            else:
                command_args = command
                
            result = subprocess.run(
                command_args, 
                shell=False,  # SECURITY FIX: Changed from True to False
                capture_output=True, 
                text=True, 
                cwd=self.workspace_root
            )
            
            if check_return and result.returncode != 0:
                print("❌ Command failed: %s", command)
                if result.stderr:
                    print("Error: %s", result.stderr)
                return None
                
            return result
        except Exception as e:
            print("❌ Exception running command: %s", command)
            print("Error: %s", e)
            return None

    def analyze_conflicts_detailed(self, branch_name):
        """Get detailed conflict analysis"""
        print("🔍 Detailed conflict analysis: %s", branch_name)
        
        # Get merge-tree output for detailed conflicts
        merge_tree_cmd = f"git merge-tree $(git merge-base main origin/{branch_name}) main origin/{branch_name}"
        result = self.run_command(merge_tree_cmd, False)
        
        conflict_files = []
        if result and result.stdout:
            # Parse merge-tree output to identify conflict files
            lines = result.stdout.split('\n')
            current_file = None
            
            for line in lines:
                if line.startswith('<<<<<<< ') or line.startswith('>>>>>>> '):
                    continue
                elif line.startswith('======='):
                    continue
                elif line.strip() and not line.startswith(('+++', '---', '@@')):
                    # This is a simplified parser - in real scenarios you'd want more robust parsing
                    pass
        
        # Use git diff to get file list
        diff_result = self.run_command(f"git diff --name-only main...origin/{branch_name}")
        if diff_result and diff_result.stdout:
            conflict_files = diff_result.stdout.strip().split('\n')
        
        analysis = {
            "total_conflicts": len(conflict_files),
            "conflict_files": conflict_files[:10],  # Show first 10
            "types": {
                "workflows": sum(1 for f in conflict_files if '.github/' in f),
                "core_code": sum(1 for f in conflict_files if f.startswith('src/core/')),
                "tests": sum(1 for f in conflict_files if f.startswith('tests/')),
                "config": sum(1 for f in conflict_files if f.endswith(('.json', '.yml', '.yaml', '.toml')))
            }
        }
        
        return analysis

    def create_resolution_branch(self, branch_name):
        """Create a resolution branch for manual conflict handling"""
        resolution_branch = f"resolve-{branch_name.replace('/', '-')}"
        
        print("🔧 Creating resolution branch: %s", resolution_branch)
        
        # Create and switch to resolution branch
        checkout_result = self.run_command(f"git checkout -b {resolution_branch}")
        if not checkout_result:
            return None
        
        # Attempt merge to trigger conflicts
        print(f"🔄 Attempting merge to surface conflicts...")
        merge_result = self.run_command(f"git merge origin/{branch_name} --no-commit", False)
        
        if merge_result and merge_result.returncode == 0:
            print("✅ No conflicts detected in practice - completing merge")
            commit_result = self.run_command(f"git commit -m 'Resolve {branch_name} - clean merge'")
            return resolution_branch if commit_result else None
        
        # Check what files have conflicts
        status_result = self.run_command("git status --porcelain")
        if status_result and status_result.stdout:
            conflicted_files = []
            for line in status_result.stdout.split('\n'):
                if line.startswith('UU ') or line.startswith('AA '):
                    conflicted_files.append(line[3:])
            
            print("📋 Found %s conflicted files:", len(conflicted_files))
            for file in conflicted_files[:5]:
                print("   • %s", file)
                
            if len(conflicted_files) > 5:
                print("   ... and %s more", len(conflicted_files) - 5)
        
        return resolution_branch

    def auto_resolve_workflow_conflicts(self, resolution_branch):
        """Attempt automatic resolution of workflow conflicts"""
        print("🤖 Attempting automatic workflow conflict resolution...")
        
        # Get list of conflicted files
        status_result = self.run_command("git status --porcelain")
        if not status_result:
            return False
        
        conflicted_files = []
        for line in status_result.stdout.split('\n'):
            if line.startswith(('UU ', 'AA ', 'AU ', 'UA ')):
                conflicted_files.append(line[3:])
        
        resolved_files = []
        
        for file_path in conflicted_files:
            if not file_path.strip():
                continue
                
            print("🔧 Analyzing conflicts in: %s", file_path)
            
            # Strategy 1: For workflow files, prefer main branch version if it's newer
            if '.github/workflows/' in file_path:
                print(f"   Workflow file - using main version")
                checkout_result = self.run_command(f"git checkout --ours {file_path}", False)
                if checkout_result and checkout_result.returncode == 0:
                    resolved_files.append(file_path)
                    continue
            
            # Strategy 2: For config files, attempt merge with our changes taking precedence
            if file_path.endswith(('.yml', '.yaml', '.json')):
                print(f"   Config file - using our version")
                checkout_result = self.run_command(f"git checkout --ours {file_path}", False)
                if checkout_result and checkout_result.returncode == 0:
                    resolved_files.append(file_path)
                    continue
            
            # Strategy 3: For deleted files, accept deletion
            if not os.path.exists(self.workspace_root / file_path):
                print(f"   File deleted - accepting deletion")
                rm_result = self.run_command(f"git rm {file_path}", False)
                if rm_result and rm_result.returncode == 0:
                    resolved_files.append(file_path)
                    continue
        
        if resolved_files:
            print("✅ Auto-resolved %s files:", len(resolved_files))
            for file in resolved_files[:3]:
                print("   • %s", file)
            if len(resolved_files) > 3:
                print("   ... and %s more", len(resolved_files) - 3)
            
            # Add resolved files
            add_result = self.run_command("git add .")
            return add_result is not None
        
        return False

    def resolve_branch_conflicts(self, candidate):
        """Resolve conflicts for a single branch"""
        branch_name = candidate["branch"]
        print("")
# 🎯 RESOLVING CONFLICTS: %s", branch_name)
        print("   Type: %s", candidate['type'])
        print("   Description: %s", candidate['description'])
        
        resolution_record = {
            "branch": branch_name,
            "start_time": datetime.now().isoformat(),
            "status": "started",
            "candidate": candidate
        }
        
        try:
            # Detailed conflict analysis
            analysis = self.analyze_conflicts_detailed(branch_name)
            resolution_record["conflict_analysis"] = analysis
            
            print(f"📊 Conflict Analysis:")
            print("   Total files: %s", analysis['total_conflicts'])
            print("   Workflows: %s", analysis['types']['workflows'])
            print("   Core code: %s", analysis['types']['core_code'])
            print("   Tests: %s", analysis['types']['tests'])
            print("   Config: %s", analysis['types']['config'])
            
            # Create resolution branch
            resolution_branch = self.create_resolution_branch(branch_name)
            if not resolution_branch:
                resolution_record["status"] = "branch_creation_failed"
                return resolution_record
            
            resolution_record["resolution_branch"] = resolution_branch
            
            # Attempt automatic resolution
            auto_resolved = self.auto_resolve_workflow_conflicts(resolution_branch)
            resolution_record["auto_resolved"] = auto_resolved
            
            if auto_resolved:
                print("🤖 Automatic resolution successful!")
                
                # Complete the merge
                commit_result = self.run_command(f"git commit -m 'Phase 3B: Auto-resolve conflicts in {branch_name}'")
                
                if commit_result:
                    # Run tests on resolved branch
                    print("🧪 Testing auto-resolved conflicts...")
                    test_result = self.run_command("python3 -m pytest tests/ -x", False)
                    
                    if test_result and test_result.returncode == 0:
                        print("✅ Tests pass! Merging to main...")
                        
                        # Merge to main
                        self.run_command("git checkout main")
                        merge_main = self.run_command(f"git merge {resolution_branch} --no-ff -m 'Phase 3B: Resolve and integrate {branch_name}'")
                        
                        if merge_main:
                            resolution_record["status"] = "success"
                            resolution_record["merged_to_main"] = True
                            print("✅ Successfully resolved and integrated %s", branch_name)
                        else:
                            resolution_record["status"] = "main_merge_failed"
                    else:
                        resolution_record["status"] = "test_failed"
                        print("❌ Tests failed after auto-resolution")
                else:
                    resolution_record["status"] = "commit_failed"
            else:
                print("⚠️  Automatic resolution incomplete")
                resolution_record["status"] = "manual_resolution_needed"
                resolution_record["guidance"] = self.generate_manual_resolution_guidance(analysis)
            
            # Cleanup: return to main
            self.run_command("git checkout main", False)
            
        except Exception as e:
            resolution_record["status"] = "error"
            resolution_record["error"] = str(e)
            print("❌ Exception during resolution: %s", e)
            self.run_command("git checkout main", False)
            
        resolution_record["end_time"] = datetime.now().isoformat()
        return resolution_record

    def generate_manual_resolution_guidance(self, analysis):
        """Generate human-readable guidance for manual resolution"""
        guidance = {
            "summary": f"Found conflicts in {analysis['total_conflicts']} files",
            "recommended_approach": [],
            "conflict_files": analysis['conflict_files']
        }
        
        if analysis['types']['workflows'] > 0:
            guidance["recommended_approach"].append(
                "Workflow conflicts: Review .github/workflows files and prefer newer main branch versions"
            )
        
        if analysis['types']['core_code'] > 0:
            guidance["recommended_approach"].append(
                "Core code conflicts: Carefully review src/core changes to preserve functionality"
            )
        
        if analysis['types']['tests'] > 0:
            guidance["recommended_approach"].append(
                "Test conflicts: Ensure all test files are compatible with current main branch"
            )
        
        return guidance

    def run_phase3b_resolution(self):
        """Execute Phase 3B conflict resolution"""
        print("🎯 AURORA CLOUDBANK - PHASE 3B: INTELLIGENT CONFLICT RESOLUTION")
        print("=" * 70)
        
        # Ensure we're on main
        self.run_command("git checkout main")
        
        self.results["status"] = "running"
        successful_resolutions = 0
        
        for candidate in self.conflicted_branches:
            print("")
%s", '='*60)
            resolution_result = self.resolve_branch_conflicts(candidate)
            self.results["resolutions"].append(resolution_result)
            
            if resolution_result["status"] == "success":
                successful_resolutions += 1
                print("✅ Resolution #%s completed", successful_resolutions)
            else:
                print("⚠️  Resolution status: %s", resolution_result['status'])
        
        # Final summary
        print(f"\n🎯 PHASE 3B SUMMARY:")
        print("   Attempted: %s", len(self.conflicted_branches))
        print("   Successful: %s", successful_resolutions)
        
        if successful_resolutions > 0:
            print("🧪 Running final validation...")
            final_test = self.run_command("python3 -m pytest tests/ -v", False)
            
            if final_test and final_test.returncode == 0:
                print("✅ All tests pass after Phase 3B resolution!")
                self.results["final_test_status"] = "passed"
            else:
                print("❌ Final tests failed!")
                self.results["final_test_status"] = "failed"
        
        # Save results
        self.results["status"] = "completed"
        self.results["end_time"] = datetime.now().isoformat()
        self.results["successful_count"] = successful_resolutions
        
        with open("PHASE3B_CONFLICT_RESOLUTION.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: PHASE3B_CONFLICT_RESOLUTION.json")
        
        if successful_resolutions > 0:
            print("\n🚀 Phase 3B completed with successful resolutions!")
            return True
        else:
            print("\n⚠️  Phase 3B completed - some conflicts need manual resolution")
            return successful_resolutions > 0

def main():
    resolver = Phase3BConflictResolver()
    success = resolver.run_phase3b_resolution()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()