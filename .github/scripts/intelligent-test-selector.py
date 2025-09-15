#!/usr/bin/env python3
"""
Aurora CloudBank Intelligent Test Selection
Analyzes file changes and selects relevant tests for optimal CI/CD performance
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Set


class IntelligentTestSelector:
    """Selects tests based on file changes and dependency analysis"""

    def __init__(self):
        self.repo_root = Path.cwd()
        self.test_mappings = self._load_test_mappings()
        self.changed_files = self._get_changed_files()

    def _load_test_mappings(self) -> Dict[str, List[str]]:
        """Load or create test-to-file mappings"""
        mappings_file = self.repo_root / ".github" / "test-mappings.json"

        if mappings_file.exists():
            with open(mappings_file) as f:
                return json.load(f)

        # Create default mappings based on Aurora architecture
        return {
            "unit": ["src/**/*.py", "modules/**/*.py", "tools/**/*.py", "*.py"],
            "integration": ["modules/*/", "tools/integration/", "scripts/", "tests/test_*_integration.py"],
            "aurora-core": [
                "src/aurora/",
                "modules/symbolic_core/",
                "modules/reflective_autonomy/",
                "aurora_*.py",
                "test_aurora_*.py",
                "test_t71_*.py",
            ],
            "security": ["scripts/aurora_security_*.py", ".security/", "auth/", "crypto*.js"],
            "api": ["aurora_api*.py", "middleware/", "static/", "templates/"],
        }

    def _get_changed_files(self) -> Set[str]:
        """Get list of changed files from git"""
        try:
            # Get changed files from git diff
            if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
                # For PR, compare with base branch
                base_ref = os.getenv("GITHUB_BASE_REF", "main")
                cmd = ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"]
            else:
                # For push, compare with previous commit
                cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
            else:
                print(f"⚠️ Git diff failed: {result.stderr}")
                return set()

        except Exception as e:
            print(f"⚠️ Error getting changed files: {e}")
            return set()

    def _path_matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a pattern"""
        from fnmatch import fnmatch

        # Handle directory patterns
        if pattern.endswith("/"):
            return file_path.startswith(pattern) or f"/{pattern}" in f"/{file_path}/"

        # Handle glob patterns
        if "*" in pattern:
            return fnmatch(file_path, pattern)

        # Handle exact matches and subpaths
        return file_path == pattern or file_path.startswith(f"{pattern}/")

    def select_tests(self) -> Dict[str, bool]:
        """Select which test groups should run based on changes"""
        if not self.changed_files:
            print("📝 No changed files detected, running all test groups")
            return {group: True for group in self.test_mappings.keys()}

        selected_groups = {}

        print(f"📁 Analyzing {len(self.changed_files)} changed files:")
        for file in sorted(self.changed_files):
            print(f"  - {file}")

        print("\n🧪 Test selection analysis:")

        for group, patterns in self.test_mappings.items():
            should_run = False
            matched_files = []
            
            for file in self.changed_files:
                for pattern in patterns:
                    if self._path_matches_pattern(file, pattern):
                        should_run = True
                        matched_files.append(file)
                        break
                        
            selected_groups[group] = should_run
            
            if should_run:
                print(f"  ✅ {group}: {len(matched_files)} relevant files changed")
                for f in matched_files[:3]:  # Show first 3 files
                    print(f"     - {f}")
                if len(matched_files) > 3:
                    print(f"     ... and {len(matched_files) - 3} more")
            else:
                print(f"  ⏭️  {group}: no relevant changes")
                
        return selected_groups

    def should_skip_build(self) -> bool:
        """Determine if build should be skipped entirely"""
        if not self.changed_files:
            return False
            
        # Skip if only documentation files changed
        doc_patterns = ["*.md", "docs/**", "*.txt", "*.rst"]
        doc_only = True
        
        for file in self.changed_files:
            is_doc = False
            for pattern in doc_patterns:
                if self._path_matches_pattern(file, pattern):
                    is_doc = True
                    break
            if not is_doc:
                doc_only = False
                break
                
        return doc_only

    def generate_test_matrix(self, selected_groups: Dict[str, bool]) -> List[Dict[str, str]]:
        """Generate test matrix for CI"""
        matrix = []
        
        for group, should_run in selected_groups.items():
            if should_run:
                matrix.append({"test-group": group})
                
        # Always include at least one test group
        if not matrix:
            matrix.append({"test-group": "unit"})
            
        return matrix


def main():
    """Main entry point for intelligent test selection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intelligent Test Selection")
    parser.add_argument("--output-format", choices=["json", "github"], 
                       default="json", help="Output format")
    parser.add_argument("--check-skip-build", action="store_true",
                       help="Check if build should be skipped")
    
    args = parser.parse_args()
    
    selector = IntelligentTestSelector()
    
    if args.check_skip_build:
        skip_build = selector.should_skip_build()
        
        if args.output_format == "github":
            print(f"skip_build={str(skip_build).lower()}")
            print(f"::set-output name=skip_build::{str(skip_build).lower()}")
        else:
            print(json.dumps({"skip_build": skip_build}))
    else:
        selected_groups = selector.select_tests()
        test_matrix = selector.generate_test_matrix(selected_groups)
        
        if args.output_format == "github":
            print(f"matrix={json.dumps(test_matrix)}")
            print(f"::set-output name=matrix::{json.dumps(test_matrix)}")
            
            # Individual group outputs
            for group, should_run in selected_groups.items():
                group_key = f"run_{group.replace('-', '_')}"
                print(f"{group_key}={str(should_run).lower()}")
                print(f"::set-output name={group_key}::{str(should_run).lower()}")
        else:
            print(json.dumps({
                "selected_groups": selected_groups,
                "test_matrix": test_matrix
            }, indent=2))


if __name__ == "__main__":
    main()
