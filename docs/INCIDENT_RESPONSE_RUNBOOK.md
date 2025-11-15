# Incident Response Runbook - PR #311
## Aurora CloudBank Flight Control Infrastructure

**Version:** 1.0  
**Effective Date:** November 10, 2025  
**Owner:** Captain Sarah Rodriguez, Operations Director  
**Emergency Contact:** See Section 1

---

## 🚨 PAGE 1: EMERGENCY CONTACTS & ESCALATION

### On-Call Rotation

| Role | Primary Contact | Backup Contact | Escalation |
|------|----------------|----------------|------------|
| **API/Backend** | CTO Dr. Marcus Webb | Dev Team Lead | Commander Thorne |
| **Security** | CSO Commander Aria Chen | Security Team | Commander Thorne |
| **Operations** | OPS Captain Rodriguez | Ops Team Lead | Commander Thorne |
| **Compliance** | CO Director James Park | Compliance Analyst | Commander Thorne |

### Contact Methods (In Order of Preference)

1. **PagerDuty** - Immediate alert (< 5 min response)
2. **Orion Station Comm** - Internal communication system
3. **Secure Email** - For non-urgent escalation
4. **Emergency Line** - Physical station emergency line

### Escalation Matrix

```
┌─────────────────────────────────────────────────────────┐
│ SEVERITY LEVEL          │ RESPONSE TIME │ ESCALATION   │
├─────────────────────────┼───────────────┼──────────────┤
│ P0 - Critical Outage    │ Immediate     │ Commander    │
│ P1 - Major Degradation  │ < 15 minutes  │ CTO/CSO      │
│ P2 - Minor Issue        │ < 1 hour      │ Team Lead    │
│ P3 - Informational      │ Next Business │ No Escalation│
└─────────────────────────────────────────────────────────┘
```

### After-Hours Emergency

**If incident occurs outside business hours:**
1. Page on-call engineer via PagerDuty
2. If no response in 15 minutes, escalate to backup
3. If no response in 30 minutes, page Commander Thorne
4. Document all contact attempts in incident log

---

## 🔥 PAGE 2: COMMON INCIDENTS & RESPONSES

### INCIDENT 1: API Server Down

**Symptoms:**
- `/health` endpoint not responding
- 502/503 errors from load balancer
- No telemetry data in monitoring

**Diagnosis:**
```bash
# Check if API server process is running
ps aux | grep "uvicorn"

# Check API server logs
tail -100 /var/log/aurora/api.log

# Test local health endpoint
curl http://localhost:8000/health
```

**Response Steps:**
1. **Restart API Server:**
   ```bash
   cd /opt/aurora-cloudbank-symbolic
   sudo systemctl restart aurora-api
   # OR if not using systemd:
   python api/aurora_api.py &
   ```

2. **Verify Health:**
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status": "healthy"}
   ```

3. **Check Logs for Errors:**
   ```bash
   grep ERROR /var/log/aurora/api.log | tail -50
   ```

4. **If Restart Fails:** Escalate to CTO Dr. Webb (P1)

---

### INCIDENT 2: Tests Failing After Deployment

**Symptoms:**
- pytest returning failures
- Integration tests timing out
- Module import errors

**Diagnosis:**
```bash
# Run quick test suite
pytest tests/test_fleet_bridge_integration.py -v

# Check for dependency issues
pip list | grep -E "(fastapi|pydantic|httpx)"

# Verify Python version
python --version  # Should be 3.11 or 3.12
```

**Response Steps:**
1. **If Tests Fail - DO NOT DEPLOY TO PRODUCTION**

2. **Rollback Immediately** (see Rollback section)

3. **Investigate Root Cause:**
   ```bash
   # Check recent commits
   git log --oneline -10
   
   # Compare with last known good commit
   git diff HEAD~1
   ```

4. **Fix and Re-test:**
   - Fix the issue in development
   - Run full test suite: `pytest tests/ -v`
   - Only proceed if 14/14 tests pass

5. **Escalate to CTO if:** Tests fail for unknown reason (P1)

---

### INCIDENT 3: Security Alert Triggered

**Symptoms:**
- Pre-commit hook blocking commits
- Security scan log showing violations
- Access logs showing unauthorized attempts

**Diagnosis:**
```bash
# Check security scan log
cat .security/scan_log.json | jq .

