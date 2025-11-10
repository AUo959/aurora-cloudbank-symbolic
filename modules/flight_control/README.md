# Flight Control Module (Station Operations Service)

Provides a minimal station flight control core for OPPY integration.

## Components
- `station_operations_service.js` – Clearance & basic resource operations, emits telemetry frames. **ESM module with lightweight scheduler loop (15s cadence).**
- `station_types.js` – JSDoc typedefs + factory for initial station state. **ESM module.**
- `demo_station_ops.js` – Runnable harness showing dock, fuel reserve, launch request. **ESM demo with clean shutdown.**

## Event Channels
- **dock:** `request`, `assigned`, `denied`, `approach`
- **launch:** `request`, `window`, `armed`, `go`, `telemetry:init`
- **resource:** `fuel:reserve`, `fuel:commit`, `fuel:denied`
- **traffic:** `slot:expired`, `schedule:tick`
- **ethics:** `check` (verdict frame)
- **ops:** `blocked` (ethics rejection), `scheduler:error`

## Usage
```bash
node modules/flight_control/demo_station_ops.js
```

## Integration Notes
- Uses global.OPPY_V21_BUS if present (v2.1 inline augmentation). Falls back to local bus.
- Ethics gate expects `context.anchor` starting with `EOS_SEED_ORION`.
- Extend `_onLaunchRequest` and `_onDockRequest` for full safety/corridor logic.

## Next Steps
1. ~~Add scheduling & slot compaction.~~ ✅ Minimal scheduler with slot expiration implemented.
2. Persist station snapshots + DLP manifests.
3. Bridge Python fleet registries to `stationState.craft`.
4. Expand maintenance & turnaround orchestration.
5. Add docking sequence phases (approach → corridor clear → final lock) with safety checks.
