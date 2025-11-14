# Aurora CloudBank - Secrets Rotation Procedures

**Mission**: HIGH-3 K8s Secrets Encryption  
**Officer**: OPS Rodriguez  
**Chain**: `#005//003//SEC`  
**Ethics Protocol**: Picard Delta 3  
**Status**: Production-Ready Documentation

---

## Overview

This document provides comprehensive procedures for rotating Aurora CloudBank's sealed secrets. Regular rotation is critical for maintaining security posture and limiting exposure window if keys are compromised.

**Core Principle**: "Rotate before compromise, not after detection."

---

## Rotation Schedule

### Recommended Rotation Frequencies

| Secret Type | Rotation Frequency | Risk Level | Impact Window |
|-------------|-------------------|------------|---------------|
| **API Keys** (Anthropic, OpenAI) | 90 days | HIGH | 24-48 hours |
| **CSRF Secret Key** | 30 days | MEDIUM | 1-4 hours |
| **JWT Signing Key** | 30 days | CRITICAL | Immediate (requires user re-login) |
| **Emergency Rotation** | As needed | CRITICAL | Immediate (< 1 hour) |

### Rotation Triggers

**Scheduled Rotation** (planned):
- Calendar-based rotation per schedule above
- Before major releases or deployments
- After team member departures with key access

**Emergency Rotation** (unplanned):
- Suspected key compromise or exposure
- Security incident or breach detection
- Accidental commit to public repository
- Key found in logs or error messages
- Compliance audit requirement

---

## Pre-Rotation Checklist

Before rotating any secrets, ensure:

- [ ] **Maintenance Window Scheduled**: Notify team of planned rotation
- [ ] **Backup Current Sealed Secrets**: Save copy of existing sealed secrets
- [ ] **Backup Encryption Keys**: Ensure sealed-secrets controller keys are backed up
- [ ] **Verify Access**: Confirm kubectl cluster-admin access
- [ ] **Test Environment**: Rotate in dev/staging first if available
- [ ] **Rollback Plan**: Document procedure to revert if issues arise
- [ ] **Team Notification**: Alert team members about upcoming rotation
- [ ] **Documentation Review**: Confirm current secrets documented in vault/manager

---

## Rotation Procedures

### 1. API Keys Rotation (Anthropic & OpenAI)

**Impact**: Minimal (if new keys provisioned before rotation)  
**Downtime**: Zero (if blue-green deployment used)  
**Duration**: 30-45 minutes

#### Step 1: Provision New API Keys

**Anthropic Claude API**:
```bash
# 1. Log into Anthropic Console
# 2. Navigate to API Keys section
# 3. Generate new API key with same permissions
# 4. Copy new key to secure location (password manager)
# 5. DO NOT revoke old key yet
```

**OpenAI GPT API**:
```bash
# 1. Log into OpenAI Platform
# 2. Navigate to API Keys
# 3. Create new secret key
# 4. Copy key immediately (shown only once)
# 5. Store in secure location
# 6. Keep old key active temporarily
```

#### Step 2: Create New Sealed Secret

```bash
# Create plaintext secret with NEW keys
kubectl create secret generic aurora-api-keys-new \
  --namespace=aurora-cloudbank \
  --from-literal=anthropic-api-key='NEW_ANTHROPIC_KEY_HERE' \
  --from-literal=openai-api-key='NEW_OPENAI_KEY_HERE' \
  --from-literal=csrf-secret-key='CURRENT_CSRF_KEY' \
  --from-literal=jwt-secret-key='CURRENT_JWT_KEY' \
  --dry-run=client -o yaml > plaintext-new-api.yaml

# Seal the new secret
kubeseal --format=yaml < plaintext-new-api.yaml > aurora-sealed-secrets-new-api.yaml

# Verify sealed secret created
cat aurora-sealed-secrets-new-api.yaml | grep "encryptedData:" -A 5

# Securely delete plaintext
shred -vfz -n 3 plaintext-new-api.yaml
```

#### Step 3: Apply New Secret (Blue-Green Deployment)

