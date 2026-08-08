# Earth Pilot ↔ Orion L1 Communication Boundary Addendum

**Document ID:** `AURORA_ARCHITECTURE__ADDENDUM__EARTH_PILOT_L1_BOUNDARY`  
**Version:** v1.0  
**Date:** 2026-08-07  
**Authority:** Operator Decision / Orion Station Architecture Council  
**Status:** Proposed canon until merged  
**Amends:** `docs/architecture/LAYER_ARCHITECTURE.md`  
**Related implementation:** `src/mesh/models.py`, `src/mesh/runtime.py`, `config/mesh/terminals/l1_terminal_registry.v1.json`  
**Related canon authority:** CanonRec `ORION__ENTITY_REGISTRY__v1.0.md`

---

## 1. Purpose

This addendum defines the permanent boundary between Earth-based human operators and Orion Station's L1 reality layer, and it defines the institutional meaning of the title **Pilot**.

Two rules are absolute:

> **A human operator cannot physically manifest in L1.**

> **Pilot is an institutional operator role, not a persona or character.**

A person using an authorized Aurora interface may occupy the Pilot role while communicating with Orion Station, its people, and its systems. That person remains Earth-based and external to Orion Station. The role does not turn the operator into a physical character, avatar, proxy body, camera-person, crew member, visitor, or other embodied entity aboard Orion Station.

This is an architectural and institutional boundary, not a narrative preference and not a run-specific convention.

---

## 2. Canonical Meaning of `Pilot`

`src/mesh/models.py` defines `pilot` / `Pilot` as the canonical sender label for user-originated mesh messages. Under this architecture, that label identifies an **institutional communications position**.

`Pilot` is analogous to a duty title or operator station: a human being may occupy the position, leave it, and be replaced by another authorized human without creating a new Orion character or changing Orion lore.

The personal identity of the individual occupying the position is separate from the role itself.

### 2.1 Pilot is a role, not a person

The system MUST NOT assume that Pilot:

- is one permanent individual;
- is the repository owner;
- is the current project's creator;
- is a named real-world person;
- carries a persistent biography, personality, backstory, appearance, or personal history;
- is an L1 human entity;
- is an Orion Station crew member or visitor;
- has a station location, body, uniform, quarters, or duty shift aboard Orion;
- has command authority merely because the communications interface can send requests.

A different human operator may occupy the Pilot position in another session, shift, deployment, or institutional context. The title remains **Pilot** unless a separate interface contract establishes another operator role.

The role therefore supports operator interchangeability without identity drift.

### 2.2 Personal identity is not canonized by role occupancy

Occupying the Pilot position does not cause the operator's real-world identity to become Orion canon.

An implementation may authenticate, audit, or attribute a real operator according to its security requirements, but such identity records belong to the external operational/authentication domain. They do not become an Orion character biography, entity record, or narrative identity merely because that person used the Pilot interface.

If an operator voluntarily identifies themselves in a message, Orion may receive that information as communications content. That still does not create an L1 embodiment or automatically create a canonical Orion entity.

### 2.3 CanonRec omission is intentional

The CanonRec Orion entity registry does not contain a Pilot entity. That absence is correct.

Pilot is a **position at the external institutional boundary**, not an inhabitant of the station and not a lore entity requiring an Orion entity ID.

The relationship is:

```text
Earth-based human operator
          │
          │ occupies institutional role
          ▼
       PILOT
  (operator position)
          │
          │ communications, requests, telemetry, reports
          ▼
Aurora communications / mesh boundary
          │
          ▼
Orion Station L1
```

The human and the role must not be collapsed into one fictional persona.

---

## 3. L1 Residency Rule

L1 is the Orion Station physical reality layer. Resident L1 entities and infrastructure have physical location on or with Orion Station.

The human occupying the Pilot role is **outside L1 and located on Earth**.

No runtime, narrative layer, simulation adapter, UI, agent, or orchestration process may create a physical L1 representation of that operator merely to provide an interaction point.

Prohibited representations include:

