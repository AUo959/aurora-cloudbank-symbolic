#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LABEL="com.aurora.mesh-runtime"
PLIST_DST="$HOME/Library/LaunchAgents/$LABEL.plist"
RUNTIME_SCRIPT="$REPO_ROOT/scripts/mesh-runtime-launch.sh"
LOG_DIR="$REPO_ROOT/runtime/mesh"

if [[ ! -x "$RUNTIME_SCRIPT" ]]; then
  echo "Mesh runtime launch script is missing or not executable: $RUNTIME_SCRIPT" >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

# Generate a LaunchAgent from the actual repo root so it never points at the
# ambiguous root-level Aurora_Sim_Architecture path.
cat >"$PLIST_DST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$RUNTIME_SCRIPT</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$REPO_ROOT</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>ThrottleInterval</key>
  <integer>10</integer>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/mesh_runtime.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/mesh_runtime.stderr.log</string>
</dict>
</plist>
EOF

if command -v plutil >/dev/null 2>&1; then
  plutil -lint "$PLIST_DST" >/dev/null
fi

launchctl bootout "gui/$(id -u)/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/$LABEL"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

echo "Installed $LABEL"
