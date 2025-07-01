#!/bin/bash
# Aurora CloudBank Security Audit Script
# Comprehensive security check for XSS and permission vulnerabilities

set -e

echo "� AURORA CLOUDBANK SECURITY AUDIT - ENHANCED"
echo "=" $(printf "%*s" 50 "" | tr ' ' '=')
echo "📅 Audit Date: $(date)"
echo "🏗️ Project: Aurora CloudBank Symbolic"
echo "🎯 Focus: XSS Prevention & Workflow Permissions"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SECURITY_ISSUES=0
WARNINGS=0

# Function to log security issues
log_security_issue() {
    echo -e "${RED}❌ SECURITY ISSUE: $1${NC}"
    ((SECURITY_ISSUES++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
    ((WARNINGS++))
}

log_passed() {
    echo -e "${GREEN}✅ PASSED: $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  INFO: $1${NC}"
}

# Function to check file existence
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1 exists"
        return 0
    else
        echo "❌ $1 missing"
        return 1
    fi
}

# Function to check directory existence
check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1 directory exists"
        return 0
    else
        echo "❌ $1 directory missing"
        return 1
    fi
}

# Function to check for security patterns in files
check_security_patterns() {
    local file="$1"
    local issues=0

    echo "🔍 Checking $file for security issues..."

    # Check for XSS vulnerabilities
    if grep -q "innerHTML\s*+=" "$file" 2>/dev/null; then
        echo "  ⚠️  Potential XSS: innerHTML concatenation found"
        issues=$((issues + 1))
    fi

    if grep -q "\.innerHTML\s*=" "$file" 2>/dev/null; then
        echo "  ⚠️  Potential XSS: Direct innerHTML assignment found"
        issues=$((issues + 1))
    fi

    # Check for eval usage
    if grep -q "eval\s*(" "$file" 2>/dev/null; then
        echo "  ⚠️  Security risk: eval() usage found"
        issues=$((issues + 1))
    fi

    # Check for unsafe protocol usage
    if grep -q "javascript:" "$file" 2>/dev/null; then
        echo "  ⚠️  Security risk: javascript: protocol found"
        issues=$((issues + 1))
    fi

    if [ $issues -eq 0 ]; then
        echo "  ✅ No security issues found"
    fi

    return $issues
}

echo "📋 1. CHECKING SECURITY INFRASTRUCTURE"
echo "-------------------------------------"

# Check for security files
total_issues=0

check_file "static/js/aurora-security.js" || total_issues=$((total_issues + 1))
check_file ".github/security-config.yml" || total_issues=$((total_issues + 1))
check_file "scripts/security_audit.sh" || total_issues=$((total_issues + 1))

echo ""
echo "📋 2. CHECKING WORKFLOW PERMISSIONS"
echo "-----------------------------------"

# Check workflow files for permissions
for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        if grep -q "permissions:" "$workflow"; then
            echo "✅ $workflow has explicit permissions"
        else
            echo "⚠️  $workflow missing explicit permissions"
            total_issues=$((total_issues + 1))
        fi
    fi
done

echo ""
echo "📋 3. CHECKING HTML FILES FOR XSS PROTECTION"
echo "--------------------------------------------"

# Check HTML files for security measures
for html_file in $(find . -name "*.html" -not -path "./node_modules/*" -not -path "./.git/*"); do
    if [ -f "$html_file" ]; then
        # Check for CSP headers
        if grep -q "Content-Security-Policy" "$html_file"; then
            echo "✅ $html_file has CSP header"
        else
            echo "⚠️  $html_file missing CSP header"
            total_issues=$((total_issues + 1))
        fi

        # Check for security script inclusion
        if grep -q "aurora-security.js" "$html_file"; then
            echo "✅ $html_file includes security script"
        else
            echo "⚠️  $html_file missing security script"
            total_issues=$((total_issues + 1))
        fi

        # Check for security patterns
        check_security_patterns "$html_file"
        security_issues=$?
        total_issues=$((total_issues + security_issues))
    fi
done

