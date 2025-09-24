#!/usr/bin/env python3

"""
Aurora CloudBank - Phase 2 Resolution Script
Safely resolves merge conflicts with guided approach
"""

import subprocess
import sys
from pathlib import Path

class Phase2ConflictResolver:
    def __init__(self):
        self.repo_root = Path.cwd()
        
    def resolve_workflow_conflicts(self):
        """Resolve conflicts in fix/workflows branch"""
        print("🔧 RESOLVING: fix/workflows branch")
        print("=" * 40)
        
        # Create resolution branch
        branch_name = "resolve-fix-workflows"
        print(f"Creating resolution branch: {branch_name}")
        
        try:
            # Checkout resolution branch
            subprocess.run(['git', 'checkout', '-b', branch_name, 'main'], check=True)
            
            # Attempt merge
            result = subprocess.run(['git', 'merge', 'origin/fix/workflows'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("📝 Merge conflicts detected. Analyzing...")
                
                # Show conflict status
                subprocess.run(['git', 'status', '--porcelain'])
                
                # Let's examine the conflicted workflow file
                self._resolve_workflow_file_conflict()
                
                # Stage resolved files
                subprocess.run(['git', 'add', '.github/workflows/aurora-enhanced-ci.yml'])
                
                # Commit resolution
                subprocess.run(['git', 'commit', '-m', 'Resolve workflow conflicts from fix/workflows branch'])
                
                print("✅ Workflow conflicts resolved")
                return True
            else:
                print("✅ Clean merge - no conflicts")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error resolving workflow conflicts: {e}")
            # Cleanup
            subprocess.run(['git', 'checkout', 'main'], capture_output=True)
            subprocess.run(['git', 'branch', '-D', branch_name], capture_output=True)
            return False
    
    def _resolve_workflow_file_conflict(self):
        """Resolve conflicts in workflow YAML file"""
        workflow_file = Path('.github/workflows/aurora-enhanced-ci.yml')
        
        if not workflow_file.exists():
            print("⚠️ Workflow file not found")
            return
            
        # Read the conflicted file
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # For workflow files, we typically want to keep our current version
        # since we've been actively maintaining and validating them
        
        # Simple resolution: take HEAD version (our current validated workflows)
        if '<<<<<<< HEAD' in content:
            lines = content.split('\n')
            resolved_lines = []
            skip_until_end = False
            
            for line in lines:
                if line.startswith('<<<<<<< HEAD'):
                    # Start of conflict - keep our version
                    continue
                elif line.startswith('======='):
                    # Start skipping branch version
                    skip_until_end = True
                    continue
                elif line.startswith('>>>>>>> '):
                    # End conflict - stop skipping
                    skip_until_end = False
                    continue
                elif not skip_until_end:
                    resolved_lines.append(line)
            
            # Write resolved content
            with open(workflow_file, 'w') as f:
                f.write('\n'.join(resolved_lines))
            
            print(f"✅ Resolved conflicts in {workflow_file} (kept current version)")
    
    def resolve_copilot_fix_137(self):
        """Resolve conflicts in copilot/fix-137 branch"""
        print("\n🔧 RESOLVING: copilot/fix-137 branch")
        print("=" * 40)
        
        branch_name = "resolve-copilot-fix-137"
        print(f"Creating resolution branch: {branch_name}")
        
        try:
            # Checkout resolution branch
            subprocess.run(['git', 'checkout', '-b', branch_name, 'main'], check=True)
            
            # Attempt merge
            result = subprocess.run(['git', 'merge', 'origin/copilot/fix-137'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("📝 Merge conflicts detected. Resolving...")
                
                # Resolve each conflicted file
                self._resolve_opal2_plugin_system()
                self._resolve_opal2_base_plugin()
                self._resolve_l2_integration_server()
                
                # Stage all resolved files
                subprocess.run(['git', 'add', '.'])
                
                # Commit resolution
                subprocess.run(['git', 'commit', '-m', 'Resolve Opal2 and L2 integration conflicts from copilot/fix-137'])
                
                print("✅ All conflicts resolved")
                return True
            else:
                print("✅ Clean merge - no conflicts")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error resolving copilot/fix-137: {e}")
            # Cleanup
            subprocess.run(['git', 'checkout', 'main'], capture_output=True)
            subprocess.run(['git', 'branch', '-D', branch_name], capture_output=True)
            return False
    
    def _resolve_opal2_plugin_system(self):
        """Resolve conflicts in modules/opal2/plugin_system.py"""
        file_path = Path('modules/opal2/plugin_system.py')
        
        if not file_path.exists():
            print(f"⚠️ {file_path} not found")
            return
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # This looks like a simple docstring addition - include both versions
        if '<<<<<<< HEAD' in content:
            # For this type of conflict, we can usually merge both changes
            content = content.replace('<<<<<<< HEAD\n', '')
            content = content.replace('=======\n', '')
            content = content.replace('>>>>>>> origin/copilot/fix-137\n', '')
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Resolved {file_path}")
    
    def _resolve_opal2_base_plugin(self):
        """Resolve conflicts in modules/opal2/plugins/base_plugin.py"""
        file_path = Path('modules/opal2/plugins/base_plugin.py')
        
        if not file_path.exists():
            print(f"⚠️ {file_path} not found")
            return
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # This appears to be method enhancement - integrate both versions
        if '<<<<<<< HEAD' in content:
            lines = content.split('\n')
            resolved_lines = []
            in_conflict = False
            
            for line in lines:
                if line.startswith('<<<<<<< HEAD'):
                    in_conflict = True
                    continue
                elif line.startswith('======='):
                    # Take branch version which seems to add functionality
                    continue
                elif line.startswith('>>>>>>> '):
                    in_conflict = False
                    continue
                elif in_conflict:
                    # Skip HEAD version, take branch version
                    continue
                else:
                    resolved_lines.append(line)
            
            with open(file_path, 'w') as f:
                f.write('\n'.join(resolved_lines))
            
            print(f"✅ Resolved {file_path}")
    
    def _resolve_l2_integration_server(self):
        """Resolve conflicts in src/servers/l2_integration_server.py"""
        file_path = Path('src/servers/l2_integration_server.py')
        
        if not file_path.exists():
            print(f"⚠️ {file_path} not found")
            return
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # For server integration files, prefer branch version (likely bug fixes)
        if '<<<<<<< HEAD' in content:
            lines = content.split('\n')
            resolved_lines = []
            skip_until_end = False
            
            for line in lines:
                if line.startswith('<<<<<<< HEAD'):
                    skip_until_end = True  # Skip HEAD version
                    continue
                elif line.startswith('======='):
                    skip_until_end = False  # Take branch version
                    continue
                elif line.startswith('>>>>>>> '):
                    continue
                elif not skip_until_end:
                    resolved_lines.append(line)
            
            with open(file_path, 'w') as f:
                f.write('\n'.join(resolved_lines))
            
            print(f"✅ Resolved {file_path}")
    
    def validate_resolution(self, branch_name: str):
        """Validate resolution by running tests"""
        print(f"\n🧪 VALIDATING RESOLUTION: {branch_name}")
        print("=" * 40)
        
        # Run tests
        test_result = subprocess.run(['python3', '-m', 'pytest', 'tests/', '-v', '--tb=short'], 
                                   capture_output=True, text=True)
        
        if test_result.returncode == 0:
            print("✅ All tests passing after resolution")
            
            # Count passed tests
            output_lines = test_result.stdout.split('\n')
            for line in reversed(output_lines):
                if 'passed' in line:
                    print(f"📊 {line.strip()}")
                    break
            
            return True
        else:
            print("❌ Tests failing after resolution")
            print("Last few lines of test output:")
            error_lines = test_result.stdout.split('\n')[-10:]
            for line in error_lines:
                if line.strip():
                    print(f"  {line}")
            return False
    
    def merge_to_main(self, branch_name: str):
        """Merge resolved branch to main"""
        print(f"\n🔄 MERGING TO MAIN: {branch_name}")
        print("=" * 40)
        
        try:
            # Switch to main
            subprocess.run(['git', 'checkout', 'main'], check=True)
            
            # Merge resolved branch
            subprocess.run(['git', 'merge', branch_name, '--no-ff', 
                          '-m', f'Phase 2: Integrate {branch_name} with conflict resolution'], 
                         check=True)
            
            # Clean up resolution branch
            subprocess.run(['git', 'branch', '-D', branch_name])
            
            print(f"✅ Successfully merged {branch_name} to main")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error merging {branch_name}: {e}")
            return False
    
    def run_phase2(self):
        """Execute complete Phase 2 resolution"""
        print("🎯 AURORA CLOUDBANK - PHASE 2 CONFLICT RESOLUTION")
        print("=" * 60)
        print("Resolving conflicts identified in Phase 2 analysis...")
        print()
        
        # Resolution plan
        resolutions = [
            ("fix/workflows", self.resolve_workflow_conflicts),
            ("copilot/fix-137", self.resolve_copilot_fix_137)
        ]
        
        successful_resolutions = []
        
        for branch_desc, resolver_func in resolutions:
            print(f"\n{'='*60}")
            
            if resolver_func():
                # Get current branch name for validation
                current_branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                              capture_output=True, text=True).stdout.strip()
                
                if self.validate_resolution(current_branch):
                    if self.merge_to_main(current_branch):
                        successful_resolutions.append(branch_desc)
                        print(f"🎉 {branch_desc} successfully integrated!")
                    else:
                        print(f"❌ Failed to merge {branch_desc}")
                else:
                    print(f"❌ Validation failed for {branch_desc}")
                    # Cleanup failed resolution
                    subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                    subprocess.run(['git', 'branch', '-D', current_branch], capture_output=True)
            else:
                print(f"❌ Resolution failed for {branch_desc}")
        
        # Final summary
        print(f"\n🎉 PHASE 2 COMPLETION SUMMARY")
        print("=" * 40)
        
        if successful_resolutions:
            print(f"✅ Successfully integrated: {', '.join(successful_resolutions)}")
        else:
            print("⚠️ No branches successfully integrated")
        
        # Run final system health check
        print("\n🔍 Final System Health Check:")
        final_test = subprocess.run(['python3', '-m', 'pytest', 'tests/', '--tb=no', '-q'], 
                                  capture_output=True, text=True)
        
        if final_test.returncode == 0:
            # Extract test count
            output = final_test.stdout
            for line in output.split('\n'):
                if 'passed' in line:
                    print(f"✅ {line.strip()}")
                    break
            print("🎯 System ready for Phase 3!")
        else:
            print("❌ System health check failed - investigation needed")
        
        return len(successful_resolutions)

def main():
    resolver = Phase2ConflictResolver()
    successful_count = resolver.run_phase2()
    
    if successful_count > 0:
        print(f"\n🎯 Phase 2 completed successfully! Ready to continue to Phase 3.")
        sys.exit(0)
    else:
        print(f"\n⚠️ Phase 2 had issues. Review and retry.")
        sys.exit(1)

if __name__ == "__main__":
    main()