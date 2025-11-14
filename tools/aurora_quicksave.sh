#!/bin/bash
# Aurora CloudBank Quicksave - Quick Access Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
QUICKSAVE_TOOL="$SCRIPT_DIR/quicksave.py"

# Quick shorthand commands
case "$1" in
    save|s)
        shift
        python3 "$QUICKSAVE_TOOL" create "$@"
        ;;
    load|l)
        python3 "$QUICKSAVE_TOOL" load
        ;;
    list|ls)
        python3 "$QUICKSAVE_TOOL" list
        ;;
    *)
        echo "Aurora CloudBank Quicksave"
        echo "========================="
        echo ""
        echo "Usage:"
        echo "  ./aurora_quicksave.sh save \"description\" [options]"
        echo "  ./aurora_quicksave.sh load"
        echo "  ./aurora_quicksave.sh list"
        echo ""
        echo "Examples:"
        echo "  ./aurora_quicksave.sh save \"Path C Phase 1 complete\" --focus \"Tests passing\" \"Schema designed\""
        echo "  ./aurora_quicksave.sh load"
        echo ""
        python3 "$QUICKSAVE_TOOL" --help
        ;;
esac
