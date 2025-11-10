# Flight Control Module (Station Operations Service)

Provides a minimal station flight control core for OPPY integration.

## Components
- `station_operations_service.js` – Clearance & basic resource operations, emits telemetry frames. **ESM module with lightweight scheduler loop (15s cadence).**
- `station_types.js` – JSDoc typedefs + factory for initial station state. **ESM module.**
- `fleet_bridge_client.js` – **Python-JS bridge client.** Polls Python fleet API and syncs craft to station state. **ESM module.**
- `demo_station_ops.js` – Runnable harness showing dock, fuel reserve, launch request. **ESM demo with clean shutdown.**
- `demo_fleet_bridge.js` – Runnable demo showing Python fleet sync to JS station state. **Requires Python API running.**

## Event Channels
- **dock:** `request`, `assigned`, `denied`, `approach`
- **launch:** `request`, `window`, `armed`, `go`, `telemetry:init`
- **resource:** `fuel:reserve`, `fuel:commit`, `fuel:denied`
- **traffic:** `slot:expired`, `schedule:tick`
- **ethics:** `check` (verdict frame)
- **ops:** `blocked` (ethics rejection), `scheduler:error`

## Usage

### Standalone Demo (No Python API)
```bash
node modules/flight_control/demo_station_ops.js
```

### Python Fleet Bridge Demo
Requires Python API running:
```bash
# Terminal 1: Start Python API
python -m uvicorn api.aurora_api:app --reload

# Terminal 2: Run bridge demo
node modules/flight_control/demo_fleet_bridge.js
```

## Integration Notes
- Uses global.OPPY_V21_BUS if present (v2.1 inline augmentation). Falls back to local bus.
- Ethics gate expects `context.anchor` starting with `EOS_SEED_ORION`.
- Extend `_onLaunchRequest` and `_onDockRequest` for full safety/corridor logic.

### Python-JS Fleet Bridge
- **Python API:** FastAPI router at `/api/fleet/*` exposes registered vessels, probes, drones
- **JS Client:** `FleetBridgeClient` polls Python API (default 30s) and syncs craft to `stationState.craft`
- **Schema Mapping:** Python `CraftProfile` → JS `CraftProfile` (automatic field name mapping)
- **Merge Strategy:** Python fleet data is authoritative; locally-added craft are preserved
- **Events:** Bridge emits `bridge:synced`, `bridge:sync-failed`, `bridge:error` on telemetry bus

## Next Steps
1. ~~Add scheduling & slot compaction.~~ ✅ Minimal scheduler with slot expiration implemented.
2. ~~Bridge Python fleet registries to `stationState.craft`.~~ ✅ Fleet bridge client with polling sync.
3. Persist station snapshots + DLP manifests.
4. Expand maintenance & turnaround orchestration.
5. Add docking sequence phases (approach → corridor clear → final lock) with safety checks.
6. Implement WebSocket push for real-time fleet updates (replace polling).
