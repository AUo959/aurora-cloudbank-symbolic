#!/bin/bash
# Commit CI/CD improvements and fixes
# This script adds and commits all the CI/CD related fixes

set -e

echo "🚀 Committing CI/CD Improvements"
echo "================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}📋 $1${NC}"
}

# Stage all CI/CD related files
print_info "Staging CI/CD related files..."

# Add workflow files
git add .github/workflows/codeql.yml
git add .github/workflows/enhanced-ci.yml
git add .github/workflows/ci.yml
git add .github/workflows/python-ci.yml

# Add configuration files
git add .github/actions-config.yml
git add devcontainer.json

# Add scripts
git add scripts/ci-maintenance.sh
git add scripts/validate-cicd.sh

# Add any other CI/CD related files
git add devcontainer_resolution_summary.py
git add README.md

print_status "All CI/CD files staged successfully"

# Create commit message
COMMIT_MSG="🔧 Fix CI/CD pipeline issues and improve reliability

- Fix CodeQL proxy.log warnings by creating temp directory proactively
- Enhance CodeQL workflow with better error handling and cleanup
- Add comprehensive CI/CD validation script
- Improve existing CI workflows with better error handling
- Fix devcontainer.json JSON validation issues
- Add GitHub Actions configuration for warning suppression
- Update README with recent DevContainer and CI/CD improvements
- Add enhanced CI pipeline with Aurora-specific checks

Fixes:
- Missing proxy.log file warnings in CodeQL analysis
- Invalid JSON in devcontainer.json
- Improved error handling in CI workflows
- Better artifact management and cleanup

CI/CD Pipeline Status:
- ✅ CodeQL Analysis: Enhanced with better cleanup
- ✅ Node.js CI: Improved conditional execution
- ✅ Python CI: Enhanced security scanning
- ✅ DevContainer: Fixed JSON validation
- ✅ Enhanced CI: Aurora-specific checks added"

# Commit the changes
print_info "Committing changes..."
git commit -m "$COMMIT_MSG"

print_status "CI/CD improvements committed successfully!"

# Show commit summary
print_info "Commit summary:"
git log --oneline -1

print_info "Files changed in this commit:"
git diff --name-only HEAD~1

echo ""
echo "🎉 CI/CD Pipeline Improvements Complete!"
echo "========================================"
echo "Next steps:"
echo "1. Push changes to remote repository"
echo "2. Monitor GitHub Actions for improved reliability"
echo "3. Verify CodeQL warnings are resolved"
echo ""
echo "To push changes, run: git push origin main"
