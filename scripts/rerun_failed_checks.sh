#!/usr/bin/env bash
set -euo pipefail

# List and optionally re-request failed/cancelled/timed_out/action_required check-runs for PRs.
# Usage:
#   scripts/rerun_failed_checks.sh 146 147 149
# Env:
#   GITHUB_TOKEN or GH_TOKEN: token with repo scope
#   CONFIRM=YES to actually send rerun requests (otherwise dry-run)

REPO="AUo959/aurora-cloudbank-symbolic"
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
if [[ -z "${TOKEN}" ]]; then
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

total_to_rerun=0
for pr in "$@"; do
  pr_json=$(api GET "/pulls/$pr")
  sha=$(echo "$pr_json" | jq -r .head.sha)
  if [[ -z "$sha" || "$sha" == "null" ]]; then
    echo "PR #$pr: unable to get head SHA; skipping" >&2
    continue
  fi
  checks=$(api GET "/commits/$sha/check-runs")
  echo "PR #$pr (sha=$sha):"
  # Collect failed check runs and try to infer workflow run IDs from details_url
  mapfile -t rows < <(echo "$checks" | jq -r '.check_runs[] | [.id, .name, .status, .conclusion, .details_url] | @tsv')
  declare -A run_ids_seen=()
  for row in "${rows[@]}"; do
    IFS=$'\t' read -r id name status conclusion details <<<"$row"
    if [[ "$status" == "completed" && ( "$conclusion" == "failure" || "$conclusion" == "cancelled" || "$conclusion" == "timed_out" || "$conclusion" == "action_required" ) ]]; then
      echo "  - FAIL: id=$id name=$name conclusion=$conclusion"
      (( total_to_rerun++ ))
      if [[ -n "${details:-}" ]]; then
        rid=$(echo "$details" | grep -oE '/runs/[0-9]+' | grep -oE '[0-9]+' | head -n1 || true)
        if [[ -n "$rid" ]]; then
          run_ids_seen[$rid]=1
        fi
      fi
    fi
  done
  # If confirming, rerun each unique workflow run id
  if [[ "${CONFIRM:-NO}" == "YES" && ${#run_ids_seen[@]} -gt 0 ]]; then
    for rid in "${!run_ids_seen[@]}"; do
      echo "  -> Re-running workflow run $rid"
      api POST "/actions/runs/$rid/rerun" >/dev/null 2>&1 || true
    done
  fi
done

if [[ "${CONFIRM:-NO}" != "YES" ]]; then
  echo "Dry-run complete. Set CONFIRM=YES to re-run associated workflow runs." >&2
else
  echo "Requested reruns for failed workflows where available."
fi
