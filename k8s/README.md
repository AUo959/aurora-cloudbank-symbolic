# Aurora CloudBank Symbolic - Kubernetes Manifests

**Chain Notation**: `#K8S//MANIFESTS//README//`  
**SRB**: `K8S_MANIFESTS_v1`  
**Ethics Protocol**: Picard_Delta_3

---

## 📁 Directory Contents

This directory contains production-ready Kubernetes manifests for deploying Aurora CloudBank Symbolic's GUI CloudHub with full MCP (Model Context Protocol) Bridge integration.

### Manifest Files

| File | Description | Resources |
|------|-------------|-----------|
| `aurora-namespace-rbac.yaml` | Namespace, ServiceAccount, RBAC, NetworkPolicy, ResourceQuota | 300+ lines |
| `aurora-configmap-secrets.yaml` | ConfigMaps (MCP, ethics, config), Secrets (API keys) | 250+ lines |
| `aurora-gui-cloudhub-deployment.yaml` | Deployment with init container, security, health checks | 400+ lines |
| `aurora-gui-cloudhub-service.yaml` | LoadBalancer, Headless, Internal services | 150+ lines |
| `aurora-hpa-monitoring.yaml` | HPA, VPA, PodMonitor, ServiceMonitor | 220+ lines |
| `aurora-ingress.yaml` | Ingress with TLS, rate limiting, security headers | 200+ lines |

**Total**: ~1,520 lines of production-ready Kubernetes configuration

### Supporting Files

| File | Description |
|------|-------------|
| `KUBERNETES_DEPLOYMENT_GUIDE.md` | Comprehensive deployment documentation |
| `Dockerfile` | Multi-stage production Docker image |
| `.dockerignore` | Build optimization exclusions |

---

## 🚀 Quick Deploy

```bash
# 1. Build and push Docker image
docker build -t your-registry.io/aurora-cloudbank-symbolic:v1.0.0 -f k8s/Dockerfile .
docker push your-registry.io/aurora-cloudbank-symbolic:v1.0.0

# 2. Update image reference in deployment
sed -i 's|aurora-cloudbank-symbolic:latest|your-registry.io/aurora-cloudbank-symbolic:v1.0.0|' k8s/aurora-gui-cloudhub-deployment.yaml

# 3. Update secrets (CRITICAL!)
# Edit k8s/aurora-configmap-secrets.yaml and replace API key placeholders

# 4. Deploy to Kubernetes
kubectl apply -f k8s/aurora-namespace-rbac.yaml
kubectl apply -f k8s/aurora-configmap-secrets.yaml
kubectl apply -f k8s/aurora-gui-cloudhub-deployment.yaml
kubectl apply -f k8s/aurora-gui-cloudhub-service.yaml
kubectl apply -f k8s/aurora-hpa-monitoring.yaml
kubectl apply -f k8s/aurora-ingress.yaml  # Optional - requires ingress-nginx

# 5. Verify deployment
kubectl get all -n aurora-cloudbank
kubectl get pods -n aurora-cloudbank -w
```

---

## 🔍 Verification

```bash
# Check pod status
kubectl get pods -n aurora-cloudbank

# Check MCP health
kubectl exec -n aurora-cloudbank deploy/aurora-gui-cloudhub -- \
  curl -s http://localhost:8000/mcp_bridge/health | jq .

# View logs
kubectl logs -n aurora-cloudbank -l app=aurora-gui-cloudhub --tail=50 -f

# Test external access
kubectl get svc aurora-gui-cloudhub -n aurora-cloudbank
curl http://<EXTERNAL-IP>/mcp_bridge/health
```

---

## 📊 Architecture

```
Internet → Ingress (TLS) → LoadBalancer Service → Pods (3-20) → MCP Bridge
                                                     ↓
                                            ConfigMaps & Secrets
                                                     ↓
                                            Ethics Protocol Validation
```

