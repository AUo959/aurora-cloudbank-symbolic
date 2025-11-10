// DLP Manifest Generator: Station state persistence with lineage tracking
// Generates DLP-compliant manifests for station snapshots with T1/SRB anchors

import { createHash } from "crypto";
import { mkdir, writeFile } from "fs/promises";
import { join } from "path";

/**
 * @typedef {import('./station_types.js').StationState} StationState
 */

/**
 * DLP Manifest structure for station snapshots
 * @typedef {Object} DLPManifest
 * @property {string} manifestId - Unique manifest ID
 * @property {string} contextTag - DLP context tag
 * @property {number} timestamp - Unix timestamp (ms)
 * @property {string} chainNotation - Current chain notation (e.g., "001//999//")
 * @property {Object} anchors - T1/SRB anchor state
 * @property {number} anchors.t1State - T1 temporal anchor value
 * @property {number} anchors.srbResolution - SRB spatial-relational boundary
 * @property {string} stateHash - SHA-256 hash of station state
 * @property {Object} snapshot - Station state snapshot
 * @property {Object} metadata - Additional tracking metadata
 */

export class DLPManifestGenerator {
  /**
   * @param {Object} options
   * @param {string} options.manifestDir - Directory to persist manifests
   * @param {Function} options.getState - Get current station state
   */
  constructor({ manifestDir = "./station_manifests", getState }) {
    this.manifestDir = manifestDir;
    this.getState = getState;
    this.lastManifestId = null;
    this.manifestCount = 0;
  }

  /**
   * Generate DLP manifest for current station state
   * @param {Object} options
   * @param {string} options.contextTag - DLP context tag
   * @param {string} [options.chainNotation="001//999//"] - Chain notation
   * @param {number} [options.t1State=0] - T1 anchor state
   * @param {number} [options.srbResolution=0] - SRB anchor resolution
   * @param {Object} [options.metadata={}] - Additional metadata
   * @returns {Promise<DLPManifest>}
   */
  async generateManifest({
    contextTag,
    chainNotation = "001//999//",
    t1State = 0,
    srbResolution = 0,
    metadata = {},
  }) {
    const timestamp = Date.now();
    const state = this.getState();
    
    // Generate state hash for integrity verification
    const stateJson = JSON.stringify(state, null, 0);
    const stateHash = createHash("sha256").update(stateJson).digest("hex");
    
    // Generate manifest ID
    const manifestId = `MANIFEST-${timestamp}-${stateHash.slice(0, 8)}`;
    
    const manifest = {
      manifestId,
      contextTag,
      timestamp,
      chainNotation,
      anchors: {
        t1State,
        srbResolution,
      },
      stateHash,
      snapshot: state,
      metadata: {
        ...metadata,
        craftCount: state.craft.length,
        dockCount: state.docks.length,
        trafficSlotCount: state.traffic.length,
        activeMissions: state.missions.length,
        fuelAvailable: state.fuel.tanks.reduce((sum, t) => sum + t.availableKg, 0),
        maintenanceTasks: state.maintenance.length,
        generatorVersion: "1.0.0",
      },
    };
    
    this.lastManifestId = manifestId;
    this.manifestCount++;
    
    return manifest;
  }

  /**
   * Persist manifest to filesystem
   * @param {DLPManifest} manifest
   * @returns {Promise<string>} - Path to persisted manifest
   */
  async persistManifest(manifest) {
    // Ensure manifest directory exists
    await mkdir(this.manifestDir, { recursive: true });
    
    // Generate filename with timestamp and context tag
    const sanitizedTag = manifest.contextTag.replace(/[^a-zA-Z0-9_-]/g, "_");
    const filename = `${manifest.timestamp}_${sanitizedTag}_${manifest.manifestId}.json`;
    const filepath = join(this.manifestDir, filename);
    
    // Write manifest with pretty formatting
    await writeFile(filepath, JSON.stringify(manifest, null, 2), "utf-8");
    
    return filepath;
  }

  /**
   * Generate and persist manifest in one operation
   * @param {Object} options - Same as generateManifest options
   * @returns {Promise<{manifest: DLPManifest, filepath: string}>}
   */
  async captureSnapshot(options) {
    const manifest = await this.generateManifest(options);
    const filepath = await this.persistManifest(manifest);
    
    return { manifest, filepath };
  }

  /**
   * Validate manifest integrity
   * @param {DLPManifest} manifest
   * @returns {boolean}
   */
  validateManifest(manifest) {
    // Recompute state hash
    const stateJson = JSON.stringify(manifest.snapshot, null, 0);
    const computedHash = createHash("sha256").update(stateJson).digest("hex");
    
    return computedHash === manifest.stateHash;
  }

  /**
   * Get manifest generation statistics
   * @returns {Object}
   */
  getStats() {
    return {
      lastManifestId: this.lastManifestId,
      manifestCount: this.manifestCount,
      manifestDir: this.manifestDir,
    };
  }
}
