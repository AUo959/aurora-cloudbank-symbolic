#!/bin/bash
set -euo pipefail

REAL_NAME="${AURORA_GPG_NAME:-Aurora CloudBank Orion Station}"
EMAIL="${AURORA_GPG_EMAIL:-tlstreets@gmail.com}"
KEY_COMMENT="${AURORA_GPG_COMMENT:-Aurora GPG 2025}"
KEY_TYPE="${AURORA_GPG_TYPE:-rsa}"
KEY_LENGTH="${AURORA_GPG_LENGTH:-4096}"
KEY_EXPIRE="${AURORA_GPG_EXPIRE:-1y}"
EXPORT_PATH="${AURORA_GPG_EXPORT_PATH:-gpg_pubkey_for_github.asc}"
EXECUTE=0
CONFIGURE_GIT=1

usage() {
  cat <<EOF
Usage: $(basename "$0") [--execute] [--no-configure-git]

Diagnose or create the Aurora GPG signing configuration.

Default mode is diagnostic-only. Re-run with --execute to generate a key,
export the public key, and optionally configure global git signing settings.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --execute)
      EXECUTE=1
      ;;
    --no-configure-git)
      CONFIGURE_GIT=0
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[setup-gpg-robust] Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

echo "Aurora CloudBank GPG Setup"
echo "=========================="
echo "Name: $REAL_NAME"
echo "Email: $EMAIL"
echo "Export path: $EXPORT_PATH"

if command -v gpg >/dev/null 2>&1; then
  echo "[setup-gpg-robust] gpg detected: $(command -v gpg)"
  gpg --list-secret-keys --keyid-format LONG "$EMAIL" 2>/dev/null || true
else
  echo "[setup-gpg-robust] gpg is not installed"
fi

if command -v git >/dev/null 2>&1; then
  echo "[setup-gpg-robust] git detected: $(command -v git)"
  git config --global --get user.name || true
  git config --global --get user.email || true
  git config --global --get user.signingkey || true
else
  echo "[setup-gpg-robust] git is not installed"
fi

if [ "$EXECUTE" -eq 0 ]; then
  echo "[setup-gpg-robust] Dry-run complete. Re-run with --execute to generate/export a key."
  exit 0
fi

command -v gpg >/dev/null 2>&1 || { echo "[setup-gpg-robust] gpg is required" >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo "[setup-gpg-robust] git is required" >&2; exit 1; }

batch_file="$(mktemp)"
trap 'rm -f "$batch_file"' EXIT

cat > "$batch_file" <<EOF
Key-Type: $KEY_TYPE
Key-Length: $KEY_LENGTH
Subkey-Type: $KEY_TYPE
Subkey-Length: $KEY_LENGTH
Name-Real: $REAL_NAME
Name-Comment: $KEY_COMMENT
Name-Email: $EMAIL
Expire-Date: $KEY_EXPIRE
%no-protection
%commit
EOF

echo "[setup-gpg-robust] Generating GPG key"
gpg --batch --generate-key "$batch_file"

KEY_ID="$(gpg --list-secret-keys --keyid-format LONG "$EMAIL" 2>/dev/null | awk '/^sec/{print $2}' | head -1 | cut -d/ -f2)"
[ -n "$KEY_ID" ] || { echo "[setup-gpg-robust] Failed to resolve generated key ID" >&2; exit 1; }

if [ "$CONFIGURE_GIT" -eq 1 ]; then
  echo "[setup-gpg-robust] Configuring global git signing"
  git config --global user.signingkey "$KEY_ID"
  git config --global user.email "$EMAIL"
  git config --global user.name "$REAL_NAME"
  git config --global commit.gpgsign true
fi

gpg --armor --export "$KEY_ID" > "$EXPORT_PATH"
echo "[setup-gpg-robust] Public key exported to $EXPORT_PATH"
echo "[setup-gpg-robust] Generated key ID: $KEY_ID"
