#!/usr/bin/env bash
set -euo pipefail

# Requires GITHUB_TOKEN or GH_TOKEN with repo scope.
# Applies labels, posts a standard comment, and merges PRs sequentially when CI is green.

REPO="AUo959/aurora-cloudbank-symbolic"
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
if [[ -z "$TOKEN" ]]; then
  echo "Error: GITHUB_TOKEN or GH_TOKEN not set." >&2
  exit 2
fi

PRS=(146 147 149 148 152 151)
LABELS='["maintenance","dependencies","rebased"]'

comment_body='Title: chore: refresh branch onto main and validate CI

- Rebase/Merge: Updated branch onto latest `main`.
- Conflicts: None (or describe resolutions).
- Lockfile: If applicable, regenerated deterministically.
- CI: Please run full CI and CodeQL.
- Notes: Part of the codespace consolidation effort (2025-09-23).'

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

get_status() {
  local pr=$1
  api GET "/pulls/$pr" | jq -r '.mergeable_state + ":" + (.base.ref // "") + ":" + (.head.sha // "")'
}

for pr in "${PRS[@]}"; do
  echo "--- Processing PR #$pr"
  # Add labels (ignore failures)
  api POST "/issues/$pr/labels" "$LABELS" >/dev/null 2>&1 || true
  # Comment (ignore failures)
  api POST "/issues/$pr/comments" "$(jq -Rn --arg b "$comment_body" '{body: $b}')" >/dev/null 2>&1 || true
  # Check mergeable state; poll a bit if unknown
  state="unknown"; tries=0
  while [[ "$state" == "unknown" && $tries -lt 6 ]]; do
    sleep 5
    state=$(api GET "/pulls/$pr" | jq -r .mergeable_state)
    ((tries++))
  done
  echo "mergeable_state=$state"
  # Only attempt merge when state is clean or has_hooks
  if [[ "$state" == "clean" || "$state" == "has_hooks" ]]; then
    resp=$(api PUT "/pulls/$pr/merge" '{"merge_method":"squash"}') || true
    merged=$(echo "$resp" | jq -r .merged 2>/dev/null || echo "false")
    if [[ "$merged" == "true" ]]; then
      echo "Merged PR #$pr"
    else
      message=$(echo "$resp" | jq -r .message 2>/dev/null || echo "")
      echo "Skipped merge for PR #$pr (state: $state). $message"
    fi
  else
    echo "Not mergeable now (state: $state)."
  fi
  sleep 1
done

echo "Done processing Dependabot PRs."
