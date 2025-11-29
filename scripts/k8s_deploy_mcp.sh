#!/bin/bash
# Aurora CloudBank Symbolic - Kubernetes MCP Services Deployment Script
# Chain Notation: #K8S//DEPLOY//MCP//
# DLP Tag: k8s_deploy_mcp_v1
#
# This script deploys MCP (Model Context Protocol) Bridge services,
# including services, HPA, and monitoring components.

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/k8s"
NAMESPACE="${AURORA_NAMESPACE:-aurora-cloudbank}"
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
    
    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace $NAMESPACE does not exist. Run k8s_deploy_relays.sh first."
        exit 1
    fi
    
    # Check if deployment exists
    if ! kubectl get deployment aurora-gui-cloudhub -n "$NAMESPACE" &> /dev/null; then
        log_warn "Deployment aurora-gui-cloudhub not found. Run k8s_deploy_relays.sh first."
    fi
    
    log_success "Prerequisites check passed"
}

# Deploy services
deploy_services() {
    log_info "Deploying MCP Services..."
    
    local service_file="$K8S_DIR/aurora-gui-cloudhub-service.yaml"
    
    if [[ ! -f "$service_file" ]]; then
        log_error "Service manifest not found: $service_file"
        exit 1
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would deploy services from: $service_file"
        kubectl apply -f "$service_file" --dry-run=client -o yaml | head -80
    else
        kubectl apply -f "$service_file"
    fi
    
    log_success "MCP Services deployed"
}

# Deploy HPA and monitoring
deploy_hpa_monitoring() {
    log_info "Deploying HPA and Monitoring components..."
    
    local hpa_file="$K8S_DIR/aurora-hpa-monitoring.yaml"
    
    if [[ ! -f "$hpa_file" ]]; then
        log_warn "HPA/Monitoring manifest not found: $hpa_file"
        log_info "Skipping HPA deployment"
        return 0
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would deploy HPA from: $hpa_file"
        kubectl apply -f "$hpa_file" --dry-run=client -o yaml | head -80
    else
        # Check if metrics-server is available
        if kubectl get apiservice v1beta1.metrics.k8s.io &> /dev/null; then
            kubectl apply -f "$hpa_file"
            log_success "HPA and monitoring deployed"
        else
            log_warn "metrics-server not found. HPA may not function correctly."
            log_info "Install metrics-server to enable autoscaling"
            kubectl apply -f "$hpa_file" 2>/dev/null || log_warn "Some HPA resources may have failed"
        fi
    fi
}

# Verify services
verify_services() {
    log_info "Verifying MCP Services..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would verify services in namespace: $NAMESPACE"
        return 0
    fi
    
    # List services
    echo ""
    echo "=== Services ==="
    kubectl get svc -n "$NAMESPACE" -o wide
    echo ""
    
    # Check service endpoints
    log_info "Checking service endpoints..."
    kubectl get endpoints -n "$NAMESPACE" 2>/dev/null || log_warn "Could not get endpoints"
}

# Verify HPA
verify_hpa() {
    log_info "Verifying HPA configuration..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would verify HPA in namespace: $NAMESPACE"
        return 0
    fi
    
    # List HPAs
    local hpas
    hpas=$(kubectl get hpa -n "$NAMESPACE" -o name 2>/dev/null)
    
    if [[ -n "$hpas" ]]; then
        echo ""
        echo "=== Horizontal Pod Autoscalers ==="
        kubectl get hpa -n "$NAMESPACE" -o wide
        
        # Show HPA details
        for hpa in $hpas; do
            echo ""
            echo "=== $(echo "$hpa" | cut -d'/' -f2) Details ==="
            kubectl describe "$hpa" -n "$NAMESPACE" | tail -20
        done
    else
        log_warn "No HPAs found in namespace $NAMESPACE"
    fi
}

