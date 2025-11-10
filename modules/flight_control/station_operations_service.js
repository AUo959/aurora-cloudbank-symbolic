"use strict";

// StationOperationsService: minimal flight control core wiring
typeof module !== 'undefined' && (module.exports = {});

class StationOperationsService {
  constructor({ bus, ethics, getState, setState }) {
    this.bus = bus;
    this.ethics = ethics;
    this.getState = getState;
    this.setState = setState;
    this._wire();
  }

  _wire() {
    if (!this.bus) return;
    this.bus.on("dock:request", (frame) => this._onDockRequest(frame));
    this.bus.on("launch:request", (frame) => this._onLaunchRequest(frame));
    this.bus.on("resource:fuel:reserve", (f) => this._reserveFuel(f));
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

if (typeof module !== "undefined") {
  module.exports.StationOperationsService = StationOperationsService;
}