- assigning the operator a deck, room, seat, terminal location, quarters, body, uniform, rank, or duty shift on Orion;
- narrating the operator walking, standing, sitting, boarding, following, touching, observing with unaided senses, or otherwise acting physically on Orion Station;
- creating an L1 NPC, avatar, holographic stand-in, telepresence body, or proxy character that is treated as the operator unless a separate future canon decision defines a real technological system with a distinct entity identity;
- treating a change in chat viewpoint as physical movement by the operator;
- inferring physical access or station command authority from occupancy of the Pilot role.

The operator remains Earth-based even when communication with Orion is immediate, conversational, or high-bandwidth.

---

## 4. Communications Semantics

A Pilot message is **external communications traffic from an Earth-based operator position to Orion Station**.

The message may become an L1 event when it is received, routed, recorded, answered, deferred, forwarded, ignored, or acted upon by an L1 person or system. The operator does not thereby become an L1 entity.

The existing mesh runtime already supports the structural separation:

- `MeshMessageRequest` carries `sender_id`, `sender_name`, content, target, channel, and message type;
- `sender_id="pilot"` / `sender_name="Pilot"` identify the operator role at the communications boundary;
- `MeshRuntime.send_message()` persists and routes communications;
- station agents may reply through routed channels;
- message and reply records establish communication, not sender residency or personal identity.

The literal string `Pilot` should therefore be read as a **role label**, not a proper name.

### 4.1 Example

Pilot transmission:

> Tell Commander Thorne I think the maintenance schedule is too aggressive.

Correct interpretation:

1. A human operator occupying the Pilot position sends an Earth-originated message.
2. The message is routed toward the appropriate Orion recipient or communications channel.
3. It becomes available according to the station's actual communications and institutional conditions.
4. Commander Thorne may read, defer, forward, answer, disregard, or act on it according to his own priorities and circumstances.
5. Any reply is transmitted back through the communications boundary to the Pilot position and therefore to its current operator.

Incorrect interpretation:

- Commander Thorne appears beside the operator;
- the operator is placed on the bridge;
- the operator becomes a named Orion character;
- a prior operator's personal traits are automatically transferred to the current operator;
- the transmission is converted into a face-to-face conversation;
- station activity reorganizes itself to make Pilot the center of the scene.

---

## 5. Institutional Role Separation

Pilot is a position in the external Aurora operating institution.

The architecture separates at least four concepts:

| Concept | Meaning |
|---|---|
| **Human operator** | The real Earth-based person currently using the interface |
| **Pilot role** | The institutional position through which authorized operator communications are represented |
| **Pilot session/runtime state** | External bookkeeping such as current connection, observation preferences, message history, or authentication context |
| **Orion L1 entity** | A physically instantiated person, system, vessel, or infrastructure entity in Orion Station reality |

These concepts MUST NOT be merged for narrative convenience.

In particular:

- role continuity does not imply personal continuity;
- session continuity does not establish a fictional biography;
- operator authentication does not establish Orion residency;
- a message signed `Pilot` identifies the institutional sending position, not necessarily a specific named person;
- Orion personnel may address the external position as “Pilot” without treating Pilot as a station character.

### 5.1 Operator substitution

A runtime must be able to replace one human operator with another without requiring changes to L1 canon.

Changing the operator may change external authorization, communication style, or attributable audit metadata according to applicable systems. It does not rewrite Orion history and does not create a new L1 entity.

This is one reason the Pilot title must remain institutionally defined rather than personalized.

---

## 6. Orion Autonomy and Non-Centrality

Orion Station is the subject of the L1 simulation. Pilot is an external operating position, not the protagonist of Orion.

Orion personnel, systems, institutions, schedules, relationships, maintenance cycles, research, disagreements, failures, routines, and external obligations continue independently of Pilot attention.

The runtime MUST NOT optimize the station around Pilot engagement.

### 6.1 Non-centrality invariant

The simulation must not alter or preferentially generate:

- events;
- pacing;
- character availability;
- dramatic relevance;
- emergencies;
- interpersonal encounters;
- institutional decisions;
- discoveries;
- convenient explanations;

merely because Pilot is watching, asking for a view, or inactive.

