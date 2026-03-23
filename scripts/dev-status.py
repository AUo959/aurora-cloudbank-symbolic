#!/usr/bin/env python3
"""
Aurora Development Status Dashboard
Quick overview of repository health and development readiness
"""

import shlex
import socket
import subprocess
import sys


from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = REPO_ROOT / ".venv/bin/python"
VENV_PIP = REPO_ROOT / ".venv/bin/pip"
VENV_FLAKE8 = REPO_ROOT / ".venv/bin/flake8"


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
    return "✅" if (REPO_ROOT / path).exists() else "❌"


def python_command(*args):
    """Build a Python command using the project venv when available."""
    executable = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)
    return [str(executable), *args]


def pip_command(*args):
    """Build a pip command using the project venv when available."""
    executable = VENV_PIP if VENV_PIP.exists() else ["pip"]
    if isinstance(executable, Path):
        return [str(executable), *args]
    return [*executable, *args]


def flake8_command(*args):
    """Build a flake8 command using the project venv when available."""
    executable = VENV_FLAKE8 if VENV_FLAKE8.exists() else ["flake8"]
    if isinstance(executable, Path):
        return [str(executable), *args]
    return [*executable, *args]


def is_port_in_use(port):
    """Check whether a localhost TCP port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def main():
    print("🌟 Aurora CloudBank Development Status Dashboard")
    print("=" * 50)

    # 1. Core Files Check
    print("\n📁 Core Files:")
    core_files = [
        "api/aurora_api.py",
        "api/aurora_gui_cloudhub_fastapi.py",
        "requirements.txt",
        "package.json",
        "pyproject.toml",
    ]

    for file in core_files:
        print(f"   {check_file_exists(file)} {file}")

    # 2. Environment Check
    print("\n🐍 Python Environment:")
    python_version, _ = run_command(python_command("--version"))
    pip_version, _ = run_command(pip_command("--version"))
    print(f"   ✅ Python: {python_version}")
    print(f"   ✅ Pip: {pip_version.split()[1] if pip_version else 'Not found'}")
    # 3. Dependencies Check
    print("\n📦 Dependencies:")
    deps_check, deps_ok = run_command(
        python_command("-c", 'import fastapi, uvicorn, numpy, yaml; print("All core packages available")')
    )
    print(f"   {'✅' if deps_ok else '⚠️ '} Core Python packages")

    npm_check, npm_ok = run_command("npm --version")
    print(f"   {'✅' if npm_ok else '❌'} Node.js/NPM")

    # 4. Code Quality Check
    print("\n🧪 Code Quality:")
    flake8_check, flake8_ok = run_command(flake8_command(".", "--count"))
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
        status = "⚠️  In use" if is_port_in_use(port) else "✅ Available"
        emoji, message = status.split(maxsplit=1)
        print(f"   {emoji} Port {port}: {message}")

    # 7. Quick Actions
    print("\n🚀 Quick Actions:")
    print("   💻 Start development: ./scripts/quick-start.sh")
    print("   🔧 Run linting: .venv/bin/flake8 . && .venv/bin/black --check .")
    print("   📋 Run tests: .venv/bin/python -m pytest tests/")
    print("   🌐 API docs: http://localhost:8000/docs (when running)")

    print("\n" + "=" * 50)
    print("🎯 Aurora Development Environment Ready!")


if __name__ == "__main__":
    main()
