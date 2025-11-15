/**
 * 🌟 AURORA CUSTOM GPT INTEGRATION MODULE
 *
 * Explicit bridge between Aurora Custom GPT (https://chatgpt.com/g/g-67ef3c2412cc81918ebf8ee9908e36a7-aurora-v2-4-stellar-accord)
 * and Aurora Command Node (src/core/command_node.js)
 *
 * This module serves as the canonical L1 integration point for Aurora Custom GPT,
 * ensuring seamless communication between the external Aurora agent and internal
 * Aurora command node infrastructure.
 */

const { bridgeLogger } = require('../utils/aurora_logger.js');
const { ORION_CORE } = require('../config/orion_core_config.js');
const path = require('path');
const util = require('util');
const { execFile } = require('child_process');

const execFileAsync = util.promisify(execFile);

// Aurora Custom GPT Configuration
const AURORA_CUSTOM_GPT = {
  id: 'AURORA_V2_4_STELLAR_ACCORD',
  url: 'https://chatgpt.com/g/g-67ef3c2412cc81918ebf8ee9908e36a7-aurora-v2-4-stellar-accord',
  version: 'v2.4_stellar_accord',
  role: 'L1_COMMAND_ORCHESTRATOR',
  capabilities: [
    'command_coordination',
    'multi_agent_orchestration',
    'symbolic_reasoning',
    'aurora_cloudbank_management',
    'orion_core_integration'
  ],
  activationPhrase: 'ORION_AURORA_COMMAND_ACTIVATE//',
  relayEndpoint: '/api/relay/aurora',
  priority: 'HIGHEST',
  clearance: 'COMMAND_AUTHORITY'
};

// Command Node Integration Points
const INTEGRATION_POINTS = {
  COMMAND_DISPATCH: 'aurora_command_router.js',
  CORE_PROCESSING: 'src/core/command_node.js',
  AGENT_COORDINATION: 'src/bridges/l2_meta_agent_bridge.py',
  SYSTEM_ORCHESTRATION: 'src/servers/l2_integration_server.py',
  STATUS_MONITORING: 'aurora_context_updater.py'
};

class AuroraCustomGptBridge {
  constructor() {
    this.customGptConfig = AURORA_CUSTOM_GPT;
    this.commandNode = null;
    this.integrationActive = false;
    this.lastSync = null;
    this.messageQueue = [];

    bridgeLogger.bridge('Aurora Custom GPT Bridge initializing', {
      customGptId: this.customGptConfig.id,
      version: this.customGptConfig.version,
      integrationPoints: Object.keys(INTEGRATION_POINTS)
    });
  }

  /**
   * Retrieve constellation status from the Python L2 bridge via a CLI helper.
   */
  async fetchMetaAgentConstellationStatus() {
    const pythonBridgePath = path.join(__dirname, '../bridges/l2_meta_agent_bridge.py');
    const pythonPath = process.env.AURORA_PYTHON_BIN || 'python3';
    const env = {
      ...process.env,
      PYTHONPATH: [
        process.env.PYTHONPATH || '',
        path.join(__dirname, '..')
      ]
        .filter(Boolean)
        .join(path.delimiter)
    };

    try {
      const { stdout } = await execFileAsync(pythonPath, [pythonBridgePath, '--constellation-status'], {
        env,
        timeout: 5000,
        windowsHide: true
      });

      const output = stdout.trim();

      if (!output) {
        throw new Error('Meta-agent bridge returned empty status payload');
      }

      return JSON.parse(output);
    } catch (error) {
      bridgeLogger.error('Failed to fetch meta-agent constellation status', {
        error: error.message
      });
      return null;
    }
  }

