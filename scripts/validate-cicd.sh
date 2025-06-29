#!/bin/bash
# CI/CD Validation Script for Aurora CloudBank
# Ensures all CI/CD configurations are valid and addresses common issues

set -e

echo "🔍 Aurora CI/CD Configuration Validator"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success") echo -e "${GREEN}✅ $message${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "error") echo -e "${RED}❌ $message${NC}" ;;
        *) echo "$message" ;;
    esac
}

# Check GitHub workflows directory
if [ -d ".github/workflows" ]; then
    print_status "success" "GitHub workflows directory found"

    # Count workflow files
    workflow_count=$(find .github/workflows -name "*.yml" -o -name "*.yaml" | wc -l)
    print_status "success" "Found $workflow_count workflow files"

    # Validate each workflow file
    for workflow in .github/workflows/*.yml .github/workflows/*.yaml; do
        if [ -f "$workflow" ]; then
            filename=$(basename "$workflow")
            if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
                print_status "success" "Valid YAML: $filename"
            else
                print_status "error" "Invalid YAML: $filename"
            fi
        fi
    done
else
    print_status "warning" "No GitHub workflows directory found"
fi

# Check for CodeQL configuration
if [ -f ".github/workflows/codeql.yml" ]; then
    print_status "success" "CodeQL workflow found"

    # Check for proxy.log handling
    if grep -q "proxy.log" .github/workflows/codeql.yml; then
        print_status "success" "Proxy.log handling configured"
    else
        print_status "warning" "Proxy.log handling may be missing"
    fi
else
    print_status "warning" "CodeQL workflow not found"
fi

# Check for package.json
if [ -f "package.json" ]; then
    print_status "success" "package.json found"

    # Validate JSON
    if python3 -c "import json; json.load(open('package.json'))" 2>/dev/null; then
        print_status "success" "Valid package.json"
    else
        print_status "error" "Invalid package.json"
    fi

    # Check for scripts
    if python3 -c "import json; scripts = json.load(open('package.json')).get('scripts', {}); exit(0 if scripts else 1)" 2>/dev/null; then
        print_status "success" "npm scripts configured"
    else
        print_status "warning" "No npm scripts found"
    fi
else
    print_status "warning" "No package.json found"
fi

# Check for requirements.txt
if [ -f "requirements.txt" ]; then
    print_status "success" "requirements.txt found"

    # Check if it's not empty
    if [ -s "requirements.txt" ]; then
        print_status "success" "requirements.txt has content"
    else
        print_status "warning" "requirements.txt is empty"
    fi
else
    print_status "warning" "No requirements.txt found"
fi

# Check for symbolic configuration
if [ -f "symbolic_config.yaml" ]; then
    print_status "success" "symbolic_config.yaml found"

    # Validate YAML
    if python3 -c "import yaml; yaml.safe_load(open('symbolic_config.yaml'))" 2>/dev/null; then
        print_status "success" "Valid symbolic_config.yaml"
    else
        print_status "error" "Invalid symbolic_config.yaml"
    fi
else
    print_status "warning" "No symbolic_config.yaml found"
fi

# Check for devcontainer
if [ -f "devcontainer.json" ]; then
    print_status "success" "devcontainer.json found"

    # Validate JSON
    if python3 -c "import json; json.load(open('devcontainer.json'))" 2>/dev/null; then
        print_status "success" "Valid devcontainer.json"
    else
        print_status "error" "Invalid devcontainer.json"
    fi
elif [ -f ".devcontainer/devcontainer.json" ]; then
    print_status "success" "devcontainer.json found in .devcontainer/"

    # Validate JSON
    if python3 -c "import json; json.load(open('.devcontainer/devcontainer.json'))" 2>/dev/null; then
        print_status "success" "Valid devcontainer.json"
    else
        print_status "error" "Invalid devcontainer.json"
    fi
else
    print_status "warning" "No devcontainer.json found"
fi

# Check git status
if git rev-parse --git-dir > /dev/null 2>&1; then
    print_status "success" "Git repository detected"

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_status "warning" "Uncommitted changes detected"
        echo "Uncommitted files:"
        git status --porcelain | head -10
    else
        print_status "success" "Working directory clean"
    fi
else
    print_status "error" "Not a git repository"
fi

# Check for common CI/CD issues
echo ""
echo "🔧 Common Issue Checks"
echo "====================="

# Check for merge conflict markers in tracked files only
if git ls-files | grep -E "\.(py|js|ts|yml|yaml)$" | xargs grep -l "<<<<<<< HEAD\|>>>>>>> \|=======" 2>/dev/null; then
    print_status "error" "Merge conflict markers found in tracked files"
else
    print_status "success" "No merge conflict markers found in tracked files"
fi

# Check for large files that are tracked by git and might cause CI issues
large_files=$(git ls-files | xargs -I {} find {} -type f -size +50M 2>/dev/null | head -5)
if [ -n "$large_files" ]; then
    print_status "warning" "Large tracked files found (>50MB):"
    echo "$large_files"
else
    print_status "success" "No problematically large tracked files found"
fi

# Summary
echo ""
echo "📋 Validation Summary"
echo "==================="
echo "If any errors were found above, please address them before running CI/CD."
echo "Warnings are non-critical but may affect CI/CD performance."
echo ""
print_status "success" "CI/CD validation completed"
