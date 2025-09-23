#!/usr/bin/env bash
set -euo pipefail

# Aurora CloudBank – Safe Repository Cleanup
# - Dry-run by default; set CONFIRM=YES to execute deletions
# - Targets only safe artifacts: *.pyc, __pycache__, common cache dirs, temp dirs
# - Explicitly excludes: .git, .venv*, backups/, bundles, node_modules (except caches), .gitwiz/metrics

usage() {
  cat <<'USAGE'
Usage: scripts/repo_cleanup_safe.sh [options]

Options (all are safe; dry-run unless CONFIRM=YES):
  --remove-pyc       Remove *.pyc files and __pycache__ directories
  --prune-temp       Remove common temp/cache directories (see list)
  --git-maintenance  Run lightweight Git maintenance (git gc --prune=now --aggressive is NOT used)
  --report-large     Report files > 50MB (no deletion)
  --all              Do all of the above
  -q, --quiet        Reduced output
  -h, --help         Show this help

Environment:
  CONFIRM=YES        Perform deletions; otherwise shows dry-run output

USAGE
}

QUIET="NO"
DO_PYC="NO"
DO_TEMP="NO"
DO_GIT="NO"
DO_LARGE="NO"

if [[ $# -eq 0 ]]; then
  usage
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remove-pyc) DO_PYC="YES" ; shift ;;
    --prune-temp) DO_TEMP="YES" ; shift ;;
    --git-maintenance) DO_GIT="YES" ; shift ;;
    --report-large) DO_LARGE="YES" ; shift ;;
    --all) DO_PYC="YES"; DO_TEMP="YES"; DO_GIT="YES"; DO_LARGE="YES"; shift ;;
    -q|--quiet) QUIET="YES" ; shift ;;
    -h|--help) usage ; exit 0 ;;
    *) echo "Unknown option: $1" ; usage ; exit 1 ;;
  esac
done

DRY_RUN="YES"
if [[ "${CONFIRM:-NO}" == "YES" ]]; then
  DRY_RUN="NO"
fi

say() { [[ "$QUIET" == "YES" ]] || echo -e "$@"; }

# Root safety check
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

say "Repo root: $repo_root"
say "Mode: $([[ "$DRY_RUN" == "YES" ]] && echo 'DRY-RUN' || echo 'EXECUTE')"

exclude_prune=(
  "./.git/*"
  "./.venv*"
  "./backups/*"
  "./bundles/*"
  "./.gitwiz/metrics/*"
)

join_excludes() {
  local joined=""
  for p in "${exclude_prune[@]}"; do
    joined+=" -not -path '$p'"
  done
  echo "$joined"
}

removed_total=0

remove_paths() {
  local paths=("$@")
  if [[ ${#paths[@]} -eq 0 || -z "${paths[0]}" ]]; then return 0; fi
  if [[ "$DRY_RUN" == "YES" ]]; then
    printf '%s\n' "${paths[@]}"
  else
    # Remove in batches, tolerate missing
    local count=0
    for p in "${paths[@]}"; do
      if [[ -e "$p" ]]; then
        rm -rf -- "$p" || true
        ((count++)) || true
      fi
    done
    echo "$count"
  fi
}

if [[ "$DO_PYC" == "YES" ]]; then
  say "\n[pyc] Scanning for *.pyc and __pycache__/"
  mapfile -t pyc_files < <(bash -lc "find . -type f -name '*.pyc' $(join_excludes) | sed 's#^\./##'")
  mapfile -t pycache_dirs < <(bash -lc "find . -type d -name '__pycache__' $(join_excludes) | sed 's#^\./##'")
  say "Found ${#pyc_files[@]} .pyc files and ${#pycache_dirs[@]} __pycache__ dirs"
  if [[ "$DRY_RUN" == "YES" ]]; then
    say "Dry-run: would remove .pyc files and __pycache__ dirs"
  else
    count1=$(remove_paths "${pyc_files[@]}" | tail -n1 || echo 0)
    count2=$(remove_paths "${pycache_dirs[@]}" | tail -n1 || echo 0)
    ((removed_total+=count1+count2)) || true
    say "Removed $((count1+count2)) pyc/cache entries"
  fi
fi

if [[ "$DO_TEMP" == "YES" ]]; then
  say "\n[temp] Scanning for temp/cache directories"
  patterns=(
    "./tmp" "./temp" "./.cache" "./**/.cache" "./**/.pytest_cache" "./**/.mypy_cache"
    "./**/.ruff_cache" "./**/.tox" "./**/.nox" "./**/.coverage*"
    "./**/node_modules/.cache" "./**/build" "./**/dist" "./**/.parcel-cache"
  )
  # Build find expression
  expr="-type d \( -name 'tmp' -o -name 'temp' -o -name '.cache' -o -name '.pytest_cache' -o -name '.mypy_cache' -o -name '.ruff_cache' -o -name '.tox' -o -name '.nox' -o -name '.parcel-cache' -o -name 'build' -o -name 'dist' \)"
  mapfile -t temp_dirs < <(bash -lc "shopt -s globstar nullglob; find . $expr $(join_excludes) -print | sed 's#^\./##' | sort -u")
  # Filter out top-level backups and metrics just in case
  safe_temp_dirs=()
  for d in "${temp_dirs[@]:-}"; do
    [[ -z "$d" ]] && continue
    [[ "$d" == backups/* ]] && continue
    [[ "$d" == .gitwiz/metrics* ]] && continue
    safe_temp_dirs+=("$d")
  done
  say "Found ${#safe_temp_dirs[@]} temp/cache directories"
  if [[ "$DRY_RUN" == "YES" ]]; then
    say "Dry-run: would remove these directories:";
    printf '  %s\n' "${safe_temp_dirs[@]}"
  else
    count=$(remove_paths "${safe_temp_dirs[@]}" | tail -n1 || echo 0)
    ((removed_total+=count)) || true
    say "Removed $count temp/cache directories"
  fi
fi

if [[ "$DO_GIT" == "YES" ]]; then
  say "\n[git] Running lightweight maintenance (git fetch --prune; git gc --prune=now)"
  if [[ "$DRY_RUN" == "YES" ]]; then
    say "Dry-run: would run git maintenance"
  else
    git fetch --prune --tags || true
    git gc --prune=now --quiet || true
  fi
fi

if [[ "$DO_LARGE" == "YES" ]]; then
  say "\n[large] Reporting files > 50MB (no deletion)"
  bash -lc "find . -type f -size +50M $(join_excludes) -printf '%s %p\n' | awk '{mb=\$1/1024/1024; \$1=sprintf(\"%6.1fMB\", mb); print}' | sort -hr || true"
fi

say "\nDone. Total removed entries: $removed_total ($([[ \"$DRY_RUN\" == \"YES\" ]] && echo 'dry-run, 0 actually removed'))."
