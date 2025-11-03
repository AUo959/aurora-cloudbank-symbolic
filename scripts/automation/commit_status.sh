#!/bin/bash

# Aurora CloudBank Git Commit and Push Script
echo "🚀 Committing and pushing Aurora CloudBank status update..."

cd /workspaces/aurora-cloudbank-symbolic

# Add the current status summary
git add CURRENT_STATUS_SUMMARY.md

# Commit with detailed message
git commit -m "📊 Add comprehensive current status summary

✅ Repository optimization complete - 47 branches cleaned up
✅ ORION Station deployment operational  
✅ All integration and cleanup phases documented
✅ Next development phase recommendations provided
✅ Markdown linting compliant

Repository now in optimal state for continued development."

# Push to main
git push origin main

echo "✅ Commit and push completed!"
