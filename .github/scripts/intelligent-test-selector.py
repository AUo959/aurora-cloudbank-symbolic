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
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
    def __init__(self):
        self.repo_root = Path.cwd()
        self.test_mappings = self._load_test_mappings()
        self.changed_files = self._get_changed_files()
<<<<<<< HEAD
        
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
=======

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
>>>>>>> origin/main
            "aurora-core": [
                "src/aurora/",
                "modules/symbolic_core/",
                "modules/reflective_autonomy/",
                "aurora_*.py",
                "test_aurora_*.py",
<<<<<<< HEAD
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
    
=======
                "test_t71_*.py",
            ],
            "security": ["scripts/aurora_security_*.py", ".security/", "auth/", "crypto*.js"],
            "api": ["aurora_api*.py", "middleware/", "static/", "templates/"],
        }

>>>>>>> origin/main
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
<<<<<<< HEAD
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                return set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
            else:
                print("⚠️ Git diff failed: %s", result.stderr)
                return set()
                
        except Exception as e:
            print("⚠️ Error getting changed files: %s", e)
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
    
=======

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
            else:
                print("⚠️ Git diff failed: %s", result.stderr)
                return set()

        except Exception as e:
            print("⚠️ Error getting changed files: %s", e)
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

>>>>>>> origin/main
    def select_tests(self) -> Dict[str, bool]:
        """Select which test groups should run based on changes"""
        if not self.changed_files:
            print("📝 No changed files detected, running all test groups")
            return {group: True for group in self.test_mappings.keys()}
<<<<<<< HEAD
        
        selected_groups = {}
        
        print("📁 Analyzing %s changed files:", len(self.changed_files))
        for file in sorted(self.changed_files):
            print("  - %s", file)
        
        print("\n🧪 Test selection analysis:")
        
        for group, patterns in self.test_mappings.items():
            should_run = False
            matched_patterns = []
            
=======

        selected_groups = {}

        print("📁 Analyzing %s changed files:", len(self.changed_files))
        for file in sorted(self.changed_files):
            print("  - %s", file)

        print("\n🧪 Test selection analysis:")

        for group, patterns in self.test_mappings.items():
            should_run = False
            matched_patterns = []

>>>>>>> origin/main
            for file in self.changed_files:
                for pattern in patterns:
                    if self._path_matches_pattern(file, pattern):
                        should_run = True
                        matched_patterns.append(pattern)
                        break
<<<<<<< HEAD
            
            selected_groups[group] = should_run
            
=======

            selected_groups[group] = should_run

>>>>>>> origin/main
            if should_run:
                print("  ✅ {group}: Will run (matched: %s)", ', '.join(set(matched_patterns)))
            else:
                print("  ⏭️ %s: Skipping (no relevant changes)", group)
<<<<<<< HEAD
        
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
        
=======

        # Always run security tests if security-related files changed
        security_keywords = ["security", "auth", "crypto", "password", "token", "key"]
        for file in self.changed_files:
            if any(keyword in file.lower() for keyword in security_keywords):
                selected_groups["security"] = True
                print("  🛡️ Security tests enabled due to security-related changes")
                break

        return selected_groups

    def generate_matrix(self) -> Dict:
        """Generate test matrix for GitHub Actions"""
        selected = self.select_tests()

>>>>>>> origin/main
        # Only include groups that should run
        include = []
        for group, should_run in selected.items():
            if should_run:
                include.append({"test-group": group})
<<<<<<< HEAD
        
=======

>>>>>>> origin/main
        # If no tests selected, run at least unit tests
        if not include:
            include = [{"test-group": "unit"}]
            print("⚠️ No tests selected, defaulting to unit tests")
<<<<<<< HEAD
        
        matrix = {"include": include}
        
        print("")
# 📊 Generated test matrix: %s test groups", len(include))
        for item in include:
            print("  - %s", item['test-group'])
        
        return matrix
    
=======

        matrix = {"include": include}

        print("")
# 📊 Generated test matrix: %s test groups", len(include))
        for item in include:
            print("  - %s", item['test-group'])

        return matrix

>>>>>>> origin/main
    def should_skip_build(self) -> bool:
        """Determine if build can be skipped entirely"""
        if not self.changed_files:
            return False
<<<<<<< HEAD
        
        # Skip build only for documentation-only changes
        doc_only_patterns = [
            "*.md", "docs/", "README*", "CHANGELOG*",
            "LICENSE*", ".gitignore", ".github/ISSUE_TEMPLATE/",
            ".github/pull_request_template.md"
        ]
        
=======

        # Skip build only for documentation-only changes
        doc_only_patterns = [
            "*.md",
            "docs/",
            "README*",
            "CHANGELOG*",
            "LICENSE*",
            ".gitignore",
            ".github/ISSUE_TEMPLATE/",
            ".github/pull_request_template.md",
        ]

>>>>>>> origin/main
        non_doc_files = []
        for file in self.changed_files:
            is_doc_only = any(self._path_matches_pattern(file, pattern) for pattern in doc_only_patterns)
            if not is_doc_only:
                non_doc_files.append(file)
<<<<<<< HEAD
        
        if not non_doc_files:
            print("📚 Only documentation files changed, build can be skipped")
            return True
        
=======

        if not non_doc_files:
            print("📚 Only documentation files changed, build can be skipped")
            return True

>>>>>>> origin/main
        return False


def main():
    """Main CLI interface"""
    import argparse
<<<<<<< HEAD
    
=======

>>>>>>> origin/main
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
<<<<<<< HEAD
    
    args = parser.parse_args()
    
    selector = IntelligentTestSelector()
    
=======

    args = parser.parse_args()

    selector = IntelligentTestSelector()

>>>>>>> origin/main
    if args.check_skip_build:
        skip = selector.should_skip_build()
        if args.output_format == "github":
            with open(os.environ["GITHUB_OUTPUT"], "a") as gh_out:
                gh_out.write(f"skip_build={str(skip).lower()}\n")
        else:
            print(json.dumps({"skip_build": skip}))
        return
<<<<<<< HEAD
    
    matrix = selector.generate_matrix()
    
=======

    matrix = selector.generate_matrix()

>>>>>>> origin/main
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
<<<<<<< HEAD
                    safe_group = group.replace('-', '_')
=======
                    safe_group = group.replace("-", "_")
>>>>>>> origin/main
                    gh_out.write(f"run_{safe_group}={str(should_run).lower()}\n")
        else:
            # Fallback for local runs
            print(json.dumps(matrix, indent=2))
    else:
        print(json.dumps(matrix, indent=2))


if __name__ == "__main__":
    main()
