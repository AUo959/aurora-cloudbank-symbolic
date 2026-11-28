# GUMAS Unified — P6 Seatless Associations and Causal Mandates

**Version:** 0.7 · **Date:** 2026-11-16
**Status:** EXPERIMENTAL / SYNTHETIC L2 ONLY / NONCANONICAL
**Stack:** P0 #1701 → P1 #1702 → P2 #1703 → P3 #1704 → P4 #1705 → P5 #1706 → P6.
**Authority:** No L1 authority, CanonRec promotion, L3 runtime permission, QGIA feed, ACE write, tactical Phase-9 Run 0 or production GUMAS API change.
**Audit:** `simulation/audits/GUMAS__AUDIT__P6_SEATLESS_ASSOCIATION_ALIGNMENT__v1.0__2026-11-16.md`

## Architectural intent

P0 implemented resource-bounded individual actions and one causally consistent
world. P3 made institutional decisions produce explicit physical consequences.
P4 diversified local decision predicates. P5 added correctly delayed remote
votes, though institutions still had a permanent `seat_site_id`.

P6 creates a *separate, explicitly seatless class of organization*:

- An association is formed by two individual agents' reciprocal, delivered
  charter consent, **not** by a pre-created polity, government or locality.
- Members remain physically situated within other site-polity projections,
  and retain their other memberships and roles.
- The association has no `seat_site_id`, no automatic territorial
  sovereignty, no power to change a site's public law or permission registry.
- Either **informed** member can initiate a new coordination procedure from
  their current site once it is reasonable for them to know the association
  exists. The proposer acts as a *mandate-specific message coordinator*, not
  a permanent capital or a universally privileged class.
- A physical shipment still has a designated local custodian and explicit
  source route for that action only. Approval does not create goods or
  change a site's independent dispatch authorization.

The two-person size, unanimous-approval rule and static actor locations
are **bounded pilot choices**, not claims about how all societies or
species form governments.

## Formation: two distinct causal signals plus confirmation

1. `offer_charter`: a founder at site A proposes public purpose and
   founder/invitee terms. Their message goes A→B over a checked directed
   route, consuming signal energy. A scheduled receipt carries its exact
   immutable public terms and SHA256 fingerprint.
2. `charter_offer_arrival`: only at the physical due time does invitee B
   receive the typed charter report. Before that, B cannot respond.
3. `respond_charter`: B independently sends a Boolean consent or refusal
   along a **separate valid return route** B→A. The association does not
   yet exist; the response remains in transit.
4. `charter_response_arrival`: A receives actual consent. Only a
   timely affirmative decision establishes `Association` with two
   members and no permanent seat. Negative or late responses cannot
   create membership.
5. `confirm_association`: A explicitly sends back a formation
   confirmation, consuming signal energy. Until its delayed arrival,
   B cannot claim knowledge of successful formation or propose a
   mandate under that association.
6. `association_confirm_arrival`: B receives an actual report of
   formation; only then can B coordinate an association action.

Each step is committed through `CausalEngine._commit` and the existing
P0 deterministic scheduler. A creator's private thought, invitation
being sent, or reply in transit is never mistaken for delivered consent.

## Mandate: decision is separate from physical act

1. An informed member proposes a material relief mandate. The proposal
   identifies its association, proposer (temporary coordinator), other
   member, an explicit local custodian, cargo route, commodity, amount,
   expiry, public terms and fingerprint. The current bounded pilot
   requires the local custodian to be the proposer.
2. The other member receives public mandate terms through a new directed
   signal. A reply cannot be sent until the actual message arrives.
3. A distinct Boolean approval/refusal travels back over another directed,
   powered route. While in flight, it is not a counted mandate approval.
4. At the response-arrival event, the **proposer** receives a typed
   decision report. Only a timely affirmative response changes the
   mandate's status to `authorized`. Refusal or expiration closes it.
5. Authorization **does not reserve or dispatch goods**. The nominated
   custodian must separately call `execute_mandate` while at the
   physical source. That atomic kernel transition enforces P0 route
   enabledness, source inventory, shared capacity windows, cargo energy
   and arrival delay, and commits a hash-linked shipment. A veto/no vote,
   stale mandate, absent goods or blocked corridor leaves all material
   resources unchanged.
