#!/usr/bin/env python3
"""
Benchmark scorecard for the #767-#836 hardening push.

Runs grep/file checks against the working tree and prints a per-metric
status. Returns non-zero exit code if `--strict` is set and any required
metric is failing.

Add new checks by appending a Check(...) to CHECKS. Each check is a pure
function over the repo root; no network calls.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Result:
    value: int | str | None
    status: str  # "pass", "warn", "fail", "info"
    detail: str = ""


@dataclass
class Check:
    domain: str
    metric: str
    target: str
    issues: str
    fn: Callable[[], Result]
    required: bool = False


def _grep_count(pattern: str, paths: list[str], include: str = "*.py") -> int:
    """Count regex matches across `paths` (silently 0 if rg/grep missing)."""
    if shutil.which("rg"):
        cmd = ["rg", "-c", "--no-heading", "-g", include, "-e", pattern, *paths]
    else:
        cmd = ["grep", "-rcE", f"--include={include}", pattern, *paths]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    total = 0
    for line in proc.stdout.splitlines():
        if ":" in line:
            try:
                total += int(line.rsplit(":", 1)[1])
            except ValueError:
                pass
    return total


def _file_exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


def _file_contains(rel: str, needle: str) -> bool:
    path = REPO_ROOT / rel
    if not path.exists():
        return False
    return needle in path.read_text(errors="ignore")


# ---------- security ----------

def check_str_e_leak() -> Result:
    n = _grep_count(r"detail=str\(e\)|detail=f\".*\{str\(e\)|detail=f\".*\{e\}", ["api", "modules", "src"])
    status = "pass" if n == 0 else "fail"
    return Result(n, status, "Issue #783 target: 0")


def check_datetime_utcnow() -> Result:
    n = _grep_count(r"datetime\.utcnow\(\)", ["api", "modules", "src"])
    return Result(n, "pass" if n == 0 else "fail", "Issue #768 target: 0")


def check_csrf_router_coverage() -> Result:
    files = subprocess.run(
        ["grep", "-rl", "Depends(verify_csrf", "--include=*.py", "api", "modules", "src"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout.splitlines()
    n = len(files)
    status = "fail" if n < 5 else "warn" if n < 10 else "pass"
    return Result(n, status, "Issue #784 target: every state-changing router")


def check_third_party_action_sha_pins() -> Result:
    workflows = list((REPO_ROOT / ".github/workflows").glob("*.yml"))
    tag_pinned = 0
    sha_pinned = 0
    pat = re.compile(r"uses:\s*([^\s@]+)@([^\s#]+)")
    for wf in workflows:
        for m in pat.finditer(wf.read_text(errors="ignore")):
            owner = m.group(1)
            ref = m.group(2)
            if owner.startswith("actions/"):
                continue
            if re.fullmatch(r"[0-9a-f]{40}", ref):
                sha_pinned += 1
            else:
                tag_pinned += 1
    total = tag_pinned + sha_pinned
    status = "pass" if tag_pinned == 0 and total > 0 else "fail"
    return Result(f"{sha_pinned}/{total} SHA-pinned", status, "Issue #832 target: all third-party")


def check_docker_digest_pins() -> Result:
    dockerfiles = [p for p in REPO_ROOT.rglob("Dockerfile*") if "node_modules" not in str(p)]
    digest = 0
    tag = 0
    for df in dockerfiles:
        for line in df.read_text(errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("FROM ") and "scratch" not in line:
                if "@sha256:" in line:
                    digest += 1
                else:
                    tag += 1
    total = digest + tag
    status = "pass" if tag == 0 and total > 0 else "fail"
    return Result(f"{digest}/{total} digest-pinned", status, "Issue #833 target: all FROM lines")


# ---------- testing / verification ----------

def check_test_function_count() -> Result:
    proc = subprocess.run(
        ["grep", "-rhE", r"^\s*(async\s+)?def test_", "--include=*.py", "tests"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    n = len(proc.stdout.splitlines())
    return Result(n, "info", "Issue #789: README must match")


def check_test_file_count() -> Result:
    n = sum(1 for _ in (REPO_ROOT / "tests").rglob("test_*.py"))
    return Result(n, "info", "Issue #789: README must match")


def check_coverage_threshold() -> Result:
    pyproj = (REPO_ROOT / "pyproject.toml").read_text(errors="ignore")
    has_section = "[tool.coverage" in pyproj
    has_threshold = "fail_under" in pyproj or "--cov-fail-under" in pyproj
    if has_threshold:
        return Result("configured", "pass", "Issue #790")
    if has_section:
        return Result("partial", "warn", "Issue #790: section without threshold")
    return Result("missing", "fail", "Issue #790: no coverage config")


def check_ci_tests_blocking() -> Result:
    workflow = REPO_ROOT / ".github/workflows/aurora-ci-minimal.yml"
    if not workflow.exists():
        return Result("missing", "fail", "Issue #758")
    text = workflow.read_text(errors="ignore")
    occurrences = text.count("continue-on-error: true")
    status = "pass" if occurrences == 0 else "fail"
    return Result(occurrences, status, "Issue #758 target: 0 in test/lint jobs")


def check_codeql_enabled() -> Result:
    workflow = REPO_ROOT / ".github/workflows/codeql-unified.yml"
    if not workflow.exists():
        return Result("missing", "warn", "Issue #786")
    text = workflow.read_text(errors="ignore")
    disabled = "if: false" in text
    return Result("disabled" if disabled else "enabled",
                  "fail" if disabled else "pass", "Issue #786")


def check_hollow_assertions() -> Result:
    n = _grep_count(r"assert.*is not None|assert hasattr", ["tests"])
    if n > 300:
        return Result(n, "fail", "Issue #791 target: <100 in Tier 1")
    if n > 100:
        return Result(n, "warn", "Issue #791 target: <100")
    return Result(n, "pass", "Issue #791")


# ---------- wiring / observability ----------

def check_telemetry_middleware() -> Result:
    has = _file_contains("api/aurora_api.py", "R2AgentTelemetry") and _grep_count(
        r"track_operation\(", ["api"]
    ) > 0
    return Result("wired" if has else "missing",
                  "pass" if has else "fail", "Issue #769")


def check_ethics_response_path() -> Result:
    # Require evaluate_action to be called from an HTTP-router file: either
    # api/aurora_api.py or any modules/*/api*.py / src/**/api*.py.
    proc = subprocess.run(
        ["grep", "-rlE", r"evaluate_action\(", "--include=*.py",
         "api", "modules", "src"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    router_callers = [
        f for f in proc.stdout.splitlines()
        if (f == "api/aurora_api.py"
            or re.search(r"(modules|src)/.*/api(_[a-z]+)?\.py$", f)
            or re.search(r"(modules|src)/.*/routes?\.py$", f))
        and "dashboard_api" not in f
        and "patchweaver" not in f
    ]
    # GUMAS routes call EthicsEngine on its own evaluator — that's the trivial
    # case and predates #770. Require the central API or another router.
    non_gumas = [f for f in router_callers if "gumas" not in f]
    main_api = "api/aurora_api.py" in router_callers
    if main_api and non_gumas:
        status = "pass"
    elif non_gumas or main_api:
        status = "warn"
    else:
        status = "fail"
    return Result(f"{len(router_callers)} ({len(non_gumas)} non-GUMAS)",
                  status,
                  "Issue #770 target: api/aurora_api.py + ≥1 other router")


def check_ledger_startup_verify() -> Result:
    ledger = REPO_ROOT / "modules/insight_ledger/ledger_core.py"
    if not ledger.exists():
        return Result("missing", "warn", "Issue #806")
    text = ledger.read_text(errors="ignore")
    init_block = text.split("def __init__", 1)[-1].split("\n    def ", 1)[0]
    called = "verify_integrity" in init_block
    return Result("called" if called else "absent",
                  "pass" if called else "fail", "Issue #806")


def check_atomic_writes() -> Result:
    files = ["modules/insight_ledger/ledger_core.py",
             "modules/aumemmanager/hierarchical_memory.py",
             "src/monitoring/monitoring_system.py",
             "src/monitoring/drift_detector.py",
             "src/monitoring/ethics_engine.py"]
    pat = re.compile(r"os\.replace\(|NamedTemporaryFile|atomic_write")
    have = sum(1 for f in files if (REPO_ROOT / f).exists()
               and pat.search((REPO_ROOT / f).read_text(errors="ignore")))
    total = len(files)
    return Result(f"{have}/{total}", "pass" if have == total else "fail",
                  "Issue #807 target: all state-bearing modules")


def check_request_id_middleware() -> Result:
    api = REPO_ROOT / "api/aurora_api.py"
    if not api.exists():
        return Result("missing", "warn", "Issue #818")
    text = api.read_text(errors="ignore")
    has = "X-Request-ID" in text or "request_id_middleware" in text
    return Result("wired" if has else "missing",
                  "pass" if has else "fail", "Issue #818")


def check_health_split() -> Result:
    api = REPO_ROOT / "api/aurora_api.py"
    if not api.exists():
        return Result("missing", "warn", "Issue #814")
    text = api.read_text(errors="ignore")
    paths = sum(1 for p in ('"/live"', '"/ready"', '"/health"') if p in text)
    return Result(f"{paths}/3", "pass" if paths == 3 else "fail",
                  "Issue #814 target: 3 distinct endpoints")


# ---------- supply chain ----------

def check_python_floor_consistency() -> Result:
    candidates = {
        "setup.py": r"python_requires\s*=\s*[\"'](>=\d+\.\d+)",
        "runtime.txt": r"python-(\d+\.\d+)",
        "sdk/python/pyproject.toml": r"requires-python\s*=\s*[\"'](>=\d+\.\d+)",
        "cli/pyproject.toml": r"requires-python\s*=\s*[\"'](>=\d+\.\d+)",
    }
    floors = set()
    for rel, pat in candidates.items():
        p = REPO_ROOT / rel
        if not p.exists():
            continue
        m = re.search(pat, p.read_text(errors="ignore"))
        if m:
            floors.add(m.group(1))
    if len(floors) <= 1:
        return Result(",".join(sorted(floors)) or "unset", "pass", "Issue #834")
    return Result(",".join(sorted(floors)), "fail", "Issue #834 target: single floor")


def check_lockfile_present_and_hashed() -> Result:
    lock = REPO_ROOT / "requirements-lock.txt"
    if not lock.exists():
        return Result("missing", "fail", "Issues #787, #835")
    has_hashes = "--hash=" in lock.read_text(errors="ignore")
    return Result("hashed" if has_hashes else "no-hashes",
                  "pass" if has_hashes else "warn", "Issue #835")


def check_env_example_completeness() -> Result:
    env_ex = REPO_ROOT / ".env.example"
    if not env_ex.exists():
        return Result("missing", "fail", "Issue #821")
    declared = {line.split("=", 1)[0].strip()
                for line in env_ex.read_text(errors="ignore").splitlines()
                if line.strip() and not line.strip().startswith("#") and "=" in line}
    proc = subprocess.run(
        ["grep", "-rhoE",
         r"os\.getenv\(\s*[\"'][A-Z_][A-Z0-9_]+|os\.environ\.get\(\s*[\"'][A-Z_][A-Z0-9_]+|"
         r"os\.environ\[\s*[\"'][A-Z_][A-Z0-9_]+",
         "--include=*.py", "api", "modules", "src", "connector"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    var_pat = re.compile(r"[\"']([A-Z_][A-Z0-9_]+)")
    referenced = set()
    for line in proc.stdout.splitlines():
        m = var_pat.search(line)
        if m:
            referenced.add(m.group(1))
    # exclude CI-only / framework vars
    skip = {"GITHUB_TOKEN", "GH_TOKEN", "GITHUB_BASE_REF", "GITHUB_EVENT_NAME",
            "GITHUB_OUTPUT", "USER", "HOME", "PATH"}
    missing = (referenced - declared) - skip
    n = len(missing)
    if n == 0:
        return Result("complete", "pass", "Issue #821")
    if n <= 5:
        return Result(n, "warn", f"Issue #821: missing {sorted(missing)[:5]}")
    return Result(n, "fail", f"Issue #821: missing {n} vars")


# ---------- connector ----------

def check_connector_tests_exist() -> Result:
    dirs = [REPO_ROOT / "tests/connector", REPO_ROOT / "connector/tests"]
    found = next((d for d in dirs if d.exists() and any(d.glob("test_*.py"))), None)
    return Result("present" if found else "missing",
                  "pass" if found else "fail", "Issue #827")


def check_connector_bridge_retries() -> Result:
    bridge = REPO_ROOT / "connector/transport/bridge.py"
    if not bridge.exists():
        return Result("missing", "warn", "Issue #824")
    text = bridge.read_text(errors="ignore")
    has_retry = ("tenacity" in text or "retry" in text.lower())
    has_user_agent = "User-Agent" in text or "user-agent" in text
    flags = []
    if has_retry:
        flags.append("retries")
    if has_user_agent:
        flags.append("user-agent")
    if len(flags) == 2:
        return Result(",".join(flags), "pass", "Issues #824, #826")
    if flags:
        return Result(",".join(flags), "warn", "Issues #824, #826 partial")
    return Result("none", "fail", "Issues #824, #826")


# ---------- registry ----------

CHECKS: list[Check] = [
    Check("security", "HTTPException str(e) leak sites", "0", "#783",
          check_str_e_leak, required=True),
    Check("security", "datetime.utcnow() call sites", "0", "#768",
          check_datetime_utcnow),
    Check("security", "Files using Depends(verify_csrf_token)", ">=10", "#784",
          check_csrf_router_coverage, required=True),
    Check("security", "Third-party GitHub Actions SHA-pinned", "all", "#832",
          check_third_party_action_sha_pins),
    Check("security", "Docker base images digest-pinned", "all", "#833",
          check_docker_digest_pins),

    Check("testing", "Test function count (info only)", "—", "#789",
          check_test_function_count),
    Check("testing", "Test file count (info only)", "—", "#789",
          check_test_file_count),
    Check("testing", "Coverage threshold configured", "configured", "#790",
          check_coverage_threshold, required=True),
    Check("testing", "continue-on-error count in CI", "0", "#758",
          check_ci_tests_blocking, required=True),
    Check("testing", "CodeQL workflow status", "enabled", "#786",
          check_codeql_enabled),
    Check("testing", "Hollow assertion count", "<100", "#791",
          check_hollow_assertions),

    Check("wiring", "Telemetry middleware wired", "wired", "#769",
          check_telemetry_middleware, required=True),
    Check("wiring", "EthicsEngine on production paths", ">=1", "#770",
          check_ethics_response_path, required=True),
    Check("wiring", "Ledger verify_integrity at startup", "called", "#806",
          check_ledger_startup_verify),
    Check("wiring", "Atomic-write coverage on state files", "all", "#807",
          check_atomic_writes),
    Check("wiring", "Request-ID middleware mounted", "wired", "#818",
          check_request_id_middleware),
    Check("ops", "Health endpoints split", "3/3", "#814",
          check_health_split),

    Check("supply", "Python floor consistency", "single", "#834",
          check_python_floor_consistency),
    Check("supply", "Lockfile present + hashed", "hashed", "#787 #835",
          check_lockfile_present_and_hashed),
    Check("supply", ".env.example completeness", "complete", "#821",
          check_env_example_completeness),

    Check("connector", "Connector tests exist", "present", "#827",
          check_connector_tests_exist, required=True),
    Check("connector", "Bridge retries + identifying headers", "both", "#824 #826",
          check_connector_bridge_retries),
]


# ---------- runner ----------

GLYPH = {"pass": "PASS", "warn": "WARN", "fail": "FAIL", "info": "INFO"}


def run(strict: bool) -> int:
    by_domain: dict[str, list[tuple[Check, Result]]] = {}
    for check in CHECKS:
        try:
            result = check.fn()
        except Exception as exc:  # noqa: BLE001
            result = Result(None, "fail", f"check raised: {exc!r}")
        by_domain.setdefault(check.domain, []).append((check, result))

    width_metric = max(len(c.metric) for c in CHECKS) + 2
    width_value = 22
    print(f"\n{'METRIC'.ljust(width_metric)} {'VALUE'.ljust(width_value)} STATUS  TARGET   ISSUES")
    print("-" * (width_metric + width_value + 30))

    failed_required = 0
    failed_any = 0
    for domain, rows in by_domain.items():
        print(f"\n[{domain.upper()}]")
        for check, result in rows:
            value = "—" if result.value is None else str(result.value)
            print(f"  {check.metric.ljust(width_metric)} "
                  f"{value.ljust(width_value)} "
                  f"{GLYPH[result.status]:5}  "
                  f"{check.target:8} "
                  f"{check.issues}")
            if result.detail:
                print(f"    └─ {result.detail}")
            if result.status == "fail":
                failed_any += 1
                if check.required:
                    failed_required += 1

    print(f"\nTotal fails: {failed_any} (required: {failed_required})")
    if strict and failed_required:
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Aurora benchmark scorecard")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if any required check fails")
    args = parser.parse_args()
    return run(strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
