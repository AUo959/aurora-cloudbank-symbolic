# Walkthrough — one request, end to end

This traces a single `POST /memory/create` through every layer it touches:
ten middlewares, two independent CSRF checks, the memory tier, and the
observability surface that records it.

Every request, response, header and status code below was produced by running
the commands against a local server. Where a layer did something surprising,
that is noted rather than tidied away.

**Follow along:**

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # or export the four keys directly
make serve-dev                 # http://localhost:8000
```

---

## The middleware stack

Starlette's `add_middleware` prepends, so **registration order is the reverse of
execution order**. Reading `api/aurora_api.py` top to bottom gives you the
inside-out view. The actual order, outermost first:

```
  request
    │
 1. r2_telemetry_middleware        trace capture (@app.middleware decorator)
 2. telemetry_middleware           operation + feature counters
 3. rate_limit_header_middleware   X-RateLimit-* response headers
 4. MetricsMiddleware              Prometheus timing
 5. RequestIDMiddleware            assigns/propagates X-Request-ID
 6. PIIMiddleware                  scrubs PII from what gets logged
 7. GlobalCsrfMiddleware           rejects unsafe methods without a token
 8. IdempotencyMiddleware          replays a prior response for a repeated key
 9. MaxBodySizeMiddleware          413s over 10 MiB (AURORA_MAX_BODY_BYTES)
10. SlowAPIMiddleware              per-IP rate limiting
    │
    ▼
  route handler
```

Verify it yourself rather than trusting the list:

```python
import api.aurora_api as a
for i, m in enumerate(a.app.user_middleware, 1):
    print(i, m.cls.__name__)
```

---

## Step 1 — Get a CSRF token

Every state-changing request needs one. `GET /api/csrf-token` is on the
middleware allowlist, so it is reachable without one:

```bash
curl -s localhost:8000/api/csrf-token
```

```json
{
  "csrf_token": "iEZKpa1z9ACvAQCrEaaEEg.1784935162.62c69fb5caf7...",
  "session_id": "iEZKpa1z9ACvAQCrEaaEEg",
  "header": "X-CSRF-Token",
  "expires_in_seconds": 300
}
```

The token is `session_id.timestamp.hmac`, signed with `CSRF_SECRET_KEY`. It is
stateless — the server stores nothing and re-derives the HMAC on the way back
in.

> **Honest note.** Because the token is not bound to a cookie or an
> authenticated session, it defends against blind cross-origin submission but
> is only as strong as the CORS policy in front of it. Keep
> `ALLOWED_CORS_ORIGINS` restrictive anywhere this matters.

---

## Step 2 — Write a memory

```bash
TOKEN=$(curl -s localhost:8000/api/csrf-token | jq -r .csrf_token)

curl -i -X POST localhost:8000/memory/create \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"walkthrough trace","memory_type":"agent",
       "owner":"reviewer","importance":2.0}'
```

```http
HTTP/1.1 200 OK
content-type: application/json
x-request-id: d9651e72-5bd2-44b3-9915-49853b1d5dcd

{"memory_id":"770c4882-442d-4e9b-b8cf-1b6af43773b9","status":"created",
 "message":"Memory created successfully with ID: 770c4882-..."}
```

### Why two headers?

`X-CSRF-Token` and `Authorization: Bearer` carry **the same token** because
there are two independent CSRF checks, and they disagree about transport:

| Check | Where | Reads |
|---|---|---|
| `GlobalCsrfMiddleware` | every unsafe method, all non-allowlisted paths | `X-CSRF-Token` header |
| `require_csrf_token` dependency | per-route, e.g. `SENSITIVE_MEMORY_DEPENDENCIES` | `Authorization: Bearer` |

Routes carrying both need both headers. This is a wart, not a design — it is
recorded here rather than hidden, because a reader who sends only one gets a
403 with no indication that a second check exists.

### What the tier did with it

`memory_type` must be one of ten canonical values — `agent`, `faction`,
`narrative`, `quantum_symbolic`, `vector_state`, `flight_control`,
`aurora_symbolic`, `cask_cultural`, `t1_anchor`, `srb_boundary`. These are
domain primitives, not generic labels; see
[`docs/archive/philosophy/02_SYMBOLIC_ARCHITECTURE.md`](archive/philosophy/02_SYMBOLIC_ARCHITECTURE.md).

Read it back:

```bash
curl -s -X POST localhost:8000/memory/retrieve \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"walkthrough","top_k":1}'
```

```json
[{
  "id": "770c4882-442d-4e9b-b8cf-1b6af43773b9",
  "content": "walkthrough trace",
  "memory_type": "agent",
  "owner": "reviewer",
  "importance": 2.0,
  "strength": 1.0,
  "access_count": 1,
  "status": "active",
  "symbolic_anchors": [],
  "cask_cultural_score": 0.0,
  "quantum_vector": null
}]
```

The tier attached `strength`, `access_count` and `status` on its own.
`access_count` is already `1` — the retrieval itself counted. Memories move
`active → compressed → archived` as strength decays; this one is in the active
tier.

`symbolic_anchors` and `quantum_vector` are empty because none were supplied.
They populate when a request provides `aurora_anchors` or `quantum_properties`.

---

## Step 3 — The gates, doing their job

Each of these was run against the same server:

```bash
# no CSRF token
curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8000/memory/create \
  -H "Content-Type: application/json" \
  -d '{"content":"x","memory_type":"agent","owner":"r"}'