```bash
# Backup current secret
kubectl get sealedsecret aurora-api-keys -n aurora-cloudbank -o yaml > backup-sealed-api-keys.yaml

# Apply new sealed secret with different name first
sed 's/aurora-api-keys/aurora-api-keys-new/g' aurora-sealed-secrets-new-api.yaml | kubectl apply -f -

# Verify new secret created
kubectl get secret aurora-api-keys-new -n aurora-cloudbank

# Test with new secret (update one pod's secret reference)
# If successful, proceed to next step
```

#### Step 4: Switch All Pods to New Secret

```bash
# Update deployment to use new secret
kubectl set env deployment/aurora-gui-cloudhub \
  --namespace=aurora-cloudbank \
  --from=secret/aurora-api-keys-new

# Monitor pod restarts
kubectl rollout status deployment/aurora-gui-cloudhub -n aurora-cloudbank

# Verify all pods using new secret
kubectl get pods -n aurora-cloudbank -o jsonpath='{.items[*].spec.containers[*].env[?(@.valueFrom.secretKeyRef.name=="aurora-api-keys-new")].valueFrom.secretKeyRef.name}'
```

#### Step 5: Verify API Functionality

```bash
# Test Anthropic API
kubectl exec -it deployment/aurora-gui-cloudhub -n aurora-cloudbank -- curl -H "x-api-key: \$(cat /etc/secrets/anthropic-api-key)" https://api.anthropic.com/v1/messages

# Test OpenAI API
kubectl exec -it deployment/aurora-gui-cloudhub -n aurora-cloudbank -- curl -H "Authorization: Bearer \$(cat /etc/secrets/openai-api-key)" https://api.openai.com/v1/models

# Check application logs for errors
kubectl logs -n aurora-cloudbank deployment/aurora-gui-cloudhub --tail=50 | grep -i "api\|auth\|error"
```

#### Step 6: Revoke Old API Keys

**ONLY after confirming new keys work for 24-48 hours**:

```bash
# Anthropic Console: Revoke old API key
# OpenAI Platform: Delete old secret key

# Remove old secret from cluster
kubectl delete secret aurora-api-keys -n aurora-cloudbank
kubectl delete sealedsecret aurora-api-keys -n aurora-cloudbank

# Rename new secret to standard name
kubectl get sealedsecret aurora-api-keys-new -n aurora-cloudbank -o yaml | \
  sed 's/aurora-api-keys-new/aurora-api-keys/g' | \
  kubectl apply -f -

# Update deployment back to standard name
kubectl set env deployment/aurora-gui-cloudhub \
  --namespace=aurora-cloudbank \
  --from=secret/aurora-api-keys

# Clean up backup files securely
shred -vfz -n 3 backup-sealed-api-keys.yaml
```

---

### 2. CSRF Secret Key Rotation

**Impact**: Medium (active sessions may require re-authentication)  
**Downtime**: Minimal (< 5 minutes)  
**Duration**: 15-20 minutes

#### Step 1: Generate New CSRF Secret

```bash
# Generate cryptographically secure random key (32 bytes)
NEW_CSRF_KEY=$(openssl rand -base64 32)

# Verify key generated
echo "New CSRF key length: ${#NEW_CSRF_KEY} characters"
# Should be 44 characters (32 bytes base64-encoded)
```

#### Step 2: Create and Seal New Secret

```bash
# Get current API keys from existing secret (to preserve them)
ANTHROPIC_KEY=$(kubectl get secret aurora-api-keys -n aurora-cloudbank -o jsonpath='{.data.anthropic-api-key}' | base64 -d)
OPENAI_KEY=$(kubectl get secret aurora-api-keys -n aurora-cloudbank -o jsonpath='{.data.openai-api-key}' | base64 -d)
CURRENT_JWT_KEY=$(kubectl get secret aurora-api-keys -n aurora-cloudbank -o jsonpath='{.data.jwt-secret-key}' | base64 -d)

# Create plaintext secret with new CSRF key
kubectl create secret generic aurora-api-keys \
  --namespace=aurora-cloudbank \
  --from-literal=anthropic-api-key="$ANTHROPIC_KEY" \
  --from-literal=openai-api-key="$OPENAI_KEY" \
  --from-literal=csrf-secret-key="$NEW_CSRF_KEY" \
  --from-literal=jwt-secret-key="$CURRENT_JWT_KEY" \
  --dry-run=client -o yaml > plaintext-csrf-rotation.yaml

# Seal the secret
kubeseal --format=yaml < plaintext-csrf-rotation.yaml > aurora-sealed-secrets.yaml

# Securely delete plaintext
shred -vfz -n 3 plaintext-csrf-rotation.yaml
unset ANTHROPIC_KEY OPENAI_KEY CURRENT_JWT_KEY NEW_CSRF_KEY
```