A quiet period remains quiet if station conditions produce a quiet period.

Operator silence is valid. Orion continues.

### 6.2 No video-game causality

The runtime must avoid the causal pattern:

```text
Pilot input → world arranges itself around Pilot → content generated for engagement
```

The preferred causal pattern is:

```text
world state → autonomous events → legitimate observation/communication → Pilot receives information
```

Pilot communications may causally affect L1 only in the ordinary sense that real external communications can affect the actions of people and institutions that receive them.

---

## 7. Observation Is Instrumentation, Not Embodiment

An operator occupying the Pilot position may ask Aurora to expose an observation window into the simulation.

Examples:

- "Show me what is happening on Deck D this morning."
- "Keep the observation aperture with Engineering for a while."
- "What is the station recording around the docking arms?"
- "Continue."

These requests control **runtime observation**, not a physical Pilot camera or body.

A change in observational focus does not cause a character to notice Pilot and does not imply that the operator traveled to the observed location.

Observation requests must not force interesting activity to occur at the selected location.

---

## 8. Epistemic Separation

The runtime must preserve distinct knowledge layers:

| State | Meaning |
|---|---|
| **L1 world state** | What actually exists or occurs in the simulation run |
| **Character knowledge** | What a specific Orion person or system knows or believes |
| **Station-recorded state** | Sensors, logs, messages, reports, institutional records |
| **Runtime observation** | What the research/orchestration layer exposes for examination |
| **Pilot-position knowledge** | What has been transmitted or exposed through the Pilot interface during the current operational context |
| **Operator personal knowledge** | Knowledge held by the real human operator outside the modeled Orion system |

These states are not interchangeable.

A sensor reading is not automatically objective truth. A character statement is not automatically confirmed fact. Runtime instrumentation may expose information that no single character knows, but it must be presented as instrumentation rather than as the operator physically witnessing the event.

A replacement operator may inherit authorized session records or institutional logs without inheriting the previous operator's personal identity, beliefs, or biography.

---

## 9. Turn-Based Runtime Semantics

For live interactive L1 runs, a "turn" is a **simulation advancement boundary**, not a conventional player turn.

A recommended cycle is:

1. **Advance autonomous world state.** Scheduled work, ongoing processes, character activity, institutional pressures, communications, and applicable stochastic mechanics resolve.
2. **Propagate consequences.** Systems update and people learn information when plausible.
3. **Expose an observation aperture.** Present a coherent sample of what happened based on observational focus, permissions, and available records.
4. **Process external Pilot input.** Observation requests, questions, or Earth-originated messages are handled through their proper interfaces.
5. **Advance again.** The station continues independently.

Pilot input does not automatically constitute an L1 physical action.

---

## 10. Authority Boundary

The Pilot title describes an operating position. It does **not**, by itself, define the full authority of whoever occupies it.

A Pilot transmission may be:

- informational;
- conversational;
- advisory;
- a request;
- a question;
- an instruction to Aurora's Earth-facing runtime;
- an authorized operational directive where a separate established authority contract explicitly permits one.

The receiving L1 institution determines what effect, if any, the communication has according to canon, role authority, security, ethics, and current circumstances.

No runtime may infer a station rank, clearance, chain-of-command position, physical access right, or personal identity solely from `sender_id="pilot"`.

Authentication, operator assignment, authorization, and audit attribution are separate institutional concerns. This document does not fabricate those mechanisms where they are not implemented.

---

## 11. Distinction from Simulated Roles and Characters

The L1 Institutional Modeling Addendum defines non-physical `simulated_role` fixtures that may appear inside deterministic L1 operational models.

Pilot is different from both a simulated role fixture and an Orion character.

- A `simulated_role` is a modeled participant inside a governed institutional rehearsal.
- An Orion character is an L1 resident entity with station identity and physical residency.
- Pilot is an external institutional operator position used by a real Earth-based human to communicate with Aurora and Orion.
- None of these categories may be silently converted into another.

Pilot therefore belongs to **institutional interface architecture**, not character lore.

---

## 12. Implementation Guidance

### 12.1 Runtime/UI

