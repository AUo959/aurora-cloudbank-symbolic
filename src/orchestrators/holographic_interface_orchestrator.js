/**
 * Aurora CloudBank Holographic Interface Orchestrator
 * Connects the beautiful holographic UI to Aurora Custom GPT bridge
 * Part of Phase 7: Holographic Command Interface deployment
 */

const crypto = require('crypto');
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const { systemLogger } = require('../utils/aurora_logger.js');
const { ORION_CORE } = require('../config/orion_core_config.js');
const AuroraCustomGptBridge = require('../integrations/aurora_custom_gpt_bridge.js');

// Import mesh agent system
const { CollaborationMeshAgent } = require('../core/mesh_agent.js');

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim() !== '';
}

function parseAllowedOrigins(rawValue, port) {
  if (isNonEmptyString(rawValue)) {
    const configuredOrigins = rawValue
      .split(',')
      .map(origin => origin.trim().replace(/\/$/, ''))
      .filter(origin => origin && origin !== '*');

    if (configuredOrigins.length > 0) {
      return configuredOrigins;
    }
  }

  return [
    `http://127.0.0.1:${port}`,
    `http://localhost:${port}`
  ];
}

function isOriginAllowed(origin, allowedOrigins) {
  return !origin || allowedOrigins.includes(origin.replace(/\/$/, ''));
}

