#!/bin/bash
# Infinite Recursion Module Helper Script
# Anchor: T9-HELPER-INFINITE-2025

set -euo pipefail

print_header() {
  echo "🌀 NEXUS Infinite Recursion Module Helper"
  echo "=========================================="
}

run_demo() {
  local depth=${1:-1000}
  echo "🚀 Running recursion demo (max depth: $depth)..."
  python -m modules.nexus.transcendence.infinite_recursion_enhanced --demo "$depth"
}

check_status() {
  echo "📊 Checking recursion status..."
  python -m modules.nexus.transcendence.infinite_recursion_enhanced --status
}

export_state() {
  local output="recursion_export.json"
  echo "📦 Exporting recursion state to $output..."
  python -m modules.nexus.transcendence.infinite_recursion_enhanced --export > "$output"
  echo "State exported to $output"
}

monitor_checkpoints() {
  local dir=".nexus/recursion/checkpoints"
  echo "🔍 Monitoring recursion checkpoints..."
  if [[ -d "$dir" ]]; then
    ls -lt "$dir" | head -5
  else
    echo "No checkpoints found yet"
  fi
}

check_paradoxes() {
  local dir=".nexus/recursion/paradoxes"
  echo "⚠️ Checking paradox queue..."
  if [[ -d "$dir" ]]; then
    ls -lt "$dir" | head -5
  else
    echo "No paradox directory found"
  fi
}

print_usage() {
  cat <<'USAGE'
Usage: scripts/infinite_recursion_helper.sh {demo [depth]|status|export|checkpoints|paradoxes}

Commands:
  demo [depth]   Run recursion demo (default depth: 1000)
  status         Show current recursion status
  export         Export current recursion state to JSON
  checkpoints    Show recent checkpoint files
  paradoxes      Show current paradox queue files
USAGE
}

main() {
  print_header
  local command=${1:-help}
  shift || true

  case "$command" in
    demo)
      run_demo "$@"
      ;;
    status)
      check_status
      ;;
    export)
      export_state
      ;;
    checkpoints)
      monitor_checkpoints
      ;;
    paradoxes)
      check_paradoxes
      ;;
    help|--help|-h)
      print_usage
      ;;
    *)
      echo "Unknown command: $command"
      print_usage
      return 1
      ;;
  esac
}

main "$@"