#### Step 3: Apply and Restart Pods

```bash
# Backup current sealed secret
kubectl get sealedsecret aurora-api-keys -n aurora-cloudbank -o yaml > backup-csrf-rotation.yaml

# Apply new sealed secret
kubectl apply -f aurora-sealed-secrets.yaml

# Verify updated
kubectl get sealedsecret aurora-api-keys -n aurora-cloudbank -o yaml | grep encryptedData

# Rolling restart to pick up new CSRF key
kubectl rollout restart deployment/aurora-gui-cloudhub -n aurora-cloudbank

# Monitor rollout
kubectl rollout status deployment/aurora-gui-cloudhub -n aurora-cloudbank
```

#### Step 4: Verify CSRF Protection

```bash
# Test CSRF validation
CSRF_TOKEN=$(kubectl exec -it deployment/aurora-gui-cloudhub -n aurora-cloudbank -- cat /etc/secrets/csrf-secret-key)

# Attempt request without CSRF token (should fail)
curl -X POST https://aurora.cloudbank.example/api/test -H "Content-Type: application/json"
# Expected: 403 Forbidden

# Attempt with valid CSRF token (should succeed)
curl -X POST https://aurora.cloudbank.example/api/test \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN"
# Expected: 200 OK or valid response

# Check logs for CSRF validation
kubectl logs -n aurora-cloudbank deployment/aurora-gui-cloudhub --tail=100 | grep -i csrf
```

---

### 3. JWT Signing Key Rotation

**Impact**: HIGH (all users must re-authenticate immediately)  
**Downtime**: None (but user sessions invalidated)  
**Duration**: 20-30 minutes

**⚠️ WARNING**: Rotating JWT signing key invalidates ALL active user sessions. Schedule during low-traffic maintenance window and notify users in advance.

#### Pre-Rotation Requirements

- [ ] Maintenance window scheduled and communicated
- [ ] User notification sent 48 hours in advance
- [ ] Support team on standby for re-login assistance
- [ ] Session monitoring dashboard ready
- [ ] Rollback plan documented

#### Step 1: Generate New JWT Key

```bash
# Generate strong JWT signing key (64 bytes recommended)
NEW_JWT_KEY=$(openssl rand -base64 64 | tr -d '\n')

# Verify key strength
echo "New JWT key length: ${#NEW_JWT_KEY} characters"
# Should be 88 characters (64 bytes base64-encoded)
```

#### Step 2: Dual-Key Grace Period (Optional but Recommended)

**For zero-downtime rotation with gradual session migration:**

```python
# Update application code to support dual JWT validation
# Old key validates existing sessions
# New key signs new sessions

JWT_OLD_KEY = os.getenv("JWT_SECRET_KEY_OLD")
JWT_NEW_KEY = os.getenv("JWT_SECRET_KEY")

def validate_jwt(token):
    try:
        # Try new key first
        return jwt.decode(token, JWT_NEW_KEY, algorithms=['HS256'])
    except jwt.InvalidSignatureError:
        # Fall back to old key during grace period
        return jwt.decode(token, JWT_OLD_KEY, algorithms=['HS256'])
```

```bash
# Create secret with BOTH old and new keys
kubectl create secret generic aurora-api-keys \
  --namespace=aurora-cloudbank \
  --from-literal=anthropic-api-key="$ANTHROPIC_KEY" \
  --from-literal=openai-api-key="$OPENAI_KEY" \
  --from-literal=csrf-secret-key="$CSRF_KEY" \
  --from-literal=jwt-secret-key="$NEW_JWT_KEY" \
  --from-literal=jwt-secret-key-old="$CURRENT_JWT_KEY" \
  --dry-run=client -o yaml > plaintext-jwt-dual.yaml

# Seal and apply
kubeseal --format=yaml < plaintext-jwt-dual.yaml > aurora-sealed-secrets-jwt-dual.yaml
kubectl apply -f aurora-sealed-secrets-jwt-dual.yaml
kubectl rollout restart deployment/aurora-gui-cloudhub -n aurora-cloudbank

# Wait for grace period (24-48 hours for most sessions to naturally expire)

# Remove old key after grace period
# (Create new sealed secret without jwt-secret-key-old field)
```

