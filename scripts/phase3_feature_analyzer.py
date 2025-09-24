#!/usr/bin/env python3

"""
Aurora CloudBank - Phase 3 Feature Integration Analyzer
Analyzes remaining branches for safe feature integration
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

class Phase3FeatureAnalyzer:
    def __init__(self):
        self.repo_root = Path.cwd()
        self.integrated_branches = {
            'copilot/fix-144',   # Phase 1
            'copilot/fix-137',   # Phase 2  
            'fix/workflows'      # Phase 2
        }
        
    def get_all_remote_branches(self) -> List[str]:
        """Get all remote branches excluding already integrated ones"""
        try:
            result = subprocess.run(['git', 'branch', '-r'], capture_output=True, text=True)
            branches = []
            
            for line in result.stdout.strip().split('\n'):
                branch = line.strip()
                if branch and not branch.startswith('origin/HEAD'):
                    clean_branch = branch.replace('origin/', '')
                    if clean_branch != 'main' and clean_branch not in self.integrated_branches:
                        branches.append(clean_branch)
            
            return sorted(branches)
            
        except subprocess.CalledProcessError:
            return []
    
    def categorize_branches(self, branches: List[str]) -> Dict[str, List[str]]:
        """Categorize branches by type and purpose"""
        categories = {
            'copilot_fixes': [],
            'ai_generation': [],
            'dependency_updates': [], 
            'feature_branches': [],
            'enhancement_branches': [],
            'experimental': [],
            'maintenance': [],
            'other': []
        }
        
        for branch in branches:
            branch_lower = branch.lower()
            
            # Categorization logic
            if branch.startswith('copilot/'):
                categories['copilot_fixes'].append(branch)
            elif any(keyword in branch_lower for keyword in ['ai/', 'generation', 'gpt', 'claude']):
                categories['ai_generation'].append(branch) 
            elif any(keyword in branch_lower for keyword in ['dependabot/', 'deps/', 'dependency', 'update/', 'bump']):
                categories['dependency_updates'].append(branch)
            elif branch.startswith('feature/'):
                categories['feature_branches'].append(branch)
            elif any(keyword in branch_lower for keyword in ['enhance', 'improve', 'optimization', 'upgrade']):
                categories['enhancement_branches'].append(branch)
            elif any(keyword in branch_lower for keyword in ['experimental', 'test', 'poc', 'prototype']):
                categories['experimental'].append(branch)
            elif any(keyword in branch_lower for keyword in ['fix/', 'bugfix', 'hotfix', 'maintenance']):
                categories['maintenance'].append(branch)
            else:
                categories['other'].append(branch)
        
        return categories
    
    def analyze_branch_safety(self, branch: str) -> Dict:
        """Analyze branch safety for integration"""
        try:
            # Get branch info
            branch_info = self._get_branch_info(branch)
            
            # Check for conflicts
            conflict_check = self._quick_conflict_check(branch)
            
            # Analyze changes
            change_analysis = self._analyze_changes(branch)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(branch_info, conflict_check, change_analysis)
            
            return {
                'branch': branch,
                'branch_info': branch_info,
                'conflicts': conflict_check,
                'changes': change_analysis,
                'risk_score': risk_score,
                'risk_level': self._get_risk_level(risk_score),
                'recommendation': self._get_recommendation(risk_score, conflict_check)
            }
            
        except Exception as e:
            return {
                'branch': branch,
                'error': str(e),
                'risk_score': 100,
                'risk_level': 'unknown',
                'recommendation': 'investigate'
            }
    
    def _get_branch_info(self, branch: str) -> Dict:
        """Get basic branch information"""
        try:
            # Get last commit info
            result = subprocess.run(['git', 'log', '-1', '--format=%H|%s|%an|%ad', f'origin/{branch}'],
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                hash_val, subject, author, date = result.stdout.strip().split('|', 3)
                return {
                    'last_commit': hash_val[:8],
                    'subject': subject,
                    'author': author,
                    'date': date
                }
            
            return {'status': 'no_info_available'}
            
        except:
            return {'status': 'error_getting_info'}
    
    def _quick_conflict_check(self, branch: str) -> Dict:
        """Quick check for potential merge conflicts"""
        try:
            # Use git merge-tree for dry-run conflict detection
            result = subprocess.run(['git', 'merge-tree', 'main', f'origin/{branch}'],
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                # Count potential conflict markers
                conflict_markers = result.stdout.count('<<<<<<<')
                return {
                    'has_conflicts': conflict_markers > 0,
                    'conflict_count': conflict_markers,
                    'status': 'conflicts_detected' if conflict_markers > 0 else 'clean'
                }
            else:
                return {
                    'has_conflicts': False,
                    'conflict_count': 0,
                    'status': 'clean'
                }
                
        except:
            return {
                'has_conflicts': None,
                'conflict_count': 0,
                'status': 'unknown'
            }
    
    def _analyze_changes(self, branch: str) -> Dict:
        """Analyze the scope and nature of changes"""
        try:
            # Get file changes
            result = subprocess.run(['git', 'diff', '--name-status', 'main', f'origin/{branch}'],
                                  capture_output=True, text=True)
            
            changes = {
                'added': 0,
                'modified': 0, 
                'deleted': 0,
                'files': [],
                'file_types': {}
            }
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t', 1)
                if len(parts) != 2:
                    continue
                    
                status, filename = parts
                changes['files'].append({'status': status, 'file': filename})
                
                # Count by status
                if status == 'A':
                    changes['added'] += 1
                elif status == 'M':
                    changes['modified'] += 1
                elif status == 'D':
                    changes['deleted'] += 1
                
                # Count by file type
                ext = Path(filename).suffix.lower()
                changes['file_types'][ext] = changes['file_types'].get(ext, 0) + 1
            
            changes['total_files'] = len(changes['files'])
            
            return changes
            
        except:
            return {
                'total_files': 0,
                'added': 0,
                'modified': 0,
                'deleted': 0,
                'files': [],
                'file_types': {}
            }
    
    def _calculate_risk_score(self, branch_info: Dict, conflict_check: Dict, changes: Dict) -> int:
        """Calculate risk score (0-100, lower is safer)"""
        risk = 0
        
        # Base risk from conflicts
        if conflict_check.get('has_conflicts'):
            risk += conflict_check.get('conflict_count', 0) * 15
            
        # Risk from change volume
        total_files = changes.get('total_files', 0)
        if total_files > 20:
            risk += 25
        elif total_files > 10:
            risk += 15
        elif total_files > 5:
            risk += 10
            
        # Risk from deletions (more dangerous)
        deleted = changes.get('deleted', 0)
        risk += deleted * 5
        
        # Risk from core file modifications
        core_patterns = ['.github/', 'src/core/', 'modules/', 'tests/']
        for file_info in changes.get('files', []):
            filename = file_info.get('file', '')
            if any(pattern in filename for pattern in core_patterns):
                risk += 5
        
        # Reduce risk for certain safe file types
        safe_extensions = ['.md', '.txt', '.json', '.yml', '.yaml']
        safe_files = sum(1 for f in changes.get('files', []) 
                        if any(f.get('file', '').endswith(ext) for ext in safe_extensions))
        
        if safe_files > total_files * 0.5:  # More than 50% safe files
            risk -= 10
            
        return max(0, min(100, risk))
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Convert risk score to level"""
        if risk_score <= 15:
            return 'low'
        elif risk_score <= 35:
            return 'medium'
        elif risk_score <= 60:
            return 'high'
        else:
            return 'critical'
    
    def _get_recommendation(self, risk_score: int, conflict_check: Dict) -> str:
        """Get integration recommendation"""
        if risk_score <= 15 and not conflict_check.get('has_conflicts'):
            return 'safe_integration'
        elif risk_score <= 35:
            return 'careful_integration'
        elif conflict_check.get('has_conflicts'):
            return 'resolve_conflicts_first'
        else:
            return 'detailed_analysis_required'
    
    def run_phase3_analysis(self):
        """Run complete Phase 3 analysis"""
        print("🎯 AURORA CLOUDBANK - PHASE 3 FEATURE INTEGRATION ANALYSIS")
        print("=" * 70)
        print(f"Starting analysis at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Get all remaining branches
        all_branches = self.get_all_remote_branches()
        print(f"📊 Total branches to analyze: {len(all_branches)}")
        print(f"📝 Previously integrated: {len(self.integrated_branches)}")
        print()
        
        # Categorize branches
        categories = self.categorize_branches(all_branches)
        
        print("📂 BRANCH CATEGORIZATION:")
        print("-" * 30)
        for category, branches in categories.items():
            if branches:
                print(f"  {category.replace('_', ' ').title()}: {len(branches)}")
                for branch in branches[:3]:  # Show first 3
                    print(f"    • {branch}")
                if len(branches) > 3:
                    print(f"    ... and {len(branches) - 3} more")
                print()
        
        # Phase 3 Focus: Feature and Enhancement Branches
        phase3_candidates = (
            categories['feature_branches'] +
            categories['enhancement_branches'] +
            categories['ai_generation'] +
            categories['copilot_fixes'][:5] +  # Top 5 copilot fixes
            categories['dependency_updates'][:3]  # Top 3 dependency updates
        )
        
        print(f"🎯 PHASE 3 CANDIDATES: {len(phase3_candidates)} branches")
        print("=" * 50)
        
        # Analyze each candidate
        analysis_results = []
        
        for branch in phase3_candidates:
            print(f"\n🔍 Analyzing: {branch}")
            print("-" * 40)
            
            analysis = self.analyze_branch_safety(branch)
            analysis_results.append(analysis)
            
            if 'error' in analysis:
                print(f"❌ Error: {analysis['error']}")
                continue
            
            # Display key metrics
            print(f"Risk Level: {analysis['risk_level']} ({analysis['risk_score']}/100)")
            print(f"Conflicts: {'Yes' if analysis['conflicts'].get('has_conflicts') else 'No'}")
            print(f"Files Changed: {analysis['changes']['total_files']}")
            print(f"Recommendation: {analysis['recommendation']}")
            
            # Show file change breakdown
            changes = analysis['changes']
            if changes['total_files'] > 0:
                print(f"Changes: +{changes['added']} ~{changes['modified']} -{changes['deleted']}")
        
        # Generate Phase 3 execution plan
        self._generate_phase3_plan(analysis_results)
        
        # Save analysis results
        self._save_analysis_results(analysis_results, categories)
        
        return analysis_results
    
    def _generate_phase3_plan(self, analysis_results: List[Dict]):
        """Generate Phase 3 execution plan"""
        print(f"\n🎯 PHASE 3 EXECUTION PLAN")
        print("=" * 40)
        
        # Group by recommendation
        safe_branches = []
        careful_branches = []
        complex_branches = []
        
        for analysis in analysis_results:
            if analysis.get('error'):
                continue
                
            rec = analysis.get('recommendation', 'unknown')
            branch = analysis.get('branch')
            
            if rec == 'safe_integration':
                safe_branches.append(branch)
            elif rec in ['careful_integration', 'resolve_conflicts_first']:
                careful_branches.append(branch)
            else:
                complex_branches.append(branch)
        
        print("📋 Integration Phases:")
        print()
        
        if safe_branches:
            print("🟢 Phase 3A - Safe Integration (Low Risk):")
            for branch in safe_branches[:5]:  # Top 5
                print(f"   • {branch}")
            if len(safe_branches) > 5:
                print(f"   ... and {len(safe_branches) - 5} more")
            print()
        
        if careful_branches:
            print("🟡 Phase 3B - Careful Integration (Medium Risk):")
            for branch in careful_branches[:3]:  # Top 3
                print(f"   • {branch}")
            if len(careful_branches) > 3:
                print(f"   ... and {len(careful_branches) - 3} more")
            print()
        
        if complex_branches:
            print("🔴 Phase 3C - Complex Integration (High Risk):")
            for branch in complex_branches[:2]:  # Top 2
                print(f"   • {branch}")
            if len(complex_branches) > 2:
                print(f"   ... and {len(complex_branches) - 2} more")
            print()
        
        # Execution recommendation
        if safe_branches:
            next_action = f"Start with Phase 3A - begin with '{safe_branches[0]}'"
        elif careful_branches:
            next_action = f"Begin Phase 3B with careful analysis of '{careful_branches[0]}'"
        else:
            next_action = "All remaining branches require detailed analysis"
        
        print(f"🎯 Recommended Next Action: {next_action}")
        
        return {
            'safe_branches': safe_branches,
            'careful_branches': careful_branches, 
            'complex_branches': complex_branches,
            'next_action': next_action
        }
    
    def _save_analysis_results(self, analysis_results: List[Dict], categories: Dict):
        """Save detailed analysis results"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'phase': 3,
            'integrated_branches': list(self.integrated_branches),
            'categories': categories,
            'analysis_results': analysis_results,
            'summary': {
                'total_analyzed': len(analysis_results),
                'safe_count': len([a for a in analysis_results if a.get('recommendation') == 'safe_integration']),
                'careful_count': len([a for a in analysis_results if a.get('recommendation') == 'careful_integration']),
                'complex_count': len([a for a in analysis_results if a.get('recommendation') not in ['safe_integration', 'careful_integration']])
            }
        }
        
        with open('PHASE3_FEATURE_ANALYSIS.json', 'w') as f:
            json.dump(results, f, indent=2)

def main():
    analyzer = Phase3FeatureAnalyzer()
    results = analyzer.run_phase3_analysis()
    
    print(f"\n📄 Detailed analysis saved to: PHASE3_FEATURE_ANALYSIS.json")
    print(f"🎯 Phase 3 analysis complete - ready for feature integration!")

if __name__ == "__main__":
    main()