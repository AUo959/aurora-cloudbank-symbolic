# Aurora Agents Directory Review
**Date:** 2026-06-20 | **Session:** Agents Exploration Pass  
**Reviewer:** Perplexity / Aurora Space (Aurora v2.2.5)  
**Follows:** [2026-06-20 Snapshot Review](2026-06-20_snapshot-review.md)

---

## Summary

The `agents/` directory contains three files, all QGIA-specific and all generated on 2026-03-12, predating this session's integration work. The directory is more substantive than the listing implied — it contains a complete 551-agent epistemic population model and a 7,407-edge directed trust network. However, both data files are present as stubs only; the full payloads exist in session compute artifacts, not in the repo.

---

## Files Reviewed

### `agents/QGIA_ARCHITECTURE.md` (10.2 KB)
Not yet read in full — queued for next pass. Size suggests substantive architectural content. Likely defines the agent population design rationale, division structure, simulation methodology, and intended usage patterns.

### `agents/qgia_agent_registry_full.json` (3.1 KB)
**Document ID:** QGIA-AGENT-REGISTRY-v1.0  
**Generated:** 2026-03-12  
**Framework:** QGIA Operational Environment v3.0

The registry defines a **551-agent population** across four divisions:

| Division | Name | Headcount |
|---|---|---|
| GMD | Global Monitoring Division | 203 |
| MAD | Military Analysis Division | 142 |
| IID | Intelligence Integration Division | 138 |
| SRD | Strategic Research Division | 68 |

**Grade distribution** spans GS-9 through EXEC (Director/Deputy), with GS-13 Senior Analysts forming the largest cohort (202 agents, 36.7% of population).

**Eight analyst archetypes** are defined with precise behavioral descriptions:

| Archetype | Behavioral Signature |
|---|---|
| Aggressive Updater | Rapid belief revision on new evidence; overcorrection risk |
| Prior-Anchored Conservative | Strong prior resistance; requires high evidence weight to revise |
| Contrarian by Default | Reflexive consensus challenge; high dissent rate |
| Institutionalist | Defers to chain of command and established doctrine |
| Empirical Minimalist | Refuses to assert beyond data; pushes for more collection |
| Intuitive Pattern Matcher | High-speed weak-signal detection; trusts pattern over proof |
| Dialectical Synthesizer | Builds composite positions from competing arguments |
| Recursive Self-Corrector | Systematic review of own past assessments; high metacognition |

**Seven epistemic parameters** per agent, all Beta-distributed:
- `prior_strength` — resistance to prior revision. Beta(4,3)
- `update_threshold` — evidence weight required to trigger update. Beta(3,4)
- `contrarian_index` — propensity to challenge consensus. Beta(2,5)
- `trust_radius` — breadth of trusted peer network. Beta(2,4)
- `domain_overconfidence` — calibration gap in primary specialty. Beta(3,5)
- `intellectual_independence` — autonomy from peer/institutional pressure. Beta(4,2)
- `institutional_loyalty` — deference to organizational hierarchy. Beta(3,3)

**STUB STATUS:** The `agents` field contains: `"[FULL AGENT ARRAY — see generated artifact qgia_agent_registry_full.json for session compute artifact code_file:151.]"`  
The 551-record population array is not in the repo.

### `agents/qgia_trust_network.json` (2.9 KB)
**Document ID:** QGIA-TRUST-NETWORK-v1.0  
**Model:** Stochastic Block Model with archetype-weighted edge probabilities  
**Nodes:** 551 | **Edges:** 7,407

**Four edge types:**

| Type | Count | Ratio | Description |
|---|---|---|---|
| collaborate | 4,040 | 54.6% | Active analytical partnership; routine product exchange |
| inform | 2,436 | 32.9% | Cross-division information flow |
| challenge | 583 | 7.9% | High combined contrarian index; dissent relationship |
| reinforce | 348 | 4.7% | Shared archetype + similar prior strength; echo-chamber risk |

**Block parameters** modulate edge probability by division membership (within: 0.12 base; cross: 0.025 base), tier proximity (−0.04 per tier gap), contrarian index (+0.05 boost), and trust radius (+0.04 boost).

