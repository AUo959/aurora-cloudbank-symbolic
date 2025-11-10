// Docking Sequence Manager: Multi-phase docking with safety checks

import { EventEmitter } from "events";

/**
 * @typedef {import('./station_types.js').StationState} StationState
 * @typedef {import('./station_types.js').DockBay} DockBay
 * @typedef {import('./station_types.js').CraftProfile} CraftProfile
 */

/**
 * Docking sequence phases
 * @enum {string}
 */
export const DockingPhase = {
  APPROACH: "APPROACH",           // Initial approach vector
  CORRIDOR_ENTRY: "CORRIDOR_ENTRY", // Entering traffic corridor
  SAFETY_HOLD: "SAFETY_HOLD",     // Hold for safety checks
  FINAL_APPROACH: "FINAL_APPROACH", // Final approach to dock
  DOCKING: "DOCKING",             // Active docking maneuver
  LOCKED: "LOCKED",               // Hard dock achieved
  UMBILICAL: "UMBILICAL",         // Umbilical connection
  COMPLETE: "COMPLETE",           // Docking complete
};

/**
 * Docking sequence state
 * @typedef {Object} DockingSequence
 * @property {string} sequenceId
 * @property {string} craftId
 * @property {string} dockId
 * @property {DockingPhase} phase
 * @property {number} startedAt
 * @property {number} phaseStartedAt
 * @property {Object} safetyChecks
 * @property {boolean} safetyChecks.corridorClear
 * @property {boolean} safetyChecks.dockReady
 * @property {boolean} safetyChecks.umbilicalReady
 * @property {boolean} safetyChecks.fireSuppressionArmed
 * @property {Object} telemetry
 * @property {string[]} warnings
 */

export class DockingSequenceManager extends EventEmitter {
  /**
   * @param {Object} options
   * @param {Function} options.getState
   * @param {Function} options.setState
   * @param {Object} options.bus
   * @param {Object} [options.ethics] - Ethics gate for validation
   */
  constructor({ getState, setState, bus, ethics }) {
    super();
    this.getState = getState;
    this.setState = setState;
    this.bus = bus;
    this.ethics = ethics;
    this.activeSequences = new Map(); // sequenceId -> DockingSequence
  }

  /**
   * Initiate docking sequence
   * @param {string} craftId
   * @param {string} dockId
   * @param {Object} context - DLP context
   * @returns {DockingSequence}
   */
  initiateDocking(craftId, dockId, context = {}) {
    // Ethics gate check
    if (this.ethics) {
      const verdict = this.ethics.validate({
        actor: "DockingSequenceManager",
        action: { kind: "initiate-docking", priority: "essential" },
        payload: { craftId, dockId },
        context,
      });
      
      if (!verdict.passed) {
        this.bus?.emitFrame?.("docking:blocked", {
          craftId,
          dockId,
          reason: verdict.rationale,
        });
        throw new Error(`Docking blocked: ${verdict.rationale.join(", ")}`);
      }
    }
    
    const state = this.getState();
    const craft = state.craft.find(c => c.id === craftId);
    const dock = state.docks.find(d => d.id === dockId);
    
    if (!craft) throw new Error(`Craft ${craftId} not found`);
    if (!dock) throw new Error(`Dock ${dockId} not found`);
    if (dock.status !== "FREE") throw new Error(`Dock ${dockId} not available`);
    
    const sequenceId = `DOCK-SEQ-${Date.now()}-${craftId}`;
    const now = Date.now();
    
    const sequence = {
      sequenceId,
      craftId,
      dockId,
      phase: DockingPhase.APPROACH,
      startedAt: now,
      phaseStartedAt: now,
      safetyChecks: {
        corridorClear: false,
        dockReady: false,
        umbilicalReady: false,
        fireSuppressionArmed: false,
      },
      telemetry: {
        range: 5000, // meters
        velocity: 25, // m/s
        alignment: 0.95, // 0-1 scale
      },
      warnings: [],
    };
    
    this.activeSequences.set(sequenceId, sequence);
    
    // Update craft status
    craft.status = "APPROACH";
    this.setState(state);
    
    this.bus?.emitFrame?.("docking:initiated", {
      sequenceId,
      craftId,
      dockId,
      phase: sequence.phase,
    });
    
    // Auto-advance to next phase
    setTimeout(() => this._advancePhase(sequenceId), 2000);
    
    return sequence;
  }