Interfaces SHOULD label Pilot-originated traffic as Earth/external/operator communications where context requires clarity.

Interfaces MUST NOT render Pilot as having an Orion physical location or persistent fictional persona.

Interfaces SHOULD avoid using a real operator's personal name as though it were synonymous with the Pilot role unless a separate display/audit requirement explicitly calls for attribution.

### 12.2 Mesh

`sender_id="pilot"` and `sender_name="Pilot"` remain valid for operator-originated mesh traffic.

Their meaning is constrained by this document: **external Earth-based institutional operator role**.

The fields identify the sending role by default; they do not, on their own, prove which human occupies that role or what authority that human holds.

### 12.3 Character and entity systems

Character loaders, entity registries, crew manifests, terminal directories, and station-location systems MUST NOT create a Pilot character record as a convenience for interactive runs.

They also MUST NOT create character records for individual Pilot operators merely because those humans communicate with Orion.

### 12.4 Simulation orchestration

Interactive L1 runtimes SHOULD keep world advancement, observation selection, operator-session state, and Pilot communications as separate operations.

A runtime MAY maintain external bookkeeping for operator authentication, Pilot communications, observation preferences, and audit attribution. Such bookkeeping is institutional/runtime state, not L1 physical state and not Orion lore.

---

## 13. Hard Rules

1. **Pilot is an institutional operator title, not a persona, character, or proper name.**
2. **The human occupying the Pilot position is Earth-based and external to L1.**
3. **No human operator is ever physically represented in L1 by virtue of using the Pilot interface.**
4. **Different authorized humans may occupy the Pilot position without changing Orion canon.**
5. **Occupying Pilot does not canonize the operator's biography, personality, appearance, or personal identity.**
6. **`pilot` / `Pilot` identifies an external communications role, not an Orion entity.**
7. **Communication with Orion does not imply physical presence on Orion.**
8. **Observation focus is instrumentation, not movement or embodiment.**
9. **Orion continues autonomously whether or not Pilot is interacting.**
10. **The simulation does not center events, pacing, characters, or drama around Pilot.**
11. **Pilot messages enter L1 only as external communications or requests, subject to routing and institutional response.**
12. **Pilot title alone grants no station rank, physical access, personal identity, or command authority.**
13. **World state, character knowledge, station records, runtime observation, Pilot-position knowledge, and operator personal knowledge remain distinct.**

---

## 14. Runtime Invariants

The following concise invariants may be embedded in future runtime specifications:

```text
PILOT_ROLE:
Pilot is an institutional Earth-side operator position, not a persona or
character. A human may occupy the position without becoming Orion canon.
Different authorized humans may occupy Pilot across sessions or shifts without
creating identity continuity between them.

PILOT_BOUNDARY:
The human occupying Pilot remains Earth-based and external to L1. Pilot has no
L1 body, location, physical presence, or automatic station authority. Pilot
input reaches Orion only through explicitly modeled communications,
observation, or external-request channels.

IDENTITY_SEPARATION:
The role label `Pilot` is not the operator's personal identity. Authentication,
audit attribution, and operator identity are external institutional state and
must not be converted into an Orion character or biography.

NON_CENTRALITY:
The simulation does not optimize events, pacing, character availability,
dramatic relevance, or institutional behavior around Pilot engagement.
```

---

## 15. Canon Reconciliation

Read `LAYER_ARCHITECTURE.md` with this addendum as follows:

- L1 physical residency applies to Orion Station entities and infrastructure.
- Human operators occupying external interface roles remain outside L1.
- The communications mesh can carry Pilot messages without creating a physical sender inside Orion.
- `Pilot` in runtime code names an institutional Earth-side operator position; it does not establish a unique persona, ontological residency, or permanent individual identity.
- The individual occupying Pilot may change without changing Orion canon.
- Pilot should not be added to the Orion entity registry merely to support interaction.
- No interactive simulation convention may override this boundary by inventing a user avatar, Pilot avatar, or physical point of view inside L1.

This addendum does not alter the L1/L2/L3 layer definitions, Orion character canon, or CanonRec entity authority. It clarifies the institutional human-interface boundary around them.
