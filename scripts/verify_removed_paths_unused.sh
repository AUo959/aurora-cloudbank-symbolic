#!/usr/bin/env bash
set -euo pipefail

# Purpose: Non-blocking check for references to removed/legacy paths.
# Prints warnings if any files reference deprecated locations. Always exits 0.

ROOT_DIR="${1:-$(pwd)}"

removed_paths=(
  ".archived_requirements"
  ".backup/requirements"
  ".ssmt_backups"
  "requirements-.*\\.txt"
)

echo "[verify] Scanning for references to removed/legacy paths in $ROOT_DIR"

found=0
for pattern in "${removed_paths[@]}"; do
  # Use ripgrep if available for speed; fall back to grep
  if command -v rg >/dev/null 2>&1; then
    matches=$(rg -n --hidden --glob '!node_modules/**' --glob '!.git/**' --glob '!htmlcov/**' --glob '!coverage/**' --no-messages -e "$pattern" "$ROOT_DIR" || true)
  else
    matches=$(grep -RIn --exclude-dir={.git,node_modules,htmlcov,coverage} --binary-files=without-match -E "$pattern" "$ROOT_DIR" 2>/dev/null || true)
  fi

  if [[ -n "$matches" ]]; then
    found=1
    echo "---"
    echo "WARN: References found for pattern [$pattern]:"
    echo "$matches" | head -n 200
    echo "---"
  fi
done

if [[ "$found" -eq 0 ]]; then
  echo "[verify] No references to removed/legacy paths detected."
else
  echo "[verify] Completed with warnings (non-blocking). Please update referencing scripts/files."
fi

exit 0
