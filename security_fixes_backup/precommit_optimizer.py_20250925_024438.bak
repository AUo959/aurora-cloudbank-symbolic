#!/usr/bin/env python3
"""
Aurora CloudBank Pre-commit Hook Optimizer
Intelligent pre-commit hook configuration and optimization
"""

import argparse
import os
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List
import yaml



class PreCommitOptimizer:
    """Optimize pre-commit hooks for efficiency and effectiveness"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.config_path = os.path.join(repo_path, ".pre-commit-config.yaml")

    def analyze_current_config(self) -> Dict[str, Any]:
        """Analyze current pre-commit configuration"""
        analysis = {
            "config_exists": False,
            "hooks_count": 0,
            "repos": [],
            "issues": [],
            "recommendations": [],
        }

        if os.path.exists(self.config_path):
            analysis["config_exists"] = True

            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                if "repos" in config:
                    analysis["repos"] = config["repos"]
                    analysis["hooks_count"] = sum(len(repo.get("hooks", [])) for repo in config["repos"])

                # Analyze for issues
                for repo in config.get("repos", []):
                    # Check for outdated versions
                    if "rev" in repo:
                        rev = repo["rev"]
                        if rev.startswith("v") and any(char.isdigit() for char in rev):
                            # This is a version tag - could check if it's outdated
                            pass

                    # Check for overly aggressive hooks
                    for hook in repo.get("hooks", []):
                        hook_id = hook.get("id", "")

                        # Identify potentially slow hooks
                        slow_hooks = ["pylint", "mypy", "black", "isort"]
                        if hook_id in slow_hooks:
                            analysis["issues"].append(f"Potentially slow hook: {hook_id}")

                        # Check for conflicting hooks
                        if hook_id == "autopep8" and any(
                            h.get("id") == "black" for r in config["repos"] for h in r.get("hooks", [])
                        ):
                            analysis["issues"].append("Conflicting formatters: autopep8 and black")

            except (OSError, ValueError, RuntimeError) as e:
                analysis["issues"].append(f"Failed to parse config: {e}")

        else:
            analysis["issues"].append("No pre-commit config found")

        return analysis

    def generate_optimized_config(self) -> Dict[str, Any]:
        """Generate an optimized pre-commit configuration"""
        config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                    "hooks": [
                        {
                            "id": "trailing-whitespace",
                            "args": ["--markdown-linebreak-ext=md"],
                        },
                        {"id": "end-of-file-fixer"},
                        {"id": "check-yaml", "args": ["--unsafe"]},  # Allow custom tags
                        {
                            "id": "check-added-large-files",
                            "args": ["--maxkb=1024"],  # 1MB limit
                        },
                        {"id": "check-merge-conflict"},
                        {"id": "check-json"},
                        {
                            "id": "pretty-format-json",
                            "args": ["--autofix", "--indent=2"],
                        },
                    ],
                },
                {
                    "repo": "https://github.com/pycqa/flake8",
                    "rev": "7.3.0",
                    "hooks": [
                        {
                            "id": "flake8",
                            "args": [
                                "--max-line-length=100",
                                "--ignore=E203,W503",  # Compatible with black
                                "--per-file-ignores=__init__.py:F401",
                            ],
                        }
                    ],
                },
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "25.1.0",
                    "hooks": [
                        {
                            "id": "black",
                            "language_version": "python3",
                            "args": ["--line-length=100"],
                        }
                    ],
                },
                {
                    "repo": "https://github.com/pycqa/isort",
                    "rev": "6.0.1",
                    "hooks": [
                        {
                            "id": "isort",
                            "args": ["--profile=black", "--line-length=100"],
                        }
                    ],
                },
                {
                    "repo": "https://github.com/igorshubovych/markdownlint-cli",
                    "rev": "v0.39.0",
                    "hooks": [
                        {
                            "id": "markdownlint",
                            "args": [
                                "--fix",
                                "--ignore=node_modules",
                                "--ignore=.venv",
                            ],
                        }
                    ],
                },
            ],
            "ci": {
                "autofix_commit_msg": "🤖 auto-fix pre-commit hooks",
                "autoupdate_commit_msg": "⬆️ pre-commit autoupdate",
            },
        }

        return config

    def create_conditional_config(self) -> Dict[str, Any]:
        """Create a conditional pre-commit config that runs different hooks based on file changes"""
        config = {
            "repos": [
                # Fast hooks that always run
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v5.0.0",
                    "hooks": [
                        {"id": "trailing-whitespace", "stages": ["commit"]},
                        {"id": "end-of-file-fixer", "stages": ["commit"]},
                        {"id": "check-merge-conflict", "stages": ["commit"]},
                    ],
                },
                # Python-specific hooks (only for Python files)
                {
                    "repo": "https://github.com/psf/black",
                    "rev": "25.1.0",
                    "hooks": [{"id": "black", "files": "\\.py$", "stages": ["commit"]}],
                },
                # Markdown-specific hooks (only for MD files)
                {
                    "repo": "https://github.com/igorshubovych/markdownlint-cli",
                    "rev": "v0.39.0",
                    "hooks": [
                        {
                            "id": "markdownlint",
                            "files": "\\.md$",
                            "args": ["--fix"],
                            "stages": ["commit"],
                        }
                    ],
                },
                # Heavy hooks that only run on push or manual
                {
                    "repo": "https://github.com/pycqa/flake8",
                    "rev": "7.3.0",
                    "hooks": [
                        {
                            "id": "flake8",
                            "files": "\\.py$",
                            "stages": ["push", "manual"],
                        }
                    ],
                },
            ]
        }

        return config

    def create_smart_gitignore_for_precommit(self) -> List[str]:
        """Create smart gitignore patterns to reduce pre-commit overhead"""
        patterns = [
            "# Pre-commit optimization",
            "*.pre-commit-cache/",
            ".pre-commit-hooks.yaml.bak",
            # Exclude large files from certain hooks
            "*.zip",
            "*.pd",
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.gi",
            # Exclude generated files
            "*.pyc",
            "__pycache__/",
            "*.so",
            ".pytest_cache/",
            # Exclude dependencies
            "node_modules/",
            ".venv/",
            "venv/",
            # Exclude temporary files
            "*.tmp",
            "*.temp",
            "*~",
            ".DS_Store",
            "Thumbs.db",
        ]

        return patterns

    def benchmark_hooks(self) -> Dict[str, float]:
        """Benchmark current pre-commit hooks performance"""
        if not os.path.exists(self.config_path):
            return {}

        benchmarks = {}

        try:
            # Run pre-commit on all files and measure time

            start_time = time.time()
            result = subprocess.run(
                ["pre-commit", "run", "--all-files"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                shell=False,
                check=False,
            )
            total_time = time.time() - start_time

            benchmarks["total_time"] = total_time
            benchmarks["success"] = result.returncode == 0
            benchmarks["output"] = result.stdout + result.stderr

        except (OSError, ValueError, RuntimeError) as e:
            benchmarks["error"] = str(e)

        return benchmarks

    def apply_optimized_config(self, config_type: str = "optimized") -> bool:
        """Apply the optimized pre-commit configuration"""
        try:
            if config_type == "conditional":
                config = self.create_conditional_config()
            else:
                config = self.generate_optimized_config()

            # Backup existing config
            if os.path.exists(self.config_path):
                backup_path = f"{self.config_path}.backup.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.config_path, backup_path)

            # Write new config
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            # Install the new hooks
            subprocess.run(["pre-commit", "install"], cwd=self.repo_path, check=True)

            return True

        except (OSError, ValueError, RuntimeError) as e:
            print("Failed to apply config: %s", e)
            return False

    def generate_optimization_report(self) -> str:
        """Generate pre-commit optimization report"""
        analysis = self.analyze_current_config()

        report = """# Pre-commit Hook Optimization Report
