// Fleet Bridge Demo: Shows Python fleet sync with JS flight control
import { StationOperationsService } from "./station_operations_service.js";
import { createInitialStationState } from "./station_types.js";
import { FleetBridgeClient } from "./fleet_bridge_client.js";
import { EventEmitter } from "events";

// Telemetry bus
const bus = new (class extends EventEmitter {
  emitFrame(type, data) {
    const frame = { type, t: Date.now(), ...data };
    this.emit(type, frame);
    this.emit("frame:*", frame);
    console.log(`[BUS] ${type}`, JSON.stringify(frame, null, 2));
    return frame;
  }
})();

// Minimal ethics gate
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

// Initialize station ops
const ops = new StationOperationsService({ bus, ethics, getState, setState });

// Initialize fleet bridge (assumes Python API running on localhost:8000)
const fleetBridge = new FleetBridgeClient({
  apiBaseUrl: "http://localhost:8000",
  pollIntervalMs: 10000, // 10s for demo
  getState,
  setState,
});

// Wire bridge events to bus
fleetBridge.on("bridge:synced", (data) => bus.emitFrame("fleet:bridge:synced", data));
fleetBridge.on("bridge:sync-failed", (data) => bus.emitFrame("fleet:bridge:failed", data));
fleetBridge.on("bridge:error", (data) => bus.emitFrame("fleet:bridge:error", data));

export async function demoFleetBridge() {
  console.log("=== Fleet Bridge Demo ===");
  console.log("NOTE: This demo requires Python API running at http://localhost:8000");
  console.log("Start API with: python -m uvicorn api.aurora_api:app --reload\n");

  // Seed one dock for demo
  stationState.docks.push({
    id: "DOCK-B2",
    type: "INTERNAL_BAY",
    compatibleClasses: ["ORS-SHUTTLE-XL", "ORS-SHUTTLE-M"],
    status: "FREE",
    atmosphere: "PRESSURIZED",
    umbilicals: { power: true, fuel: true, data: true },
    safety: { fireReady: true, isolationDoor: true, evaOpen: false },
  });

  // Start fleet bridge
  console.log("Starting fleet bridge...");
  fleetBridge.start();

  // Wait for initial sync
  await new Promise((resolve) => {
    const timeout = setTimeout(() => {
      console.warn("⚠️  Fleet sync timeout - continuing anyway");
      resolve();
    }, 5000);

    fleetBridge.once("bridge:synced", () => {
      clearTimeout(timeout);
      resolve();
    });
  });

  console.log(`\n✅ Fleet synced! ${stationState.craft.length} craft available.`);

  // Show craft roster
  console.log("\n📋 Craft Roster:");
  for (const craft of stationState.craft) {
    console.log(`  - ${craft.id} (${craft.class}) - Status: ${craft.status}`);
  }

  // If we have craft, simulate ops
  if (stationState.craft.length > 0) {
    const firstCraft = stationState.craft[0];
    console.log(`\n🚀 Simulating ops for ${firstCraft.id}...\n`);

    bus.emitFrame("dock:request", {
      craftId: firstCraft.id,
      desiredWindow: { start: Date.now(), end: Date.now() + 900000 },
      context: { anchor: "EOS_SEED_ORION" },
    });

    bus.emitFrame("resource:fuel:reserve", {
      craftId: firstCraft.id,
      kg: 800,
      fuelType: "LH2",
      context: { anchor: "EOS_SEED_ORION" },
    });
  }

  // Let scheduler run one tick
  await new Promise((resolve) => setTimeout(resolve, 2000));

  console.log("\n📊 Final Station State Summary:");
  console.log(`  - Docks: ${stationState.docks.length}`);
  console.log(`  - Craft: ${stationState.craft.length}`);
  console.log(`  - Traffic Slots: ${stationState.traffic.length}`);
  console.log(`  - Fuel Available: ${stationState.fuel.tanks[0].availableKg} kg`);
  console.log(`  - Scheduler Lag: ${stationState.ops.schedulerLagMs} ms`);

  // Cleanup
  ops._scheduleTimer && clearInterval(ops._scheduleTimer);
  fleetBridge.stop();
  console.log("\n✅ Demo completed.");
}

// Execute if run directly
if (process.argv[1]) {
  const thisPath = new URL(import.meta.url).pathname;
  const invokedPath = process.argv[1];
  if (thisPath === invokedPath || invokedPath.endsWith("demo_fleet_bridge.js")) {
    await demoFleetBridge();
  }
}
