"use strict";
// Demo harness wiring StationOperationsService with a state instance & bus.

const { StationOperationsService } = require("./station_operations_service.js");
const { createInitialStationState } = require("./station_types.js");
const EventEmitter = require("events");

// Use global bus if v2.1 augmentation present
const bus = (global.OPPY_V21_BUS && global.OPPY_V21_BUS.emitFrame) ? global.OPPY_V21_BUS : new (class extends EventEmitter { emitFrame(type, data) { const frame = { type, t: Date.now(), ...data }; this.emit(type, frame); this.emit("frame:*", frame); console.log(`[BUS] ${type}`, frame); return frame; } })();

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

async function demo() {
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

  console.log("Final station state:");
  console.log(JSON.stringify(stationState, null, 2));
}

if (require.main === module) {
  demo();
}

module.exports = { demo };
