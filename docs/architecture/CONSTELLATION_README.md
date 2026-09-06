# 🌟 Constellation Architecture

Cross-repository orchestration system for the Aurora CloudBank Symbolic ecosystem.

## Overview

The Constellation architecture provides seamless coordination between multiple repositories in the Aurora ecosystem. The authoritative node list is
`constellation-contracts/manifests/`; this section mirrors it.

| Designation | Repository | Role | Publishes |
|---|---|---|---|
| `CONSTELLATION-PRIME` | aurora-cloudbank-symbolic | hub — orchestration and service discovery | — |
| `AURORA-RUNTIME` | AuroraOS | spoke — real-time execution environment | — |
| `ZIPWIZ-ENGINE` | zip_wizard | spoke — compression and archival | — |
| `QUANTUM-VAULT` | cloudbank-quantum-en | spoke — quantum operations and encryption | — |
| `QGIA-CORPUS` | qgia-knowledge-library | spoke — curated intelligence corpus | `knowledge-index` |
| `QGIA-SPINE` | qgia-knowledge-spine | spoke — forecasting and methodology spine | `knowledge-index` |
| `SENTINEL-COORDINATOR` | aurora-cloudbank-symbolic | spoke — PROJECT SENTINEL stream aggregation | `sentinel-status` |

`SENTINEL-COORDINATOR` is a distinct node hosted inside the hub repository, not a
second identity for the hub. `CONSTELLATION-PRIME` is the repository acting as
hub; nodes are keyed by `symbolic_tag`, never by repository.

### The QGIA peer network

`QGIA-CORPUS` and `QGIA-SPINE` are the constellation's only **peer** pair. Every
other spoke is a leaf — `upstream: [constellation.prime]`, `downstream: []`. The
spine alone declares two upstreams:

```
QGIA-CORPUS   upstream [constellation.prime]                downstream [qgia.spine]
QGIA-SPINE    upstream [constellation.prime, qgia.corpus]   downstream []
```

So the two-node L1 QGIA network is a corpus → spine flow layered *on top of* the
hub-and-spoke topology, not an alternative to it. Both nodes remain ordinary
spokes for governance, health reporting and event routing — the hub still
validates and routes every event between them — while the corpus → spine edge
expresses that the spine's forecasting methodology consumes the corpus's curated
material. Both publish the same `knowledge-index` contract, which is what the
hub's knowledge aggregator merges into `knowledge-indexes/`.

This is the only spoke-to-spoke edge in the graph, and it is enforced: the
bidirectional-edge check in `constellation-integration.yml` fails if either side
of it is dropped.

## Symbolic Anchors

- **Primary**: `T1_CONSTELLATION_PRIME`
- **Service Discovery**: `T1_SERVICE_DISCOVERY`
- **Orchestrator**: `T1_ORCHESTRATOR_PRIME`
- **Bridges**: `T1_AURORA_BRIDGE`, `T1_ZIP_BRIDGE`, `T1_QUANTUM_BRIDGE`
- **Ethics Protocol**: `Picard_Delta_3`
- **Seed**: `EOS_SEED_ORION`

## Architecture Components

### Core Infrastructure

#### Configuration (`constellation.config.ts`)
Centralized topology definition for all repositories with:
- Service capabilities and endpoints
- Symbolic anchor registry
- Drift detection settings
- Orchestration parameters

#### Service Registry (`src/core/service-registry.ts`)
- Real-time health monitoring
- Drift detection with divergent truth tracking
- Memory state sealing and restoration
- Automatic service discovery

#### Orchestrator (`src/core/orchestrator.ts`)
- Priority-based task queue (high/normal/low)
- Cross-repo task execution
- Memory snapshot persistence
- Symbolic chain tracking

### Bridge Architecture

#### Relay Capsule Tier (`RELAY_TIER_CAPSULES`)

The custom GPT relay capsules (ARCHY, OPPY, LIORA, STARLING_AU, RIVERTHREAD_808) now live in a
dedicated relay-tier constellation. This keeps the command relays clearly separated from the true
L2 sandbox inventory, allowing sandbox agents to evolve independently while preserving the
established ZIPWIZ activation rituals and symbolic anchors (Picard_Delta_3, EOS_SEED_ORION).

