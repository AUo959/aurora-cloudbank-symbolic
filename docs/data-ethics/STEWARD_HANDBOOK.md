# 🛡️ Data Guardian Steward Handbook

**Aurora CloudBank Ethical Data Guardian**  
**Version:** 0.1.0  
**Anchor:** T1-EDG-DOCS-001  
**Chain:** #005//005/EDG

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [PII Detection](#pii-detection)
5. [Redaction Strategies](#redaction-strategies)
6. [CLI Usage](#cli-usage)
7. [API Reference](#api-reference)
8. [Integration Guide](#integration-guide)
9. [Security & Privacy](#security--privacy)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Ethical Data Guardian** is Aurora CloudBank's comprehensive PII (Personally Identifiable Information) detection and redaction system. It provides:

- **Detection**: Identify 12 types of PII across text and structured data
- **Redaction**: 6 configurable strategies to protect sensitive information
- **Tracking**: Full DLP (Data Lineage & Provenance) integration
- **CLI & API**: Multiple interfaces for different workflows

### Why Data Guardian?

- **Zero Dependencies**: Pure Python stdlib implementation
- **Production-Ready**: 23 tests, 100% pass rate
- **Auditable**: Complete audit trails and DLP tracking
- **Flexible**: 6 redaction strategies for different use cases

---

## Quick Start

### Installation

Data Guardian is included with Aurora CloudBank. No additional installation required.

```bash
# Verify installation
python -c "from modules.data_guardian import PIIDetector; print('✓ Installed')"
```

### 5-Minute Tutorial

**1. Scan a file for PII:**

```bash
# Create sample file
echo "Email: john@example.com, Phone: 555-123-4567" > sample.txt

# Scan for PII
python -c "
from modules.data_guardian.cli import DataGuardianCLI
cli = DataGuardianCLI()
result = cli.scan_file('sample.txt')
print(f'Found {result[\"total_detections\"]} PII items')
"
```

**2. Redact PII from a file:**

```bash
python -c "
from modules.data_guardian.cli import DataGuardianCLI
cli = DataGuardianCLI()
result = cli.redact_file('sample.txt', strategy='mask')
print(f'Redacted {result[\"total_redactions\"]} items')
print(f'Output: {result[\"output_file\"]}')
"
```

**3. Interactive CLI:**

```bash
python aurora_cli.py
# In interactive mode:
# aurora> data:scan sample.txt
# aurora> data:redact sample.txt --strategy hash
```

---

## Core Concepts

### PII Types

Data Guardian detects 12 categories of PII:

| Type | Description | Example |
|------|-------------|---------|
| `EMAIL` | Email addresses (RFC 5322) | `user@example.com` |
| `PHONE` | Phone numbers (multiple formats) | `(555) 123-4567` |
| `SSN` | US Social Security Numbers | `123-45-6789` |
| `CREDIT_CARD` | Credit card numbers | `4532-1234-5678-9010` |
| `IP_ADDRESS` | IPv4 addresses | `192.168.1.100` |
| `DATE_OF_BIRTH` | Dates of birth | `01/15/1990` |
| `PASSPORT` | Passport numbers | `A12345678` |
| `DRIVER_LICENSE` | Driver's license numbers | `DL123456` |
| `BANK_ACCOUNT` | Bank account numbers | `9876543210` |
| `FULL_NAME` | Person names | `Jane Smith` |
| `ADDRESS` | Physical addresses | `123 Main St` |
| `CUSTOM` | Custom patterns | User-defined |

### Confidence Scoring

Each detection includes a confidence score (0.0-1.0):

- **0.95**: High confidence (e.g., well-formed email)
- **0.85**: Medium confidence (e.g., phone with variations)
- **0.70**: Standard threshold (default)
- **0.50**: Low confidence (may include false positives)

### Regions

Detection rules are region-specific:

- `US`: United States (SSN, US phone formats)
- `EU`: European Union (GDPR-focused)
- `UK`: United Kingdom
- `CA`: Canada
- `AU`: Australia

---

## PII Detection

### Basic Detection

```python
from modules.data_guardian.detection_rules import PIIDetector

# Initialize detector
detector = PIIDetector(region="US")

# Detect PII in text
text = "Contact: alice@example.com, Phone: 555-123-4567"
detections = detector.detect(text, min_confidence=0.7)

# Results
for d in detections:
    print(f"Type: {d['type']}, Value: {d['match']}, Confidence: {d['confidence']}")
```

### Dictionary Scanning

```python
# Scan nested structures
data = {
    "user": {
        "email": "user@example.com",
        "phone": "555-123-4567"
    },
    "contacts": ["alice@test.com", "bob@test.org"]
}

detections = detector.scan_dict(data)
# Returns nested dict with detections at each path
```

### Custom Rules

```python
import re
from modules.data_guardian.detection_rules import DetectionRule, PIIType

# Add custom pattern
custom_rule = DetectionRule(
    pii_type=PIIType.CUSTOM,
    pattern=re.compile(r"EMP-\d{6}"),
    confidence=0.9,
    region="US",
    description="Employee ID pattern"
)

detector.add_rule(custom_rule)
```

---

## Redaction Strategies

### Strategy Overview

| Strategy | Description | Use Case | Example |
|----------|-------------|----------|---------|
| `MASK` | Structure-preserving asterisks | Visual privacy, debugging | `john@example.com` → `****@*******.***` |
| `HASH` | SHA256 deterministic hash | Consistent pseudonymization | `test@example.com` → `SHA256:a1b2c3...` |
| `REMOVE` | Complete deletion | Maximum privacy | `Email: test@example.com` → `Email: ` |
| `PARTIAL` | Show first/last chars | Human recognition | `longname@example.com` → `lo*****@ex*****.com` |
| `TOKEN` | Numbered placeholders | Reversible with key | `test@example.com` → `[PII-EMAIL-001]` |
| `SYNTHETIC` | Fake but realistic data | Testing environments | `real@example.com` → `fake42@example.com` |

### Basic Redaction

```python
from modules.data_guardian.redaction import RedactionEngine, RedactionStrategy

# Initialize
detector = PIIDetector()
redactor = RedactionEngine()

# Detect and redact
text = "Email: sensitive@example.com"
detections = detector.detect(text)
redacted = redactor.redact_text(text, detections, RedactionStrategy.MASK)

print(redacted)  # "Email: *********@*******.***"
```

### Audit Trails

```python
# Redact with audit tracking
redacted = redactor.redact_text(text, detections, RedactionStrategy.HASH)

# Get audit trail
audit = redactor.get_audit_trail()
for entry in audit:
    print(f"Redacted: {entry}")

# Reset audit for next operation
redactor.reset_audit_trail()
```

---

## CLI Usage

### Scan Commands

**Scan a file:**
```bash
python -c "
from modules.data_guardian.cli import DataGuardianCLI
cli = DataGuardianCLI()
cli.scan_file('myfile.txt', output_format='json')
"
```

**Scan stdin:**
```bash
echo "Email: test@example.com" | python -c "
from modules.data_guardian.cli import DataGuardianCLI
import sys
cli = DataGuardianCLI()
cli.scan_stdin()
"
```

### Redact Commands

**Redact a file:**
```bash
python -c "
from modules.data_guardian.cli import DataGuardianCLI
cli = DataGuardianCLI()
cli.redact_file('myfile.txt', strategy='mask', output_path='myfile.redacted.txt')
"
```

**In-place redaction:**
```bash
python -c "
from modules.data_guardian.cli import DataGuardianCLI
cli = DataGuardianCLI()
cli.redact_file('myfile.txt', strategy='hash', in_place=True)
"
```

### Interactive Mode

```bash
python aurora_cli.py

# Commands:
# aurora> data:scan <file>                   # Scan file for PII
# aurora> data:redact <file> --strategy mask # Redact PII
# aurora> data:strategies                    # List strategies
# aurora> data:pii-types                     # List detectable types
```

---

## API Reference

### FastAPI Endpoints

Data Guardian provides REST API endpoints when integrated with `aurora_api.py`:

#### POST /data/scan

Scan text or JSON for PII.

**Request:**
```json
{
  "data": "Email: test@example.com, Phone: 555-123-4567",
  "confidence_threshold": 0.7,
  "region": "US"
}
```

**Response:**
```json
{
  "detections": [
    {
      "type": "email",
      "value": "test@example.com",
      "confidence": 0.95,
      "location": {"start": 7, "end": 23}
    },
    {
      "type": "phone",
      "value": "555-123-4567",
      "confidence": 0.85,
      "location": {"start": 32, "end": 44}
    }
  ],
  "total_detections": 2
}
```

#### POST /data/redact

Redact PII with specified strategy.

**Request:**
```json
{
  "data": "Email: test@example.com",
  "strategy": "mask",
  "confidence_threshold": 0.7,
  "region": "US"
}
```

**Response:**
```json
{
  "redacted_data": "Email: ****@*******.***",
  "redaction_count": 1,
  "audit_trail": ["SHA256:..."],
  "strategy": "mask"
}
```

#### GET /data/strategies

List available redaction strategies.

#### GET /data/pii-types

List detectable PII types.

#### GET /data/regions

List supported regions.

#### GET /data/health

Health check endpoint.

---

## Integration Guide

### With DLP Tracking

```python
from modules.data_guardian.integration import DataGuardianDLPIntegration

# Initialize with DLP tracking
integration = DataGuardianDLPIntegration(
    region="US",
    context_tag="my-app"
)

# Scan with tracking
scan_result = integration.scan_with_tracking(
    data="Email: sensitive@example.com",
    min_confidence=0.7
)

print(f"DLP Tag: {scan_result['dlp_tag_id']}")
print(f"Data Hash: {scan_result['data_hash']}")

# Redact with tracking (reuses scan detections)
redact_result = integration.redact_with_tracking(
    data="Email: sensitive@example.com",
    strategy=RedactionStrategy.MASK,
    scan_result=scan_result
)

print(f"Redacted: {redact_result['redacted_data']}")
print(f"Audit: {len(redact_result['audit_trail'])} entries")

# Export manifest
manifest = integration.create_export_manifest("my_export.json")
print(f"Exported to: {manifest['export_path']}")
```

### With FastAPI Middleware

```python
from fastapi import FastAPI
from modules.data_guardian.middleware import DataGuardianMiddleware
from modules.data_guardian.redaction import RedactionStrategy

app = FastAPI()

# Add middleware
middleware = DataGuardianMiddleware(
    app,
    enabled=True,
    scan_requests=True,
    scan_responses=True,
    redact_mode=False,  # Set True to auto-redact
    redaction_strategy=RedactionStrategy.MASK,
    region="US",
    excluded_paths=["/health", "/docs"]
)

# Middleware automatically scans all requests/responses
# View stats
stats = middleware.get_stats()
print(f"PII detected: {stats['pii_detected']}")
```

---

## Security & Privacy

### Best Practices

1. **Confidence Thresholds**: Use 0.7+ for production to minimize false positives
2. **Strategy Selection**:
   - `MASK`: For logs and debugging
   - `HASH`: For analytics requiring consistency
   - `REMOVE`: For maximum privacy compliance
3. **Audit Trails**: Always review audit logs before production deployment
4. **Region Configuration**: Match detection region to data jurisdiction

### GDPR Compliance

Data Guardian supports GDPR Article 32 (Security of Processing):

- **Pseudonymization**: Use `HASH` or `TOKEN` strategies
- **Minimization**: Use `REMOVE` to delete unnecessary PII
- **Audit Logs**: Full redaction audit trails
- **Right to Erasure**: `REMOVE` strategy supports complete deletion

### HIPAA Compliance

For healthcare data:

- Enable `SSN`, `DATE_OF_BIRTH`, `ADDRESS` detection
- Use `HASH` for patient identifiers needing consistency
- Maintain audit trails for all redactions
- Configure excluded paths for non-PHI endpoints

---

## Troubleshooting

### Common Issues

**Issue**: False positives in email detection  
**Solution**: Increase `min_confidence` to 0.8 or 0.9

**Issue**: Missing detections  
**Solution**: Lower `min_confidence` to 0.5, or add custom rules

**Issue**: Slow performance on large files  
**Solution**: Process in chunks or use streaming detection

**Issue**: DLP integration fails  
**Solution**: Verify `src/core/native_dlp_export.py` is accessible

### Debug Mode

```python
# Enable verbose detection
detector = PIIDetector(region="US")
detections = detector.detect(text, min_confidence=0.5)

# Print all detections with confidence
for d in detections:
    print(f"{d['type']}: {d['match']} (confidence: {d['confidence']})")

# Check detector stats
stats = detector.get_stats()
print(f"Total rules: {stats['total_rules']}")
print(f"PII types: {stats['pii_types']}")
```

### Support

- **Documentation**: `docs/data-ethics/STEWARD_HANDBOOK.md`
- **Tests**: `tests/test_data_guardian.py`
- **Examples**: `modules/data_guardian/integration.py` (demo)
- **API Docs**: `/docs` endpoint when server running

---

## Appendix

### Version History

- **0.1.0** (T1-EDG-DOCS-001): Initial release
  - 12 PII types, 6 redaction strategies
  - CLI, API, DLP integration
  - 23 tests, 100% pass rate

### Anchor Progression

- T1-EDG-001: Foundation (detection, redaction, middleware)
- T1-EDG-002: API & CLI
- T1-EDG-003: Test suite
- T1-EDG-004: DLP integration
- T1-EDG-DOCS-001: Documentation

### License

Part of Aurora CloudBank Symbolic system. See repository LICENSE.

---

**End of Steward Handbook**  
*Protect data. Preserve privacy. Proceed ethically.* 🛡️
