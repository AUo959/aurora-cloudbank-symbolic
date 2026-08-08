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

This addendum defines the permanent boundary between a human user operating Aurora from Earth and Orion Station's L1 reality layer.

The central rule is absolute:

> **A user cannot physically manifest in L1.**

The user is Earth-based and external to Orion Station. The user may communicate with Orion Station, its people, and its systems through defined communications interfaces, but the user never becomes a physical character, avatar, proxy body, camera-person, crew member, visitor, or other embodied entity aboard Orion Station.

This is an architectural boundary, not a narrative preference and not a run-specific convention.

---

## 2. Canonical Role of `Pilot`

`src/mesh/models.py` defines `pilot` / `Pilot` as the canonical sender identity for user-originated mesh messages. That identity is an **interface role**.

`Pilot` MUST NOT be interpreted as:

- an L1 human entity;
- an Orion Station crew role;
- a station visitor;
- a physical observer aboard the station;
- a remotely embodied surrogate;
- a character whose location is tracked in station space;
- a command billet merely because the interface can send requests.

The CanonRec Orion entity registry does not contain a Pilot entity. That absence is correct and intentional under this boundary.

The clean relationship is:

```text
Earth-based user / Pilot
          │
          │ communications, requests, telemetry, reports
          ▼
Aurora communications / mesh boundary
          │
          ▼
Orion Station L1
```

`Pilot` is therefore a communications/interface identity for an external Earth-based human operator.

---

## 3. L1 Residency Rule

L1 is the Orion Station physical reality layer. Resident L1 entities and infrastructure have physical location on or with Orion Station.

The Earth-based user is **outside L1**.

No runtime, narrative layer, simulation adapter, UI, agent, or orchestration process may create a physical L1 representation of the user merely to provide an interaction point.

Prohibited representations include:

- assigning the user a deck, room, seat, terminal location, quarters, body, uniform, rank, or duty shift;
- narrating the user walking, standing, sitting, boarding, following, touching, observing with unaided senses, or otherwise acting physically on Orion Station;
- creating an L1 NPC, avatar, holographic stand-in, telepresence body, or proxy character that is treated as the user unless a separate future canon decision explicitly defines a real technological system with a different entity identity;
- treating a change in chat viewpoint as physical movement by the user;
- inferring physical access or command authority from the ability to send a message.

A user remains Earth-based even when communication with Orion is immediate, conversational, or high-bandwidth.

---

## 4. Communications Semantics

A user message is **external communications traffic addressed to Orion Station**.

The message may become an L1 event when it is received, routed, recorded, answered, deferred, forwarded, ignored, or acted upon by an L1 person or system. The sender does not thereby become an L1 entity.

The existing mesh runtime already supports this separation:

- `MeshMessageRequest` carries `sender_id`, `sender_name`, content, target, channel, and message type;
- `MeshRuntime.send_message()` persists and routes the communication;
- station agents may reply through routed channels;
- the message and reply are records of communication, not evidence of sender residency.

### 4.1 Examples

Earth user:

> Tell Commander Thorne I think the maintenance schedule is too aggressive.

Correct interpretation:

1. An Earth-originated message is routed toward the appropriate Orion recipient or communications channel.
2. The message becomes available according to the station's actual communications and institutional conditions.
3. Commander Thorne may read, defer, forward, answer, disregard, or act on it according to his own priorities and circumstances.
4. Any reply is transmitted back to Earth.

Incorrect interpretation:

- Commander Thorne appears beside the user;
- the user is placed on the bridge;
- the message is converted into a face-to-face conversation;
- station activity reorganizes itself to make the user the center of the scene.

---

## 5. Orion Autonomy and Non-Centrality

Orion Station is the subject of the L1 simulation. The user is not.

Orion personnel, systems, institutions, schedules, relationships, maintenance cycles, research, disagreements, failures, routines, and external obligations continue independently of user attention.

The runtime MUST NOT optimize the station around Pilot engagement.

### 5.1 Non-centrality invariant

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

merely because the user is watching, asking for a view, or has become inactive.

A quiet period remains quiet if station conditions produce a quiet period.

User silence is valid. Orion continues.

### 5.2 No video-game causality

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

## 6. Observation Is Instrumentation, Not Embodiment

An Earth-based user may ask Aurora to expose an observation window into the simulation.

Examples:

- "Show me what is happening on Deck D this morning."
- "Keep the observation aperture with Engineering for a while."
- "What is the station recording around the docking arms?"
- "Continue."

These requests control **runtime observation**, not a physical user camera or body.

A change in observational focus does not cause a character to notice the user and does not imply that the user traveled to the observed location.

Observation requests must not force interesting activity to occur at the selected location.

---

## 7. Epistemic Separation

The runtime must preserve distinct knowledge layers:

| State | Meaning |
|---|---|
| **L1 world state** | What actually exists or occurs in the simulation run |
| **Character knowledge** | What a specific Orion person or system knows or believes |
| **Station-recorded state** | Sensors, logs, messages, reports, institutional records |
| **Runtime observation** | What the research/orchestration layer exposes for examination |
| **Pilot knowledge** | What has actually been communicated or shown to the Earth-based user |

