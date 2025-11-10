// Fleet Bridge Client: Node.js client for Python fleet bridge API
// Fetches craft profiles from Python backend and syncs to station state

import { EventEmitter } from "events";

/**
 * @typedef {import('./station_types.js').CraftProfile} CraftProfile
 * @typedef {import('./station_types.js').StationState} StationState
 */

export class FleetBridgeClient extends EventEmitter {
  /**
   * @param {Object} options
   * @param {string} options.apiBaseUrl - Base URL for Python fleet API
   * @param {number} [options.pollIntervalMs=30000] - Polling interval (30s default)
   * @param {Function} options.getState - Get current station state
   * @param {Function} options.setState - Set station state
   */
  constructor({ apiBaseUrl, pollIntervalMs = 30000, getState, setState }) {
    super();
    this.apiBaseUrl = apiBaseUrl;
    this.pollIntervalMs = pollIntervalMs;
    this.getState = getState;
    this.setState = setState;
    this.pollTimer = null;
    this.connected = false;
    this.lastSyncMs = 0;
    this.syncCount = 0;
  }

  /**
   * Start polling Python fleet API for craft updates
   */
  start() {
    if (this.pollTimer) return; // Already started
    
    this.emit("bridge:starting", { apiBaseUrl: this.apiBaseUrl });
    
    // Initial sync
    this._syncFleet().catch((err) =>
      this.emit("bridge:error", { phase: "initial-sync", error: String(err) })
    );
    
    // Poll periodically
    this.pollTimer = setInterval(() => {
      this._syncFleet().catch((err) =>
        this.emit("bridge:error", { phase: "poll-sync", error: String(err) })
      );
    }, this.pollIntervalMs);
    
    this.emit("bridge:started", { pollIntervalMs: this.pollIntervalMs });
  }

  /**
   * Stop polling
   */
  stop() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    this.connected = false;
    this.emit("bridge:stopped", { syncCount: this.syncCount });
  }

  /**
   * Fetch and sync fleet craft to station state
   * @private
   */
  async _syncFleet() {
    try {
      const url = `${this.apiBaseUrl}/api/fleet/craft`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Fleet API error: ${response.status} ${response.statusText}`);
      }
      
      const craftList = await response.json();
      
      // Update station state with fetched craft
      const state = this.getState();
      
      // Merge strategy: Python fleet data is authoritative for craft registry
      // Keep existing craft not in Python registry (locally added)
      const pythonCraftIds = new Set(craftList.map(c => c.id));
      const localOnlyCraft = state.craft.filter(c => !pythonCraftIds.has(c.id));
      
      // Map Python schema to JS schema
      const mappedCraft = craftList.map(pc => ({
        id: pc.id,
        class: pc.craft_class,  // Python uses craft_class, JS uses class
        dimensions: pc.dimensions,
        massKg: pc.mass_kg,
        portType: pc.port_type,
        fuelType: pc.fuel_type,
        maxRCS: pc.max_rcs,
        capabilities: pc.capabilities,
        status: pc.status,
        maintenanceDueAt: pc.maintenance_due_at,
      }));
      
      state.craft = [...mappedCraft, ...localOnlyCraft];
      this.setState(state);
      
      this.connected = true;
      this.lastSyncMs = Date.now();
      this.syncCount++;
      
      this.emit("bridge:synced", {
        craftCount: craftList.length,
        localOnlyCount: localOnlyCraft.length,
        syncCount: this.syncCount,
      });
    } catch (error) {
      this.connected = false;
      this.emit("bridge:sync-failed", { error: String(error) });
      throw error;
    }
  }

  /**
   * Fetch specific craft by ID
   * @param {string} craftId
   * @returns {Promise<CraftProfile|null>}
   */
  async getCraftById(craftId) {
    try {
      const url = `${this.apiBaseUrl}/api/fleet/craft/${craftId}`;
      const response = await fetch(url);
      
      if (response.status === 404) return null;
      if (!response.ok) {
        throw new Error(`Fleet API error: ${response.status} ${response.statusText}`);
      }
      
      const pc = await response.json();
      
      // Map to JS schema
      return {
        id: pc.id,
        class: pc.craft_class,
        dimensions: pc.dimensions,
        massKg: pc.mass_kg,
        portType: pc.port_type,
        fuelType: pc.fuel_type,
        maxRCS: pc.max_rcs,
        capabilities: pc.capabilities,
        status: pc.status,
        maintenanceDueAt: pc.maintenance_due_at,
      };
    } catch (error) {
      this.emit("bridge:fetch-error", { craftId, error: String(error) });
      return null;
    }
  }

  /**
   * Get fleet status summary
   * @returns {Promise<Object>}
   */
  async getFleetStatus() {
    try {
      const url = `${this.apiBaseUrl}/api/fleet/status`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Fleet API error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      this.emit("bridge:status-error", { error: String(error) });
      throw error;
    }
  }
}
