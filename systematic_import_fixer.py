#!/usr/bin/env python3
"""
Systematic Import Fixer for Aurora CloudBank
Addresses 791 undefined name errors by adding missing imports
"""

import ast
import os
import re

from collections import defaultdict


class ImportFixer:
    pass
    def __init__(self, repo_path: str = "."):
    pass
        self.repo_path = Path(repo_path)

        # Enhanced import mappings for remaining issues
        self.import_mappings = {
            # Type annotations (top priority - 96+53+44 = 193 issues)
            "Dict": "from typing import Dict",
            "List": "from typing import List",
            "Any": "from typing import Any",
            "Optional": "from typing import Optional",
            "Union": "from typing import Union",
            "Callable": "from typing import Callable",
            "Tuple": "from typing import Tuple",
            "Set": "from typing import Set",
            # Standard library (enhanced)
            "subprocess": "import subprocess",
            "Path": "from pathlib import Path",
            "datetime": "import datetime",
            "json": "import json",
            "sys": "import sys",
            "os": "import os",
            "re": "import re",
            "time": "import time",
            "logging": "import logging",
            "argparse": "import argparse",
            "random": "import random",
            "hashlib": "import hashlib",
            "shutil": "import shutil",
            "tempfile": "import tempfile",
            "uuid": "import uuid",
            "threading": "import threading",
            "multiprocessing": "import multiprocessing",
            "concurrent": "import concurrent.futures",
            "asyncio": "import asyncio",
            "gzip": "import gzip",
            "zipfile": "import zipfile",
            "shlex": "import shlex",
            "sched": "import sched",
            "traceback": "import traceback",
            "timedelta": "from datetime import timedelta",
            "defaultdict": "from collections import defaultdict",
            # IO operations
            "StringIO": "from io import StringIO",
            # FastAPI/web (34+10 = 44 issues)
            "HTTPException": "from fastapi import HTTPException",
            "JSONResponse": "from fastapi.responses import JSONResponse",
            "HTMLResponse": "from fastapi.responses import HTMLResponse",
            "Request": "from fastapi import Request",
            "Response": "from fastapi import Response",
            "Depends": "from fastapi import Depends",
            "FastAPI": "from fastapi import FastAPI",
            "StaticFiles": "from fastapi.staticfiles import StaticFiles",
            "WebSocket": "from fastapi import WebSocket",
            "WebSocketDisconnect": "from fastapi import WebSocketDisconnect",
            "uvicorn": "import uvicorn",
            # Data science
            "np": "import numpy as np",
            "pd": "import pandas as pd",
            "plt": "import matplotlib.pyplot as plt",
            # Dataclasses and pydantic
            "dataclass": "from dataclasses import dataclass",
            "field": "from dataclasses import field",
            "asdict": "from dataclasses import asdict",
            "Field": "from pydantic import Field",
            "BaseModel": "from pydantic import BaseModel",
            # Third party common
            "yaml": "import yaml",
            "toml": "import toml",
            "schedule": "import schedule",
            "requests": "import requests",
            "click": "import click",
            "pytest": "import pytest",
            # File system watching
            "Observer": "from watchdog.observers import Observer",
            "FileSystemEventHandler": "from watchdog.events import FileSystemEventHandler",
            # Qiskit quantum computing
            "QuantumCircuit": "from qiskit import QuantumCircuit",
            "AerSimulator": "from qiskit_aer import AerSimulator",
            # Project-specific patterns (make these conditional imports)
            "CanonicalValidator": "from .canonical_validator import CanonicalValidator",
            "ValidationManager": "from .canonical_validator import ValidationManager",
            "EnhancedGITWiz": "from .gitwiz_enhanced import GitWizEnhanced as EnhancedGITWiz",
            "GITWizWorkflowOrchestrator": "from .gitwiz_workflow_orchestrator import GITWizWorkflowOrchestrator",
            "LintCleanupManager": "from .gitwiz_lint_cleanup_manager import LintCleanupManager",
            "BranchCleanupManager": "from .branch_cleanup_automation import BranchCleanupManager",
            "RepositoryHealthMonitor": "from .repository_health_monitor_v2 import RepositoryHealthMonitor",
            # Aurora-specific classes
            "NativeSymbolicVector": "from src.core.native_vsa import NativeSymbolicVector",
            "NativeVSAMemory": "from src.core.native_vsa import NativeVSAMemory",
            "NativeQuantumCircuit": "from src.core.native_quantum import NativeQuantumCircuit",
            "NativeQuantumProcessingLayer": "from src.quantum_core.quantum_processing_layer import NativeQuantumProcessingLayer",
            "NativeSymbolicCPUAnchor": "from src.quantum_core.symbolic_cpu_anchor import NativeSymbolicCPUAnchor",
            "SymbolicAnchorTracker": "from tools.symbolic.anchor_tracker import SymbolicAnchorTracker",
            "MemorySealingEngine": "from tools.symbolic.memory_sealer import MemorySealingEngine",
            "ManifestGenerator": "from tools.symbolic.manifest_generator import ManifestGenerator",
            "AuroraDeveloperCLI": "from tools.cli.aurora_dev_cli import AuroraDeveloperCLI",
            # Opal2-specific
            "QuantumRenderer": "from modules.opal2.quantum_renderer import QuantumRenderer",
            "PluginSystem": "from modules.opal2.plugin_system import PluginSystem",
            "GlyphCore": "from modules.opal2.glyph_core import GlyphCore",
            "SymbolicCore": "from modules.symbolic_core import SymbolicCore",
            "GlyphCache": "from modules.opal2.glyph_cache import GlyphCache",
            # Bridge systems
            "auroraCustomGptBridge": "from src.integrations.chatgpt_agent_mode import auroraCustomGptBridge",
            "AURORA_CUSTOM_GPT": "from src.integrations.chatgpt_agent_mode import AURORA_CUSTOM_GPT",
            # System monitoring
            "ps": "import psutil as ps",
            # Helper functions and logging
            "get_logger": "from logging import getLogger as get_logger",
        }

    def analyze_file_imports(self, file_path: Path) -> tuple:
    pass
        """Analyze what imports a file needs and already has"""
        try:
    pass
            with open(file_path, "r", encoding="utf-8") as f:
    pass
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
    pass
            return set(), set(), content

        # Get undefined names from flake8
        undefined_names = self.get_undefined_names(file_path)

        # Get existing imports
        existing_imports = self.get_existing_imports(content)

        return undefined_names, existing_imports, content

    def get_undefined_names(self, file_path: Path) -> set:
    pass
        """Get undefined names for a specific file using flake8"""
        try:
    pass
            result = subprocess.run(
                ["flake8", "--select=F821", "--format=%(text)s", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            undefined_names = set()
            for line in result.stdout.strip().split("\n"):
    pass
                if line and "undefined name" in line:
    pass
                    # Extract name from "undefined name 'name'"
                    match = re.search(r"undefined name '([^']+)'", line)
                    if match:
    pass
                        undefined_names.add(match.group(1))

            return undefined_names
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
    pass
            return set()

    def get_existing_imports(self, content: str) -> set:
    pass
        """Extract existing import statements"""
        existing_imports = set()

        # Find import lines
        import_lines = []
        for line in content.split("\n"):
    pass
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
    pass
                import_lines.append(line)

        # Extract imported names
        for line in import_lines:
    pass
            if line.startswith("import "):
    pass
                # import module [as alias]
                parts = line.split()
                if len(parts) >= 2:
    pass
                    module = parts[1].split(".")[0]
                    existing_imports.add(module)
                    if "as" in parts and len(parts) >= 4:
    pass
                        existing_imports.add(parts[3])

            elif line.startswith("from "):
    pass
                # from module import name [as alias]
                match = re.match(r"from\s+[\w.]+\s+import\s+(.+)", line)
                if match:
    pass
                    imports_part = match.group(1)
                    # Handle multiple imports
                    for item in imports_part.split(","):
    pass
                        item = item.strip()
                        if " as " in item:
    pass
                            alias = item.split(" as ")[-1].strip()
                            existing_imports.add(alias)
                        else:
    pass
                            existing_imports.add(item.strip())

        return existing_imports

    def add_imports_to_file(self, file_path: Path, needed_imports: list) -> bool:
    pass
        """Add imports to a file in the appropriate location"""
        try:
    pass
            with open(file_path, "r", encoding="utf-8") as f:
    pass
                lines = f.readlines()
        except (UnicodeDecodeError, PermissionError):
    pass
            return False

        # Find the insertion point (after shebang, docstring, and existing imports)
        insert_line = 0
        in_docstring = False
        docstring_quotes = None

        for i, line in enumerate(lines):
    pass
            stripped = line.strip()

            # Skip shebang
            if i == 0 and stripped.startswith("#!"):
    pass
                insert_line = i + 1
                continue

            # Handle docstrings
            if not in_docstring:
    pass
                if stripped.startswith('"""') or stripped.startswith("'''"):
    pass
                    docstring_quotes = stripped[:3]
                    if stripped.count(docstring_quotes) >= 2:
    pass
                        # Single line docstring
                        insert_line = i + 1,
                    else:
    pass
                        # Multi-line docstring starts
                        in_docstring = True
                    continue,
            else:
    pass
                if docstring_quotes in stripped:
    pass
                    # Multi-line docstring ends
                    in_docstring = False
                    insert_line = i + 1
                continue

            # Skip existing imports
            if stripped.startswith("import ") or stripped.startswith("from "):
    pass
                insert_line = i + 1
                continue

            # Skip empty lines and comments after imports
            if not stripped or stripped.startswith("#"):
    pass
                continue

            # Found first non-import, non-comment line
            break

        # Insert imports
        import_lines = [import_stmt + "\n" for import_stmt in needed_imports]
        if needed_imports:
    pass
            import_lines.append("\n")  # Add blank line after imports

        lines[insert_line:insert_line] = import_lines

        # Write back,
        try:
    pass
            with open(file_path, "w", encoding="utf-8") as f:
    pass
                f.writelines(lines)
            return True
        except PermissionError:
    pass
            return False

    def fix_file(self, file_path: Path) -> dict:
    pass
        """Fix imports for a single file"""
        undefined_names, existing_imports, content = self.analyze_file_imports(file_path)

        if not undefined_names:
    pass
            return {"status": "no_issues", "added": []}

        # Determine what imports to add
        imports_to_add = []
        names_fixed = []

        for name in undefined_names:
    pass
            if name in existing_imports:
    pass
                continue  # Already imported

            if name in self.import_mappings:
    pass
                import_stmt = self.import_mappings[name]
                if import_stmt not in imports_to_add:
    pass
                    imports_to_add.append(import_stmt)
                    names_fixed.append(name)

        if not imports_to_add:
    pass
            return {"status": "no_mappings", "undefined": list(undefined_names)}

        # Add imports
        success = self.add_imports_to_file(file_path, imports_to_add)

        return {
            "status": "success" if success else "failed",
            "added": imports_to_add,
            "fixed_names": names_fixed,
            "remaining": list(undefined_names - set(names_fixed)),
        }

    def fix_repository(self, file_patterns: list = None) -> dict:
    pass
        """Fix imports across the repository"""
        if file_patterns is None:
    pass
            file_patterns = ["**/*.py"]

        python_files = []
        for pattern in file_patterns:
    pass
            python_files.extend(self.repo_path.glob(pattern))

        # Filter out disabled files and hidden directories
        python_files = [
            f
            for f in python_files
            if not f.name.endswith(".disabled") and not any(part.startswith(".") for part in f.parts)
        ]

        results = {
            "files_processed": 0,
            "files_fixed": 0,
            "total_imports_added": 0,
            "total_names_fixed": 0,
            "files_with_issues": [],
        }

        for file_path in python_files:
    pass
            try:
    pass
                result = self.fix_file(file_path)
                results["files_processed"] += 1

                if result["status"] == "success":
    pass
                    results["files_fixed"] += 1
                    results["total_imports_added"] += len(result["added"])
                    results["total_names_fixed"] += len(result["fixed_names"])

                    print(
                        "✅ {file_path.relative_to(self.repo_path)}: "
                        "Added {len(result['added'])} imports, "
                        "fixed {len(result['fixed_names'])} names"
                    )

                elif result["status"] == "no_issues":
    pass
                    print("✓ {file_path.relative_to(self.repo_path)}: No issues")

                elif result["status"] == "no_mappings":
    pass
                    print("⚠️ {file_path.relative_to(self.repo_path)}: " "Unknown imports needed: {result['undefined']}")
                    results["files_with_issues"].append(
                        {"file": str(file_path.relative_to(self.repo_path)), "undefined": result["undefined"]}
                    )

                else:
    pass
                    print("❌ {file_path.relative_to(self.repo_path)}: Failed to fix")

            except Exception as _:
    pass
                print("❌ {file_path.relative_to(self.repo_path)}: Error - {e}")

        return results

def main():
    pass
    print("🔧 Aurora CloudBank Systematic Import Fixer")
    print("=" * 50)

    fixer = ImportFixer()

    # Start with high-impact files first
    high_priority_patterns = ["aurora_*.py", "scripts/*.py", "modules/**/*.py", "src/**/*.py"]

    print("Phase 1: Fixing high-priority files...")
    results = fixer.fix_repository(high_priority_patterns)

    print("\n📊 Phase 1 Results:")
    print("Files processed: {results['files_processed']}")
    print("Files fixed: {results['files_fixed']}")
    print("Total imports added: {results['total_imports_added']}")
    print("Total names fixed: {results['total_names_fixed']}")

    if results["files_with_issues"]:
    pass
        print("\n⚠️ Files needing manual attention: {len(results['files_with_issues'])}")
        for issue in results["files_with_issues"][:5]:  # Show first 5
            print("  - {issue['file']}: {issue['undefined']}")

    print("\nPhase 2: Fixing remaining files...")
    results2 = fixer.fix_repository(["**/*.py"])

    print("\n📊 Final Results:")
    print("Total files processed: {results2['files_processed']}")
    print("Total files fixed: {results2['files_fixed']}")
    print("Total imports added: {results2['total_imports_added']}")
    print("Total names fixed: {results2['total_names_fixed']}")

if __name__ == "__main__":
    pass
    main()