# Test MCP health endpoint
test_mcp_health() {
    log_info "Testing MCP Bridge health endpoint..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would test MCP health endpoint"
        return 0
    fi
    
    # Get a pod name
    local pod_name
    pod_name=$(kubectl get pods -n "$NAMESPACE" -l app=aurora-gui-cloudhub -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [[ -z "$pod_name" ]]; then
        log_warn "No pods found to test health endpoint"
        return 0
    fi
    
    log_info "Testing health endpoint on pod: $pod_name"
    
    # Execute health check inside pod
    local health_result
    health_result=$(kubectl exec -n "$NAMESPACE" "$pod_name" -- curl -s http://localhost:8000/mcp_bridge/health 2>/dev/null || echo '{"error": "health check failed"}')
    
    echo ""
    echo "=== MCP Health Check Result ==="
    echo "$health_result" | python3 -m json.tool 2>/dev/null || echo "$health_result"
    echo "================================"
    echo ""
    
    # Verify security layers
    if echo "$health_result" | grep -q '"ethics_lock".*"ENFORCED"'; then
        log_success "Ethics lock is ENFORCED"
    else
        log_warn "Ethics lock status could not be verified"
    fi
    
    if echo "$health_result" | grep -q '"drift_lock".*"ACTIVE"'; then
        log_success "Drift lock is ACTIVE"
    else
        log_warn "Drift lock status could not be verified"
    fi
}

# Check MCP logs for initialization markers
check_mcp_logs() {
    log_info "Checking MCP logs for initialization markers..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would check MCP logs"
        return 0
    fi
    
    # Get logs from pods
    local logs
    logs=$(kubectl logs -n "$NAMESPACE" -l app=aurora-gui-cloudhub --tail=100 --all-containers=true 2>/dev/null || echo "")
    
    if [[ -z "$logs" ]]; then
        log_warn "No logs available from MCP pods"
        return 0
    fi
    
    echo ""
    echo "=== MCP Initialization Status ==="
    
    # Check for ZIPWIZ handshake
    if echo "$logs" | grep -qi "zipwiz"; then
        log_success "✓ ZIPWIZ component detected"
        echo "$logs" | grep -i "zipwiz" | tail -3
    else
        log_info "○ No ZIPWIZ markers in recent logs"
    fi
    
    # Check for anchor sync
    if echo "$logs" | grep -qi "anchor.*sync\|sync.*anchor\|anchor.*init"; then
        log_success "✓ Anchor synchronization detected"
        echo "$logs" | grep -i "anchor" | tail -3
    else
        log_info "○ No anchor sync markers in recent logs"
    fi
    
    # Check for drift status
    if echo "$logs" | grep -qi "drift.*status\|drift.*zero\|drift.*lock"; then
        log_success "✓ Drift monitoring active"
        echo "$logs" | grep -i "drift" | tail -3
    else
        log_info "○ No drift status markers in recent logs"
    fi
    
    # Check for MCP bridge initialization
    if echo "$logs" | grep -qi "mcp.*bridge\|bridge.*init\|mcp.*ready"; then
        log_success "✓ MCP Bridge initialized"
        echo "$logs" | grep -i "mcp\|bridge" | tail -3
    else
        log_info "○ No MCP bridge markers in recent logs"
    fi
    
    echo "================================="
    echo ""
}

# Print deployment summary
print_summary() {
    echo ""
    echo "========================================"
    echo "    Aurora MCP Deployment Summary"
    echo "========================================"
    echo "Namespace: $NAMESPACE"
    echo "Dry Run: $DRY_RUN"
    echo ""
    
    if [[ "$DRY_RUN" != "true" ]]; then
        echo "Services:"
        kubectl get svc -n "$NAMESPACE" 2>/dev/null | head -10
        echo ""
        echo "HPA:"
        kubectl get hpa -n "$NAMESPACE" 2>/dev/null || echo "  Not configured"
        echo ""
        echo "Pods:"
        kubectl get pods -n "$NAMESPACE" -l app=aurora-gui-cloudhub -o wide 2>/dev/null | head -10
    fi
    
    echo "========================================"
}

# Main execution
main() {
    log_info "Aurora CloudBank - MCP Services Deployment Script"
    log_info "Chain: #K8S//DEPLOY//MCP//"
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
            -h|--help)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --dry-run        Run in dry-run mode (no changes)"
                echo "  --namespace NS   Kubernetes namespace (default: aurora-cloudbank)"
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
    deploy_services
    deploy_hpa_monitoring
    
    # Verification steps
    verify_services
    verify_hpa
    test_mcp_health
    check_mcp_logs
    
    print_summary
    
    log_success "MCP services deployment completed!"
}

main "$@"
