"""CASK chart generation utilities using native Python."""

from __future__ import annotations
import json
from typing import List, Dict, Union, Optional
from .analysis import DataFrameReplacement


class SimpleChart:
    """Lightweight chart representation without external plotting dependencies."""
    
    def __init__(self, chart_type: str, data: Dict, title: str = ""):
        self.chart_type = chart_type
        self.data = data
        self.title = title
    
    def to_dict(self) -> Dict:
        """Convert chart to dictionary representation."""
        return {
            "type": self.chart_type,
            "title": self.title,
            "data": self.data
        }
    
    def to_json(self, filename: str = None) -> str:
        """Convert chart to JSON representation."""
        chart_json = json.dumps(self.to_dict(), indent=2)
        if filename:
            with open(filename, 'w') as f:
                f.write(chart_json)
        return chart_json
    
    def show(self):
        """Display chart information (text representation)."""
        print(f"Chart: {self.title}")
        print(f"Type: {self.chart_type}")
        print(f"Data points: {len(self.data.get('labels', []))}")
        
        if self.chart_type == 'bar':
            labels = self.data.get('labels', [])
            values = self.data.get('values', [])
            max_val = max(values) if values else 1
            for label, value in zip(labels, values):
                bar_length = int(value / max_val * 50) if max_val > 0 else 0
                bar = '█' * bar_length
                print(f"{label:30} {bar} {value}")
        
        elif self.chart_type == 'pie':
            labels = self.data.get('labels', [])
            values = self.data.get('values', [])
            total = sum(values) if values else 0
            for label, value in zip(labels, values):
                percentage = (value / total * 100) if total > 0 else 0
                print(f"{label:30} {percentage:6.1f}% ({value})")


def create_architecture_flowchart(output_file: str = "cask_architecture_flowchart.json") -> SimpleChart:
    """Generate the CASK architecture flowchart."""
    components = {
        "knowledge_layer": [
            "Global Cross-Linguistic Database",
            "Ethics & Value Systems Index",
            "Cultural Cognition Framework",
            "Historical Institutional Systems",
            "Language-to-Symbolic Fusion Layer"
        ],
        "processing_layer": [
            "Symbolic Vector Chain Compressor (SVCC)",
            "GPT Native Encoding Layer",
            "Agent Simulation Generation Module"
        ],
        "validation_layer": [
            "Recursive Ethics Validator",
            "Full ORION Simulation Runtime"
        ]
    }
    
    chart_data = {
        "architecture": components,
        "connections": [
            {"from": "knowledge_layer", "to": "processing_layer"},
            {"from": "processing_layer", "to": "validation_layer"}
        ]
    }
    
    chart = SimpleChart('flowchart', chart_data, 'CASK Technical Architecture')
    chart.to_json(output_file)
    return chart


def create_component_breakdown_chart(df: DataFrameReplacement) -> SimpleChart:
    """Create a breakdown chart of CASK components."""
    components = df.data.get('Component', [])
    
    # Create a simple count-based chart
    component_counts = {}
    for component in components:
        if 'Database' in component or 'Index' in component:
            category = 'Data Storage'
        elif 'Framework' in component or 'Layer' in component:
            category = 'Processing'
        elif 'Module' in component or 'Runtime' in component:
            category = 'Execution'
        elif 'Validator' in component:
            category = 'Validation'
        else:
            category = 'Other'
        
        component_counts[category] = component_counts.get(category, 0) + 1
    
    chart_data = {
        'labels': list(component_counts.keys()),
        'values': list(component_counts.values())
    }
    
    return SimpleChart('pie', chart_data, 'CASK Component Distribution')


def create_specification_complexity_chart(df: DataFrameReplacement) -> SimpleChart:
    """Create a chart showing specification complexity by component."""
    components = df.data.get('Component', [])
    specifications = df.data.get('Technical_Specification', [])
    
    # Measure complexity by character count
    complexity_scores = []
    for spec in specifications:
        if spec:
            complexity = len(spec)
            complexity_scores.append(complexity)
        else:
            complexity_scores.append(0)
    
    chart_data = {
        'labels': [comp[:20] + '...' if len(comp) > 20 else comp for comp in components],
        'values': complexity_scores
    }
    
    return SimpleChart('bar', chart_data, 'Specification Complexity by Component')


