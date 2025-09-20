#!/usr/bin/env python3
"""
Aurora CloudBank - Consolidated Branch Cleanup Script
Performs automated branch consolidation based on analysis results.
"""

import subprocess
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


class ConsolidatedBranchCleanup:
    """Executes branch consolidation based on analysis."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.dry_run = True

    def load_analysis(self, analysis_file: str) -> Dict:
        """Load consolidation analysis results."""
        try:
            with open(analysis_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Analysis file not found: {analysis_file}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in analysis file: {analysis_file}")
            return {}

    def delete_merged_branches(self, branches: List[Dict]) -> Dict:
        """Delete branches that are already merged."""
        results = {
            'deleted': 0,
            'errors': 0,
            'skipped': 0
        }

        print(f"\n🗑️  Deleting {len(branches)} merged branches...")
        
        for branch in branches:
            branch_name = branch['name']
            
            # Skip main branch
            if branch_name == 'main':
                results['skipped'] += 1
                continue
                
            try:
                if self.dry_run:
                    print(f"   [DRY RUN] Would delete: {branch_name}")
                    results['deleted'] += 1
                else:
                    # Delete remote branch
                    cmd = ["git", "push", "origin", "--delete", branch_name]
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True, 
                        cwd=self.repo_path
                    )
                    
                    if result.returncode == 0:
                        print(f"   ✅ Deleted: {branch_name}")
                        results['deleted'] += 1
                    else:
                        print(f"   ❌ Failed to delete {branch_name}: {result.stderr}")
                        results['errors'] += 1
                        
            except Exception as e:
                print(f"   ❌ Error deleting {branch_name}: {e}")
                results['errors'] += 1

        return results

    def create_archive_tags(self, branches: List[Dict]) -> Dict:
        """Create archive tags for important branches before deletion."""
        results = {
            'archived': 0,
            'errors': 0
        }

        print(f"\n📦 Creating archive tags for {len(branches)} branches...")
        
        for branch in branches:
            branch_name = branch['name']
            tag_name = f"archive/{branch_name.replace('/', '_')}"
            
            try:
                if self.dry_run:
                    print(f"   [DRY RUN] Would create tag: {tag_name}")
                    results['archived'] += 1
                else:
                    # Create tag
                    cmd = ["git", "tag", tag_name, f"origin/{branch_name}"]
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.repo_path
                    )
                    
                    if result.returncode == 0:
                        # Push tag
                        push_cmd = ["git", "push", "origin", tag_name]
                        push_result = subprocess.run(
                            push_cmd,
                            capture_output=True,
                            text=True,
                            cwd=self.repo_path
                        )
                        
                        if push_result.returncode == 0:
                            print(f"   ✅ Archived: {branch_name} -> {tag_name}")
                            results['archived'] += 1
                        else:
                            print(f"   ❌ Failed to push tag {tag_name}: {push_result.stderr}")
                            results['errors'] += 1
                    else:
                        print(f"   ❌ Failed to create tag {tag_name}: {result.stderr}")
                        results['errors'] += 1
                        
            except Exception as e:
                print(f"   ❌ Error archiving {branch_name}: {e}")
                results['errors'] += 1

        return results

    def generate_pr_recommendations(self, branches: List[Dict]) -> str:
        """Generate PR creation recommendations."""
        if not branches:
            return "No branches require pull requests."
            
        recommendations = [
            "🚀 PULL REQUEST CREATION RECOMMENDATIONS",
            "=" * 50,
            ""
        ]
        
        for i, branch in enumerate(branches, 1):
            recommendations.extend([
                f"{i}. Branch: {branch['name']}",
                f"   Author: {branch['details']['author']}",
                f"   Subject: {branch['details']['subject']}",
                f"   Action: Create PR to merge this branch into main",
                ""
            ])
        
        recommendations.extend([
            "Note: These branches contain unmerged commits that may be valuable.",
            "Review each branch and create pull requests as appropriate."
        ])
        
        return "\n".join(recommendations)

    def generate_consolidation_summary(self, analysis: Dict, results: Dict) -> str:
        """Generate comprehensive consolidation summary."""
        summary = [
            "\n🎯 AURORA CLOUDBANK BRANCH CONSOLIDATION SUMMARY",
            "=" * 60,
            "",
            f"📊 ANALYSIS RESULTS:",
            f"   Total Branches Analyzed: {analysis['summary']['total_branches']}",
            f"   Consolidation Potential: {analysis['summary']['consolidation_ratio']}%",
            "",
            f"🚀 ACTIONS COMPLETED:",
            f"   Branches Deleted: {results.get('deleted', 0)}",
            f"   Branches Archived: {results.get('archived', 0)}",
            f"   Errors Encountered: {results.get('errors', 0)}",
            "",
            f"📋 REMAINING ACTIONS:",
            f"   Pull Requests Needed: {analysis['summary']['pr_candidates']}",
            f"   Manual Review Required: {analysis['summary']['needs_review']}",
            "",
            "✅ OPTIMIZATION BENEFITS:",
            "   - Cleaner repository structure",
            "   - Faster Git operations",
            "   - Reduced visual clutter",
            "   - Improved developer experience",
            "",
            "🔗 NEXT STEPS:",
            "   1. Create pull requests for unmerged branches",
            "   2. Review branches requiring manual attention",
            "   3. Continue using this script for ongoing maintenance",
            ""
        ]
        
        return "\n".join(summary)

    def execute_consolidation(self, analysis: Dict, archive_important: bool = True) -> Dict:
        """Execute the full consolidation process."""
        print("🌟 Aurora CloudBank - Branch Consolidation Execution")
        print("=" * 60)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")
        
        results = {
            'deleted': 0,
            'archived': 0,
            'errors': 0
        }
        
        # Step 1: Archive important branches (optional)
        if archive_important:
            important_branches = [
                branch for branch in analysis['safe_to_delete']
                if branch['category'] in ['backup', 'safety', 'canonical']
            ]
            if important_branches:
                archive_results = self.create_archive_tags(important_branches)
                results['archived'] = archive_results['archived']
                results['errors'] += archive_results['errors']
        
        # Step 2: Delete merged branches
        delete_results = self.delete_merged_branches(analysis['safe_to_delete'])
        results['deleted'] = delete_results['deleted']
        results['errors'] += delete_results['errors']
        
        # Step 3: Generate PR recommendations
        if analysis['pull_requests_needed']:
            print(f"\n{self.generate_pr_recommendations(analysis['pull_requests_needed'])}")
        
        # Step 4: Generate summary
        print(self.generate_consolidation_summary(analysis, results))
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Aurora CloudBank Consolidated Branch Cleanup")
    parser.add_argument("--analysis", default="/tmp/comprehensive_consolidation_analysis.json",
                       help="Path to consolidation analysis JSON file")
    parser.add_argument("--execute", action="store_true",
                       help="Execute cleanup (default: dry run)")
    parser.add_argument("--no-archive", action="store_true",
                       help="Skip archiving important branches")
    
    args = parser.parse_args()
    
    cleanup = ConsolidatedBranchCleanup()
    cleanup.dry_run = not args.execute
    
    # Load analysis
    analysis = cleanup.load_analysis(args.analysis)
    if not analysis:
        print("❌ Cannot proceed without valid analysis data")
        sys.exit(1)
    
    # Execute consolidation
    results = cleanup.execute_consolidation(
        analysis, 
        archive_important=not args.no_archive
    )
    
    # Exit with appropriate code
    if results['errors'] > 0:
        print(f"\n⚠️  Completed with {results['errors']} errors")
        sys.exit(1)
    else:
        print(f"\n✅ Consolidation completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()