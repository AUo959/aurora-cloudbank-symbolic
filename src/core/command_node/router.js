/**
 * Aurora CommandNode - Routing Logic
 * Handles command routing across L1, L2, and L3 layers
 * Part of unified CommandNode architecture
 */

import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

// Layer clearance mapping
export const CLEARANCE_LEVELS = {
  'L1_ONLY': ['L1'],
  'L1_L2_BRIDGE': ['L1', 'L2'],
  'L1_L3_INTEGRATION': ['L1', 'L2', 'L3'],
  'L2_L3_BRIDGE': ['L2', 'L3'],
  'L3_SYMBOLIC': ['L3'],
  'EMERGENCY_PROTOCOL': ['L1', 'L2', 'L3', 'EMERGENCY'],
};

// Default L1 agents (Bridge agents)
export const DEFAULT_L1_AGENTS = ['ARCHY', 'LIORA', 'OPPY', 'STARLING_AU', 'RIVERTHREAD_808', 'SHADOWFAX'];

// Default L2 agents (Cognitive agents)
export const DEFAULT_L2_AGENTS = [
  'ARCHY', 'LIORA', 'OPPY', 'STARLING_AU', 'RIVERTHREAD_808', 'DAEDALUS', 'VOIDWHISPER',
];

// Default L3 agents (Symbolic agents)
export const DEFAULT_L3_AGENTS = ['Glyphon', 'Axiomera', 'Sentari', 'Caelion', 'Velatrix', 'Harmion'];

/**
 * Command Router class
 * Routes commands to appropriate handlers based on layer and agent
 */
export class CommandRouter {
  constructor(options = {}) {
    this.routerId = options.routerId || 'AURORA_COMMAND_ROUTER';
    this.version = options.version || '3.5.1';
    this.nodeId = options.nodeId || 'AURORA_COMMAND_NODE';
    this.anchorSeed = options.anchorSeed || 'AURORA_WEB_ENV_FOUNDATION';

    // Routing tables for each layer
    this.routingTables = {
      l1: new Map(),
      l2: new Map(),
      l3: new Map(),
    };

    // Command history and metrics
    this.commandHistory = [];
    this.routingMetrics = {
      totalCommands: 0,
      successfulRoutes: 0,
      failedRoutes: 0,
      averageLatency: 0,
    };

    // Setup log directory
    this.logsDir = options.logsDir || path.join(process.cwd(), 'logs');
    this._ensureLogsDir();

    // Initialize default routes
    this._setupDefaultRoutes();
  }

  /**
   * Ensure logs directory exists
   */
  _ensureLogsDir() {
    if (!fs.existsSync(this.logsDir)) {
      fs.mkdirSync(this.logsDir, { recursive: true });
    }
  }

  /**
   * Setup default routing handlers
   */
  _setupDefaultRoutes() {
    // L1 layer routes
    DEFAULT_L1_AGENTS.forEach(agent => {
      this.routingTables.l1.set(agent, this._createAgentHandler(agent, 'L1'));
    });

    // L2 layer routes
    DEFAULT_L2_AGENTS.forEach(agent => {
      this.routingTables.l2.set(agent, this._createAgentHandler(agent, 'L2'));
    });

    // L3 layer routes
    DEFAULT_L3_AGENTS.forEach(agent => {
      this.routingTables.l3.set(agent, this._createAgentHandler(agent, 'L3'));
    });
  }

