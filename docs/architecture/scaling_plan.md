# Aurora CloudBank Scaling Plan

**Status:** Architecture plan
**Last reviewed:** 2026-06-02
**Scope:** Horizontal and multi-region scaling for the CloudBank API and adjacent runtime services

This plan extends the current single-worker safety posture into a staged path
for horizontal and multi-region operation. It does not declare the current
runtime safe for active-active scaling. Kubernetes replica counts and HPA
manifests provide pod mechanics; they are not sufficient proof that stateful
CloudBank modules can run concurrently without externalized state, write
ordering, and failover controls.

## Current Posture

| Surface | Current evidence | Scaling implication |
| --- | --- | --- |
| Primary API | `api/aurora_api.py` is the FastAPI aggregation point for active and active-optional routers. | API pods can only scale safely for routes whose state is externalized or read-only. |
| GUI CloudHub Kubernetes deployment | `k8s/aurora-gui-cloudhub-deployment.yaml` sets 3 replicas and `k8s/aurora-hpa-monitoring.yaml` defines an HPA range of 3-20 pods. | Useful for stateless request handling after state externalization; not a complete state-safety guarantee. |
| GUI CloudHub service | `k8s/aurora-gui-cloudhub-service.yaml` uses `sessionAffinity: ClientIP`. | Sticky sessions can reduce churn but must not be the data-consistency mechanism. |
| Draft CloudBank deployment | `k8s/deployment/aurora-cloudbank.yml` is explicitly marked draft and not for production. | Do not use it as production scaling evidence. |
| NeMo GPU service | `k8s/aurora-nemo-deployment.yaml` uses `replicas: 1` and `strategy: Recreate`. | GPU inference scaling needs a queue and GPU-node capacity model, not blind HPA. |
| Rate limiting | `src/middleware/fastapi_security.py` can use `REDIS_URL`; `docs/Rate-Limiting.md` recommends Redis for distributed environments. | Multi-replica API deployments must use Redis-backed limits before production traffic. |
| Playground sessions | `src/playground/storage.py` uses Redis when available and falls back to in-memory storage. | Production replicas must make Redis required instead of silently falling back. |
| AuMemManager | `modules/aumemmanager/api_integration.py` creates a module-level `HierarchicalMemoryManager`; the manager stores memory in process dictionaries. | Memory writes are pod-local today and must be moved behind a durable backend before multi-writer scale. |
| Insight Ledger | `modules/insight_ledger/api.py` keeps a module-level ledger instance; `api/aurora_api.py` initializes `./data/insight_ledger`. | Ledger writes need a single-writer service, durable append log, or transactional backend before concurrent pods write to it. |
| Auth and logout | `src/security/auth_routes.py` documents logout as client-side; `docs/RBAC_SECURITY_SUMMARY.md` lists database-backed users and Redis token blacklist as future work. | Users, refresh state, revocation, and session tracking need shared storage before HA auth claims. |
| Mesh and audit records | `src/mesh/runtime.py` uses SQLite and JSONL transcripts; monitoring/audit components write JSONL files. | Event and audit surfaces need shared databases, object storage, or log pipelines before cross-pod and cross-region operation. |

## Target Architecture

The target production shape is a stateless API tier backed by explicit shared
state services:

- API pods: horizontally scalable FastAPI workers with no required local
  mutable state for production request handling.
- Redis: distributed rate limits, short-lived sessions, token revocation,
  streaming coordination, and cache invalidation.
- PostgreSQL or compatible relational store: users, RBAC assignments, durable
  session metadata, coordination indexes, idempotency keys, and operational
  state that requires transactions.
- Durable ledger backend: append-only writer service or transactional store
  with explicit write ordering and integrity verification.
- Memory backend: persistent/vector storage for AuMemManager memory tiers,
  plus Redis or equivalent for hot retrieval caches.
- Event bus: NATS, Kafka, Redis Streams, or equivalent for mesh events,
  cross-pod notifications, long-running jobs, and region replication feeds.
- Object storage: uploads, exports, sealed snapshots, ledger exports, model
  artifacts, and durable transcripts.
- Observability stack: OpenTelemetry traces, Prometheus-compatible metrics,
  centralized logs, and alerting that can distinguish region, pod, user, and
  request correlation IDs.
- Secrets and configuration: cloud KMS or secret manager with versioned
  rollout and rotation controls.

## Externalization Targets

| Priority | Target | Required change | Scale unlocked |
| --- | --- | --- | --- |
| P0 | Rate limiting | Require `REDIS_URL` for multi-replica production and fail closed if Redis is absent. | Safe per-user and per-IP limits across pods. |
| P0 | Playground and agent sessions | Make Redis mandatory for production session, result, share-code, and stream state. | Pod replacement and load balancing without session loss. |
| P0 | Idempotency and request correlation | Persist mutation idempotency keys with request, actor, route, and result metadata. | Safer retries, rollouts, and regional failover. |
| P1 | Auth users and revocation | Move users, refresh-token state, logout revocation, and session tracking into shared storage. | HA auth and accountable logout semantics. |
| P1 | Insight Ledger | Introduce a ledger storage interface with single-writer, transaction, or durable-log guarantees. | Concurrent API pods without corrupting audit history. |
| P1 | AuMemManager | Replace module-level in-memory production storage with a backend interface and durable/vector store. | Consistent memory reads and writes across pods. |
| P1 | Mesh/event state | Move mesh events and transcripts from local SQLite/JSONL to an event bus and durable sink. | Cross-pod communication and replay. |
| P2 | Monitoring and audit logs | Route JSONL-style audit events through centralized logging or append-only object storage. | Region-level compliance records and recovery. |
| P2 | Uploads, snapshots, and model artifacts | Replace pod-local file assumptions with object storage or managed PVC policy. | Rollouts and pod rescheduling without data loss. |
| P2 | NeMo/GPU inference | Add a queue, GPU node-pool sizing, and backpressure policy. | Independent GPU worker scale without overloading scarce devices. |