# Review recent git activity
git log --oneline -20

# Check for suspicious file access
grep "DENIED" /var/log/aurora/access.log
```

**Response Steps:**
1. **DO NOT BYPASS SECURITY HOOKS**

2. **If Pre-Commit Hook Blocks:**
   - Review the specific violation
   - Fix the code issue (don't use --no-verify)
   - Consult CSO Chen if violation is unclear

3. **If Unauthorized Access Detected:**
   - **IMMEDIATE:** Notify CSO Chen (P0 - Critical)
   - Preserve logs: `cp /var/log/aurora/* /tmp/incident-logs/`
   - Lock affected user accounts
   - Initiate security incident procedure

4. **If CVE Alert Received:**
   - Assess severity (Critical/High = P1, Moderate = P2)
   - Create tracking issue in GitHub
   - Schedule patch in next sprint

**Activation Phrase Redaction:**
- Bridge activation failures are now automatically redacted in logs and responses.
- If any activation phrase appears in telemetry or incident notes, escalate to CSO Chen immediately and purge/redact the artifact.

---

### INCIDENT 4: Performance Degradation

**Symptoms:**
- API response times > 1 second
- Docking sequences taking > 30 seconds
- High CPU/memory usage

**Diagnosis:**
```bash
# Check system resources
top -b -n 1 | head -20
free -h
df -h

# Check API performance
time curl http://localhost:8000/api/fleet/status

# Check for resource leaks
ps aux --sort=-%mem | head -10
```

**Response Steps:**
1. **Identify Bottleneck:**
   - CPU bound: Profile Python code
   - Memory bound: Check for memory leaks
   - I/O bound: Check disk/network

2. **Immediate Mitigation:**
   - Restart API server (clears memory leaks)
   - Scale horizontally (add more instances)
   - Enable caching if available

3. **Long-term Fix:**
   - Profile code with cProfile
   - Optimize database queries
   - Implement caching layer (Redis)

4. **Escalate to CTO if:** Performance degrades below SLA (P1)

---

### INCIDENT 5: DLP Manifest Generation Failure

**Symptoms:**
- No manifests being created in `station_manifests/`
- Hash validation failures
- Telemetry showing manifest errors

**Diagnosis:**
```bash
# Check if directory exists and is writable
ls -ld station_manifests/
touch station_manifests/test.txt && rm station_manifests/test.txt

# Check recent manifests
ls -lt station_manifests/ | head -10

# Check for generation errors
grep "manifest" /var/log/aurora/api.log | grep ERROR
```

**Response Steps:**
1. **Verify Directory Permissions:**
   ```bash
   sudo chmod 750 station_manifests/
   sudo chown aurora-dlp-service:aurora-operations station_manifests/
   ```

2. **Check Disk Space:**
   ```bash
   df -h | grep "station_manifests"
   # If full, archive old manifests to S3
   ```

3. **Test Manual Generation:**
   ```bash
   node modules/flight_control/demo_infrastructure.js
   # Should create 2 manifests
   ```

4. **If Still Failing:** Check DLP generator code, escalate to Dev Team (P2)

---

## 🔄 PAGE 3: ROLLBACK PROCEDURES

### Emergency Rollback - API Server

**When to Rollback:**
- Tests failing after deployment
- Critical bugs in production
- Performance regression
- Security vulnerability introduced

**Rollback Procedure:**

```bash
# 1. SSH to production server
ssh ops@orion-station-api-01

# 2. Navigate to application directory
cd /opt/aurora-cloudbank-symbolic

# 3. Check current commit
git log --oneline -5

# 4. Identify last known good commit
# (Check deployment log or monitoring for last stable version)
LAST_GOOD_COMMIT="db9eea9"  # Example

# 5. Create rollback branch
git checkout -b rollback-emergency-$(date +%Y%m%d-%H%M%S)

# 6. Revert to last known good
git reset --hard $LAST_GOOD_COMMIT

# 7. Restart API server
sudo systemctl restart aurora-api

# 8. Verify health
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 9. Run smoke tests
pytest tests/test_fleet_bridge_integration.py -v -x

# 10. Monitor for 15 minutes
watch -n 30 'curl -s http://localhost:8000/api/fleet/status | jq .'
```

**Post-Rollback:**
1. Document what went wrong in incident report
2. Notify team via Slack/email
3. Create GitHub issue for the problem
4. Fix forward - don't stay on old version long-term

---

### Database Rollback (If Applicable)

**Note:** PR #311 doesn't introduce database schema changes, but for future reference:

```bash
# If database migrations were applied:

# 1. Identify migration to rollback to
alembic history

# 2. Rollback migrations
alembic downgrade -1  # Rollback one migration
# OR
alembic downgrade <revision_id>  # Rollback to specific revision

# 3. Verify database state
psql -U aurora -d aurora_db -c "\dt"
```

---

### Service Restart Sequence

**Correct order to restart services:**

```bash
# 1. Stop all services (reverse dependency order)
sudo systemctl stop aurora-api
sudo systemctl stop aurora-telemetry
sudo systemctl stop aurora-dlp

# 2. Verify all stopped
sudo systemctl status aurora-*

# 3. Start services (dependency order)
sudo systemctl start aurora-dlp
sudo systemctl start aurora-telemetry
sudo systemctl start aurora-api

# 4. Verify health
for service in aurora-dlp aurora-telemetry aurora-api; do
    echo "Checking $service..."
    sudo systemctl status $service | head -5
done

# 5. Run health checks
curl http://localhost:8000/health
```

---

### Verification Checklist After Rollback/Restart

- [ ] API server responding to `/health` endpoint
- [ ] All 4 fleet bridge tests passing
- [ ] DLP manifests being generated
- [ ] Telemetry events being logged
- [ ] No errors in application logs (last 100 lines)
- [ ] CPU usage < 70%
- [ ] Memory usage < 80%
- [ ] Disk space > 20% free

**If Any Check Fails:** Continue investigating, escalate to next level

---

## 📊 Monitoring & Alerting

### Key Metrics to Watch

1. **API Response Time**
   - Threshold: > 500ms (warning), > 1s (critical)
   - Alert: Slack + PagerDuty

2. **Test Pass Rate**
   - Threshold: < 100% (critical)
   - Alert: Block deployment

3. **Error Rate**
   - Threshold: > 1% (warning), > 5% (critical)
   - Alert: Slack + PagerDuty

4. **Disk Space**
   - Threshold: < 20% (warning), < 10% (critical)
   - Alert: Email + Slack

5. **Security Scan Failures**
   - Threshold: Any critical/high CVE (critical)
   - Alert: CSO Chen immediately

---

## 📝 Incident Documentation

**After Every Incident:**

1. **Create Incident Report:**
   - Incident ID
   - Start/end time
   - Severity level
   - Root cause
   - Resolution steps
   - Lessons learned

2. **Update Runbook:**
   - Add new incident pattern if not covered
   - Update contact information if changed
   - Revise procedures based on what worked

3. **Post-Mortem (P0/P1 only):**
   - Schedule within 48 hours
   - Invite all stakeholders
   - Document in `docs/incidents/`
   - Create action items to prevent recurrence

---

## 🎯 Quick Reference Commands

```bash
# Health check
curl http://localhost:8000/health

# Run tests
pytest tests/ -v

# Check logs
tail -f /var/log/aurora/api.log

# Restart API
sudo systemctl restart aurora-api

# Check system resources
top
df -h
free -h

# Git status
git status
git log --oneline -10

# Check security
cat .security/scan_log.json | jq .
```

---

**RUNBOOK APPROVED BY:**

Captain Sarah Rodriguez, Operations Director  
Date: 2025-11-10

**DLP:** INCIDENT-RUNBOOK-311  
**T1:** 311-RUNBOOK  
**SRB:** 2097152  
**@seal:** RUNBOOK-APPROVED-20251110

---

**END OF RUNBOOK - KEEP THIS ACCESSIBLE 24/7**
