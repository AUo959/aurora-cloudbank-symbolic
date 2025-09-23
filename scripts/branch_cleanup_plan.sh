#!/usr/bin/env bash
set -euo pipefail

# Aurora CloudBank – Branch Cleanup Plan Generator
# Produces a Markdown plan with suggested actions for remote branches relative to main

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
cd "$REPO_ROOT"

echo "# Branch Cleanup Plan"
echo
echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%SZ')"
echo

echo "Fetching remotes..." 1>&2
git fetch --all --prune > /dev/null 2>&1 || true

MAIN=origin/main
if ! git rev-parse --verify -q "$MAIN" >/dev/null; then
  echo "❌ Could not find $MAIN" 1>&2
  exit 1
fi

echo "| Branch | Ahead | Behind | Last Commit (UTC) | Category | Suggested Action |"
echo "|--------|-------|--------|--------------------|----------|------------------|"

git for-each-ref --format='%(refname:short)' refs/remotes/origin | grep -v '^origin/HEAD$' | while read -r RB; do
  BR=${RB#origin/}
  if [[ "$BR" == "main" ]]; then
    continue
  fi

  AHEAD=$(git rev-list --count "$MAIN..$RB" 2>/dev/null || echo 0)
  BEHIND=$(git rev-list --count "$RB..$MAIN" 2>/dev/null || echo 0)
  LAST=$(git log -1 --date=format-local:'%Y-%m-%d %H:%M:%SZ' --pretty=format:%cd --date=iso-strict "$RB" 2>/dev/null || echo "-")

  CATEGORY="up-to-date"
  SUGGEST="No action"
  if [[ "$AHEAD" -gt 0 && "$BEHIND" -gt 0 ]]; then
    CATEGORY="diverged"
    SUGGEST="Rebase/merge main; resolve conflicts; refresh PR"
  elif [[ "$BEHIND" -gt 0 ]]; then
    CATEGORY="behind"
    SUGGEST="Merge main or close if obsolete"
  elif [[ "$AHEAD" -gt 0 ]]; then
    CATEGORY="ahead"
    SUGGEST="Open/refresh PR against main"
  fi

  if [[ "$BR" == dependabot/* ]]; then
    SUGGEST="Update base then close/recreate Dependabot PR if needed"
  elif [[ "$BR" == copilot/fix-* ]]; then
    SUGGEST="Review; merge if relevant or close as obsolete"
  fi

  echo "| $BR | $AHEAD | $BEHIND | ${LAST:-'-'} | $CATEGORY | $SUGGEST |"
done