These states are not interchangeable.

A sensor reading is not automatically objective truth. A character statement is not automatically confirmed fact. Runtime instrumentation may expose information that no single character knows, but it must be presented as instrumentation rather than as the Pilot physically witnessing the event.

---

## 8. Turn-Based Runtime Semantics

For live interactive L1 runs, a "turn" is a **simulation advancement boundary**, not a conventional player turn.

A recommended cycle is:

1. **Advance autonomous world state.** Scheduled work, ongoing processes, character activity, institutional pressures, communications, and applicable stochastic mechanics resolve.
2. **Propagate consequences.** Systems update and people learn information when plausible.
3. **Expose an observation aperture.** Present a coherent sample of what happened based on observational focus, permissions, and available records.
4. **Process external Pilot input.** Observation requests, questions, or Earth-originated messages are handled through their proper interfaces.
5. **Advance again.** The station continues independently.

Pilot input does not automatically constitute an L1 physical action.

---

## 9. Authority Boundary

The ability to communicate with Orion does not itself grant L1 command authority.

A Pilot message may be:

- informational;
- conversational;
- advisory;
- a request;
- a question;
- an instruction to Aurora's Earth-facing runtime;
- an authorized operational directive where a separate established authority contract explicitly permits one.

The receiving L1 institution determines what effect, if any, the communication has according to canon, role authority, security, ethics, and current circumstances.

No runtime may infer a station rank, clearance, chain-of-command position, or physical access right solely from `sender_id="pilot"`.

---

## 10. Distinction from Simulated Roles

The L1 Institutional Modeling Addendum defines non-physical `simulated_role` fixtures that may appear inside deterministic L1 operational models.

The Pilot is different.

- A `simulated_role` is a modeled participant inside a governed institutional rehearsal.
- The Pilot is the real external user-interface identity through which an Earth-based human communicates with Aurora.
- Neither category is a resident L1 person.
- Neither category may be silently promoted into the Orion staff/entity registry.

---

## 11. Implementation Guidance

### 11.1 Runtime/UI

Interfaces SHOULD label user-originated traffic as Earth/external/Pilot communications where context requires clarity.

Interfaces MUST NOT render the Pilot as having an Orion physical location.

### 11.2 Mesh

`sender_id="pilot"` and `sender_name="Pilot"` remain valid for user-originated mesh traffic.

Their meaning is constrained by this document: **external Earth-based communications identity only**.

### 11.3 Character and entity systems

Character loaders, entity registries, crew manifests, terminal directories, and station-location systems MUST NOT create a Pilot character record as a convenience for interactive runs.

### 11.4 Simulation orchestration

Interactive L1 runtimes SHOULD keep world advancement, observation selection, and Pilot communication as separate operations.

A runtime MAY maintain private bookkeeping for Pilot communications and observation preferences. Such bookkeeping is runtime/interface state, not L1 physical state.

---

## 12. Hard Rules

1. **The user is Earth-based and external to L1.**
2. **A user is never physically represented in L1.**
3. **`Pilot` is an interface/communications identity, not an Orion character.**
4. **Communication with Orion does not imply physical presence on Orion.**
5. **Observation focus is instrumentation, not movement or embodiment.**
6. **The station continues autonomously whether or not the user is interacting.**
7. **The simulation does not center events, pacing, characters, or drama around the user.**
8. **User messages enter L1 only as external communications or requests, subject to routing and institutional response.**
9. **Pilot identity alone grants no station rank, physical access, or command authority.**
10. **World state, character knowledge, station records, runtime observation, and Pilot knowledge remain distinct.**

---

## 13. Runtime Invariant

The following concise invariant may be embedded in future runtime specifications:

```text
PILOT_BOUNDARY:
The Pilot is an Earth-based external human operator. `pilot` is a
communications/interface identity only. The Pilot has no L1 body, location,
station role, physical presence, or automatic command authority. Orion Station
evolves autonomously. Pilot input may observe the simulation or enter L1 only
through explicitly modeled remote communications or external-request channels.

NON_CENTRALITY:
The simulation does not optimize events, pacing, character availability,
dramatic relevance, or institutional behavior around Pilot engagement.
```

---

## 14. Canon Reconciliation

Read `LAYER_ARCHITECTURE.md` with this addendum as follows:

- L1 physical residency applies to Orion Station entities and infrastructure.
- The Earth-based user is not an L1 resident entity.
- The communications mesh can carry external user messages without creating a physical sender inside Orion.
- `Pilot` in runtime code names the user-facing communications role; it does not establish ontological residency.
- No interactive simulation convention may override this boundary by inventing a user avatar or physical point of view inside L1.

This addendum does not alter the L1/L2/L3 layer definitions, Orion character canon, or CanonRec entity authority. It clarifies the external human-interface boundary around them.
