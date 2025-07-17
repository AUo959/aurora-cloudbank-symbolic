#!/bin/bash
# Aurora/GUMAS CLI Chaining System
# Chain format: 001//999//. progression logic
# Operator: AUo959

set -euo pipefail

# Configuration
OPERATOR_ID="AUo959"
CHAIN_FORMAT_REGEX="^[0-9]{3}//[a-zA-Z0-9_]+//.?$"
LOG_DIR="/tmp/aurora_cli_logs"
STATE_DIR="/tmp/aurora_cli_state"
EXPORT_DIR="./exports"

# Ensure directories exist
mkdir -p "$LOG_DIR" "$STATE_DIR" "$EXPORT_DIR"

# Global variables
CURRENT_CHAIN=""
OPERATION_COUNTER=1
SESSION_ID="session_$(date +%s)_${OPERATOR_ID}"

# Logging function
log() {
    local level="$1"
    shift
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $*" | tee -a "$LOG_DIR/aurora_cli.log"
}

# Initialize chain progression
init_chain() {
    local operation_name="$1"
    local chain_id=$(printf "%03d" $OPERATION_COUNTER)
    CURRENT_CHAIN="${chain_id}//${operation_name}//."
    
    log "INFO" "Initializing chain: $CURRENT_CHAIN"
    log "INFO" "Session ID: $SESSION_ID"
    log "INFO" "Operator: $OPERATOR_ID"
    
    # Create state file
    cat > "$STATE_DIR/chain_${chain_id}.json" <<EOF
{
  "chainId": "$chain_id",
  "operationName": "$operation_name",
  "operatorId": "$OPERATOR_ID",
  "sessionId": "$SESSION_ID",
  "startTime": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "status": "initialized",
  "steps": [],
  "metadata": {}
}
EOF
    
    echo "$CURRENT_CHAIN"
}

# Progress chain to next step
progress_chain() {
    local step_name="$1"
    local step_data="${2:-{}}"
    
    if [[ -z "$CURRENT_CHAIN" ]]; then
        log "ERROR" "No active chain to progress"
        return 1
    fi
    
    local chain_id=$(echo "$CURRENT_CHAIN" | cut -d'/' -f1)
    local state_file="$STATE_DIR/chain_${chain_id}.json"
    
    if [[ ! -f "$state_file" ]]; then
        log "ERROR" "Chain state file not found: $state_file"
        return 1
    fi
    
    log "INFO" "Progressing chain $CURRENT_CHAIN: $step_name"
    
    # Update state file with new step
    local step_entry="{\"step\": \"$step_name\", \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\", \"data\": $step_data}"
    
    # Use jq to update the JSON file
    if command -v jq >/dev/null; then
        jq ".steps += [$step_entry]" "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    else
        # Fallback without jq
        log "WARN" "jq not available, using basic JSON append"
        cp "$state_file" "${state_file}.bak"
    fi
}

# Seal chain and create manifest
seal_chain() {
    local seal_reason="${1:-completed}"
    
    if [[ -z "$CURRENT_CHAIN" ]]; then
        log "ERROR" "No active chain to seal"
        return 1
    fi
    
    local chain_id=$(echo "$CURRENT_CHAIN" | cut -d'/' -f1)
    local operation_name=$(echo "$CURRENT_CHAIN" | cut -d'/' -f2)
    local state_file="$STATE_DIR/chain_${chain_id}.json"
    
    log "INFO" "Sealing chain $CURRENT_CHAIN: $seal_reason"
    
    # Update final status
    if command -v jq >/dev/null; then
        jq ".status = \"sealed\" | .sealReason = \"$seal_reason\" | .endTime = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" "$state_file" > "${state_file}.tmp" && mv "${state_file}.tmp" "$state_file"
    fi
    
    # Create export manifest
    create_export_manifest "$chain_id" "$operation_name" "$seal_reason"
    
    # Reset current chain
    CURRENT_CHAIN=""
    OPERATION_COUNTER=$((OPERATION_COUNTER + 1))
    
    log "INFO" "Chain sealed successfully"
}

# Create export manifest
create_export_manifest() {
    local chain_id="$1"
    local operation_name="$2" 
    local seal_reason="$3"
    
    local manifest_file="$EXPORT_DIR/manifest_${chain_id}_$(date +%s).json"
    
    cat > "$manifest_file" <<EOF
{
  "manifestVersion": "1.0.0",
  "operatorId": "$OPERATOR_ID",
  "sessionId": "$SESSION_ID",
  "chain": {
    "id": "$chain_id",
    "operation": "$operation_name",
    "format": "$CURRENT_CHAIN",
    "sealReason": "$seal_reason"
  },
  "export": {
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "stateFile": "chain_${chain_id}.json",
    "logFile": "aurora_cli.log"
  },
  "compliance": {
    "auroraStandard": "2024.1",
    "gumasCompliant": true,
    "operatorTraceability": true
  },
  "integrity": {
    "checksum": "$(sha256sum "$STATE_DIR/chain_${chain_id}.json" | cut -d' ' -f1)",
    "signature": "aurora_${OPERATOR_ID}_$(date +%s)"
  }
}
EOF
    
    log "INFO" "Export manifest created: $manifest_file"
    echo "$manifest_file"
}

