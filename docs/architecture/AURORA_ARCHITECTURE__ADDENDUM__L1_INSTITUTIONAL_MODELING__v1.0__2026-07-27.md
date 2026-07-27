# L1 Institutional Modeling Addendum

**Document ID:** `AURORA_ARCHITECTURE__ADDENDUM__L1_INSTITUTIONAL_MODELING`  
**Version:** v1.0  
**Date:** 2026-07-27  
**Authority:** Orion Station Architecture Council / Operator Decision  
**Status:** Proposed canon until merged  
**Amends:** `docs/architecture/LAYER_ARCHITECTURE.md`  
**Related:** `aurora-cloudbank-symbolic#1350`, `Aurora_ORIONCORE_Directory_Main#44`

---

## 1. Purpose

`LAYER_ARCHITECTURE.md` correctly separates L1 Orion Station operations from L2 GUMAS and experimental scenario environments. Its statement that L1 entities have physical location was written to settle entity residency—especially relay agents—not to prohibit L1 systems from deterministically modeling institutional workflows.

This addendum defines that missing distinction.

Aurora may execute a deterministic model of a real institutional process in L1 when the model is an operational control activity about Aurora's real repository, systems, evidence, approvals, or readiness. The resulting event records are L1 operational records.

The simulated roles and interactions represented inside that event are **not** physical L1 entities. They are explicitly typed `simulated_role` fixtures and have no Orion Station location, staff-registry identity, or real-world agency.

---

## 2. Two Different Uses of Simulation

### 2.1 L1 institutional modeling

An L1 institutional model rehearses or tests an operational workflow such as:

- external security-review preparation,
- internal red-team process,
- incident response,
- audit and approval chains,
- evidence custody,
- vendor-selection procedure,
- remediation and retest governance.

Its object is the real Aurora operational system and its institutional controls. Its output is used by L1 operators to improve actual readiness, scope, evidence handling, issues, and remediation.

The **execution, provenance, decisions, and retained artifacts** are L1 operational state. The represented assessor, vendor, committee member, or signature is a simulation fixture—not an ontological inhabitant of Orion Station.

### 2.2 L2 scenario-world simulation

L2 contains computational environments whose modeled world or scenario has its own state, entities, events, or experimental dynamics, including GUMAS, hypothetical geopolitical scenarios, temporal models, and research simulations.

L2 outputs may inform L1, but their in-world state remains L2.

---

## 3. Classification Test

Classify an activity as L1 institutional modeling only when all of the following are true:

1. The modeled workflow governs or evaluates an actual Aurora operational surface, repository baseline, control, approval path, or engagement-readiness process.
2. The accountable operator, invoking system, baseline commit, evidence chain, and output repository are identified.
3. The event does not instantiate a persistent scenario world or autonomous fictional institution.
4. Simulated participants are typed as `simulated_role` and are not entered into the L1 staff or entity registries.
5. The output directly supports L1 operational action such as issue creation, remediation, retesting, scope preparation, or control improvement.
6. The artifact preserves execution mode and does not claim real-world interaction.

If the modeled environment has autonomous scenario state, in-world actors, fictional continuity, or experimental world dynamics, classify that environment as L2.

---

## 4. Residency and Representation

For L1 institutional modeling:

| Component | Classification |
|---|---|
| Operator, runtime, repository baseline, and evidence custody | L1 operational state |
| Deterministic event envelope and output artifacts | L1 operational records |
| Simulated assessor, vendor, agency, committee, or approver | `simulated_role` representation; no physical residency |
| Real verified internal participant | L1 real-world/internal participant |
| Real verified external participant | L1 external-engagement participant, supported by external evidence |
| Hypothetical world, GUMAS polity, or autonomous scenario actor | L2 |

A `simulated_role` is not an L1 person or entity merely because the event record is L1. It must not receive a deck location, registry ID, biography, credential, or real signature.

---

## 5. Data and Authority

A deterministic L1 institutional event may be committed canon and first-class operational data. This means it is retained, queried, replayed, compared, and used in normal issue and remediation workflows.

Its evidence authority remains `operational_simulation_evidence`. That authority can support claims about the simulation run, the tested workflow, reproduced technical behavior, and capability readiness. It cannot support claims that a real firm, agency, assessor, regulator, or independent reviewer acted.

The label protects provenance without reducing the data's operational standing.

---

## 6. Gate-001 Application

- **Gate-001A** is L1 institutional modeling: deterministic security-review workflow capability using `simulated_role` participants and first-class operational records.
- **Gate-001B** is an L1 real-world external engagement supported by independently attributable external evidence.

Gate-001A and Gate-001B concern the same institutional domain, but they are separate evidence events. Gate-001A does not become L2, and it does not substitute for Gate-001B.

---

## 7. Canon Reconciliation

Read `LAYER_ARCHITECTURE.md` as follows after this addendum:

- “Everything in L1 has a physical location” applies to **resident entities and infrastructure**.
- It does not require every data structure, process model, rehearsal record, or represented role to be a physical entity.
- L1 systems may create operational models and records while remaining accountable for their provenance.
- Represented simulated roles are not resident entities.
- L2 remains the home of scenario-world and experimental simulation state.

This addendum does not move GUMAS, research simulations, hypothetical worlds, or autonomous scenario actors into L1.

---

## 8. Hard Rules

- L1 institutional modeling is an operational process classification, not a claim that simulated participants physically exist.
- Simulated roles never enter the L1 staff registry.
- L1 event records preserve first-class data treatment and explicit simulated provenance.
- L2 scenario state remains L2.
- No simulated event may claim real-world external interaction or independent assurance.
- A different execution mode requires a new evidence event, not relabeling.
