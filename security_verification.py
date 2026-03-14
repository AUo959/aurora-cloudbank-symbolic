#!/usr/bin/env python3
"""
🔒 Aurora CloudBank Security Verification & Final Report
Post-remediation security verification and comprehensive audit report.
"""

import ast
import shlex
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_ROOT = REPO_ROOT / "scripts"
IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist"}


def secure_run(cmd: str) -> tuple[str, str, int]:
    """Securely execute command without shell injection."""
    try:
        cmd_parts = shlex.split(cmd)
        result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30, check=False)
        return result.stdout, result.stderr, result.returncode
    except (subprocess.TimeoutExpired, OSError) as e:
        return "", str(e), 1


def iter_script_python_files():
    """Yield repo-owned Python scripts for runtime security verification."""
    if not SCRIPTS_ROOT.exists():
        return

    for path in SCRIPTS_ROOT.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def call_name(node: ast.AST) -> str:
    """Return a dotted call name when it can be resolved statically."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def shell_keyword_is_true(node: ast.Call) -> bool:
    """Return True when a call explicitly sets shell=True."""
    for keyword in node.keywords:
        if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
            return True
    return False


def inspect_script_runtime_risks():
    """Scan script files for real runtime risk sites instead of matching raw strings."""
    shell_true_sites = []
    dynamic_exec_sites = []

    for path in iter_script_python_files() or []:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue

        relative_path = path.relative_to(REPO_ROOT)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            name = call_name(node.func)
            line = getattr(node, "lineno", 0)

            if name in {"eval", "exec"}:
                dynamic_exec_sites.append((relative_path, line, name))
            elif name.startswith("subprocess.") and shell_keyword_is_true(node):
                shell_true_sites.append((relative_path, line, name))

    return shell_true_sites, dynamic_exec_sites


def main():
    """Generate final security verification report."""
    print("🔒 AURORA CLOUDBANK - FINAL SECURITY VERIFICATION")
    print("=" * 60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Verification: Current runtime security snapshot")
    print()

    # Check for remaining vulnerabilities
    print("🔍 VULNERABILITY SCAN RESULTS")
    print("-" * 40)

    shell_true_sites, dynamic_exec_sites = inspect_script_runtime_risks()
    critical_findings = 0
    dynamic_exec_warnings = 0
    infra_warnings = 0
    missing_infra = 0

    if shell_true_sites:
        critical_findings += len(shell_true_sites)
        print("❌ CRITICAL: shell=True vulnerabilities still found:")
        for file_path, line, callsite in shell_true_sites:
            print(f"   - {file_path}:{line} ({callsite})")
    else:
        print("✅ shell=True vulnerabilities: RESOLVED")

    if dynamic_exec_sites:
        dynamic_exec_warnings += len(dynamic_exec_sites)
        print("⚠️  WARNING: Dynamic code execution found:")
        for file_path, line, callsite in dynamic_exec_sites:
            print(f"   - {file_path}:{line} ({callsite})")
    else:
        print("✅ Dynamic code execution: CLEAN")

    print()
    print("🛡️  SECURITY INFRASTRUCTURE STATUS")
    print("-" * 40)

    security_files = {
        ".security/security_policy.json": [".security/security_policy.json"],
        ".security/secure_helpers.py": [".security/secure_helpers.py", ".security/secure_helpers.py.disabled"],
        ".github/security-config.yml": [".github/security-config.yml"],
        "SECURITY.md": ["SECURITY.md"],
    }

    for label, candidates in security_files.items():
        resolved = next((candidate for candidate in candidates if (REPO_ROOT / candidate).exists()), None)
        if resolved is None:
            print(f"❌ {label} MISSING")
            missing_infra += 1
        elif resolved.endswith(".disabled"):
            print(f"⚠️  {label} present as disabled artifact ({Path(resolved).name})")
            infra_warnings += 1
        else:
            print(f"✅ {label}")

    print()
    print("📊 VERIFICATION SUMMARY")
    print("-" * 40)
    print(f"Critical findings: {critical_findings}")
    print(f"Dynamic execution warnings: {dynamic_exec_warnings}")
    print(f"Infrastructure warnings: {infra_warnings}")
    print(f"Missing infrastructure files: {missing_infra}")

    print()
    print("🎯 SECURITY COMPLIANCE STATUS")
    print("-" * 40)
    if critical_findings == 0 and dynamic_exec_warnings == 0 and infra_warnings == 0 and missing_infra == 0:
        print("✅ Runtime verification: clean")
        print("✅ Shell injection: protected")
        print("✅ Dynamic execution: not detected")
        print("✅ Security infrastructure: complete")
    else:
        print("⚠️  Review required before calling the audit fully clean")
        print(f"⚠️  Shell injection findings: {critical_findings}")
        print(f"⚠️  Dynamic execution findings: {dynamic_exec_warnings}")
        print(f"⚠️  Infrastructure warnings: {infra_warnings}")
        print(f"⚠️  Infrastructure gaps: {missing_infra}")

    print()
    print("🚀 NEXT STEPS")
    print("-" * 40)
    print("1. Fix or explicitly justify any remaining script runtime findings")
    print("2. Re-enable or remove disabled security helper artifacts intentionally")
    print("3. Keep dependency and governance scans in the regular validation loop")

    print()
    print("=" * 60)
    if critical_findings == 0 and dynamic_exec_warnings == 0 and infra_warnings == 0 and missing_infra == 0:
        print("🎉 AURORA CLOUDBANK VERIFICATION IS CLEAN")
        print("🔒 No runtime script regressions were detected")
        print("🛡️  Security infrastructure checks passed")
    else:
        print("🔍 AURORA CLOUDBANK VERIFICATION REQUIRES FOLLOW-UP")
        print("🛠️  Findings above should be reviewed before treating the audit as final")
    print("=" * 60)


if __name__ == "__main__":
    main()
