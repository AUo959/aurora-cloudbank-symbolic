#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENSURE_PYTHON_ENV=0
UPGRADE_PYTHON_DEPS=0
CHECK_OUTDATED=0
INCLUDE_OPTIONAL=0

cd "$REPO_ROOT"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--ensure-python-env] [--upgrade-python-deps] [--check-outdated] [--include-optional]

Run the canonical maintenance flow.

Flags:
  --ensure-python-env   Rebuild the canonical Python environment before reporting
  --upgrade-python-deps Upgrade Python dependencies from requirements files
  --check-outdated      Attempt network-backed outdated dependency checks
  --include-optional    Include requirements-optional.txt during Python maintenance
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --ensure-python-env)
      ENSURE_PYTHON_ENV=1
      ;;
    --upgrade-python-deps)
      UPGRADE_PYTHON_DEPS=1
      ;;
    --check-outdated)
      CHECK_OUTDATED=1
      ;;
    --include-optional)
      INCLUDE_OPTIONAL=1
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[maintenance] Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

dependency_cmd=(python3 scripts/gitwiz_dependency_updater.py --scan --output logs/dependency_status.json)
[ "$ENSURE_PYTHON_ENV" -eq 1 ] && dependency_cmd+=(--ensure-env --apply)
[ "$UPGRADE_PYTHON_DEPS" -eq 1 ] && dependency_cmd+=(--upgrade-python --apply)
[ "$CHECK_OUTDATED" -eq 1 ] && dependency_cmd+=(--check-outdated)
[ "$INCLUDE_OPTIONAL" -eq 1 ] && dependency_cmd+=(--include-optional)

echo "[maintenance] Validating Python environment and dependency status..."
"${dependency_cmd[@]}"

echo "[maintenance] Running branch cleanup wrapper..."
python3 scripts/branch_cleanup.py

echo "[maintenance] Writing repository health report..."
python3 scripts/repo_health_monitor.py --output logs/repo_health_status.json

echo "[maintenance] Maintenance complete."
