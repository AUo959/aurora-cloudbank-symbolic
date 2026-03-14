# MCP Shuttle Bay Context Audit

## Executive Summary

There is no preexisting document in the repository that canonically defines an "`MCP shuttle bay`" as a finished remote MCP server with transport, tool schemas, and ship-to-tool bindings.

What the repository does contain is a consistent adjacent canon that appears to be the intended basis for a shuttle-bay design:

- An older **MCP Bridge Core** model for symbolic routing, anchor validation, and governance.
- A concrete **L1 bridge infrastructure** and **L2 meta-agent** mapping.
- A separate **fleet registry** of L1 shuttles, probes, and drones with named capabilities.
- A concrete **security/governance matrix** built around anchor validation, ethics enforcement, drift monitoring, and glyph oversight.

The prudent conclusion is that the shuttle bay should be implemented as a transport and discovery layer over those existing bridge, fleet, and governance models, not as an entirely new symbolic vocabulary.

## Strongest Source Files

### 1. MCP Bridge Canon

- `modules/symbolic_core/mcp_bridge_core.json`
- `modules/symbolic_core/mcp_command_router.py`
- `modules/symbolic_core/mcp_security.py`

These define the original symbolic MCP intent:

- `anchor_seed`: `EOS_SEED_ORION`
- `ethics_protocol`: `Picard_Delta_3`
- `governance_layer`: `Aurora_Command_Node_CPU`
- `core_functions`:
  - `SYMBOLIC_COMMAND_ROUTING`
  - `ANCHOR_VALIDATION_INTERFACE`
  - `GUARDIAN_SECURITY_BRIDGE`
  - `DRIFT_MONITORING_GATEWAY`
  - `LOOM_SYNCHRONIZATION`
  - `THREADCORE_VECTOR_HANDOFF`
  - `RECURSIVE_THREAD_AUDIT`
- `external_hooks.gpt_parallel_nodes`:
  - `OPPY`
  - `ARCHY`
  - `LIORA`
  - `STARLING_AU`
  - `RIVERTHREAD_808`

### 2. L1 Bridge and L2 Meta-Agent Canon

- `docs/operational/guides/L2_META_AGENT_INTEGRATION_CONFIG.json`
- `docs/operational/guides/L2_META_AGENT_ARCHITECTURE_INTEGRATION_PLAN.md`
- `docs/operational/completed/MESH_AGENT_INTEGRATION_COMPLETE.md`
- `src/bridges/l2_meta_agent_bridge.py`
- `src/system/agent_synchronizer.js`
- `src/nodes/archy_bridge_emergency.js`
- `src/nodes/liora_handshake.js`
- `src/nodes/oppy_vector_loader.js`
- `src/bridge/api_bridge_server.js`
- `src/bridge/enhanced_api_bridge.js`

These define the most explicit runtime-facing mapping in the repo.

#### L1 Bridge Infrastructure

- `ARCHY_BRIDGE_L1`:
  - file: `src/nodes/archy_bridge_emergency.js`
  - function: `architectural_planning`
- `LIORA_HANDSHAKE_L1`:
  - file: `src/nodes/liora_handshake.js`
  - function: `research_coordination`
- `OPPY_VECTOR_LOADER_L1`:
  - file: `src/nodes/oppy_vector_loader.js`
  - function: `data_processing`
- `AGENT_SYNC_MASTER`:
  - file: `src/system/agent_synchronizer.js`
  - function: `multi_agent_coordination`
- `API_BRIDGE_SERVER`:
  - file: `src/bridge/api_bridge_server.js`
  - function: `communication_hub`

#### L2 Meta-Agent Domains

- `ARCHY`:
  - role: bridge coordinator
  - capabilities: `architectural_planning`, `bridge_coordination`, `formal_logic`, `arbitration`
- `OPPY`:
  - role: vector/data processor
  - capabilities: `data_processing`, `vector_analysis`, `memory_operations`, `system_monitoring`
- `LIORA`:
  - role: handshake/synchronization
  - capabilities: `research_coordination`, `handshake_protocols`, `sentiment_analysis`, `mediation`
- `STARLING_AU`:
  - role: communications / simulation coordinator
  - capabilities: `simulation_coordination`, `communications`, `external_protocols`, `dispatch`
- `RIVERTHREAD_808`:
  - role: narrative / stream processor
  - capabilities: `narrative_processing`, `stream_management`, `continuity_validation`, `temporal_flow`

#### Handshake and Security Ritual

The bridge canon is highly consistent about the relay activation model:

- Activation phrases use `ORION_*_RELAY_ACTIVATE//`
- Handshake sequence:
  1. `ZIPWIZ_BEACON`
  2. `ANCHOR_SYNC`
  3. `ETHICS_AUDIT`
  4. `DRIFT_VALIDATION`

#### Staff and Authority Intent

