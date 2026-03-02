#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "[setup-gpg] Diagnostic mode (no keys imported, no config changed)."

if command -v gpg >/dev/null 2>&1; then
  echo "- gpg available: $(gpg --version | head -n 1)"
  key_count=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | rg -c '^sec' || true)
  echo "- detected secret keys: ${key_count:-0}"
else
  echo "- gpg is not installed"
fi

for candidate in aurora-public-key.asc gpg_pubkey_for_github.asc; do
  if [ -f "$candidate" ]; then
    echo "- found key material: $candidate"
  fi
done

echo "Guidance: review key files and run an explicit import command only when ready."