6. P0 shipment-arrival events change destination inventory at the
   calculated physical time, not at approval time. The total commodity
   and energy-to-heat balance is conserved.

The receipt distinguishes `association_approved` from
`site_dispatch_authorized`. An association's consent does not silently
change individual property rights, law or site access; the prototype
can record a physically performed but independently unauthorized act,
as P3 already distinguishes feasibility from institutional legality.

## Synthetic proof scenarios

- Site A `union_depot`, site B `frontier_port` at 1200 km separation.
- Signal route A→B and separately defined B→A each take four seconds
  at fixture signal speed 300 km/s. No instant communication or FTL.
- Charter offered t=0, delivered to B t=4; reply sent t=4,
  counted at A t=8. A can announce formation at t=8 and B knows at
  t=12.
- A may propose mandate at t=8; B receives the terms t=12 and returns
  a ballot received by A t=16. A physically dispatches three rations
  at t=16; cargo takes 12 seconds and arrives t=28.
- A remote-initiative counterfactual uses B as temporary proposer and
  local custodian only after formation confirmation arrives at t=12;
  the same two-way delay and physical constraints apply in reverse.
- Negative charter or mandate votes, expired return messages,
  unauthorized execution attempts and competing cargo cause separate
  counterfactual outcomes with no hidden auto-formation or auto-shipment.

These times, resource amounts and identities are synthetic acceptance
fixtures, not canonical galactic timelines, political structures or
technology claims.

## Contracts and validation

New data types `Charter`, `Association`, `Mandate` are version-scoped
inside `simulation/runtime/gumas_unified/federated_model.py`.
The module validates unique references, existing actors, origin/target
path direction, due times, bounded terms, fingerprint, physically
delivered member knowledge, status progression, and matching association
origin consent. Event handlers and public functions are in
`federated_actions.py`, with no direct external I/O.

Empty P6 maps `charters`, `associations`, `mandates` are omitted
from `Universe.digest()`. Thus P0–P5 historical fixture hashes
and previously recorded event payload shapes remain unchanged when
the P6 subsystem is not instantiated. The P0 kernel remains sole
world writer; no P3/4/5 institution APIs are replaced.

Review-only `association_view` is not injected into simulated actors'
beliefs. Only typed, physically delivered notices/replies enter
`Actor.received_reports`. State history is deterministic and
SHA256-chained, but self-consistent hashes are **not** authenticated
external source signatures or complete replay certification.

## Reproduction

```sh
python -m unittest discover -s tests -p 'test_gumas_unified*.py' -v
python -m simulation.runtime.gumas_unified.scenario
python -m simulation.runtime.gumas_unified.political_scenario
python -m simulation.runtime.gumas_unified.governance_scenario
python -m simulation.runtime.gumas_unified.distributed_scenario
python -m simulation.runtime.gumas_unified.federated_scenario
```

Acceptance includes all inherited P0–P5 tests plus P6 formation,
notice/response delays, reciprocal consent, declined charter,
founder and invitee knowledge boundaries, remote-origin mandates,
resource and energy conservation, negative/late votes, expiry,
duplicate prevention, unauthorized access, capacity competition,
status and hash validation, replay, and unchanged historical hashes.

## Limits and next integration gate

- Two-member, two-way protocol is a first proof, **not generalized
  multiagent decentralized consensus**, organization history,
  negotiation, governance legitimacy, markets, citizenship,
  evolving territory, interstellar FTL or dynamic actor migration.
- No true signing/authentication of voter credentials. External
  identity references remain synthetic P2, never source canon.
- No live L1 tasking or L3 authority enforcement. Historical P3–P5
  Codacy quality findings remain merge blockers until resolved or
  independently dispositioned; P6 code gets its own static gates.
- The P0 clock remains whole-second; P2 tactical millisecond
  references remain nonexecuting. No shared real-time/canonical
  timeline alignment has been authorized.
- A remote member's association formation knowledge requires a
  confirmation signal; no omniscient observer state is treated
  as the actor's knowledge.
- An authorized association does not change site custody or
  property law; the receipt reports both independent permissions.
- No claim of empirical, canonical political validity is made;
  any civilization/organization in canon requires separate
  source-grounded explanatory reconstruction.
- Before merge: independent review, P0–P6 regression, inherited
  P3/P4/P5 quality gates, CloudBank/root provenance alignment,
  branch protection and CanonRec authority review. No bypass.
