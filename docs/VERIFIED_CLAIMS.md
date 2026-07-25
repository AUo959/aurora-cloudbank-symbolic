# Verified Claims

Every claim this repository makes about itself should be checkable by someone
who does not trust it. This document pairs each claim with the command that
proves or falsifies it, and the result that command produced.

This follows the standard the design philosophy sets for the system's own
outputs — *"only outputs that can be proven wrong are outputs that can be
proven right"* ([05_GANDALF_STANDARD.md](archive/philosophy/05_GANDALF_STANDARD.md)).
It applies the same rule to the documentation.

**Setup for everything below:**

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install pytest pytest-asyncio pytest-timeout

# The app refuses to start without these four. Generate throwaway ones:
export AURORA_SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export CSRF_SECRET_KEY=$(openssl rand -hex 32)
export WS_AUTH_SECRET=$(openssl rand -hex 32)
```

Measured on Python 3.12, `requirements.txt` only, no optional extras, no
external services.

---

## The system installs and starts

```bash
python -c "import time,sys; sys.path.insert(0,'.'); t=time.time(); import api.aurora_api; print(f'{time.time()-t:.1f}s')"

python -c "import sys; sys.path.insert(0,'.'); import api.aurora_api as a; s=a.app.openapi(); print(len(s['paths']),'paths', sum(len(v) for v in s['paths'].values()),'operations')"
```

Observed: **1.7 s**, **282 paths / 290 operations / 30 tags**.

**The count depends on your configuration, and this is worth knowing before you
compare notes with anyone.** Route registration is tolerant by design — modules
whose optional dependencies are absent are skipped and logged rather than
aborting boot. With a `.env` file present and optional extras installed the same
command reports **294 paths / 302 operations**. The 282/290 figure is the floor
for a minimal install, not a ceiling.

---

## The test suite

```bash
pytest -q
```

Observed on a clean clone with core requirements only:

| | count |
|---|---|
| passed | **3,008** |
| failed | 36 |
| errors | 27 |
| skipped | 123 |
| duration | ~5 min 30 s |

The 36 failures and 27 errors are **environmental, not logic**, and are honest
about it — a hardcoded `/var/lib/nemo_snapshots` path, absent Redis, and
unconfigured auth users account for most of them. They are listed here rather
than hidden because a reader will hit them, and discovering them unannounced is
worse than being told.

Fast path: `pytest -m unit`.

---

## Tamper-evident audit log

**Claim:** altering any recorded field in an audit entry breaks verification.

```bash
pytest tests/test_audit_logger_security.py -q    # 4 passed
```

To see it directly rather than trusting the suite:

```python
from src.monitoring.audit_logger import AuditLogger
lg = AuditLogger(signing_key="demo-key")
for i in range(4):
    lg.log_drift_alert(agent_id=f"a{i}", severity="WARNING",
                       metric_name=f"m{i}", current_value=0.5+i, baseline_value=0.4)

print(lg.verify_chain())                       # True
entry = lg.entries[1]
entry.data = dict(entry.data, current_value=999.0)   # alter a recorded fact
print(lg.verify_entry(entry), lg.verify_chain())     # False False
```

Observed: clean chain verifies; altering either `data` or `severity` on any
entry flips both `verify_entry()` and `verify_chain()` to `False`. SHA-256 over
the entry content with `previous_hash` linkage
(`src/monitoring/audit_logger.py`).

---

## PII detection and redaction

**Claim:** PII is detected and masked before it reaches a log or a response.

```bash
pytest tests/test_data_guardian.py tests/test_persist_redact.py -q    # 34 passed
```

```python
from modules.data_guardian.detection_rules import PIIDetector
from modules.data_guardian.redaction import RedactionEngine

sample = "Contact john.doe@example.com or call 555-123-4567. SSN 123-45-6789, card 4111-1111-1111-1111"
hits = PIIDetector().detect(sample)          # list of dicts: type, start, end
print(RedactionEngine().redact_text(sample, hits))
```

Observed:

```
Contact ********@*******.*** or call ************. SSN ***********, card *******************
```

**Scope, stated honestly:** `PIIType` declares 12 categories; **6 have
detection rules** — email, SSN, phone, credit card, IP address, date of birth.
Driver's licence, passport, bank account, full name, address and custom are
declared but not implemented. There is no credential or secret detection: an
AWS key passes through unredacted.

---

## Log-injection resistance

**Claim:** user input cannot forge log lines.

```bash
pytest tests/test_log_sanitizer.py -q    # 14 passed
```

```python
from modules.data_guardian.log_sanitizer import sanitize_log_output
print(repr(sanitize_log_output("user=bob\n2026-01-01 ADMIN forged entry")))
```

Observed: `'user=bob\\n2026-01-01 ADMIN forged entry'` — newlines become literal
escapes, so the line cannot be split. Also strips C0/C1 control characters and
truncates at 4096 chars. This is an **injection** guard, not a PII redactor;
the two are separate concerns handled by separate code.

---

## CSRF enforcement

**Claim:** state-changing requests without a valid token are rejected.

```bash
make serve-dev          # in another terminal
TOKEN=$(curl -s localhost:8000/api/csrf-token | jq -r .csrf_token)