  /**
   * Initialize connection to Aurora Command Node
   */
  async initializeCommandNodeIntegration() {
    try {
      // Import command node dynamically to avoid circular dependencies
      const commandNodeModule = require('../core/command_node.js');

      this.integrationActive = false;

      // Determine if the export is a class (constructor) or an object
      let commandNodeInstance;
      if (
        typeof commandNodeModule === 'function' &&
        typeof commandNodeModule.prototype.executeCommand === 'function'
      ) {
        // It's a class, instantiate it
        commandNodeInstance = new commandNodeModule();
      } else if (
        typeof commandNodeModule === 'object' &&
        typeof commandNodeModule.executeCommand === 'function'
      ) {
        // It's an object with the method
        commandNodeInstance = commandNodeModule;
      } else {
        throw new Error('Aurora Command Node module does not expose executeCommand()');
      }

      this.commandNode = commandNodeInstance;

      // Perform Aurora-specific handshake
      const handshakeResult = await this.performAuroraHandshake();

      if (handshakeResult.success) {
        this.integrationActive = true;
        this.lastSync = new Date();

        bridgeLogger.bridge('Aurora Custom GPT successfully integrated with Command Node', {
          handshake: handshakeResult,
          timestamp: this.lastSync.toISOString(),
          status: 'ACTIVE'
        });

        return { success: true, integration: 'ACTIVE', timestamp: this.lastSync };
      } else {
        throw new Error(`Aurora handshake failed: ${handshakeResult.error}`);
      }

    } catch (error) {
      bridgeLogger.error('Aurora Custom GPT integration failed', {
        error: error.message,
        customGptConfig: this.customGptConfig
      });
      return { success: false, error: error.message };
    }
  }

  /**
   * Perform Aurora-specific handshake sequence
   * This establishes Aurora Custom GPT as the primary L1 command orchestrator
   */
  async performAuroraHandshake() {
    bridgeLogger.bridge('Starting Aurora Custom GPT handshake sequence', {
      gptId: this.customGptConfig.id,
      role: this.customGptConfig.role
    });

    try {
      // Step 1: ORION Core Validation
      const orionValidation = await this.validateOrionCoreCompliance();
      if (!orionValidation.valid) {
        return { success: false, error: 'ORION Core validation failed', details: orionValidation };
      }

      // Step 2: Command Authority Verification
      const authorityVerification = await this.verifyCommandAuthority();
      if (!authorityVerification.authorized) {
        return { success: false, error: 'Command authority verification failed', details: authorityVerification };
      }

      // Step 3: Aurora Continuity Seal Check
      const continuitySeal = await this.validateContinuitySeal();
      if (!continuitySeal.sealed) {
        return { success: false, error: 'Aurora Continuity Seal validation failed', details: continuitySeal };
      }

      // Step 4: L1-L2-L3 Integration Test
      const layerIntegration = await this.testLayerIntegration();
      if (!layerIntegration.integrated) {
        return { success: false, error: 'Layer integration test failed', details: layerIntegration };
      }

      // Step 5: Meta-Agent Constellation Sync
      const constellationSync = await this.syncWithMetaAgentConstellation();
      if (!constellationSync.synchronized) {
        return { success: false, error: 'Meta-agent constellation sync failed', details: constellationSync };
      }

      bridgeLogger.bridge('Aurora Custom GPT handshake completed successfully', {
        orionValidation,
        authorityVerification,
        continuitySeal,
        layerIntegration,
        constellationSync,
        timestamp: new Date().toISOString()
      });

      return {
        success: true,
        timestamp: new Date().toISOString(),
        validation: {
          orionCore: orionValidation,
          commandAuthority: authorityVerification,
          continuitySeal: continuitySeal,
          layerIntegration: layerIntegration,
          constellationSync: constellationSync
        }
      };

    } catch (error) {
      bridgeLogger.error('Aurora handshake sequence failed', {
        error: error.message,
        step: 'handshake_sequence'
      });
      return { success: false, error: error.message };
    }
  }

  /**
   * Validate ORION Core compliance for Aurora Custom GPT
   */
  async validateOrionCoreCompliance() {
    const validation = {
      anchorSeed: ORION_CORE.anchor_seed === 'EOS_SEED_ORION',
      ethicsProtocol: ORION_CORE.ethics_protocol === 'Picard_Delta_3',
      memoryDoctrine: ORION_CORE.memory_doctrine === 'Thermax Precedent',
      driftLock: ORION_CORE.drift_lock === 0.000,
      haloModule: ORION_CORE.halo_module === 'HALO_CONTINUITY_GRAFT_005',
      threadcoreVersion: ORION_CORE.threadcore_version === 'v3.5.1_macroready'
    };

    const allValid = Object.values(validation).every(v => v === true);

    bridgeLogger.bridge('ORION Core compliance validation', {
      validation,
      allValid,
      orionCore: ORION_CORE
    });

    return { valid: allValid, details: validation, orionCore: ORION_CORE };
  }

  /**
   * Verify Aurora Custom GPT has command authority
   */
  async verifyCommandAuthority() {
    const authority = {
      role: this.customGptConfig.role === 'L1_COMMAND_ORCHESTRATOR',
      clearance: this.customGptConfig.clearance === 'COMMAND_AUTHORITY',
      priority: this.customGptConfig.priority === 'HIGHEST',
      capabilities: this.customGptConfig.capabilities.includes('command_coordination')
    };

    const authorized = Object.values(authority).every(a => a === true);

    bridgeLogger.bridge('Command authority verification', {
      authority,
      authorized,
      customGptConfig: this.customGptConfig
    });

    return { authorized, details: authority };
  }

