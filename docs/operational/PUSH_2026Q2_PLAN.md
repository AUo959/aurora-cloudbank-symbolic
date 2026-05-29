# Push 2026-Q2 — Wholistic Plan

**Scope**: GitHub issues #758–#841 (84 open as of 2026-05-29).
**North-star artifact**: `scripts/benchmark_scorecard.py` — when `--strict` returns 0, the push is done.

---

## TL;DR

- 84 open issues across 11 domains.
- Decomposes into **9 phases + an independent connector track**.
- Critical path: **#834 → #758 → #818 → #774 → #769 → #815 → #770 → #775**.
- ~45 issues are parallelizable once Phase 2 (request envelope) is in.
- Estimated ~50 engineering-weeks (3 engineers + connector track ≈ 5 calendar months).

---

## Upfront decisions (resolve before Phase 4)

| # | Decision | Driving issue | Recommendation |
|---|---|---|---|
| D1 | AuMemManager durability: volatile / snapshot / tier-aware | #805 | Periodic snapshot — minimal change, makes the "56K capacity" claim honest |
| D2 | Multi-worker: single-worker enforced vs Redis-backed externalization | #810 | Single-worker enforced now; externalization tracked in #840 |
| D3 | Ethics rule source of truth: hardcoded vs `config/ethics_rules.json` | #782 | Ship `config/ethics_rules.json`; remove inline list |
| D4 | Dependency surface: keep `setup.py` vs migrate to PEP 621 `pyproject.toml` | #836 | Migrate to `pyproject.toml`; delete `setup.py` |
| D5 | Container base image rebase cadence | #833 | Pin by SHA256 digest; quarterly Dependabot update window |

---

## Phase map

### Phase 0 — Pre-flight hygiene (parallelizable, low blast radius)

| Issue | Title |
|---|---|
| #767 | Pin kube-linter installer |
| #768 | `datetime.utcnow()` sweep (136 sites) |
| #786 | Re-enable CodeQL + upgrade deprecated v1/v2 actions |
| #788 | Cookie flags decision + doc |
| #789 | Reconcile README test counts |
| #795 | Remove `modules/nexus` lint exclusion (or justify) |
| #821 | `.env.example` completeness |
| #830 | Requirements file inventory drift |
| #831 | Upper-bound pins on critical packages |
| #832 | SHA-pin 11 third-party Actions |
| #833 | Digest-pin base images |
| #834 | Python floor consistency |
| #836 | setup.py vs pyproject.toml (D4) |

**Exit**: scorecard rows for `datetime.utcnow`, third-party action pins, docker pins, Python floor, .env.example all PASS.

---

### Phase 1 — Make CI meaningful

| Issue | Title |
|---|---|
| #758 | CI tests/quality fail-closed |
| #760 | Reconcile README production claims |
| #787 | Lock file in CI (depends on regenerating) |
| #790 | Coverage threshold (`--cov-fail-under`) |
| #791 | Replace 333 hollow assertions (Tier 1) |
| #792 | Mark or refactor 5 unmarked sleep>1s sites |
| #793 | Lifespan + route inventory + middleware tests |
| #794 | Scoped conftest env fixtures (enable `pytest -n auto`) |
| #835 | `pip --require-hashes` (after #787) |

**Exit**: any failing critical test blocks merge; coverage threshold configured; `continue-on-error` count = 0 on test/lint jobs.

---

### Phase 2 — Request envelope + observability spine (critical path)

| Issue | Title |
|---|---|
| #818 | Request-ID middleware (`X-Request-ID`) |
| #774 | Canonical `context_tag` envelope (consumes #818) |
| #769 | R-2 Telemetry middleware (consumes #774) |
| #781 | Log sanitizer filter (independent but ship now) |

**Exit**: every request emits a span, carries `X-Request-ID`, writes one ledger row with `context_tag`.

---

### Phase 3 — Operational backbone

