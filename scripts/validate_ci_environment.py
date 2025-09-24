#!/usr/bin/env python3
"""
CI Environment Validation Script
===============================

Validates that all required lint tools are properly installed and functional
in the CI environment. This script helps ensure consistency between local
development and CI environments.

Usage:
    python validate_ci_environment.py
    python validate_ci_environment.py --fix-missing

Author: Aurora/ORION Core
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple



class CIEnvironmentValidator:
    """Validates and optionally fixes CI environment setup."""

    def __init__(self):
        self.required_python_tools = ["flake8", "black", "isort", "pylint", "bandit", "autopep8"]
        self.required_node_tools = ["eslint", "prettier", "markdownlint"]
        self.results = {
            "python_tools": {},
            "node_tools": {},
            "overall_status": "unknown",
            "missing_tools": [],
            "recommendations": [],
        }

    def check_tool_availability(self, tool: str) -> Tuple[bool, str]:
        """Check if a tool is available and get version."""
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip().split("\n")[0]
                return True, version
            return False, f"Exit code: {result.returncode}"
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False, "Not found or timeout"

    def validate_python_tools(self) -> None:
        """Validate Python lint tools."""
        print("🐍 Validating Python tools...")
        for tool in self.required_python_tools:
            available, info = self.check_tool_availability(tool)
            self.results["python_tools"][tool] = {
                "available": available,
                "version": info if available else None,
                "error": info if not available else None,
            }
            status = "✅" if available else "❌"
            print("  {status} {tool}: %s", info)
            if not available:
                self.results["missing_tools"].append(f"python:{tool}")

    def validate_node_tools(self) -> None:
        """Validate Node.js lint tools."""
        print("\n📦 Validating Node.js tools...")

        # Check if npm is available first
        npm_available, npm_info = self.check_tool_availability("npm")
        if not npm_available:
            print("  ❌ npm not available - skipping Node.js tools")
            for tool in self.required_node_tools:
                self.results["node_tools"][tool] = {"available": False, "version": None, "error": "npm not available"}
            return

        print("  ✅ npm: %s", npm_info)

        for tool in self.required_node_tools:
            available, info = self.check_tool_availability(tool)
            self.results["node_tools"][tool] = {
                "available": available,
                "version": info if available else None,
                "error": info if not available else None,
            }
            status = "✅" if available else "❌"
            print("  {status} {tool}: %s", info)
            if not available:
                self.results["missing_tools"].append(f"node:{tool}")

    def generate_recommendations(self) -> None:
        """Generate recommendations for fixing issues."""
        if not self.results["missing_tools"]:
            self.results["recommendations"].append("✅ All required tools are available")
            self.results["overall_status"] = "success"
            return

        self.results["overall_status"] = "issues_found"

        python_missing = [t.split(":")[1] for t in self.results["missing_tools"] if t.startswith("python:")]
        node_missing = [t.split(":")[1] for t in self.results["missing_tools"] if t.startswith("node:")]

        if python_missing:
            tools_str = " ".join(python_missing)
            self.results["recommendations"].append(f"Install missing Python tools: pip install {tools_str}")

        if node_missing:
            tools_str = " ".join(node_missing)
            self.results["recommendations"].append(f"Install missing Node.js tools: npm install -g {tools_str}")

    def test_gitwiz_integration(self) -> None:
        """Test GitWiz integration if available."""
        print("\n🔧 Testing GitWiz integration...")
        gitwiz_script = Path("scripts/gitwiz_integrated_command.py")

        if not gitwiz_script.exists():
            print("  ❌ GitWiz integrated command not found")
            self.results["gitwiz_status"] = "not_found"
            return

        try:
            result = subprocess.run(
                [sys.executable, str(gitwiz_script), "status"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=gitwiz_script.parent.parent,
            )

            if result.returncode == 0:
                print("  ✅ GitWiz status check successful")
                self.results["gitwiz_status"] = "working"

                # Try to parse the JSON output
                try:
                    # Find the JSON output in the stdout
                    lines = result.stdout.strip().split("\n")
                    json_line = None
                    for line in lines:
                        if line.strip().startswith("{"):
                            json_line = line.strip()
                            break

                    if json_line:
                        gitwiz_data = json.loads(json_line)
                        capabilities = gitwiz_data.get("capabilities", {}).get("lint_tools", {})
                        working_tools = sum(1 for tool, status in capabilities.items() if status)
                        total_tools = len(capabilities)
                        print("  📊 GitWiz detects {working_tools}/%s tools available", total_tools)
                        self.results["gitwiz_tools_detected"] = f"{working_tools}/{total_tools}"
                    else:
                        print("  ⚠️  No JSON output found in GitWiz response")
                        self.results["gitwiz_tools_detected"] = "unknown"
                except (json.JSONDecodeError, IndexError, KeyError) as e:
                    print("  ⚠️  GitWiz output parsing failed: %s", e)
                    self.results["gitwiz_tools_detected"] = "parse_error"
            else:
                print("  ❌ GitWiz status check failed (exit code: %s)", result.returncode)
                print("  Error: %s", result.stderr)
                self.results["gitwiz_status"] = "failed"
        except subprocess.TimeoutExpired:
            print("  ❌ GitWiz status check timed out")
            self.results["gitwiz_status"] = "timeout"
        except Exception as e:
            print("  ❌ GitWiz test error: %s", e)
            self.results["gitwiz_status"] = "error"

    def validate(self) -> Dict:
        """Run complete validation."""
        print("🔍 CI Environment Validation Starting...\n")

        self.validate_python_tools()
        self.validate_node_tools()
        self.test_gitwiz_integration()
        self.generate_recommendations()

        print("\n" + "=" * 60)
        print("📊 Overall Status: %s", self.results['overall_status'].upper())

        if self.results["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in self.results["recommendations"]:
                print("  %s", rec)

        return self.results

    def fix_missing_tools(self) -> None:
        """Attempt to install missing tools."""
        if not self.results["missing_tools"]:
            print("✅ No missing tools to install")
            return

        print("🔧 Attempting to install missing tools...")

        python_missing = [t.split(":")[1] for t in self.results["missing_tools"] if t.startswith("python:")]
        node_missing = [t.split(":")[1] for t in self.results["missing_tools"] if t.startswith("node:")]

        if python_missing:
            print("Installing Python tools: %s", ' '.join(python_missing))
            try:
                subprocess.run([sys.executable, "-m", "pip", "install"] + python_missing, check=True)
                print("✅ Python tools installed successfully")
            except subprocess.CalledProcessError as e:
                print("❌ Failed to install Python tools: %s", e)

        if node_missing and shutil.which("npm"):
            print("Installing Node.js tools: %s", ' '.join(node_missing))
            try:
                subprocess.run(["npm", "install", "-g"] + node_missing, check=True)
                print("✅ Node.js tools installed successfully")
            except subprocess.CalledProcessError as e:
                print("❌ Failed to install Node.js tools: %s", e)


def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="Validate CI environment setup")
    parser.add_argument("--fix-missing", action="store_true", help="Attempt to install missing tools")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    validator = CIEnvironmentValidator()
    results = validator.validate()

    if args.fix_missing and results["missing_tools"]:
        print("\n" + "=" * 60)
        validator.fix_missing_tools()

        # Re-validate after fixing
        print("\n🔄 Re-validating after fixes...")
        results = validator.validate()

    if args.output == "json":
        print("\n" + json.dumps(results, indent=2))

    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "success" else 1)


if __name__ == "__main__":
    main()
