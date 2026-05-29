#!/usr/bin/env python3
"""
Benchmark scorecard for the #767-#836 hardening push.

Runs static checks against the working tree and prints a per-metric
status. Returns non-zero exit code if `--strict` is set and any required
metric is failing.

Add a new check by appending a Check(...) to CHECKS. Each check is a
pure function over the repo root; no network, no subprocess.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

# Narrow set of exceptions a single check can plausibly raise.
_CHECK_EXCEPTIONS = (
    OSError,
    re.error,
    ValueError,
    AttributeError,
    KeyError,
    IndexError,
    UnicodeDecodeError,
)


@dataclass(frozen=True)
class Result:
    value: int | str | None
    status: str  # "pass", "warn", "fail", "info"
    detail: str = ""


@dataclass(frozen=True)
class Check:
    domain: str
    metric: str
    target: str
    issues: str
    fn: Callable[[], Result]
    required: bool = False


# ---------- file walking helpers (pure Python; no subprocess) ----------

def _iter_python_files(roots: Iterable[str]) -> Iterable[Path]:
    """Yield every *.py file under each root, skipping common noise dirs."""
    skip_parts = {".git", "__pycache__", "node_modules", ".venv", "venv",
                  ".mypy_cache", ".pytest_cache", ".tox", "dist", "build"}
    for root in roots:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            if any(part in skip_parts for part in path.parts):
                continue
            yield path


@lru_cache(maxsize=512)
def _read_text(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _file_text(rel: str) -> str:
    return _read_text(str(REPO_ROOT / rel))


def _file_exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


def _file_contains(rel: str, needle: str) -> bool:
    return needle in _file_text(rel)


def _regex_count(pattern: str, roots: Iterable[str]) -> int:
    """Count regex matches across every *.py file under `roots`."""
    rx = re.compile(pattern)
    total = 0
    for path in _iter_python_files(roots):
        total += sum(1 for _ in rx.finditer(_read_text(str(path))))
    return total


def _regex_files(pattern: str, roots: Iterable[str]) -> list[str]:
    """Return repo-relative paths of files matching `pattern`."""
    rx = re.compile(pattern)
    hits: list[str] = []
    for path in _iter_python_files(roots):
        if rx.search(_read_text(str(path))):
            hits.append(str(path.relative_to(REPO_ROOT)))
    return hits


def _regex_capture_set(pattern: str, roots: Iterable[str], group: int = 1) -> set[str]:
    """Return the set of unique capture-group values across all matches."""
    rx = re.compile(pattern)
    out: set[str] = set()
    for path in _iter_python_files(roots):
        for m in rx.finditer(_read_text(str(path))):
            try:
                value = m.group(group)
            except IndexError:
                continue
            if value:
                out.add(value)
    return out


# ---------- security ----------

def check_str_e_leak() -> Result:
    n = _regex_count(
        r'detail=str\(e\)|detail=f".*\{str\(e\)|detail=f".*\{e\}',
        ("api", "modules", "src"),
    )
    return Result(n, "pass" if n == 0 else "fail", "Issue #783 target: 0")


def check_datetime_utcnow() -> Result:
    n = _regex_count(r"datetime\.utcnow\(\)", ("api", "modules", "src"))
    return Result(n, "pass" if n == 0 else "fail", "Issue #768 target: 0")


def check_csrf_router_coverage() -> Result:
    files = _regex_files(r"Depends\(verify_csrf", ("api", "modules", "src"))
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
        sha, tag = _classify_action_pins(_read_text(str(wf)))
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
        if "node_modules" in df.parts:
            continue
        for line in _read_text(str(df)).splitlines():
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

_TEST_DEF_RE = re.compile(r"^\s*(?:async\s+)?def\s+test_", re.MULTILINE)


def check_test_function_count() -> Result:
    total = 0
    for path in _iter_python_files(("tests",)):
        total += sum(1 for _ in _TEST_DEF_RE.finditer(_read_text(str(path))))
    return Result(total, "info", "Issue #789: README must match")


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


# Match `if: false` as a YAML field, not as a substring inside a comment.
_CODEQL_DISABLED_RE = re.compile(r"^\s*if:\s*false\b", re.MULTILINE)


def check_codeql_enabled() -> Result:
    text = _file_text(".github/workflows/codeql-unified.yml")
    if not text:
        return Result("missing", "warn", "Issue #786")
    disabled = bool(_CODEQL_DISABLED_RE.search(text))
    return Result(
        "disabled" if disabled else "enabled",
        "fail" if disabled else "pass",
        "Issue #786",
    )


def check_hollow_assertions() -> Result:
    n = _regex_count(r"assert.*is not None|assert hasattr", ("tests",))
    if n > 300:
        return Result(n, "fail", "Issue #791 target: <100 in Tier 1")
    if n > 100:
        return Result(n, "warn", "Issue #791 target: <100")
    return Result(n, "pass", "Issue #791")


# ---------- wiring / observability ----------

def check_telemetry_middleware() -> Result:
    has_class = _file_contains("api/aurora_api.py", "R2AgentTelemetry")
    has_call = _regex_count(r"track_operation\(", ("api",)) > 0
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
    raw = _regex_files(r"evaluate_action\(", ("api", "modules", "src"))
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
    # Either inline verify_integrity or a helper named *verify*startup*.
    called = (
        "verify_integrity" in init_block
        or "_verify_on_startup" in init_block
    )
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


def check_app_assembly_tests() -> Result:
    path = REPO_ROOT / "tests/test_app_assembly.py"
    if not path.exists():
        return Result("missing", "fail", "Issue #793")
    text = _read_text(str(path))
    has_routes = "EXPECTED_ROUTES" in text
    has_middleware = "EXPECTED_MIDDLEWARE" in text
    has_lifespan = "lifespan" in text.lower()
    score = sum((has_routes, has_middleware, has_lifespan))
    if score == 3:
        return Result("present", "pass", "Issue #793")
    return Result(f"{score}/3", "warn", "Issue #793: scaffold partial")


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

# Files that semantically declare a Python *floor* (requires-python).
# runtime.txt is excluded: it pins the deploy runtime version, not a
# constraint, and may legitimately be ≥ the floor.
# setup.py was removed by #836; pyproject.toml is now the root source.
_FLOOR_PATTERNS = (
    ("pyproject.toml", r"requires-python\s*=\s*['\"](>=\d+\.\d+)"),
    ("sdk/python/pyproject.toml", r"requires-python\s*=\s*['\"](>=\d+\.\d+)"),
    ("cli/pyproject.toml", r"requires-python\s*=\s*['\"](>=\d+\.\d+)"),
)


def check_python_floor_consistency() -> Result:
    floors: set[str] = set()
    for rel, pat in _FLOOR_PATTERNS:
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


_ENV_REF_RE = (
    r"os\.getenv\(\s*['\"]([A-Z_][A-Z0-9_]+)"
    r"|os\.environ\.get\(\s*['\"]([A-Z_][A-Z0-9_]+)"
    r"|os\.environ\[\s*['\"]([A-Z_][A-Z0-9_]+)"
)
_ENV_SKIP = frozenset({
    "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_BASE_REF", "GITHUB_EVENT_NAME",
    "GITHUB_OUTPUT", "USER", "HOME", "PATH",
})


def _env_referenced() -> set[str]:
    rx = re.compile(_ENV_REF_RE)
    referenced: set[str] = set()
    for path in _iter_python_files(("api", "modules", "src", "connector")):
        for m in rx.finditer(_read_text(str(path))):
            name = next((g for g in m.groups() if g), None)
            if name:
                referenced.add(name)
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
    candidates = (REPO_ROOT / "tests/connector", REPO_ROOT / "connector/tests")
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
    Check("testing", "App-assembly test scaffold", "present", "#793",
          check_app_assembly_tests),
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


def _collect_by_domain() -> dict[str, list[tuple[Check, Result]]]:
    by_domain: dict[str, list[tuple[Check, Result]]] = {}
    for check in CHECKS:
        by_domain.setdefault(check.domain, []).append((check, _execute(check)))
    return by_domain


def _tally_fails(rows: Iterable[tuple[Check, Result]]) -> tuple[int, int]:
    any_count = 0
    required_count = 0
    for check, result in rows:
        if result.status != "fail":
            continue
        any_count += 1
        if check.required:
            required_count += 1
    return any_count, required_count


def _print_scorecard(by_domain: dict[str, list[tuple[Check, Result]]]) -> None:
    width_metric = max(len(c.metric) for c in CHECKS) + 2
    width_value = 22
    header = f"{'METRIC'.ljust(width_metric)} {'VALUE'.ljust(width_value)} STATUS  TARGET   ISSUES"
    print(f"\n{header}")
    print("-" * (width_metric + width_value + 30))
    for domain, rows in by_domain.items():
        print(f"\n[{domain.upper()}]")
        for check, result in rows:
            _print_row(check, result, width_metric, width_value)


def run(strict: bool) -> int:
    by_domain = _collect_by_domain()
    _print_scorecard(by_domain)
    all_rows = [pair for rows in by_domain.values() for pair in rows]
    failed_any, failed_required = _tally_fails(all_rows)
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
