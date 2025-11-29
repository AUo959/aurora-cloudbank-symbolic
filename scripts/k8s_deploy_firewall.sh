#!/bin/bash
# Aurora CloudBank Symbolic - Kubernetes Firewall/Network Policy Deployment Script
# Chain Notation: #K8S//DEPLOY//FIREWALL//
# DLP Tag: k8s_deploy_firewall_v1
#
# This script deploys network policies, security configurations, and firewall rules
# for the Aurora CloudBank Kubernetes deployment.

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
        log_warn "Namespace $NAMESPACE does not exist. Creating it..."
        if [[ "$DRY_RUN" != "true" ]]; then
            kubectl create namespace "$NAMESPACE"
        fi
    fi
    
    log_success "Prerequisites check passed"
}

# Deploy network policies from namespace-rbac
deploy_network_policies() {
    log_info "Deploying Network Policies..."
    
    # Network policies are included in aurora-namespace-rbac.yaml
    local kubectl_cmd="kubectl apply -f $K8S_DIR/aurora-namespace-rbac.yaml"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would execute: $kubectl_cmd"
        
        # Show NetworkPolicy resources
        log_info "NetworkPolicy resources that would be deployed:"
        grep -A 50 "kind: NetworkPolicy" "$K8S_DIR/aurora-namespace-rbac.yaml" | head -60
    else
        $kubectl_cmd
    fi
    
    log_success "Network Policies deployed"
}

# Deploy resource quotas and limit ranges
deploy_resource_controls() {
    log_info "Deploying Resource Quotas and Limit Ranges..."
    
    # Resource quotas and limit ranges are included in aurora-namespace-rbac.yaml
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Resource controls are part of namespace-rbac deployment"
        
        # Show ResourceQuota
        log_info "ResourceQuota configuration:"
        grep -A 30 "kind: ResourceQuota" "$K8S_DIR/aurora-namespace-rbac.yaml" | head -35
        
        # Show LimitRange
        log_info "LimitRange configuration:"
        grep -A 40 "kind: LimitRange" "$K8S_DIR/aurora-namespace-rbac.yaml" | head -45
    else
        log_info "Resource controls deployed with namespace RBAC"
    fi
    
    log_success "Resource controls configured"
}

# Deploy ingress rules (if available)
deploy_ingress() {
    log_info "Deploying Ingress rules..."
    
    local ingress_file="$K8S_DIR/aurora-ingress.yaml"
    
    if [[ -f "$ingress_file" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] Would deploy Ingress from: $ingress_file"
            kubectl apply -f "$ingress_file" --dry-run=client -o yaml | head -50
        else
            # Check if ingress-nginx is available
            if kubectl get ingressclass nginx &> /dev/null; then
                kubectl apply -f "$ingress_file"
                log_success "Ingress deployed"
            else
                log_warn "ingress-nginx IngressClass not found. Skipping Ingress deployment."
                log_info "Install ingress-nginx controller to enable external access"
            fi
        fi
    else
        log_warn "Ingress manifest not found: $ingress_file"
    fi
}

# Verify network policy enforcement
verify_network_policies() {
    log_info "Verifying Network Policies..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would verify network policies in namespace: $NAMESPACE"
        return 0
    fi
    
    # List network policies
    local policies
    policies=$(kubectl get networkpolicies -n "$NAMESPACE" -o name 2>/dev/null)
    
    if [[ -n "$policies" ]]; then
        log_success "Network policies found:"
        echo "$policies"
        
        # Show details of each policy
        for policy in $policies; do
            echo ""
            echo "=== $(echo "$policy" | cut -d'/' -f2) ==="
            kubectl describe "$policy" -n "$NAMESPACE" | grep -A 20 "Spec:" | head -25
        done
    else
        log_warn "No network policies found in namespace $NAMESPACE"
    fi
}

# Verify resource quotas
verify_resource_quotas() {
    log_info "Verifying Resource Quotas..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would verify resource quotas in namespace: $NAMESPACE"
        return 0
    fi
    
    # List resource quotas
    local quotas
    quotas=$(kubectl get resourcequotas -n "$NAMESPACE" -o name 2>/dev/null)
    
    if [[ -n "$quotas" ]]; then
        log_success "Resource quotas found:"
        kubectl get resourcequotas -n "$NAMESPACE" -o wide
    else
        log_warn "No resource quotas found in namespace $NAMESPACE"
    fi
}

# Verify limit ranges
verify_limit_ranges() {
    log_info "Verifying Limit Ranges..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would verify limit ranges in namespace: $NAMESPACE"
        return 0
    fi
    
    # List limit ranges
    local limits
    limits=$(kubectl get limitranges -n "$NAMESPACE" -o name 2>/dev/null)
    
    if [[ -n "$limits" ]]; then
        log_success "Limit ranges found:"
        kubectl describe limitranges -n "$NAMESPACE" | head -50
    else
        log_warn "No limit ranges found in namespace $NAMESPACE"
    fi
}

# Check pod security standards compliance
check_pod_security() {
    log_info "Checking Pod Security Standards compliance..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would check pod security in namespace: $NAMESPACE"
        return 0
    fi
    
    # Check namespace labels for Pod Security Standards
    local pss_labels
    pss_labels=$(kubectl get namespace "$NAMESPACE" -o jsonpath='{.metadata.labels}' 2>/dev/null)
    
    if echo "$pss_labels" | grep -q "pod-security"; then
        log_success "Pod Security Standards labels found"
    else
        log_warn "No Pod Security Standards labels found on namespace"
        log_info "Consider adding: pod-security.kubernetes.io/enforce: restricted"
    fi
}

# Print deployment summary
print_summary() {
    echo ""
    echo "========================================"
    echo "   Aurora Firewall Deployment Summary"
    echo "========================================"
    echo "Namespace: $NAMESPACE"
    echo "Dry Run: $DRY_RUN"
    echo ""
    
    if [[ "$DRY_RUN" != "true" ]]; then
        echo "Network Policies:"
        kubectl get networkpolicies -n "$NAMESPACE" 2>/dev/null || echo "  None configured"
        echo ""
        echo "Resource Quotas:"
        kubectl get resourcequotas -n "$NAMESPACE" 2>/dev/null || echo "  None configured"
        echo ""
        echo "Limit Ranges:"
        kubectl get limitranges -n "$NAMESPACE" 2>/dev/null || echo "  None configured"
        echo ""
        echo "Ingress:"
        kubectl get ingress -n "$NAMESPACE" 2>/dev/null || echo "  None configured"
    fi
    
    echo "========================================"
}

# Main execution
main() {
    log_info "Aurora CloudBank - Firewall Deployment Script"
    log_info "Chain: #K8S//DEPLOY//FIREWALL//"
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
    deploy_network_policies
    deploy_resource_controls
    deploy_ingress
    
    # Verification steps
    verify_network_policies
    verify_resource_quotas
    verify_limit_ranges
    check_pod_security
    
    print_summary
    
    log_success "Firewall deployment completed!"
}

main "$@"
