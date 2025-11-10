// ESM demo harness wiring StationOperationsService with a state instance & bus.
import { EventEmitter } from "events";
import { StationOperationsService } from "./station_operations_service.js";
import { createInitialStationState } from "./station_types.js";

// Use global bus if v2.1 augmentation present
const bus = (globalThis.OPPY_V21_BUS && globalThis.OPPY_V21_BUS.emitFrame)
  ? globalThis.OPPY_V21_BUS
  : new (class extends EventEmitter {
      emitFrame(type, data) {
        const frame = { type, t: Date.now(), ...data };
        this.emit(type, frame);
        this.emit("frame:*", frame);
        console.log(`[BUS] ${type}`, frame);
        return frame;
      }
    })();

// Minimal ethics fallback
const ethics = {
  validate(intent) {
    if (!intent.context || !intent.context.anchor) {
      return { passed: false, rationale: ["missing anchor"], policy: "Picard_Delta_3" };
    }
    return { passed: true, rationale: [], policy: "Picard_Delta_3" };
  },
};

let stationState = createInitialStationState();
const getState = () => stationState;
const setState = (s) => { stationState = s; };

const ops = new StationOperationsService({ bus, ethics, getState, setState });

export async function demo() {
  console.log("=== Station Ops Demo ===");
  // Seed docks & craft
  stationState.docks.push({
    id: "DOCK-A1",
    type: "EXTERNAL_BERTH",
    compatibleClasses: ["ORS-SHUTTLE-XL"],
    status: "FREE",
    atmosphere: "VACUUM",
    umbilicals: { power: true, fuel: true, data: true },
    safety: { fireReady: true, isolationDoor: true, evaOpen: false },
  });
  stationState.craft.push({
    id: "STARLING_AU",
    class: "ORS-SHUTTLE-XL",
    dimensions: { length: 32, width: 11, height: 7 },
    massKg: 21000,
    portType: "RING",
    fuelType: "LH2",
    maxRCS: 4000,
    capabilities: ["autodock"],
    status: "APPROACH",
  });

  bus.emitFrame("dock:request", { craftId: "STARLING_AU", desiredWindow: { start: Date.now(), end: Date.now() + 900000 }, context: { anchor: "EOS_SEED_ORION" } });
  bus.emitFrame("resource:fuel:reserve", { craftId: "STARLING_AU", kg: 1200, fuelType: "LH2", context: { anchor: "EOS_SEED_ORION" } });
  bus.emitFrame("launch:request", { craftId: "STARLING_AU", window: { start: Date.now() + 3600000, end: Date.now() + 3700000 }, context: { anchor: "EOS_SEED_ORION" } });

  console.log("\nFinal station state:");
  console.log(JSON.stringify(stationState, null, 2));
  
  // Stop the scheduler to allow demo to exit cleanly
  if (ops._scheduleTimer) {
    clearInterval(ops._scheduleTimer);
    console.log("\n✅ Demo completed, scheduler stopped.");
  }
}

// Execute when run directly: node modules/flight_control/demo_station_ops.js
if (process.argv[1]) {
  const thisPath = new URL(import.meta.url).pathname;
  const invokedPath = process.argv[1];
  if (thisPath === invokedPath || invokedPath.endsWith("demo_station_ops.js")) {
    // top-level await is supported in ESM on Node 18+
    await demo();
  }
}
