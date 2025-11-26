#!/usr/bin/env python3
"""
Aurora CloudBank Intelligent Test Selection
Analyzes file changes and selects relevant tests for optimal CI/CD performance
"""

import logging

logger = logging.getLogger(__name__)

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
            "unit": [
                "src/**/*.py",
                "modules/**/*.py",
                "tools/**/*.py",
                "*.py"
            ],
            "integration": [
                "modules/*/",
                "tools/integration/",
                "scripts/",
                "tests/test_*_integration.py"
            ],
            "aurora-core": [
                "src/aurora/",
                "modules/symbolic_core/",
                "modules/reflective_autonomy/",
                "aurora_*.py",
                "test_aurora_*.py",
                "test_t71_*.py"
            ],
            "security": [
                "scripts/aurora_security_*.py",
                ".security/",
                "auth/",
                "crypto*.js"
            ],
            "api": [
                "aurora_api*.py",
                "middleware/",
                "static/",
                "templates/"
            ]
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
                return set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            else:
                logger.warning("Git diff failed: {result.stderr}")
                return set()
                
        except Exception as e:
            logger.warning("Error getting changed files: {e}")
            return set()
    
    def _path_matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a pattern"""
        from fnmatch import fnmatch
        
        # Handle directory patterns
        if pattern.endswith('/'):
            return file_path.startswith(pattern) or f"/{pattern}" in f"/{file_path}/"
        
        # Handle glob patterns
        if '*' in pattern:
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
            matched_patterns = []
            
            for file in self.changed_files:
                for pattern in patterns:
                    if self._path_matches_pattern(file, pattern):
                        should_run = True
                        matched_patterns.append(pattern)
                        break
            
            selected_groups[group] = should_run
            
            if should_run:
                print(f"  ✅ {group}: Will run (matched: {', '.join(set(matched_patterns))})")
            else:
                print(f"  ⏭️ {group}: Skipping (no relevant changes)")
        
        # Always run security tests if security-related files changed
        security_keywords = ['security', 'auth', 'crypto', 'password', 'token', 'key']
        for file in self.changed_files:
            if any(keyword in file.lower() for keyword in security_keywords):
                selected_groups['security'] = True
                print("  🛡️ Security tests enabled due to security-related changes")
                break
        
        return selected_groups
    
    def generate_matrix(self) -> Dict:
        """Generate test matrix for GitHub Actions"""
        selected = self.select_tests()
        
        # Only include groups that should run
        include = []
        for group, should_run in selected.items():
            if should_run:
                include.append({"test-group": group})
        
        # If no tests selected, run at least unit tests
        if not include:
            include = [{"test-group": "unit"}]
            logger.warning("No tests selected, defaulting to unit tests")
        
        matrix = {"include": include}
        
        print("")
# 📊 Generated test matrix: %s test groups", len(include))
        for item in include:
            print(f"  - {item['test-group']}")
        
        return matrix
    
    def should_skip_build(self) -> bool:
        """Determine if build can be skipped entirely"""
        if not self.changed_files:
            return False
        
        # Skip build only for documentation-only changes
        doc_only_patterns = [
            "*.md", "docs/", "README*", "CHANGELOG*",
            "LICENSE*", ".gitignore", ".github/ISSUE_TEMPLATE/",
            ".github/pull_request_template.md"
        ]
        
        non_doc_files = []
        for file in self.changed_files:
            is_doc_only = any(self._path_matches_pattern(file, pattern) for pattern in doc_only_patterns)
            if not is_doc_only:
                non_doc_files.append(file)
        
        if not non_doc_files:
            print("📚 Only documentation files changed, build can be skipped")
            return True
        
        return False


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora Intelligent Test Selection")
    parser.add_argument(
        "--output-format",
        choices=["json", "github"],
        default="github",
        help="Output format for CI/CD integration",
    )
    parser.add_argument(
        "--check-skip-build",
        action="store_true",
        help="Check if entire build can be skipped",
    )
    
    args = parser.parse_args()
    
    selector = IntelligentTestSelector()
    
    if args.check_skip_build:
        skip = selector.should_skip_build()
        if args.output_format == "github":
            with open(os.environ["GITHUB_OUTPUT"], "a") as gh_out:
                gh_out.write(f"skip_build={str(skip).lower()}\n")
        else:
            print(json.dumps({"skip_build": skip}))
        return
    
    matrix = selector.generate_matrix()
    
    if args.output_format == "github":
        # Output for GitHub Actions using $GITHUB_OUTPUT
        matrix_json = json.dumps(matrix)
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as gh_out:
                gh_out.write(f"matrix={matrix_json}\n")
                # Also output individual test group flags
                selected = selector.select_tests()
                for group, should_run in selected.items():
                    safe_group = group.replace('-', '_')
                    gh_out.write(f"run_{safe_group}={str(should_run).lower()}\n")
        else:
            # Fallback for local runs
            print(json.dumps(matrix, indent=2))
    else:
        print(json.dumps(matrix, indent=2))


if __name__ == "__main__":
    main()