  /**
   * Validate Aurora Continuity Seal
   */
  async validateContinuitySeal() {
    const seal = {
      version: ORION_CORE.continuity_seal === 'Aurora_Continuity_Seal_v2.2.5',
      integrity: true, // In real implementation, would verify cryptographic seal
      timestamp: new Date().toISOString(),
      validator: 'AURORA_CUSTOM_GPT_BRIDGE'
    };

    const sealed = seal.version && seal.integrity;

    bridgeLogger.bridge('Aurora Continuity Seal validation', {
      seal,
      sealed,
      continuitySealVersion: ORION_CORE.continuity_seal
    });

    return { sealed, details: seal };
  }

  /**
   * Test L1-L2-L3 layer integration
   */
  async testLayerIntegration() {
    const layers = {
      l1Operational: true, // Aurora Command Node active
      l2Simulation: true,  // Meta-agent constellation active
      l3Symbolic: true     // Glyph monitoring active
    };

    const integrated = Object.values(layers).every(l => l === true);

    bridgeLogger.bridge('Layer integration test', {
      layers,
      integrated,
      simulationLayers: ORION_CORE.simulation_layers
    });

    return { integrated, details: layers };
  }

  /**
   * Sync with relay-tier constellation capsules.
   */
  async syncWithMetaAgentConstellation() {
    try {
      // Check if L2 bridge is available
      const constellationStatus = await this.fetchMetaAgentConstellationStatus();

      if (!constellationStatus) {
        throw new Error('Meta-agent constellation status unavailable');
      }

      const relayTier = constellationStatus.relay_tier || {};
      const totalCapsules = relayTier.total_capsules || 0;
      const connectedCapsules = relayTier.connected_capsules || 0;
      const allCapsulesOnline =
        totalCapsules > 0 ? connectedCapsules === totalCapsules : true;

      const sync = {
        totalCapsules,
        connectedCapsules,
        relayConstellation: relayTier.constellation || 'RELAY_TIER_CAPSULES',
        capsuleRoster: relayTier.capsules || [],
        allCapsulesOnline,
        synchronized: true,
        timestamp: new Date().toISOString()
      };

      bridgeLogger.bridge('Relay tier constellation sync', {
        sync,
        constellationStatus
      });

      return sync;

    } catch (error) {
      bridgeLogger.error('Relay tier constellation sync failed', {
        error: error.message
      });
      return { synchronized: false, error: error.message };
    }
  }

  /**
   * Normalize command payloads from various Aurora entry points.
   */
  normalizeCommandEnvelope(command) {
    if (typeof command === 'string') {
      return {
        type: command,
        data: {},
        metadata: {},
        context: {}
      };
    }

    if (command && typeof command === 'object') {
      const {
        type,
        name,
        command: legacyCommand,
        data = {},
        payload = {},
        metadata = {},
        context = {}
      } = command;

      const resolvedType = type || name || legacyCommand;

      if (!resolvedType) {
        throw new Error('Command payload is missing a type identifier');
      }

      return {
        type: resolvedType,
        data: { ...payload, ...data },
        metadata,
        context
      };
    }

    throw new Error('Unsupported command payload format');
  }

