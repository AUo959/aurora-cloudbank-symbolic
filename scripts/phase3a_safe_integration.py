#!/usr/bin/env python3
"""
Aurora CloudBank - Phase 3A: Safe Feature Integration

Focuses on the least risky, most valuable integrations from Phase 3 analysis.
Implements graduated integration with comprehensive safety validation.

Author: GitHub Copilot Agent
Created: 2025-09-24
Phase: 3A (Safe Features)
"""

import subprocess
import sys
import json
import os
from datetime import datetime
from pathlib import Path

class Phase3ASafeIntegrator:
    def __init__(self):
        self.workspace_root = Path("/workspaces/aurora-cloudbank-symbolic")
        self.results = {
            "phase": "3A",
            "start_time": datetime.now().isoformat(),
            "integrations": [],
            "status": "initializing"
        }
        
        # Phase 3A candidates (safest first)
        self.safe_candidates = [
            {
                "branch": "copilot/fix-140",
                "type": "copilot_fix",
                "priority": "high",
                "risk": "low",
                "description": "GitHub workflow and configuration cleanup"
            },
            {
                "branch": "copilot/fix-123", 
                "type": "copilot_fix",
                "priority": "high",
                "risk": "medium",
                "description": "Configuration and workflow enhancements"
            },
            {
                "branch": "dependabot/npm_and_yarn/concurrently-9.2.1",
                "type": "dependency",
                "priority": "medium", 
                "risk": "low",
                "description": "NPM dependency update for concurrently package"
            }
        ]

    def run_command(self, command, check_return=True):
        """Execute shell command with error handling"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.workspace_root
            )
            
            if check_return and result.returncode != 0:
                print(f"❌ Command failed: {command}")
                print(f"Error: {result.stderr}")
                return None
                
            return result
        except Exception as e:
            print(f"❌ Exception running command: {command}")
            print(f"Error: {e}")
            return None

    def validate_system_health(self):
        """Pre-integration health check"""
        print("🔍 PHASE 3A: Validating system health...")
        
        # Check git status
        result = self.run_command("git status --porcelain")
        if result and result.stdout.strip():
            print("⚠️  Uncommitted changes detected:")
            print(result.stdout)
            return False
            
        # Run quick test suite
        print("🧪 Running test validation...")
        test_result = self.run_command("python3 -m pytest tests/ -v --tb=short -x", False)
        if not test_result or test_result.returncode != 0:
            print("❌ Tests failing - aborting integration")
            return False
            
        print("✅ System health validated")
        return True

    def analyze_branch_safety(self, branch_name):
        """Detailed safety analysis of a branch"""
        print(f"\n🔍 Analyzing safety: {branch_name}")
        
        analysis = {
            "branch": branch_name,
            "conflicts": False,
            "file_count": 0,
            "test_impact": False,
            "core_files": [],
            "safe_to_integrate": True
        }
        
        # Check for conflicts using merge-tree
        merge_result = self.run_command(f"git merge-tree $(git merge-base main origin/{branch_name}) main origin/{branch_name}", False)
        if merge_result and merge_result.stdout.strip():
            analysis["conflicts"] = True
            analysis["safe_to_integrate"] = False
            print(f"❌ Merge conflicts detected")
            
        # Analyze changed files
        diff_result = self.run_command(f"git diff main..origin/{branch_name} --name-only")
        if diff_result:
            files = diff_result.stdout.strip().split('\n') if diff_result.stdout.strip() else []
            analysis["file_count"] = len(files)
            
            # Check for core file modifications
            core_patterns = [
                'src/core/', 'src/aurora/core/', 'aurora_api.py', 
                'tests/', 'setup.py', 'requirements.txt', 'pyproject.toml'
            ]
            
            for file in files:
                for pattern in core_patterns:
                    if pattern in file:
                        analysis["core_files"].append(file)
                        if 'tests/' in file:
                            analysis["test_impact"] = True
        
        # Risk assessment
        if analysis["file_count"] > 50:
            print(f"⚠️  High file change count: {analysis['file_count']}")
            analysis["safe_to_integrate"] = False
            
        if len(analysis["core_files"]) > 10:
            print(f"⚠️  Many core files affected: {len(analysis['core_files'])}")
            
        print(f"📊 Analysis: {analysis['file_count']} files, {len(analysis['core_files'])} core files")
        return analysis

    def integrate_branch(self, candidate):
        """Safely integrate a single branch"""
        branch_name = candidate["branch"]
        print(f"\n🚀 INTEGRATING: {branch_name}")
        print(f"   Type: {candidate['type']}")
        print(f"   Description: {candidate['description']}")
        
        integration_record = {
            "branch": branch_name,
            "start_time": datetime.now().isoformat(),
            "status": "started",
            "candidate": candidate
        }
        
        try:
            # Safety analysis
            analysis = self.analyze_branch_safety(branch_name)
            integration_record["safety_analysis"] = analysis
            
            if not analysis["safe_to_integrate"]:
                integration_record["status"] = "skipped_unsafe"
                print(f"⏭️  Skipping {branch_name} - safety analysis failed")
                return integration_record
            
            # Create integration branch
            integration_branch = f"phase3a-{branch_name.replace('/', '-')}"
            self.run_command(f"git checkout -b {integration_branch}")
            
            # Perform merge
            print(f"🔄 Merging origin/{branch_name} into {integration_branch}...")
            merge_result = self.run_command(f"git merge origin/{branch_name} --no-ff -m 'Phase 3A: Integrate {branch_name}'", False)
            
            if not merge_result or merge_result.returncode != 0:
                print(f"❌ Merge failed for {branch_name}")
                integration_record["status"] = "merge_failed"
                integration_record["error"] = merge_result.stderr if merge_result else "Unknown merge error"
                
                # Cleanup failed merge
                self.run_command("git merge --abort", False)
                self.run_command("git checkout main", False)
                self.run_command(f"git branch -D {integration_branch}", False)
                return integration_record
            
            # Run tests on integrated branch
            print("🧪 Running validation tests...")
            test_result = self.run_command("python3 -m pytest tests/ -v --tb=short", False)
            
            if not test_result or test_result.returncode != 0:
                print(f"❌ Tests failed after integrating {branch_name}")
                integration_record["status"] = "test_failed"
                integration_record["test_output"] = test_result.stderr if test_result else "Unknown test error"
                
                # Cleanup failed integration
                self.run_command("git checkout main", False)
                self.run_command(f"git branch -D {integration_branch}", False)
                return integration_record
            
            # Merge back to main
            print("✅ Tests passed! Merging to main...")
            self.run_command("git checkout main")
            merge_main_result = self.run_command(f"git merge {integration_branch} --no-ff -m 'Phase 3A: Successfully integrated {branch_name}'")
            
            if not merge_main_result or merge_main_result.returncode != 0:
                print(f"❌ Failed to merge {integration_branch} to main")
                integration_record["status"] = "main_merge_failed"
                return integration_record
            
            # Cleanup integration branch
            self.run_command(f"git branch -d {integration_branch}")
            
            integration_record["status"] = "success"
            integration_record["end_time"] = datetime.now().isoformat()
            print(f"✅ Successfully integrated {branch_name}")
            
        except Exception as e:
            integration_record["status"] = "error"
            integration_record["error"] = str(e)
            print(f"❌ Exception during integration: {e}")
            
            # Ensure we're back on main
            self.run_command("git checkout main", False)
            
        return integration_record

    def run_phase3a_integration(self):
        """Execute Phase 3A safe integration"""
        print("🎯 AURORA CLOUDBANK - PHASE 3A: SAFE FEATURE INTEGRATION")
        print("=" * 70)
        
        if not self.validate_system_health():
            print("❌ System health check failed - aborting Phase 3A")
            return False
        
        self.results["status"] = "running"
        successful_integrations = 0
        
        for candidate in self.safe_candidates:
            print(f"\n{'='*50}")
            integration_result = self.integrate_branch(candidate)
            self.results["integrations"].append(integration_result)
            
            if integration_result["status"] == "success":
                successful_integrations += 1
                print(f"✅ Integration #{successful_integrations} completed")
            else:
                print(f"⚠️  Integration skipped/failed: {integration_result['status']}")
        
        # Final validation
        print(f"\n🎯 PHASE 3A SUMMARY:")
        print(f"   Attempted: {len(self.safe_candidates)}")
        print(f"   Successful: {successful_integrations}")
        
        if successful_integrations > 0:
            print("🧪 Running final test suite...")
            final_test = self.run_command("python3 -m pytest tests/ -v", False)
            
            if final_test and final_test.returncode == 0:
                print("✅ All tests pass after Phase 3A integration!")
                self.results["final_test_status"] = "passed"
            else:
                print("❌ Final tests failed!")
                self.results["final_test_status"] = "failed"
        
        # Save results
        self.results["status"] = "completed"
        self.results["end_time"] = datetime.now().isoformat()
        self.results["successful_count"] = successful_integrations
        
        with open("PHASE3A_INTEGRATION_RESULTS.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: PHASE3A_INTEGRATION_RESULTS.json")
        
        if successful_integrations > 0:
            print("\n🚀 Phase 3A completed successfully!")
            print("   Ready for git push and Phase 3B planning")
            return True
        else:
            print("\n⚠️  No integrations completed in Phase 3A")
            return False

def main():
    integrator = Phase3ASafeIntegrator()
    success = integrator.run_phase3a_integration()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()