def create_research_landscape_chart(output_file: str = "cask_research_landscape.json") -> SimpleChart:
    """Generate the research landscape chart."""
    research_data = [
        {"name": "GPT-4", "technical_maturity": 8, "cultural_awareness": 3, "complexity": "Medium"},
        {"name": "Multi-Agent Trans", "technical_maturity": 6, "cultural_awareness": 7, "complexity": "High"},
        {"name": "CAS Score", "technical_maturity": 5, "cultural_awareness": 8, "complexity": "Medium"},
        {"name": "Neuro-Symbolic", "technical_maturity": 6, "cultural_awareness": 4, "complexity": "High"},
        {"name": "Real-time Trans", "technical_maturity": 8, "cultural_awareness": 5, "complexity": "Medium"},
        {"name": "CASK System", "technical_maturity": 3, "cultural_awareness": 9, "complexity": "Very High"}
    ]
    
    chart_data = {
        "research_landscape": research_data,
        "x_axis": "technical_maturity",
        "y_axis": "cultural_awareness"
    }
    
    chart = SimpleChart('scatter', chart_data, 'Cultural AI Research Landscape')
    chart.to_json(output_file)
    return chart


def create_project_gantt_chart(output_file: str = "cask_gantt_chart.json") -> SimpleChart:
    """Generate the project timeline Gantt chart."""
    tasks = [
        {"task": "Core Ling DB", "start": 1, "end": 12, "phase": "Phase 1: Foundation"},
        {"task": "Cultural Parameters", "start": 6, "end": 15, "phase": "Phase 1: Foundation"},
        {"task": "Prototype Trans", "start": 10, "end": 18, "phase": "Phase 1: Foundation"},
        {"task": "Symbol Fusion", "start": 19, "end": 30, "phase": "Phase 2: Integration"},
        {"task": "SVCC Compression", "start": 24, "end": 33, "phase": "Phase 2: Integration"},
        {"task": "GPT Optimization", "start": 30, "end": 36, "phase": "Phase 2: Integration"},
        {"task": "Ethics Validation", "start": 37, "end": 45, "phase": "Phase 3: Ethics"},
        {"task": "Bias Detection", "start": 42, "end": 48, "phase": "Phase 3: Ethics"},
        {"task": "L1-L2-L3 Architecture", "start": 49, "end": 57, "phase": "Phase 4: Simulation"},
        {"task": "Cultural Integration", "start": 54, "end": 60, "phase": "Phase 4: Simulation"},
        {"task": "Performance Optimization", "start": 61, "end": 72, "phase": "Phase 5: Deployment"},
        {"task": "Security Testing", "start": 72, "end": 81, "phase": "Phase 5: Deployment"}
    ]
    
    chart_data = {
        "tasks": tasks,
        "timeline_months": 84
    }
    
    chart = SimpleChart('gantt', chart_data, 'CASK Project Timeline (84 Months)')
    chart.to_json(output_file)
    return chart


def create_system_architecture_overview() -> SimpleChart:
    """Create an overview chart of the system architecture."""
    architecture_layers = [
        'User Interface Layer',
        'API Gateway',
        'Business Logic',
        'Data Processing',
        'Storage Layer',
        'Infrastructure'
    ]
    
    # Simulated complexity/importance scores
    layer_scores = [15, 25, 40, 35, 20, 30]
    
    chart_data = {
        'labels': architecture_layers,
        'values': layer_scores
    }
    
    return SimpleChart('bar', chart_data, 'System Architecture Overview')


def export_charts_to_json(charts: List[SimpleChart], filename: str):
    """Export multiple charts to a single JSON file."""
    charts_data = {
        'charts': [chart.to_dict() for chart in charts],
        'metadata': {
            'generated_by': 'CASK Charts Module',
            'chart_count': len(charts)
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(charts_data, f, indent=2)


def generate_all_cask_charts(df: DataFrameReplacement) -> List[SimpleChart]:
    """Generate all CASK charts."""
    return [
        create_component_breakdown_chart(df),
        create_specification_complexity_chart(df),
        create_system_architecture_overview(),
        create_architecture_flowchart(),
        create_research_landscape_chart(),
        create_project_gantt_chart()
    ]