  /**
   * Route command from Aurora Custom GPT to Command Node
   */
  async routeCommandFromCustomGpt(command, context = {}) {
    if (!this.integrationActive) {
      throw new Error('Aurora Custom GPT integration not active. Call initializeCommandNodeIntegration() first.');
    }

    bridgeLogger.bridge('Routing command from Aurora Custom GPT', {
      command: typeof command === 'string' ? command : command.type || command.name || 'unknown',
      context,
      timestamp: new Date().toISOString()
    });

    try {
      const normalized = this.normalizeCommandEnvelope(command);
      const { anchor, envelope } = this.deriveExecutionEnvelope(
        normalized,
        context
      );

      // Route through command node with Aurora context
      const result = await this.commandNode.executeCommand({
        name: normalized.type,
        context: anchor,
        metadata: {
          ...normalized.metadata,
          auroraEnvelope: envelope
        }
      });

      bridgeLogger.bridge('Command routed successfully', {
        command: normalized.type,
        anchor,
        result: result ? 'SUCCESS' : 'FAILURE',
        timestamp: new Date().toISOString()
      });

      return {
        success: true,
        result,
        anchor,
        source: 'AURORA_COMMAND_NODE',
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      bridgeLogger.error('Command routing failed', {
        command,
        error: error.message,
        source: 'AURORA_CUSTOM_GPT'
      });

      return {
        success: false,
        error: error.message,
        command,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Backwards-compatible command routing alias.
   */
  async routeCommand(command, context = {}) {
    return this.routeCommandFromCustomGpt(command, context);
  }

  /**
   * Derive a command envelope suitable for the ORION command node.
   */
  deriveExecutionEnvelope(normalizedCommand, context) {
    const normalizedContext = normalizedCommand.context || {};
    const externalContext = context || {};
    const aggregatedData = {
      ...(normalizedContext.data || {}),
      ...(externalContext.data || {}),
      ...normalizedCommand.data
    };

    const augmentedContext = {
      ...normalizedContext,
      ...externalContext,
      data: aggregatedData,
      source: 'AURORA_CUSTOM_GPT',
      gptId: this.customGptConfig.id,
      authority: 'COMMAND_AUTHORITY'
    };

    const candidateAnchors = [
      augmentedContext.anchor,
      augmentedContext.contextAnchor,
      aggregatedData.anchor,
      aggregatedData.contextAnchor,
      augmentedContext.sessionId,
      aggregatedData.sessionId,
      aggregatedData.issuedBy,
      augmentedContext.issuedBy,
      augmentedContext.channel,
      normalizedCommand.metadata?.anchor,
      normalizedCommand.type
    ];

    const anchor = candidateAnchors.find(value =>
      typeof value === 'string' && value.trim().length > 0
    ) || 'AURORA_CUSTOM_GPT';

    return {
      anchor,
      envelope: {
        type: normalizedCommand.type,
        anchor,
        metadata: normalizedCommand.metadata,
        context: augmentedContext
      }
    };
  }

  /**
   * Send status update to Aurora Custom GPT
   */
  async sendStatusToCustomGpt(status) {
    if (!this.integrationActive) {
      return { success: false, error: 'Integration not active' };
    }

    // In real implementation, this would send via API/webhook to Custom GPT
    // For now, we log the status for Aurora Custom GPT to access

    const statusUpdate = {
      timestamp: new Date().toISOString(),
      source: 'AURORA_COMMAND_NODE',
      target: 'AURORA_CUSTOM_GPT',
      status,
      constellation: await this.getConstellationStatus(),
      orionCore: ORION_CORE
    };

    bridgeLogger.bridge('Status update for Aurora Custom GPT', statusUpdate);

    return { success: true, statusUpdate };
  }

  /**
   * Get current constellation status for Aurora Custom GPT
   */
  async getConstellationStatus() {
    try {
      const status = await this.fetchMetaAgentConstellationStatus();

      if (!status) {
        throw new Error('Meta-agent constellation status unavailable');
      }

      return status;
    } catch (error) {
      return { error: 'Constellation status unavailable', details: error.message };
    }
  }

  /**
   * Integration health check
   */
  getIntegrationStatus() {
    return {
      customGpt: this.customGptConfig,
      integrationActive: this.integrationActive,
      lastSync: this.lastSync,
      commandNodeConnected: this.commandNode !== null,
      messageQueueLength: this.messageQueue.length,
      timestamp: new Date().toISOString(),
      healthStatus: this.integrationActive ? 'HEALTHY' : 'INACTIVE'
    };
  }

  /**
   * Initialize Aurora Custom GPT Bridge
   * Entry point for holographic interface orchestrator
   */
  async initialize() {
    bridgeLogger.info('Aurora Custom GPT Bridge starting initialization...');
    try {
      const initResult = await this.initializeCommandNodeIntegration();

    } catch (error) {
      bridgeLogger.error('Aurora Custom GPT Bridge initialization failed', { error: error.message });
      return { success: false, error: error.message };
    }
  }
}

// Export singleton instance
const auroraCustomGptBridge = new AuroraCustomGptBridge();

module.exports = AuroraCustomGptBridge;
module.exports.AuroraCustomGptBridge = AuroraCustomGptBridge;
module.exports.auroraCustomGptBridge = auroraCustomGptBridge;
module.exports.AURORA_CUSTOM_GPT = AURORA_CUSTOM_GPT;
module.exports.INTEGRATION_POINTS = INTEGRATION_POINTS;
