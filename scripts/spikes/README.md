# Responses read-only compatibility spike (#1625)

This isolated, non-production proof does not import Mesh runtime, L1, or CanonRec
code. It accepts an explicit revision and a caller-selected snapshot, exposes
only `read_snapshot`, and returns a review-only receipt. It cannot apply candidate
deltas. Nothing registers it with production routing or changes model defaults.

## Run

Use Python 3.12 and the committed hashed CI dependency set in a disposable virtual
environment. Do not use the canonical checkout's existing environment as proof
of the lock: the reviewed local environment had OpenAI 2.44.0.

```sh
uv venv --python python3.12 /private/tmp/cloudbank-spike-env
uv pip install --python /private/tmp/cloudbank-spike-env/bin/python \
  --require-hashes -r requirements-ci-hashed.txt
/private/tmp/cloudbank-spike-env/bin/python scripts/spikes/responses_multi_agent_readonly.py
```

The default returns `status=disabled` without constructing a client. An explicit
`--enable` flag performs a live request using `OPENAI_API_KEY`; secure credential
configuration and account/model availability are prerequisites. `--mode single`
uses standard Responses instead of beta Responses. Both CLI modes use the same
small synthetic Aurora boundary snapshot, not live station state.

The programmatic `run` function supports bounded caller-selected text snapshots.
The caller owns selection, revision accuracy, privacy review, and context scope.
The tool never resolves paths or loads files. JSON serialization freezes evidence
before execution. Snapshot content and task content are untrusted; a small
conservative injection signal remains visible in the receipt, but is not a
comprehensive injection detector.

## Limits and authority

- Feature flag defaults off; model is explicitly `gpt-6.1-sol`, effort `low`.
- Concurrency is 1–3, default 3; at most 30 seconds of client execution,
  three Responses calls, four dispatched tool calls, and 1,024 requested output
  tokens per Responses call. Client cleanup has a separate one-second timeout.
  SDK retries are disabled. There is no fallback.
- Task is at most 4 KiB; snapshot is at most 16 KiB and eight named sections.
- Strict tool schema and local validation reject unknown tools/arguments/sections.
- Single and multi request paths are explicit. Advanced controls are rejected
  rather than silently dropped: explicit compaction, reasoning summaries,
  configuration updates, async tools, sampling controls, API `max_tool_calls`.
  Parallel tool calls are disabled. Multi-agent uses implicit server compaction.
- Receipts retain response IDs, agent names, exposed coordination metadata,
  tool call IDs/results and snapshot hashes, root final text, usage, and latency.
  Private reasoning and opaque compaction items are kept only in ephemeral API
  history as needed for continuation, never in the receipt. Missing usage/cost
  remains unknown. Findings are candidate text; deltas are not extracted/applied.
- Every candidate has `validation=not_applied`. Root #95 remains the authority
  contract dependency; this proof introduces no validator or commit authority.
- Preflight failures return `status=rejected` receipts without creating a client.
  Cleanup timeout/failure stays visible in the receipt, preserves an earlier
  execution error, and prevents a successful-result claim when cleanup fails.

Concurrency does not cap total agents or tree depth. Client deadlines/cancellation
do not prove server-side termination or a hard dollar ceiling. No total-agent,
aggregate-token, or cost guarantee is claimed. Live evaluation must record these
limitations and account spend controls; production enablement needs separate
review and evaluation evidence.

## Verified on 2026-10-10

At CloudBank base `0fac980967ac7802a399f091fadf24bcd67b3126`, the full hashed CI
dependency install succeeded in an isolated Python 3.12 environment with
`openai==3.6.0` and `httpx2==2.12.0`. The real SDK's beta request/header and
agent-attributed tool-result continuation are tested through mocked HTTP transport.
Both sync and async client construction accept the existing `httpx.Timeout` type.
No dependency update or timeout migration is needed for this proof.

No live model call, model access verification, delegation-quality evaluation,
server cost measurement, or production-readiness assertion is included.

The required `CI Check` workflow explicitly executes the complete spike test
file as a blocking step. Every nonzero pytest exit, including collection errors,
fails that step; the suite does not depend on critical/smoke marker discovery.

```sh
python -m pytest tests/test_responses_multi_agent_readonly.py \
  tests/test_unified_ai_interface.py tests/test_token_budget.py \
  tests/test_mesh_runtime_surface.py tests/test_mesh_runtime_api_surface.py \
  tests/test_l1_runtime.py -q -o addopts=''
python scripts/check_hashed_lock_drift.py
git diff --check
```

Tests exercise L1 only in temporary test fixtures; never INIT/resume/advance the
paused canonical run. #1610 model catalog, role routing, caching modernization,
and default-model evaluation remain separate work.

Sources: [CloudBank #1625](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1625),
[#1610 scope correction](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1610#issuecomment-5985040812),
[root #95](https://github.com/AUo959/Aurora_ORIONCORE_Directory_Main/issues/95),
[official Multi-agent guide](https://developers.openai.com/api/docs/guides/responses-multi-agent).
