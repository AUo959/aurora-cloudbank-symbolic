#!/usr/bin/env bash
set -euo pipefail

# Guarded rebase helper for 'Review Needed' branches.
# Usage:
#   bash scripts/rebase_review_branches.sh                       # dry-run (prints)
#   bash scripts/rebase_review_branches.sh --pattern '^dependabot/'
#   bash scripts/rebase_review_branches.sh --branch codex/foo --branch codex/bar
#   CONFIRM=YES bash scripts/rebase_review_branches.sh --execute --pattern '^dependabot/'

DRY_RUN=1
PATTERN=""
declare -a ONLY_BRANCHES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute)
      if [[ "${CONFIRM:-NO}" != "YES" ]]; then
        echo 'Refusing to execute without CONFIRM=YES' >&2; exit 2
      fi
      DRY_RUN=0
      shift
      ;;
    --pattern)
      PATTERN="${2:-}"
      shift 2
      ;;
    --branch)
      ONLY_BRANCHES+=("${2:-}")
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2; exit 2
      ;;
  esac
done

branches=(
  "codex/add-import_arc_file-function"
  "codex/add-import_arc_file-function-aqaiwv"
  "codex/add-import_arc_file-function-oobujt"
  "codex/add-import_arc_file-function-ykro34"
  "codex/deprecate-crypto.js-and-update-imports"
  "codex/design-pqn-modular-architecture-with-orion-integration"
  "codex/enhance-arc-and-open-pr"
  "codex/enhance-arc-and-open-pr-2zl12j"
  "codex/enhance-arc-and-open-pr-bbckr7"
  "codex/enhance-arc-and-open-pr-ptoteb"
  "codex/refactor-diagnostics-for-async-file-handling"
  "codex/refactor-numeric-checks-in-aurora_api.py"
  "codex/remove-large-binary-files-from-version-control"
  "codex/replace-crypto.js-with-environment-keys"
  "codex/validate-command-input-in-ethics_layer"
  "dependabot/npm_and_yarn/concurrently-9.2.1"
  "dependabot/npm_and_yarn/helmet-8.1.0"
  "dependabot/pip/incremental-24.7.2"
  "dependabot/pip/mercurial-7.1.1"
  "dependabot/pip/netaddr-1.3.0"
  "dependabot/pip/s3transfer-0.14.0"
)

# Apply filters
declare -a TARGETS=()
if [[ ${#ONLY_BRANCHES[@]} -gt 0 ]]; then
  TARGETS=("${ONLY_BRANCHES[@]}")
else
  for b in "${branches[@]}"; do
    if [[ -z "$PATTERN" || "$b" =~ $PATTERN ]]; then
      TARGETS+=("$b")
    fi
  done
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "No branches matched the filter; nothing to do." >&2
  exit 0
fi

echo 'Fetching remotes...' >&2
git fetch origin --prune

for br in "${TARGETS[@]}"; do
  echo '---' >&2
  echo "[INFO] Processing origin/$br" >&2
  echo "git checkout -B $br origin/$br"
  echo "git rebase --rebase-merges --autostash origin/main"
  echo "git push --force-with-lease origin $br"
  if [[ $DRY_RUN -eq 0 ]]; then
    git checkout -B "$br" "origin/$br"
    if git rebase --rebase-merges --autostash origin/main; then
      git push --force-with-lease origin "$br"
      echo "[OK] Rebased and pushed origin/$br" >&2
    else
      echo "[WARN] Conflicts on origin/$br; aborting rebase. Consider manual merge." >&2
      git rebase --abort || true
    fi
  fi
done

git checkout main >/dev/null 2>&1 || true
