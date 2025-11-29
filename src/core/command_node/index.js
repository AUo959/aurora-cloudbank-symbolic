/**
 * Aurora CommandNode - Unified Command Node Architecture
 * Consolidates routing, encryption, ethics, and THREADCORE functionality
 *
 * This module provides a single canonical interface for:
 * - Simple CLI/workflow routing (previously aurora_command_router.js)
 * - Secure encrypted dispatch (previously src/nodes/command_node.js)
 * - Ethics validation (previously src/core/command_node.js)
 * - THREADCORE integration (previously services/command_node/)
 *
 * @version 3.5.1
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// Import sub-modules
import { CommandRouter, CLEARANCE_LEVELS } from './router.js';
import { encryptPayload, decryptPayload, isEncryptionAvailable } from './encryption.js';
import { ethicsCheck, anchorResolve, validateEthics, getDefaultProtocol } from './ethics.js';
import {
  threadcore,
  patchweaver,
  zipwiz,
  ThreadcoreAdapter,
  PatchweaverAdapter,
  ZipwizAdapter,
  DEFAULT_GLYPH_AGENTS,
  DEFAULT_ANCHOR_SEED,
} from './threadcore.js';

// Node metadata
export const SYMBOLIC_NODE_METADATA = {
  node: 'ORION_CORE_COMMAND',
  version: 'v3.5.1',
  mode: 'unified',
  deployTimestamp: new Date().toISOString(),
  linkedAgents: ['ZIPWIZ', 'PATCHWEAVER', 'THREADCORE'],
  status: 'live',
};

/**
 * Unified CommandNode class
 * Provides all command node functionality in a single interface
 */
