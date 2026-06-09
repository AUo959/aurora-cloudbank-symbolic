#!/usr/bin/env bash
# Generates requirements-hashed.txt with SHA256 hashes for supply-chain integrity.
#
# Run this script whenever requirements.txt changes, then commit the output file.
# The resulting requirements-hashed.txt can be used with `pip install --require-hashes`
# to verify that every installed package matches a known-good hash, preventing
# malicious package substitution (dependency confusion, typosquatting, etc.).
#
# Usage:
#   bash scripts/generate_hashed_requirements.sh
#
# Requirements:
#   pip-tools >= 6.0 (pip install pip-tools)
#
# After generation:
#   git add requirements-hashed.txt
#   git commit -m "build: regenerate hashed requirements lock file"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT="${REPO_ROOT}/requirements-hashed.txt"

echo "Installing pip-tools (if not already present)..."
pip install pip-tools --quiet

echo "Generating hashed requirements lock file from requirements.txt..."
pip-compile "${REPO_ROOT}/requirements.txt" \
    --generate-hashes \
    --output-file "${OUTPUT}" \
    --resolver=backtracking \
    --quiet

echo ""
echo "Generated: ${OUTPUT}"
echo "Lines: $(wc -l < "${OUTPUT}")"
echo ""
echo "Next steps:"
echo "  1. Review ${OUTPUT} for any unexpected packages"
echo "  2. git add requirements-hashed.txt"
echo "  3. git commit -m 'build: regenerate hashed requirements lock file'"
echo ""
echo "To validate the hashes against installed packages, run:"
echo "  pip install --require-hashes -r requirements-hashed.txt --dry-run"