echo ""
echo "📋 4. CHECKING JAVASCRIPT FILES"
echo "-------------------------------"

# Check JavaScript files for security issues
for js_file in $(find . -name "*.js" -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./static/js/aurora-security.js"); do
    if [ -f "$js_file" ]; then
        check_security_patterns "$js_file"
        security_issues=$?
        total_issues=$((total_issues + security_issues))
    fi
done

echo ""
echo "📋 5. CHECKING PYTHON FILES FOR SQL INJECTION"
echo "---------------------------------------------"

# Check Python files for potential SQL injection vulnerabilities
for py_file in $(find . -name "*.py" -not -path "./node_modules/*" -not -path "./.git/*"); do
    if [ -f "$py_file" ]; then
        if grep -q "execute.*%" "$py_file" 2>/dev/null; then
            echo "⚠️  $py_file: Potential SQL injection with string formatting"
            total_issues=$((total_issues + 1))
        fi

        if grep -q "query.*format" "$py_file" 2>/dev/null; then
            echo "⚠️  $py_file: Potential SQL injection with .format()"
            total_issues=$((total_issues + 1))
        fi

        if grep -q "execute.*f\"" "$py_file" 2>/dev/null; then
            echo "⚠️  $py_file: Potential SQL injection with f-strings"
            total_issues=$((total_issues + 1))
        fi
    fi
done

echo ""
echo "📋 6. CHECKING PACKAGE SECURITY"
echo "-------------------------------"

# Check for package.json security issues
if [ -f "package.json" ]; then
    echo "✅ package.json found"

    # Check for npm audit if npm is available
    if command -v npm >/dev/null 2>&1; then
        echo "🔍 Running npm audit..."
        if npm audit --audit-level moderate 2>/dev/null; then
            echo "✅ No moderate/high security vulnerabilities found in npm packages"
        else
            echo "⚠️  Security vulnerabilities found in npm packages - run 'npm audit fix'"
            total_issues=$((total_issues + 1))
        fi
    fi
fi

# Check for requirements.txt security
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"

    # Check for known vulnerable packages (basic check)
    if grep -qi "django.*[<>=].*1\." requirements.txt 2>/dev/null; then
        echo "⚠️  Potentially outdated Django version detected"
        total_issues=$((total_issues + 1))
    fi

    if grep -qi "flask.*[<>=].*0\." requirements.txt 2>/dev/null; then
        echo "⚠️  Potentially outdated Flask version detected"
        total_issues=$((total_issues + 1))
    fi
fi

echo ""
echo "📋 7. CHECKING FILE PERMISSIONS"
echo "-------------------------------"

# Check for executable files that shouldn't be
find . -name "*.html" -perm /u+x -not -path "./.git/*" | while read -r file; do
    echo "⚠️  $file is executable (should not be)"
    total_issues=$((total_issues + 1))
done

find . -name "*.css" -perm /u+x -not -path "./.git/*" | while read -r file; do
    echo "⚠️  $file is executable (should not be)"
    total_issues=$((total_issues + 1))
done

find . -name "*.json" -perm /u+x -not -path "./.git/*" | while read -r file; do
    echo "⚠️  $file is executable (should not be)"
    total_issues=$((total_issues + 1))
done

echo ""
echo "📊 SECURITY AUDIT SUMMARY"
echo "========================="

if [ $total_issues -eq 0 ]; then
    echo "🎉 EXCELLENT! No security issues found."
    echo "✅ Aurora CloudBank is secure and ready for deployment."
    exit 0
elif [ $total_issues -lt 5 ]; then
    echo "⚠️  MINOR ISSUES: $total_issues security issues found."
    echo "🔧 Please address these issues before production deployment."
    exit 1
elif [ $total_issues -lt 10 ]; then
    echo "⚠️  MODERATE ISSUES: $total_issues security issues found."
    echo "🔧 Address these issues promptly."
    exit 1
else
    echo "🚨 CRITICAL: $total_issues security issues found."
    echo "🔒 Do not deploy until all issues are resolved."
    exit 2
fi
