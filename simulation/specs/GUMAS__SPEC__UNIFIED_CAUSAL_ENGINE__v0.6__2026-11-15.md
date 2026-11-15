# GUMAS Unified — P5 Distributed Participation and Information-Bounded Consent

**Version:** 0.6 · **Date:** 2026-11-15
**Status:** PROPOSED / ISOLATED SYNTHETIC L2 / NONCANONICAL
**Branch:** `feat/gumas-unified-distributed-governance-p5-20261115`
**Stack:** P0 #1701 → P1 #1702 → P2 #1703 → P3 #1704 → P4 #1705 → P5.
**Authority:** simulation research only; no L1, L3, CanonRec, ACE, QGIA or tactical runtime authority.

## Motivation and scope

P3's council model required local presence for each ballot. P4 proved that
delegation, unanimity and veto authority could produce different institutional
outcomes under one physical kernel. P5 addresses the missing *spatial* and
*epistemic* dimensions: an actor may belong to an institution based at another
site, even one bearing a different polity name, without acquiring instant
knowledge or an instantaneous vote.

P5 does **not** assert the nation-state as a universal organization nor
turn institutional labels into physics. A polity, association, council,
kinship group, corporation or individual is a possible observation frame
over the same historical state. This stage is narrower: **a known institution
with geographically distributed members** and explicit directed communication.
Fully nonterritorial governance, dynamic organization formation, membership
changes and negotiated jurisdiction are later work.

## Causal sequence

1. **Local motion:** a seat-present member proposes one resource allocation
   via P3's state-hash-bound `prepare_relief_proposal`. The motion is a
   particular historical object with fixed amount, commodity, route and expiry.
2. **Outbound notice:** an institution member physically present at the
   seat explicitly sends `policy_notice_sent` over a *directed, enabled*
   route to a registered remote member. Source-site energy is consumed and
   accumulated as heat using P0 signal mechanics; a notice-arrival event
   is scheduled at `t + ceil(distance_km / signal_speed_km_s)`.
   The remote actor's received knowledge is unchanged until this event.
3. **Received knowledge:** `policy_notice_arrival` writes an exact motion
   reference and SHA256 fingerprint to the recipient's `received_reports`.
   Remote actors cannot ballot via this P5 API before this typed, delivered
   notice exists. A hash is internal consistency evidence, not an
   authenticated signature.
4. **Individually chosen remote vote:** an eligible, actually informed
   member sends a `remote_ballot_sent` signal over a separately established,
   enabled **return** route from their present site to the institution seat.
   Its Boolean intent and identity remain recorded in the isolated operator
   ledger, but **are not added to `motion.votes`** at send time. Transmission
   consumes energy and has an explicit due time.
5. **Institutional receipt:** only a scheduled
   `policy_ballot_arrival` event may change `motion.votes`. At arrival the
   motion must still be proposed, before its expiry, and the voter must
   remain eligible under the existing P4 decision rule. A rejected,
   ratified, expired or otherwise closed motion receives a
   `arrived_unusable` observation without retroactive consent.
   Exact-deadline arrivals are not counted.
6. **Separate mandate and physical work:** approval is not an auto-commit.
   An explicitly present local officer still invokes P3 ratification,
   reserves material goods, and another local executor dispatches them under
   P0 cargo capacity, energy and arrival constraints. A remote observer
   receives any outcome only through another separately sent signal.

No global turn-level political shock, hidden telepathic coordination, instant
FTL or magically self-executing mandate is introduced.

## Data and compatibility

- `RemoteBallot` contains ballot/motion/voter/route identifiers,
  Boolean choice, send/arrival seconds, notice fingerprint and status
  `in_flight|counted|arrived_unusable`.
- `Universe.remote_ballots` is a validated map with uniqueness by
  (motion, voter), legal membership, directed route, valid signal-time
  interval and prior delivered notice.
- New scheduler kinds are `policy_notice_arrival` and
  `policy_ballot_arrival`. They run through the existing kernel
  copy–validate–commit receipt mechanism and cannot be manually
  acknowledged by public API calls.
- Missing P5 records omit `remote_ballots` from the hash input,
  preserving original P0–P4 receipts, state hashes and operator-view
  payload shapes. P3's direct local ballot remains local-only.
- Read-only `distributed_council_view` exposes only the number of
  in-flight remote ballots, **not their preferences**. An authorized
  operator can inspect ledger evidence; that is not an institution member's
  knowledge. Existing P3 `institution_view` sees only counted ballots.

## Counterfactual fixture

Same 2 sites, different local polity labels:

- Council seat and resource origin: `union_depot` (fixture_union).
- Remote member physically at `frontier_port` (fixture_frontier).
- The member simultaneously belongs to `frontier_assembly` locally and
  to `relief_council` remotely; organizational membership does not
  require exclusive territorial identification.
- Outbound notice route: union_depot → frontier_port (1200 km at
  300 km/s signal speed) = 4 seconds.
- Independent return route: frontier_port → union_depot = 4 seconds.
- A motion sent at t=0 is known to the remote member at t=4; a remote
  vote sent t=4 can only count at t=8. Approved cargo dispatched t=8
  at 100 km/s arrives at t=20; any separate outcome report sent t=8
  is visible to the remote observer at t=12.
- P4 delegated (remote delegate), unanimous and veto governance all
  execute on the **same** physical scenario, while a negative veto
  leaves supplies at origin.
- With motion expiry at t=6, a ballot sent at t=4 but received at t=8
  is logged as `arrived_unusable`; it does not reopen or approve
  expired policy.

The numbers are **synthetic local test parameters**, not galactic constants,
canon military logistics or FTL rules.

## Invariants / verification

Run from CloudBank root:

    python -m unittest discover -s tests -p 'test_gumas_unified*.py' -v
    python -m simulation.runtime.gumas_unified.scenario
    python -m simulation.runtime.gumas_unified.political_scenario
    python -m simulation.runtime.gumas_unified.governance_scenario
    python -m simulation.runtime.gumas_unified.distributed_scenario

Tests cover P0–P4 inherited behavior, independent directed paths,
signal energy, delayed private actor knowledge, in-flight ballot
non-counting, delivery order, veto/quorum, remote delegate, explicit
expiry, exact deadline, duplicate prevention, no unauthorized
remote members, overlapping memberships and polity-name independence.
The resource ledger must account for all matter and energy, including
communication energy converted to heat and cargo that remains in transit.

## Limits and next gate

- **No cryptographic voter authentication** or external L3 authority:
  source identity may attach an active synthetic P2 binding digest only.
  A sandbox state supplied with fabricated old reports is not protected
  by an independent event-replay proof. This is a fixture-only kernel.
- Existing P0 whole-second clock is retained. P2 tactical millisecond
  coordinates are still declarative/read-only; do not resample them here.
- No autonomous voter deliberation or motivational model. Agents'
  preferences are explicit choices in the synthetic scenarios.
- No actor movement, dynamic membership, institutional succession, custody
  transfer, public-legitimacy feedback, market clearing, authenticated
  proposal commitments, peer-to-peer consensus protocol, or politically
  compelled material action is represented.
- `Institution.seat_site_id` still defines where the current action
  contract can ratify and release goods. The distributed member can
  participate without traveling; **fully decentralized** or overlapping
  decision jurisdictions without a single seat remain future work.
- In-flight notices are delivered if they were already sent even if
  the underlying corridor later changes; this is a recorded propagation
  event, not an always-open route.
- Root peer-review and source-gate reconciliation remain required before
  any merge or active API hookup. P3/P4 unresolved SonarCloud/Codacy
  findings are inherited merge blockers. No Run 0 authorization.
