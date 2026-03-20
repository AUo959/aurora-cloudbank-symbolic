#!/usr/bin/env bash
set -euo pipefail

LABEL="com.aurora.mesh-runtime"
PLIST_DST="$HOME/Library/LaunchAgents/$LABEL.plist"

launchctl bootout "gui/$(id -u)/$LABEL" >/dev/null 2>&1 || true
rm -f "$PLIST_DST"

echo "Uninstalled $LABEL"
