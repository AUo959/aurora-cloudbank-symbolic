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
from functools import lru_cache
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent

# Narrow set of exceptions a single check can plausibly raise. Anything else
# is a real bug we want to see.
_CHECK_EXCEPTIONS = (
    subprocess.SubprocessError,
    OSError,
    re.error,
    ValueError,
    AttributeError,
    KeyError,
    IndexError,
)

_SUBPROCESS_TIMEOUT = 30


class ToolMissingError(RuntimeError):
    """Raised when a required external tool (grep, rg) is not on PATH."""


@lru_cache(maxsize=8)
def _resolve(tool: str) -> str | None:
    """Return the absolute path of `tool`, or None if it is not installed."""
    return shutil.which(tool)


def _require(tool: str) -> str:
    path = _resolve(tool)
    if path is None:
        raise ToolMissingError(f"required tool not on PATH: {tool}")
    return path


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a subprocess with a bounded timeout, never via the shell."""
    return subprocess.run(  # noqa: S603 -- argv list, shell=False, absolute path
        argv,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=_SUBPROCESS_TIMEOUT,
        shell=False,
    )


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


def _grep_cmd(pattern: str, paths: list[str], include: str, mode: str) -> list[str]:
    """Build a grep/rg argv with an absolute path. `mode` is 'count' or 'list'."""
    rg = _resolve("rg")
    if rg is not None:
        if mode == "count":
            return [rg, "-c", "--no-heading", "-g", include, "-e", pattern, *paths]
        if mode == "list":
            return [rg, "-l", "-g", include, "-e", pattern, *paths]
    grep = _require("grep")
    if mode == "count":
        return [grep, "-rcE", f"--include={include}", pattern, *paths]
    return [grep, "-rlE", f"--include={include}", pattern, *paths]


def _grep_count(pattern: str, paths: list[str], include: str = "*.py") -> int:
    """Count regex matches across `paths`."""
    proc = _run(_grep_cmd(pattern, paths, include, "count"))
    total = 0
    for line in proc.stdout.splitlines():
        if ":" not in line:
            continue
        try:
            total += int(line.rsplit(":", 1)[1])
        except ValueError:
            continue
    return total


def _grep_list(pattern: str, paths: list[str], include: str = "*.py") -> list[str]:
    """Return files containing matches for `pattern`."""
    proc = _run(_grep_cmd(pattern, paths, include, "list"))
    return [line for line in proc.stdout.splitlines() if line]


def _file_text(rel: str) -> str:
    path = REPO_ROOT / rel
    if not path.exists():
        return ""
    return path.read_text(errors="ignore")


def _file_exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


def _file_contains(rel: str, needle: str) -> bool:
    return needle in _file_text(rel)


# ---------- security ----------

def check_str_e_leak() -> Result:
    n = _grep_count(
        r"detail=str\(e\)|detail=f\".*\{str\(e\)|detail=f\".*\{e\}",
        ["api", "modules", "src"],
    )
    return Result(n, "pass" if n == 0 else "fail", "Issue #783 target: 0")


def check_datetime_utcnow() -> Result:
    n = _grep_count(r"datetime\.utcnow\(\)", ["api", "modules", "src"])
    return Result(n, "pass" if n == 0 else "fail", "Issue #768 target: 0")


def check_csrf_router_coverage() -> Result:
    files = _grep_list(r"Depends\(verify_csrf", ["api", "modules", "src"])
    n = len(files)
    status = "fail" if n < 5 else "warn" if n < 10 else "pass"
    return Result(n, status, "Issue #784 target: every state-changing router")


_ACTION_PIN_RE = re.compile(r"uses:\s*([^\s@]+)@([^\s#]+)")
_SHA_RE = re.compile(r"[0-9a-f]{40}")


def _classify_action_pins(workflow_text: str) -> tuple[int, int]:
    """Return (third_party_sha_pinned, third_party_tag_pinned)."""
    sha = 0
    tag = 0
    for m in _ACTION_PIN_RE.finditer(workflow_text):
        owner, ref = m.group(1), m.group(2)
        if owner.startswith("actions/"):
            continue
        if _SHA_RE.fullmatch(ref):
            sha += 1
        else:
            tag += 1
    return sha, tag


def check_third_party_action_sha_pins() -> Result:
    workflow_dir = REPO_ROOT / ".github/workflows"
    if not workflow_dir.exists():
        return Result("no workflows dir", "warn", "Issue #832")
    sha_total = 0
    tag_total = 0
    for wf in workflow_dir.glob("*.yml"):
        sha, tag = _classify_action_pins(wf.read_text(errors="ignore"))
        sha_total += sha
        tag_total += tag
    total = sha_total + tag_total
    if total == 0:
        return Result("0 third-party", "warn", "Issue #832: nothing to pin")
    status = "pass" if tag_total == 0 else "fail"
    return Result(f"{sha_total}/{total} SHA-pinned", status, "Issue #832")


def _is_digest_pinned(from_line: str) -> bool | None:
    """True if `FROM ... @sha256:...`, False if tag-pinned, None if irrelevant."""
    stripped = from_line.strip()
    if not stripped.startswith("FROM ") or "scratch" in stripped:
        return None
    return "@sha256:" in stripped


def check_docker_digest_pins() -> Result:
    digest = 0
    tag = 0
    for df in REPO_ROOT.rglob("Dockerfile*"):
        if "node_modules" in str(df):
            continue
        for line in df.read_text(errors="ignore").splitlines():
            verdict = _is_digest_pinned(line)
            if verdict is True:
                digest += 1
            elif verdict is False:
                tag += 1
    total = digest + tag
    if total == 0:
        return Result("0 FROM lines", "warn", "Issue #833")
    status = "pass" if tag == 0 else "fail"
    return Result(f"{digest}/{total} digest-pinned", status, "Issue #833")


# ---------- testing / verification ----------

def check_test_function_count() -> Result:
    proc = _run([_require("grep"), "-rhE", r"^\s*(async\s+)?def test_",
                 "--include=*.py", "tests"])
    n = sum(1 for _ in proc.stdout.splitlines())
    return Result(n, "info", "Issue #789: README must match")


def check_test_file_count() -> Result:
    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.exists():
        return Result(0, "warn", "Issue #789: tests/ missing")
    n = sum(1 for _ in tests_dir.rglob("test_*.py"))
    return Result(n, "info", "Issue #789: README must match")


def check_coverage_threshold() -> Result:
    pyproj = _file_text("pyproject.toml")
    has_section = "[tool.coverage" in pyproj
    has_threshold = "fail_under" in pyproj or "--cov-fail-under" in pyproj
    if has_threshold:
        return Result("configured", "pass", "Issue #790")
    if has_section:
        return Result("partial", "warn", "Issue #790: section without threshold")
    return Result("missing", "fail", "Issue #790: no coverage config")


def check_ci_tests_blocking() -> Result:
    text = _file_text(".github/workflows/aurora-ci-minimal.yml")
    if not text:
        return Result("missing", "fail", "Issue #758")
    occurrences = text.count("continue-on-error: true")
    return Result(occurrences,
                  "pass" if occurrences == 0 else "fail",
                  "Issue #758 target: 0 in test/lint jobs")


def check_codeql_enabled() -> Result:
    text = _file_text(".github/workflows/codeql-unified.yml")
    if not text:
        return Result("missing", "warn", "Issue #786")
    disabled = "if: false" in text
    return Result(
        "disabled" if disabled else "enabled",
        "fail" if disabled else "pass",
        "Issue #786",
    )


def check_hollow_assertions() -> Result:
    n = _grep_count(r"assert.*is not None|assert hasattr", ["tests"])
    if n > 300:
        return Result(n, "fail", "Issue #791 target: <100 in Tier 1")
    if n > 100:
        return Result(n, "warn", "Issue #791 target: <100")
    return Result(n, "pass", "Issue #791")


# ---------- wiring / observability ----------

def check_telemetry_middleware() -> Result:
    has_class = _file_contains("api/aurora_api.py", "R2AgentTelemetry")
    has_call = _grep_count(r"track_operation\(", ["api"]) > 0
    return Result(
        "wired" if (has_class and has_call) else "missing",
        "pass" if (has_class and has_call) else "fail",
        "Issue #769",
    )


_ROUTER_PATH_RE = re.compile(
    r"(modules|src)/.*/(api(_[a-z]+)?|routes?)\.py$"
)


def _ethics_router_callers() -> tuple[list[str], list[str], bool]:
    """Return (all_router_callers, non_gumas_callers, central_api_among_them)."""
    raw = _grep_list(r"evaluate_action\(", ["api", "modules", "src"])
    router_callers = [
        f for f in raw
        if (f == "api/aurora_api.py" or _ROUTER_PATH_RE.search(f))
        and "dashboard_api" not in f
        and "patchweaver" not in f
    ]
    non_gumas = [f for f in router_callers if "gumas" not in f]
    main_api = "api/aurora_api.py" in router_callers
    return router_callers, non_gumas, main_api


def check_ethics_response_path() -> Result:
    router_callers, non_gumas, main_api = _ethics_router_callers()
    if main_api and non_gumas:
        status = "pass"
    elif non_gumas or main_api:
        status = "warn"
    else:
        status = "fail"
    return Result(
        f"{len(router_callers)} ({len(non_gumas)} non-GUMAS)",
        status,
        "Issue #770 target: api/aurora_api.py + ≥1 other router",
    )


def check_ledger_startup_verify() -> Result:
    text = _file_text("modules/insight_ledger/ledger_core.py")
    if not text:
        return Result("missing", "warn", "Issue #806")
    parts = text.split("def __init__", 1)
    if len(parts) < 2:
        return Result("no __init__", "warn", "Issue #806")
    init_block = parts[1].split("\n    def ", 1)[0]
    called = "verify_integrity" in init_block
    return Result("called" if called else "absent",
                  "pass" if called else "fail", "Issue #806")


_ATOMIC_WRITE_RE = re.compile(r"os\.replace\(|NamedTemporaryFile|atomic_write")
_STATE_FILES = (
    "modules/insight_ledger/ledger_core.py",
    "modules/aumemmanager/hierarchical_memory.py",
    "src/monitoring/monitoring_system.py",
    "src/monitoring/drift_detector.py",
    "src/monitoring/ethics_engine.py",
)


def check_atomic_writes() -> Result:
    have = sum(
        1 for rel in _STATE_FILES
        if _ATOMIC_WRITE_RE.search(_file_text(rel))
    )
    total = len(_STATE_FILES)
    return Result(
        f"{have}/{total}",
        "pass" if have == total else "fail",
        "Issue #807 target: all state-bearing modules",
    )


def check_request_id_middleware() -> Result:
    text = _file_text("api/aurora_api.py")
    if not text:
        return Result("missing", "warn", "Issue #818")
    has = "X-Request-ID" in text or "request_id_middleware" in text
    return Result("wired" if has else "missing",
                  "pass" if has else "fail", "Issue #818")


def check_health_split() -> Result:
    text = _file_text("api/aurora_api.py")
    if not text:
        return Result("missing", "warn", "Issue #814")
    paths_found = sum(1 for p in ('"/live"', '"/ready"', '"/health"') if p in text)
    return Result(
        f"{paths_found}/3",
        "pass" if paths_found == 3 else "fail",
        "Issue #814 target: 3 distinct endpoints",
    )


# ---------- supply chain ----------

_FLOOR_PATTERNS = {
    "setup.py": r"python_requires\s*=\s*[\"'](>=\d+\.\d+)",
    "runtime.txt": r"python-(\d+\.\d+)",
    "sdk/python/pyproject.toml": r"requires-python\s*=\s*[\"'](>=\d+\.\d+)",
    "cli/pyproject.toml": r"requires-python\s*=\s*[\"'](>=\d+\.\d+)",
}


def check_python_floor_consistency() -> Result:
    floors: set[str] = set()
    for rel, pat in _FLOOR_PATTERNS.items():
        text = _file_text(rel)
        if not text:
            continue
        m = re.search(pat, text)
        if m:
            floors.add(m.group(1))
    if len(floors) <= 1:
        return Result(",".join(sorted(floors)) or "unset", "pass", "Issue #834")
    return Result(",".join(sorted(floors)), "fail",
                  "Issue #834 target: single floor")


def check_lockfile_present_and_hashed() -> Result:
    text = _file_text("requirements-lock.txt")
    if not text:
        return Result("missing", "fail", "Issues #787, #835")
    has_hashes = "--hash=" in text
    return Result("hashed" if has_hashes else "no-hashes",
                  "pass" if has_hashes else "warn", "Issue #835")


_ENV_REF_RE = re.compile(
    r"os\.getenv\(\s*[\"'][A-Z_][A-Z0-9_]+|"
    r"os\.environ\.get\(\s*[\"'][A-Z_][A-Z0-9_]+|"
    r"os\.environ\[\s*[\"'][A-Z_][A-Z0-9_]+"
)
_VAR_NAME_RE = re.compile(r"[\"']([A-Z_][A-Z0-9_]+)")
_ENV_SKIP = frozenset({
    "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_BASE_REF", "GITHUB_EVENT_NAME",
    "GITHUB_OUTPUT", "USER", "HOME", "PATH",
})


def _env_referenced() -> set[str]:
    proc = _run([_require("grep"), "-rhoE", _ENV_REF_RE.pattern,
                 "--include=*.py", "api", "modules", "src", "connector"])
    referenced: set[str] = set()
    for line in proc.stdout.splitlines():
        m = _VAR_NAME_RE.search(line)
        if m:
            referenced.add(m.group(1))
    return referenced


def _env_declared() -> set[str]:
    declared: set[str] = set()
    for line in _file_text(".env.example").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        declared.add(s.split("=", 1)[0].strip())
    return declared


def check_env_example_completeness() -> Result:
    if not _file_exists(".env.example"):
        return Result("missing", "fail", "Issue #821")
    missing = (_env_referenced() - _env_declared()) - _ENV_SKIP
    n = len(missing)
    if n == 0:
        return Result("complete", "pass", "Issue #821")
    sample = sorted(missing)[:5]
    if n <= 5:
        return Result(n, "warn", f"Issue #821: missing {sample}")
    return Result(n, "fail", f"Issue #821: missing {n} vars (e.g. {sample})")


# ---------- connector ----------

def check_connector_tests_exist() -> Result:
    candidates = [REPO_ROOT / "tests/connector", REPO_ROOT / "connector/tests"]
    found = any(d.exists() and any(d.glob("test_*.py")) for d in candidates)
    return Result("present" if found else "missing",
                  "pass" if found else "fail", "Issue #827")


def check_connector_bridge_retries() -> Result:
    text = _file_text("connector/transport/bridge.py")
    if not text:
        return Result("missing", "warn", "Issue #824")
    has_retry = "tenacity" in text or "retry" in text.lower()
    has_user_agent = "User-Agent" in text or "user-agent" in text
    flags = [name for name, present in
             (("retries", has_retry), ("user-agent", has_user_agent))
             if present]
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


def _execute(check: Check) -> Result:
    try:
        return check.fn()
    except ToolMissingError as exc:
        return Result(None, "warn", f"tool missing: {exc}")
    except _CHECK_EXCEPTIONS as exc:
        return Result(None, "fail", f"check raised: {exc!r}")


def _print_row(check: Check, result: Result, w_metric: int, w_value: int) -> None:
    value = "—" if result.value is None else str(result.value)
    print(f"  {check.metric.ljust(w_metric)} "
          f"{value.ljust(w_value)} "
          f"{GLYPH[result.status]:5}  "
          f"{check.target:8} "
          f"{check.issues}")
    if result.detail:
        print(f"    └─ {result.detail}")


def run(strict: bool) -> int:
    by_domain: dict[str, list[tuple[Check, Result]]] = {}
    for check in CHECKS:
        by_domain.setdefault(check.domain, []).append((check, _execute(check)))

    width_metric = max(len(c.metric) for c in CHECKS) + 2
    width_value = 22
    print(f"\n{'METRIC'.ljust(width_metric)} {'VALUE'.ljust(width_value)} STATUS  TARGET   ISSUES")
    print("-" * (width_metric + width_value + 30))

    failed_required = 0
    failed_any = 0
    for domain, rows in by_domain.items():
        print(f"\n[{domain.upper()}]")
        for check, result in rows:
            _print_row(check, result, width_metric, width_value)
            if result.status == "fail":
                failed_any += 1
                if check.required:
                    failed_required += 1

    print(f"\nTotal fails: {failed_any} (required: {failed_required})")
    return 1 if (strict and failed_required) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Aurora benchmark scorecard")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if any required check fails")
    args = parser.parse_args()
    return run(strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
