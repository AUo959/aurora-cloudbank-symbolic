#!/bin/bash
# Quick activation script for Aurora CloudBank environment

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$REPO_ROOT/.venv/bin/activate" ]]; then
  source "$REPO_ROOT/.venv/bin/activate"
  if [[ -f "$REPO_ROOT/.env" ]]; then
    set -a
    source "$REPO_ROOT/.env"
    set +a
  fi
    echo "✅ Aurora CloudBank environment activated"
    echo "🌐 API docs: http://localhost:8000/docs (when running)"
    echo "🧪 Run tests: python -m pytest tests/"
    echo "🔧 Validate deps: python scripts/validate_dependencies.py"
else
    echo "❌ Virtual environment not found"
    echo "Run: bash scripts/setup_environment.sh"
fi
