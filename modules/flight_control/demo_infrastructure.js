// Complete Infrastructure Demo: DLP persistence + Maintenance + Enhanced docking
import { StationOperationsService } from "./station_operations_service.js";
import { createInitialStationState } from "./station_types.js";
import { DLPManifestGenerator } from "./dlp_manifest_generator.js";
import { MaintenanceOrchestrator } from "./maintenance_orchestrator.js";
import { DockingSequenceManager } from "./docking_sequence_manager.js";
import { EventEmitter } from "events";

// Telemetry bus
const bus = new (class extends EventEmitter {
  emitFrame(type, data) {
    const frame = { type, t: Date.now(), ...data };
    this.emit(type, frame);
    this.emit("frame:*", frame);
    console.log(`[${new Date().toISOString()}] ${type}`, JSON.stringify(data, null, 2));
    return frame;
  }
})();

// Ethics gate
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

// Initialize all systems
const ops = new StationOperationsService({ bus, ethics, getState, setState });
const dlpGenerator = new DLPManifestGenerator({
  manifestDir: "./station_manifests",
  getState,
});
const maintenanceOrc = new MaintenanceOrchestrator({ getState, setState, bus });
const dockingMgr = new DockingSequenceManager({ getState, setState, bus, ethics });

// T1/SRB anchor tracking (simulated)
let t1State = 0;
let srbResolution = 0;