export class CommandNode {
  constructor(options = {}) {
    this.nodeId = options.nodeId || 'AURORA_COMMAND_NODE';
    this.version = options.version || 'v3.5.1';
    this.anchorSeed = options.anchorSeed || DEFAULT_ANCHOR_SEED;
    this.ethicsProtocol = options.ethicsProtocol || getDefaultProtocol();
    this.enableEncryption = options.enableEncryption !== false && isEncryptionAvailable();

    // Initialize router
    this.router = new CommandRouter({
      nodeId: this.nodeId,
      version: this.version,
      anchorSeed: this.anchorSeed,
      logsDir: options.logsDir,
    });

    // THREADCORE components (create new instances for each CommandNode)
    this.threadcore = new ThreadcoreAdapter();
    this.patchweaver = new PatchweaverAdapter();
    this.zipwiz = new ZipwizAdapter();

    // Diagnostics
    this.diagnostics = this._loadDiagnostics();

    // Setup logs directory
    this.logsDir = options.logsDir || path.join(process.cwd(), 'logs');
    this._ensureLogsDir();

    // Initialize timestamp
    this.timestamp = new Date().toISOString();
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
   * Load diagnostics state
   */
  _loadDiagnostics() {
    const diagPath = path.join(process.cwd(), 'diagnostics.json');
    try {
      if (fs.existsSync(diagPath)) {
        return JSON.parse(fs.readFileSync(diagPath, 'utf8'));
      }
    } catch {
      // Ignore errors
    }
    return {
      commandCount: 0,
      processedCount: 0,
      lastCommandAt: null,
      load: 0,
    };
  }

  /**
   * Save diagnostics state
   */
  _saveDiagnostics() {
    const diagPath = path.join(process.cwd(), 'diagnostics.json');
    try {
      fs.writeFileSync(diagPath, JSON.stringify(this.diagnostics, null, 2));
    } catch {
      // Ignore errors
    }
  }

  // ============================================
  // SIMPLE ROUTING (aurora_command_router.js compatibility)
  // ============================================

  /**
   * Route a command through symbolic dispatch
   * @param {string} commandType - Type of command
   * @param {object} payload - Command payload
   * @returns {object} Routing result with commandId and status
   */
  routeCommand(commandType, payload = {}) {
    return this.router.routeCommand(commandType, payload);
  }

  /**
   * Initialize web environment via command node
   * @param {object} config - Configuration options
   */
  initWebEnvironment(config = {}) {
    return this.routeCommand('WEB_ENV_INIT', {
      environment_type: 'multi_agent_quantum_hybrid',
      foundation_phase: 'architecture_planning',
      features: [
        'symbolic_cpu_anchor',
        'interactive_interface',
        'research_hub_framework',
        'audiovisual_system',
      ],
      config: config,
    });
  }

  /**
   * Coordinate multi-agent system
   * @param {string[]} agents - List of agents to coordinate
   */
  coordinateMultiAgent(agents = []) {
    return this.routeCommand('MULTI_AGENT_COORD', {
      agents: agents,
      coordination_mode: 'quantum_symbolic',
      synergy_level: 'high',
    });
  }

  /**
   * Establish quantum anchor
   * @param {object} anchorConfig - Anchor configuration
   */
  establishQuantumAnchor(anchorConfig = {}) {
    return this.routeCommand('QUANTUM_ANCHOR_EST', {
      anchor_type: 'symbolic_cpu',
      quantum_layer: 'hybrid_processing',
      config: anchorConfig,
    });
  }

  // ============================================
  // ENCRYPTED DISPATCH (src/nodes/command_node.js compatibility)
  // ============================================

  /**
   * Dispatch a symbolic command with optional encryption
   * @param {object} symbolicCommand - The command to dispatch
   * @param {object} options - Dispatch options
   * @returns {object} Dispatch result
   */
  dispatchSymbolicCommand(symbolicCommand, options = {}) {
    const useEncryption = options.encrypt !== false && this.enableEncryption;

    const payload = {
      metadata: SYMBOLIC_NODE_METADATA,
      command: symbolicCommand,
      anchor: this.anchorSeed,
    };

    let result;
    if (useEncryption) {
      try {
        const encrypted = encryptPayload(payload);
        const dispatchPath = path.join(this.logsDir, 'dispatch.encrypted.json');
        fs.writeFileSync(dispatchPath, JSON.stringify(encrypted, null, 2));
        result = {
          success: true,
          encrypted: true,
          location: dispatchPath,
        };
      } catch (error) {
        result = {
          success: false,
          encrypted: false,
          error: error.message,
        };
      }
    } else {
      const dispatchPath = path.join(this.logsDir, 'dispatch.json');
      fs.writeFileSync(dispatchPath, JSON.stringify(payload, null, 2));
      result = {
        success: true,
        encrypted: false,
        location: dispatchPath,
      };
    }

    return result;
  }

  // ============================================
  // ETHICS VALIDATION (src/core/command_node.js compatibility)
  // ============================================

  /**
   * Execute a command with ethics validation
   * @param {object} command - The command to execute
   * @returns {string} Execution result message
   * @throws {Error} If ethics check fails
   */
  executeCommand(command) {
    // Ethics check
    if (!ethicsCheck(command)) {
      throw new Error('Ethics violation detected');
    }

    // Update diagnostics
    this.diagnostics.commandCount = (this.diagnostics.commandCount || 0) + 1;
    this.diagnostics.lastCommandAt = Date.now();
    this.diagnostics.load =
      this.diagnostics.commandCount - (this.diagnostics.processedCount || 0);
    this._saveDiagnostics();

    // Resolve anchor
    const anchor = anchorResolve(command.context || 'AUTO');

    // Process command
    this.diagnostics.processedCount = (this.diagnostics.processedCount || 0) + 1;
    this._saveDiagnostics();

    return `Command ${command.name || command.action} executed with anchor ${anchor}`;
  }

  /**
   * Validate command ethics
   * @param {object} command - Command to validate
   * @returns {object} Validation result
   */
  validateCommand(command) {
    return validateEthics(command, this.ethicsProtocol);
  }

  // ============================================
  // LAYER DISPATCH (src/system/aurora_command_router.js compatibility)
  // ============================================

  /**
   * Dispatch command with full layer routing
   * @param {object} routingRequest - Routing request with agent, layer, command
   * @returns {Promise<object>} Dispatch result
   */
  async dispatch(routingRequest) {
    return this.router.dispatch(routingRequest);
  }

  /**
   * Route L3 validation request
   * @param {string} agentId - Agent to handle validation
   * @param {object} validationRequest - Validation request
   */
  async routeL3Validation(agentId, validationRequest) {
    return this.dispatch({
      agent: agentId,
      layer: 'L3_SYMBOLIC',
      command: {
        type: 'validation',
        ...validationRequest,
      },
      metadata: {
        clearanceLevel: 'L1_L3_INTEGRATION',
        validationType: 'symbolic',
      },
    });
  }

  /**
   * Route emergency request
   * @param {object} emergencyRequest - Emergency request
   */
  async routeEmergency(emergencyRequest) {
    return this.dispatch({
      agent: 'SHADOWFAX',
      layer: 'EMERGENCY_PROTOCOL',
      command: emergencyRequest,
      metadata: {
        clearanceLevel: 'EMERGENCY_PROTOCOL',
        priority: 'CRITICAL',
      },
    });
  }

  // ============================================
  // THREADCORE INTEGRATION (services/command_node/ compatibility)
  // ============================================

  /**
   * Initialize Aurora Core with THREADCORE
   * @param {object} options - Initialization options
   */
  initializeAuroraCore(options = {}) {
    const config = {
      seed: options.seed || this.anchorSeed,
      ethics: options.ethics || this.ethicsProtocol,
      glyphAgents: options.glyphAgents || DEFAULT_GLYPH_AGENTS,
    };

    this.threadcore.init(config);
    this.patchweaver.connect();
    this.zipwiz.pingBeacon('constellation');

    return {
      status: 'initialized',
      config: config,
      components: {
        threadcore: this.threadcore.isInitialized(),
        patchweaver: this.patchweaver.isConnected(),
        zipwiz: true,
      },
    };
  }

  /**
   * Relay command to THREADCORE
   * @param {string} command - Command name
   * @param {*} payload - Command payload
   */
  relayCommand(command, payload) {
    switch (command) {
      case 'SEED_ANCHOR':
        return this.threadcore.seed(payload);
      case 'UPDATE_THREAD':
        return this.threadcore.update(payload);
      case 'REFLECT':
        return this.threadcore.reflect();
      default:
        return { status: 'unknown_command', command };
    }
  }

  // ============================================
  // STATUS AND UTILITIES
  // ============================================

  /**
   * Get node status
   */
  getStatus() {
    return {
      nodeId: this.nodeId,
      version: this.version,
      timestamp: this.timestamp,
      anchorSeed: this.anchorSeed,
      ethicsProtocol: this.ethicsProtocol,
      encryptionAvailable: this.enableEncryption,
      router: this.router.getStatus(),
      diagnostics: this.diagnostics,
      components: {
        threadcore: this.threadcore.isInitialized(),
        patchweaver: this.patchweaver.isConnected(),
      },
    };
  }

  /**
   * Get metrics
   */
  getMetrics() {
    return this.router.getMetrics();
  }

  /**
   * Register a custom route
   */
  registerRoute(layer, agentId, handler) {
    return this.router.registerRoute(layer, agentId, handler);
  }

  /**
   * Unregister a route
   */
  unregisterRoute(layer, agentId) {
    return this.router.unregisterRoute(layer, agentId);
  }
}

// Re-export utilities
export {
  CommandRouter,
  CLEARANCE_LEVELS,
  encryptPayload,
  decryptPayload,
  isEncryptionAvailable,
  ethicsCheck,
  anchorResolve,
  validateEthics,
  getDefaultProtocol,
  threadcore,
  patchweaver,
  zipwiz,
  ThreadcoreAdapter,
  PatchweaverAdapter,
  ZipwizAdapter,
  DEFAULT_GLYPH_AGENTS,
  DEFAULT_ANCHOR_SEED,
};

// Default export
export default CommandNode;
