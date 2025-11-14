# Kubernetes Secrets Management - Sealed Secrets Implementation Guide

**Version:** 1.0.0  
**Date:** November 11, 2025  
**Officer:** OPS Rodriguez  
**Mission:** HIGH-3 K8s Secrets Encryption

---

## 🎯 Overview

This guide provides step-by-step instructions for implementing encrypted secrets management in Aurora CloudBank using **Bitnami Sealed Secrets**. Sealed Secrets allows you to encrypt Kubernetes secrets and safely store them in git repositories.

### Why Sealed Secrets?

- ✅ **GitOps-Friendly:** Encrypted secrets can be committed to version control
- ✅ **One-Way Encryption:** Only the cluster controller can decrypt
- ✅ **Zero External Dependencies:** Runs entirely in-cluster
- ✅ **Strong Encryption:** Uses AES-256-GCM encryption
- ✅ **Industry Standard:** Widely adopted in production environments

---

## 📋 Prerequisites

**Required Access:**
- Kubernetes cluster admin privileges
- `kubectl` configured and authenticated
- Git repository write access

**Required Tools:**
- `kubectl` v1.20+
- `kubeseal` CLI tool
- `openssl` for key generation

---

## 🚀 Installation Steps

### Step 1: Install Sealed Secrets Controller

The sealed-secrets controller must be installed in your Kubernetes cluster. It runs in the `kube-system` namespace by default.

```bash
# Apply the controller manifest
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Verify the controller is running
kubectl get pods -n kube-system | grep sealed-secrets-controller

# Expected output:
# sealed-secrets-controller-xxxxxxxxx-xxxxx   1/1     Running   0          30s
```

**Verification:**
```bash
# Check controller logs
kubectl logs -n kube-system -l name=sealed-secrets-controller

# Should see: "controller version: v0.24.0"
```

### Step 2: Install kubeseal CLI Tool

The `kubeseal` CLI is used to encrypt secrets on your local machine.

**macOS (Homebrew):**
```bash
brew install kubeseal
```

**Linux:**
```bash
# Download binary
KUBESEAL_VERSION='0.24.0'
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz

# Extract and install
tar xfz kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz
sudo install -m 755 kubeseal /usr/local/bin/kubeseal
```

**Verify Installation:**
```bash
kubeseal --version
# Expected: kubeseal version: v0.24.0
```

---

## 🔒 Sealing Secrets

### Step 3: Create Secret Manifest

First, create a standard Kubernetes Secret manifest (do NOT apply it yet):

```bash
# Create secret from literal values
kubectl create secret generic aurora-api-keys \
  --namespace=aurora-cloudbank \
  --from-literal=anthropic-api-key='your-actual-anthropic-key-here' \
  --from-literal=openai-api-key='your-actual-openai-key-here' \
  --from-literal=csrf-secret-key='your-actual-csrf-secret-here' \
  --from-literal=jwt-secret-key='your-actual-jwt-secret-here' \
  --dry-run=client \
  -o yaml > aurora-secret-plaintext.yaml
```

**⚠️ IMPORTANT:** This file contains plaintext secrets. **Never commit this file to git.**

### Step 4: Seal the Secret

Use `kubeseal` to encrypt the secret:

```bash
# Seal the secret (requires cluster access to fetch public key)
kubeseal --format=yaml \
  --controller-namespace=kube-system \
  --controller-name=sealed-secrets-controller \
  < aurora-secret-plaintext.yaml \
  > k8s/aurora-sealed-secrets.yaml

# Verify sealed secret was created
cat k8s/aurora-sealed-secrets.yaml
```

**Output Structure:**
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: aurora-api-keys
  namespace: aurora-cloudbank
spec:
  encryptedData:
    anthropic-api-key: AgA7xV...  # Long encrypted string
    openai-api-key: AgB2kP...
    csrf-secret-key: AgC9mL...
    jwt-secret-key: AgD4nQ...
  template:
    metadata:
      name: aurora-api-keys
      namespace: aurora-cloudbank
    type: Opaque
```

### Step 5: Delete Plaintext Secret

**CRITICAL:** Securely delete the plaintext secret file:

```bash
# Overwrite with random data before deletion
shred -vfz -n 3 aurora-secret-plaintext.yaml

# Or use secure deletion
rm -P aurora-secret-plaintext.yaml  # macOS
# OR
srm aurora-secret-plaintext.yaml     # Linux with secure-delete package
```

---

## 📦 Deployment

### Step 6: Deploy Sealed Secret

Apply the sealed secret to your cluster:

```bash
# Apply sealed secret
kubectl apply -f k8s/aurora-sealed-secrets.yaml

# Verify SealedSecret resource was created
kubectl get sealedsecrets -n aurora-cloudbank

# Wait for controller to decrypt (usually instant)
sleep 5

# Verify regular Secret was auto-created by controller
kubectl get secrets -n aurora-cloudbank | grep aurora-api-keys