export async function demoInfrastructure() {
  console.log("=== Flight Control Infrastructure Demo ===\n");
  
  // Setup: Seed docks and craft
  stationState.docks.push({
    id: "DOCK-ALPHA-1",
    type: "EXTERNAL_BERTH",
    compatibleClasses: ["ORS-SHUTTLE-XL", "ORS-FRIGATE-CONSTANCY"],
    status: "FREE",
    atmosphere: "VACUUM",
    umbilicals: { power: true, fuel: true, data: true },
    safety: { fireReady: true, isolationDoor: true, evaOpen: false },
  });
  
  stationState.craft.push({
    id: "ENTERPRISE_XL",
    class: "ORS-SHUTTLE-XL",
    dimensions: { length: 32, width: 11, height: 7 },
    massKg: 21000,
    portType: "RING",
    fuelType: "LH2",
    maxRCS: 4000,
    capabilities: ["autodock", "mesh-nav", "autonomous"],
    status: "APPROACH",
    maintenanceDueAt: Date.now() + 3600000, // 1 hour from now
  });
  
  console.log("✅ Station initialized with 1 dock and 1 craft\n");
  
  // === 1. DLP Manifest Snapshot ===
  console.log("=== 1. DLP Manifest Generation ===");
  t1State = 42;
  srbResolution = 1337;
  
  const { manifest: manifest1, filepath: filepath1 } = await dlpGenerator.captureSnapshot({
    contextTag: "station_init_snapshot",
    chainNotation: "005//001//ACC",
    t1State,
    srbResolution,
    metadata: { phase: "initialization", operator: "demo" },
  });
  
  console.log(`📋 Manifest generated: ${manifest1.manifestId}`);
  console.log(`   Hash: ${manifest1.stateHash.slice(0, 16)}...`);
  console.log(`   Persisted: ${filepath1}`);
  console.log(`   Validation: ${dlpGenerator.validateManifest(manifest1) ? "✅ VALID" : "❌ INVALID"}\n`);
  
  // === 2. Maintenance Orchestration ===
  console.log("=== 2. Maintenance Orchestration ===");
  
  // Schedule post-flight inspection
  const task1 = maintenanceOrc.scheduleMaintenance("ENTERPRISE_XL", "POST_FLIGHT_INSPECT", {
    priority: "HIGH",
    reason: "Standard post-approach inspection",
  });
  console.log(`🔧 Scheduled: ${task1.template} for ${task1.craftId}`);
  console.log(`   Task ID: ${task1.taskId}`);
  console.log(`   Due: ${new Date(task1.dueBy).toISOString()}\n`);
  
  // Start the task
  await new Promise(resolve => setTimeout(resolve, 1000));
  maintenanceOrc.startTask(task1.taskId, { lead: "Engineer_Alpha", team: ["Tech_B1", "Tech_B2"] });
  console.log(`⚙️  Task started with 3-person crew\n`);
  
  // Simulate task completion
  await new Promise(resolve => setTimeout(resolve, 2000));
  maintenanceOrc.completeTask(task1.taskId, {
    findings: "All systems nominal",
    partsUsed: [],
    notes: "Green across the board",
  });
  console.log(`✅ Task completed\n`);
  
  const maintSummary = maintenanceOrc.getMaintenanceSummary();
  console.log("📊 Maintenance Summary:", maintSummary, "\n");
  
  // === 3. Enhanced Docking Sequence ===
  console.log("=== 3. Enhanced Docking Sequence ===");
  
  // Wire docking events for live monitoring (console output for tests)
  dockingMgr.on("docking:phase-advanced", (data) => {
    console.log(`   🚀 Phase: ${data.phase} | Range: ${data.telemetry.range}m | Velocity: ${data.telemetry.velocity}m/s`);
  });
  
  dockingMgr.on("docking:safety-checks", (data) => {
    console.log(`   🛡️  Safety checks: ${JSON.stringify(data.checks)}`);
  });
  
  // Also log phase changes with simpler format for test matching
  bus.on("docking:phase-advanced", (frame) => {
    // Already logged above via dockingMgr event
  });
  
  bus.on("docking:safety-checks", (frame) => {
    // Already logged above via dockingMgr event
  });
  
  // Initiate docking
  const sequence = dockingMgr.initiateDocking("ENTERPRISE_XL", "DOCK-ALPHA-1", {
    anchor: "EOS_SEED_ORION",
  });
  
  console.log(`🎯 Docking sequence initiated: ${sequence.sequenceId}`);
  console.log(`   Craft: ${sequence.craftId} → Dock: ${sequence.dockId}\n`);
  
  // Wait for docking to complete (phases auto-advance)
  await new Promise((resolve) => {
    dockingMgr.once("docking:complete", () => resolve());
    // Fallback timeout
    setTimeout(resolve, 30000);
  });
  
  console.log("\n✅ Docking sequence complete!\n");
  
  // === 4. Final State Snapshot with DLP ===
  console.log("=== 4. Final State Snapshot ===");
  t1State = 84; // Advanced
  srbResolution = 2674; // Advanced
  
  const { manifest: manifest2, filepath: filepath2 } = await dlpGenerator.captureSnapshot({
    contextTag: "docking_complete_snapshot",
    chainNotation: "005//001//ACC",
    t1State,
    srbResolution,
    metadata: {
      phase: "operational",
      event: "docking-complete",
      dockedCraft: stationState.docks.filter(d => d.status === "ASSIGNED").length,
    },
  });
  
  console.log(`📋 Final manifest: ${manifest2.manifestId}`);
  console.log(`   Craft count: ${manifest2.metadata.craftCount}`);
  console.log(`   Maintenance tasks: ${manifest2.metadata.maintenanceTasks}`);
  console.log(`   Fuel available: ${manifest2.metadata.fuelAvailable} kg`);
  console.log(`   Persisted: ${filepath2}\n`);
  
  // === 5. System Summary ===
  console.log("=== System Summary ===");
  console.log("DLP Generator:", dlpGenerator.getStats());
  console.log("Active Docking Sequences:", dockingMgr.getActiveSequences().length);
  console.log("Maintenance Summary:", maintenanceOrc.getMaintenanceSummary());
  
  console.log("\n📈 Station State:");
  console.log(`   Docks: ${stationState.docks.length} (${stationState.docks.filter(d => d.status === "ASSIGNED").length} occupied)`);
  console.log(`   Craft: ${stationState.craft.length} (${stationState.craft.filter(c => c.status === "DOCKED").length} docked)`);
  console.log(`   Traffic Slots: ${stationState.traffic.length}`);
  console.log(`   Fuel: ${stationState.fuel.tanks[0].availableKg} / ${stationState.fuel.tanks[0].capacityKg} kg`);
  
  // Cleanup
  ops._scheduleTimer && clearInterval(ops._scheduleTimer);
  maintenanceOrc.stop();
  
  console.log("\n✅ Infrastructure demo complete!");
}

// Execute if run directly
if (process.argv[1]) {
  const thisPath = new URL(import.meta.url).pathname;
  const invokedPath = process.argv[1];
  if (thisPath === invokedPath || invokedPath.endsWith("demo_infrastructure.js")) {
    await demoInfrastructure();
  }
}
