// Maintenance Orchestrator: Schedules and manages craft servicing workflows

import { EventEmitter } from "events";

/**
 * @typedef {import('./station_types.js').MaintenanceTask} MaintenanceTask
 * @typedef {import('./station_types.js').StationState} StationState
 * @typedef {import('./station_types.js').CraftProfile} CraftProfile
 */

/**
 * Maintenance task templates by craft class
 */
const MAINTENANCE_TEMPLATES = {
  "ORS-SHUTTLE-XL": {
    "POST_FLIGHT_INSPECT": { hours: 2, skills: ["inspect", "systems"], parts: [] },
    "ENGINE_SERVICE": { hours: 8, skills: ["propulsion", "certified"], parts: ["filter-LH2", "seal-kit"] },
    "HULL_INTEGRITY": { hours: 4, skills: ["structural", "weld"], parts: ["patch-composite"] },
    "AVIONICS_CHECK": { hours: 3, skills: ["avionics", "certified"], parts: [] },
  },
  "ORS-FRIGATE-CONSTANCY": {
    "POST_FLIGHT_INSPECT": { hours: 4, skills: ["inspect", "systems", "senior"], parts: [] },
    "ENGINE_SERVICE": { hours: 16, skills: ["propulsion", "certified", "senior"], parts: ["filter-LH2", "seal-kit", "coolant"] },
    "HULL_INTEGRITY": { hours: 12, skills: ["structural", "weld", "senior"], parts: ["patch-composite", "armor-plate"] },
    "WEAPON_SYSTEMS": { hours: 8, skills: ["armament", "certified"], parts: ["rail-coil", "targeting-array"] },
  },
  "ORS-PROBE-SURVEYOR": {
    "POST_FLIGHT_INSPECT": { hours: 1, skills: ["inspect"], parts: [] },
    "SENSOR_CALIBRATE": { hours: 2, skills: ["sensors", "certified"], parts: ["cal-kit"] },
  },
  "ORS-DRONE-SCOUT": {
    "POST_FLIGHT_INSPECT": { hours: 0.5, skills: ["inspect"], parts: [] },
    "BATTERY_SERVICE": { hours: 1, skills: ["power"], parts: ["battery-cell"] },
  },
};

export class MaintenanceOrchestrator extends EventEmitter {
  /**
   * @param {Object} options
   * @param {Function} options.getState - Get station state
   * @param {Function} options.setState - Set station state
   * @param {Object} options.bus - Telemetry bus
   */
  constructor({ getState, setState, bus }) {
    super();
    this.getState = getState;
    this.setState = setState;
    this.bus = bus;
    this.checkIntervalMs = 60000; // 1 minute
    this.checkTimer = null;
    this._startChecks();
  }

  /**
   * Start periodic maintenance checks
   * @private
   */
  _startChecks() {
    if (this.checkTimer) return;
    
    this.checkTimer = setInterval(() => {
      try {
        this._runMaintenanceCheck();
      } catch (e) {
        this.bus?.emitFrame?.("maintenance:check:error", { error: String(e) });
      }
    }, this.checkIntervalMs);
    
    // Run initial check
    this._runMaintenanceCheck();
  }

