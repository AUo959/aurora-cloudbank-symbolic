#!/bin/bash

##############################################################################
# Aurora CloudBank - Emergency Loop Prevention Restore
# 
# Quickly restores all loop prevention mechanisms if they are disabled
##############################################################################

echo "🚨 Aurora CloudBank - Emergency Loop Prevention Restore"
echo "======================================================="

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
    echo -e "${BLUE}[RESTORE]${NC} $1"
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

print_action() {
    echo -e "${PURPLE}🚀${NC} $1"
}

print_emergency() {
    echo -e "${RED}🚨${NC} $1"
}

print_emergency "EMERGENCY LOOP PREVENTION ACTIVATION"
echo ""

# Step 1: Stop any running Aurora processes
print_action "Step 1: Stopping any running Aurora processes..."
./stop_aurora.sh 2>/dev/null || echo "stop_aurora.sh not found or failed"

# Kill Aurora sync and cleanup processes
pkill -f "aurora.*sync" 2>/dev/null || echo "No Aurora sync processes running"
pkill -f "aurora.*cleanup" 2>/dev/null || echo "No Aurora cleanup processes running"
pkill -f "cleanup.*aurora" 2>/dev/null || echo "No cleanup processes running"

print_success "Process cleanup complete"

# Step 2: Create/restore sync override configuration
print_action "Step 2: Creating Smart Sync override configuration..."
cat > .aurora_sync_override.json << 'EOF'
{
  "sync_enabled": false,
  "commit_throttle_minutes": 60,
  "validation_cycle_prevention": true,
  "symbolic_anchor_preservation": true,
  "entropy_threshold": 0.1,
  "emergency_mode": true,
  "auto_commit_disabled": true,
  "smart_staging_disabled": true,
  "exclude_patterns": [
    "*.validation",
    ".aurora/*",
    "validation_*",
    "*VALIDATION*.md",
    "*validation*.md",
    ".aurora_validation_config.json",
    ".aurora_sync_override.json"
  ]
}
EOF
print_success "Smart Sync override configuration created"

# Step 3: Create/restore validation configuration
print_action "Step 3: Creating validation manager configuration..."
cat > .aurora_validation_config.json << 'EOF'
{
  "strategy": "memory_only",
  "validation_dir": "/tmp/aurora_validation",
  "exclude_from_commit": true,
  "auto_cleanup": true,
  "memory_seal": true,
  "dlp_tags": ["AURORA_INTERNAL", "VALIDATION_EXEMPT", "ENTROPY_STABLE"],
  "smart_sync_prevention": true,
  "cycle_prevention_active": true
}
EOF
print_success "Validation manager configuration created"

# Step 4: Create/restore symbolic seal
print_action "Step 4: Creating symbolic anchor seal..."
CURRENT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > .aurora_symbolic_seal << EOF
T1_ANCHOR_SEALED_$(date +%Y%m%d_%H%M%S)
REVERT_POINT: $CURRENT_COMMIT
SRB_BASE: codespace-orange-invention-v6ww7ww775w5fw6q
ENTROPY_STATE: CLEAN
DLP_TAG: AURORA_SYMBOLIC_LOCK
MEMORY_SEAL_ACTIVE: TRUE
VALIDATION_LOOP_PREVENTED: TRUE
SMART_SYNC_DISABLED: TRUE
EMERGENCY_RESTORE: TRUE
TIMESTAMP: $TIMESTAMP
EOF
print_success "Symbolic anchor seal created"

# Step 5: Update .gitignore if needed
print_action "Step 5: Updating .gitignore protection..."
if ! grep -q ".aurora_sync_override.json" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Aurora Smart Sync Loop Prevention - Memory Sealed" >> .gitignore
    echo ".aurora_validation_config.json" >> .gitignore
    echo ".aurora_sync_override.json" >> .gitignore
    echo ".aurora_symbolic_seal" >> .gitignore
    echo ".aurora_exports_manifest.yml" >> .gitignore
    echo ".aurora_reliquary_index.md" >> .gitignore
    print_success "Updated .gitignore with protection patterns"
else
    print_status ".gitignore already has protection patterns"
fi

# Step 6: Verify restoration
print_action "Step 6: Verifying loop prevention restoration..."
echo ""

if [[ -f "./verify_loop_prevention.sh" ]]; then
    ./verify_loop_prevention.sh
    VERIFICATION_RESULT=$?
else
    print_warning "verify_loop_prevention.sh not found - running basic checks"
    
    # Basic verification
    BASIC_CHECKS=0
    TOTAL_BASIC=3
    
    if [[ -f ".aurora_sync_override.json" ]]; then
        echo -e "${GREEN}✅${NC} Smart Sync Override: Present"
        BASIC_CHECKS=$((BASIC_CHECKS + 1))
    fi
    
    if [[ -f ".aurora_validation_config.json" ]]; then
        echo -e "${GREEN}✅${NC} Validation Config: Present"
        BASIC_CHECKS=$((BASIC_CHECKS + 1))
    fi
    
    if [[ -f ".aurora_symbolic_seal" ]]; then
        echo -e "${GREEN}✅${NC} Symbolic Seal: Present"
        BASIC_CHECKS=$((BASIC_CHECKS + 1))
    fi
    
    if [[ $BASIC_CHECKS -eq $TOTAL_BASIC ]]; then
        VERIFICATION_RESULT=0
        echo -e "${GREEN}🎉 Basic verification passed${NC}"
    else
        VERIFICATION_RESULT=1
        echo -e "${RED}❌ Basic verification failed${NC}"
    fi
fi

echo ""
print_emergency "EMERGENCY RESTORATION COMPLETE"
echo "================================"

if [[ $VERIFICATION_RESULT -eq 0 ]]; then
    print_success "🛡️ Loop prevention mechanisms restored and verified"
    print_success "🔒 Aurora Smart Sync is disabled and protected"
    print_success "🧠 Memory-only validation active"
    echo ""
    echo -e "${CYAN}📋 Status:${NC}"
    echo -e "  ${GREEN}✓${NC} Emergency loop prevention: ACTIVE"
    echo -e "  ${GREEN}✓${NC} Auto-commit disabled: YES"
    echo -e "  ${GREEN}✓${NC} Validation cycle prevention: YES"
    echo -e "  ${GREEN}✓${NC} Symbolic anchors sealed: YES"
    echo ""
    echo -e "${PURPLE}🔧 To restore normal operation later:${NC}"
    echo -e "  1. Remove .aurora_sync_override.json"
    echo -e "  2. Run verification script to confirm"
    echo -e "  3. Resume normal development"
else
    print_error "⚠️ Emergency restoration completed with issues"
    print_warning "Manual intervention may be required"
    echo -e "${YELLOW}📋 Check configuration files manually${NC}"
fi

echo ""
echo -e "${CYAN}🛡️ Repository protected against Aurora Smart Sync loops${NC}"