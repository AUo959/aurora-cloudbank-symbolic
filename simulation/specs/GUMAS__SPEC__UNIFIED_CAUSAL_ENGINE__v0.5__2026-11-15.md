# GUMAS Unified — Heterogeneous Governance Protocols (P4)

**Version:** 0.5 | **Date:** 2026-11-15
**Status:** PROPOSED / L2 SYNTHETIC ONLY
**Alignment audit:** \`simulation/audits/GUMAS__AUDIT__P4_INFRASTRUCTURE_ALIGNMENT__v1.0__2026-11-15.md\`
**Lineage:** P0 #1701 → P1 #1702 → P2 #1703 → P3 #1704 → P4.

## Objective

Prove that identical physical resources, transport limitations, individual
agency, and macro projections can coexist with different local institutional
authorization mechanisms. A polity is an observational frame over an evolving
causal reality, not a required nation-state type or a universal decision law.

## Implementation

A frozen \`GovernanceProtocol\` is keyed by a preexisting institution in
\`Universe.governance_rules\`. Missing protocols imply exactly the P3
\`quorum_threshold\` rule; the P3 state/receipt/projection shape is unchanged
when no P4 policy is present.

Three supplemental modes:

1. \`delegated\`: a single existing institution member is an explicit delegate;
   their positive ballot enables ratification; a negative ballot rejects.
   The local fixture uses quorum=1 and threshold=1. This is recorded
   delegation as scenario data, not an automatic hereditary monarchy.
2. \`unanimous\`: all institution members vote yes. Any negative ballot
   rejects; no other actor can create their vote. Exact 3-of-3
   is the initial synthetic example, not a universal limit.
3. \`veto\`: a quorum/threshold is required **plus** every named veto holder's
   affirmative ballot. A veto holder's no rejects immediately. A threshold
   alone cannot override recorded veto power.

Rules are installed at synthetic world initialization and validated:
institution IDs, delegate/veto holder membership, mutually compatible
quorums and threshold, no duplicate veto holders, bounded recognized
protocol values. No extra permission, origin, source-canon promotion,
decision automation or institutional rule mutation is conferred.

An institution's *authorization* is distinguishable from a physically
possible act. Once authorized, goods still move from local inventory
through escrow and a physically supported corridor. No protocol can
create resources, bypass information delay, obtain absent stock, or
forge causal event receipts.

## Explicit negative constraints

- No political structure is assumed to emerge inevitably.
- Earth social statistics are not assigned universally to other species.
- No canonical organization is asserted to use any of these protocols.
- No source-canon ACE identity is created or promoted.
- No P1 tactical macrostep, Phase-9 Run 0 or L1/QGIA interaction executes.
- No remote voting across nonlocal routes; a later stage must explicitly
  account for message latency and individual information.
- No government termination, insurgency onset, coup or war probability is
  introduced; the legacy v3 \`CIVIL_WAR_ONSET\` issue remains separate.

## Contract tests

    python -m unittest discover -s tests -p 'test_gumas_unified*.py' -v
    python -m simulation.runtime.gumas_unified.scenario
    python -m simulation.runtime.gumas_unified.political_scenario
    python -m simulation.runtime.gumas_unified.governance_scenario

Required tests: all P0-P3 regressions; sample delegated/unanimous/veto
decision paths; negative veto, failed unauthorized ballots, missing consent,
bad quorum, invalid rule data, physically remote voting refusal; identical
material totals and information latency; no one-off polity-name effects;
P0 fixed state hash and P3 receipt/projection compatibility in the
absence of a P4 policy.

## Follow-on architectural stages

P5 should address distributed institutions without inventing instant
communications, including verified remote ballots, in-flight messages,
agent knowledge, changed jurisdictions and institutional membership.
P6 should connect general action commitments to physical-time profiles,
source-authenticated identity and history constraints, then compare
heterogeneous canonical polities through audited explanatory reconstructions.

The 2026-11-15 infrastructure audit and inherited P3 static-analysis
failures remain explicit blockers to merge, promotion and live service
activation. Passing targeted tests is evidence of the isolated P4 contract
only, not complete platform integration.
