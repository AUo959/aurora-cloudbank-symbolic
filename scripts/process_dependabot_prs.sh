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

# Polling configuration
POLL_INTERVAL_SECONDS=${POLL_INTERVAL_SECONDS:-30}
MAX_WAIT_SECONDS=${MAX_WAIT_SECONDS:-1800} # 30 minutes

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

get_mergeable_state() {
  local pr=$1
  # Guard against transient API/jq failures
  local out
  out=$(api GET "/pulls/$pr" 2>/dev/null || true)
  echo "$out" | jq -r '.mergeable_state // "unknown"' 2>/dev/null || echo "unknown"
}

get_head_sha() {
  local pr=$1
  local out
  out=$(api GET "/pulls/$pr" 2>/dev/null || true)
  echo "$out" | jq -r '.head.sha // ""' 2>/dev/null || echo ""
}

get_ci_overall_state() {
  local sha=$1
  # Prefer Checks API (GitHub Actions) if present; fall back to legacy Status API
  local checks
  checks=$(api GET "/commits/$sha/check-runs" 2>/dev/null || true)
  local total
  total=$(echo "$checks" | jq -r '.total_count // 0' 2>/dev/null || echo 0)
  if [[ "$total" != "0" ]]; then
    # Any in_progress/queued -> pending
    local inprog
    inprog=$(echo "$checks" | jq -r '[.check_runs[] | select(.status=="in_progress" or .status=="queued")] | length' 2>/dev/null || echo 0)
    if (( inprog > 0 )); then
      echo pending
      return 0
    fi
    # Any completed with failure/cancelled/timed_out/action_required -> failure
    local failed
    failed=$(echo "$checks" | jq -r '[.check_runs[] | select(.status=="completed" and (.conclusion=="failure" or .conclusion=="cancelled" or .conclusion=="timed_out" or .conclusion=="action_required"))] | length' 2>/dev/null || echo 0)
    if (( failed > 0 )); then
      echo failure
      return 0
    fi
    # If all completed and none failed -> success (success/neutral/skipped)
    echo success
    return 0
  fi

  # Fallback to Status API combined state
  local state
  state=$(api GET "/commits/$sha/status" 2>/dev/null | jq -r '.state // "pending"' 2>/dev/null || echo pending)
  case "$state" in
    success|failure|error|pending)
      echo "$state" ;;
    *)
      echo pending ;;
  esac
}

wait_for_ci_success() {
  local sha=$1
  local waited=0
  while (( waited < MAX_WAIT_SECONDS )); do
    local state
    state=$(get_ci_overall_state "$sha")
    echo "CI state for $sha: $state"
    case "$state" in
      success)
        return 0 ;;
      failure|error)
        return 1 ;;
      pending|null|"null"|*)
        sleep "$POLL_INTERVAL_SECONDS"
        waited=$(( waited + POLL_INTERVAL_SECONDS )) ;;
    esac
  done
  echo "CI wait timed out for $sha after ${MAX_WAIT_SECONDS}s"
  return 2
}

# Apply labels/comments up front for all PRs
echo "Applying labels and comments to Dependabot PRs..."
for pr in "${PRS[@]}"; do
  echo "Labeling/commenting PR #$pr"
  api POST "/issues/$pr/labels" "$LABELS" >/dev/null 2>&1 || true
  api POST "/issues/$pr/comments" "$(jq -Rn --arg b "$comment_body" '{body: $b}')" >/dev/null 2>&1 || true
done

for pr in "${PRS[@]}"; do
  echo "--- Processing PR #$pr"
  # Add labels (ignore failures)
  api POST "/issues/$pr/labels" "$LABELS" >/dev/null 2>&1 || true
  # Comment (ignore failures)
  api POST "/issues/$pr/comments" "$(jq -Rn --arg b "$comment_body" '{body: $b}')" >/dev/null 2>&1 || true
  # Check mergeable state; poll briefly if unknown
  state="unknown"; tries=0
  while [[ "$state" == "unknown" && $tries -lt 6 ]]; do
    sleep 5
    state=$(get_mergeable_state "$pr")
    ((tries++))
  done
  echo "mergeable_state=$state"

  # Wait for CI success on head sha before merging
  head_sha=$(get_head_sha "$pr")
  if [[ -z "$head_sha" || "$head_sha" == "null" ]]; then
    echo "Could not determine head sha for PR #$pr; skipping merge."
    sleep 1
    continue
  fi
  if wait_for_ci_success "$head_sha"; then
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
      echo "Not mergeable (state: $state) even though CI is green."
    fi
  else
    echo "CI not successful for PR #$pr; skipping merge for now."
  fi
  sleep 1
done

echo "Done processing Dependabot PRs."