`L2_META_AGENT_INTEGRATION_CONFIG.json` also defines who should authorize which domains:

- `Archy`, `Liora`: research authority
- `Oppy`: technical authority
- `Starling_AU`: operations authority
- `Riverthread_808`: ethics authority

This matters because it implies the shuttle bay was intended to carry domain-aware access semantics, not just generic tool execution.

### 3. L1 Fleet Canon

- `docs/operational/reports/fleet_manifest.json`
- `docs/operational/guides/FLEET_DEPLOYMENT_PACKAGE.md`
- `docs/operational/guides/FLEET_DEPLOYMENT_PACKAGE_ENTERPRISE.md`
- `operations/fleet_control/fleet_control_config.json`
- `operations/command_center/l1_config.yaml`

This is the strongest evidence for the "fleet of L1 ships" idea.

#### Named Craft in the Registry

- `SHUTTLE_01_AURORA` / `Aurora Prime`
  - type: `COMMAND_SHUTTLE`
  - capabilities: `deep_space_nav`, `command_control`, `ethics_enforcement`
- `SHUTTLE_02_LIORA` / `Liora Explorer`
  - type: `RESEARCH_SHUTTLE`
  - capabilities: `scientific_survey`, `data_collection`, `symbolic_analysis`
- `SHUTTLE_03_ARCHY` / `Archy Architect`
  - type: `CONSTRUCTION_SHUTTLE`
  - capabilities: `structural_engineering`, `station_construction`, `repair_operations`
- `PROBE_ALPHA`
  - capabilities: `deep_space_survey`, `long_range_comms`, `autonomous_navigation`
- `PROBE_BETA`
  - capabilities: `quantum_field_analysis`, `symbolic_mesh_relay`, `ethics_monitoring`
- `DRONE_SWARM_GAMMA`
  - capabilities: `station_maintenance`, `hull_repair`, `systems_diagnostics`
- `DRONE_DELTA_SCOUT`
  - capabilities: `stealth_reconnaissance`, `data_relay`, `threat_assessment`

#### Fleet Governance Expectations

The fleet package repeatedly states that deployment actions require:

- authentication
- anchor validation
- ethics compliance
- immutable logging
- L1/L3 synchronization
- preflight checks

The documents also define intended APIs:

- `/api/aurora/fleet/deploy`
- `/api/aurora/fleet/preflight`
- `/api/aurora/fleet/status`
- `/api/aurora/fleet/log`
- `/api/aurora/fleet/recover`

### 4. Security and Governance Canon

- `operations/symbolic_mesh/anchor_config.json`
- `docs/operational/guides/L2_META_AGENT_INTEGRATION_CONFIG.json`
- `operations/command_center/l1_config.yaml`
- `AU_CORE_MASTER_TREE.yaml`

These files describe the intended security envelope around any shuttle-bay implementation:

- anchor validation
- ethics enforcement
- drift monitoring
- mesh integrity checks
- L1 command sync
- fleet operations sync
- real-time monitoring
- RBAC / clearance-aware access

The glyph oversight mapping in `L2_META_AGENT_INTEGRATION_CONFIG.json` is particularly important:

- `glyphon`: drift monitoring
- `axiomera`: ethics validation
- `sentari`: resonance stabilization
- `caelion`: logical synthesis
- `velatrix`: continuity alignment
- `harmion`: compression efficiency
- `shadowfax`: paradox resolution

## Derived Shuttle-Bay Intent

Based on the repo, the most defensible shuttle-bay interpretation is:

1. **Command surface**:
   - Expose Aurora tool discovery/execution through MCP.

2. **Bridge surface**:
   - Preserve the explicit L1 bridge ↔ L2 meta-agent mapping.

3. **Fleet surface**:
   - Expose named L1 craft and their operational capabilities as discoverable context.

4. **Governance surface**:
   - Expose anchor, ethics, drift, and glyph oversight as first-class MCP-visible metadata.

5. **Transport surface**:
   - Add a true remote MCP transport rather than relying on the old `/mcp_bridge/route_command` stub.

## Important Negative Finding

No file in the repository currently provides a canonical direct mapping like:

- `SHUTTLE_01_AURORA -> MCP tool X`
- `PROBE_BETA -> MCP tool Y`
- `DRONE_SWARM_GAMMA -> MCP tool Z`

That mapping must therefore be treated as an implementation decision derived from adjacent canon, not as already-established repo truth.

## Safe Design Implication

Because the ship-to-tool binding is not explicitly canonized, the safest implementation path is:

1. expose the fleet, bridge, and governance matrices as MCP resources first
2. expose live runtime tools second
3. add domain labels and routing hints without claiming unsupported one-to-one ship bindings
4. keep sensitive activation material out of remote-discoverable resources

This approach preserves the strongest repo-grounded intent without inventing unsupported canon.
