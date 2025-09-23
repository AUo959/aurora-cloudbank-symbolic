#!/usr/bin/env bash
set -euo pipefail

# Generate a safe prune plan for remote branches fully merged into origin/main.
# - Dry-run by default: writes MERGED_BRANCH_PRUNE_PLAN.md with backup + delete commands
# - Set CONFIRM=YES to also create bundles and delete remote branches
# - Optional filter: --pattern 'regex' to include only matching branches

usage() {
  cat <<'USAGE'
Usage: scripts/generate_merged_branch_prune_plan.sh [--pattern REGEX] [--execute]

Options:
  --pattern REGEX   Only include branches matching REGEX (applied to short name)
  --execute         Perform backups and delete remote branches (requires CONFIRM=YES)
  -h, --help        Show this help

Behavior:
  - Excludes: origin/HEAD, origin/main, origin/gh-pages (if present)
  - Output: MERGED_BRANCH_PRUNE_PLAN.md with commands and safety notes
  - Backups: backups/<branch>-<timestamp>.bundle
USAGE
}

PATTERN=""
DO_EXECUTE="NO"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pattern) PATTERN=${2:-}; shift 2;;
    --execute) DO_EXECUTE="YES"; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown option: $1" >&2; usage; exit 1;;
  esac
done

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || { echo 'Not a git repo' >&2; exit 2; })"
cd "$repo_root"

git fetch --prune --tags >/dev/null 2>&1 || true

timestamp=$(date -u +%Y%m%dT%H%M%SZ)
plan_file="MERGED_BRANCH_PRUNE_PLAN.md"
mkdir -p backups

mapfile -t merged < <(git branch -r --merged origin/main \
  | sed 's/^\s*//; s/\s*$//' \
  | grep -vE '^(origin/HEAD|origin/main|origin/gh-pages)$' \
  | grep -v ' -> ' || true)

# Filter by pattern if provided
filtered=()
for ref in "${merged[@]}"; do
  short="${ref#origin/}"
  if [[ -n "$PATTERN" ]]; then
    if [[ "$short" =~ $PATTERN ]]; then
      filtered+=("$short")
    fi
  else
    filtered+=("$short")
  fi
done

{
  echo "# Merged Branch Prune Plan"
  echo "Generated: $timestamp"
  echo
  if [[ ${#filtered[@]} -eq 0 ]]; then
    echo "No remote branches fully merged into main (after exclusions)."
  else
    echo "The following branches are fully merged into main and eligible for safe pruning:"
    echo
    for b in "${filtered[@]}"; do
      echo "- origin/$b"
    done
    echo
    echo "## Safety Procedure"
    echo "1) Create a backup bundle for each branch"
    echo "2) Delete the remote branch"
    echo
    echo '```bash'
    for b in "${filtered[@]}"; do
      echo "git bundle create backups/${b//\//-}-$timestamp.bundle origin/$b"
    done
    for b in "${filtered[@]}"; do
      echo "git push origin --delete $b"
    done
    echo '```'
    echo
    echo "Bundles will be created under backups/ and are already gitignored."
  fi
} > "$plan_file"

echo "Wrote $plan_file with ${#filtered[@]} candidate(s)."

if [[ "$DO_EXECUTE" == "YES" ]]; then
  if [[ "${CONFIRM:-NO}" != "YES" ]]; then
    echo "Refusing to execute without CONFIRM=YES" >&2
    exit 3
  fi
  for b in "${filtered[@]}"; do
    git bundle create "backups/${b//\//-}-$timestamp.bundle" "origin/$b" || true
    git push origin --delete "$b" || true
  done
  echo "Executed backup + remote delete for ${#filtered[@]} branches."
fi