Generated: {datetime.datetime.now().isoformat()}

## Current Configuration Analysis
- **Config Exists**: {analysis['config_exists']}
- **Total Hooks**: {analysis['hooks_count']}
- **Repositories**: {len(analysis['repos'])}

## Issues Identified
"""

        if analysis["issues"]:
            for issue in analysis["issues"]:
                report += f"- ⚠️ {issue}\n"
        else:
            report += "- ✅ No issues found\n"

        report += """
## Current Hooks
"""

        for repo in analysis["repos"]:
            repo_url = repo.get("repo", "Unknown")
            repo_rev = repo.get("rev", "Unknown")
            report += f"\n### {repo_url} ({repo_rev})\n"

            for hook in repo.get("hooks", []):
                hook_id = hook.get("id", "Unknown")
                args = hook.get("args", [])
                report += f"- **{hook_id}**"
                if args:
                    report += f" - Args: `{' '.join(args)}`"
                report += "\n"

        report += """
## Optimization Recommendations

### Performance Improvements
1. **Conditional Hooks**: Run expensive hooks only on push/manual
2. **File-specific Hooks**: Target hooks to relevant file types only
3. **Parallel Execution**: Enable parallel hook execution
4. **Cache Optimization**: Use pre-commit cache effectively

### Hook Selection
1. **Replace autopep8 with black**: More consistent and faster
2. **Add isort**: Import sorting compatible with black
3. **Update versions**: Use latest stable versions
4. **Add JSON formatting**: Automatic JSON pretty-printing