**Key Features**:
- ✅ Zero-downtime rolling updates
- ✅ Autoscaling (3-20 pods based on CPU/memory)
- ✅ Self-healing (liveness/readiness probes)
- ✅ Zero-trust networking (NetworkPolicy)
- ✅ Least privilege RBAC
- ✅ TLS/SSL encryption
- ✅ Ethics protocol enforcement (Picard_Delta_3)
- ✅ Symbolic continuity preservation (T1, SRB, chain notation)

---

## 🔧 Configuration

### Required Updates Before Deploy

1. **Docker Image** (`aurora-gui-cloudhub-deployment.yaml`):
   ```yaml
   image: your-registry.io/aurora-cloudbank-symbolic:v1.0.0  # Update this
   ```

2. **API Keys** (`aurora-configmap-secrets.yaml`):
   ```yaml
   anthropic-api-key: <base64-encoded-key>  # Replace placeholder
   openai-api-key: <base64-encoded-key>     # Replace placeholder
   ```

3. **Domain** (`aurora-ingress.yaml`):
   ```yaml
   - host: aurora.example.com  # Replace with your domain
   ```

### Optional Customization

- **Replicas**: Edit `replicas: 3` in deployment
- **Resources**: Adjust `requests` and `limits` in deployment
- **HPA Targets**: Change CPU/memory thresholds in HPA
- **Network Policies**: Modify ingress/egress rules in namespace RBAC
- **TLS**: Configure cert-manager issuer in ingress

---

## 🔒 Security

### Security Best Practices Applied

✅ **Non-root containers**: UID 1000  
✅ **Read-only root filesystem**: Prevents tampering  
✅ **No privilege escalation**: Enforced via securityContext  
✅ **Network segmentation**: Zero-trust NetworkPolicy  
✅ **RBAC least privilege**: Minimal permissions  
✅ **Secret encryption**: Kubernetes secrets at rest  
✅ **Resource limits**: Prevents resource exhaustion  
✅ **PodDisruptionBudget**: Maintains availability during updates

### Security Validation

```bash
# Scan image
trivy image your-registry.io/aurora-cloudbank-symbolic:v1.0.0

# Scan manifests
trivy config k8s/

# Verify RBAC
kubectl auth can-i --list --as=system:serviceaccount:aurora-cloudbank:aurora-gui-cloudhub -n aurora-cloudbank

# Check security contexts
kubectl get deployment aurora-gui-cloudhub -n aurora-cloudbank -o jsonpath='{.spec.template.spec.securityContext}' | jq .
```

---

## 📈 Monitoring

### Prometheus Metrics

Exposed on `/metrics` endpoint:
- `http_requests_total`
- `http_request_duration_seconds`
- `mcp_health_check_success_total`
- `vsa_operations_total`
- `quantum_circuit_executions_total`

### Health Checks

- **Liveness**: `/mcp_bridge/health` (restart if fails)
- **Readiness**: `/mcp_bridge/health` (no traffic if fails)
- **Startup**: 60s grace period

### Logging

```bash
# Stream logs
kubectl logs -n aurora-cloudbank -l app=aurora-gui-cloudhub -f

# Export logs
kubectl logs -n aurora-cloudbank -l app=aurora-gui-cloudhub --since=1h > logs.txt
```

---

## 🔄 Scaling

### Manual Scaling

```bash
# Scale to N replicas
kubectl scale deployment aurora-gui-cloudhub --replicas=5 -n aurora-cloudbank
```

### Autoscaling

**Automatic scaling triggers**:
- CPU utilization > 70%
- Memory utilization > 80%

**Scaling behavior**:
- Scale up: +4 pods or +100% per minute (max)
- Scale down: -1 pod or -10% per 2 minutes (min)
- Stabilization: 60s up, 300s down

```bash
# View HPA status
kubectl get hpa -n aurora-cloudbank

# Describe HPA
kubectl describe hpa aurora-gui-cloudhub-hpa -n aurora-cloudbank
```

