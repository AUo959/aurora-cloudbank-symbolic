import os
from pathlib import Path
import shlex
import shutil
import subprocess
import time


WORKSPACE_DIR = Path(__file__).resolve().parent.parent
VENV_DIR = WORKSPACE_DIR / ".venv"


def run_command(command, step_name, timeout=300, env=None, cwd=None):
    print(f"[{step_name}] {command}")
    cmd_parts = shlex.split(command) if isinstance(command, str) else command
    subprocess.run(cmd_parts, check=True, timeout=timeout, env=env, cwd=cwd or WORKSPACE_DIR)


def get_venv_env():
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(VENV_DIR)
    env["PATH"] = f"{VENV_DIR / 'bin'}:{env.get('PATH', '')}"
    return env


def ensure_workspace_venv():
    if not (VENV_DIR / "bin" / "python").exists():
        run_command(["python3", "-m", "venv", str(VENV_DIR)], "Workspace venv")
    run_command([str(VENV_DIR / "bin" / "python"), "-m", "pip", "install", "--upgrade", "pip"], "Upgrade pip")


def install_python_dependencies():
    env = get_venv_env()
    setup_script = WORKSPACE_DIR / "scripts" / "setup_environment.sh"
    requirements_file = "requirements.txt"
    if not (WORKSPACE_DIR / requirements_file).exists():
        requirements_file = "requirements.txt"

    if setup_script.exists():
        run_command(["bash", str(setup_script)], "Python setup", env=env)
    else:
        run_command(
            [str(VENV_DIR / "bin" / "python"), "-m", "pip", "install", "-r", requirements_file],
            "Python dependencies",
            env=env,
        )

    run_command(
        [str(VENV_DIR / "bin" / "python"), "-c", "import fastapi; print(fastapi.__version__)"],
        "FastAPI validation",
        env=env,
    )


def run_step(step_name, commands):
    for i, cmd in enumerate(commands, 1):
        print(f"[{step_name}] Attempt {i}: {cmd}")
        try:
            cmd_parts = shlex.split(cmd) if isinstance(cmd, str) else cmd
            subprocess.run(cmd_parts, check=True, timeout=300, cwd=WORKSPACE_DIR)
            print(f"[{step_name}] Success on attempt {i}")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"[{step_name}] Failed attempt {i}: {e}")
            time.sleep(2)
    print(f"[{step_name}] All attempts failed")
    return False


def main():
    overall_success = True
    os.chdir(WORKSPACE_DIR)

    try:
        ensure_workspace_venv()
        install_python_dependencies()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"[Python bootstrap] Failed: {exc}")
        overall_success = False

    # Install system packages (if running as root or via sudo)
    if os.geteuid() == 0 or shutil.which("sudo"):
        overall_success &= run_step(
            "System packages",
            [
                "sudo apt-get update && sudo apt-get install -y python3 python3-pip",
                "sudo apt-get update --fix-missing && sudo apt-get install -y python3 python3-pip",
                "sudo apt-get install -y python3 python3-pip || true",
            ],
        )

    # Install Node dependencies
    overall_success &= run_step(
        "Node dependencies",
        [
            "npm install",
            "npm install --legacy-peer-deps",
            "npm ci || true",
        ],
    )

    # Run onboarding script if available
    if os.path.isfile("scripts/dev/on_startup.sh"):
        overall_success &= run_step("Startup script", ["bash scripts/dev/on_startup.sh"])

    if overall_success:
        print("\n[Bootstrap] Environment initialization complete ✅")
    else:
        print("\n[Bootstrap] Completed with some failures. Review the log above to diagnose issues.")


if __name__ == "__main__":
    main()
