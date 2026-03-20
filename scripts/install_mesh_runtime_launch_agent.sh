#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LABEL="com.aurora.mesh-runtime"
TEMPLATE_PATH="$REPO_ROOT/deployment/launchd/$LABEL.plist.template"
PLIST_DST="$HOME/Library/LaunchAgents/$LABEL.plist"
LAUNCH_SCRIPT="$REPO_ROOT/scripts/mesh-runtime-launch.sh"
STDOUT_LOG="$REPO_ROOT/runtime/mesh/mesh_runtime.stdout.log"
STDERR_LOG="$REPO_ROOT/runtime/mesh/mesh_runtime.stderr.log"

escape_sed() {
  printf '%s' "$1" | sed 's/[&|]/\\&/g'
}

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "Missing launchd template: $TEMPLATE_PATH" >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$REPO_ROOT/runtime/mesh"
chmod +x "$LAUNCH_SCRIPT"

rendered_plist="$(mktemp)"
sed \
  -e "s|__LAUNCH_SCRIPT__|$(escape_sed "$LAUNCH_SCRIPT")|g" \
  -e "s|__REPO_ROOT__|$(escape_sed "$REPO_ROOT")|g" \
  -e "s|__STDOUT_LOG__|$(escape_sed "$STDOUT_LOG")|g" \
  -e "s|__STDERR_LOG__|$(escape_sed "$STDERR_LOG")|g" \
  "$TEMPLATE_PATH" > "$rendered_plist"

cp "$rendered_plist" "$PLIST_DST"
rm -f "$rendered_plist"

launchctl bootout "gui/$(id -u)/$LABEL" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/$LABEL"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

echo "Installed $LABEL"
