#!/usr/bin/env python3
"""Build Synergy Dashboard from registry and repo files with Prometheus/OpenTelemetry metrics."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import datetime
import urllib.parse

try:
    import requests
except Exception:
    requests = None  # Fallback when requests isn't available in GH Actions runtime

# -----------------------
# Configuration
# -----------------------
PROMETHEUS_QUERY_URL = os.getenv("PROMETHEUS_QUERY_URL", "http://localhost:9090/api/v1/query")
# Optional: endpoint that exposes OTel metrics via Prometheus-compatible exporter
OTEL_METRICS_ENDPOINT = os.getenv("OTEL_METRICS_ENDPOINT", None)
# A label or prefix that maps repo components to metrics labels
COMPONENT_LABEL_KEY = os.getenv("COMPONENT_LABEL_KEY", "component")

# Expected Prometheus metric names (override via env if your deployment differs)
METRIC_INVOCATIONS = os.getenv("METRIC_INVOCATIONS", "component_invocations_total")
METRIC_ERRORS = os.getenv("METRIC_ERRORS", "component_errors_total")
METRIC_LATENCY = os.getenv("METRIC_LATENCY", "component_response_time_seconds_sum")
METRIC_LATENCY_COUNT = os.getenv("METRIC_LATENCY_COUNT", "component_response_time_seconds_count")

# Prometheus range window for point-in-time rate/avg queries (PromQL subquery window)
WINDOW = os.getenv("PROMQL_WINDOW", "5m")


def safe_requests_get(url: str, params: Optional[Dict] = None, timeout: int = 8) -> Optional[dict]:
    if requests is None:
        return None
    try:
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def build_promql_rate(metric: str, component: str) -> str:
    comp = urllib.parse.quote(component)
    return f"sum(rate({metric}{{{COMPONENT_LABEL_KEY}=\"{component}\"}}[{WINDOW}]))"


def build_promql_sum(metric: str, component: str) -> str:
    return f"sum({metric}{{{COMPONENT_LABEL_KEY}=\"{component}\"}})"


def query_prometheus_scalar(query: str) -> Optional[float]:
    data = safe_requests_get(PROMETHEUS_QUERY_URL, params={"query": query})
    if not data or data.get("status") != "success":
        return None
    result = data.get("data", {}).get("result", [])
    if not result:
        return 0.0
    # Instant vector result: take first sample value
    try:
        value = result[0].get("value")
        if isinstance(value, list) and len(value) >= 2:
            return float(value[1])
    except Exception:
        return None
    return None


def get_component_metrics(component: str) -> Dict[str, Optional[float]]:
    """Collect metrics for a component from Prometheus and optional OTel endpoint."""
    metrics = {"invocations": None, "errors": None, "error_rate": None, "avg_latency": None}

    # Prefer rate-based instantaneous view for invocations and errors
    inv_q = build_promql_rate(METRIC_INVOCATIONS, component)
    err_q = build_promql_rate(METRIC_ERRORS, component)

    invocations_per_s = query_prometheus_scalar(inv_q)
    errors_per_s = query_prometheus_scalar(err_q)

    # Compute error rate percentage from rates if both available
    if invocations_per_s is not None and invocations_per_s >= 0:
        metrics["invocations"] = invocations_per_s
        if errors_per_s is not None and errors_per_s >= 0:
            metrics["errors"] = errors_per_s
            metrics["error_rate"] = (errors_per_s / invocations_per_s * 100.0) if invocations_per_s > 0 else 0.0

    # Average response time via rate of sums divided by rate of counts
    lat_sum_q = f"sum(rate({METRIC_LATENCY}{{{COMPONENT_LABEL_KEY}=\"{component}\"}}[{WINDOW}]))"
    lat_cnt_q = f"sum(rate({METRIC_LATENCY_COUNT}{{{COMPONENT_LABEL_KEY}=\"{component}\"}}[{WINDOW}]))"
    lat_sum = query_prometheus_scalar(lat_sum_q)
    lat_cnt = query_prometheus_scalar(lat_cnt_q)
    if lat_sum is not None and lat_cnt is not None and lat_cnt > 0:
        metrics["avg_latency"] = lat_sum / lat_cnt

    # Optional: If an OTel metrics endpoint is provided and Prometheus returns None, try fallback
    # This assumes the endpoint exposes Prometheus text or JSON convertible via sidecar. Keep simple: skip detailed scrape.
    # Hook placeholder for future extension.

    return metrics


def load_registry(registry_path: str) -> Dict:
    """Load the registry.json file."""
    try:
        with open(registry_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Registry file not found at {registry_path}")
        return {"agents": [], "components": []}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in registry file: {e}")
        return {"agents": [], "components": []}


def scan_python_files(repo_root: str) -> Set[str]:
    """Scan repository for Python files and extract component names."""
    components = set()
    repo_path = Path(repo_root)

    for py_file in repo_path.rglob('*.py'):
        # Skip virtual environments and hidden directories
        if any(part.startswith('.') or part == 'venv' for part in py_file.parts):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple heuristic: look for class definitions
                for line in content.split('\n'):
                    if line.strip().startswith('class '):
                        class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                        components.add(class_name)
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}")

    return components


def build_dashboard_table(registry: Dict, discovered_components: Set[str]) -> str:
    """Build the Markdown table for the dashboard."""
    lines: List[str] = []
    lines.append("# Synergy Dashboard")
    lines.append("")
    lines.append("Auto-generated dashboard showing agents, components, relationships, and live metrics.")
    lines.append("")

    # Agents section
    lines.append("## Agents")
    lines.append("")
    lines.append("| Name | Version | Description | Dependencies | Status |")
    lines.append("|------|---------|-------------|--------------|--------|")

    for agent in registry.get('agents', []):
        name = agent.get('name', 'N/A')
        version = agent.get('version', 'N/A')
        description = agent.get('description', 'N/A')
        deps = ', '.join(agent.get('dependencies', []))
        status = agent.get('status', 'unknown')
        lines.append(f"| {name} | {version} | {description} | {deps} | {status} |")

    lines.append("")

    # Components section with metrics
    lines.append("## Components")
    lines.append("")
    lines.append("| Name | Version | Description | Dependencies | Status | Invocation Count (req/s) | Error Rate (%) | Avg. Response Time (s) |")
    lines.append("|------|---------|-------------|--------------|--------|--------------------------:|---------------:|-----------------------:|")

    for component in registry.get('components', []):
        name = component.get('name', 'N/A')
        version = component.get('version', 'N/A')
        description = component.get('description', 'N/A')
        deps = ', '.join(component.get('dependencies', []))
        status = component.get('status', 'unknown')

        invocations = error_rate = avg_latency = "N/A"
        m = get_component_metrics(name)
        if m:
            if m.get("invocations") is not None:
                invocations = f"{m['invocations']:.4f}"
            if m.get("error_rate") is not None:
                error_rate = f"{m['error_rate']:.2f}"
            if m.get("avg_latency") is not None:
                avg_latency = f"{m['avg_latency']:.4f}"

        lines.append(
            f"| {name} | {version} | {description} | {deps} | {status} | {invocations} | {error_rate} | {avg_latency} |"
        )

    lines.append("")

    # Discovered classes
    lines.append("## Discovered Python Classes")
    lines.append("")
    if discovered_components:
        lines.append("The following Python classes were discovered in the repository:")
        lines.append("")
        for comp in sorted(discovered_components):
            lines.append(f"- {comp}")
    else:
        lines.append("No Python classes discovered.")

    lines.append("")
    lines.append("---")
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines.append(f"*Last updated: {ts} by build_dashboard.py*")

    # Metrics config hint
    lines.append("")
    lines.append("> Metrics powered by Prometheus/OpenTelemetry. Configure via env: PROMETHEUS_QUERY_URL, COMPONENT_LABEL_KEY, METRIC_* and PROMQL_WINDOW.")

    return '\n'.join(lines)


def main():
    """Main entry point."""
    # Determine paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    registry_path = repo_root / '.github' / 'registry' / 'registry.json'
    dashboard_path = repo_root / '.github' / 'dashboards' / 'synergy_dashboard.md'

    print(f"Loading registry from: {registry_path}")
    registry = load_registry(str(registry_path))

    print(f"Scanning Python files in: {repo_root}")
    discovered = scan_python_files(str(repo_root))
    print(f"Discovered {len(discovered)} Python classes")

    print("Building dashboard...")
    dashboard_content = build_dashboard_table(registry, discovered)

    # Ensure dashboard directory exists
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Writing dashboard to: {dashboard_path}")
    with open(dashboard_path, 'w') as f:
        f.write(dashboard_content)

    print("Dashboard built successfully!")


if __name__ == '__main__':
    main()
