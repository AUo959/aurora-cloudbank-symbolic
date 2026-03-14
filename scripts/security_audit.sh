#!/bin/bash
# Aurora CloudBank Security Audit Script
# Comprehensive security check for XSS and permission vulnerabilities

set -uo pipefail

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

find_project_files() {
    local pattern="$1"
    find . \
        \( -type d \( -name ".git" -o -name "node_modules" -o -name ".venv" -o -name "venv" -o -name "__pycache__" -o -name ".pytest_cache" -o -name "build" -o -name "dist" -o -name "coverage" \) -prune \) \
        -o -type f -name "$pattern" -print0
}

# Function to check for security patterns in files
check_security_patterns() {
    local file="$1"
    local issues=0

    echo "🔍 Checking $file for security issues..."

    # Check for XSS vulnerabilities
    if grep -q "innerHTML\s*+=" "$file" 2>/dev/null && ! grep -q "AuroraSecurity\.sanitizeHTML" "$file" 2>/dev/null; then
        echo "  ⚠️  Potential XSS: innerHTML concatenation found (not properly sanitized)"
        issues=$((issues + 1))
    elif grep -q "innerHTML\s*+=" "$file" 2>/dev/null; then
        # Check if all innerHTML += usages are sanitized
        unsanitized_innerHTML=$(grep -n "innerHTML\s*+=" "$file" | grep -v "AuroraSecurity\.sanitizeHTML" | wc -l)
        if [ "$unsanitized_innerHTML" -gt 0 ]; then
            echo "  ⚠️  Potential XSS: $unsanitized_innerHTML unsanitized innerHTML concatenation(s) found"
            issues=$((issues + 1))
        fi
    fi

    if grep -q "\.innerHTML\s*=" "$file" 2>/dev/null; then
        # Check for unsafe innerHTML assignments (excluding empty string assignments and sanitized ones)
        unsanitized_assignments=$(grep -n "\.innerHTML\s*=" "$file" | grep -v "innerHTML\s*=\s*''" | grep -v 'innerHTML\s*=\s*""' | grep -v "AuroraSecurity\.sanitizeHTML" | wc -l)
        if [ "$unsanitized_assignments" -gt 0 ]; then
            echo "  ⚠️  Potential XSS: $unsanitized_assignments unsafe innerHTML assignment(s) found"
            issues=$((issues + 1))
        fi
    fi

    # Check for eval usage
    if grep -q "eval\s*(" "$file" 2>/dev/null; then
        echo "  ⚠️  Security risk: eval() usage found"
        issues=$((issues + 1))
    fi

    # Check for unsafe protocol usage
    protocol_hits=$(grep -n "javascript:" "$file" 2>/dev/null | grep -v "replace(/javascript:" | grep -vcE '^[0-9]+:[[:space:]]*(//|/\*|\*|#)')
    if [ "${protocol_hits:-0}" -gt 0 ]; then
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
while IFS= read -r -d '' html_file; do
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
done < <(find_project_files "*.html")

echo ""
echo "📋 4. CHECKING JAVASCRIPT FILES"
echo "-------------------------------"

# Check JavaScript files for security issues
while IFS= read -r -d '' js_file; do
    if [ -f "$js_file" ]; then
        check_security_patterns "$js_file"
        security_issues=$?
        total_issues=$((total_issues + security_issues))
    fi
done < <(find_project_files "*.js")

echo ""
echo "📋 5. CHECKING PYTHON FILES FOR SQL INJECTION"
echo "---------------------------------------------"

# Check Python files for potential SQL injection vulnerabilities
while IFS= read -r -d '' py_file; do
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
done < <(find_project_files "*.py")

echo ""
echo "📋 6. CHECKING PACKAGE SECURITY"
echo "-------------------------------"

# Check for package.json security issues
if [ -f "package.json" ]; then
    echo "✅ package.json found"

    # Check for npm audit if npm is available
    if command -v npm >/dev/null 2>&1; then
        echo "🔍 Running npm audit..."
        audit_output=$(npm audit --audit-level moderate 2>&1)
        audit_rc=$?
        if [ $audit_rc -eq 0 ]; then
            echo "✅ No moderate/high security vulnerabilities found in npm packages"
        elif printf '%s\n' "$audit_output" | grep -qiE "network|ENOTFOUND|EAI_AGAIN|ECONNRESET|timed out|audit endpoint"; then
            echo "ℹ️  npm audit could not complete in the current environment: network-restricted or audit service unavailable"
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
while IFS= read -r -d '' file; do
    echo "⚠️  $file is executable (should not be)"
    total_issues=$((total_issues + 1))
done < <(find_project_files "*.html" | xargs -0 -I {} sh -c 'if [ -x "$1" ]; then printf "%s\0" "$1"; fi' _ {})

while IFS= read -r -d '' file; do
    echo "⚠️  $file is executable (should not be)"
    total_issues=$((total_issues + 1))
done < <(find_project_files "*.css" | xargs -0 -I {} sh -c 'if [ -x "$1" ]; then printf "%s\0" "$1"; fi' _ {})

while IFS= read -r -d '' file; do
    echo "⚠️  $file is executable (should not be)"
    total_issues=$((total_issues + 1))
done < <(find_project_files "*.json" | xargs -0 -I {} sh -c 'if [ -x "$1" ]; then printf "%s\0" "$1"; fi' _ {})

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