| Issue | Title | Depends |
|---|---|---|
| #759 | Align startup commands with canonical entrypoint | — |
| #802 | Fire-and-forget `asyncio.create_task` safety | — |
| #803 | `MemoryCache` LRU + size cap | — |
| #804 | ThreadPoolExecutor lifecycle | — |
| #813 | Configurable storage paths | — |
| #814 | `/live` / `/ready` / `/health` split | #815 |
| #815 | Config validation + "startup complete" + Pydantic Settings | #834 |
| #816 | Graceful shutdown coordinator | #815, #804 |
| #817 | Uvicorn hardening (timeouts, body cap, concurrency, proxy) | — |
| #819 | Idempotency-Key support | #774 |
| #820 | Instance-level PID/file lock | #813 |

**Exit**: clean SIGTERM behavior, structured "startup complete" log, three health endpoints with distinct semantics.

---

### Phase 4 — Persistence durability (needs D1, D2, D3)

| Issue | Title | Depends |
|---|---|---|
| #762 | Quantum mixed-state: implement or fail-closed | — |
| #763 | Regenerate or retire stale API catalog | — |
| #764 | Mesh runtime `/api/mesh/agents` contract drift | — |
| #805 | AuMemManager durability (D1) | #807, #813 |
| #806 | Insight Ledger startup verify | #807, #808 |
| #807 | Atomic writes + fsync (8 sites) | — |
| #808 | Write locks on 4 monitoring stores | #807 |
| #809 | Retention TTL on violations/alerts/interventions | — |
| #810 | Multi-worker contract (D2) | #815 |
| #811 | Schema versioning + migration registry | — |

**Exit**: scorecard atomic-write row PASS, ledger startup verify PASS, retention enforced.

---

### Phase 5 — Security / PII / boundary

| Issue | Title | Depends |
|---|---|---|
| #766 | BUILD_PHASE_PLACEHOLDER secrets fail-closed | #815 |
| #783 | Sanitize 153 `HTTPException(detail=str(e))` sites | #774 |
| #784 | CSRF coverage on every state-changing route | — |
| #785 | Rate-limit matrix on AI/crew/quantum/memory-write | — |
| #778 | PII detection/redaction middleware | #774 |
| #812 | PII redaction at persistence boundary | #778, #807 |

**Exit**: scorecard `str(e)` row PASS, CSRF coverage PASS, rate-limit coverage documented.

---

### Phase 6 — Ethics gate + AI safety

| Issue | Title | Depends |
|---|---|---|
| #761 | HR mocks + `OrganizationalIntelligence` | — |
| #770 | EthicsEngine on chat/agent/quantum + enforcement handlers | #782, #774 |
| #771 | Synergy dashboard runtime topology | #769 |
| #779 | DriftDetector live agent feed | #769 |
| #780 | Preserve and integrate CASK (Track A: specs surface; Track B: Recursive Ethics Validator + Cultural Cognition Framework) | #770, #782 |
| #782 | Rule source of truth (D3) | — |
| #796 | LLM SDK hardening (timeouts, retries, semaphore) | — |
| #797 | Prompt-injection wrapping | — |
| #798 | Token budget + per-user spend caps | #774, #796 |
| #799 | Memory token cap + dedup | — |
| #800 | Memory cache user/tenant scoping | — |
| #801 | AIModel enum reconciliation | — |

**Exit**: ethics-response-path row PASS, drift signals fire under test, CASK Track A surface live.

---

### Phase 7 — Module wiring + vertical workflows

| Issue | Title | Depends |
|---|---|---|
| #765 | Opal2 decorators + CI coverage | — |
| #772 | Consolidate crew endpoints (drop inline duplicate) | — |
| #773 | Expose memory retrieval router | #774 |
| #775 | Vertical V1: memory-augmented chat | #773, #774, #770, #769, #778 |
| #776 | Vertical V2: ethics-gated quantum scenario | #770, #774 |
| #777 | Decide shell orchestrators (wire / demote / retire) | #775, #776 |

**Exit**: at least two vertical workflows demonstrate end-to-end traversal of the spine.

---

### Phase 8 — Connector track (independent; assign to single person)

