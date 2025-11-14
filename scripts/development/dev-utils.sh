#!/bin/bash
# Aurora Development Utilities

case "$1" in
    "quick-check")
        echo "🚀 Running quick development checks..."
        python3 tools/workflow/aurora_failure_prevention_system.py --check
        ;;
    "pre-deploy")
        echo "🚀 Pre-deployment validation..."
        python3 tools/workflow/aurora_failure_prevention_system.py --check
        if [ $? -eq 0 ]; then
            echo "✅ Ready for deployment"
        else
            echo "❌ Fix issues before deploying"
        fi
        ;;
    "optimize")
        echo "⚡ Running workflow optimization..."
        python3 tools/workflow/aurora_workflow_optimization_manager.py
        ;;
    *)
        echo "Aurora Development Utilities"
        echo "Usage: $0 [quick-check|pre-deploy|optimize]"
        ;;
esac