# -> 403   GlobalCsrfMiddleware, before routing

# invalid memory_type
... -d '{"content":"x","memory_type":"nonsense","owner":"r"}'
# -> 400   handler, after validation

# 11 MiB body
... --data-binary @big.json
# -> 413   MaxBodySizeMiddleware, on declared Content-Length
```

| Sent | Status | Rejected by |
|---|---|---|
| No CSRF token | **403** | `GlobalCsrfMiddleware` |
| Malformed token | **403** | `GlobalCsrfMiddleware` |
| Valid token, bad `memory_type` | **400** | route handler |
| Valid token, 11 MiB body | **413** | `MaxBodySizeMiddleware` |
| Valid token, valid body | **200** | — |

The 400 is worth noting. Until recently it was a 500: every route wrapped its
body in `except Exception` with no `HTTPException` guard, so intentional 4xx
were re-raised as server errors. A gate that reports the wrong status is worse
than one that reports nothing, because it sends the reader looking for a bug on
the wrong side of the wire.

---

## Step 4 — The ethics gate

Memory writes are not ethics-gated. The gate is its own endpoint, evaluated for
actions that need it:

```bash
curl -s -X POST localhost:8000/gumas/evaluate \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" -H "Authorization: Bearer $TOKEN" \
  -d '{"agent_id":"reviewer","action_type":"observe_and_learn",
       "context_tag":"walkthrough"}'
```

```json
{
  "compliant": true,
  "should_block": false,
  "violations": [],
  "evaluation_timestamp": "2026-07-25T05:12:04.274774+00:00",
  "context_tag": "walkthrough"
}
```

`should_block` is separate from `compliant` on purpose: an action can be
non-compliant and still permitted at a lower resistance level. The five-
dimension geometric model behind it is in
[`docs/GEOMETRIC_ETHICS_ARCHITECTURE.md`](GEOMETRIC_ETHICS_ARCHITECTURE.md); the
reasoning for gating this way at all is in
[`04_ETHICS_PROTOCOL.md`](archive/philosophy/04_ETHICS_PROTOCOL.md).

`context_tag` echoes back. It is the DLP thread — the same tag ties a request
to its audit entries.

---

## Step 5 — What observability recorded

The write left traces without being asked to:

```bash
curl -s localhost:8000/metrics | grep -E "POST_memory_create|memory_api"
```

```
aurora_operations_total{operation="POST_memory_create"} 1
aurora_feature_usage_total{feature="memory_api"} 1
```

Two different questions: `aurora_operations_total` counts HTTP calls,
`aurora_feature_usage_total` counts *capability* use. A single feature can be
reached by several routes, so the counts diverge — deliberately.

Tier state also moved:

```bash
curl -s localhost:8000/memory/metrics
```

```json
{"total_memories": 1, "active_memories": 1, "compressed_memories": 0,
 "archived_memories": 0, "quantum_vectors": 0, ...}
```

And `x-request-id` on the response is the correlation key: `RequestIDMiddleware`
assigns one if the client did not send it, and it appears on log lines for the
request. Send your own to trace a call across services.

---

## What this does not show

- **Persistence.** `HierarchicalMemoryManager` accepts a `persist_path`, but
  `api_integration.py` instantiates it with only `max_active_memories=1000`.
  So the default server holds memories in process: restart it and the count
  returns to zero. The capability exists; this configuration does not use it.
- **Authentication.** `/api/auth/` only registers when auth users are
  configured (`AURORA_AUTH_USERS_JSON` / `AURORA_AUTH_USERS_FILE`); a default
  local run starts without it and logs the reason. The `Authorization` header
  above carries a CSRF token, not a JWT.
- **Rate limiting under load.** `SlowAPIMiddleware` is active but a handful of
  curls will not reach the limit.
- **The audit chain.** `src/monitoring/audit_logger.py` maintains a
  hash-linked, tamper-evident log, but memory writes do not currently feed it.
  See [`VERIFIED_CLAIMS.md`](VERIFIED_CLAIMS.md) for a runnable demonstration
  that altering an entry breaks verification.

---

## Where to go next

| You want | Read |
|---|---|
| The layer model (L1/L2/L3) and code map | [`ARCHITECTURE_QUICKMAP.md`](../ARCHITECTURE_QUICKMAP.md) |
| Whether a claim is true | [`VERIFIED_CLAIMS.md`](VERIFIED_CLAIMS.md) |
| Why it is built this way | [`archive/philosophy/PHILOSOPHY.md`](archive/philosophy/PHILOSOPHY.md) |
| Every documentation directory and its authority | [`index.md`](index.md) |
| The full route listing | [`reference/API_CATALOG.md`](reference/API_CATALOG.md) |

---

*Traced against `main`. If a command here does not produce the stated result,
that is a bug in this document — please open an issue.*