| Issue | Title | Depends |
|---|---|---|
| #822 | Pilot seal → HMAC | — |
| #823 | Error scrubbing on MCP boundary | — |
| #824 | Bridge fail-closed + retries + circuit breaker | — |
| #825 | JSON schema enforcement at dispatch | — |
| #826 | User-Agent + X-Source-Client headers | — |
| #827 | Connector test directory + first tests | — |
| #828 | Wire MCP tools to real Aurora API endpoints | Phase 7 endpoints |
| #829 | ChatGPT + Gemini parameter validation | — |

**Exit**: connector ships v0.1.0-hardened with real endpoints, HMAC seal, full test coverage.

---

### Phase 9 — Strategic / post-push

| Issue | Title |
|---|---|
| #838 | Establish load-testing harness |
| #839 | Per-endpoint performance budgets |
| #840 | Horizontal / multi-region scaling plan |
| #841 | Schedule external pen test / security review |

**Exit**: load baseline captured, budgets documented, scaling plan reviewed, pen test scheduled.

---

## Critical path

```
#834 ─┐
#758 ─┼─→ #818 ─→ #774 ─→ #769 ─→ #815 ─→ #770 ─→ #775 ─→ #777
#787 ─┘                          └→ #816                 #776
                                  └→ #814
```

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| #770 ethics wiring blocks vertical work if D3 drags | M | H | Resolve D3 week 1; ship #782 as a 1-day ticket |
| #807 atomic writes break startup load on existing torn files | L | H | Read-side tolerates `.tmp` files; document migration |
| #810 multi-worker decision deferred | M | H | Resolve D2 now; single-worker is the obvious near-term answer |
| #828 connector → real endpoints requires endpoints that don't exist yet | H | M | Sequence after Phase 7 or stub connector-side |
| #774 envelope changes contract everywhere at once | M | H | Make `context_tag` optional first, ratchet to required after Phase 5 |
| CodeQL re-enable surfaces 100s of pre-existing findings | H | M | Triage first run into fix/document/suppress |
| PII middleware (#778) adds latency on every request | M | M | Benchmark before rollout; per-route bypass on known-clean paths |

---

## Execution rhythm (suggested)

| Sprint (2 wks) | Focus |
|---|---|
| 1 | Phase 0 batch + start Phase 1 + decisions D1–D5 |
| 2 | Finish Phase 1 + spike Phase 2 spine + start Phase 8 |
| 3 | Phase 2 complete + Phase 3 starts + Phase 8 continues |
| 4 | Phase 3 finish + Phase 4 starts |
| 5 | Phase 4 + Phase 5 parallel; first Phase 6 (#782, #779) |
| 6 | Phase 6 bulk |
| 7 | Phase 7 verticals; Phase 8 endpoint catch-up (#828) |
| 8 | Phase 9 launches; scorecard `--strict` green |

---

## Definition of done

1. `python scripts/benchmark_scorecard.py --strict` returns exit code 0.
2. All 84 issues closed or documented as deferred.
3. README and CLAUDE.md carry no numeric claims unbacked by a regenerated artifact.
4. CI has a required critical-suite step; CodeQL is required; coverage threshold is enforced.
5. A documented canonical-request integration test passes: chat → PII middleware → envelope → ethics gate → ledger → memory → telemetry, all keyed by one `context_tag`.

---

## Burndown

Burndown is observed via `python scripts/benchmark_scorecard.py`. Snapshot rows here whenever a phase exit is hit:

| Date | Total fails / required | Notes |
|---|---|---|
| 2026-05-29 | 20 / 7 | Baseline before push begins |
| 2026-05-29 | 19 / 7 | #834 Python floor unified at `>=3.11`; #789, #830 docs reconciled |
| 2026-05-29 | 18 / 7 | #768 `datetime.utcnow()` sweep complete (136 → 0); #788 cookies posture documented; #831 upper-bound pins added to 38 packages |
| 2026-05-29 | 17 / 7 | #767 kube-linter pinned via official action; #786 CodeQL re-enabled (Python + JavaScript matrix, weekly schedule, scoped permissions) |

---

## Cross-references

- Scorecard: `scripts/benchmark_scorecard.py`
- Test inventory generator: `scripts/test_inventory.py`
- Decisions log: `docs/decisions/` (to be created as D1–D5 are resolved)
