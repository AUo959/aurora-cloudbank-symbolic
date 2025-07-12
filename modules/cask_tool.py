#!/usr/bin/env python3
"""Utilities for interacting with the CASK reference assets.

This module loads data from ``CASK_Assets.zip`` and provides helper
functions to parse the included CSV files as native Python data structures.
It can also generate a simplified architecture chart for quick visualization.
"""

from __future__ import annotations

import os
import zipfile
import csv
import io
from typing import List, Dict, Any

# Handle relative imports for both module and standalone execution
try:
    from .cask.analysis import DataFrameReplacement
except ImportError:
    from cask.analysis import DataFrameReplacement

ASSET_ZIP = "CASK_Assets.zip"


def _open_asset(name: str) -> str:
    """Return the contents of ``name`` within ``ASSET_ZIP`` as a string."""
    if not os.path.exists(ASSET_ZIP):
        raise FileNotFoundError(f"{ASSET_ZIP} not found")
    try:
        with zipfile.ZipFile(ASSET_ZIP) as zf:
            with zf.open(name) as file:
                return file.read().decode("utf-8")
    except KeyError:
        raise FileNotFoundError(f"{name} not found in {ASSET_ZIP}")


def load_specifications() -> DataFrameReplacement:
    """Load the CASK technical specifications table."""
    try:
        csv_content = _open_asset("cask_specifications.csv")
        
        # Parse CSV content
        reader = csv.DictReader(io.StringIO(csv_content))
        data = {}
        
        # Initialize columns
        for row in reader:
            for key in row.keys():
                if key not in data:
                    data[key] = []
        
        # Reset reader and read data
        reader = csv.DictReader(io.StringIO(csv_content))
        for row in reader:
            for key, value in row.items():
                data[key].append(value)
        
        return DataFrameReplacement(data)
        
    except FileNotFoundError:
        # Return sample data if asset file not found
        try:
            from .cask.analysis import generate_technical_specifications
        except ImportError:
            from cask.analysis import generate_technical_specifications
        return generate_technical_specifications()


def load_research_landscape() -> DataFrameReplacement:
    """Load the research landscape comparison data."""
    try:
        csv_content = _open_asset("research_landscape.csv")
        reader = csv.DictReader(io.StringIO(csv_content))
        data = {}
        
        for row in reader:
            for key in row.keys():
                if key not in data:
                    data[key] = []
        
        reader = csv.DictReader(io.StringIO(csv_content))
        for row in reader:
            for key, value in row.items():
                data[key].append(value)
        
        return DataFrameReplacement(data)
        
    except FileNotFoundError:
        # Return sample data if asset file not found
        sample_data = {
            "System": ["GPT-4", "Multi-Agent", "CASK", "Neuro-Symbolic"],
            "Technical_Maturity": [8, 6, 3, 6],
            "Cultural_Awareness": [3, 7, 9, 4],
            "Complexity": ["Medium", "High", "Very High", "High"]
        }
        return DataFrameReplacement(sample_data)


def load_project_timeline() -> DataFrameReplacement:
    """Load the project timeline data."""
    try:
        csv_content = _open_asset("project_timeline.csv")
        reader = csv.DictReader(io.StringIO(csv_content))
        data = {}
        
        for row in reader:
            for key in row.keys():
                if key not in data:
                    data[key] = []
        
        reader = csv.DictReader(io.StringIO(csv_content))
        for row in reader:
            for key, value in row.items():
                data[key].append(value)
        
        return DataFrameReplacement(data)
        
    except FileNotFoundError:
        # Return sample data if asset file not found
        sample_data = {
            "Task": ["Core Database", "Cultural Framework", "Symbol Fusion", "Ethics Validation"],
            "Start_Month": [1, 6, 19, 37],
            "End_Month": [12, 15, 30, 45],
            "Phase": ["Foundation", "Foundation", "Integration", "Ethics"]
        }
        return DataFrameReplacement(sample_data)


def generate_architecture_chart(output_format: str = "json") -> str:
    """Generate a simplified CASK architecture chart."""
    try:
        from .cask.charts_native import create_architecture_flowchart
    except ImportError:
        from cask.charts_native import create_architecture_flowchart
    
    if output_format == "json":
        chart = create_architecture_flowchart("cask_architecture.json")
        return "cask_architecture.json"
    else:
        # Text-based representation
        architecture_text = """
CASK Architecture Overview:

Knowledge Layer:
├── Global Cross-Linguistic Database
├── Ethics & Value Systems Index
├── Cultural Cognition Framework
├── Historical Institutional Systems
└── Language-to-Symbolic Fusion Layer

Processing Layer:
├── Symbolic Vector Chain Compressor (SVCC)
├── GPT Native Encoding Layer
└── Agent Simulation Generation Module

Validation Layer:
├── Recursive Ethics Validator
└── Full ORION Simulation Runtime
"""
        return architecture_text


def export_all_data(output_dir: str = "cask_export") -> List[str]:
    """Export all CASK data to files."""
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    exported_files = []
    
    # Export specifications
    specs = load_specifications()
    specs_file = os.path.join(output_dir, "specifications.csv")
    specs.to_csv(specs_file)
    exported_files.append(specs_file)
    
    # Export research landscape
    research = load_research_landscape()
    research_file = os.path.join(output_dir, "research_landscape.csv")
    research.to_csv(research_file)
    exported_files.append(research_file)
    
    # Export timeline
    timeline = load_project_timeline()
    timeline_file = os.path.join(output_dir, "project_timeline.csv")
    timeline.to_csv(timeline_file)
    exported_files.append(timeline_file)
    
    # Export architecture chart
    arch_file = os.path.join(output_dir, "architecture.json")
    generate_architecture_chart(output_format="json")
    if os.path.exists("cask_architecture.json"):
        import shutil
        shutil.move("cask_architecture.json", arch_file)
        exported_files.append(arch_file)
    
    return exported_files


def print_summary():
    """Print a summary of CASK data."""
    print("CASK (Culturally Aware Simulation Knowledge) Summary")
    print("=" * 50)
    
    specs = load_specifications()
    print(f"Technical Specifications: {len(specs.index)} components")
    
    research = load_research_landscape()
    print(f"Research Landscape: {len(research.index)} systems compared")
    
    timeline = load_project_timeline()
    print(f"Project Timeline: {len(timeline.index)} tasks defined")
    
    print("\nArchitecture Layers:")
    print("- Knowledge Layer (5 components)")
    print("- Processing Layer (3 components)")
    print("- Validation Layer (2 components)")


if __name__ == "__main__":
    print_summary()