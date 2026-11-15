# GUMAS Unified — P3 Noncombat Institutional Causality

**Version:** 0.4 · **Date:** 2026-11-15
**Status:** PROPOSED / L2 SYNTHETIC RESEARCH ONLY
**Stack:** P0 #1701 → P1 #1702 → P2 #1703 → P3 (this PR).
**Canon authority:** none; no L1/CanonRec/THREADCORE writes.

## Purpose

P0 established one world state, material/information constraints, deterministic
transitions, observational projections and a causal receipt chain. P1 added
read-only external evidence adapters. P2 demonstrated synthetic ACE identity
binding and declared tactical-millisecond mapping. **P3 introduces the first
active, noncombat political processor:** a local relief council approves or
rejects a resource allocation through recorded individual ballots. A valid
approval reserves physical goods; a separate feasible dispatch sends them over
the already established corridor. The recipient learns through existing
delayed communication.

This is not a general theory of federation, empire, nation state, biological
polity or AI government. The institution's membership, seat, quorum and vote
threshold are **scenario data**, with no civilization-name branching.
No synthetic local council vote is claimed to have happened in Aurora canon.

## Typed and validated state

New \`Institution\`: institution_id, seat_site_id, polity_id, distinct
member actor IDs, quorum, approval threshold.

New \`ReliefMotion\`: motion ID, institution/proposer, route, commodity,
positive quantity, expiry, individually identified ballots, state
(proposed / ratified / dispatched / rejected / expired), reserved commodity
quantity, approval time and shipment reference.

The original \`Universe\` state adds \`institutions\` and \`relief_motions\`.
Both are omitted from the canonical state digest when empty so P0/P1/P2
state hashes and event receipts remain reproducible with existing fixtures.

Validation enforces member uniqueness, valid organization/site/polity
relationship, physically existing routes and actors, mandatory positive
quorums, valid statuses, escrow/status consistency, and only actual
member ballots of Boolean yes/no. These are **local procedural rules**, not
laws of physics.

## Proposal → ballot → reservation → dispatch

- **Proposal:** \`prepare_relief_proposal()\` is pure and returns a frozen,
  SHA256-bound proposal tied to an exact L2 pre-state hash/run. It is
  accepted only from an institution member physically present at that seat.
  \`CausalEngine.propose_relief()\` commits a new motion, expiry event,
  optional active P2 identity-binding hash, and causal ledger receipt.
- **Ballots:** each member present at the seat can cast one yes/no ballot.
  Each ballot changes one committed state and emits a receipt. No
  omniscient automatic consensus or invented vote history is permitted.
  A motion is rejected early when the remaining members could no longer
  meet the specified approval threshold.
- **Ratification:** another explicit action requires the recorded quorum
  and yes threshold, a currently traversable route, and sufficient **available**
  goods in the institution's local source depot. The kernel atomically moves
  those goods from available inventory into the motion's reserved stock
  (escrow), recording the event. This is a resource custody model, not
  energy creation or a probability-of-rebellion variable.
- **Dispatch:** an existing physical actor at the seat may physically
  release the reserved goods into a shipment. Cargo speed, route capacity
  windows, energy cost/heat accounting and arrival scheduling use P0's
  underlying state and physical profile. An unauthorized executor may
  physically act, but the receipt records \`institutionally_authorized=false\`.
  This prototype models an accessible depot; it does not imply real
  secured-storehouse access or automatic legal immunity.
- **Expiry:** the existing event scheduler handles a motion expiry. If
  reservations have not departed, escrow returns to the site; goods already
  shipped stay shipped, and goods rejected or never allocated never move.
  The receipt preserves the causal progression; there is no duplicated
  \`POLICY_ONSET\` or repeat allocation on subsequent turns.
- **Observation:** local and polity projections distinguish available,
  in-transit and reserved goods. \`institution_view()\` is an *operator-only*
  aggregate, not a claim that remote actors see votes instantaneously.
  Individual actors at the physical council seat may participate; a
  remote recipient learns through P0's directed signal corridor and delay.

The accounting invariant is:

\`total(commodity) = sum(site.available) + sum(in_transit) + sum(motion.escrow)\`

Energy retains P0's converted-to-heat accounting. Legitimacy, cohesion,
social trust and other political indices are **not** conserved commodities
and remain outside this first causal exercise.

## Cross-stage scenario

\`python -m simulation.runtime.gumas_unified.political_scenario\`

Two counterfactual paths have identical synthetic setup but different
agent ballots:

- **Approve:** yes + yes meets quorum; three units of rations move from
  available to reserved, then into the corridor and finally the recipient.
- **Reject:** yes + no + no makes approval impossible, so the motion is
  rejected and those three units remain at origin.

Both paths may notify the remote observer only by sending a message
through the P0 signal corridor; 1200 km / 300 km/s = 4 s, while
1200 km / 100 km/s = 12 s for cargo. The demo also records one active
P2 *synthetic* ACE-to-governor identity binding, but the council's legal
membership is modeled **independently** of external ACE canon.

This is a **counterfactual causal comparison**, not an assertion about
actual Galactic Union factions, relief policy or planetary supply needs.

## Verification

Run from repository root with Python 3.12:

    python -m unittest discover -s tests -p 'test_gumas_unified*.py' -v
    python -m simulation.runtime.gumas_unified.scenario
    python -m simulation.runtime.gumas_unified.political_scenario

Tests should cover deterministic replay, proposal stale-state rejection,
individual yes/no votes, quorum, duplicate vote refusal, membership/seat
constraints, stock scarcity, escrow conserved across approval/dispatch/expiry,
energy/capacity checks, no double fulfillment, institutional illegality
distinct from physical access, observer locality and delayed knowledge,
operator projections, polity-name independence, and continued P0 digest
compatibility. No external unmerged PR code is invoked.

## Explicit limitations

- Only one **in-person** synthetic local institution and one type of
  resource motion; no remote voting, deliberation protocol, coalition
  building, distributed sovereignty, durable markets, competing institutional
  jurisdictions, private property or secured custody beyond available stock.
- Actor decisions are explicit scenario/test inputs. No general autonomous
  personality, cognition, stochastic policy maker or hidden political
  causal mechanism is claimed. External provenance remains unauthenticated.
- Institution membership and threshold are scenario-provided, not inferred
  from canonical labels or polity categories.
- The transport code uses the same P0 state constraints but is a dedicated
  domain transition. Future contracts should unify the shipment utility
  and add property-based tests over alternate physical profiles.
- The P0/P3 clock still resolves commits in **integer seconds**. P2's
  subsecond tactical coordinate mapping remains read-only, not executable.
- No direct trust/legitimacy deltas, insurgency spawn, coup, civil war,
  nation-state inevitability assumption, Earth-derived rates or political
  stability multipliers are introduced.
- The **legacy v3 repeated \`CIVIL_WAR_ONSET\` bug is not patched here**,
  because it is in another code lineage/repository and must be repaired
  under its own isolated owner-reviewed issue and regression tests.
- Hash chains and synthetic fixture grants are not source signatures,
  authenticated L3 operator authority or proofs of real-world execution.
  This PR grants no tactical Phase-9 Run 0 authority.
- No shared-world durable checkpoints, signed receipts, market
  equilibration or canonical promotion are implemented.

## Next gate: P4

Develop a reviewable generalized institutional/action proposal schema
with explicit information provenance and actor capability interfaces;
validate canonical technologies and a high-resolution shared clock;
separately fix the legacy onset bug; introduce heterogeneous governance
fixtures to test the same physics without requiring a single social form.
The stacked PRs remain drafts until independent review.
