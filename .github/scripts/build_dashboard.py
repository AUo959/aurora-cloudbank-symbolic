#!/usr/bin/env python3
"""Build Synergy Dashboard from registry and repo files with Prometheus/OpenTelemetry metrics.

Refinements:
- Support new performance metrics: cpu_usage, memory_footprint_mb, uptime_hours, success_rate
- Add safe handling for missing/empty metrics and fields
- Render additional columns in docs/DASHBOARD.md
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import datetime as dt
from datetime import timezone
import urllib.parse

try:
    import requests  # type: ignore
except Exception:
    requests = None  # Fallback when requests isn't available

# -----------------------
# Configuration
# -----------------------
# PROMETHEUS_QUERY_URL should point to the Prometheus HTTP API /api/v1/query endpoint
PROMETHEUS_QUERY_URL = os.getenv("PROMETHEUS_QUERY_URL", "http://localhost:9090/api/v1/query")
# Range window for rate/avg queries
WINDOW = os.getenv("PROMQL_WINDOW", "5m")
# Metric label key that maps components to metrics series
COMPONENT_LABEL_KEY = os.getenv("COMPONENT_LABEL_KEY", "component")

# Optional metric names (override via env if your deployment differs)
METRIC_INVOCATIONS = os.getenv("METRIC_INVOCATIONS", "component_invocations_total")
METRIC_ERRORS = os.getenv("METRIC_ERRORS", "component_errors_total")
METRIC_LATENCY_SUM = os.getenv("METRIC_LATENCY", "component_response_time_seconds_sum")
METRIC_LATENCY_COUNT = os.getenv("METRIC_LATENCY_COUNT", "component_response_time_seconds_count")

# New metric names for CPU/Memory/Uptime/Success Rate if available in Prometheus
METRIC_CPU = os.getenv("METRIC_CPU", "component_cpu_usage_percent")
METRIC_MEM = os.getenv("METRIC_MEM", "component_memory_footprint_megabytes")
METRIC_UPTIME = os.getenv("METRIC_UPTIME", "component_uptime_hours")
METRIC_SUCCESS_RATE = os.getenv("METRIC_SUCCESS_RATE", "component_success_rate_percent")

ROOT = Path(__file__).resolve().parents[2]  # repo root
DOCS_DASHBOARD = ROOT / "docs" / "DASHBOARD.md"
REGISTRY_PATH = ROOT / ".github" / "registry" / "registry.json"

# -----------------------
# Helpers
# -----------------------

def now_iso() -> str:
    return dt.datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_requests_get(url: str, params: Optional[Dict[str, Any]] = None, timeout: int = 8) -> Optional[dict]:
    if requests is None:
        return None
    try:
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def build_promql_sum(metric: str, component: str) -> str:
    return f'sum({metric}{{{COMPONENT_LABEL_KEY}="{component}"}})'


def build_promql_rate(metric: str, component: str) -> str:
    return f'sum(rate({metric}{{{COMPONENT_LABEL_KEY}="{component}"}}[{WINDOW}]))'


def query_prometheus_scalar(query: str) -> Optional[float]:
    data = safe_requests_get(PROMETHEUS_QUERY_URL, params={"query": query})
    if not data or data.get("status") != "success":
        return None
    result = data.get("data", {}).get("result", [])
    if not result:
        return None
    try:
        # value: [timestamp, stringValue]
        value = float(result[0].get("value", [None, "0"][1]))
        return value
    except Exception:
        try:
            return float(result[0]["value"][1])
        except Exception:
            return None


# -----------------------
# Registry loading and normalization
# -----------------------

def load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {"agents": [], "components": []}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {"agents": [], "components": []}


def get_nested(dct: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    cur = dct
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def fmt(v: Optional[Any], default: str = "-") -> str:
    if v is None:
        return default
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def normalize_perf_metrics(item: Dict[str, Any]) -> Dict[str, Optional[float]]:
    perf = item.get("performance_metrics") or {}
    return {
        "cpu_usage": _coerce_float(perf.get("cpu_usage")),
        "memory_footprint_mb": _coerce_float(perf.get("memory_footprint_mb")),
        "uptime_hours": _coerce_float(perf.get("uptime_hours")),
        "success_rate": _coerce_float(perf.get("success_rate")),
    }


def _coerce_float(v: Any) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


# -----------------------
# Metrics aggregation (Prometheus + registry fallback)
# -----------------------

def enrich_with_prom_metrics(component_name: str, base_metrics: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
    # Attempt to pull live metrics; fallback to registry values when missing
    # CPU
    cpu_q = build_promql_sum(METRIC_CPU, component_name)
    cpu_v = query_prometheus_scalar(cpu_q)
    # Memory
    mem_q = build_promql_sum(METRIC_MEM, component_name)
    mem_v = query_prometheus_scalar(mem_q)
    # Uptime
    uptime_q = build_promql_sum(METRIC_UPTIME, component_name)
    uptime_v = query_prometheus_scalar(uptime_q)
    # Success rate
    sr_q = build_promql_sum(METRIC_SUCCESS_RATE, component_name)
    sr_v = query_prometheus_scalar(sr_q)

    return {
        "cpu_usage": cpu_v if cpu_v is not None else base_metrics.get("cpu_usage"),
        "memory_footprint_mb": mem_v if mem_v is not None else base_metrics.get("memory_footprint_mb"),
        "uptime_hours": uptime_v if uptime_v is not None else base_metrics.get("uptime_hours"),
        "success_rate": sr_v if sr_v is not None else base_metrics.get("success_rate"),
    }


# -----------------------
# Dashboard rendering
# -----------------------

def render_table(headers: List[str], rows: List[List[str]]) -> str:
    # Simple GitHub-flavored markdown table
    line1 = "| " + " | ".join(headers) + " |\n"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |\n"
    body = "".join(["| " + " | ".join(r) + " |\n" for r in rows])
    return line1 + sep + body


def build_dashboard_md(registry: Dict[str, Any]) -> str:
    timestamp = now_iso()
    agents: List[Dict[str, Any]] = registry.get("agents", []) or []
    components: List[Dict[str, Any]] = registry.get("components", []) or []

    headers = [
        "Name",
        "Type",
        "Version",
        "Status",
        "Owner",
        "CPU %",
        "Memory MB",
        "Uptime (h)",
        "Success %",
        "Errors (recent)",
        "Last Updated",
        "Description",
    ]

    def row_for(item: Dict[str, Any], kind: str) -> List[str]:
        name = item.get("name") or "unknown"
        version = item.get("version") or "-"
        status = item.get("status") or "-"
        owner = item.get("owner") or "-"
        desc = item.get("description") or "-"
        last_updated = item.get("last_updated") or "-"

        base_metrics = normalize_perf_metrics(item)
        # Enrich via Prometheus if possible
        enriched = enrich_with_prom_metrics(name, base_metrics)

        # Errors
        err_hist = item.get("error_history") or []
        err_cell = "-"
        if isinstance(err_hist, list) and err_hist:
            # show last 2 compact
            recent = err_hist[-2:]
            def fmt_err(e: Dict[str, Any]) -> str:
                ts = e.get("timestamp", "?")
                sev = e.get("severity", "?")
                msg = e.get("error", "?")
                return f"{ts} [{sev}] {msg}"
            err_cell = "; ".join(fmt_err(e) for e in recent)

        row = [
            str(name),
            kind,
            str(version),
            str(status),
            str(owner),
            fmt(enriched.get("cpu_usage")),
            fmt(enriched.get("memory_footprint_mb")),
            fmt(enriched.get("uptime_hours")),
            fmt(enriched.get("success_rate")),
            err_cell,
            str(last_updated),
            str(desc),
        ]
        return row

    rows: List[List[str]] = []
    for a in agents:
        rows.append(row_for(a, "agent"))
    for c in components:
        rows.append(row_for(c, "component"))

    table = render_table(headers, rows)

    md = [
        "# Synergy Dashboard",
        "",
        f"Generated: {timestamp}",
        "",
        "Notes:",
        "- Metrics columns may include live data from Prometheus when available.",
        "- Missing metrics are shown as '-' to indicate unavailability.",
        "",
        table,
        "",
    ]
    return "\n".join(md)


def main() -> int:
    registry = load_registry()
    content = build_dashboard_md(registry)
    DOCS_DASHBOARD.parent.mkdir(parents=True, exist_ok=True)
    with open(DOCS_DASHBOARD, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote dashboard to {DOCS_DASHBOARD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
