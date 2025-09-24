# Extracted script from feature/digital-ghost-dlp-sonar
# Original path: scripts/architectural_sonar.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Architectural Sonar: A proactive tool for detecting architectural drift and code entropy.

This script analyzes the Aurora CloudBank Symbolic codebase to ensure it adheres to
the canonical patterns and architectural guidelines defined in project documentation.
It detects deviations such as incorrect dependencies, declining code quality, and
pattern violations, generating reports to facilitate predictive refactoring.
"""

import ast
import json
import os
import subprocess
from pathlib import Path
import importlib

# Dynamic imports to avoid static analysis import errors in lean environments
try:
    yaml = importlib.import_module("yaml")
except Exception:  # Degrade gracefully if PyYAML isn't available
    yaml = None  # type: ignore[assignment]

try:
    _radon_complexity = importlib.import_module("radon.complexity")
    _radon_metrics = importlib.import_module("radon.metrics")
    cc_rank = getattr(_radon_complexity, "cc_rank")
    mi_rank = getattr(_radon_metrics, "mi_rank")
except Exception:
    # Provide minimal fallbacks so the script can still run
    def cc_rank(value):  # type: ignore
        return "N/A"

    def mi_rank(value):  # type: ignore
        return "N/A"


# --- Configuration ---
# It's better to move these to a separate config file later
# For now, let's define them here.
WORKSPACE_ROOT = Path(__file__).parent.parent
SRC_DIRS = [WORKSPACE_ROOT / "src", WORKSPACE_ROOT / "modules"]
ARCH_BLUEPRINT_FILE = WORKSPACE_ROOT / "AU_CORE_MASTER_TREE.yaml"
COPILOT_INSTRUCTIONS = WORKSPACE_ROOT / ".github/copilot-instructions.md"
REPORT_OUTPUT_FILE = WORKSPACE_ROOT / "reports/architectural_sonar_report.json"


# --- Helper Functions ---

def get_python_files(directories):
    """Yields all .py files in the given directories."""
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    yield Path(root) / file


def parse_architecture_blueprint(file_path):
    """Parses the YAML file defining the core architecture."""
    try:
        with open(file_path, 'r') as f:
            if yaml is None:
                print("Warning: PyYAML not available; skipping blueprint parse.")
                return None
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Architecture blueprint not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error parsing YAML blueprint: {e}")
        return None


# --- Analysis Functions ---

def analyze_dependencies(file_path, allowed_dependencies):
    """
    Analyzes a file's imports to check for architectural violations.
    (This is a placeholder for a more sophisticated implementation)
    """
    violations = []
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read(), filename=str(file_path))
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Basic check: does the import violate defined boundaries?
                # A real implementation would need a graph of module dependencies.
                pass  # Placeholder
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module:
                # More complex check needed here based on the blueprint
                pass  # Placeholder
    return violations


def analyze_code_metrics(file_path):
    """
    Calculates code metrics (Cyclomatic Complexity, Maintainability Index) for a file.
    """
    metrics = {}
    try:
        # Using radon via subprocess to handle file-by-file analysis easily
        # This is a bit slow but robust.
        cc_data = []
        mi_data = {}
        try:
            cc_result = subprocess.check_output(
                ["radon", "cc", "-s", "-j", str(file_path)],
                encoding='utf-8'
            )
            cc_data = json.loads(cc_result).get(str(file_path), [])
        except Exception:
            pass

        try:
            mi_result = subprocess.check_output(
                ["radon", "mi", "-s", "-j", str(file_path)],
                encoding='utf-8'
            )
            mi_data = json.loads(mi_result).get(str(file_path), {})
        except Exception:
            pass

        total_cc = sum(item.get('complexity', 0) for item in cc_data)
        average_cc = total_cc / len(cc_data) if cc_data else 0
        
        metrics = {
            "maintainability_index": mi_data.get("mi", 0),
            "mi_rank": mi_rank(mi_data.get("mi", 0)),
            "cyclomatic_complexity_avg": average_cc,
            "cc_rank": cc_rank(average_cc)
        }

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not analyze metrics for {file_path}: {e}")
        metrics = {"error": str(e)}

    return metrics


def analyze_pattern_adherence(file_path):
    """
    Checks for adherence to project-specific patterns (e.g., DLP tagging).
    (This is a placeholder for a more sophisticated implementation)
    """
    violations = []
    # Example check: Ensure symbolic operations use NativeDLPTracker
    # A real implementation would use the AST to find function calls and check context.
    with open(file_path, 'r') as f:
        content = f.read()
        if "symbolic_operation" in content and "NativeDLPTracker" not in content:
            violations.append({
                "type": "PatternViolation",
                "message": "A symbolic operation may be missing NativeDLPTracker instrumentation."
            })
    return violations


# --- Main Orchestrator ---

def main():
    """Main function to run the architectural sonar."""
    print("🚀 Starting Architectural Sonar scan...")
    
    blueprint = parse_architecture_blueprint(ARCH_BLUEPRINT_FILE)
    if not blueprint:
        print("Aborting scan due to missing or invalid architecture blueprint.")
        return

    all_results = {}
    python_files = list(get_python_files(SRC_DIRS))
    print(f"Found {len(python_files)} Python files to analyze.")

    for i, file_path in enumerate(python_files):
        relative_path = file_path.relative_to(WORKSPACE_ROOT)
        print(f"[{i+1}/{len(python_files)}] Analyzing: {relative_path}")

        # In a real implementation, 'allowed_deps' would be derived from the blueprint
        allowed_deps = []
        
        dependency_violations = analyze_dependencies(file_path, allowed_deps)
        metrics = analyze_code_metrics(file_path)
        pattern_violations = analyze_pattern_adherence(file_path)

        all_results[str(relative_path)] = {
            "metrics": metrics,
            "violations": {
                "dependencies": dependency_violations,
                "patterns": pattern_violations
            }
        }

    # --- Reporting ---
    REPORT_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_OUTPUT_FILE, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Scan complete. Report generated at: {REPORT_OUTPUT_FILE}")
    # Here you could add logic to summarize findings and print a high-level report.


if __name__ == "__main__":
    # Run regardless; internal checks will degrade gracefully
    main()
