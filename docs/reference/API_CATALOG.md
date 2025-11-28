# Aurora CloudBank Symbolic API - Sonnet 4 Enhanced

**Version:** 1.0.0  
**Generated:** 2025-11-13T03:50:42.013302  
**Total Routes:** 169

Quantum-enhanced symbolic governance system with ChatGPT Agent Mode integration

---

## Table of Contents

- [AuMemManager](#aumemmanager)
- [Data Guardian](#data-guardian)
- [Event Coordination](#event-coordination)
- [GUMAS Ethics](#gumas-ethics)
- [HR System](#hr-system)
- [Insight Ledger](#insight-ledger)
- [Synergy Dashboard](#synergy-dashboard)
- [cross-repo-collaboration](#cross-repo-collaboration)
- [fleet-bridge](#fleet-bridge)
- [monitoring](#monitoring)
- [quantum-simulator](#quantum-simulator)
- [rd-pipeline](#rd-pipeline)
- [resilience](#resilience)
- [subroutines](#subroutines)
- [synergy](#synergy)

---

## AuMemManager

**Routes:** 11

### `POST /memory/compress`

**Summary:** Compress Memories  
Manually trigger memory compression

**Parameters:**

- `compression_ratio` (query) - Optional
  - Compression ratio
- `importance_threshold` (query) - Optional
  - Importance threshold

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /memory/create`

**Summary:** Create Memory  
Create a new memory item with quantum-symbolic capabilities

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /memory/export`

**Summary:** Export System State  
Export complete system state

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /memory/health`

**Summary:** Health Check  
Health check for AuMemManager system

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /memory/lifecycle/batch_process`

**Summary:** Batch Process Lifecycle  
Process memory lifecycle operations (decay, compression, cleanup)

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /memory/metrics`

**Summary:** Get System Metrics  
Get comprehensive system metrics

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /memory/quantum/create_vector`

**Summary:** Create Quantum Vector  
Create a quantum-symbolic vector for memory management

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /memory/quantum/entangle`

**Summary:** Entangle Vectors  
Create quantum entanglement between two vectors

**Parameters:**

- `vector1_id` (query) - ✅ Required
- `vector2_id` (query) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /memory/quantum/network_analysis`

**Summary:** Get Quantum Network Analysis  
Get detailed quantum entanglement network analysis

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /memory/quantum/trajectory`

**Summary:** Compute Trajectory  
Compute quantum vector trajectory using flight control

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /memory/retrieve`

**Summary:** Retrieve Memories  
Retrieve memories using attention-based scoring

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

## Data Guardian

**Routes:** 6

### `GET /data/health`

**Summary:** Health check for Data Guardian service  
Check if Data Guardian service is operational

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /data/pii-types`

**Summary:** List detectable PII types  
Get list of PII types that can be detected

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /data/redact`

**Summary:** Redact PII from data  
Detect and redact PII from provided data using specified strategy

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /data/regions`

**Summary:** List supported regions  
Get list of supported regions for PII detection rules

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /data/scan`

**Summary:** Scan data for PII  
Scan provided data structure for personally identifiable information (PII)

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /data/strategies`

**Summary:** List available redaction strategies  
Get list of available PII redaction strategies

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

## Event Coordination

**Routes:** 15

### `POST /api/coordination/conflicts/detect`

**Summary:** Detect Conflict  
Detect potential conflicts with other agents

**Example:**
```json
{
    "agent_id": "r2-agent-001",
    "resource_id": "dataset-123",
    "resource_type": "dataset",
    "operation": "write"
}
```

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /api/coordination/conflicts/resolve`

**Summary:** Resolve Conflict  
Mark conflict as resolved

**Example:**
```json
{
    "conflict_id": "conflict-123",
    "strategy": "priority_based",
    "resolved_by": "r2-agent-001"
}
```

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /api/coordination/event-types`

**Summary:** Get Event Types  
Get list of available event types

**Example:** GET /api/coordination/event-types

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /api/coordination/events/discover`

**Summary:** Discover Events  
Discover available events based on filter criteria

**Example:** GET /api/coordination/events/discover?event_types=task.created&priorities=high

**Parameters:**

- `event_types` (query) - Optional
- `priorities` (query) - Optional
- `source_agent_ids` (query) - Optional

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /api/coordination/events/publish`

**Summary:** Publish Event  
Publish event to coordination registry

**Example:**
```json
{
    "event_type": "task.created",
    "priority": "normal",
    "source_agent_id": "r2-agent-001",
    "payload": {
        "task_id": "task-123",
        "description": "Process data"
    }
}
```

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /api/coordination/events/replay/{agent_id}`

**Summary:** Replay Events  
Replay historical events for audit or recovery

**Example:** GET /api/coordination/events/replay/r2-agent-001?start_time=2024-01-01T00:00:00Z

**Parameters:**

- `agent_id` (path) - ✅ Required
- `start_time` (query) - Optional
- `end_time` (query) - Optional

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /api/coordination/locks/acquire`

**Summary:** Acquire Lock  
Acquire exclusive lock on resource

**Example:**
```json
{
    "agent_id": "r2-agent-001",
    "resource_id": "dataset-123",
    "resource_type": "dataset",
    "ttl_seconds": 300
}
```

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `DELETE /api/coordination/locks/{resource_id}`

**Summary:** Release Lock  
Release lock on resource

**Example:** DELETE /api/coordination/locks/dataset-123?agent_id=r2-agent-001

**Parameters:**

- `resource_id` (path) - ✅ Required
- `agent_id` (query) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /api/coordination/metrics`

**Summary:** Get Registry Metrics  
Get coordination registry metrics and statistics

**Example:** GET /api/coordination/metrics

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /api/coordination/status`

**Summary:** Get Registry Status  
Get coordination registry health status

**Example:** GET /api/coordination/status

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /api/coordination/subscriptions/subscribe`

**Summary:** Subscribe To Events  
Subscribe to events matching filter criteria

**Example:**
```json
{
    "agent_id": "r2-agent-001",
    "event_types": ["task.created", "task.assigned"],
    "priorities": ["high", "critical"]
}
```

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /api/coordination/subscriptions/{agent_id}`

**Summary:** Get Agent Subscriptions  
Get all active subscriptions for an agent

**Example:** GET /api/coordination/subscriptions/r2-agent-001

**Parameters:**

- `agent_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `DELETE /api/coordination/subscriptions/{subscription_id}`

**Summary:** Unsubscribe From Events  
Unsubscribe from events

**Example:** DELETE /api/coordination/subscriptions/abc-123

**Parameters:**

- `subscription_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /api/coordination/workflows/create`

**Summary:** Create Workflow  
Create multi-agent workflow

**Example:**
```json
{
    "name": "Data Processing Pipeline",
    "description": "Multi-stage data processing",
    "steps": [
        {"step_id": "step1", "action": "fetch_data"},
        {"step_id": "step2", "action": "process_data"}
    ],
    "agent_assignments": {
        "step1": "r2-agent-001",
        "step2": "r2-agent-002"
    },
    "created_by": "orchestrator"
}
```

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /api/coordination/workflows/{workflow_id}`

**Summary:** Get Workflow Status  
Get workflow status

**Example:** GET /api/coordination/workflows/workflow-123

**Parameters:**

- `workflow_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

## GUMAS Ethics

**Routes:** 11

### `GET /gumas/categories`

**Summary:** Get Categories  
Get all available rule categories

DLP: gumas_categories

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /gumas/evaluate`

**Summary:** Evaluate Action  
Evaluate an action against ethics rules

Returns list of violations (if any) and whether action should be blocked.

DLP: gumas_evaluate_action

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /gumas/health`

**Summary:** Health Check  
Health check endpoint for GUMAS Ethics API

DLP: gumas_health

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /gumas/rules`

**Summary:** Get Rules  
Get all configured ethics rules

DLP: gumas_rules_list

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /gumas/rules`

**Summary:** Add Rule  
Add a new ethics rule

DLP: gumas_add_rule

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **201**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /gumas/rules/{rule_id}`

**Summary:** Get Rule  
Get specific rule by ID

DLP: gumas_rule_detail

**Parameters:**

- `rule_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `DELETE /gumas/rules/{rule_id}`

**Summary:** Delete Rule  
Delete an ethics rule

DLP: gumas_delete_rule

**Parameters:**

- `rule_id` (path) - ✅ Required

**Responses:**

- **204**: Successful Response
- **422**: Validation Error
  - Content: application/json

---

### `POST /gumas/rules/{rule_id}/register-evaluator`

**Summary:** Register Custom Evaluator  
Register a custom condition evaluator for a rule

Note: This endpoint is for documentation purposes. Custom evaluators
must be registered programmatically via the EthicsEngine API.

DLP: gumas_register_evaluator

**Parameters:**

- `rule_id` (path) - ✅ Required
- `condition` (query) - ✅ Required
  - Condition pattern to register evaluator for

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /gumas/severities`

**Summary:** Get Severities  
Get all available violation severity levels

DLP: gumas_severities

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /gumas/violations`

**Summary:** Get Violations  
Get violations with optional filtering

DLP: gumas_violations_query

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `DELETE /gumas/violations`

**Summary:** Clear Violations  
Clear old violations

DLP: gumas_clear_violations

**Parameters:**

- `before` (query) - Optional
  - Clear violations before this ISO timestamp

**Responses:**

- **204**: Successful Response
- **422**: Validation Error
  - Content: application/json

---

## HR System

**Routes:** 4

### `POST /hr_system/analyze_staffing`

**Summary:** Analyze Staffing Needs  
Analyze staffing needs for a department

Returns staffing gap analysis and recommendations.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /hr_system/generate_character`

**Summary:** Generate Character  
Generate a quantum-symbolic character profile

Creates crew member profile with skills, background, and personality.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /hr_system/health`

**Summary:** Health Check  
Health check endpoint for HR System module

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /hr_system/organizational_intel`

**Summary:** Get Organizational Intelligence  
Get organizational intelligence and capacity planning

Returns department structure, capacity, and staffing insights.

**Parameters:**

- `department` (query) - Optional
  - Filter by department

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

## Insight Ledger

**Routes:** 7

### `GET /ledger/entry/{entry_id}`

**Summary:** Get Entry by ID  
Retrieve a specific ledger entry by its unique identifier

**Parameters:**

- `entry_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /ledger/export`

**Summary:** Export Ledger  
Export complete ledger to JSON file for backup or analysis

**Parameters:**

- `output_path` (query) - ✅ Required
  - Output file path
- `include_genesis` (query) - Optional
  - Include genesis entry in export

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /ledger/health`

**Summary:** Ledger Health Check  
Quick health check for ledger service

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /ledger/history`

**Summary:** Query Ledger History  
Query ledger entries with flexible filters (time, type, source, tags, etc.)

**Request Body:**
- Required: No
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /ledger/insight`

**Summary:** Record New Insight  
Record a new insight in the immutable ledger with cryptographic signature

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **201**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /ledger/stats`

**Summary:** Get Ledger Statistics  
Retrieve ledger health metrics, entry counts, and integrity status

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /ledger/verify`

**Summary:** Verify Ledger Integrity  
Cryptographically verify the integrity of the entire ledger or a subset

**Parameters:**

- `limit` (query) - Optional
  - Max entries to verify (None=all)

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

## Synergy Dashboard

**Routes:** 8

### `GET /synergy/components`

**Summary:** List Components  
List all registered components

Returns list of components, optionally filtered by status.

**Parameters:**

- `status` (query) - Optional
  - Filter by status

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /synergy/components`

**Summary:** Register Component  
Register a new component in the registry

Creates or updates component registration with dependencies.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **201**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /synergy/components/{name}`

**Summary:** Get Component  
Get details for a specific component

Returns component metadata including dependencies and status.

**Parameters:**

- `name` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `PUT /synergy/components/{name}/status`

**Summary:** Update Component Status  
Update component health status

Updates the operational status of a registered component.

**Parameters:**

- `name` (path) - ✅ Required

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /synergy/conflicts`

**Summary:** Detect Conflicts  
Detect dependency conflicts in the registry

Identifies circular dependencies, missing dependencies, and version conflicts.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /synergy/dependencies/{name}`

**Summary:** Get Dependencies  
Get dependencies for a component

Returns direct dependencies or full transitive dependency tree.

**Parameters:**

- `name` (path) - ✅ Required
- `recursive` (query) - Optional
  - Include transitive dependencies

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /synergy/export`

**Summary:** Export Registry  
Export complete registry state

Returns all registry data for backup, analysis, or integration.

**Parameters:**

- `context_tag` (query) - Optional
  - DLP context tag

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /synergy/health`

**Summary:** Registry Health  
Get registry health status

Returns metrics about registry state and component health distribution.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

## cross-repo-collaboration

**Routes:** 9

### `POST /collab/agents/sync`

**Summary:** Sync Agent Status  
Synchronize agent status across repositories.

Flags missing agents or alignment drift, returns change log.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

### `POST /collab/context/export`

**Summary:** Export Context  
Export signed capsule context for external repository.

Creates a multi-repo capsule with linked repository info, shared anchors,
and agent roster. Logs export with DLP tracking.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

### `POST /collab/context/import`

**Summary:** Import Context  
Import and validate capsule from external repository.

Validates seals/anchors, runs ethics checks, and returns activation report.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

### `POST /collab/drift/diff`

**Summary:** Compute Capsule Diff  
Compute difference between capsule states before/after an operation.

Returns detailed diff showing changes in drift, agents, repos, and anchors.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

### `GET /collab/drift/events`

**Summary:** Get Drift Events  
Get drift events with optional filtering.

Query Parameters:
    - level: Filter by drift level (green, yellow, red)
    - event_type: Filter by event type
    - limit: Maximum number of events to return (default: 50, max: 200)

**Parameters:**

- `level` (query) - Optional
- `event_type` (query) - Optional
- `limit` (query) - Optional

**Request Body:**
- Required: No
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

### `GET /collab/drift/statistics`

**Summary:** Get Drift Statistics  
Get detailed drift statistics and trends.

Returns comprehensive drift metrics, event counts, and trend analysis.

**Request Body:**
- Required: No
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

### `POST /collab/invite`

**Summary:** Repo Linking Invite  
Initiate repository linking invitation.

Exchanges anchors, permissions, and establishes trust chain.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

### `GET /collab/status`

**Summary:** Get Collab Status  
Get current cross-repo collaboration system status.

Returns active capsules, agent roster, drift metrics.

**Request Body:**
- Required: No
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

### `POST /collab/workflow/trigger`

**Summary:** Trigger Workflow  
Trigger build/test workflow in external repository.

Supports event chaining for multi-repo sync.
Note: Requires GitHub API credentials for actual workflow triggering.

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **404**: Not found
- **422**: Validation Error
  - Content: application/json

---

## fleet-bridge

**Routes:** 3

### `GET /api/fleet/craft`

**Summary:** Get All Craft  
Get all registered craft profiles.

Returns craft data compatible with JS station_types.js CraftProfile schema.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /api/fleet/craft/{craft_id}`

**Summary:** Get Craft By Id  
Get specific craft profile by ID.

**Parameters:**

- `craft_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /api/fleet/status`

**Summary:** Get Fleet Status  
Get overall fleet status summary.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

## monitoring

**Routes:** 27

### `POST /monitoring/action/evaluate`

**Summary:** Evaluate Action  
Evaluate action against ethics rules

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /monitoring/agent/{agent_id}/status`

**Summary:** Get Agent Status  
Get comprehensive status for an agent

**Parameters:**

- `agent_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /monitoring/alerts`

**Summary:** Get Alerts  
Get drift alerts

**Parameters:**

- `agent_id` (query) - Optional
  - Filter by agent ID
- `level` (query) - Optional
  - Filter by alert level
- `since_hours` (query) - Optional
  - Hours to look back

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /monitoring/audit`

**Summary:** Get Audit Log  
Get audit log entries

**Parameters:**

- `agent_id` (query) - Optional
  - Filter by agent ID
- `event_type` (query) - Optional
  - Filter by event type
- `since_hours` (query) - Optional
  - Hours to look back

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /monitoring/baseline`

**Summary:** Establish Baseline  
Establish behavioral baseline for an agent

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /monitoring/behavior/check`

**Summary:** Check Behavior  
Check agent behavior for drift

**Parameters:**

- `agent_id` (query) - ✅ Required
  - Agent identifier
- `context_tag` (query) - Optional
  - DLP context tag

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /monitoring/behavior/record`

**Summary:** Record Behavior  
Record behavioral metrics for an agent

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /monitoring/compliance/report`

**Summary:** Get Compliance Report  
Generate compliance report

**Parameters:**

- `since_hours` (query) - Optional
  - Hours to look back
- `agent_id` (query) - Optional
  - Specific agent ID

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /monitoring/dashboard/stats`

**Summary:** Get Dashboard Stats  
Get overall dashboard statistics

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /monitoring/export`

**Summary:** Export State  
Export full monitoring system state

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /monitoring/health`

**Summary:** Health Check  
Health check for monitoring system

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /monitoring/violations`

**Summary:** Get Violations  
Get ethics violations

**Parameters:**

- `agent_id` (query) - Optional
  - Filter by agent ID
- `severity` (query) - Optional
  - Filter by severity
- `since_hours` (query) - Optional
  - Hours to look back

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/alerts`

**Summary:** Get Alerts  
Get alerts with optional filtering.

Args:
    active_only: Only return unresolved alerts
    severity: Filter by severity (info/warning/error/critical)

Returns:
    Alert list and statistics

**Parameters:**

- `active_only` (query) - Optional
  - Filter to active alerts only
- `severity` (query) - Optional
  - Filter by severity

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /sentinel/alerts/acknowledge`

**Summary:** Acknowledge Alert  
Acknowledge an alert.

Args:
    request: Alert acknowledgment request with alert_id

Returns:
    Success status

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /sentinel/alerts/resolve`

**Summary:** Resolve Alert  
Resolve an alert.

Args:
    request: Alert resolution request with alert_id

Returns:
    Success status

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/alerts/rules`

**Summary:** Get Alert Rules  
Get all configured alert rules.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /sentinel/alerts/rules`

**Summary:** Create Alert Rule  
Create a new alert rule.

Args:
    rule_request: Alert rule configuration

Returns:
    Created rule details

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `DELETE /sentinel/alerts/rules/{rule_name}`

**Summary:** Delete Alert Rule  
Delete an alert rule.

**Parameters:**

- `rule_name` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/dashboard`

**Summary:** Get Dashboard  
Get comprehensive dashboard data.

Returns health, metrics, alerts, and system info in single response.
Ideal for dashboard UI that needs all data at once.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /sentinel/health`

**Summary:** Get Health  
Get comprehensive health report.

Returns overall system health status with individual checks for CPU,
memory, and disk usage, plus active alert counts.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /sentinel/metrics`

**Summary:** Get Metrics Summary  
Get summary of all collected metrics.

Returns metric names, data point counts, collection info, and stats
for key system metrics (CPU, memory, disk).

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /sentinel/metrics/collect`

**Summary:** Trigger Collection  
Manually trigger metric collection.

Useful for testing or forcing immediate data refresh.

Returns:
    Collection results with metrics collected and alerts triggered

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /sentinel/metrics/{metric_name}`

**Summary:** Get Metric Stats  
Get detailed statistics for a specific metric.

Args:
    metric_name: Name of metric to query

Returns:
    Statistics including avg, min, max, trend, latest value

**Parameters:**

- `metric_name` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/metrics/{metric_name}/history`

**Summary:** Get Metric History  
Get historical values for a metric.

Args:
    metric_name: Name of metric to query
    count: Number of recent values to return (1-1000)

Returns:
    List of recent metric values

**Parameters:**

- `metric_name` (path) - ✅ Required
- `count` (query) - Optional
  - Number of recent values

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/notifications/channels`

**Summary:** List Notification Channels  
List all registered notification channels.

Returns channel names, types, and status.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /sentinel/notifications/history`

**Summary:** Get Notification History  
Get notification history.

Args:
    limit: Number of recent notifications to return (1-1000)

Returns:
    List of notification records with alert ID, channel, success status

**Parameters:**

- `limit` (query) - Optional
  - Number of records to return

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/notifications/status`

**Summary:** Get Notification Status  
Get notification system status.

Returns enabled channels, configuration, and recent notification history.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

## quantum-simulator

**Routes:** 11

### `GET /simulate/backends`

**Summary:** List Available Backends  
List available quantum backends.

Returns:
    Dict with list of available backend names

Example Response:
    ```json
    {
        "available_backends": ["mock", "simulator"],
        "total_count": 2
    }
    ```

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /simulate/cache/clear`

**Summary:** Clear Cache  
Clear simulation cache.

Args:
    expired_only: If True, only remove expired entries. If False, clear all.

Returns:
    204 No Content on success

**Parameters:**

- `expired_only` (query) - Optional
  - Clear only expired entries

**Responses:**

- **204**: Successful Response
- **422**: Validation Error
  - Content: application/json

---

### `GET /simulate/cache/stats`

**Summary:** Get Cache Stats  
Get cache statistics and metrics.

Returns:
    Dict with cache performance metrics:
    - total_entries: Total cached simulations
    - active_entries: Non-expired entries
    - expired_entries: Expired entries pending cleanup
    - cache_utilization: Percentage of cache capacity used
    - symbolic_nodes: Number of scenario genealogy relationships

Example Response:
    ```json
    {
        "total_entries": 156,
        "active_entries": 142,
        "expired_entries": 14,
        "total_accesses": 1847,
        "avg_access_count": 13.0,
        "cache_utilization": 0.156,
        "symbolic_nodes": 23
    }
    ```

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /simulate/forecast`

**Summary:** Run Forecast  
Run quantum-enhanced forecasting simulation.

Specialized endpoint for supply chain and energy grid forecasting scenarios.
Validates that forecast_config is provided.

Args:
    request: Scenario configuration with forecast parameters

Returns:
    SimulationResult with forecast time series

Raises:
    HTTPException: 400 if forecast_config is missing

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **202**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /simulate/genealogy/{simulation_id}`

**Summary:** Get Scenario Genealogy  
Get scenario genealogy (parent chain).

Returns the chain of parent simulations that led to this scenario,
useful for tracking scenario evolution and parameter optimization.

Args:
    simulation_id: Simulation identifier

Returns:
    Dict with genealogy information:
    - simulation_id: Current simulation ID
    - parents: List of parent simulation IDs (oldest first)

Example Response:
    ```json
    {
        "simulation_id": "sim_20251026_120000_abc123",
        "parents": ["sim_20251025_100000_xyz789", "sim_20251024_140000_def456"]
    }
    ```

**Parameters:**

- `simulation_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /simulate/health`

**Summary:** Quantum Simulator Health  
Health check for quantum simulator service.

Returns:
    Dict with service health status

Example Response:
    ```json
    {
        "status": "healthy",
        "orchestrator_initialized": true,
        "available_backends": 2,
        "cache_active_entries": 142,
        "message": "Quantum simulator operational"
    }
    ```

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /simulate/results/{simulation_id}`

**Summary:** Get Simulation Result  
Retrieve simulation result by ID.

Checks cache first, returns cached result if available and not expired.

Args:
    simulation_id: Unique simulation identifier

Returns:
    SimulationResult if found

Raises:
    HTTPException: 404 if simulation not found or expired

**Parameters:**

- `simulation_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `DELETE /simulate/results/{simulation_id}`

**Summary:** Delete Simulation Result  
Delete cached simulation result.

Args:
    simulation_id: Simulation identifier

Raises:
    HTTPException: 404 if simulation not found

**Parameters:**

- `simulation_id` (path) - ✅ Required

**Responses:**

- **204**: Successful Response
- **422**: Validation Error
  - Content: application/json

---

### `POST /simulate/scenario`

**Summary:** Run Simulation  
Run quantum-classical hybrid simulation scenario.

Executes simulation asynchronously and returns result. For long-running
simulations, use the progress WebSocket endpoint to track status.

Args:
    request: Scenario configuration and parameters

Returns:
    SimulationResult with measurement, optimization, and/or forecast results

Example:
    ```json
    {
        "name": "Q1 Supply Chain Optimization",
        "scenario_type": "supply_chain",
        "backend": "mock",
        "optimization_method": "qaoa",
        "parameters": {"max_iterations": 100},
        "forecast_config": {
            "time_steps": 30,
            "variables": ["inventory", "demand", "cost"]
        },
        "seed": 42,
        "tags": ["supply-chain", "q1-2025"]
    }
    ```

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **202**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /simulate/scenarios`

**Summary:** List Scenarios  
List cached simulation scenarios with optional filtering.

Args:
    scenario_type: Filter by scenario type (supply_chain, energy_grid, etc.)
    status: Filter by status (completed, running, failed)
    limit: Maximum number of results (1-1000)

Returns:
    List of scenario summaries, sorted by start time (most recent first)

Example:
    GET /simulate/scenarios?scenario_type=supply_chain&status=completed&limit=50

**Parameters:**

- `scenario_type` (query) - Optional
  - Filter by scenario type
- `status` (query) - Optional
  - Filter by status
- `limit` (query) - Optional
  - Maximum results

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /simulate/status/{simulation_id}`

**Summary:** Get Simulation Status  
Get current status of running simulation.

Args:
    simulation_id: Simulation identifier

Returns:
    SimulationStatus with progress and estimated time remaining

Raises:
    HTTPException: 404 if simulation not found

**Parameters:**

- `simulation_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

## rd-pipeline

**Routes:** 10

### `GET /rd/capacity/{team_member}`

**Summary:** Capacity  

**Parameters:**

- `team_member` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /rd/coherence/full`

**Summary:** Full Coherence  

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /rd/coherence/mediation`

**Summary:** Coherence Mediation  
Return low-coherence pairs with anchor suggestions.

Complexity kept low via small dedicated helper steps.

**Parameters:**

- `threshold` (query) - Optional
- `limit` (query) - Optional

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /rd/health`

**Summary:** Rd Health  

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /rd/projects`

**Summary:** List Projects  
List all active R&D projects with basic metadata.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /rd/projects`

**Summary:** Create Project  
Create new R&D project with DLP tracking.

**Parameters:**

- `session_id` (query) - Optional

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /rd/projects/{project_id}/advance`

**Summary:** Advance Stage  
Advance project to next stage with milestone tracking.

**Parameters:**

- `project_id` (path) - ✅ Required
- `session_id` (query) - Optional

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /rd/projects/{project_id}/coherence`

**Summary:** Update Coherence  
Calculate team coherence score using VSA vectors.

**Parameters:**

- `project_id` (path) - ✅ Required
- `session_id` (query) - Optional

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /rd/projects/{project_id}/readiness`

**Summary:** Update Readiness  
Calculate production readiness score for project.

**Parameters:**

- `project_id` (path) - ✅ Required
- `session_id` (query) - Optional

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /rd/report`

**Summary:** Report  

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

## resilience

**Routes:** 15

### `GET /sentinel/alerts`

**Summary:** Get Alerts  
Get alerts with optional filtering.

Args:
    active_only: Only return unresolved alerts
    severity: Filter by severity (info/warning/error/critical)

Returns:
    Alert list and statistics

**Parameters:**

- `active_only` (query) - Optional
  - Filter to active alerts only
- `severity` (query) - Optional
  - Filter by severity

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /sentinel/alerts/acknowledge`

**Summary:** Acknowledge Alert  
Acknowledge an alert.

Args:
    request: Alert acknowledgment request with alert_id

Returns:
    Success status

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /sentinel/alerts/resolve`

**Summary:** Resolve Alert  
Resolve an alert.

Args:
    request: Alert resolution request with alert_id

Returns:
    Success status

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/alerts/rules`

**Summary:** Get Alert Rules  
Get all configured alert rules.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /sentinel/alerts/rules`

**Summary:** Create Alert Rule  
Create a new alert rule.

Args:
    rule_request: Alert rule configuration

Returns:
    Created rule details

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `DELETE /sentinel/alerts/rules/{rule_name}`

**Summary:** Delete Alert Rule  
Delete an alert rule.

**Parameters:**

- `rule_name` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/dashboard`

**Summary:** Get Dashboard  
Get comprehensive dashboard data.

Returns health, metrics, alerts, and system info in single response.
Ideal for dashboard UI that needs all data at once.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /sentinel/health`

**Summary:** Get Health  
Get comprehensive health report.

Returns overall system health status with individual checks for CPU,
memory, and disk usage, plus active alert counts.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /sentinel/metrics`

**Summary:** Get Metrics Summary  
Get summary of all collected metrics.

Returns metric names, data point counts, collection info, and stats
for key system metrics (CPU, memory, disk).

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `POST /sentinel/metrics/collect`

**Summary:** Trigger Collection  
Manually trigger metric collection.

Useful for testing or forcing immediate data refresh.

Returns:
    Collection results with metrics collected and alerts triggered

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /sentinel/metrics/{metric_name}`

**Summary:** Get Metric Stats  
Get detailed statistics for a specific metric.

Args:
    metric_name: Name of metric to query

Returns:
    Statistics including avg, min, max, trend, latest value

**Parameters:**

- `metric_name` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/metrics/{metric_name}/history`

**Summary:** Get Metric History  
Get historical values for a metric.

Args:
    metric_name: Name of metric to query
    count: Number of recent values to return (1-1000)

Returns:
    List of recent metric values

**Parameters:**

- `metric_name` (path) - ✅ Required
- `count` (query) - Optional
  - Number of recent values

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/notifications/channels`

**Summary:** List Notification Channels  
List all registered notification channels.

Returns channel names, types, and status.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /sentinel/notifications/history`

**Summary:** Get Notification History  
Get notification history.

Args:
    limit: Number of recent notifications to return (1-1000)

Returns:
    List of notification records with alert ID, channel, success status

**Parameters:**

- `limit` (query) - Optional
  - Number of records to return

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /sentinel/notifications/status`

**Summary:** Get Notification Status  
Get notification system status.

Returns enabled channels, configuration, and recent notification history.

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

## subroutines

**Routes:** 9

### `POST /subroutines/execute`

**Summary:** Execute Subroutine  
Execute a subroutine with provided inputs.

Args:
    request: Execution request with subroutine ID and inputs
    
Returns:
    Execution result

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /subroutines/export`

**Summary:** Export Registry  
Export full registry state.

Returns:
    Complete registry export with all subroutines

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /subroutines/get/{subroutine_id}`

**Summary:** Get Subroutine  
Get details for a specific subroutine.

Args:
    subroutine_id: Subroutine unique ID
    
Returns:
    Subroutine details

**Parameters:**

- `subroutine_id` (path) - ✅ Required

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /subroutines/health`

**Summary:** Health Check  
Health check for subroutine system.

Returns:
    Health status

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /subroutines/list`

**Summary:** List Subroutines  
List all registered subroutines with optional filters.

Args:
    category: Filter by category
    status_filter: Filter by status
    
Returns:
    List of subroutines

**Parameters:**

- `category` (query) - Optional
- `status_filter` (query) - Optional

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /subroutines/register`

**Summary:** Register Subroutine  
Register a new subroutine in the system.

Returns:
    Registered subroutine details

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **201**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `POST /subroutines/search`

**Summary:** Search Subroutines  
Search subroutines by query, category, status, or tags.

Returns:
    List of matching subroutines

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /subroutines/stats`

**Summary:** Get Registry Stats  
Get registry statistics.

Returns:
    Registry statistics including counts by category and status

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `PUT /subroutines/status/{subroutine_id}`

**Summary:** Update Subroutine Status  
Update subroutine status.

Args:
    subroutine_id: Subroutine ID
    request: New status
    
Returns:
    Updated subroutine

**Parameters:**

- `subroutine_id` (path) - ✅ Required

**Request Body:**
- Required: Yes
- Content Types: application/json

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

## synergy

**Routes:** 6

### `GET /api/synergy/components`

**Summary:** Get Components  
Get all registered R-2 components with real-time status

DLP: synergy_dashboard_components

**Parameters:**

- `status_filter` (query) - Optional
  - Filter by status: active|degraded|offline

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /api/synergy/health`

**Summary:** Health Check  
Health check endpoint for synergy dashboard API

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /api/synergy/interactions`

**Summary:** Get Interactions  
Get component interaction flows with metrics

DLP: synergy_dashboard_interactions

**Parameters:**

- `component_id` (query) - Optional
  - Filter by component ID

**Responses:**

- **200**: Successful Response
  - Content: application/json
- **422**: Validation Error
  - Content: application/json

---

### `GET /api/synergy/metrics`

**Summary:** Get Metrics  
Get aggregated dashboard metrics and system health

DLP: synergy_dashboard_metrics

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /api/synergy/synergy-scores`

**Summary:** Get Synergy Scores  
Get synergy scores for component pairs with optimization opportunities

DLP: synergy_dashboard_synergy_scores

**Responses:**

- **200**: Successful Response
  - Content: application/json

---

### `GET /api/synergy/topology`

**Summary:** Get Topology  
Get complete component topology with nodes, edges, and clusters

DLP: synergy_dashboard_topology

**Responses:**

- **200**: Successful Response
  - Content: application/json

---
