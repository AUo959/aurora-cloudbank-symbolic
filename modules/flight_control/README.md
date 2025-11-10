# Flight Control Module (Station Operations Service)

Provides a minimal station flight control core for OPPY integration.

## Components
- `station_operations_service.js` – Clearance & basic resource operations, emits telemetry frames.
- `station_types.js` – JSDoc typedefs + factory for initial station state.
- `demo_station_ops.js` – Runnable harness showing dock, fuel reserve, launch request.

## Event Channels
- dock:* (request, assigned, denied)
- launch:* (request, window, armed, go)
- resource:* (fuel:reserve, fuel:commit, fuel:denied)
- ethics:check (verdict frame)
- ops:blocked (ethics rejection)

## Usage
```bash
node modules/flight_control/demo_station_ops.js
```

## Integration Notes
- Uses global.OPPY_V21_BUS if present (v2.1 inline augmentation). Falls back to local bus.
- Ethics gate expects `context.anchor` starting with `EOS_SEED_ORION`.
- Extend `_onLaunchRequest` and `_onDockRequest` for full safety/corridor logic.

## Next Steps
1. Add scheduling & slot compaction.
2. Persist station snapshots + DLP manifests.
3. Bridge Python fleet registries to `stationState.craft`.
4. Expand maintenance & turnaround orchestration.