  /**
   * Stop maintenance checks
   */
  stop() {
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = null;
    }
  }

  /**
   * Check for overdue maintenance and schedule tasks
   * @private
   */
  _runMaintenanceCheck() {
    const state = this.getState();
    const now = Date.now();
    
    for (const craft of state.craft) {
      // Check if maintenance is due
      if (craft.maintenanceDueAt && craft.maintenanceDueAt < now) {
        // Find existing tasks for this craft
        const existingTasks = state.maintenance.filter(t => t.craftId === craft.id);
        
        // If no tasks scheduled, create post-flight inspection
        if (existingTasks.length === 0) {
          this.scheduleMaintenance(craft.id, "POST_FLIGHT_INSPECT", {
            priority: "HIGH",
            reason: "Overdue maintenance detected",
          });
        }
      }
    }
    
    // Check task deadlines
    const overdueTasks = state.maintenance.filter(
      t => t.status !== "COMPLETED" && t.dueBy && t.dueBy < now
    );
    
    if (overdueTasks.length > 0) {
      this.bus?.emitFrame?.("maintenance:tasks:overdue", {
        count: overdueTasks.length,
        taskIds: overdueTasks.map(t => t.taskId),
      });
    }
  }

  /**
   * Schedule maintenance task for craft
   * @param {string} craftId
   * @param {string} templateName
   * @param {Object} options
   * @param {string} [options.priority="NORMAL"] - Task priority
   * @param {string} [options.reason] - Reason for maintenance
   * @param {number} [options.dueBy] - Deadline timestamp
   * @returns {MaintenanceTask}
   */
  scheduleMaintenance(craftId, templateName, options = {}) {
    const state = this.getState();
    const craft = state.craft.find(c => c.id === craftId);
    
    if (!craft) {
      throw new Error(`Craft ${craftId} not found`);
    }
    
    // Get template for craft class
    const templates = MAINTENANCE_TEMPLATES[craft.class] || MAINTENANCE_TEMPLATES["ORS-SHUTTLE-XL"];
    const template = templates[templateName];
    
    if (!template) {
      throw new Error(`Template ${templateName} not found for ${craft.class}`);
    }
    
    // Create task
    const taskId = `MAINT-${Date.now()}-${craftId}`;
    const task = {
      taskId,
      craftId,
      template: templateName,
      required: template,
      status: "SCHEDULED",
      dueBy: options.dueBy || Date.now() + (template.hours * 3600000), // hours to ms
      deferralAllowed: options.priority !== "CRITICAL",
      notes: options.reason || `Scheduled ${templateName}`,
      priority: options.priority || "NORMAL",
    };
    
    state.maintenance.push(task);
    this.setState(state);
    
    this.bus?.emitFrame?.("maintenance:scheduled", {
      taskId,
      craftId,
      template: templateName,
      dueBy: task.dueBy,
    });
    
    return task;
  }

  /**
   * Start maintenance task execution
   * @param {string} taskId
   * @param {Object} crew - Crew assignment
   * @returns {boolean}
   */
  startTask(taskId, crew = {}) {
    const state = this.getState();
    const task = state.maintenance.find(t => t.taskId === taskId);
    
    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }
    
    if (task.status !== "SCHEDULED") {
      return false; // Already in progress or completed
    }
    
    task.status = "IN_PROGRESS";
    task.startedAt = Date.now();
    task.crew = crew;
    this.setState(state);
    
    this.bus?.emitFrame?.("maintenance:started", {
      taskId,
      craftId: task.craftId,
      estimatedHours: task.required.hours,
    });
    
    return true;
  }

  /**
   * Complete maintenance task
   * @param {string} taskId
   * @param {Object} results - Task completion results
   * @returns {boolean}
   */
  completeTask(taskId, results = {}) {
    const state = this.getState();
    const task = state.maintenance.find(t => t.taskId === taskId);
    
    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }
    
    task.status = "COMPLETED";
    task.completedAt = Date.now();
    task.results = results;
    
    // Update craft maintenance due date
    const craft = state.craft.find(c => c.id === task.craftId);
    if (craft) {
      // Schedule next maintenance based on craft class
      const nextMaintenanceHours = craft.class === "ORS-FRIGATE-CONSTANCY" ? 168 : 72; // 1 week vs 3 days
      craft.maintenanceDueAt = Date.now() + (nextMaintenanceHours * 3600000);
    }
    
    this.setState(state);
    
    this.bus?.emitFrame?.("maintenance:completed", {
      taskId,
      craftId: task.craftId,
      duration: task.completedAt - task.startedAt,
    });
    
    return true;
  }

  /**
   * Get maintenance summary for all craft
   * @returns {Object}
   */
  getMaintenanceSummary() {
    const state = this.getState();
    
    return {
      totalTasks: state.maintenance.length,
      scheduled: state.maintenance.filter(t => t.status === "SCHEDULED").length,
      inProgress: state.maintenance.filter(t => t.status === "IN_PROGRESS").length,
      completed: state.maintenance.filter(t => t.status === "COMPLETED").length,
      overdue: state.maintenance.filter(
        t => t.status !== "COMPLETED" && t.dueBy && t.dueBy < Date.now()
      ).length,
      craftNeedingMaintenance: state.craft.filter(
        c => c.maintenanceDueAt && c.maintenanceDueAt < Date.now()
      ).length,
    };
  }
}
