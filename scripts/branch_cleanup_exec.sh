#!/usr/bin/env bash
set -euo pipefail

# Aurora CloudBank – Automated branch cleanup helper
# This script interacts with remote branches based on patterns; it prompts for confirmation by default.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
cd "$REPO_ROOT"

PATTERN=${1:-}
DRY=${DRY_RUN:-1}

if [[ -z "$PATTERN" ]]; then
  echo "Usage: $0 <pattern>"
  echo "Examples:"
  echo "  $0 'copilot/fix-*'"
  echo "  $0 'dependabot/*'"
  echo "Environment: DRY_RUN=0 to push deletions"
  exit 2
fi

echo "Scanning remote branches matching: $PATTERN" 1>&2
git fetch --all --prune > /dev/null 2>&1 || true

MATCHES=$(git for-each-ref --format='%(refname:short)' refs/remotes/origin | grep -v '^origin/HEAD$' | sed 's#^origin/##' | grep -E "^${PATTERN//\*/.*}$" || true)

if [[ -z "$MATCHES" ]]; then
  echo "No matches for pattern: $PATTERN" 1>&2
  exit 0
fi

echo "Candidates:" 1>&2
echo "$MATCHES" | sed 's/^/  - /' 1>&2

if [[ "${DRY}" != "0" ]]; then
  echo "DRY RUN: Would delete the following on origin:" 1>&2
  echo "$MATCHES" | sed 's/^/  origin\//'
  exit 0
fi

read -r -p "Proceed to delete these remote branches on origin? (y/N) " ans
if [[ ! "$ans" =~ ^[Yy]$ ]]; then
  echo "Aborted." 1>&2
  exit 1
fi

while read -r BR; do
  echo "Deleting origin/$BR ..." 1>&2
  git push origin --delete "$BR" || true
done <<< "$MATCHES"

echo "Done."