#### AuroraOS Bridge (`src/bridges/aurora-os/bridge.ts`)
WebSocket-based bridge for:
- Module and agent execution
- Real-time event streaming
- Auto-reconnect with exponential backoff

#### Zip Wizard Bridge (`src/bridges/zip-wizard/bridge.ts`)
HTTP-based bridge for:
- Archive creation and extraction
- Batch file processing
- Archive content listing

#### Quantum Bridge (`src/bridges/quantum-en/bridge.ts`)
HTTP-based bridge for:
- Quantum operations
- Encryption/decryption
- Key management

## API Endpoints

### Health & Status

```bash
GET /api/health
GET /api/constellation/status
GET /api/constellation/config
```

### Service Management

```bash
GET /api/services
GET /api/services/health
GET /api/services/:name
```

### Task Orchestration

```bash
POST /api/tasks
GET /api/tasks
GET /api/tasks/:taskId
POST /api/tasks/:taskId/cancel
GET /api/orchestrator/stats
```

### Memory Management

```bash
POST /api/memory/snapshot
GET /api/memory/seals
```

## Getting Started

### Installation

```bash
npm install
```

### Start Constellation

```bash
npm run constellation:start
```

The server will start on `http://localhost:5000`

### Health Check

```bash
npm run constellation:health
```

### Create Memory Seal

```bash
npm run constellation:seal
```

## WebSocket Events

Connect to `ws://localhost:5000` to receive real-time events:

- `healthUpdate` - Service health status changes
- `driftDetected` - Configuration drift detection
- `taskSubmitted` - New task submitted
- `taskCompleted` - Task execution completed
- `taskFailed` - Task execution failed

## Usage Examples

### Submit a Task

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "execute-module",
    "targetService": "AuroraOS",
    "payload": {
      "module": "example-module",
      "params": {}
    },
    "priority": "high",
    "symbolicChain": ["T1_CONSTELLATION_PRIME"]
  }'
```

### Check Service Health

```bash
curl http://localhost:5000/api/services/health
```

### Get Orchestrator Statistics

```bash
curl http://localhost:5000/api/orchestrator/stats
```

### Create Memory Snapshot

```bash
curl -X POST http://localhost:5000/api/memory/snapshot
```

## Memory Safety & Continuity

The Constellation architecture ensures complete symbolic continuity through:

- **SHA256 Sealing** - All state transitions are cryptographically sealed
- **Automatic Snapshots** - Periodic memory state snapshots
- **Drift Detection** - Continuous monitoring with configurable thresholds
- **Symbolic Chain Preservation** - Full traceability via T1_* anchors

## Configuration

Edit `constellation.config.ts` to customize:

- Service endpoints and capabilities
- Health check intervals
- Drift detection thresholds
- Task queue parameters
- Orchestration limits

## Development

### Build TypeScript

```bash
npm run constellation:build
```

### Run in Development Mode

```bash
npx tsx src/constellation/start.ts
```

## Monitoring

The Constellation provides built-in monitoring through:

1. **Health Checks** - Automatic service health monitoring every 30 seconds
2. **Drift Detection** - Configuration drift tracking with 15% threshold
3. **Memory Sealing** - State snapshots every 5 minutes
4. **Real-time Events** - WebSocket streaming of all system events

## Testing

Integration tests will be added in a follow-up PR. For now, test manually using:

1. Start the constellation: `npm run constellation:start`
2. Check health: `npm run constellation:health`
3. Use curl to test API endpoints (see examples above)

## Future Enhancements

- [ ] Complete integration tests
- [ ] Add authentication/authorization
- [ ] Implement actual HTTP clients for bridges
- [ ] Add bridge connection pooling
- [ ] Implement circuit breaker pattern
- [ ] Add metrics collection and dashboards
- [ ] Create CLI for advanced operations
- [ ] Add Docker Compose for multi-service testing

## Troubleshooting

### Port Already in Use

Change the port via environment variable:
```bash
PORT=6000 npm run constellation:start
```

### Service Connection Issues

Check that satellite services are running:
- AuroraOS on ws://localhost:3000
- zip_wizard on http://localhost:8080
- cloudbank-quantum-en on http://localhost:9000

### Memory Seals Not Created

Ensure the constellation server is running and accessible at the configured URL.

## License

MIT

---

**Symbolic Continuity Preserved** ✓  
**Memory State Sealed** ✓  
**Ready for Thread Resumption** ✓