#### Step 3: Immediate Rotation (No Grace Period)

**If immediate rotation required (security incident):**

```bash
# Get current non-JWT secrets
ANTHROPIC_KEY=$(kubectl get secret aurora-api-keys -n aurora-cloudbank -o jsonpath='{.data.anthropic-api-key}' | base64 -d)
OPENAI_KEY=$(kubectl get secret aurora-api-keys -n aurora-cloudbank -o jsonpath='{.data.openai-api-key}' | base64 -d)
CSRF_KEY=$(kubectl get secret aurora-api-keys -n aurora-cloudbank -o jsonpath='{.data.csrf-secret-key}' | base64 -d)

# Create new sealed secret with new JWT key
kubectl create secret generic aurora-api-keys \
  --namespace=aurora-cloudbank \
  --from-literal=anthropic-api-key="$ANTHROPIC_KEY" \
  --from-literal=openai-api-key="$OPENAI_KEY" \
  --from-literal=csrf-secret-key="$CSRF_KEY" \
  --from-literal=jwt-secret-key="$NEW_JWT_KEY" \
  --dry-run=client -o yaml > plaintext-jwt-rotation.yaml

# Seal the secret
kubeseal --format=yaml < plaintext-jwt-rotation.yaml > aurora-sealed-secrets.yaml

# Backup, apply, and restart
kubectl get sealedsecret aurora-api-keys -n aurora-cloudbank -o yaml > backup-jwt-rotation.yaml
kubectl apply -f aurora-sealed-secrets.yaml
kubectl rollout restart deployment/aurora-gui-cloudhub -n aurora-cloudbank

# Securely delete plaintext
shred -vfz -n 3 plaintext-jwt-rotation.yaml
unset ANTHROPIC_KEY OPENAI_KEY CSRF_KEY NEW_JWT_KEY
```

#### Step 4: Force Session Invalidation

```bash
# Clear Redis session store (if applicable)
kubectl exec -it redis-master-0 -n aurora-cloudbank -- redis-cli FLUSHDB

# Or delete session storage PVC
kubectl delete pvc session-storage -n aurora-cloudbank

# Monitor user re-login rate
kubectl logs -n aurora-cloudbank deployment/aurora-gui-cloudhub --tail=200 | grep -i "login\|authentication" | wc -l
```

#### Step 5: Verify JWT Validation

```bash
# Test JWT generation with new key
NEW_TOKEN=$(kubectl exec -it deployment/aurora-gui-cloudhub -n aurora-cloudbank -- \
  python3 -c "import jwt; import os; print(jwt.encode({'user': 'test'}, os.getenv('JWT_SECRET_KEY'), algorithm='HS256'))")

echo "New JWT token generated: $NEW_TOKEN"

# Verify token validates correctly
kubectl exec -it deployment/aurora-gui-cloudhub -n aurora-cloudbank -- \
  python3 -c "import jwt; import os; jwt.decode('$NEW_TOKEN', os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])"

# Expected: {'user': 'test'} (no exceptions)

# Test old token fails (if immediate rotation)
# Should raise jwt.InvalidSignatureError
```

---

## Emergency Rotation Procedures

### Scenario: Suspected Key Compromise

**Response Time**: < 1 hour from detection to completion

#### Phase 1: Immediate Containment (0-15 minutes)

```bash
# 1. Alert security team
echo "SECURITY ALERT: Suspected key compromise detected at $(date)" | tee -a /var/log/aurora/security-alerts.log

# 2. Backup current secrets for forensics
kubectl get sealedsecret aurora-api-keys -n aurora-cloudbank -o yaml > forensics-sealed-secrets-$(date +%Y%m%d-%H%M%S).yaml

# 3. Disable compromised key at provider (if API key)
# - Anthropic Console: Disable key immediately
# - OpenAI Platform: Revoke key immediately

# 4. Enable enhanced monitoring
kubectl logs -f deployment/aurora-gui-cloudhub -n aurora-cloudbank | grep -i "unauthorized\|forbidden\|failed\|error" &
```

