#!/usr/bin/env python3
"""

    import shlex

staff_node_ci_helper.py

Automation tool to streamline the pull-commit-push workflow.
It integrates Orion staff node sync and existing CI helpers
so Copilot or other agents can easily maintain the repo.
"""



logger = get_logger("staff_node_ci_helper")

def run_cmd(cmd: str) -> None:
    """Run a shell command and exit on failure."""
    logger.info("Running: %s", cmd)
    try:
        cmd_parts = shlex.split(cmd)
        result = subprocess.run(cmd_parts, timeout=300, shell=False, check=False)
        if result.returncode != 0:
            logger.error("Command failed: %s", cmd)
            sys.exit(result.returncode)
    except subprocess.TimeoutExpired:
        logger.error("Command timed out: %s", cmd)
        sys.exit(1)
    except Exception as e:
        logger.error("Command execution error: %s", e)
        sys.exit(1)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automate pull/commit/push pipeline with staff node support"
    )
    parser.add_argument(
        "--commit-msg",
        default="🔧 Update via staff node helper",
        help="Commit message to use",
    )
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest")
    parser.add_argument(
        "--skip-sync", action="store_true", help="Skip staff registry sync"
    )
    parser.add_argument("--push", action="store_true", help="Push after commit")
    args = parser.parse_args()

    run_cmd("git pull origin main")

    if not args.skip_sync and os.path.exists("scripts/orion_backup_sync.py"):
        sync_cmd = (
            "python scripts/orion_backup_sync.py --command-node command_node_data "
            "--pl-branch pl_branch_data"
        )
        run_cmd(sync_cmd)
    else:
        logger.info("Staff sync skipped")

    run_cmd("bash scripts/ci-maintenance.sh")
    run_cmd("bash scripts/validate-cicd.sh")

    if not args.skip_tests:
        run_cmd("pytest -q")

    run_cmd("git add -A")
    run_cmd('git commit -m "{args.commit_msg}"')

    if args.push:
        run_cmd("git push origin main")

if __name__ == "__main__":
    main()
