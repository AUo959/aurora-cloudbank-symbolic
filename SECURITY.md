# 🔒 Aurora CloudBank - Security Policy & Guidelines

## Security Overview

Aurora CloudBank applies defence-in-depth to protect user data and system
integrity: CSRF enforcement on every state-changing route, PII scrubbing before
logging, a hash-linked tamper-evident audit ledger, and path containment on
every filesystem-touching surface.

**This project has not been independently audited, and carries no security
score.** Any number here would be self-assigned, and a self-assigned score is
the kind of claim this repository tries not to make — see
[`docs/VERIFIED_CLAIMS.md`](docs/VERIFIED_CLAIMS.md) for the standard: every
claim shows the command that produces it.

What can be said with evidence:

- **114 security-marked tests** cover path containment, CSRF, PII redaction, and
  ledger tamper detection. Run them with `pytest -m security -q`
  (114 passed, 4 skipped, ~2 s on the machine this was measured on).
- Static analysis runs on every PR (CodeQL, SonarCloud, Codacy, GitGuardian).
- Known open security work is tracked in public issues rather than closed
  silently — see the `security:` prefixed issues.

Known-open findings are listed in the issue tracker, not summarised here, so
that this file cannot drift away from them.

## 🛡️ Security Framework

### Core Security Principles
- **Defense in Depth**: Multiple layers of security controls
- **Zero Trust Architecture**: Verify everything, trust nothing
- **Principle of Least Privilege**: Minimal access rights
- **Security by Design**: Built-in security from ground up

### Security Components
1. **Input Validation & Sanitization**
2. **Authentication & Authorization**
3. **Encryption at Rest & Transit**
4. **Security Monitoring & Alerting**
5. **Vulnerability Management**
6. **Incident Response**

## 🔐 Security Measures Implemented

### 1. Dependency Security
- **Automated Vulnerability Scanning**: Daily dependency scans
- **Version Pinning**: All dependencies locked to secure versions
- **Security-First Updates**: Prioritized security patches
- **License Compliance**: Only approved licenses allowed

### 2. Code Security
- **Static Analysis**: Comprehensive security pattern scanning
- **Input Validation**: All user inputs validated and sanitized
- **Secure Coding**: Following OWASP secure coding guidelines
- **Code Review**: Security-focused peer reviews

### 3. Infrastructure Security
- **Security Headers**: Comprehensive HTTP security headers
- **Rate Limiting**: API abuse prevention
- **SSL/TLS**: End-to-end encryption
- **Environment Isolation**: Secure environment separation

### 4. Monitoring & Detection
- **Real-time Monitoring**: 24/7 security event monitoring
- **Threat Detection**: Advanced pattern recognition
- **Incident Response**: Automated alert system
- **Audit Logging**: Complete security event logging

## 🍪 Authentication & Cookie Policy

### Authentication Architecture

Aurora CloudBank uses **stateless, token-based authentication** exclusively. The API does not
set HTTP cookies for any purpose.

- **Primary auth**: `Authorization: Bearer <JWT>` header
- **Session management**: Cryptographically-signed JWT tokens with configurable expiry
- **CSRF protection**: Token-based CSRF verification (`X-CSRF-Token` header), not cookie-based

### Cookie Usage

**The Aurora CloudBank API backend does not issue `Set-Cookie` headers.**

No cookies are created, read, or required by any API endpoint. This means HTTP cookie flags
(`Secure`, `HttpOnly`, `SameSite`) are not applicable to the backend itself.

**Rationale:**
- Stateless token-based auth is better suited for REST APIs and microservices
- Eliminates cookie-related attack surfaces (session fixation, cross-site cookie leakage)
- Enables horizontal scaling without shared session state
- Simplifies CORS configuration (no `credentials: true` needed)

### Guidance for Web Clients

If a web frontend stores JWT tokens in cookies (a valid hardening option), it should enforce
`Secure; HttpOnly; SameSite=Strict` on those cookies. The backend enforces no opinion on
client-side token storage.

## 🚨 Vulnerability Reporting

### Responsible Disclosure
Please report security vulnerabilities privately to: security@auroracloudbank.com

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested remediation (if known)

### Response Timeline
- **Critical**: Response within 24 hours
- **High**: Response within 72 hours
- **Medium/Low**: Response within 1 week

## 🔧 Security Configuration

### Environment Security
```bash
# Use secure environment configuration
cp .env.secure.template .env
# Configure secure values (see template comments)
```

### Dependency Security
```bash
# Install security-enhanced dependencies
pip install -r requirements-secure.txt

# Run security audit
pip-audit --desc
safety check
```

### Security Monitoring
```bash
# Start security monitoring
python security_monitoring_system.py

# View security dashboard
curl http://localhost:8000/security/status
```

## 📊 What runs, and what it does not tell you

This table previously reported five metrics as "✅ Achieved", including a
self-assigned 100/100 code security score. None of those figures were measured,
so they have been replaced with the checks that actually run and an honest note
on each one's limits.

| Check | Runs on | What it does *not* cover |
|---|---|---|
| CodeQL | every PR | Alerts dismissed as "won't fix" do not reappear. Query all states, not just `open`, before concluding a branch is clean. Every high/critical dismissal is adjudicated in [docs/CODEQL_TRIAGE.md](docs/CODEQL_TRIAGE.md). |
| SonarCloud | every PR | Quality gate is scoped to changed lines, not the whole tree. |
| Codacy | every PR | Currently fails any PR that adds pytest tests — see the tracking issue on the zero-new-issues threshold. |
| GitGuardian | every PR | Detects committed secrets; says nothing about secrets supplied at runtime. |
| Security-marked tests | `pytest -m security` | Covers path containment, CSRF, PII redaction, ledger tamper detection. Not exhaustive. |
| Dependabot | continuous | Opens PRs; merging them is not automatic, and the `frontend/` package has no build gate verifying them. |

**No CI job runs on macOS or Windows.** Every workflow is `ubuntu-latest`, so
platform-specific defects reach `main` unchallenged — three have, all in path
handling.

## 🏆 Design principles

These are the principles the architecture is built to, **not certifications** —
nothing here has been certified or independently assessed:

- **OWASP Top 10**: used as a design reference
- **Security by design**: security considered at architecture level, not bolted on
- **Zero trust**: verify at each boundary rather than trusting callers
- **Defence in depth**: containment enforced at more than one layer, so a single
  missed check is not sufficient on its own

## 📋 Security Checklist

### Development Security
- [ ] All dependencies scanned for vulnerabilities
- [ ] Code reviewed for security patterns
- [ ] Input validation implemented
- [ ] Authentication/authorization tested
- [ ] Security headers configured

### Deployment Security
- [ ] Environment variables secured
- [ ] SSL/TLS certificates valid
- [ ] Monitoring systems active
- [ ] Backup encryption enabled
- [ ] Access controls verified

### Operational Security
- [ ] Security logs monitored
- [ ] Vulnerability scans scheduled
- [ ] Incident response plan ready
- [ ] Security training completed
- [ ] Regular security assessments

---

**Last Updated**: September 25, 2025
**Security Team**: Aurora CloudBank Security Team
**Next Review**: October 25, 2025
