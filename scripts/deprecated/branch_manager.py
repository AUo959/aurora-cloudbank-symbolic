#!/usr/bin/env python3
import argparse
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

"""
Aurora CloudBank Branch Management System
Automated cleanup and monitoring for repository branches
"""


@dataclass
class BranchInfo:
    """Information about a git branch"""
    name: str
    last_commit_date: str
    last_commit_hash: str
    author: str
    is_merged: bool
    days_old: int
    category: str


class BranchManager:
    """Automated branch management and cleanup system"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.dry_run = True
        self.categories = {
            "codex/": "feature",
            "R-": "agent",
            "alert-": "security",
            "dependabot/": "dependency",
            "copilot/": "ai-generated",
            "chore/": "maintenance",
        }
    
    def get_branches(self) -> List[str]:
        """Get list of all branches in repository"""
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "branch", "-r"],
                capture_output=True,
                text=True,
                check=True
            )
            branches = []
            for line in result.stdout.strip().split("\n"):
                branch = line.strip()
                if branch and "->" not in branch:
                    branches.append(branch.replace("origin/", ""))
            return branches
        except subprocess.CalledProcessError as e:
            print(f"Error getting branches: {e}")
            return []
    
    def get_branch_info(self, branch: str) -> Optional[BranchInfo]:
        """Get detailed information about a branch"""
        try:
            # Get last commit info
            result = subprocess.run(
                ["git", "-C", self.repo_path, "log", "-1", "--format=%H|%ci|%an", f"origin/{branch}"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                return None
            
            commit_hash, commit_date, author = result.stdout.strip().split("|")
            
            # Calculate days old
            commit_datetime = datetime.strptime(commit_date[:10], "%Y-%m-%d")
            days_old = (datetime.now() - commit_datetime).days
            
            # Check if merged
            is_merged = self.is_branch_merged(branch)
            
            # Categorize branch
            category = self.categorize_branch(branch)
            
            return BranchInfo(
                name=branch,
                last_commit_date=commit_date,
                last_commit_hash=commit_hash[:8],
                author=author,
                is_merged=is_merged,
                days_old=days_old,
                category=category
            )
        except Exception as e:
            print(f"Error getting info for branch {branch}: {e}")
            return None
    
    def is_branch_merged(self, branch: str) -> bool:
        """Check if branch is merged into main"""
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "branch", "-r", "--merged", "origin/main"],
                capture_output=True,
                text=True,
                check=True
            )
            return f"origin/{branch}" in result.stdout
        except subprocess.CalledProcessError:
            return False
    
    def categorize_branch(self, branch: str) -> str:
        """Categorize branch based on naming conventions"""
        for prefix, category in self.categories.items():
            if branch.startswith(prefix):
                return category
        return "other"
    
    def analyze_branches(self) -> Dict[str, List[BranchInfo]]:
        """Analyze all branches and categorize them"""
        branches = self.get_branches()
        analysis = {
            "stale": [],
            "active": [],
            "merged": [],
            "unknown": []
        }
        
        for branch in branches:
            info = self.get_branch_info(branch)
            if not info:
                continue
            
            if info.is_merged:
                analysis["merged"].append(info)
            elif info.days_old > 90:
                analysis["stale"].append(info)
            elif info.days_old > 30:
                analysis["active"].append(info)
            else:
                analysis["active"].append(info)
        
        return analysis
    
    def print_analysis(self, analysis: Dict[str, List[BranchInfo]]):
        """Print branch analysis report"""
        print("\n=== Branch Analysis Report ===")
        
        for category, branches in analysis.items():
            if not branches:
                continue
            
            print(f"\n{category.upper()} ({len(branches)} branches):")
            for branch in sorted(branches, key=lambda x: x.days_old, reverse=True):
                print(f"  - {branch.name}")
                print(f"    Last commit: {branch.days_old} days ago by {branch.author}")
                print(f"    Hash: {branch.last_commit_hash}")
                print(f"    Category: {branch.category}")
    
    def cleanup_merged_branches(self, analysis: Dict[str, List[BranchInfo]]):
        """Delete merged branches"""
        merged_branches = analysis.get("merged", [])
        
        if not merged_branches:
            print("\nNo merged branches to clean up")
            return
        
        print(f"\n{'DRY RUN: Would delete' if self.dry_run else 'Deleting'} {len(merged_branches)} merged branches:")
        
        for branch in merged_branches:
            if branch.name in ["main", "master", "develop"]:
                continue
            
            print(f"  - {branch.name} (merged {branch.days_old} days ago)")
            
            if not self.dry_run:
                try:
                    subprocess.run(
                        ["git", "-C", self.repo_path, "push", "origin", "--delete", branch.name],
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"    Error deleting branch: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Aurora CloudBank Branch Management System"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to git repository (default: current directory)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up merged branches"
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually delete branches (default is dry run)"
    )
    
    args = parser.parse_args()
    
    manager = BranchManager(repo_path=args.repo)
    manager.dry_run = not args.no_dry_run
    
    print(f"Analyzing repository at: {args.repo}")
    print(f"Mode: {'LIVE' if not manager.dry_run else 'DRY RUN'}")
    
    analysis = manager.analyze_branches()
    manager.print_analysis(analysis)
    
    if args.cleanup:
        manager.cleanup_merged_branches(analysis)
    
    print("\nBranch analysis complete.")


if __name__ == "__main__":
    main()