# no token
curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/memory/create \
  -H "Content-Type: application/json" \
  -d '{"content":"x","memory_type":"agent","owner":"you"}'

# malformed token
curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/memory/create \
  -H "Content-Type: application/json" -H "X-CSRF-Token: not.a.token" \
  -d '{"content":"x","memory_type":"agent","owner":"you"}'

# valid token
curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/memory/create \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"x","memory_type":"agent","owner":"you"}'
```

Observed: **403**, **403**, **200**.

**Threat model, stated honestly:** the token is a stateless HMAC and is not
bound to a cookie or authenticated session by default. It defends against blind
cross-origin submission, but its strength depends on the CORS policy in front
of it. Keep `ALLOWED_CORS_ORIGINS` restrictive anywhere this matters.

---

## Pilot seal (MCP elevated access)

**Claim:** elevated connector operations require an unforgeable, expiring seal.

```bash
pytest tests/connector/test_auth_token.py tests/connector/test_hmac_seal.py -q
```

Observed: **26 passed**. The suite asserts that a forged scope, an extended
expiry, a seal signed with a different secret, an expired seal, and the
pre-#822 substring-style seal are all rejected.

---

## Deterministic simulation

**Claim:** the same seed produces the same run; a different seed does not.

```bash
# use `md5` instead of `md5sum` on macOS
sim() { python simulation/orion_station_simulation.py --seed "$1" --ticks 30 --log-level WARNING | md5sum; }

a=$(sim 42); b=$(sim 42); c=$(sim 43)
[ "$a" = "$b" ]  && echo "deterministic:  yes"
[ "$a" != "$c" ] && echo "seed-sensitive: yes"
```

Observed: identical digests across runs at seed 42; different digest at seed 43.

There is **no automated test asserting this** — it is verified by the command
above only. Adding one is open work.

---

## MCP connector

**Claim:** Aurora state is exposed over the Model Context Protocol as five
read-only tools.

```bash
pip install -r requirements-optional.txt
python -c "from connector.tools import TOOL_REGISTRY; print(len(TOOL_REGISTRY), sorted(TOOL_REGISTRY))"
python -m connector.server --help
```

Observed: **5** — `aurora_get_agents`, `aurora_get_capsules`, `aurora_get_drift`,
`aurora_get_ethics_log`, `aurora_get_state`.

Offline connector tests run with no configuration:

```bash
pytest tests/connector -q      # 35 passed, 79 skipped
```

The 79 skipped are integration tests needing `AURORA_CONNECTOR_TOKEN` and a
running API; they announce that rather than failing silently. See
[`tests/connector/conftest.py`](../tests/connector/conftest.py).

---

## Scale

| Measure | Value | Check |
|---|---|---|
| Test files | 293 | `git ls-files 'tests/**test_*.py' 'tests/test_*.py' \| wc -l` |
| Test lines | 64,389 | `git ls-files tests \| grep '\.py$' \| xargs wc -l \| tail -1` |
| Source lines (api+src+modules) | 145,391 | `git ls-files api src modules \| grep '\.py$' \| xargs wc -l \| tail -1` |
| Middleware modules | 12 | `ls src/middleware/*.py \| wc -l` |

Test-to-source ratio is roughly **1:2.3** (64,389 / 145,391).

---

## What is not claimed

Stated so nobody has to discover it by reading code:

- **Quantum cloud backends** (AWS Braket, Azure Quantum, IBM, Cirq) require
  provider accounts and fall back to local simulation. The local
  `quantum_state.py` `apply_gate()` is explicitly a mock and says so in its
  own source.
- **HALO/PAS drift control** is a working runtime class; the end-to-end L1–L2
  wiring that would feed it live signals is not shipped.
- **Recovered protocol custody** — the manifest schema exists, but all five
  protocols' custody hashes are still `PENDING` (tracked in #1233).
- **Connector v0.2 write operations and v0.3 streaming** are planned, not
  built. `connector/README.md` marks them as such.

---

*Reproduced against `main`. If a command here does not produce the stated
result, that is a bug in this document — please open an issue.*
