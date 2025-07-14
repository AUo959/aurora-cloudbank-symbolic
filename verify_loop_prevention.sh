#!/bin/bash

##############################################################################
# Aurora CloudBank - Loop Prevention Verification Script
# 
# Verifies that all loop prevention mechanisms are in place and working
##############################################################################

echo "🔍 Aurora CloudBank - Loop Prevention Verification"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ️${NC} $1"
}

CHECKS_PASSED=0
CHECKS_TOTAL=0

check_file() {
    local file="$1"
    local description="$2"
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    
    if [[ -f "$file" ]]; then
        print_success "$description: Present"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        print_error "$description: Missing"
        return 1
    fi
}

check_config_value() {
    local file="$1"
    local key="$2"
    local expected="$3"
    local description="$4"
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    
    if [[ -f "$file" ]]; then
        if grep -q "\"$key\":[[:space:]]*$expected" "$file"; then
            print_success "$description: Correct ($expected)"
            CHECKS_PASSED=$((CHECKS_PASSED + 1))
            return 0
        else
            print_error "$description: Incorrect or missing"
            return 1
        fi
    else
        print_error "$description: Config file missing"
        return 1
    fi
}

print_status "Checking Aurora Smart Sync loop prevention mechanisms..."
echo ""

# Check 1: Sync Override Configuration
print_info "🔒 Checking Smart Sync Override Configuration"
check_file ".aurora_sync_override.json" "Smart Sync Override Config"
check_config_value ".aurora_sync_override.json" "sync_enabled" "false" "Sync Disabled"
check_config_value ".aurora_sync_override.json" "auto_commit_disabled" "true" "Auto-commit Disabled"
check_config_value ".aurora_sync_override.json" "validation_cycle_prevention" "true" "Validation Cycle Prevention"
echo ""

# Check 2: Validation Configuration
print_info "🧠 Checking Validation Manager Configuration"
check_file ".aurora_validation_config.json" "Validation Manager Config"
check_config_value ".aurora_validation_config.json" "strategy" "\"memory_only\"" "Memory-only Strategy"
check_config_value ".aurora_validation_config.json" "exclude_from_commit" "true" "Exclude from Commit"
check_config_value ".aurora_validation_config.json" "memory_seal" "true" "Memory Seal Active"
echo ""

# Check 3: Symbolic Anchor Sealing
print_info "🔮 Checking Symbolic Anchor Sealing"
check_file ".aurora_symbolic_seal" "Symbolic Anchor Seal"
if [[ -f ".aurora_symbolic_seal" ]]; then
    CHECKS_TOTAL=$((CHECKS_TOTAL + 2))
    if grep -q "T1_ANCHOR_SEALED" ".aurora_symbolic_seal"; then
        print_success "T1 Anchor: Sealed"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        print_error "T1 Anchor: Not sealed"
    fi
    
    if grep -q "MEMORY_SEAL_ACTIVE: TRUE" ".aurora_symbolic_seal"; then
        print_success "Memory Seal: Active"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        print_error "Memory Seal: Inactive"
    fi
fi
echo ""

# Check 4: Exports Manifest and Reliquary Index
print_info "📊 Checking Structured Exports and Reliquary"
check_file ".aurora_exports_manifest.yml" "Exports Manifest"
check_file ".aurora_reliquary_index.md" "Reliquary Index"
echo ""

# Check 5: GitIgnore Protection
print_info "🛡️ Checking GitIgnore Protection"
CHECKS_TOTAL=$((CHECKS_TOTAL + 3))
if grep -q ".aurora_sync_override.json" .gitignore; then
    print_success "Sync Override Config: Protected in .gitignore"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    print_error "Sync Override Config: Not protected in .gitignore"
fi

if grep -q ".aurora_validation_config.json" .gitignore; then
    print_success "Validation Config: Protected in .gitignore"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    print_error "Validation Config: Not protected in .gitignore"
fi

if grep -q ".aurora_symbolic_seal" .gitignore; then
    print_success "Symbolic Seal: Protected in .gitignore"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    print_error "Symbolic Seal: Not protected in .gitignore"
fi
echo ""

# Check 6: Running Processes
print_info "🔍 Checking for Running Aurora Processes"
CHECKS_TOTAL=$((CHECKS_TOTAL + 2))
AURORA_SYNC_PROCESSES=$(pgrep -f "aurora.*sync" | wc -l)
AURORA_CLEANUP_PROCESSES=$(pgrep -f "aurora.*cleanup" | wc -l)

if [[ $AURORA_SYNC_PROCESSES -eq 0 ]]; then
    print_success "Aurora Sync Processes: None running"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    print_warning "Aurora Sync Processes: $AURORA_SYNC_PROCESSES running"
fi

if [[ $AURORA_CLEANUP_PROCESSES -eq 0 ]]; then
    print_success "Aurora Cleanup Processes: None running"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    print_warning "Aurora Cleanup Processes: $AURORA_CLEANUP_PROCESSES running"
fi
echo ""

# Check 7: Enhanced Cleanup Script Protection
print_info "🧹 Checking Enhanced Cleanup Script Protection"
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if grep -q "aurora_sync_override.json" "scripts/aurora_enhanced_cleanup_command.sh"; then
    print_success "Enhanced Cleanup Script: Has override protection"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    print_error "Enhanced Cleanup Script: Missing override protection"
fi
echo ""

# Summary
echo "========================================"
echo -e "${CYAN}📊 VERIFICATION SUMMARY${NC}"
echo "========================================"
echo -e "Checks passed: ${GREEN}$CHECKS_PASSED${NC} / ${BLUE}$CHECKS_TOTAL${NC}"

PERCENTAGE=$((CHECKS_PASSED * 100 / CHECKS_TOTAL))

if [[ $CHECKS_PASSED -eq $CHECKS_TOTAL ]]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED - Loop prevention fully operational!${NC}"
    echo -e "${CYAN}🛡️ Aurora Smart Sync loop prevention mechanisms are active${NC}"
    echo -e "${PURPLE}🔒 Repository is protected against validation cycles${NC}"
    EXIT_CODE=0
elif [[ $PERCENTAGE -ge 80 ]]; then
    echo -e "${YELLOW}⚠️ MOSTLY PROTECTED - $PERCENTAGE% of checks passed${NC}"
    echo -e "${CYAN}🔧 Some optional protections missing but core prevention active${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ INSUFFICIENT PROTECTION - Only $PERCENTAGE% of checks passed${NC}"
    echo -e "${YELLOW}⚠️ Manual intervention required to ensure loop prevention${NC}"
    EXIT_CODE=1
fi

echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
if [[ $CHECKS_PASSED -eq $CHECKS_TOTAL ]]; then
    echo -e "  ${GREEN}✓${NC} Loop prevention is fully operational"
    echo -e "  ${GREEN}✓${NC} Safe to continue normal development"
    echo -e "  ${CYAN}ℹ️${NC} To re-enable Smart Sync: Remove .aurora_sync_override.json"
else
    echo -e "  ${RED}!${NC} Fix missing configurations before continuing"
    echo -e "  ${YELLOW}!${NC} Run this script again after fixes"
    echo -e "  ${CYAN}ℹ️${NC} Consult .aurora_reliquary_index.md for recovery procedures"
fi

exit $EXIT_CODE