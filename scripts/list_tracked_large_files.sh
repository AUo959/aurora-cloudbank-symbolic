#!/usr/bin/env bash
set -euo pipefail

threshold_mb=${1:-10}

git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "Not a git repo" >&2; exit 1; }

git ls-files -z | while IFS= read -r -d '' f; do
  if [[ -f "$f" ]]; then
    sz=$(stat -c %s "$f" 2>/dev/null || echo 0)
    if (( sz > threshold_mb*1024*1024 )); then
      printf "%8.1fMB %s\n" "$(echo "$sz" | awk '{printf $1/1024/1024}')" "$f"
    fi
  fi
done | sort -hr || true