# Should see:
# aurora-api-keys   Opaque   4      5s
```

### Step 7: Verify Secret Access

Test that the decrypted secret is accessible:

```bash
# Describe the secret (values are opaque)
kubectl describe secret aurora-api-keys -n aurora-cloudbank

# Decode and view one key (for testing only)
kubectl get secret aurora-api-keys -n aurora-cloudbank -o jsonpath='{.data.anthropic-api-key}' | base64 --decode
```

---

## 🔄 Secret Rotation Procedure

### Rotating Individual Keys

1. **Generate New Secret Value:**
```bash
# Example: Generate new CSRF secret
NEW_CSRF=$(openssl rand -hex 32)
echo $NEW_CSRF
```

2. **Create Updated Secret Manifest:**
```bash
kubectl create secret generic aurora-api-keys \
  --namespace=aurora-cloudbank \
  --from-literal=anthropic-api-key='existing-key' \
  --from-literal=openai-api-key='existing-key' \
  --from-literal=csrf-secret-key="$NEW_CSRF" \
  --from-literal=jwt-secret-key='existing-key' \
  --dry-run=client \
  -o yaml > aurora-secret-plaintext.yaml
```

3. **Re-seal:**
```bash
kubeseal --format=yaml < aurora-secret-plaintext.yaml > k8s/aurora-sealed-secrets.yaml
```

4. **Apply and Restart Pods:**
```bash
kubectl apply -f k8s/aurora-sealed-secrets.yaml

# Restart pods to pick up new secret
kubectl rollout restart deployment/aurora-gui-cloudhub -n aurora-cloudbank
```

5. **Clean Up:**
```bash
shred -vfz -n 3 aurora-secret-plaintext.yaml
```

---

## 🛡️ Security Best Practices

### 1. Never Commit Plaintext Secrets

Add to `.gitignore`:
```
# Plaintext secrets (NEVER COMMIT)
*-secret-plaintext.yaml
*-plaintext.yaml
aurora-secret-*.yaml
!*-sealed-*.yaml  # Allow sealed secrets
```

### 2. Backup Sealed Secrets Controller Keys

The controller's private key should be backed up securely:

```bash
# Export controller keys (requires admin access)
kubectl get secret -n kube-system sealed-secrets-key -o yaml > sealed-secrets-key-backup.yaml

# Store in secure location (e.g., password manager, vault)
# NEVER commit this to git
```

### 3. Rotate Secrets Regularly

- **Critical Secrets:** Every 30 days
- **API Keys:** Every 90 days
- **After Team Changes:** Immediately

### 4. Audit Secret Access

Monitor who accesses secrets:

```bash
# Enable audit logging in Kubernetes
# Watch for secret access events
kubectl logs -n kube-system -l name=sealed-secrets-controller --tail=100 | grep "Unsealed secret"
```

### 5. Use Separate Sealed Secrets Per Environment

Create different sealed secrets for dev/staging/prod:
- `aurora-sealed-secrets-dev.yaml`
- `aurora-sealed-secrets-staging.yaml`
- `aurora-sealed-secrets-prod.yaml`

---

## 🔧 Troubleshooting

### Problem: Controller Can't Decrypt Secret

**Symptoms:** SealedSecret exists but regular Secret not created

**Solutions:**
```bash
# Check controller logs
kubectl logs -n kube-system -l name=sealed-secrets-controller

# Common issues:
# 1. Wrong namespace in SealedSecret
# 2. Wrong cluster (sealed secret bound to original cluster)
# 3. Controller key changed/lost
```

### Problem: Sealed Secret Won't Apply

**Error:** `cannot seal secret: no encrypted data`

**Solution:**
```bash
# Ensure plaintext secret has data fields populated
cat aurora-secret-plaintext.yaml | grep "data:" -A 5

# Re-create with correct values
```

### Problem: Old Secrets Still Being Used

**Symptoms:** Application using outdated secret values

**Solution:**
```bash
# Force pod restart to reload secrets
kubectl delete pod -n aurora-cloudbank -l app=aurora-gui-cloudhub

# Or rolling restart
kubectl rollout restart deployment/aurora-gui-cloudhub -n aurora-cloudbank
```

---

## 📊 Verification Checklist

- [ ] Sealed-secrets controller installed and running
- [ ] kubeseal CLI tool installed and working
- [ ] SealedSecret resource created in cluster
- [ ] Regular Secret auto-created by controller
- [ ] Pod can mount and access secret values
- [ ] Plaintext secret files deleted securely
- [ ] Only sealed secrets committed to git
- [ ] Documentation updated with rotation procedures
- [ ] Team trained on secret management workflow

---

## 🔗 Additional Resources

- **Official Documentation:** https://github.com/bitnami-labs/sealed-secrets
- **Best Practices:** https://kubernetes.io/docs/concepts/security/secrets-good-practices/
- **Key Management:** https://github.com/bitnami-labs/sealed-secrets#secret-rotation

---

**Chain Notation:** `#005//003//SEC`  
**DLP Tag:** `high3_k8s_secrets_documentation`  
**Officer:** OPS Rodriguez  
**Commander:** Thorne

🎖️ **Mission Documentation Complete**
