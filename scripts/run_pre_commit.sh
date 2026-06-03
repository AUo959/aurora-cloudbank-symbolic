#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

staged_files="$(git diff --cached --name-only --diff-filter=ACM || true)"
if [[ -z "${staged_files//[[:space:]]/}" ]]; then
  echo "✅ No staged files to validate."
  exit 0
fi

run_gitwiz_scan() {
  local gitwiz_script
  local relevant_files
  local temp_file

  gitwiz_script="$(git ls-files 'scripts/gitwiz_integrated_command.py' | head -n 1 || true)"
  if [[ -z "$gitwiz_script" || ! -f "$gitwiz_script" ]]; then
    echo "ℹ️ GitWiz integrated command not found; skipping staged lint scan."
    return 0
  fi

  relevant_files="$(printf '%s\n' "$staged_files" | grep -E '\.(py|js|jsx|ts|tsx|md)$' || true)"
  if [[ -z "${relevant_files//[[:space:]]/}" ]]; then
    echo "ℹ️ No GitWiz-relevant staged files."
    return 0
  fi

  temp_file="$(mktemp)"
  printf '%s\n' "$relevant_files" > "$temp_file"

  if python3 -m scripts.gitwiz_integrated_command lint-scan --target "$temp_file" >/tmp/gitwiz_precommit.log 2>&1; then
    echo "✅ GitWiz staged lint scan passed."
    rm -f "$temp_file"
    return 0
  fi

  echo "❌ GitWiz staged lint scan failed."
  cat /tmp/gitwiz_precommit.log
  rm -f "$temp_file"
  return 1
}

echo "🔍 Aurora CloudBank canonical pre-commit"
python3 scripts/auto_selective_ingest_gate.py
if [[ -f "./smart-devops" ]]; then
  bash ./smart-devops quick
else
  echo "ℹ️ smart-devops not found; skipping."
fi
run_gitwiz_scan
python3 scripts/git_pre_commit_hook.py

if command -v npm >/dev/null 2>&1 && [[ -f package.json ]]; then
  echo "🧹 Running npm lint check..."
  npm run lint:check || echo "ℹ️ npm lint check reported issues (informational only)."
else
  echo "ℹ️ npm not available; skipping npm lint check."
fi

echo "✅ Aurora pre-commit validation passed."
