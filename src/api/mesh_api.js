/**
 * Mesh API Integration for Aurora CloudBank
 * Provides RESTful endpoints for mesh agent communication and management
 */

const express = require('express');
const crypto = require('crypto');
const { MESH_CONFIG, MeshFederation } = require('../core/mesh_agent.js');
const { systemLogger, bridgeLogger } = require('../utils/aurora_logger.js');

const router = express.Router();

// Global mesh federation instance
let meshFederation = null;

/**
 * Initialize mesh federation
 */
async function initializeMeshFederation() {
  if (!meshFederation) {
    meshFederation = new MeshFederation();
    await meshFederation.initializeMesh();

    systemLogger.info('🕸️ [MESH_API] Mesh federation initialized', {
      status: meshFederation.status,
      agentCount: meshFederation.agents.size
    });
  }
  return meshFederation;
}

/**
 * GET /api/mesh/status
 * Get overall mesh status and agent constellation
 */
router.get('/status', async (req, res) => {
  try {
    await initializeMeshFederation();
    const status = meshFederation.getStatus();

    systemLogger.info('📊 [MESH_API] Status requested', {
      meshStatus: status.meshStatus,
      agentCount: status.agentCount
    });

    res.json({
      success: true,
      timestamp: Date.now(),
      mesh: status,
      endpoints: MESH_CONFIG.relayApiEndpoints
    });
  } catch (error) {
    systemLogger.error('❌ [MESH_API] Status request failed', {
      error: error.message
    });

    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

/**
 * POST /api/mesh/message
 * Send message through mesh (direct or broadcast)
 */
router.post('/message', async (req, res) => {
  try {
    await initializeMeshFederation();
    const { from, to, content, type = 'direct' } = req.body;

    if (!from || !content) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: from, content',
        timestamp: Date.now()
      });
    }

    const agent = meshFederation.agents.get(from);
    if (!agent) {
      return res.status(404).json({
        success: false,
        error: `Agent ${from} not found in constellation`,
        timestamp: Date.now()
      });
    }

    let message;
    if (type === 'broadcast') {
      message = await agent.broadcastMessage(content);
    } else {
      if (!to) {
        return res.status(400).json({
          success: false,
          error: 'Direct messages require "to" field',
          timestamp: Date.now()
        });
      }
      message = await agent.sendMessage(to, content);
    }

    bridgeLogger.bridge('📨 [MESH_API] Message sent through mesh', {
      from: from,
      to: to || 'BROADCAST',
      type: type,
      messageId: message.timestamp
    });

    res.json({
      success: true,
      message: message,
      timestamp: Date.now()
    });

  } catch (error) {
    systemLogger.error('❌ [MESH_API] Message send failed', {
      error: error.message,
      body: req.body
    });

    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

/**
 * POST /api/mesh/arbitration
 * Initiate arbitration process
 */
router.post('/arbitration', async (req, res) => {
  try {
    await initializeMeshFederation();
    const { initiator, description } = req.body;

    if (!initiator || !description) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: initiator, description',
        timestamp: Date.now()
      });
    }

    const agent = meshFederation.agents.get(initiator);
    if (!agent) {
      return res.status(404).json({
        success: false,
        error: `Agent ${initiator} not found in constellation`,
        timestamp: Date.now()
      });
    }

    const arbitration = await agent.initiateArbitration(description);

    systemLogger.info('⚖️ [MESH_API] Arbitration initiated', {
      initiator: initiator,
      description: description,
      arbitrationId: arbitration.timestamp
    });

    res.json({
      success: true,
      arbitration: arbitration,
      timestamp: Date.now()
    });

  } catch (error) {
    systemLogger.error('❌ [MESH_API] Arbitration initiation failed', {
      error: error.message,
      body: req.body
    });

    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

/**
 * GET /api/mesh/agents/:agentId
 * Get specific agent status and information
 */
router.get('/agents/:agentId', async (req, res) => {
  try {
    await initializeMeshFederation();
    const { agentId } = req.params;

    const agent = meshFederation.agents.get(agentId);
    if (!agent) {
      return res.status(404).json({
        success: false,
        error: `Agent ${agentId} not found in constellation`,
        timestamp: Date.now()
      });
    }

    const agentInfo = {
      id: agent.id,
      role: agent.role,
      status: agent.status,
      ethicsStatus: agent.ethicsStatus,
      driftLevel: agent.driftLevel,
      lastSync: agent.lastSync,
      meshConnected: agent.meshConnected,
      apiEndpoint: agent.apiEndpoint,
      sessionId: agent.sessionId
    };

    systemLogger.info(`🔍 [MESH_API] Agent info requested for ${agentId}`, {
      status: agent.status,
      role: agent.role
    });

    res.json({
      success: true,
      agent: agentInfo,
      timestamp: Date.now()
    });

  } catch (error) {
    systemLogger.error('❌ [MESH_API] Agent info request failed', {
      error: error.message,
      agentId: req.params.agentId
    });

    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

/**
 * POST /api/mesh/agents/:agentId/activate
 * Activate specific agent using activation phrase
 */
router.post('/agents/:agentId/activate', async (req, res) => {
  try {
    await initializeMeshFederation();
    const { agentId } = req.params;
    const { activationPhrase } = req.body;

    const agent = meshFederation.agents.get(agentId);
    if (!agent) {
      return res.status(404).json({
        success: false,
        error: `Agent ${agentId} not found in constellation`,
        timestamp: Date.now()
      });
    }

    const expectedPhrase = MESH_CONFIG.activationPhrases[agentId];
    if (activationPhrase !== expectedPhrase) {
      return res.status(401).json({
        success: false,
        error: 'Invalid activation phrase',
        timestamp: Date.now()
      });
    }

    // Re-run handshake if needed
    if (agent.status !== 'LIVE') {
      await agent.handshake();
    }

    const activationDigest = crypto
      .createHash('sha256')
      .update(expectedPhrase)
      .digest('hex');

    bridgeLogger.bridge(`🚀 [MESH_API] Agent ${agentId} activated`, {
      agentId: agentId,
      status: agent.status,
      activationVerification: {
        method: 'sha256',
        digest: activationDigest
      }
    });

    res.json({
      success: true,
      agent: {
        id: agent.id,
        status: agent.status,
        activated: true
      },
      timestamp: Date.now()
    });

  } catch (error) {
    systemLogger.error('❌ [MESH_API] Agent activation failed', {
      error: error.message,
      agentId: req.params.agentId
    });

    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

/**
 * GET /api/mesh/config
 * Get mesh configuration and protocols
 */
router.get('/config', (req, res) => {
  try {
    systemLogger.info('⚙️ [MESH_API] Configuration requested');

    res.json({
      success: true,
      config: {
        version: MESH_CONFIG.version,
        anchorSeed: MESH_CONFIG.anchorSeed,
        ethicsProtocol: MESH_CONFIG.ethicsProtocol,
        constellation: MESH_CONFIG.constellation,
        commProtocol: MESH_CONFIG.commProtocol,
        endpoints: MESH_CONFIG.relayApiEndpoints,
        activationPhrases: Object.keys(MESH_CONFIG.activationPhrases)
      },
      timestamp: Date.now()
    });

  } catch (error) {
    systemLogger.error('❌ [MESH_API] Configuration request failed', {
      error: error.message
    });

    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

module.exports = {
  router,
  initializeMeshFederation,
  MESH_CONFIG
};
