#!/usr/bin/env python3
"""
Aurora CloudBank - Validation Manager
Elegant solution for handling validation file regeneration cycles

This module provides multiple strategies for handling the validation file update cycle:
1. Smart exclusion - ignore validation files during pre-commit
2. Timestamped reports - use unique filenames to avoid conflicts
3. Post-commit hooks - update validation files after commit
4. Memory-based validation - skip file writes during commit process

Author: Aurora CloudBank Development Team
Version: 1.0.0
Date: July 14, 2025
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional

class ValidationManager:
    """Manages validation file lifecycle to prevent regeneration cycles"""
    
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.validation_files = {
            "PRE_COMMIT_VALIDATION_ISSUES.md",
            "CANONICAL_VALIDATION_REPORT.md", 
            "AURORA_VALIDATION_SUMMARY.md"
        }
        self.config_file = self.repo_root / ".aurora_validation_config.json"
        self.load_config()
    
    def _find_repo_root(self) -> Path:
        """Find the git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def load_config(self):
        """Load validation manager configuration"""
        default_config = {
            "strategy": "smart_exclusion",  # smart_exclusion, timestamped, post_commit, memory_only
            "validation_dir": ".aurora_validation",
            "max_reports": 10,
            "exclude_from_commit": True,
            "auto_cleanup": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                self.config = {**default_config, **config}
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def is_validation_file(self, file_path: str) -> bool:
        """Check if a file is a validation file that should be managed"""
        filename = Path(file_path).name
        return filename in self.validation_files
    
    def get_validation_file_path(self, base_name: str = "PRE_COMMIT_VALIDATION_ISSUES.md") -> Path:
        """Get the appropriate path for validation files based on strategy"""
        strategy = self.config["strategy"]
        
        if strategy == "timestamped":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"validation_report_{timestamp}.md"
            return self.repo_root / self.config["validation_dir"] / name
        
        elif strategy == "post_commit":
            return self.repo_root / self.config["validation_dir"] / base_name
        
        elif strategy == "memory_only":
            # Return temp file that will be ignored
            return Path(tempfile.mktemp(suffix=".md"))
        
        else:  # smart_exclusion
            return self.repo_root / base_name
    
    def should_exclude_from_commit(self, file_path: str) -> bool:
        """Determine if file should be excluded from commit"""
        if not self.config["exclude_from_commit"]:
            return False
        
        if self.is_validation_file(file_path):
            strategy = self.config["strategy"]
            return strategy in ["smart_exclusion", "memory_only"]
        
        return False
    
    def filter_staged_files(self, staged_files: List[str]) -> List[str]:
        """Filter out validation files from staged files if configured"""
        if not self.config["exclude_from_commit"]:
            return staged_files
        
        return [f for f in staged_files if not self.should_exclude_from_commit(f)]
    
    def setup_pre_commit_exclusion(self):
        """Set up git pre-commit hook to exclude validation files"""
        gitignore_path = self.repo_root / ".gitignore"
        
        # Patterns to ignore validation files during commit
        ignore_patterns = [
            "# Aurora Validation Manager - Auto-generated",
            "PRE_COMMIT_VALIDATION_ISSUES.md",
            "CANONICAL_VALIDATION_REPORT.md",
            "AURORA_VALIDATION_SUMMARY.md",
            ".aurora_validation/",
            ".aurora_validation_config.json"
        ]
        
        # Read existing gitignore
        existing_lines = []
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                existing_lines = f.read().splitlines()
        
        # Add patterns if not already present
        lines_to_add = []
        for pattern in ignore_patterns:
            if pattern not in existing_lines:
                lines_to_add.append(pattern)
        
        if lines_to_add:
            with open(gitignore_path, 'a') as f:
                f.write("\n")
                f.write("\n".join(lines_to_add))
                f.write("\n")
            
            print(f"✅ Updated .gitignore with {len(lines_to_add)} validation exclusions")
    
    def create_post_commit_hook(self):
        """Create post-commit hook to update validation files after commit"""
        hooks_dir = self.repo_root / ".git" / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        post_commit_hook = hooks_dir / "post-commit"
        
        hook_content = '''#!/bin/bash
# Aurora CloudBank - Post-commit validation update
# Updates validation files after successful commit

echo "🔄 Updating validation files post-commit..."

# Run validation on the new commit
if [ -f "scripts/canonical_validator.py" ]; then
    python scripts/canonical_validator.py --post-commit-update
fi

echo "✅ Post-commit validation update complete"
'''
        
        with open(post_commit_hook, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        os.chmod(post_commit_hook, 0o755)
        print("✅ Created post-commit hook for validation updates")
    
    def cleanup_old_reports(self):
        """Clean up old validation reports based on config"""
        if not self.config["auto_cleanup"]:
            return
        
        validation_dir = self.repo_root / self.config["validation_dir"]
        if not validation_dir.exists():
            return
        
        # Find timestamped reports
        reports = list(validation_dir.glob("validation_report_*.md"))
        reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep only max_reports newest
        max_reports = self.config["max_reports"]
        if len(reports) > max_reports:
            for old_report in reports[max_reports:]:
                old_report.unlink()
                print(f"🗑️ Cleaned up old report: {old_report.name}")
    
    def implement_strategy(self, strategy: str):
        """Implement a specific validation strategy"""
        self.config["strategy"] = strategy
        self.save_config()
        
        if strategy == "smart_exclusion":
            self.setup_pre_commit_exclusion()
            print("✅ Implemented smart exclusion strategy")
            print("   - Validation files excluded from commits via .gitignore")
            print("   - Reports generated but not committed")
        
        elif strategy == "timestamped":
            validation_dir = self.repo_root / self.config["validation_dir"]
            validation_dir.mkdir(exist_ok=True)
            self.setup_pre_commit_exclusion()
            print("✅ Implemented timestamped strategy")
            print(f"   - Reports saved to {validation_dir}")
            print("   - Unique filenames prevent conflicts")
        
        elif strategy == "post_commit":
            validation_dir = self.repo_root / self.config["validation_dir"]
            validation_dir.mkdir(exist_ok=True)
            self.create_post_commit_hook()
            print("✅ Implemented post-commit strategy")
            print("   - Validation files updated after commit")
            print("   - Separate commit for validation updates")
        
        elif strategy == "memory_only":
            print("✅ Implemented memory-only strategy")
            print("   - Validation runs but no files written")
            print("   - Console output only during commits")
    
    def status_report(self):
        """Generate status report of current validation setup"""
        print("\n🛰️ Aurora Validation Manager Status")
        print("=" * 50)
        print(f"Strategy: {self.config['strategy']}")
        print(f"Repository Root: {self.repo_root}")
        print(f"Exclude from Commit: {self.config['exclude_from_commit']}")
        
        # Check git hooks
        hooks_dir = self.repo_root / ".git" / "hooks"
        pre_commit = hooks_dir / "pre-commit"
        post_commit = hooks_dir / "post-commit"
        
        print(f"\nGit Hooks:")
        print(f"  Pre-commit: {'✅' if pre_commit.exists() else '❌'}")
        print(f"  Post-commit: {'✅' if post_commit.exists() else '❌'}")
        
        # Check validation directory
        validation_dir = self.repo_root / self.config["validation_dir"]
        if validation_dir.exists():
            reports = list(validation_dir.glob("*.md"))
            print(f"\nValidation Directory: {validation_dir}")
            print(f"  Reports: {len(reports)}")
        
        # Check current validation files
        print(f"\nCurrent Validation Files:")
        for vf in self.validation_files:
            path = self.repo_root / vf
            if path.exists():
                size = path.stat().st_size
                print(f"  {vf}: {size} bytes")
            else:
                print(f"  {vf}: Not found")


def main():
    """CLI interface for validation manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora Validation Manager")
    parser.add_argument("--strategy", choices=["smart_exclusion", "timestamped", "post_commit", "memory_only"],
                       help="Implement validation strategy")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old reports")
    parser.add_argument("--exclude-file", help="Check if file should be excluded")
    
    args = parser.parse_args()
    
    manager = ValidationManager()
    
    if args.status:
        manager.status_report()
    elif args.strategy:
        manager.implement_strategy(args.strategy)
    elif args.cleanup:
        manager.cleanup_old_reports()
    elif args.exclude_file:
        excluded = manager.should_exclude_from_commit(args.exclude_file)
        print(f"File: {args.exclude_file}")
        print(f"Exclude from commit: {excluded}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
