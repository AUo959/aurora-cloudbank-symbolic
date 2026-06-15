# Trustworthy Insight Ledger Guide

**Aurora CloudBank Symbolic - Trustworthy AI Infrastructure**

Version: 1.0.0  
Anchor: T1-TIL-005  
Status: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Security Model](#security-model)
4. [Getting Started](#getting-started)
5. [API Reference](#api-reference)
6. [CLI Reference](#cli-reference)
7. [Python SDK](#python-sdk)
8. [Use Cases](#use-cases)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Performance](#performance)
12. [Integration Guide](#integration-guide)

---

## Overview

### What is the Insight Ledger?

The **Trustworthy Insight Ledger** is Aurora's cryptographically-secured, append-only audit trail for AI insights, decisions, and analysis results. It provides **transparency**, **accountability**, and **verifiability** for AI systems by creating an immutable record of every significant decision or insight generated.

### Key Features

- **Immutable Storage**: Append-only architecture prevents modification or deletion
- **Cryptographic Integrity**: HMAC-SHA256 signatures + SHA-256 hash chains
- **Tamper Detection**: Automatic verification of ledger integrity
- **Flexible Querying**: Filter by type, source, time, tags, severity, or full-text search
- **Multiple Interfaces**: REST API, Python SDK, and CLI
- **DLP Integration**: Automatic Data Lineage Protocol tracking
- **Performance**: Handles 10,000+ entries efficiently with sub-second queries
- **Thread-Safe**: Concurrent writes without corruption
- **Auto-Checkpointing**: Periodic integrity snapshots every N entries

### Why Use It?

**Regulatory Compliance**
- Audit trails for GDPR, CCPA, HIPAA compliance
- Demonstrate AI decision transparency
- Prove data provenance and lineage

**Trustworthy AI**
- Record AI reasoning and explanations
- Track model predictions and confidence
- Document decision-making processes

**Security & Monitoring**
- Audit trail for security events
- Tamper-evident logging
- Intrusion detection via integrity verification

**Research & Development**
- Reproducibility of AI experiments
- Track model evolution over time
- Analyze decision patterns

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Aurora API Layer                      │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │  FastAPI     │  │   CLI       │  │  Python SDK  │   │
│  │  Endpoints   │  │  Commands   │  │  Direct API  │   │
│  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘   │
└─────────┼──────────────────┼─────────────────┼──────────┘
          │                  │                 │
          └──────────────────┼─────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Insight Ledger  │
                    │   Core Engine    │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  Signature     │  │  Ledger Core    │  │  DLP Tracker   │
│  Manager       │  │  (Append-Only)  │  │  Integration   │
│  (HMAC/SHA)    │  │  Storage        │  │  (Optional)    │
└────────────────┘  └─────────┬───────┘  └────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   File Storage     │
                    │  ┌──────────────┐  │
                    │  │ entries.jsonl│  │ ← Main ledger
                    │  ├──────────────┤  │
                    │  │  index.json  │  │ ← Fast lookups
                    │  ├──────────────┤  │
                    │  │  ledger.key  │  │ ← HMAC secret
                    │  └──────────────┘  │
                    └────────────────────┘
```

### Data Flow

**Recording an Insight:**

```
1. Client submits InsightRecord
   ↓
2. Ledger validates schema
   ↓
3. Generate unique entry_id + timestamp
   ↓
4. Create HMAC signature
   ↓
5. Link to previous entry via hash
   ↓
6. Append to entries.jsonl (atomic write)
   ↓
7. Update index.json
   ↓
8. (Optional) Track in DLP system
   ↓
9. Return complete LedgerEntry
```

**Verifying Integrity:**

```
1. Read entries from JSONL file
   ↓
2. For each entry:
   - Verify HMAC signature
   - Verify hash chain link
   - Check previous_hash continuity
   ↓
3. Generate verification report
   - Count verified/failed entries
   - List errors and failures
   - Measure verification time
```

### Storage Format

**JSONL Format (entries.jsonl)**

Each line is a complete JSON object representing one ledger entry:

```json
{"entry_id":"insight_20250126_120000_000001","timestamp":"2025-01-26T12:00:00Z","entry_type":"insight","insight_type":"decision","content":"Approved user request","context":{"policy":"v2"},"source":"auth-service","tags":["access-control"],"severity":"info","related_anchor":"T1-ACC-003","signature":"a1b2c3d4...","previous_hash":"9e8f7d6c...","entry_hash":"1a2b3c4d..."}
```

**Index Format (index.json)**

Cached metadata for O(1) stats lookups:

```json
{
  "entry_count": 1250,
  "last_hash": "1a2b3c4d...",
  "first_timestamp": "2025-01-01T00:00:00Z",
  "last_timestamp": "2025-01-26T12:00:00Z",
  "entries_by_type": {
    "decision": 450,
    "analysis": 320,
    "alert": 480
  },
  "entries_by_source": {
    "auth-service": 450,
    "monitor-service": 800
  }
}
```

### Hash Chain Mechanism

Each entry links to the previous entry via cryptographic hash:

```
Genesis Entry
  entry_hash: hash_0
  previous_hash: null
       ↓
Entry 1
  entry_hash: hash_1
  previous_hash: hash_0
       ↓
Entry 2
  entry_hash: hash_2
  previous_hash: hash_1
       ↓
     ...
```

**Hash Calculation:**
```python
entry_hash = SHA256({
    "entry_id": "...",
    "timestamp": "...",
    "content": "...",
    "previous_hash": "...",
    "signature": "..."
})
```

Any modification breaks the chain → tamper detection!

---

## Security Model

### Cryptographic Guarantees

**1. Authenticity (HMAC Signatures)**

Every entry is signed with HMAC-SHA256:

```python
signature = HMAC-SHA256(secret_key, entry_data)
```

- Proves entry was created by legitimate system (has secret key)
- Cannot be forged without secret key
- Constant-time verification prevents timing attacks

**2. Integrity (Hash Chains)**

Entries are linked via SHA-256 hashes:

```python
entry_hash = SHA256(entry_id + timestamp + content + previous_hash + signature)
```

- Any modification changes the hash
- Break in chain immediately detected
- Forward security: can't modify past without breaking future

**3. Immutability (Append-Only Storage)**

- No update or delete operations
- JSONL format: atomic append-only writes
- Thread-safe locking prevents corruption

### Threat Model

**Protected Against:**

✅ **Unauthorized Modification**: HMAC signatures prevent tampering  
✅ **Entry Deletion**: Hash chain breaks if entries removed  
✅ **Entry Insertion**: Previous hash mismatch detected  
✅ **Replay Attacks**: Timestamps + unique IDs prevent duplicates  
✅ **Forgery**: Cannot create valid signature without secret key  
✅ **Chain Breaks**: Integrity verification detects any discontinuity  

**Not Protected Against:**

❌ **Secret Key Compromise**: Attacker with key can forge entries  
❌ **Complete Deletion**: If entire ledger is deleted, no recovery  
❌ **Physical Access**: Direct filesystem access can delete files  
❌ **Timestamp Manipulation**: System clock must be trusted  

### Security Best Practices

**1. Secret Key Management**

```bash
# Generate strong key
python -c "from modules.insight_ledger.crypto_signatures import generate_secret_key; print(generate_secret_key())"

# Store securely (e.g., environment variable)
export LEDGER_SECRET_KEY="your_secret_key_here"

# Restrict file permissions
chmod 600 data/insight_ledger/ledger.key
```

**2. Regular Integrity Checks**

```bash
# Verify integrity daily
insight_ledger verify --storage ./data/insight_ledger

# Alert on failures
if ! insight_ledger verify; then
    send_alert "Ledger integrity compromised!"
fi
```

**3. Backup & Recovery**

```bash
# Daily exports
insight_ledger export --output ./backups/ledger_$(date +%Y%m%d).json

# Verify backups
verify_backup_integrity
```

**4. Access Control**

```python
# Restrict API access with authentication
@app.post("/ledger/insight")
async def record_insight(
    request: RecordInsightRequest,
    token: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify token before recording
    verify_token(token)
    ...
```

---

## Getting Started

### Installation

**1. Basic Installation**

The Insight Ledger is included with Aurora CloudBank:

```bash
cd aurora-cloudbank-symbolic
pip install -r requirements.txt
```

**2. Verify Installation**

```bash
python -c "from modules.insight_ledger import InsightLedger; print('✅ Installed')"
```

### Quick Start (Python SDK)

```python
from modules.insight_ledger.ledger_core import InsightLedger
from modules.insight_ledger.schemas import InsightRecord, InsightType

# Initialize ledger
ledger = InsightLedger(storage_path="./my_ledger")

# Record an insight
insight = InsightRecord(
    insight_type=InsightType.DECISION,
    content="Approved user access to sensitive data",
    source="access-control-service",
    context={"user_id": "user_123", "policy": "data-access-v2"},
    tags=["access-control", "approval"],
    severity="info",
    related_anchor="T1-ACC-003"
)

entry = ledger.record_insight(insight)
print(f"Recorded: {entry.entry_id}")

# Query history
from modules.insight_ledger.schemas import AuditQuery

query = AuditQuery(
    insight_types=[InsightType.DECISION],
    limit=10
)
entries = ledger.query_history(query)

# Verify integrity
report = ledger.verify_integrity()
print(f"Integrity: {'✅ Verified' if report['chain_intact'] else '❌ Compromised'}")
```

### Quick Start (REST API)

**1. Start Aurora API Server**

```bash
cd aurora-cloudbank-symbolic
python aurora_api.py
```

**2. Record an Insight**

```bash
curl -X POST "http://localhost:8000/ledger/insight" \
  -H "Content-Type: application/json" \
  -d '{
    "insight": {
      "insight_type": "decision",
      "content": "Approved user request",
      "source": "auth-service",
      "severity": "info"
    }
  }'
```

**3. Query History**

```bash
curl -X POST "http://localhost:8000/ledger/history" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 10,
    "insight_types": ["decision"]
  }'
```

**4. Verify Integrity**

```bash
curl "http://localhost:8000/ledger/verify"
```

### Quick Start (CLI)

```bash
# Record a decision
python -m modules.insight_ledger.cli record \
  --type decision \
  --content "Approved sensitive data access" \
  --source auth-service \
  --tags "access-control,approval"

# Query recent alerts
python -m modules.insight_ledger.cli query \
  --type alert \
  --limit 50 \
  --format table

# Verify integrity
python -m modules.insight_ledger.cli verify

# Get statistics
python -m modules.insight_ledger.cli stats

# Export for backup
python -m modules.insight_ledger.cli export \
  --output ./backup.json
```

---

## API Reference

### POST /ledger/insight

Record a new insight in the ledger.

**Request:**

```json
{
  "insight": {
    "insight_type": "decision",
    "content": "Approved user access based on policy compliance",
    "context": {"policy": "data-access-v2", "user_id": "usr_123"},
    "source": "aurora-access-control",
    "tags": ["access-control", "policy"],
    "severity": "info",
    "related_anchor": "T1-ACC-003"
  }
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "entry_id": "insight_20250126_120000_000042",
  "entry": {
    "entry_id": "insight_20250126_120000_000042",
    "timestamp": "2025-01-26T12:00:00Z",
    "insight_type": "decision",
    "content": "Approved user access based on policy compliance",
    "context": {"policy": "data-access-v2", "user_id": "usr_123"},
    "source": "aurora-access-control",
    "tags": ["access-control", "policy"],
    "severity": "info",
    "related_anchor": "T1-ACC-003",
    "signature": "a1b2c3d4e5f6...",
    "previous_hash": "9e8f7d6c5b4a...",
    "entry_hash": "1a2b3c4d5e6f..."
  },
  "message": "Insight recorded successfully"
}
```

**Insight Types:**

- `decision` - AI decision with rationale
- `analysis` - Data analysis result
- `recommendation` - System recommendation
- `prediction` - Predictive model output
- `explanation` - Explanation/reasoning
- `audit` - Audit trail entry
- `alert` - System alert or warning
- `metric` - Performance or quality metric

**Severity Levels:**

- `info` - Informational
- `warning` - Warning condition
- `error` - Error occurred
- `critical` - Critical issue

### GET /ledger/verify

Verify the cryptographic integrity of the ledger.

**Query Parameters:**

- `limit` (optional): Maximum entries to verify (default: all)

**Response (200 OK):**

```json
{
  "report": {
    "total_entries": 1250,
    "verified_entries": 1250,
    "failed_entries": [],
    "chain_intact": true,
    "verification_time_ms": 125.4,
    "errors": []
  },
  "summary": "✅ Ledger integrity verified: 1250/1250 entries validated in 125.4ms"
}
```

**Error Response (chain compromised):**

```json
{
  "report": {
    "total_entries": 1250,
    "verified_entries": 1248,
    "failed_entries": ["insight_20250126_150000_000789", "insight_20250126_160000_000823"],
    "chain_intact": false,
    "verification_time_ms": 132.1,
    "errors": [
      "Entry insight_20250126_150000_000789: Invalid signature",
      "Entry insight_20250126_160000_000823: Hash mismatch"
    ]
  },
  "summary": "❌ Integrity compromised: 2 failed entries, 2 errors detected"
}
```

### POST /ledger/history

Query ledger history with flexible filters.

**Request:**

```json
{
  "start_time": "2025-01-01T00:00:00Z",
  "end_time": "2025-01-31T23:59:59Z",
  "insight_types": ["decision", "alert"],
  "sources": ["auth-service", "monitor-service"],
  "tags": ["security", "access-control"],
  "severity": ["warning", "error", "critical"],
  "search_text": "failed login",
  "limit": 100,
  "offset": 0
}
```

**Response (200 OK):**

```json
{
  "entries": [
    {
      "entry_id": "insight_20250115_083045_000456",
      "timestamp": "2025-01-15T08:30:45Z",
      "insight_type": "alert",
      "content": "Failed login attempt detected",
      "source": "auth-service",
      "tags": ["security", "authentication"],
      "severity": "warning",
      "signature": "...",
      "entry_hash": "..."
    }
  ],
  "total_returned": 1,
  "query": { ... }
}
```

### GET /ledger/stats

Get ledger statistics and health metrics.

**Response (200 OK):**

```json
{
  "total_entries": 1250,
  "first_entry_time": "2025-01-01T00:00:00Z",
  "last_entry_time": "2025-01-26T12:00:00Z",
  "entries_by_type": {
    "decision": 450,
    "analysis": 320,
    "alert": 480
  },
  "entries_by_source": {
    "aurora-access-control": 450,
    "resilience-sentinel": 800
  },
  "integrity_verified": true,
  "ledger_size_bytes": 2458000
}
```

### POST /ledger/export

Export complete ledger to JSON file.

**Query Parameters:**

- `output_path` (required): Output file path
- `include_genesis` (optional): Include genesis entry (default: true)

**Response (200 OK):**

```json
{
  "success": true,
  "export_path": "/path/to/export.json",
  "entries_exported": 1250
}
```

### GET /ledger/entry/{entry_id}

Retrieve a specific ledger entry by ID.

**Response (200 OK):**

```json
{
  "entry_id": "insight_20250126_120000_000042",
  "timestamp": "2025-01-26T12:00:00Z",
  "insight_type": "decision",
  "content": "...",
  "signature": "...",
  "entry_hash": "..."
}
```

**Response (404 Not Found):**

```json
{
  "detail": "Entry not found: invalid_id_xyz"
}
```

### GET /ledger/health

Health check endpoint for monitoring.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "ledger_initialized": true,
  "total_entries": 1250,
  "integrity_verified": true,
  "timestamp": "2025-01-26T12:00:00Z"
}
```

---

## CLI Reference

### insight_ledger record

Record a new insight via command line.

**Usage:**

```bash
python -m modules.insight_ledger.cli record \
  --type <INSIGHT_TYPE> \
  --content "<CONTENT>" \
  --source <SOURCE> \
  [--tags <TAG1,TAG2>] \
  [--severity <SEVERITY>] \
  [--context '<JSON>'] \
  [--storage <PATH>]
```

**Examples:**

```bash
# Simple decision
insight_ledger record \
  --type decision \
  --content "Approved data access request" \
  --source auth-service

# Alert with tags and severity
insight_ledger record \
  --type alert \
  --content "Unusual login pattern detected" \
  --source monitor-service \
  --tags "security,authentication" \
  --severity warning

# With JSON context
insight_ledger record \
  --type analysis \
  --content "Performance degradation detected" \
  --source performance-monitor \
  --context '{"cpu_usage": 95, "memory_usage": 88}'
```

### insight_ledger verify

Verify ledger integrity.

**Usage:**

```bash
insight_ledger verify [--limit <N>] [--storage <PATH>]
```

**Examples:**

```bash
# Verify all entries
insight_ledger verify

# Verify last 1000 entries only
insight_ledger verify --limit 1000
```

### insight_ledger query

Query ledger history with filters.

**Usage:**

```bash
insight_ledger query \
  [--type <TYPE>] \
  [--source <SOURCE>] \
  [--tags <TAG1,TAG2>] \
  [--search "<TEXT>"] \
  [--limit <N>] \
  [--format <table|json|csv>] \
  [--storage <PATH>]
```

**Examples:**

```bash
# Query all decisions
insight_ledger query --type decision --limit 50

# Query from specific source
insight_ledger query --source auth-service --format json

# Full-text search
insight_ledger query --search "failed login" --format table

# Multiple filters
insight_ledger query \
  --type alert \
  --tags "security" \
  --limit 100 \
  --format csv > alerts.csv
```

### insight_ledger stats

Get ledger statistics.

**Usage:**

```bash
insight_ledger stats [--storage <PATH>]
```

**Output:**

```
📊 Ledger Statistics

Total Entries:      1250
First Entry:        2025-01-01 00:00:00
Last Entry:         2025-01-26 12:00:00
Integrity Verified: ✅ Yes
Storage Size:       2,458,000 bytes

📈 Entries by Type:
   decision          450
   alert             480
   analysis          320

🔍 Entries by Source:
   aurora-access-control        450
   resilience-sentinel          800
```

### insight_ledger export

Export ledger to JSON file.

**Usage:**

```bash
insight_ledger export \
  --output <PATH> \
  [--no-genesis] \
  [--storage <PATH>]
```

**Examples:**

```bash
# Export all entries
insight_ledger export --output ./backup.json

# Export without genesis
insight_ledger export --output ./export.json --no-genesis
```

---

## Python SDK

### InsightLedger Class

Main interface for ledger operations.

**Initialization:**

```python
from modules.insight_ledger.ledger_core import InsightLedger

ledger = InsightLedger(
    storage_path="./data/ledger",    # Required: storage directory
    secret_key=None,                 # Optional: HMAC key (auto-generated if None)
    auto_checkpoint=1000             # Optional: checkpoint frequency (0=disabled)
)
```

**Methods:**

#### record_insight(insight: InsightRecord) → LedgerEntry

Record a new insight in the ledger.

```python
from modules.insight_ledger.schemas import InsightRecord, InsightType

insight = InsightRecord(
    insight_type=InsightType.DECISION,
    content="Approved request",
    source="my-service"
)

entry = ledger.record_insight(insight)
print(f"Recorded: {entry.entry_id}")
```

#### query_history(query: AuditQuery) → List[LedgerEntry]

Query ledger history with filters.

```python
from modules.insight_ledger.schemas import AuditQuery
from datetime import datetime, timedelta

query = AuditQuery(
    start_time=datetime.now() - timedelta(days=7),
    insight_types=[InsightType.ALERT],
    severity=["warning", "critical"],
    limit=100
)

entries = ledger.query_history(query)
for entry in entries:
    print(f"{entry.timestamp}: {entry.content}")
```

#### verify_integrity(limit: Optional[int]) → Dict[str, Any]

Verify cryptographic integrity.

```python
report = ledger.verify_integrity()

if report["chain_intact"]:
    print("✅ Integrity verified")
else:
    print(f"❌ {len(report['failed_entries'])} failures")
    for error in report["errors"]:
        print(f"  - {error}")
```

#### get_stats() → LedgerStats

Get ledger statistics.

```python
stats = ledger.get_stats()

print(f"Total entries: {stats.total_entries}")
print(f"Integrity: {'✅' if stats.integrity_verified else '❌'}")
print(f"Size: {stats.ledger_size_bytes:,} bytes")

for itype, count in stats.entries_by_type.items():
    print(f"  {itype}: {count}")
```

#### export_ledger(output_path: str, include_genesis: bool) → int

Export ledger to JSON file.

```python
count = ledger.export_ledger(
    output_path="./backup.json",
    include_genesis=True
)

print(f"Exported {count} entries")
```

### InsightRecord Schema

Data model for recording insights.

```python
from modules.insight_ledger.schemas import InsightRecord, InsightType

insight = InsightRecord(
    insight_type=InsightType.DECISION,        # Required
    content="Decision description",            # Required (1-10000 chars)
    source="service-name",                     # Required (1-256 chars)
    
    context={"key": "value"},                  # Optional: metadata dict
    tags=["tag1", "tag2"],                     # Optional: up to 20 tags
    severity="info",                           # Optional: info/warning/error/critical
    related_anchor="T1-ACC-003"                # Optional: Aurora anchor (max 64 chars)
)
```

### AuditQuery Schema

Query parameters for filtering history.

```python
from modules.insight_ledger.schemas import AuditQuery, InsightType
from datetime import datetime, timedelta

query = AuditQuery(
    start_time=datetime(2025, 1, 1),           # Optional: start timestamp
    end_time=datetime(2025, 2, 1),             # Optional: end timestamp
    insight_types=[InsightType.ALERT],         # Optional: filter by types
    sources=["auth-service"],                  # Optional: filter by sources
    tags=["security"],                         # Optional: filter by tags (OR logic)
    severity=["warning", "critical"],          # Optional: filter by severity
    search_text="failed",                      # Optional: full-text search
    limit=100,                                 # Optional: max results (1-10000)
    offset=0                                   # Optional: pagination offset
)
```

---

## Use Cases

### 1. Audit Trail for Access Control

**Scenario:** Record every access decision for compliance.

```python
from modules.insight_ledger import InsightLedger, InsightRecord, InsightType

ledger = InsightLedger("./data/access_ledger")

def log_access_decision(user_id, resource, decision, policy):
    """Log access control decision."""
    insight = InsightRecord(
        insight_type=InsightType.DECISION,
        content=f"{'Approved' if decision else 'Denied'} access to {resource}",
        source="access-control",
        context={
            "user_id": user_id,
            "resource": resource,
            "policy": policy,
            "decision": decision
        },
        tags=["access-control", "compliance"],
        severity="info" if decision else "warning",
        related_anchor="T1-ACC"
    )
    
    entry = ledger.record_insight(insight)
    return entry.entry_id

# Usage
entry_id = log_access_decision(
    user_id="usr_123",
    resource="/api/sensitive-data",
    decision=True,
    policy="data-access-v2"
)
```

### 2. AI Model Prediction Tracking

**Scenario:** Track ML model predictions for reproducibility.

```python
def log_prediction(model_name, input_data, prediction, confidence):
    """Log ML model prediction."""
    insight = InsightRecord(
        insight_type=InsightType.PREDICTION,
        content=f"Model {model_name} predicted: {prediction}",
        source="ml-inference-service",
        context={
            "model": model_name,
            "input": input_data,
            "prediction": prediction,
            "confidence": confidence
        },
        tags=["ml", "prediction", model_name],
        severity="info",
        related_anchor="T1-ML"
    )
    
    ledger.record_insight(insight)

# Usage
log_prediction(
    model_name="fraud-detector-v2",
    input_data={"transaction_amount": 5000, "location": "US"},
    prediction="legitimate",
    confidence=0.95
)
```

### 3. Security Event Monitoring

**Scenario:** Log security alerts with automatic integrity checks.

```python
def log_security_event(event_type, description, severity="warning"):
    """Log security event."""
    insight = InsightRecord(
        insight_type=InsightType.ALERT,
        content=description,
        source="security-monitor",
        context={"event_type": event_type},
        tags=["security", event_type],
        severity=severity,
        related_anchor="T1-SEC"
    )
    
    ledger.record_insight(insight)
    
    # Verify integrity after critical events
    if severity == "critical":
        report = ledger.verify_integrity(limit=100)
        if not report["chain_intact"]:
            send_alert("Ledger integrity compromised!")

# Usage
log_security_event(
    event_type="brute_force",
    description="Multiple failed login attempts from IP 192.168.1.100",
    severity="critical"
)
```

### 4. Data Provenance Tracking

**Scenario:** Track data transformations for lineage.

```python
def log_data_transformation(input_id, output_id, operation, metadata):
    """Log data transformation for provenance."""
    insight = InsightRecord(
        insight_type=InsightType.AUDIT,
        content=f"Data transformation: {operation}",
        source="data-pipeline",
        context={
            "input_id": input_id,
            "output_id": output_id,
            "operation": operation,
            "metadata": metadata
        },
        tags=["data-provenance", "transformation"],
        severity="info"
    )
    
    return ledger.record_insight(insight)

# Usage
log_data_transformation(
    input_id="raw_data_001",
    output_id="clean_data_001",
    operation="anonymization",
    metadata={"pii_fields_removed": ["email", "phone"]}
)
```

### 5. Compliance Reporting

**Scenario:** Generate compliance reports from ledger.

```python
from datetime import datetime, timedelta

def generate_compliance_report(start_date, end_date):
    """Generate compliance report for date range."""
    query = AuditQuery(
        start_time=start_date,
        end_time=end_date,
        insight_types=[InsightType.DECISION, InsightType.AUDIT]
    )
    
    entries = ledger.query_history(query)
    
    # Analyze entries
    total_decisions = len([e for e in entries if e.insight_type == InsightType.DECISION])
    total_audits = len([e for e in entries if e.insight_type == InsightType.AUDIT])
    
    # Verify integrity
    report = ledger.verify_integrity()
    
    return {
        "period": f"{start_date} to {end_date}",
        "total_decisions": total_decisions,
        "total_audits": total_audits,
        "integrity_verified": report["chain_intact"],
        "entries": entries
    }

# Usage
report = generate_compliance_report(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)

print(f"Compliance Report: {report['period']}")
print(f"Decisions: {report['total_decisions']}")
print(f"Integrity: {'✅' if report['integrity_verified'] else '❌'}")
```

---

## Best Practices

### 1. Consistent Insight Types

Use consistent insight types across your system:

```python
# ✅ Good: Consistent types
InsightType.DECISION  # For access control, approvals
InsightType.ALERT     # For security events, anomalies
InsightType.ANALYSIS  # For data analysis results
InsightType.METRIC    # For performance metrics

# ❌ Bad: Mixing types inconsistently
InsightType.DECISION  # Used for both access control AND analysis
```

### 2. Meaningful Content

Write clear, actionable content:

```python
# ✅ Good: Clear and specific
content = "Approved data access for user usr_123 to dataset DS_456 based on policy P2"

# ❌ Bad: Vague
content = "Access granted"
```

### 3. Rich Context

Include relevant metadata in context:

```python
# ✅ Good: Comprehensive context
context = {
    "user_id": "usr_123",
    "dataset_id": "DS_456",
    "policy_id": "P2",
    "timestamp_ms": 1706270400000,
    "ip_address": "192.168.1.100"
}

# ❌ Bad: Missing context
context = {"user_id": "usr_123"}
```

### 4. Appropriate Tags

Use tags for classification and filtering:

```python
# ✅ Good: Specific, hierarchical tags
tags = ["access-control", "sensitive-data", "compliance", "gdpr"]

# ❌ Bad: Generic or redundant tags
tags = ["event", "log", "thing"]
```

### 5. Regular Integrity Checks

Schedule periodic verification:

```python
import schedule

def verify_daily():
    """Daily integrity check."""
    report = ledger.verify_integrity()
    
    if not report["chain_intact"]:
        send_alert("Ledger integrity compromised!")
        log_to_external_system(report)
    else:
        print(f"✅ Verified {report['verified_entries']} entries")

# Run every day at 3 AM
schedule.every().day.at("03:00").do(verify_daily)
```

### 6. Backup Strategy

Implement regular backups:

```bash
#!/bin/bash
# Daily backup script

DATE=$(date +%Y%m%d)
BACKUP_DIR="./backups/ledger"
mkdir -p $BACKUP_DIR

# Export ledger
insight_ledger export --output "$BACKUP_DIR/ledger_$DATE.json"

# Verify export
if [ $? -eq 0 ]; then
    echo "✅ Backup created: ledger_$DATE.json"
    
    # Compress old backups (keep 7 days)
    find $BACKUP_DIR -name "*.json" -mtime +7 -exec gzip {} \;
    
    # Delete very old backups (keep 90 days)
    find $BACKUP_DIR -name "*.json.gz" -mtime +90 -delete
else
    echo "❌ Backup failed!"
    exit 1
fi
```

### 7. Error Handling

Handle errors gracefully:

```python
def safe_record_insight(insight_data):
    """Record insight with error handling."""
    try:
        insight = InsightRecord(**insight_data)
        entry = ledger.record_insight(insight)
        return {"success": True, "entry_id": entry.entry_id}
        
    except ValidationError as e:
        # Handle schema validation errors
        logger.error(f"Invalid insight data: {e}")
        return {"success": False, "error": "validation_error", "details": str(e)}
        
    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Failed to record insight: {e}")
        return {"success": False, "error": "internal_error"}
```

### 8. Performance Optimization

For high-throughput scenarios:

```python
# Batch processing with threading
import threading
from queue import Queue

insight_queue = Queue()

def insight_worker():
    """Worker thread for recording insights."""
    while True:
        insight = insight_queue.get()
        if insight is None:
            break
        try:
            ledger.record_insight(insight)
        except Exception as e:
            logger.error(f"Failed to record: {e}")
        finally:
            insight_queue.task_done()

# Start worker threads
for _ in range(4):
    t = threading.Thread(target=insight_worker, daemon=True)
    t.start()

# Enqueue insights
insight_queue.put(my_insight)
```

---

## Troubleshooting

### Common Issues

#### Issue: "Ledger not initialized"

**Error:**
```
HTTPException: 503 Service Unavailable
Detail: Ledger not initialized. Configure storage path first.
```

**Solution:**
```python
# Initialize ledger before use
from modules.insight_ledger.api import initialize_ledger

initialize_ledger(storage_path="./data/insight_ledger")
```

#### Issue: Integrity verification fails

**Error:**
```
❌ Integrity compromised!
Entry insight_20250126_120000_000789: Invalid signature
```

**Possible Causes:**
1. Entry was manually modified
2. Secret key changed/lost
3. File corruption
4. Malicious tampering

**Solutions:**

```bash
# 1. Check specific failed entry
insight_ledger query --search "000789" --format json

# 2. Restore from backup
cp ./backups/ledger_latest.json ./data/insight_ledger/

# 3. If corruption is localized, export clean entries
# (Requires manual intervention - contact administrator)
```

#### Issue: Performance degradation

**Symptom:** Slow queries on large ledgers (10,000+ entries)

**Solutions:**

```python
# 1. Use pagination
query = AuditQuery(limit=100, offset=0)  # First page
entries_page1 = ledger.query_history(query)

query.offset = 100  # Next page
entries_page2 = ledger.query_history(query)

# 2. Filter aggressively
query = AuditQuery(
    start_time=datetime.now() - timedelta(days=7),  # Recent only
    sources=["specific-service"],  # Specific source
    limit=100
)

# 3. Use auto-checkpointing
ledger = InsightLedger(
    storage_path="./data/ledger",
    auto_checkpoint=1000  # Checkpoint every 1000 entries
)
```

#### Issue: Storage space concerns

**Problem:** Ledger files growing large

**Solutions:**

```bash
# 1. Export and archive old entries
insight_ledger export --output ./archive/2024.json
# (Then manually remove old entries if needed - requires new ledger)

# 2. Compress old backups
gzip ./backups/ledger_*.json

# 3. Monitor storage
du -h ./data/insight_ledger/
```

#### Issue: Secret key lost

**Problem:** `ledger.key` file deleted or corrupted

**Impact:** Cannot verify existing signatures, but can still create new entries

**Solutions:**

```python
# Option 1: Restore from backup
cp ./backups/ledger.key ./data/insight_ledger/

# Option 2: Start new ledger (loses verification capability for old entries)
# Create new storage directory
ledger_new = InsightLedger(storage_path="./data/ledger_new")
```

---

## Performance

### Benchmarks

**Test Environment:**
- Python 3.12
- SSD storage
- 16GB RAM
- 4 CPU cores

**Results:**

| Operation | Entries | Time | Throughput |
|-----------|---------|------|------------|
| Record insight | 1,000 | 0.8s | 1,250 insights/sec |
| Record insight | 10,000 | 8.1s | 1,234 insights/sec |
| Verify integrity | 1,000 | 0.12s | 8,333 entries/sec |
| Verify integrity | 10,000 | 1.2s | 8,333 entries/sec |
| Query (no filter) | 1,000 | 0.05s | 20,000 entries/sec |
| Query (filtered) | 1,000 | 0.08s | 12,500 entries/sec |
| Export | 10,000 | 1.5s | 6,666 entries/sec |

### Scalability

**Storage Requirements:**

- Average entry size: ~800 bytes
- 10,000 entries: ~8 MB
- 100,000 entries: ~80 MB
- 1,000,000 entries: ~800 MB

**Memory Usage:**

- Base: ~50 MB (ledger instance)
- Per query result: ~1KB per entry
- Verification: ~100 MB (10,000 entries)

### Optimization Tips

**1. Batch Operations**

```python
# Process multiple insights together
insights = [create_insight(i) for i in range(100)]

for insight in insights:
    ledger.record_insight(insight)  # Still atomic
```

**2. Limit Verification Scope**

```python
# Verify recent entries only
report = ledger.verify_integrity(limit=1000)  # Last 1000 entries
```

**3. Use Checkpoints**

```python
# Enable auto-checkpointing
ledger = InsightLedger(
    storage_path="./data/ledger",
    auto_checkpoint=1000  # Checkpoint every 1000 entries
)
```

**4. Optimize Queries**

```python
# Use specific filters
query = AuditQuery(
    start_time=recent_time,      # Narrow time range
    sources=["specific-source"],  # Single source
    limit=100                     # Reasonable limit
)
```

---

## Integration Guide

### Integrating with Aurora API

The Insight Ledger is automatically integrated with Aurora CloudBank's API:

```python
# In aurora_api.py (already configured)
from modules.insight_ledger.api import initialize_ledger, router

# Initialize ledger
initialize_ledger(storage_path="./data/insight_ledger")

# Include router
app.include_router(router)
```

### Integrating with Custom Services

**FastAPI Integration:**

```python
from fastapi import FastAPI
from modules.insight_ledger.api import initialize_ledger, router

app = FastAPI()

# Initialize ledger on startup
@app.on_event("startup")
async def startup_event():
    initialize_ledger(storage_path="./data/my_ledger")

# Include ledger routes
app.include_router(router, prefix="/api", tags=["audit"])
```

**Flask Integration:**

```python
from flask import Flask, request, jsonify
from modules.insight_ledger import InsightLedger, InsightRecord

app = Flask(__name__)
ledger = InsightLedger(storage_path="./data/ledger")

@app.route("/audit/record", methods=["POST"])
def record_audit():
    data = request.json
    insight = InsightRecord(**data)
    entry = ledger.record_insight(insight)
    return jsonify({"entry_id": entry.entry_id})
```

### DLP Integration

Automatic DLP tracking for ledger operations:

```python
from modules.insight_ledger.dlp_integration import initialize_dlp_integration
from src.core.native_dlp_export import NativeDLPTracker

# Initialize DLP tracker
dlp_tracker = NativeDLPTracker()

# Initialize DLP integration
dlp_integration = initialize_dlp_integration(dlp_tracker)

# Now ledger operations are automatically tracked in DLP
insight = InsightRecord(...)
entry = ledger.record_insight(insight)
# → DLP record created automatically
```

### Webhook Integration

Send webhooks on critical events:

```python
import requests

def send_webhook(event_type, data):
    """Send webhook notification."""
    requests.post(
        "https://my-webhook-endpoint.com/notify",
        json={"event": event_type, "data": data}
    )

# Custom ledger wrapper
class WebhookLedger:
    def __init__(self, ledger):
        self.ledger = ledger
    
    def record_insight(self, insight):
        entry = self.ledger.record_insight(insight)
        
        # Send webhook for critical insights
        if insight.severity == "critical":
            send_webhook("critical_insight", {
                "entry_id": entry.entry_id,
                "content": insight.content
            })
        
        return entry

# Usage
webhook_ledger = WebhookLedger(ledger)
```

---

## Conclusion

The **Trustworthy Insight Ledger** provides Aurora CloudBank with a production-ready, cryptographically-secured audit trail for AI operations. With its append-only architecture, HMAC signatures, and hash chain integrity, it ensures **transparency**, **accountability**, and **verifiability** for all AI insights and decisions.

**Key Takeaways:**

✅ **Immutable**: Append-only storage prevents tampering  
✅ **Verifiable**: Cryptographic signatures + hash chains  
✅ **Flexible**: REST API, Python SDK, and CLI  
✅ **Performant**: 1,000+ insights/sec, sub-second queries  
✅ **Production-Ready**: 40+ tests, comprehensive error handling  

**Next Steps:**

1. Review [API Reference](#api-reference) for endpoint details
2. Explore [Use Cases](#use-cases) for implementation patterns
3. Follow [Best Practices](#best-practices) for optimal usage
4. Set up [regular backups](#6-backup-strategy) and [integrity checks](#5-regular-integrity-checks)

**Support:**

- Documentation: `docs/ledger/LEDGER_GUIDE.md`
- Source Code: `modules/insight_ledger/`
- Tests: `tests/test_insight_ledger.py`
- Anchor: T1-TIL (Trustworthy Insight Ledger)

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-26  
**Anchor:** T1-TIL-005  
**Status:** ✅ Production Ready
