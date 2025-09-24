#!/usr/bin/env python3

"""
Aurora CloudBank - Phase 2 Conflict Analysis & Resolution
Analyzes merge conflicts and prepares safe resolution strategies
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile
import shutil

class Phase2ConflictAnalyzer:
    def __init__(self):
        self.repo_root = Path.cwd()
        
    def analyze_branch_conflicts(self, branch: str) -> Dict:
        """Analyze merge conflicts for a specific branch"""
        print(f"🔍 Analyzing conflicts for branch: {branch}")
        print("=" * 50)
        
        # Create temporary branch for analysis
        temp_branch = f"conflict-analysis-{branch.replace('/', '-')}"
        
        try:
            # Create analysis branch
            subprocess.run(['git', 'checkout', '-b', temp_branch, 'main'], 
                         capture_output=True, check=True)
            
            # Attempt merge to identify conflicts
            result = subprocess.run(['git', 'merge', f'origin/{branch}', '--no-commit'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Clean merge
                subprocess.run(['git', 'reset', '--hard', 'HEAD'], capture_output=True)
                subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                subprocess.run(['git', 'branch', '-D', temp_branch], capture_output=True)
                
                return {
                    'status': 'clean',
                    'conflicts': [],
                    'files_changed': self._get_changed_files(branch),
                    'recommendation': 'Safe to merge'
                }
            else:
                # Get conflict details
                conflicts = self._analyze_conflicts()
                
                # Reset and cleanup
                subprocess.run(['git', 'merge', '--abort'], capture_output=True)
                subprocess.run(['git', 'checkout', 'main'], capture_output=True)
                subprocess.run(['git', 'branch', '-D', temp_branch], capture_output=True)
                
                return {
                    'status': 'conflicts',
                    'conflicts': conflicts,
                    'files_changed': self._get_changed_files(branch),
                    'recommendation': 'Requires manual resolution'
                }
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error analyzing branch {branch}: {e}")
            # Cleanup on error
            subprocess.run(['git', 'checkout', 'main'], capture_output=True)
            subprocess.run(['git', 'branch', '-D', temp_branch], capture_output=True)  
            return {
                'status': 'error',
                'error': str(e),
                'recommendation': 'Investigation required'
            }
    
    def _analyze_conflicts(self) -> List[Dict]:
        """Analyze current merge conflicts"""
        try:
            # Get list of conflicted files
            result = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], 
                                  capture_output=True, text=True)
            
            conflicted_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            conflicts = []
            for file_path in conflicted_files:
                if not file_path:
                    continue
                    
                conflict_info = self._analyze_file_conflict(file_path)
                conflicts.append(conflict_info)
            
            return conflicts
            
        except Exception as e:
            print(f"Error analyzing conflicts: {e}")
            return []
    
    def _analyze_file_conflict(self, file_path: str) -> Dict:
        """Analyze conflicts in a specific file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Count conflict markers
            conflict_blocks = content.count('<<<<<<< HEAD')
            
            # Identify conflict types
            conflict_lines = []
            lines = content.split('\n')
            in_conflict = False
            current_conflict = []
            
            for i, line in enumerate(lines):
                if line.startswith('<<<<<<< HEAD'):
                    in_conflict = True
                    current_conflict = {'start': i, 'head_lines': [], 'branch_lines': []}
                elif line.startswith('=======') and in_conflict:
                    current_conflict['separator'] = i
                elif line.startswith('>>>>>>> ') and in_conflict:
                    current_conflict['end'] = i
                    current_conflict['total_lines'] = i - current_conflict['start'] + 1
                    conflict_lines.append(current_conflict)
                    in_conflict = False
                elif in_conflict:
                    if 'separator' not in current_conflict:
                        current_conflict['head_lines'].append(line)
                    else:
                        current_conflict['branch_lines'].append(line)
            
            return {
                'file': file_path,
                'conflict_blocks': conflict_blocks,
                'conflicts': conflict_lines,
                'severity': 'high' if conflict_blocks > 5 else 'medium' if conflict_blocks > 2 else 'low'
            }
            
        except Exception as e:
            return {
                'file': file_path,
                'error': str(e),
                'severity': 'unknown'
            }
    
    def _get_changed_files(self, branch: str) -> List[str]:
        """Get list of files changed in branch"""
        try:
            result = subprocess.run(['git', 'diff', '--name-only', 'main', f'origin/{branch}'], 
                                  capture_output=True, text=True)
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except:
            return []
    
    def generate_resolution_strategy(self, branch: str, analysis: Dict) -> Dict:
        """Generate resolution strategy for conflicts"""
        if analysis['status'] == 'clean':
            return {
                'strategy': 'direct_merge',
                'steps': [
                    f"git merge origin/{branch} --no-ff",
                    "Run full test suite",
                    "Validate system health"
                ],
                'risk_level': 'low'
            }
        
        if analysis['status'] == 'conflicts':
            conflict_files = [c['file'] for c in analysis['conflicts']]
            
            # Determine strategy based on conflict complexity
            total_conflicts = sum(c['conflict_blocks'] for c in analysis['conflicts'])
            high_severity = any(c['severity'] == 'high' for c in analysis['conflicts'])
            
            if total_conflicts <= 3 and not high_severity:
                return {
                    'strategy': 'guided_resolution',
                    'steps': [
                        f"Create resolution branch: git checkout -b resolve-{branch.replace('/', '-')}",
                        f"Attempt merge: git merge origin/{branch}",
                        f"Resolve conflicts in: {', '.join(conflict_files)}",
                        "Run tests after each resolution",
                        "Merge to main after validation"
                    ],
                    'risk_level': 'medium',
                    'conflicted_files': conflict_files
                }
            else:
                return {
                    'strategy': 'careful_analysis',
                    'steps': [
                        "Manual analysis of each conflict required",
                        "Consider splitting into smaller merges",
                        "Extensive testing needed",
                        "May require coordination with original author"
                    ],
                    'risk_level': 'high',
                    'conflicted_files': conflict_files
                }
        
        return {
            'strategy': 'investigation',
            'steps': ["Investigate branch status", "Check for missing dependencies"],
            'risk_level': 'unknown'
        }
    
    def run_phase2_analysis(self):
        """Run complete Phase 2 analysis"""
        print("🎯 AURORA CLOUDBANK - PHASE 2 CONFLICT ANALYSIS")
        print("=" * 60)
        print("Analyzing problematic branches from Phase 1...")
        print()
        
        # Branches that had issues in Phase 1
        problem_branches = [
            'copilot/fix-137',  # Had merge conflicts
            'fix/workflows'     # Flagged as potentially conflicting
        ]
        
        results = {}
        
        for branch in problem_branches:
            print(f"\n📊 Branch: {branch}")
            print("-" * 40)
            
            # Check if branch exists
            check_result = subprocess.run(['git', 'show-ref', '--verify', '--quiet', f'refs/remotes/origin/{branch}'])
            if check_result.returncode != 0:
                print(f"⚠️ Branch {branch} not found - skipping")
                results[branch] = {'status': 'not_found'}
                continue
            
            # Analyze conflicts
            analysis = self.analyze_branch_conflicts(branch)
            strategy = self.generate_resolution_strategy(branch, analysis)
            
            results[branch] = {
                'analysis': analysis,
                'strategy': strategy
            }
            
            # Display results
            print(f"Status: {analysis['status']}")
            if analysis['status'] == 'conflicts':
                print(f"Conflicts: {len(analysis['conflicts'])} files")
                for conflict in analysis['conflicts']:
                    print(f"  • {conflict['file']} ({conflict['conflict_blocks']} blocks, {conflict['severity']} severity)")
            
            print(f"Strategy: {strategy['strategy']}")
            print(f"Risk Level: {strategy['risk_level']}")
            
            if strategy.get('conflicted_files'):
                print(f"Files needing resolution: {', '.join(strategy['conflicted_files'])}")
        
        print(f"\n🎯 PHASE 2 ANALYSIS COMPLETE")
        print("=" * 40)
        
        # Generate overall recommendation
        self._generate_phase2_recommendations(results)
        
        return results
    
    def _generate_phase2_recommendations(self, results: Dict):
        """Generate Phase 2 execution recommendations"""
        print("\n💡 PHASE 2 RECOMMENDATIONS:")
        print("-" * 30)
        
        safe_branches = []
        guided_branches = []
        complex_branches = []
        
        for branch, data in results.items():
            if data.get('status') == 'not_found':
                continue
                
            strategy = data.get('strategy', {})
            risk_level = strategy.get('risk_level', 'unknown')
            
            if risk_level == 'low':
                safe_branches.append(branch)
            elif risk_level == 'medium':
                guided_branches.append(branch)
            else:
                complex_branches.append(branch)
        
        if safe_branches:
            print(f"✅ Safe to merge immediately: {', '.join(safe_branches)}")
        
        if guided_branches:
            print(f"⚠️ Guided resolution needed: {', '.join(guided_branches)}")
            print("   → Use conflict resolution tools and careful testing")
        
        if complex_branches:
            print(f"🔴 Complex analysis required: {', '.join(complex_branches)}")
            print("   → Manual intervention and extensive testing needed")
        
        print(f"\n🎯 Next Action: {'Start with safe branches' if safe_branches else 'Begin guided resolution' if guided_branches else 'Investigate complex conflicts'}")

def main():
    analyzer = Phase2ConflictAnalyzer()
    results = analyzer.run_phase2_analysis()
    
    # Save results for future reference
    import json
    with open('PHASE2_CONFLICT_ANALYSIS.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed analysis saved to: PHASE2_CONFLICT_ANALYSIS.json")

if __name__ == "__main__":
    main()