function timingSafeEqualString(expected, provided) {
  if (!isNonEmptyString(expected) || !isNonEmptyString(provided)) {
    return false;
  }

  const expectedBuffer = Buffer.from(expected, 'utf8');
  const providedBuffer = Buffer.from(provided, 'utf8');

  if (expectedBuffer.length !== providedBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(expectedBuffer, providedBuffer);
}

function extractBearerToken(headerValue) {
  if (!isNonEmptyString(headerValue)) {
    return '';
  }

  const [scheme, token] = headerValue.split(' ');
  if (scheme !== 'Bearer' || !isNonEmptyString(token)) {
    return '';
  }

  return token.trim();
}

function getAuthorityTokenFromRequest(req) {
  return extractBearerToken(req.get('Authorization')) || (isNonEmptyString(req.get('Aurora-Command-Authority')) ? req.get('Aurora-Command-Authority').trim() : '');
}

function getAuthorityTokenFromSocket(socket) {
  return (
    extractBearerToken(socket.handshake?.headers?.authorization) ||
    (isNonEmptyString(socket.handshake?.headers?.['aurora-command-authority']) ? socket.handshake.headers['aurora-command-authority'].trim() : '') ||
    (isNonEmptyString(socket.handshake?.auth?.token) ? socket.handshake.auth.token.trim() : '')
  );
}

class HolographicInterfaceOrchestrator {
  constructor(port = 8080) {
    this.port = port;
    this.host = process.env.AURORA_HOLOGRAPHIC_HOST || '127.0.0.1';
    this.allowedOrigins = parseAllowedOrigins(process.env.AURORA_HOLOGRAPHIC_ALLOWED_ORIGINS, port);
    this.privilegedCommandsEnabled = process.env.AURORA_ENABLE_HOLOGRAPHIC_COMMANDS === 'true';
    this.authorityToken = (process.env.AURORA_HOLOGRAPHIC_AUTHORITY_TOKEN || '').trim();
    this.app = express();
    this.server = http.createServer(this.app);
    this.io = socketIo(this.server, {
      cors: {
        origin: (origin, callback) => {
          if (isOriginAllowed(origin, this.allowedOrigins)) {
            callback(null, true);
            return;
          }

          callback(new Error('Origin not allowed'));
        },
        methods: ['GET', 'POST'],
        allowedHeaders: ['Authorization', 'Aurora-Command-Authority', 'Content-Type']
      }
    });

    this.logger = systemLogger;
    this.connectedClients = new Set();
    this.commandHistory = [];
    this.auroraCustomGptBridge = null;

    // Collaboration Chamber features
    this.meshSystem = new CollaborationMeshAgent('SYSTEM');
    this.activeAgents = new Map();
    this.commandTraceback = new Map();
    this.liveFeed = [];
    this.collaborationSessions = new Set();

    this.setupMiddleware();
    this.setupRoutes();
    this.setupSocketHandlers();
    this.initializeAuroraBridge();
  }

  setupMiddleware() {
    this.app.use(express.json({ limit: '1mb' }));
    this.app.use(express.static(path.join(__dirname, '../interface')));

    // CORS headers for Aurora Custom GPT integration
    this.app.use((req, res, next) => {
      const origin = req.headers.origin;
      if (origin && !isOriginAllowed(origin, this.allowedOrigins)) {
        res.status(403).json({
          success: false,
          error: 'Origin not allowed'
        });
        return;
      }

      if (origin) {
        res.header('Access-Control-Allow-Origin', origin);
      }

      res.header('Vary', 'Origin');
      res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization, Aurora-Command-Authority');
      if (req.method === 'OPTIONS') {
        res.sendStatus(204);
        return;
      }
      next();
    });
  }

  setupRoutes() {
    // Serve holographic interface
    this.app.get('/', (req, res) => {
      res.sendFile(path.join(__dirname, '../interface/holographic_command_interface.html'));
    });

    // Aurora Custom GPT integration endpoints
    this.app.post('/api/holographic/command', async (req, res) => {
      try {
        if (!this.ensurePrivilegedCommandAccess(req, res)) {
          return;
        }

        const { command, source, authority } = req.body;
        if (!isNonEmptyString(command)) {
          res.status(400).json({
            success: false,
            error: 'Command is required'
          });
          return;
        }

        this.logger.info('Received holographic command', {
          source: source || 'unknown',
          commandLength: command.trim().length
        });

        const result = await this.executeHolographicCommand(command.trim(), source, authority);

        // Broadcast to connected clients
        this.io.emit('command_executed', {
          command,
          result,
          timestamp: new Date().toISOString(),
          source
        });

        res.json({
          success: true,
          result,
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        this.logger.error(`Holographic command error: ${error.message}`);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Real-time system status
    this.app.get('/api/holographic/status', (req, res) => {
      res.json({
        status: 'operational',
        auroraCustomGptBridge: this.auroraCustomGptBridge ? 'connected' : 'disconnected',
        connectedClients: this.connectedClients.size,
        orionCoreVersion: ORION_CORE.version,
        commandHistoryLength: this.commandHistory.length,
        systemHealth: {
          holographicInterface: 'online',
          websocketServer: 'active',
          auroraBridge: this.auroraCustomGptBridge ? 'operational' : 'initializing'
        }
      });
    });

    // Agent constellation status
    this.app.get('/api/holographic/agents', async (req, res) => {
      try {
        if (!this.auroraCustomGptBridge) {
          throw new Error('Aurora Custom GPT Bridge not initialized');
        }

        const agentStatus = await this.getAgentConstellationStatus();

        res.json({
          success: true,
          agents: agentStatus,
          constellationHealth: 'optimal',
          driftLock: 'Δ0.0'
        });

      } catch (error) {
        this.logger.error(`Agent status error: ${error.message}`);
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Serve collaboration chamber interface
    this.app.get('/chamber', (req, res) => {
      res.sendFile(path.join(__dirname, '../interfaces/aurora_collaboration_chamber.html'));
    });

    // Mesh communication endpoint
    this.app.post('/api/mesh/broadcast', async (req, res) => {
      try {
        if (!this.ensurePrivilegedCommandAccess(req, res)) {
          return;
        }

        const { message, authority } = req.body;
        if (!isNonEmptyString(message)) {
          res.status(400).json({
            success: false,
            error: 'Message is required'
          });
          return;
        }

        const result = await this.broadcastToMesh(message.trim(), authority);

        res.json({
          success: true,
          messageId: result.messageId,
          timestamp: result.timestamp,
          recipients: result.recipients
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Direct agent communication endpoint
    this.app.post('/api/agent/:agentId/message', async (req, res) => {
      try {
        if (!this.ensurePrivilegedCommandAccess(req, res)) {
          return;
        }

        const { agentId } = req.params;
        const { message, authority } = req.body;
        if (!isNonEmptyString(message)) {
          res.status(400).json({
            success: false,
            error: 'Message is required'
          });
          return;
        }

        const result = await this.sendDirectMessage(agentId, message.trim(), authority);

        res.json({
          success: true,
          messageId: result.messageId,
          timestamp: result.timestamp,
          agent: agentId,
          response: result.response
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Live feed endpoint
    this.app.get('/api/chamber/feed', (req, res) => {
      res.json({
        success: true,
        feed: this.liveFeed.slice(-50), // Last 50 messages
        connectedClients: this.connectedClients.size,
        activeSessions: this.collaborationSessions.size
      });
    });

    // Command traceback endpoint
    this.app.get('/api/chamber/traceback/:commandId', (req, res) => {
      const { commandId } = req.params;
      const traceback = this.commandTraceback.get(commandId);

      if (traceback) {
        res.json({
          success: true,
          traceback
        });
      } else {
        res.status(404).json({
          success: false,
          error: 'Command traceback not found'
        });
      }
    });
  }

  setupSocketHandlers() {
    this.io.on('connection', (socket) => {
      this.connectedClients.add(socket.id);
      this.collaborationSessions.add(socket.id);
      this.logger.info(`Collaboration Chamber client connected: ${socket.id}`);

      // Send initial system status and recent feed
      socket.emit('system_status', {
        auroraVersion: ORION_CORE.version,
        customGptConnected: !!this.auroraCustomGptBridge,
        agentsOnline: this.activeAgents.size,
        driftLock: 'Δ0.0',
        meshStatus: 'ACTIVE',
        chamberMode: 'OPERATIONAL'
      });

      // Send recent live feed
      socket.emit('live_feed_history', this.liveFeed.slice(-20));

      // Handle real-time commands with enhanced traceback
      socket.on('execute_command', async (data) => {
        try {
          if (!this.ensurePrivilegedSocketAccess(socket, 'command_result')) {
            return;
          }

          const { command, authority, target = '' } = data || {};
          if (!isNonEmptyString(command)) {
            socket.emit('command_result', {
              success: false,
              error: 'Command is required',
              timestamp: new Date().toISOString()
            });
            return;
          }

          const commandId = `ws-${Date.now()}-${socket.id}`;

          this.addCommandTraceback(commandId, command.trim(), '/ws/execute_command', {
            socketId: socket.id,
            target,
            authority
          });

          let result;

          // Route command based on target
          if (target === '@mesh' || (isNonEmptyString(target) && target.startsWith('{{@mesh'))) {
            this.addTracebackStep(commandId, 'Routing to mesh broadcast system');
            result = await this.broadcastToMesh(command.trim(), authority);
          } else if (isNonEmptyString(target) && (target.startsWith('@agent.') || target.startsWith('{{@agent.'))) {
            const agentId = target.replace('@agent.', '').replace('{{@agent.', '').split(' ')[0];
            this.addTracebackStep(commandId, `Routing to direct agent communication: ${agentId}`);
            result = await this.sendDirectMessage(agentId, command.trim(), authority);
          } else {
            // Default routing through Aurora bridge
            this.addTracebackStep(commandId, 'Routing to Aurora Custom GPT Bridge');
            result = await this.executeHolographicCommand(command.trim(), 'collaboration_chamber', authority);
          }

          socket.emit('command_result', {
            success: true,
            result,
            commandId,
            timestamp: new Date().toISOString()
          });

          // Broadcast to all chamber clients
          this.io.emit('command_executed', {
            command,
            result,
            commandId,
            timestamp: new Date().toISOString(),
            source: 'collaboration_chamber',
            authority
          });

          this.addTracebackStep(commandId, 'Command execution completed successfully', result);

        } catch (error) {
          const errorResult = {
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
          };

          socket.emit('command_result', errorResult);

          if (data && data.commandId) {
            this.addTracebackStep(data.commandId, 'Command execution failed', null, error.message);
          }
        }
      });

      // Handle agent selection with enhanced feedback
      socket.on('select_agent', (agentName) => {
        this.logger.info(`Agent selected by ${socket.id}: ${agentName}`);

        const agent = this.activeAgents.get(agentName);
        const capabilities = agent ? this.getAgentCapabilities(agentName) : ['Agent not available'];

        socket.emit('agent_selected', {
          agent: agentName,
          status: agent ? 'active' : 'unavailable',
          capabilities,
          driftLock: 'Δ0.0'
        });

        // Add to live feed
        this.addToLiveFeed('SYSTEM', `Agent ${agentName} selected by user`, 'system', {
          socketId: socket.id,
          agentStatus: agent ? 'active' : 'unavailable'
        });
      });

      // Handle mesh broadcast requests
      socket.on('mesh_broadcast', async (data) => {
        try {
          if (!this.ensurePrivilegedSocketAccess(socket, 'mesh_broadcast_result')) {
            return;
          }

          const { message, authority } = data || {};
          if (!isNonEmptyString(message)) {
            socket.emit('mesh_broadcast_result', {
              success: false,
              error: 'Message is required'
            });
            return;
          }

          const result = await this.broadcastToMesh(message.trim(), authority || 'user');

          socket.emit('mesh_broadcast_result', {
            success: true,
            result
          });
        } catch (error) {
          socket.emit('mesh_broadcast_result', {
            success: false,
            error: error.message
          });
        }
      });

      // Handle direct agent messages
      socket.on('direct_message', async (data) => {
        try {
          if (!this.ensurePrivilegedSocketAccess(socket, 'direct_message_result')) {
            return;
          }

          const { agentId, message, authority } = data || {};
          if (!isNonEmptyString(agentId) || !isNonEmptyString(message)) {
            socket.emit('direct_message_result', {
              success: false,
              error: 'Agent ID and message are required'
            });
            return;
          }

          const result = await this.sendDirectMessage(agentId, message.trim(), authority || 'user');

          socket.emit('direct_message_result', {
            success: true,
            result
          });
        } catch (error) {
          socket.emit('direct_message_result', {
            success: false,
            error: error.message
          });
        }
      });

      // Handle traceback requests
      socket.on('get_traceback', (commandId) => {
        const traceback = this.commandTraceback.get(commandId);
        socket.emit('traceback_data', {
          commandId,
          traceback: traceback || null
        });
      });

      socket.on('disconnect', () => {
        this.connectedClients.delete(socket.id);
        this.collaborationSessions.delete(socket.id);
        this.logger.info(`Collaboration Chamber client disconnected: ${socket.id}`);

        // Notify remaining clients
        this.io.emit('client_disconnected', {
          socketId: socket.id,
          connectedClients: this.connectedClients.size
        });
      });
    });
  }

  async initializeAuroraBridge() {
    try {
      this.auroraCustomGptBridge = new AuroraCustomGptBridge();
      await this.auroraCustomGptBridge.initialize();

      this.logger.info('Aurora Custom GPT Bridge initialized for holographic interface');

      // Notify connected clients
      this.io.emit('bridge_status', {
        status: 'connected',
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      this.logger.error(`Failed to initialize Aurora Bridge: ${error.message}`);
    }
  }

  async initialize() {
    try {
      await this.initializeAuroraBridge();
      await this.initializeMeshSystem();
      await this.initializeCollaborationChamber();
    } catch (error) {
      this.logger.error(`Initialization error: ${error.message}`);
    }
  }

  async initializeMeshSystem() {
    try {
      // Initialize mesh federation
      await this.meshSystem.initializeFederation();

      // Setup agent constellation
      const agents = ['ARCHY', 'OPPY', 'LIORA', 'STARLING_AU', 'RIVERTHREAD_808'];
      for (const agentId of agents) {
        const agent = await this.meshSystem.activateAgent(agentId);
        this.activeAgents.set(agentId, agent);
        this.logger.info(`Activated agent: ${agentId}`);
      }

      this.logger.info('🕸️ Mesh system initialized with all agents active');
    } catch (error) {
      this.logger.error(`Mesh system initialization error: ${error.message}`);
      throw error;
    }
  }

  async initializeCollaborationChamber() {
    try {
      // Setup collaboration chamber routes
      this.setupCollaborationRoutes();

      // Initialize live feed system
      this.setupLiveFeedSystem();

      // Setup command traceback system
      this.setupCommandTracebackSystem();

      this.logger.info('🏛️ Collaboration Chamber initialized');
    } catch (error) {
      this.logger.error(`Collaboration Chamber initialization error: ${error.message}`);
      throw error;
    }
  }

  ensurePrivilegedCommandAccess(req, res) {
    if (!this.privilegedCommandsEnabled) {
      res.status(503).json({
        success: false,
        error: 'Privileged holographic commands are disabled'
      });
      return false;
    }

    if (!isNonEmptyString(this.authorityToken)) {
      res.status(503).json({
        success: false,
        error: 'Holographic authority token is not configured'
      });
      return false;
    }

    const providedToken = getAuthorityTokenFromRequest(req);
    if (!timingSafeEqualString(this.authorityToken, providedToken)) {
      res.status(401).json({
        success: false,
        error: isNonEmptyString(providedToken) ? 'Invalid authority token' : 'Missing authority token'
      });
      return false;
    }

    return true;
  }

  ensurePrivilegedSocketAccess(socket, failureEvent) {
    if (!this.privilegedCommandsEnabled) {
      socket.emit(failureEvent, {
        success: false,
        error: 'Privileged holographic commands are disabled',
        timestamp: new Date().toISOString()
      });
      return false;
    }

    if (!isNonEmptyString(this.authorityToken)) {
      socket.emit(failureEvent, {
        success: false,
        error: 'Holographic authority token is not configured',
        timestamp: new Date().toISOString()
      });
      return false;
    }

    const providedToken = getAuthorityTokenFromSocket(socket);
    if (!timingSafeEqualString(this.authorityToken, providedToken)) {
      socket.emit(failureEvent, {
        success: false,
        error: isNonEmptyString(providedToken) ? 'Invalid authority token' : 'Missing authority token',
        timestamp: new Date().toISOString()
      });
      return false;
    }

    return true;
  }

  async executeHolographicCommand(command, source, authority) {
    // Add to command history
    const commandEntry = {
      command,
      source,
      authority,
      timestamp: new Date().toISOString(),
      id: `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };

    this.commandHistory.push(commandEntry);

    // Keep only last 100 commands
    if (this.commandHistory.length > 100) {
      this.commandHistory.shift();
    }

    // Execute through Aurora Custom GPT Bridge if available
    if (this.auroraCustomGptBridge) {
      try {
        const bridgeResult = await this.auroraCustomGptBridge.routeCommand({
          command,
          source: 'holographic_interface',
          authority,
          sessionId: `holographic_${Date.now()}`
        });

        return {
          status: 'success',
          result: bridgeResult,
          via: 'aurora_custom_gpt_bridge',
          commandId: commandEntry.id
        };

      } catch (error) {
        this.logger.error(`Bridge command execution failed: ${error.message}`);
        return {
          status: 'error',
          error: error.message,
          fallback: 'holographic_simulation',
          commandId: commandEntry.id
        };
      }
    }

    // Fallback holographic simulation
    return this.simulateCommandExecution(command, commandEntry.id);
  }

  simulateCommandExecution(command, commandId) {
    const responses = {
      'aurora.initialize()': 'Aurora CloudBank v3.5.1 initialized successfully',
      'meta_agents.constellation.status()': '5/5 agents online with Δ0.0 drift-lock',
      'custom_gpt.bridge.validate()': 'Aurora Custom GPT bridge connection validated',
      'system.health.check()': 'All systems operational - holographic interface active',
      'agents.synchronize()': 'Agent constellation synchronized - ZIPWIZ protocol active'
    };

    const response = responses[command] || `Command '${command}' processed by holographic simulation`;

    return {
      status: 'simulated',
      result: response,
      via: 'holographic_simulation',
      commandId
    };
  }

  async getAgentConstellationStatus() {
    const agents = [
      { name: 'ARCHY', status: 'active', drift: 0.0, specialization: 'Architecture & System Design' },
      { name: 'OPPY', status: 'active', drift: 0.0, specialization: 'Optimization & Performance' },
      { name: 'LIORA', status: 'active', drift: 0.0, specialization: 'Learning & Adaptation' },
      { name: 'STARLING_AU', status: 'active', drift: 0.0, specialization: 'Stellar Communication' },
      { name: 'RIVERTHREAD_808', status: 'active', drift: 0.0, specialization: 'Data Flow & Threading' }
    ];

    return agents;
  }

  getAgentCapabilities(agentName) {
    const capabilities = {
      ARCHY: ['System Architecture', 'Design Patterns', 'Code Structure'],
      OPPY: ['Performance Optimization', 'Resource Management', 'Efficiency Analysis'],
      LIORA: ['Machine Learning', 'Adaptive Algorithms', 'Pattern Recognition'],
      STARLING_AU: ['Communication Protocols', 'Network Architecture', 'Signal Processing'],
      RIVERTHREAD_808: ['Data Streaming', 'Parallel Processing', 'Pipeline Management']
    };

    return capabilities[agentName] || ['General AI Capabilities'];
  }

  setupCollaborationRoutes() {
    // Serve collaboration chamber interface
    this.app.get('/chamber', (req, res) => {
      res.sendFile(path.join(__dirname, '../interfaces/aurora_collaboration_chamber.html'));
    });

    // Mesh communication endpoint
    this.app.post('/api/mesh/broadcast', async (req, res) => {
      try {
        if (!this.ensurePrivilegedCommandAccess(req, res)) {
          return;
        }

        const { message, authority } = req.body;
        if (!isNonEmptyString(message)) {
          res.status(400).json({
            success: false,
            error: 'Message is required'
          });
          return;
        }

        const result = await this.broadcastToMesh(message.trim(), authority);

        res.json({
          success: true,
          messageId: result.messageId,
          timestamp: result.timestamp,
          recipients: result.recipients
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Direct agent communication endpoint
    this.app.post('/api/agent/:agentId/message', async (req, res) => {
      try {
        if (!this.ensurePrivilegedCommandAccess(req, res)) {
          return;
        }

        const { agentId } = req.params;
        const { message, authority } = req.body;
        if (!isNonEmptyString(message)) {
          res.status(400).json({
            success: false,
            error: 'Message is required'
          });
          return;
        }

        const result = await this.sendDirectMessage(agentId, message.trim(), authority);

        res.json({
          success: true,
          messageId: result.messageId,
          timestamp: result.timestamp,
          agent: agentId,
          response: result.response
        });
      } catch (error) {
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Live feed endpoint
    this.app.get('/api/chamber/feed', (req, res) => {
      res.json({
        success: true,
        feed: this.liveFeed.slice(-50), // Last 50 messages
        connectedClients: this.connectedClients.size,
        activeSessions: this.collaborationSessions.size
      });
    });

    // Command traceback endpoint
    this.app.get('/api/chamber/traceback/:commandId', (req, res) => {
      const { commandId } = req.params;
      const traceback = this.commandTraceback.get(commandId);

      if (traceback) {
        res.json({
          success: true,
          traceback
        });
      } else {
        res.status(404).json({
          success: false,
          error: 'Command traceback not found'
        });
      }
    });
  }

  setupLiveFeedSystem() {
    // Live feed message structure
    this.addToLiveFeed = (sender, content, type, metadata = {}) => {
      const message = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        sender,
        content,
        type, // 'mesh', 'agent', 'system', 'user'
        timestamp: new Date().toISOString(),
        metadata
      };

      this.liveFeed.push(message);

      // Keep only last 1000 messages
      if (this.liveFeed.length > 1000) {
        this.liveFeed = this.liveFeed.slice(-1000);
      }

      // Broadcast to all connected clients
      this.io.emit('live_feed_update', message);

      return message;
    };
  }

  setupCommandTracebackSystem() {
    this.addCommandTraceback = (commandId, command, path, metadata = {}) => {
      const traceback = {
        commandId,
        command,
        path,
        timestamp: new Date().toISOString(),
        metadata,
        steps: []
      };

      this.commandTraceback.set(commandId, traceback);

      // Cleanup old tracebacks (keep last 500)
      if (this.commandTraceback.size > 500) {
        const oldestKey = this.commandTraceback.keys().next().value;
        this.commandTraceback.delete(oldestKey);
      }

      return traceback;
    };

    this.addTracebackStep = (commandId, step, result = null, error = null) => {
      const traceback = this.commandTraceback.get(commandId);
      if (traceback) {
        traceback.steps.push({
          step,
          result,
          error,
          timestamp: new Date().toISOString()
        });

        // Broadcast traceback update
        this.io.emit('traceback_update', {
          commandId,
          step: traceback.steps[traceback.steps.length - 1]
        });
      }
    };
  }

  async broadcastToMesh(message, authority = 'system') {
    const commandId = `mesh-${Date.now()}`;
    this.addCommandTraceback(commandId, message, '/api/mesh/broadcast');

    try {
      this.addTracebackStep(commandId, 'Formatting mesh broadcast message');

      // Format message for mesh broadcast
      const meshMessage = `{{@mesh ::: ${message}}}`;

      this.addTracebackStep(commandId, 'Broadcasting to all agents in constellation');

      // Send to all active agents
      const recipients = [];
      const responses = new Map();

      for (const [agentId, agent] of this.activeAgents) {
        try {
          const response = await agent.receiveMessage(meshMessage, authority);
          recipients.push(agentId);
          responses.set(agentId, response);

          this.addTracebackStep(commandId, `Agent ${agentId} received message`, response);
        } catch (error) {
          this.addTracebackStep(commandId, `Agent ${agentId} error`, null, error.message);
        }
      }

      // Add to live feed
      this.addToLiveFeed('MESH', message, 'mesh', {
        commandId,
        recipients,
        authority
      });

      const result = {
        messageId: commandId,
        timestamp: new Date().toISOString(),
        recipients,
        responses: Object.fromEntries(responses)
      };

      this.addTracebackStep(commandId, 'Mesh broadcast completed', result);

      return result;
    } catch (error) {
      this.addTracebackStep(commandId, 'Mesh broadcast failed', null, error.message);
      throw error;
    }
  }

  async sendDirectMessage(agentId, message, authority = 'user') {
    const commandId = `direct-${agentId}-${Date.now()}`;
    this.addCommandTraceback(commandId, message, `/api/agent/${agentId}/message`);

    try {
      this.addTracebackStep(commandId, `Formatting direct message to ${agentId}`);

      // Format message for direct agent communication
      const directMessage = `{{@agent.${agentId} ::: ${message}}}`;

      this.addTracebackStep(commandId, `Sending message to agent ${agentId}`);

      const agent = this.activeAgents.get(agentId);
      if (!agent) {
        throw new Error(`Agent ${agentId} not found or not active`);
      }

      const response = await agent.receiveMessage(directMessage, authority);

      this.addTracebackStep(commandId, `Agent ${agentId} responded`, response);

      // Add to live feed
      this.addToLiveFeed(agentId, message, 'agent', {
        commandId,
        authority,
        direct: true
      });

      const result = {
        messageId: commandId,
        timestamp: new Date().toISOString(),
        agent: agentId,
        response
      };

      this.addTracebackStep(commandId, 'Direct message completed', result);

      return result;
    } catch (error) {
      this.addTracebackStep(commandId, 'Direct message failed', null, error.message);
      throw error;
    }
  }

  start() {
    this.server.listen(this.port, this.host, () => {
      this.logger.info(`🌟 Aurora CloudBank Holographic Command Interface started on ${this.host}:${this.port}`);
      this.logger.info(`✨ Access the interface at: http://localhost:${this.port}`);
      if (!this.privilegedCommandsEnabled) {
        this.logger.info('🔒 Privileged holographic commands are disabled until AURORA_ENABLE_HOLOGRAPHIC_COMMANDS=true');
      } else if (!isNonEmptyString(this.authorityToken)) {
        this.logger.info('🔒 Privileged holographic commands require AURORA_HOLOGRAPHIC_AUTHORITY_TOKEN');
      }
      this.logger.info('🎯 PHASE 7: HOLOGRAPHIC COMMAND INTERFACE - OPERATIONAL');
    });
  }

  getStatus() {
    return {
      port: this.port,
      connectedClients: this.connectedClients.size,
      auroraCustomGptBridge: !!this.auroraCustomGptBridge,
      commandHistoryLength: this.commandHistory.length,
      uptime: process.uptime()
    };
  }
}

module.exports = HolographicInterfaceOrchestrator;

// Auto-start if run directly
if (require.main === module) {
  const orchestrator = new HolographicInterfaceOrchestrator();
  orchestrator.start();
}
