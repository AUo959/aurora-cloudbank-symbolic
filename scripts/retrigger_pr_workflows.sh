#!/usr/bin/env bash
set -euo pipefail

# Close and reopen PRs to trigger pull_request.reopened events (re-runs CodeQL, etc.)
# Usage: scripts/retrigger_pr_workflows.sh 146 147 ...
# Env: GITHUB_TOKEN or GH_TOKEN must be set. Set CONFIRM=YES to actually perform close/open.

REPO="AUo959/aurora-cloudbank-symbolic"
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
if [[ -z "$TOKEN" ]]; then
  echo "Error: GITHUB_TOKEN or GH_TOKEN not set." >&2
  exit 2
fi

if [[ $# -eq 0 ]]; then
  echo "Provide one or more PR numbers." >&2
  exit 1
fi

api() {
  local method="$1" path="$2" data="${3:-}"
  if [[ -n "$data" ]]; then
    curl -sS -X "$method" -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
      -d "$data" "https://api.github.com/repos/$REPO$path"
  else
    curl -sS -X "$method" -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/$REPO$path"
  fi
}

for pr in "$@"; do
  meta=$(api GET "/pulls/$pr")
  state=$(echo "$meta" | jq -r .state)
  head=$(echo "$meta" | jq -r .head.ref)
  echo "PR #$pr: current_state=$state head=$head"
  if [[ "${CONFIRM:-NO}" != "YES" ]]; then
    echo "  dry-run: would close then reopen PR #$pr"
    continue
  fi
  if [[ "$state" != "open" ]]; then
    echo "  skipping: PR not open"
    continue
  fi
  echo "  closing PR #$pr..."
  api PATCH "/pulls/$pr" '{"state":"closed"}' >/dev/null
  sleep 2
  echo "  reopening PR #$pr..."
  api PATCH "/pulls/$pr" '{"state":"open"}' >/dev/null
  # Add a note
  api POST "/issues/$pr/comments" "$(jq -Rn --arg b "CI retriggered by close/reopen to refresh CodeQL after config fix." '{body: $b}')" >/dev/null || true
  echo "  retriggered"
  sleep 2
done

echo "Done."