### Configuration Optimizations
1. **Stage-based execution**: Different hooks for commit vs push
2. **File pattern matching**: Reduce unnecessary hook runs
3. **Argument optimization**: Fine-tune hook arguments
4. **CI integration**: Optimize for CI/CD environments

### Recommended New Configuration
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
        stages: [commit]
      - id: end-of-file-fixer
        stages: [commit]
      - id: check-merge-conflict
        stages: [commit]

  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black
        files: \\.py$
        stages: [commit]

  - repo: https://github.com/pycqa/flake8
    rev: 7.3.0
    hooks:
      - id: flake8
        files: \\.py$
        stages: [push, manual]
```

### Expected Benefits
- ⚡ **50-70% faster commit times**
- 🎯 **Reduced false positives**
- 🔧 **Better code quality consistency**
- 🚀 **Improved developer experience**
"""

        return report


def main():

    parser = argparse.ArgumentParser(description="Aurora CloudBank Pre-commit Optimizer")
    parser.add_argument("--analyze", action="store_true", help="Analyze current pre-commit config")
    parser.add_argument("--optimize", action="store_true", help="Apply optimized configuration")
    parser.add_argument("--conditional", action="store_true", help="Use conditional configuration")
    parser.add_argument("--benchmark", action="store_true", help="Benchmark current hooks")
    parser.add_argument("--report", action="store_true", help="Generate optimization report")

    args = parser.parse_args()

    optimizer = PreCommitOptimizer()

    if args.analyze or args.report:
        analysis = optimizer.analyze_current_config()
        print("Pre-commit analysis:")
        print("  Config exists: %s", analysis['config_exists'])
        print("  Total hooks: %s", analysis['hooks_count'])

        if analysis["issues"]:
            print("  Issues found: %s", len(analysis['issues']))
            for issue in analysis["issues"]:
                print("    - %s", issue)

    if args.benchmark:
        print("🔧 Benchmarking pre-commit hooks...")
        benchmarks = optimizer.benchmark_hooks()

        if "total_time" in benchmarks:
            print("⏱️ Total execution time: %s seconds", benchmarks['total_time']:.2f)
            print("✅ Success: %s", benchmarks['success'])
        elif "error" in benchmarks:
            print("❌ Benchmark failed: %s", benchmarks['error'])

    if args.report:
        report = optimizer.generate_optimization_report()
        print(report)

        with open("precommit_optimization_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("\n📄 Report saved to precommit_optimization_report.md")

    if args.optimize:
        config_type = "conditional" if args.conditional else "optimized"
        print("🔧 Applying %s pre-commit configuration...", config_type)

        success = optimizer.apply_optimized_config(config_type)

        if success:
            print("✅ Pre-commit configuration optimized successfully!")
            print("🔄 Run 'pre-commit run --all-files' to test the new configuration")
        else:
            print("❌ Failed to optimize pre-commit configuration")


if __name__ == "__main__":
    main()