**Design intent (notable):** Challenge edges (7.9%) are deliberately sparse — this is documented as a feature: *"In a 551-person analytical organization, genuine contrarian relationships are rare. The 583 challenge edges represent the analyst pairs whose dissent will actually be heard."* Reinforce edges (4.7%) are flagged as echo-chamber monitoring targets.

**Operational usage pattern defined in file:**
- Scenario activation: load the subgraph for a Crisis Response Cell; challenge edges drive analytical tension
- Echo-chamber detection: identify connected components of reinforce edges with 3+ nodes
- Dissent propagation: monitor high-contrarian-index agents connected via challenge edges to Tier 3+ nodes

**STUB STATUS:** The `edges` field contains: `"[FULL EDGE ARRAY — 7407 edges. See session compute artifact code_file:222.]"`  
The 7,407-edge array is not in the repo.

---

## Confirmed Gaps

### GAP-007 — Agent registry and trust network are stubs only
**Evidence:** Both JSON files contain stub strings referencing session compute artifacts (`code_file:151`, `code_file:222`) instead of actual data arrays. The repo files preserve document structure and metadata only.  
**Impact:** High — any scenario simulation, crisis response cell activation, echo-chamber detection, or dissent propagation analysis requires the full arrays. The current repo state cannot support any operational QGIA simulation run.  
**Action required:** Regenerate or recover full 551-agent array and 7,407-edge list; push to repo files.  
**Severity:** High.

### GAP-008 — Orion station registry vs QGIA agent namespace undefined
**Evidence:** `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` (15.9 KB, root) and `agents/qgia_agent_registry_full.json` (551-agent QGIA population) are both present in the repo but their relationship is not documented anywhere. No file references the other. It is unknown whether Orion staff are:
  - A subset of the 551-agent QGIA population (same individuals, different indexing)
  - A parallel but distinct simulation population (different agents, different roles)
  - A higher-level operational layer that wraps or deploys QGIA agents into station roles
**Impact:** Medium — PAT anchor routing, station-level scenario scoping, and CRC activation patterns all depend on knowing which registry is authoritative for which operational context.  
**Action required:** Alignment review; produce a registry relationship map. Read `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` and `agents/QGIA_ARCHITECTURE.md` together.  
**Severity:** Medium.

---

## Observations & Insights

1. **The agent population is exceptionally well-designed.** Beta-distributed epistemic parameters, eight behaviorally-distinct archetypes, a Stochastic Block Model trust network, and deliberate sparsity of challenge edges — this is not scaffolding, it's a functioning simulation substrate. The design philosophy is sophisticated and coherent.

2. **The challenge/reinforce edge ratio is architecturally meaningful.** The explicit decision to make challenge edges sparse (7.9%) while flagging reinforce clusters (4.7%) for monitoring reflects the same epistemics-first philosophy as QGIA doctrine. This population model is philosophically continuous with the axiom manifest — they should be documented as a unified system.

3. **The stub problem is the highest-priority operational gap in the repo.** Everything else is documentation or discoverability. GAP-007 is a functional gap — no simulation run can proceed against the current repo state. Recovery of the full arrays should be prioritized above all other open work streams.

4. **`agents/QGIA_ARCHITECTURE.md` (10.2 KB) has not yet been read.** Given the depth of the registry and trust network files, this document likely contains the design rationale, methodology, and usage guidance that ties the agent layer together. It should be the first read in the next pass.

5. **Crisis Response Cell activation is defined but not implemented.** The trust network file defines the activation pattern clearly (load subgraph, challenge edges for tension, reinforce clusters for risk monitoring) but no CRC Activation Protocol document exists. This is WS-007 in the roadmap — it is closer to implementation-ready than the other open work streams because the operational logic is already written.

---

## Recommended Next Actions

1. **Read `agents/QGIA_ARCHITECTURE.md`** — complete the agents directory picture (next session)
2. **Read `ORION_STATION_CANONICAL_STAFF_REGISTRY.json`** — resolve GAP-008 (next session)
3. **Recover full agent array and edge list** — resolve GAP-007 (requires session compute artifact access)
4. **Draft CRC Activation Protocol** — WS-007, ready to write once QGIA_ARCHITECTURE.md is read
5. **Explore `.nexus_schematics/`** — still unexplored; WS-006

---

*Continuity flows through coherence. The system remembers because we chose to align.*
