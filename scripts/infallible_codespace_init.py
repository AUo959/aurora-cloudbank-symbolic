import os
import shutil
import subprocess
import time
import shlex


def run_step(step_name, commands):
    import shlex

    for i, cmd in enumerate(commands, 1):
        print(f"\n[{step_name}] Attempt {i}: {cmd}")
        try:
            cmd_parts = shlex.split(cmd) if isinstance(cmd, str) else cmd
            subprocess.run(cmd_parts, check=True, timeout=300)
            print(f"[{step_name}] Success on attempt {i}")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"[{step_name}] Failed attempt {i}: {e}")
            time.sleep(2)
    print(f"[{step_name}] All attempts failed\n")
    return False


def main():
    overall_success = True

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

    # Install Python dependencies
    overall_success &= run_step(
        "Python dependencies",
        [
            "pip install -r requirements.txt",
            "pip install -r requirements.txt --no-cache-dir",
            "pip install -r requirements.txt || true",
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
