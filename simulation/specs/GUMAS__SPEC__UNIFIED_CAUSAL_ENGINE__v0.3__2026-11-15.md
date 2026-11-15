# GUMAS Unified — Synthetic Identity Binding and Exact Clock Alignment (P2)

**Version:** 0.3
**Date:** 2026-11-15
**Status:** PROPOSED / EXPERIMENTAL / SYNTHETIC L2 ONLY
**Parent:** P1 PR #1702, stacked on P0 PR #1701 (both drafts).
**Authority:** No L1 progression, CanonRec promotion, ACE character creation, tactical execution, or publication.

## Purpose

P2 closes two laboratory integration gaps in the GUMAS Unified vertical slice:

1. Move beyond inspecting a candidate ACE identity: bind an identity reference
   to an **existing** synthetic L2 actor through the kernel's
   copy-validate-commit ledger and explicit operator-intent fixture grant.
2. Translate an externally validated Phase-9 *relative tactical millisecond*
   interval into an exact local synthetic L2 millisecond coordinate, without
   truncating subsecond precision or causing any tactical or P0 event.

This is **not source-authenticated integration**. Caller-supplied projections,
fixture grants and SHA256 digests prove consistency, not that an actual Pilot,
CanonRec or ACE authority approved the data. No real/unverified identity
may be promoted merely by passing a P2 fixture grant.

## P2 Identity binding

Implementation: \`simulation/runtime/gumas_unified/bindings.py\`.

- Input: the pure P1 \`observe_ace_identity\` projection (origin constrained
  to \`sandbox_created\` or \`inherited_canon\`) and an explicit, exact-field
  fixture grant supplied by the caller.
- Grant scope \`synthetic_fixture_only\`, operation \`bind_fixture_identity\`,
  explicit intent, \`fixture:\` reference, run ID, before-state SHA256,
  existing actor ID/site, source world and entity ID, exact source projection
  digest, effective time and expiry. Canon promotion, memory injection and
  permission changes must all be false.
- \`CausalEngine.bind_fixture_identity()\` validates the proposal before
  calling the kernel's only state writer (\`_commit\`); the binding is an
  append-only, fingerprinted record in \`Universe.identity_bindings\`.
- One-to-one mapping per L2 run: reject duplicate binding of an actor or
  duplicate use of a world/entity pair. A retry of an already committed
  grant fails without a new event.
- The binding is a **synthetic identity label only**. It does not alter
  actor physical location, permissions, preferences, memories, observations,
  inventory, affiliations or canon.
- After expiry, the original receipt remains in history; the binding view
  reports \`active_at_current_time = false\`. P2 has no rebind, revoke,
  authenticated permission grant or time-based event scheduler for identity.
- The raw character background, files, personal data and materialization
  details are not carried into the L2 world.
- A forged fixture grant is only a fabricated synthetic fixture operation.
  This API is NOT appropriate for real ACE or source-canon write authority.

## P2 Time coordinate contract

Implementation: \`simulation/runtime/gumas_unified/time_alignment.py\`.

- Requires a P1 \`observe_phase9_ledger\` projection and a separate,
  *explicit*, fixture-only mapping grant bound to the current P0 world
  hash, P0 run ID, Phase-9 run ID, projection digest and tail-ledger hash.
- The synthetic reference frame's coordinate assumption is explicitly
  1 tactical elapsed millisecond = 1 L2 millisecond, with tactical T0
  declared to coincide with the *current P0 snapshot's time in seconds*.
- The transform is exact integer math:
  \`mapped_l2_ms = anchor_l2_time_s * 1000 + tactical_elapsed_ms\`.
  Display seconds plus remainder using \`divmod(ms, 1000)\`.
- Only an interval \`0 <= start < end <= observed_tail_ms\` may be mapped.
  Both endpoints must lie in the supplied external ledger's span.
- The anchor becomes stale after **any** P0 state transition, including
  identity binding. Bind first, then prepare the anchor.
- The transform does not assert a shared physical spacetime, verified
  causal path, source clock epoch, authenticated T0 event or synchronization.
  Its role is an **operator-reviewed coordinate hypothesis**, not an event.
- No P0 clock advancement, scheduling, resource accounting change,
  agent observation, Phase-9 Run 0, canonical or live tactical state change.

The \`operator_cross_scale_frame\` function combines a **kernel-committed**
active synthetic identity association with an exact mapped tactical interval,
as a read-only, non-agent-visible review packet. It never imports a tactical
effect or political result.

## Physical and epistemic limitations

P0 currently commits in whole simulation seconds. P2 does NOT change
that clock. Its \`mapped_start_l2_ms\` and \`mapped_end_l2_ms\` can represent
subsecond coordinates, but cannot be submitted as P0 executable events.
That requires a later versioned event clock and scheduling contract.

Similarly, a Phase-9 abstract "macrostep" is not evidence of a broader
galactic macro event. No alias, recipient, observation, authorization, or
physics should be inferred from its name. Cross-frame causal reconciliation
is deferred pending authoritative source authentication and explicit spatial
and temporal registration.

## Upstream references / frozen lineage

- Root PR #85 (\`codex/ace-persistent-continuity-20260906\`) supplies
  sandbox-scope world-status and retrieval contracts.
- CloudBank tactical PR #1506
  (\`agent/gumas-flash-rebellion-battle-baseline\`) supplies
  Phase-9 relative-millisecond, immutable-ledger contracts.
- P1 PR #1702 validates and labels source packets, without executing either
  upstream engine.
- P0 PR #1701 provides transactional L2 execution, identity and resource
  objects, exact whole-second scheduling and the event ledger.
- All upstream PRs remain unmerged / gated for this purpose.
  P2 does not bypass the tactical blocked Run 0 or independently claim
  that these sources are cryptographically authenticated.

## Tests

From CloudBank root:

    python -m unittest discover -s tests -p 'test_gumas_unified*.py' -v
    python -m simulation.runtime.gumas_unified.scenario

P2 tests require: atomic commit and ledger replay; no changes to permissions
or observations; private-data exclusion; expiry; duplicate entity refusal;
stale/mismatched identity grants; invalid authority scopes; source tampering;
exact 7.200/7.425-second coordinate mapping without rounding; stale source or
local snapshots; false execution claims; out-of-span intervals and side-effect
free operator combination.

## Next gated milestone: P3

1. Obtain provenance-verified source snapshots from independently reviewed
   repository pins/receipts; move fixture-only grants to an actual
   authenticated L3 authorization mechanism before live agent binding.
2. Design one shared high-precision event clock / spacetime reference
   with FTL and technology profiles vetted against canon.
3. Add a proposal-validation-commit adapter for one **noncombat** political
   action, with source actor, capabilities, resource effects and recipient
   information. No arbitrary per-turn rebellion hazard.
4. Repair transition-only \`CIVIL_WAR_ONSET\` in the legacy shadow path;
   test for pathologies and label statistical calibration separately.
5. Do not merge, retarget, or activate these contracts without review.

The P2 work is meaningful executable groundwork, not proof that the
historically established Aurora worlds are now physically synchronized.