  /**
   * Advance docking sequence to next phase
   * @private
   * @param {string} sequenceId
   */
  _advancePhase(sequenceId) {
    const sequence = this.activeSequences.get(sequenceId);
    if (!sequence) return;
    
    const state = this.getState();
    const craft = state.craft.find(c => c.id === sequence.craftId);
    const dock = state.docks.find(d => d.id === sequence.dockId);
    
    if (!craft || !dock) {
      this._abortSequence(sequenceId, "Craft or dock no longer available");
      return;
    }
    
    switch (sequence.phase) {
      case DockingPhase.APPROACH:
        // Check corridor entry conditions
        sequence.phase = DockingPhase.CORRIDOR_ENTRY;
        sequence.telemetry.range = 2500;
        this._checkCorridorSafety(sequence, state);
        this.emit("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: { ...sequence.telemetry },
        });
        this.bus.emitFrame("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: sequence.telemetry,
        });
        break;
        
      case DockingPhase.CORRIDOR_ENTRY:
        // Enter safety hold for checks
        sequence.phase = DockingPhase.SAFETY_HOLD;
        sequence.telemetry.range = 1000;
        this._performSafetyChecks(sequence, dock);
        this.emit("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: { ...sequence.telemetry },
        });
        this.bus.emitFrame("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: sequence.telemetry,
        });
        break;
        
      case DockingPhase.SAFETY_HOLD:
        // Proceed to final approach if safe
        if (this._allSafetyChecksPassed(sequence)) {
          sequence.phase = DockingPhase.FINAL_APPROACH;
          sequence.telemetry.range = 500;
          sequence.telemetry.velocity = 5; // Slow approach
          this.emit("docking:phase-advanced", {
            sequenceId,
            craftId: sequence.craftId,
            phase: sequence.phase,
            telemetry: { ...sequence.telemetry },
          });
          this.bus.emitFrame("docking:phase-advanced", {
            sequenceId,
            craftId: sequence.craftId,
            phase: sequence.phase,
            telemetry: sequence.telemetry,
          });
        } else {
          sequence.warnings.push("Safety checks incomplete, holding");
          // Retry safety checks
          setTimeout(() => this._performSafetyChecks(sequence, dock), 3000);
          return;
        }
        break;
        
      case DockingPhase.FINAL_APPROACH:
        // Begin docking maneuver
        sequence.phase = DockingPhase.DOCKING;
        sequence.telemetry.range = 50;
        sequence.telemetry.velocity = 0.5;
        this.emit("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: { ...sequence.telemetry },
        });
        this.bus.emitFrame("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: sequence.telemetry,
        });
        break;
        
      case DockingPhase.DOCKING:
        // Achieve hard dock
        sequence.phase = DockingPhase.LOCKED;
        sequence.telemetry.range = 0;
        sequence.telemetry.velocity = 0;
        dock.status = "ASSIGNED";
        dock.occupancy = { craftId: sequence.craftId, since: Date.now() };
        craft.status = "DOCKED";
        this.emit("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: { ...sequence.telemetry },
        });
        this.bus.emitFrame("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: sequence.telemetry,
        });
        break;
        
      case DockingPhase.LOCKED:
        // Connect umbilicals
        sequence.phase = DockingPhase.UMBILICAL;
        this._connectUmbilicals(dock);
        this.emit("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: { ...sequence.telemetry },
        });
        this.bus.emitFrame("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: sequence.telemetry,
        });
        break;
        
      case DockingPhase.UMBILICAL:
        // Complete sequence
        sequence.phase = DockingPhase.COMPLETE;
        this.emit("docking:phase-advanced", {
          sequenceId,
          craftId: sequence.craftId,
          phase: sequence.phase,
          telemetry: { ...sequence.telemetry },
        });
        this._completeSequence(sequenceId);
        return; // No further advancement
    }
    
    sequence.phaseStartedAt = Date.now();
    this.setState(state);
    
    this.bus?.emitFrame?.("docking:phase-advanced", {
      sequenceId,
      craftId: sequence.craftId,
      phase: sequence.phase,
      telemetry: sequence.telemetry,
    });
    
    // Auto-advance (except for safety hold which is conditional)
    if (sequence.phase !== DockingPhase.SAFETY_HOLD) {
      const delay = this._getPhaseDelay(sequence.phase);
      setTimeout(() => this._advancePhase(sequenceId), delay);
    }
  }

  /**
   * Get delay for phase transition
   * @private
   */
  _getPhaseDelay(phase) {
    const delays = {
      [DockingPhase.APPROACH]: 3000,
      [DockingPhase.CORRIDOR_ENTRY]: 2000,
      [DockingPhase.SAFETY_HOLD]: 3000,
      [DockingPhase.FINAL_APPROACH]: 4000,
      [DockingPhase.DOCKING]: 5000,
      [DockingPhase.LOCKED]: 2000,
      [DockingPhase.UMBILICAL]: 3000,
    };
    return delays[phase] || 2000;
  }

  /**
   * Check corridor safety
   * @private
   */
  _checkCorridorSafety(sequence, state) {
    // Check for traffic conflicts
    const hasConflicts = state.traffic.some(
      slot => slot.status === "CONFIRMED" && slot.corridor === "L-ALPHA-OUT"
    );
    
    sequence.safetyChecks.corridorClear = !hasConflicts;
    
    if (hasConflicts) {
      sequence.warnings.push("Traffic corridor conflict detected");
    }
  }

  /**
   * Perform safety checks
   * @private
   */
  _performSafetyChecks(sequence, dock) {
    sequence.safetyChecks.dockReady = dock.status === "FREE" && !dock.safety.evaOpen;
    sequence.safetyChecks.umbilicalReady = dock.umbilicals.power && dock.umbilicals.fuel;
    sequence.safetyChecks.fireSuppressionArmed = dock.safety.fireReady;
    
    const checksData = {
      sequenceId: sequence.sequenceId,
      checks: sequence.safetyChecks,
      allPassed: this._allSafetyChecksPassed(sequence),
    };
    
    this.emit("docking:safety-checks", checksData);
    this.bus?.emitFrame?.("docking:safety-checks", checksData);
    
    // If all passed, trigger phase advancement
    if (this._allSafetyChecksPassed(sequence)) {
      setTimeout(() => this._advancePhase(sequence.sequenceId), 1000);
    }
  }

  /**
   * Check if all safety checks passed
   * @private
   */
  _allSafetyChecksPassed(sequence) {
    return Object.values(sequence.safetyChecks).every(check => check === true);
  }

  /**
   * Connect umbilicals
   * @private
   */
  _connectUmbilicals(dock) {
    this.bus?.emitFrame?.("docking:umbilical-connect", {
      dockId: dock.id,
      power: dock.umbilicals.power,
      fuel: dock.umbilicals.fuel,
      data: dock.umbilicals.data,
    });
  }

  /**
   * Complete docking sequence
   * @private
   */
  _completeSequence(sequenceId) {
    const sequence = this.activeSequences.get(sequenceId);
    if (!sequence) return;
    
    const duration = Date.now() - sequence.startedAt;
    
    this.emit("docking:complete", {
      sequenceId,
      craftId: sequence.craftId,
      dockId: sequence.dockId,
      duration,
      warnings: sequence.warnings,
    });
    
    this.bus?.emitFrame?.("docking:complete", {
      sequenceId,
      craftId: sequence.craftId,
      dockId: sequence.dockId,
      duration,
      warnings: sequence.warnings,
    });
    
    this.activeSequences.delete(sequenceId);
  }

  /**
   * Abort docking sequence
   * @param {string} sequenceId
   * @param {string} reason
   */
  _abortSequence(sequenceId, reason) {
    const sequence = this.activeSequences.get(sequenceId);
    if (!sequence) return;
    
    this.bus?.emitFrame?.("docking:aborted", {
      sequenceId,
      craftId: sequence.craftId,
      phase: sequence.phase,
      reason,
    });
    
    this.activeSequences.delete(sequenceId);
  }

  /**
   * Get active docking sequences
   * @returns {DockingSequence[]}
   */
  getActiveSequences() {
    return Array.from(this.activeSequences.values());
  }

  /**
   * Emergency abort all docking sequences
   */
  emergencyAbortAll() {
    for (const [sequenceId, sequence] of this.activeSequences) {
      this._abortSequence(sequenceId, "EMERGENCY ABORT");
    }
  }
}