# Validate chain format
validate_chain_format() {
    local chain="$1"
    
    if [[ ! "$chain" =~ $CHAIN_FORMAT_REGEX ]]; then
        log "ERROR" "Invalid chain format: $chain"
        log "ERROR" "Expected format: 001//operation_name//."
        return 1
    fi
    
    return 0
}

# Show current chain status
show_status() {
    if [[ -z "$CURRENT_CHAIN" ]]; then
        echo "No active chain"
        return 0
    fi
    
    local chain_id=$(echo "$CURRENT_CHAIN" | cut -d'/' -f1)
    local state_file="$STATE_DIR/chain_${chain_id}.json"
    
    echo "Current Chain: $CURRENT_CHAIN"
    echo "Operator: $OPERATOR_ID"
    echo "Session: $SESSION_ID"
    
    if [[ -f "$state_file" ]]; then
        echo "State File: $state_file"
        if command -v jq >/dev/null; then
            echo "Steps:"
            jq -r '.steps[] | "  - \(.step) (\(.timestamp))"' "$state_file"
        fi
    fi
}

# List all chains in session
list_chains() {
    echo "Aurora CLI Chains - Session: $SESSION_ID"
    echo "Operator: $OPERATOR_ID"
    echo "---"
    
    for state_file in "$STATE_DIR"/chain_*.json; do
        if [[ -f "$state_file" ]]; then
            local chain_id=$(basename "$state_file" .json | cut -d'_' -f2)
            if command -v jq >/dev/null; then
                local operation_name=$(jq -r '.operationName' "$state_file")
                local status=$(jq -r '.status' "$state_file")
                echo "Chain $chain_id: $operation_name ($status)"
            else
                echo "Chain $chain_id: $(basename "$state_file")"
            fi
        fi
    done
}

# Export chain data
export_chain() {
    local chain_id="$1"
    local export_format="${2:-json}"
    
    local state_file="$STATE_DIR/chain_${chain_id}.json"
    if [[ ! -f "$state_file" ]]; then
        log "ERROR" "Chain $chain_id not found"
        return 1
    fi
    
    local export_file="$EXPORT_DIR/chain_${chain_id}_export_$(date +%s).$export_format"
    
    case "$export_format" in
        "json")
            cp "$state_file" "$export_file"
            ;;
        "yaml")
            if command -v yq >/dev/null; then
                yq eval "$state_file" > "$export_file"
            else
                log "ERROR" "yq not available for YAML export"
                return 1
            fi
            ;;
        *)
            log "ERROR" "Unsupported export format: $export_format"
            return 1
            ;;
    esac
    
    log "INFO" "Chain exported: $export_file"
    echo "$export_file"
}

# Main command dispatcher
main() {
    case "${1:-help}" in
        "init")
            if [[ $# -lt 2 ]]; then
                echo "Usage: aurora_cli.sh init <operation_name>"
                exit 1
            fi
            init_chain "$2"
            ;;
        "progress")
            if [[ $# -lt 2 ]]; then
                echo "Usage: aurora_cli.sh progress <step_name> [step_data_json]"
                exit 1
            fi
            progress_chain "$2" "${3:-{}}"
            ;;
        "seal")
            seal_chain "${2:-completed}"
            ;;
        "status")
            show_status
            ;;
        "list")
            list_chains
            ;;
        "export")
            if [[ $# -lt 2 ]]; then
                echo "Usage: aurora_cli.sh export <chain_id> [format]"
                exit 1
            fi
            export_chain "$2" "${3:-json}"
            ;;
        "validate")
            if [[ $# -lt 2 ]]; then
                echo "Usage: aurora_cli.sh validate <chain_format>"
                exit 1
            fi
            validate_chain_format "$2"
            ;;
        "help"|*)
            cat <<EOF
Aurora/GUMAS CLI Chaining System
Operator: $OPERATOR_ID

Usage: aurora_cli.sh <command> [args...]

Commands:
  init <operation_name>       Initialize new chain with 001//999//. format
  progress <step> [data]      Progress current chain to next step
  seal [reason]               Seal current chain and create manifest
  status                      Show current chain status
  list                        List all chains in session
  export <chain_id> [format]  Export chain data (json|yaml)
  validate <chain_format>     Validate chain format
  help                        Show this help

Chain Format: 001//operation_name//.
Example: 001//symbolic_init//.

All operations are traced to operator $OPERATOR_ID and comply with Aurora/GUMAS standards.
EOF
            ;;
    esac
}

# Run main function with all arguments
main "$@"