#### Phase 2: Generate Emergency Secrets (15-30 minutes)

```bash
# Generate ALL new secrets
NEW_ANTHROPIC_KEY="sk-ant-api03-EMERGENCY_KEY_PROVISION_FROM_CONSOLE"
NEW_OPENAI_KEY="sk-EMERGENCY_KEY_PROVISION_FROM_PLATFORM"
NEW_CSRF_KEY=$(openssl rand -base64 32)
NEW_JWT_KEY=$(openssl rand -base64 64 | tr -d '\n')

# Create emergency sealed secret
kubectl create secret generic aurora-api-keys-emergency \
  --namespace=aurora-cloudbank \
  --from-literal=anthropic-api-key="$NEW_ANTHROPIC_KEY" \
  --from-literal=openai-api-key="$NEW_OPENAI_KEY" \
  --from-literal=csrf-secret-key="$NEW_CSRF_KEY" \
  --from-literal=jwt-secret-key="$NEW_JWT_KEY" \
  --dry-run=client -o yaml > plaintext-emergency.yaml

# Seal immediately
kubeseal --format=yaml < plaintext-emergency.yaml > aurora-sealed-secrets-emergency.yaml

# Securely delete plaintext
shred -vfz -n 3 plaintext-emergency.yaml
unset NEW_ANTHROPIC_KEY NEW_OPENAI_KEY NEW_CSRF_KEY NEW_JWT_KEY
```

#### Phase 3: Deploy Emergency Secrets (30-45 minutes)

```bash
# Apply emergency sealed secret
kubectl apply -f aurora-sealed-secrets-emergency.yaml

# Force immediate pod restart (no rolling update)
kubectl delete pods -n aurora-cloudbank -l app=aurora-gui-cloudhub

# Wait for pods to restart with new secrets
kubectl wait --for=condition=ready pod -l app=aurora-gui-cloudhub -n aurora-cloudbank --timeout=120s

# Verify all pods using new secrets
kubectl get pods -n aurora-cloudbank -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}'
```

#### Phase 4: Validation and Monitoring (45-60 minutes)

```bash
# Test all API endpoints
curl -i https://aurora.cloudbank.example/health
curl -i https://aurora.cloudbank.example/api/v1/quantum/status

# Monitor error rates
kubectl logs -n aurora-cloudbank deployment/aurora-gui-cloudhub --tail=500 | grep -c "ERROR"

# Check for unauthorized access attempts
kubectl logs -n aurora-cloudbank deployment/aurora-gui-cloudhub --tail=1000 | grep -i "unauthorized\|403\|401"

# Verify no old keys being used
kubectl logs -n aurora-cloudbank deployment/aurora-gui-cloudhub --tail=1000 | grep -i "invalid.*key\|authentication.*failed"
```

#### Phase 5: Post-Incident Documentation (after containment)

- Document timeline of compromise detection and response
- Root cause analysis of how key was compromised
- Review and update .gitignore rules
- Audit all commits for exposed secrets (use git-secrets or truffleHog)
- Update runbooks with lessons learned
- Schedule post-mortem meeting with team

---

## Rotation Validation Checklist

After ANY secret rotation, verify:

- [ ] **New secret deployed**: `kubectl get sealedsecret aurora-api-keys -n aurora-cloudbank`
- [ ] **Pods restarted**: All pods show recent restart time
- [ ] **API keys functional**: Test Anthropic and OpenAI API calls succeed
- [ ] **CSRF validation working**: Test CSRF protection with valid/invalid tokens
- [ ] **JWT signing functional**: Generate and validate new JWT tokens
- [ ] **No errors in logs**: Check for authentication/authorization errors
- [ ] **Old secrets removed**: Verify old API keys revoked at providers
- [ ] **Plaintext files deleted**: Confirm secure deletion of plaintext manifests
- [ ] **Backup created**: Current sealed secret backed up before rotation
- [ ] **Documentation updated**: Rotation date recorded in runbook
- [ ] **Team notified**: Rotation completion communicated to team
- [ ] **Monitoring active**: Enhanced monitoring enabled for 48 hours post-rotation

---

