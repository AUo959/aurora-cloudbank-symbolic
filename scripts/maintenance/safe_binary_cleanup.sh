#!/bin/bash
# Aurora CloudBank - Safe Binary File Cleanup Script
# Generated automatically - review before execution

echo "🧹 Aurora CloudBank - Safe Binary File Cleanup"
echo "============================================="
echo "📅 Cleanup Date: $(date)"
echo ""

# Create backup directory
mkdir -p .cleanup_backup

echo "🗑️  Removing large files safely..."

# Remove virtual environment (can be recreated)
if [ -d "./venv_opal2" ]; then
    echo "   Removing venv_opal2/ (81MB)"
    rm -rf ./venv_opal2
    echo "   ✅ venv_opal2 removed"
fi

# Remove large ZIP archive
if [ -f "./SRB_SHADOWFAX_Stillness_v1.0.zip" ]; then
    echo "   Moving large ZIP to backup..."
    mv "./SRB_SHADOWFAX_Stillness_v1.0.zip" .cleanup_backup/
    echo "   ✅ Large ZIP moved to backup"
fi

# Remove large audit report (can be regenerated)
if [ -f "./REPOSITORY_AUDIT_REPORT.json" ]; then
    echo "   Removing audit report (can be regenerated)"
    rm "./REPOSITORY_AUDIT_REPORT.json"
    echo "   ✅ Audit report removed"
fi

# Remove large PDF documentation
if [ -f "./docs/operational/guides/Comprehensive Guide to Integrating ChatGPT Workflo.pdf" ]; then
    echo "   Moving large PDF to backup..."
    mv "./docs/operational/guides/Comprehensive Guide to Integrating ChatGPT Workflo.pdf" .cleanup_backup/
    echo "   ✅ Large PDF moved to backup"
fi

echo ""
echo "🎉 Cleanup completed successfully!"
echo "💾 Estimated space saved: ~95MB"
echo "📁 Backups available in .cleanup_backup/"
echo ""
echo "📋 Next steps:"
echo "1. Test that everything still works"
echo "2. Recreate venv_opal2 if needed: python3 -m venv venv_opal2"
echo "3. Commit the cleanup changes"
