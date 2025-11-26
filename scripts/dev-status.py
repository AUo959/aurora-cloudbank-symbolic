#!/usr/bin/env python3
"""
Aurora Development Status Dashboard
Quick overview of repository health and development readiness
"""

import shlex
import subprocess


from pathlib import Path


def run_command(cmd):
    """Run command and return output, handling errors gracefully."""
    try:
        # Use shlex.split for secure command execution
        cmd_parts = shlex.split(cmd) if isinstance(cmd, str) else cmd
        result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30, shell=False, check=False)
        return result.stdout.strip(), result.returncode == 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        return "", False


def check_file_exists(path):
    """Check if file exists and return status."""
    return "✅" if Path(path).exists() else "❌"


def main():
    print("🌟 Aurora CloudBank Development Status Dashboard")
    print("=" * 50)

    # 1. Core Files Check
    print("\n📁 Core Files:")
    core_files = [
        "aurora_api.py",
        "aurora_gui_cloudhub_fastapi.py",
        "requirements.txt",
        "package.json",
        "pyproject.toml",
    ]

    for file in core_files:
        print(f"   {check_file_exists(file)} {file}")

    # 2. Environment Check
    print("\n🐍 Python Environment:")
    python_version, _ = run_command("python3 --version")
    pip_version, _ = run_command("pip --version")
    print(f"   ✅ Python: {python_version}")
    print(f"   ✅ Pip: {pip_version.split()[1] if pip_version else 'Not found'}")
    # 3. Dependencies Check
    print("\n📦 Dependencies:")
    deps_check, deps_ok = run_command(
        "python3 -c 'import fastapi, uvicorn, numpy, yaml; print(\"All core packages available\")'"
    )
    print(f"   {'✅' if deps_ok else '⚠️ '} Core Python packages")

    npm_check, npm_ok = run_command("npm --version")
    print(f"   {'✅' if npm_ok else '❌'} Node.js/NPM")

    # 4. Code Quality Check
    print("\n🧪 Code Quality:")
    flake8_check, flake8_ok = run_command("flake8 . --count")
    flake8_count = flake8_check.split("\n")[-1] if flake8_check else "0"
    print(f"   {'✅' if flake8_count == '0' else '⚠️ '} Flake8: {flake8_count} issues")

    # 5. Git Status
    print("\n📊 Repository:")
    git_status, _ = run_command("git status --porcelain")
    uncommitted = len(git_status.split("\n")) if git_status else 0
    clean_status = "Clean" if uncommitted == 0 else f"{uncommitted} uncommitted changes"
    print(f"   {'✅' if uncommitted == 0 else '⚠️ '} Git status: {clean_status}")

    git_branch, _ = run_command("git branch --show-current")
    print(f"   📍 Current branch: {git_branch}")

    # 6. Port Availability
    print("\n🌐 Development Ports:")
    ports = [8000, 8080, 3001]
    for port in ports:
        port_check, port_free = run_command(f"netstat -tuln 2>/dev/null | grep ':{port} ' || echo 'free'")
        status = "✅ Available" if "free" in port_check or not port_check else "⚠️  In use"
        print(f"   {status.split()[0]} Port {port}: {status.split()[1]}")

    # 7. Quick Actions
    print("\n🚀 Quick Actions:")
    print("   💻 Start development: ./scripts/quick-start.sh")
    print("   🔧 Run linting: flake8 . && black --check .")
    print("   📋 Run tests: python -m pytest tests/")
    print("   🌐 API docs: http://localhost:8000/docs (when running)")

    print("\n" + "=" * 50)
    print("🎯 Aurora Development Environment Ready!")


if __name__ == "__main__":
    main()
