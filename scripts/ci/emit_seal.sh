#!/usr/bin/env bash
# T1/SRB approval seal emitter for CI audit
set -euo pipefail
DATA="$1"
SEAL=$(printf "%s" "$DATA" | sha256sum | cut -d' ' -f1)
echo "seal=$SEAL"