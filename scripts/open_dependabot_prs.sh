#!/usr/bin/env bash
set -euo pipefail

# Open GitHub compare pages to create PRs for Dependabot branches.
# Dry-run prints URLs. Set OPEN=YES to actually open in default browser via $BROWSER.
# Usage:
#   bash scripts/open_dependabot_prs.sh                  # print URLs only
#   OPEN=YES bash scripts/open_dependabot_prs.sh         # open URLs in browser

get_repo_slug() {
  local url
  url=$(git config --get remote.origin.url)
  case "$url" in
    git@github.com:*)
      echo "${url#git@github.com:}" | sed 's/\.git$//' ;;
    https://github.com/*)
      echo "${url#https://github.com/}" | sed 's/\.git$//' ;;
    http://github.com/*)
      echo "${url#http://github.com/}" | sed 's/\.git$//' ;;
    *)
      echo "" ;;
  esac
}

slug=$(get_repo_slug)
if [[ -z "$slug" ]]; then
  echo "Could not determine GitHub repo slug from origin remote." >&2
  exit 2
fi

owner=${slug%%/*}

branches=(
  "dependabot/npm_and_yarn/concurrently-9.2.1"
  "dependabot/npm_and_yarn/helmet-8.1.0"
  "dependabot/pip/incremental-24.7.2"
  "dependabot/pip/mercurial-7.1.1"
  "dependabot/pip/netaddr-1.3.0"
  "dependabot/pip/s3transfer-0.14.0"
)

for br in "${branches[@]}"; do
  url="https://github.com/${slug}/compare/main...${owner}:${br}?expand=1"
  echo "$url"
  if [[ "${OPEN:-NO}" == "YES" ]]; then
    if [[ -n "${BROWSER:-}" ]]; then
      "$BROWSER" "$url" >/dev/null 2>&1 || true
    else
      # Try xdg-open as a fallback in Linux containers
      command -v xdg-open >/dev/null 2>&1 && xdg-open "$url" >/dev/null 2>&1 || true
    fi
  fi
done

echo "Tip: Set OPEN=YES to open these in your browser." >&2
