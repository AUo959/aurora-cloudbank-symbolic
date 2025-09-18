#!/usr/bin/env python3
"""
Aurora CloudBank Intelligent Test Selection
Analyzes file changes and selects relevant tests for optimal CI/CD performance
"""

import os

from typing import Dict, List, Set

class IntelligentTestSelector:
    pass
    """Selects tests based on file changes and dependency analysis"""

    def __init__(self):
    pass
        self.repo_root = Path.cwd()
        self.test_mappings = self._load_test_mappings()
        self.changed_files = self._get_changed_files()

    def _load_test_mappings(self) -> Dict[str, List[str]]:
    pass
        """Load or create test-to-file mappings"""
        mappings_file = self.repo_root / ".github" / "test-mappings.json"

        if mappings_file.exists():
    pass
            with open(mappings_file) as f:
    pass
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
    pass
        """Get list of changed files from git"""
        try:
    pass
            # Get changed files from git diff
            if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
    pass
                # For PR, compare with base branch
                base_ref = os.getenv("GITHUB_BASE_REF", "main")
                cmd = ["git", "dif", "--name-only", "origin/{base_ref}...HEAD"]
            else:
    pass
                # For push, compare with previous commit
                cmd = ["git", "dif", "--name-only", "HEAD~1", "HEAD"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
    pass
                return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
            else:
    pass
                print("⚠️ Git diff failed: {result.stderr}")
                return set()

        except Exception as _:
    pass
            print("⚠️ Error getting changed files: {e}")
            return set()

    def _path_matches_pattern(self, file_path: str, pattern: str) -> bool:
    pass
        """Check if file path matches a pattern"""
        from fnmatch import fnmatch

        # Handle directory patterns
        if pattern.endswith("/"):
    pass
            return file_path.startswith(pattern) or "/{pattern}" in "/{file_path}/"

        # Handle glob patterns
        if "*" in pattern:
    pass
            return fnmatch(file_path, pattern)

        # Handle exact matches and subpaths
        return file_path == pattern or file_path.startswith("{pattern}/")

    def select_tests(self) -> Dict[str, bool]:
    pass
        """Select which test groups should run based on changes"""
        if not self.changed_files:
    pass
            print("📝 No changed files detected, running all test groups")
            return {group: True for group in self.test_mappings.keys()}

        selected_groups = {}

        print("📁 Analyzing {len(self.changed_files)} changed files:")
        for file in sorted(self.changed_files):
    pass
            print("  - {file}")

        print("\n🧪 Test selection analysis:")

        for group, patterns in self.test_mappings.items():
    pass
            should_run = False
            matched_patterns = []

            for file in self.changed_files:
    pass
                for pattern in patterns:
    pass
                    if self._path_matches_pattern(file, pattern):
    pass
                        should_run = True
                        matched_patterns.append(pattern)
                        break

            selected_groups[group] = should_run

            if should_run:
    pass
                print("  ✅ {group}: Will run (matched: {', '.join(set(matched_patterns))})")
            else:
    pass
                print("  ⏭️ {group}: Skipping (no relevant changes)")

        # Always run security tests if security-related files changed
        security_keywords = ["security", "auth", "crypto", "password", "token", "key"]
        for file in self.changed_files:
    pass
            if any(keyword in file.lower() for keyword in security_keywords):
    pass
                selected_groups["security"] = True
                print("  🛡️ Security tests enabled due to security-related changes")
                break

        return selected_groups

    def generate_matrix(self) -> Dict:
    pass
        """Generate test matrix for GitHub Actions"""
        selected = self.select_tests()

        # Only include groups that should run
        include = []
        for group, should_run in selected.items():
    pass
            if should_run:
    pass
                include.append({"test-group": group})

        # If no tests selected, run at least unit tests
        if not include:
    pass
            include = [{"test-group": "unit"}]
            print("⚠️ No tests selected, defaulting to unit tests")

        matrix = {"include": include}

        pass  # Exception handled} test groups")
        for item in include:
    pass
            print("  - {item['test-group']}")

        return matrix

    def should_skip_build(self) -> bool:
    pass
        """Determine if build can be skipped entirely"""
        if not self.changed_files:
    pass
            return False

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

        non_doc_files = []
        for file in self.changed_files:
    pass
            is_doc_only = any(self._path_matches_pattern(file, pattern) for pattern in doc_only_patterns)
            if not is_doc_only:
    pass
                non_doc_files.append(file)

        if not non_doc_files:
    pass
            print("📚 Only documentation files changed, build can be skipped")
            return True

        return False

def main():
    pass
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
    pass
        skip = selector.should_skip_build()
        if args.output_format == "github":
    pass
            with open(os.environ["GITHUB_OUTPUT"], "a") as gh_out:
    pass
                gh_out.write("skip_build={str(skip).lower()}\n")
        else:
    pass
            print(json.dumps({"skip_build": skip}))
        return

    matrix = selector.generate_matrix()

    if args.output_format == "github":
    pass
        # Output for GitHub Actions using $GITHUB_OUTPUT
        matrix_json = json.dumps(matrix)
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
    pass
            with open(github_output, "a") as gh_out:
    pass
                gh_out.write("matrix={matrix_json}\n")
                # Also output individual test group flags
                selected = selector.select_tests()
                for group, should_run in selected.items():
    pass
                    safe_group = group.replace("-", "_")
                    gh_out.write("run_{safe_group}={str(should_run).lower()}\n")
        else:
    pass
            # Fallback for local runs
            print(json.dumps(matrix, indent=2))
    else:
    pass
        print(json.dumps(matrix, indent=2))

if __name__ == "__main__":
    pass
    main()
