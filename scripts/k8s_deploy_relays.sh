#!/bin/bash
# Aurora CloudBank Symbolic - Kubernetes Relay Deployment Script
# Chain Notation: #K8S//DEPLOY//RELAYS//
# DLP Tag: k8s_deploy_relays_v1
#
# This script deploys Aurora relay pods to a Kubernetes cluster.
# It handles namespace creation, RBAC setup, and relay pod deployment.

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/k8s"
NAMESPACE="${AURORA_NAMESPACE:-aurora-cloudbank}"
REGISTRY="${CONTAINER_REGISTRY:-ghcr.io/auo959}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
DRY_RUN="${DRY_RUN:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Check your kubeconfig."
        exit 1
    fi
    
    # Check if required manifest files exist
    local required_files=(
        "$K8S_DIR/aurora-namespace-rbac.yaml"
        "$K8S_DIR/aurora-configmap-secrets.yaml"
        "$K8S_DIR/aurora-gui-cloudhub-deployment.yaml"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required manifest file not found: $file"
            exit 1
        fi
    done
    
    log_success "Prerequisites check passed"
}

# Create namespace and RBAC
setup_namespace() {
    log_info "Setting up namespace and RBAC..."
    
    local kubectl_cmd="kubectl apply -f $K8S_DIR/aurora-namespace-rbac.yaml"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would execute: $kubectl_cmd"
        kubectl apply -f "$K8S_DIR/aurora-namespace-rbac.yaml" --dry-run=client -o yaml | head -50
    else
        $kubectl_cmd
    fi
    
    log_success "Namespace and RBAC configured"
}

# Deploy ConfigMaps and Secrets
deploy_config() {
    log_info "Deploying ConfigMaps and Secrets..."
    
    local kubectl_cmd="kubectl apply -f $K8S_DIR/aurora-configmap-secrets.yaml"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would execute: $kubectl_cmd"
    else
        $kubectl_cmd
    fi
    
    log_success "ConfigMaps and Secrets deployed"
}

# Deploy relay pods (main deployment)
deploy_relays() {
    log_info "Deploying Aurora relay pods..."
    log_info "Using image: ${REGISTRY}/aurora-cloudbank-symbolic:${IMAGE_TAG}"
    
    # Update image in deployment manifest (temporary copy)
    local temp_manifest="/tmp/aurora-gui-cloudhub-deployment-updated.yaml"
    sed "s|aurora-cloudbank-symbolic:latest|${REGISTRY}/aurora-cloudbank-symbolic:${IMAGE_TAG}|g" \
        "$K8S_DIR/aurora-gui-cloudhub-deployment.yaml" > "$temp_manifest"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would deploy with updated manifest"
        kubectl apply -f "$temp_manifest" --dry-run=client -o yaml | head -100
    else
        kubectl apply -f "$temp_manifest"
        
        # Wait for rollout
        log_info "Waiting for deployment rollout..."
        if kubectl rollout status deployment/aurora-gui-cloudhub -n "$NAMESPACE" --timeout=300s; then
            log_success "Relay deployment completed successfully"
        else
            log_error "Deployment rollout failed"
            exit 1
        fi
    fi
    
    # Clean up temp file
    rm -f "$temp_manifest"
}

# Verify relay pods are healthy
verify_relays() {
    log_info "Verifying relay pods..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would verify pods in namespace: $NAMESPACE"
        return 0
    fi
    
    # Get pod status
    local pods
    pods=$(kubectl get pods -n "$NAMESPACE" -l app=aurora-gui-cloudhub -o jsonpath='{.items[*].status.phase}')
    
    if [[ -z "$pods" ]]; then
        log_error "No relay pods found"
        exit 1
    fi
    
    # Check if all pods are running
    local all_running=true
    for status in $pods; do
        if [[ "$status" != "Running" ]]; then
            all_running=false
            break
        fi
    done
    
    if [[ "$all_running" == "true" ]]; then
        log_success "All relay pods are running"
    else
        log_warn "Some pods are not in Running state"
        kubectl get pods -n "$NAMESPACE" -l app=aurora-gui-cloudhub
    fi
}

# Output relay logs for verification
show_relay_logs() {
    log_info "Fetching relay logs for verification..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would fetch logs from namespace: $NAMESPACE"
        return 0
    fi
    
    # Get logs from all relay pods (last 50 lines)
    echo ""
    echo "=== Relay Pod Logs ==="
    kubectl logs -n "$NAMESPACE" -l app=aurora-gui-cloudhub --tail=50 --all-containers=true 2>/dev/null || {
        log_warn "Could not fetch logs (pods may not be ready yet)"
    }
    echo "======================"
    echo ""
    
    # Check for specific initialization markers
    log_info "Checking for initialization markers..."
    
    local logs
    logs=$(kubectl logs -n "$NAMESPACE" -l app=aurora-gui-cloudhub --all-containers=true 2>/dev/null || echo "")
    
    # Check for ZIPWIZ handshake
    if echo "$logs" | grep -qi "zipwiz\|handshake"; then
        log_success "ZIPWIZ handshake detected in logs"
    else
        log_warn "No ZIPWIZ handshake detected (may not be initialized yet)"
    fi
    
    # Check for anchor sync
    if echo "$logs" | grep -qi "anchor.*sync\|sync.*anchor"; then
        log_success "Anchor sync detected in logs"
    else
        log_warn "No anchor sync detected (may not be initialized yet)"
    fi
    
    # Check for drift status
    if echo "$logs" | grep -qi "drift.*status\|zero.*drift"; then
        log_success "Drift status detected in logs"
    else
        log_warn "No drift status detected (may not be initialized yet)"
    fi
}

# Print deployment summary
print_summary() {
    echo ""
    echo "========================================"
    echo "    Aurora Relay Deployment Summary"
    echo "========================================"
    echo "Namespace: $NAMESPACE"
    echo "Image: ${REGISTRY}/aurora-cloudbank-symbolic:${IMAGE_TAG}"
    echo "Dry Run: $DRY_RUN"
    echo ""
    
    if [[ "$DRY_RUN" != "true" ]]; then
        echo "Pod Status:"
        kubectl get pods -n "$NAMESPACE" -l app=aurora-gui-cloudhub -o wide 2>/dev/null || echo "Unable to get pod status"
        echo ""
        echo "Services:"
        kubectl get svc -n "$NAMESPACE" 2>/dev/null || echo "Unable to get services"
    fi
    
    echo "========================================"
}

# Main execution
main() {
    log_info "Aurora CloudBank - Relay Deployment Script"
    log_info "Chain: #K8S//DEPLOY//RELAYS//"
    echo ""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --dry-run        Run in dry-run mode (no changes)"
                echo "  --namespace NS   Kubernetes namespace (default: aurora-cloudbank)"
                echo "  --registry REG   Container registry (default: ghcr.io/auo959)"
                echo "  --tag TAG        Image tag (default: latest)"
                echo "  -h, --help       Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute deployment steps
    check_prerequisites
    setup_namespace
    deploy_config
    deploy_relays
    verify_relays
    show_relay_logs
    print_summary
    
    log_success "Relay deployment completed!"
}

main "$@"
