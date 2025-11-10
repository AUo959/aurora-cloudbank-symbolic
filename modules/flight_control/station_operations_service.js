// StationOperationsService: minimal flight control core wiring (ESM)

export class StationOperationsService {
  constructor({ bus, ethics, getState, setState }) {
    this.bus = bus;
    this.ethics = ethics;
    this.getState = getState;
    this.setState = setState;
    // scheduler state
    this._lastScheduleRun = 0;
    this._scheduleIntervalMs = 15000; // 15s minimal cadence
    this._scheduleTimer = null;
    this._wire();
  }

  _wire() {
    if (!this.bus) return;
    this.bus.on("dock:request", (frame) => this._onDockRequest(frame));
    this.bus.on("launch:request", (frame) => this._onLaunchRequest(frame));
    this.bus.on("resource:fuel:reserve", (f) => this._reserveFuel(f));
    // start lightweight scheduling loop
    this._startSchedulingLoop();
  }

  _startSchedulingLoop() {
    if (this._scheduleTimer) return;
    this._scheduleTimer = setInterval(() => {
      try { this._runScheduler(); } catch (e) {
        this.bus.emitFrame && this.bus.emitFrame("ops:scheduler:error", { error: String(e) });
      }
    }, this._scheduleIntervalMs);
  }

  _runScheduler() {
    const now = Date.now();
    const state = this.getState();
    // simple compaction: expire slots past end, emit updates, attempt reassignment
    const expired = [];
    for (const slot of state.traffic) {
      if (slot.status === "CONFIRMED" && slot.window.end < now) {
        slot.status = "EXPIRED";
        expired.push(slot.slotId);
        this.bus.emitFrame && this.bus.emitFrame("traffic:slot:expired", { slotId: slot.slotId });
      }
    }
    // minimal backpressure metric (expired vs active)
    const activeSlots = state.traffic.filter(s => s.status === "CONFIRMED").length;
    state.ops.backpressure = activeSlots > 20 ? 1 : activeSlots/20;
    state.ops.schedulerLagMs = now - this._lastScheduleRun;
    this._lastScheduleRun = now;
    this.setState(state);
    this.bus.emitFrame && this.bus.emitFrame("traffic:schedule:tick", {
      active: activeSlots,
      expiredCount: expired.length,
      lagMs: state.ops.schedulerLagMs,
    });
  }

  _gate(intent) {
    const verdict = this.ethics && this.ethics.validate ? this.ethics.validate(intent) : { passed: true };
    this.bus && this.bus.emitFrame && this.bus.emitFrame("ethics:check", { component: "StationOps", verdict });
    if (!verdict.passed) {
      this.bus.emitFrame("ops:blocked", { reason: verdict.rationale, intent });
      return { ok: false, verdict };
    }
    return { ok: true, verdict };
  }

  _onDockRequest({ craftId, desiredWindow, constraints, context }) {
    const gated = this._gate({
      actor: "StationOps",
      action: { kind: "dock-clearance", priority: "essential" },
      payload: { intent: "dock", craftId },
      context,
    });
    if (!gated.ok) return;

    const state = this.getState();
    const craft = state.craft.find((c) => c.id === craftId);
    const dock = this._findCompatibleDock(state, craft);
    const slot = this._allocateSlot(state, desiredWindow, "ARRIVAL");

    if (!dock || !slot) {
      return this.bus.emitFrame("dock:denied", { craftId, reason: "no_dock_or_slot" });
    }

    dock.status = "ASSIGNED";
    dock.occupancy = { craftId, since: Date.now() };
    slot.assignedCraftId = craftId;
    slot.status = "CONFIRMED";

    this.setState(state);
    this.bus.emitFrame("dock:assigned", { craftId, dockId: dock.id, slotId: slot.slotId });
    // emit approach phase kickoff
    this.bus.emitFrame("dock:approach", { craftId, dockId: dock.id });
  }

  _onLaunchRequest({ craftId, window, context }) {
    const gated = this._gate({
      actor: "StationOps",
      action: { kind: "launch-clearance", priority: "essential" },
      payload: { intent: "launch", craftId },
      context,
    });
    if (!gated.ok) return;

    // TODO: safety/corridor checks
    this.bus.emitFrame("launch:window", { craftId, window, ok: true });
    this.bus.emitFrame("launch:armed", { craftId });
    this.bus.emitFrame("launch:go", { craftId });
    // placeholder for post-launch tracking
    this.bus.emitFrame("launch:telemetry:init", { craftId });
  }

  _reserveFuel({ craftId, kg, fuelType, context }) {
    const gated = this._gate({
      actor: "StationOps",
      action: { kind: "fuel-reserve", priority: "essential" },
      payload: { intent: "fuel", craftId, kg, fuelType },
      context,
    });
    if (!gated.ok) return;

    const state = this.getState();
    const tank = state.fuel.tanks.find((t) => t.fuelType === fuelType);
    if (!tank || tank.availableKg < kg) {
      return this.bus.emitFrame("resource:fuel:denied", { craftId, reason: "insufficient" });
    }
    tank.availableKg -= kg;
    state.fuel.entries.push({ id: `TX-${Date.now()}`, ts: Date.now(), craftId, type: "ISSUE", fuelType, kg, by: "StationOps" });
    this.setState(state);
    this.bus.emitFrame("resource:fuel:commit", { craftId, fuelType, kg });
  }

  _findCompatibleDock(state, craft) {
    if (!craft) return undefined;
    return state.docks.find(
      (d) => d.status === "FREE" && d.compatibleClasses && d.compatibleClasses.includes(craft.class) && !(d.safety && d.safety.evaOpen)
    );
  }

  _allocateSlot(state, desiredWindow, op) {
    const id = `SLOT-${Date.now()}`;
    const slot = { slotId: id, window: desiredWindow || { start: Date.now(), end: Date.now() + 600000 }, op, corridor: "L-ALPHA-OUT", priority: "NORMAL", status: "CONFIRMED" };
    state.traffic.push(slot);
    return slot;
  }
}