## Rollout Phases

### Phase 0: State Inventory and Deployment Gate

Do not increase production replicas for state-changing routes until each route
has an owner, state classification, idempotency stance, and rollback plan.

Deliverables:

- Route-by-route inventory of read-only, idempotent mutation, and ordered
  mutation paths.
- Production environment gate that blocks multi-replica mode when required
  shared stores are missing.
- Runbook language that distinguishes pod redundancy from state-safe scale.
- Load-test baseline for the current single-region, single-writer posture.

### Phase 1: Single-Region Stateless API Tier

Run multiple API pods in one region only after shared transient state is active.

Required controls:

- Redis-backed rate limiting, sessions, token revocation, and streaming state.
- Health, readiness, and dependency checks that include Redis and core backing
  stores, not only process liveness.
- Per-route idempotency keys for state-changing APIs.
- Centralized logs and traces with pod, request, user, and correlation IDs.

Exit criteria:

- Rolling restart does not lose active sessions.
- Duplicate mutation requests are deduplicated or safely rejected.
- Load tests prove no route depends on a single pod-local cache for correctness.

### Phase 2: Shared Durable State

Move durable state out of process and local files.

Required controls:

- PostgreSQL or equivalent for auth, RBAC, durable sessions, coordination
  indexes, and idempotency records.
- Ledger write interface with a single writer, optimistic concurrency control,
  or append-log sequencing.
- AuMemManager backend interface with persistent/vector storage and explicit
  cache invalidation.
- Object storage for uploads, snapshots, exports, and model artifacts.

Exit criteria:

- Two or more API pods can process mixed read/write traffic for one region.
- Integrity verification can replay ledger and audit events after pod loss.
- Memory reads are consistent after a write by a different pod.

### Phase 3: Multi-Region Active-Passive

Start with active-passive because it keeps mutation authority and ledger
ordering simpler.

Required controls:

- Region-specific deployment overlays and DNS failover policy.
- Database replication, backup, and restore procedures with declared RPO/RTO.
- Object-storage replication and ledger verification after failover.
- Failover drill that promotes the passive region and proves rollback.

Exit criteria:

- Passive region can serve read-only health and warmup checks.
- A documented failover can promote the passive region without split-brain
  writes.
- Operators know which region owns mutation authority at any time.

### Phase 4: Limited Active-Active

Only move routes to active-active after conflict behavior is explicit.

Candidate patterns:

- Region-sharded writes for users, tenants, or ledger partitions.
- Event-sourced writes with deterministic replay.
- CRDT or merge-safe state only where business semantics permit it.
- Strict global single-writer lanes for ledgers, high-risk mutations, and
  symbolic continuity changes.

Exit criteria:

- Every active-active route has conflict tests.
- Region loss and replay are tested under write load.
- Ledger, audit, and memory records remain explainable after replication lag.

## Follow-Up Issue List

1. Make Redis mandatory for production multi-replica rate limiting.
2. Make Redis mandatory for production playground and agent session storage.
3. Add an idempotency-key store and middleware for state-changing API routes.
4. Design the PostgreSQL schema for auth users, RBAC assignments, refresh
   tokens, token revocation, and durable session metadata.
5. Introduce a storage interface for Insight Ledger and select a single-writer
   or append-log implementation.
6. Introduce a durable/vector backend interface for AuMemManager production
   memory tiers.
7. Move mesh events, transcripts, and cross-pod notifications to a durable event
   bus plus replayable storage.
8. Add object-storage configuration for uploads, exports, sealed snapshots,
   ledger exports, and model artifacts.
9. Add a deployment readiness gate that rejects HPA or multi-replica production
   mode unless required shared state services are configured.
10. Add a single-region multi-replica load and soak test suite.
11. Add an active-passive region failover runbook with RPO/RTO targets and drill
   evidence requirements.
12. Define NeMo/GPU inference scaling around a queue, node-pool capacity, and
   backpressure rather than generic pod HPA.

## Operator Rules

- Treat the single-worker posture as the safe default until a route passes the
  externalization and idempotency gates above.
- Do not use sticky sessions as the correctness model. They are an optimization
  only.
- Do not run ledger, memory, mesh, or audit writers in multiple pods until their
  write-ordering and recovery behavior is tested.
- Prefer active-passive regional failover before active-active.
- Update deployment docs whenever a phase graduates so operator-facing claims
  match current repo evidence.