---

## 🐛 Troubleshooting

### Common Issues

**Pods not starting**:
```bash
kubectl describe pod <pod-name> -n aurora-cloudbank
kubectl logs <pod-name> -n aurora-cloudbank
```

**Health check failing**:
```bash
kubectl exec -n aurora-cloudbank deploy/aurora-gui-cloudhub -- \
  curl -v http://localhost:8000/mcp_bridge/health
```

**Service not accessible**:
```bash
kubectl get endpoints aurora-gui-cloudhub -n aurora-cloudbank
kubectl describe svc aurora-gui-cloudhub -n aurora-cloudbank
```

**Autoscaling not working**:
```bash
kubectl top pods -n aurora-cloudbank
kubectl describe hpa aurora-gui-cloudhub-hpa -n aurora-cloudbank
```

---

## 📚 Documentation

For detailed instructions, see:
- **[KUBERNETES_DEPLOYMENT_GUIDE.md](./KUBERNETES_DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[../docs/API.md](../docs/API.md)** - API documentation
- **[../ETHICS_PROTOCOL.md](../ETHICS_PROTOCOL.md)** - Ethics protocol details

---

## 🎯 Prerequisites

- Kubernetes cluster v1.24+
- kubectl CLI
- Docker v20.10+
- Container registry access
- (Optional) ingress-nginx controller
- (Optional) cert-manager for TLS
- (Optional) metrics-server for autoscaling
- (Optional) Prometheus for monitoring

---

## 🛡️ Ethics Protocol

All resources comply with **Picard_Delta_3** ethics protocol:

✅ Zero-trust security principles  
✅ Transparency and auditability  
✅ Privacy by design  
✅ Human oversight requirements  
✅ Symbolic continuity preservation

### Validation

```bash
# Verify ethics lock
kubectl exec -n aurora-cloudbank deploy/aurora-gui-cloudhub -- \
  curl -s http://localhost:8000/mcp_bridge/health | \
  jq '.security_layers.ethics_lock'

# Expected: {"status": "ENFORCED", "enforced": true}
```

---

## 📝 Maintenance

### Rolling Updates

```bash
# Update image
kubectl set image deployment/aurora-gui-cloudhub \
  aurora-gui-cloudhub=your-registry.io/aurora-cloudbank-symbolic:v1.1.0 \
  -n aurora-cloudbank

# Watch rollout
kubectl rollout status deployment/aurora-gui-cloudhub -n aurora-cloudbank

# Rollback if needed
kubectl rollout undo deployment/aurora-gui-cloudhub -n aurora-cloudbank
```

### ConfigMap Updates

```bash
# Edit ConfigMap
kubectl edit configmap mcp-bridge-config -n aurora-cloudbank

# Restart pods to pick up changes
kubectl rollout restart deployment/aurora-gui-cloudhub -n aurora-cloudbank
```

### Secret Rotation

```bash
# Create new secret
kubectl create secret generic aurora-api-keys \
  --from-literal=anthropic-api-key='new-key' \
  --from-literal=openai-api-key='new-key' \
  --dry-run=client -o yaml | kubectl apply -f - -n aurora-cloudbank

# Restart pods
kubectl rollout restart deployment/aurora-gui-cloudhub -n aurora-cloudbank
```

---

## 🔗 Related Projects

- [Aurora CloudBank Symbolic](https://github.com/AUo959/aurora-cloudbank-symbolic)
- [MCP Bridge Core](../modules/symbolic_core/)
- [AuMemManager](../modules/aumemmanager/)

---

## 📄 License

See [LICENSE](../LICENSE) in repository root.

---

**Aurora CloudBank Symbolic Kubernetes Manifests**  
**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Chain**: #K8S//MANIFESTS//README//COMPLETE//  
**SRB**: K8S_MANIFESTS_v1  
**Ethics**: Picard_Delta_3 ✅