  /**
   * Create a handler for an agent
   */
  _createAgentHandler(agentId, layer) {
    return async (command, metadata = {}) => {
      // Simulate agent processing with minimal delay
      const processingDelay = Math.random() * 50 + 25; // 25-75ms

      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            success: true,
            agentId: agentId,
            layer: layer,
            command: command,
            metadata: metadata,
            result: `Processed by ${agentId} on ${layer}`,
            timestamp: Date.now(),
          });
        }, processingDelay);
      });
    };
  }

  /**
   * Route a simple command (backward compatible with aurora_command_router.js)
   * @param {string} commandType - Type of command
   * @param {object} payload - Command payload
   * @returns {object} Routing result with commandId and status
   */
  routeCommand(commandType, payload = {}) {
    const commandId = crypto.randomUUID();
    const timestamp = new Date().toISOString();

    const symbolicCommand = {
      id: commandId,
      type: commandType,
      payload: payload,
      timestamp: timestamp,
      node: this.nodeId,
      anchor: this.anchorSeed,
    };

    // Log command
    this._logCommand(symbolicCommand);

    // Update metrics
    this.routingMetrics.totalCommands++;
    this.routingMetrics.successfulRoutes++;

    return {
      commandId: commandId,
      status: 'routed',
      timestamp: timestamp,
    };
  }

  /**
   * Dispatch a command with full layer routing
   * @param {object} routingRequest - The routing request
   * @returns {Promise<object>} Dispatch result
   */
  async dispatch(routingRequest) {
    const startTime = Date.now();

    try {
      // Validate routing request
      const validation = this._validateRoutingRequest(routingRequest);
      if (!validation.valid) {
        throw new Error(`Routing validation failed: ${validation.reason}`);
      }

      // Determine target layer
      const targetLayer = this._determineTargetLayer(routingRequest.layer);

      // Check clearance
      if (!this._checkClearance(routingRequest.metadata?.clearanceLevel, targetLayer)) {
        throw new Error(`Insufficient clearance for ${targetLayer} access`);
      }

      // Route the command
      const result = await this._routeToLayer(routingRequest, targetLayer);

      // Update metrics
      const latency = Date.now() - startTime;
      this._updateMetrics(true, latency);

      // Log route
      this._logRoute(routingRequest, result, latency, true);

      return result;
    } catch (error) {
      const latency = Date.now() - startTime;
      this._updateMetrics(false, latency);
      this._logRoute(routingRequest, null, latency, false, error.message);

      return {
        success: false,
        error: error.message,
        routingRequest: routingRequest,
        timestamp: Date.now(),
      };
    }
  }

  /**
   * Validate a routing request
   */
  _validateRoutingRequest(request) {
    if (!request.agent) {
      return { valid: false, reason: 'Missing agent field' };
    }
    if (!request.command) {
      return { valid: false, reason: 'Missing command field' };
    }
    if (!request.layer) {
      return { valid: false, reason: 'Missing layer field' };
    }
    return { valid: true };
  }

  /**
   * Determine target layer from layer specification
   */
  _determineTargetLayer(layerSpec) {
    if (layerSpec.includes('L1')) return 'L1';
    if (layerSpec.includes('L2')) return 'L2';
    if (layerSpec.includes('L3')) return 'L3';
    if (layerSpec === 'EMERGENCY_PROTOCOL') return 'L1';
    if (layerSpec === 'SYNC_BEACON') return 'L1';
    if (layerSpec === 'ANCHOR_SYNC') return 'L1';
    if (layerSpec === 'DRIFT_CHECK') return 'L1';
    if (layerSpec === 'MEMORY_AUDIT') return 'L1';
    return 'L2'; // Default to L2
  }

  /**
   * Check clearance for target layer
   */
  _checkClearance(clearanceLevel, targetLayer) {
    if (!clearanceLevel) return true;
    const allowedLayers = CLEARANCE_LEVELS[clearanceLevel];
    if (!allowedLayers) return false;
    return allowedLayers.includes(targetLayer) || allowedLayers.includes('EMERGENCY');
  }

  /**
   * Route command to the appropriate layer
   */
  async _routeToLayer(request, targetLayer) {
    const routingTable = this.routingTables[targetLayer.toLowerCase()];
    if (!routingTable) {
      throw new Error(`No routing table for layer ${targetLayer}`);
    }

    const handler = routingTable.get(request.agent);
    if (!handler) {
      // Create default response for unknown agents
      return this._createDefaultResponse(request, targetLayer);
    }

    const result = await handler(request.command, request.metadata);

    return {
      ...result,
      routedBy: this.routerId,
      routingLayer: targetLayer,
      routingTimestamp: Date.now(),
    };
  }

  /**
   * Create default response for unknown agents
   */
  _createDefaultResponse(request, targetLayer) {
    return {
      success: true,
      agentId: request.agent,
      layer: targetLayer,
      command: request.command,
      result: `Default handling for ${request.agent} on ${targetLayer}`,
      default: true,
      routedBy: this.routerId,
      timestamp: Date.now(),
    };
  }

  /**
   * Update routing metrics
   */
  _updateMetrics(success, latency) {
    this.routingMetrics.totalCommands++;
    if (success) {
      this.routingMetrics.successfulRoutes++;
    } else {
      this.routingMetrics.failedRoutes++;
    }

    // Update average latency
    const totalLatency =
      this.routingMetrics.averageLatency * (this.routingMetrics.totalCommands - 1) + latency;
    this.routingMetrics.averageLatency = totalLatency / this.routingMetrics.totalCommands;
  }

  /**
   * Log a simple command
   */
  _logCommand(command) {
    try {
      const logPath = path.join(this.logsDir, 'aurora_command_routing.log');
      const logEntry = JSON.stringify(command) + '\n';
      fs.appendFileSync(logPath, logEntry);
    } catch {
      // Ignore logging errors
    }
  }

  /**
   * Log a route event
   */
  _logRoute(request, result, latency, success, error = null) {
    const logEntry = {
      timestamp: Date.now(),
      routerId: this.routerId,
      agent: request.agent,
      layer: request.layer,
      success: success,
      latency: latency,
      command: request.command?.type || 'unknown',
      error: error,
    };

    this.commandHistory.push(logEntry);

    // Keep history manageable
    if (this.commandHistory.length > 1000) {
      this.commandHistory = this.commandHistory.slice(-500);
    }
  }

  /**
   * Register a custom route
   */
  registerRoute(layer, agentId, handler) {
    const routingTable = this.routingTables[layer.toLowerCase()];
    if (!routingTable) {
      throw new Error(`Invalid layer: ${layer}`);
    }
    routingTable.set(agentId, handler);
    return { status: 'registered', agent: agentId, layer };
  }

  /**
   * Unregister a route
   */
  unregisterRoute(layer, agentId) {
    const routingTable = this.routingTables[layer.toLowerCase()];
    if (!routingTable) return false;
    return routingTable.delete(agentId);
  }

  /**
   * Get router status
   */
  getStatus() {
    return {
      routerId: this.routerId,
      version: this.version,
      metrics: this.routingMetrics,
      recentCommands: this.commandHistory.slice(-10),
      routingTables: {
        l1: Array.from(this.routingTables.l1.keys()),
        l2: Array.from(this.routingTables.l2.keys()),
        l3: Array.from(this.routingTables.l3.keys()),
      },
      clearanceLevels: Object.keys(CLEARANCE_LEVELS),
    };
  }

  /**
   * Get metrics
   */
  getMetrics() {
    const successRate =
      this.routingMetrics.totalCommands > 0
        ? (this.routingMetrics.successfulRoutes / this.routingMetrics.totalCommands) * 100
        : 0;

    return {
      ...this.routingMetrics,
      successRate: successRate,
      recentLatency: this.commandHistory.slice(-10).map((c) => c.latency),
      timestamp: Date.now(),
    };
  }
}

export default CommandRouter;