## Rollback Procedures

If rotation causes issues:

```bash
# 1. Identify backup sealed secret
ls -lh backup-*.yaml

# 2. Apply previous sealed secret
kubectl apply -f backup-sealed-api-keys.yaml

# 3. Force immediate pod restart
kubectl rollout restart deployment/aurora-gui-cloudhub -n aurora-cloudbank

# 4. Monitor recovery
kubectl rollout status deployment/aurora-gui-cloudhub -n aurora-cloudbank

# 5. Verify service restored
curl -i https://aurora.cloudbank.example/health

# 6. Document rollback reason for post-mortem
echo "Rollback executed at $(date): REASON_HERE" >> /var/log/aurora/rotation-log.txt
```

---

## Automation Opportunities

### Automated Rotation Script (Future Enhancement)

```bash
#!/bin/bash
# aurora-rotate-secrets.sh - Automated secret rotation
# Usage: ./aurora-rotate-secrets.sh [api-keys|csrf|jwt|all]

SECRET_TYPE="$1"
NAMESPACE="aurora-cloudbank"
BACKUP_DIR="./secret-rotation-backups"

rotate_api_keys() {
  echo "Rotating API keys..."
  # Provision new keys from providers (manual step required)
  read -sp "Enter new Anthropic API key: " NEW_ANTHROPIC_KEY
  echo
  read -sp "Enter new OpenAI API key: " NEW_OPENAI_KEY
  echo
  
  # Create and seal new secret
  # ... (implementation follows manual procedures)
}

rotate_csrf_key() {
  echo "Rotating CSRF key..."
  NEW_CSRF_KEY=$(openssl rand -base64 32)
  # ... (implementation follows manual procedures)
}

rotate_jwt_key() {
  echo "WARNING: This will invalidate all user sessions!"
  read -p "Are you sure? (yes/no): " CONFIRM
  if [[ "$CONFIRM" != "yes" ]]; then
    echo "Rotation cancelled."
    exit 1
  fi
  
  echo "Rotating JWT key..."
  NEW_JWT_KEY=$(openssl rand -base64 64 | tr -d '\n')
  # ... (implementation follows manual procedures)
}

# Main execution
case "$SECRET_TYPE" in
  api-keys) rotate_api_keys ;;
  csrf) rotate_csrf_key ;;
  jwt) rotate_jwt_key ;;
  all)
    rotate_api_keys
    rotate_csrf_key
    rotate_jwt_key
    ;;
  *)
    echo "Usage: $0 [api-keys|csrf|jwt|all]"
    exit 1
    ;;
esac
```

---

## Best Practices Summary

1. **Never Rotate All Secrets Simultaneously**: Rotate incrementally to isolate issues
2. **Always Test in Lower Environments First**: Dev → Staging → Production
3. **Maintain Dual-Key Grace Periods for JWT**: Prevents mass user disruption
4. **Backup Before Rotation**: Always backup current sealed secrets
5. **Monitor for 48 Hours Post-Rotation**: Watch for delayed errors or edge cases
6. **Document Every Rotation**: Maintain audit trail of all rotations
7. **Automate Where Possible**: Reduce human error through automation
8. **Schedule During Low Traffic**: Minimize user impact
9. **Communicate Proactively**: Notify team before, during, and after rotation
10. **Practice Emergency Rotation**: Run drills quarterly

---

## Compliance and Audit

**Rotation Log Template**:

```
Date: 2025-11-11
Officer: OPS Rodriguez
Secret Type: api-keys
Rotation Type: Scheduled
Old Key Revoked: Yes
New Key Validated: Yes
Downtime: 0 minutes
Issues: None
Chain Notation: #005//003//SEC
T1 Anchor: 71580
SRB Anchor: 2510
Ethics Protocol: Picard Delta 3
```

Maintain rotation logs for compliance audits:
- HIPAA: 90-day audit trail required
- PCI DSS: Key rotation documented
- SOC 2: Access control change logs
- ISO 27001: Information security management records

---

**End of Rotation Procedures**

For questions or issues, refer to `k8s/SECRETS_MANAGEMENT.md` or contact the Security Team.

*"In Stellenbosch We Trust, Secrets We Rotate."*  
— Commander Thorne, Orion Station Security Operations
