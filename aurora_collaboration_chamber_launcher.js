#!/usr/bin/env node

/**
 * Aurora Collaboration Chamber Launcher
 * Enhanced Aurora CloudBank holographic interface with @mesh system integration
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

const PROJECT_ROOT = __dirname;
const PORT = Number.parseInt(process.env.AURORA_CHAMBER_PORT || '8080', 10);
const HOST = process.env.AURORA_CHAMBER_HOST || '127.0.0.1';
const ENABLE_SYSTEM_COMMANDS = process.env.AURORA_ENABLE_CHAMBER_COMMANDS === '1';
const ENABLE_CONTEXT_TRANSFER = process.env.AURORA_ENABLE_CONTEXT_TRANSFER === '1';

function parseListEnv(value, fallback) {
  if (!value || !value.trim()) {
    return fallback;
  }

  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizeOrigin(origin) {
  return origin.replace(/\/+$/, '');
}

const ALLOWED_ORIGINS = new Set(
  parseListEnv(process.env.AURORA_CHAMBER_ALLOWED_ORIGINS, [
    `http://${HOST}:${PORT}`,
    `http://127.0.0.1:${PORT}`,
    `http://localhost:${PORT}`
  ]).map(normalizeOrigin)
);

const ALLOWED_CONTEXT_ROOTS = parseListEnv(process.env.AURORA_CONTEXT_TRANSFER_ROOTS, [
  path.join(PROJECT_ROOT, 'docs'),
  path.join(PROJECT_ROOT, 'src'),
  path.join(PROJECT_ROOT, 'static'),
  path.join(PROJECT_ROOT, 'tests')
]).map((root) => path.resolve(root));

const SAFE_SYSTEM_COMMANDS = {
  'git status': {
    command: 'git',
    args: ['status']
  },
  'npm run lint': {
    command: 'npm',
    args: ['run', 'lint']
  },
  'npm run time-to-clean-up': {
    command: 'npm',
    args: ['run', 'time-to-clean-up']
  },
  'npm run validation:cleanup': {
    command: 'npm',
    args: ['run', 'validation:cleanup']
  },
  'npm run validation:status': {
    command: 'npm',
    args: ['run', 'validation:status']
  },
  'ps aux | grep aurora': {
    command: 'ps',
    args: ['aux'],
    transformOutput: (stdout) =>
      stdout
        .split('\n')
        .filter((line) => /aurora/i.test(line))
        .join('\n')
  },
  'python scripts/aurora_validation_manager.py --cleanup': {
    command: 'python3',
    args: ['scripts/aurora_validation_manager.py', '--cleanup']
  },
  'python scripts/aurora_validation_manager.py --status': {
    command: 'python3',
    args: ['scripts/aurora_validation_manager.py', '--status']
  },
  'python scripts/canonical_validator.py --status': {
    command: 'python3',
    args: ['scripts/canonical_validator.py', '--status']
  }
};

function isAllowedOrigin(origin) {
  if (!origin) {
    return true;
  }
  return ALLOWED_ORIGINS.has(normalizeOrigin(origin));
}

function buildRejectedCommandResult(command, processId, reason) {
  return {
    processId,
    command,
    timestamp: new Date().toISOString(),
    success: false,
    stdout: '',
    stderr: '',
    exitCode: 1,
    error: reason
  };
}

function resolveContextPath(filePath) {
  if (!ENABLE_CONTEXT_TRANSFER) {
    throw new Error(
      'Context transfer is disabled by default. Set AURORA_ENABLE_CONTEXT_TRANSFER=1 to enable it explicitly.'
    );
  }

  if (typeof filePath !== 'string' || !filePath.trim()) {
    throw new Error('Context transfer requires a non-empty relative file path.');
  }

  if (path.isAbsolute(filePath)) {
    throw new Error('Absolute paths are not allowed for context transfer.');
  }

  const resolvedPath = path.resolve(PROJECT_ROOT, filePath);
  const withinAllowedRoot = ALLOWED_CONTEXT_ROOTS.some(
    (root) => resolvedPath === root || resolvedPath.startsWith(`${root}${path.sep}`)
  );

  if (!withinAllowedRoot) {
    throw new Error('Requested file is outside the allowed context roots.');
  }

  return resolvedPath;
}

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: (origin, callback) => {
      if (isAllowedOrigin(origin)) {
        callback(null, true);
        return;
      }
      callback(new Error('Origin not allowed by Aurora chamber policy.'));
    },
    methods: ['GET', 'POST']
  }
});

// Collaboration Chamber state
const chamberState = {
  connectedClients: new Set(),
  activeAgents: new Map([
    ['ARCHY', { status: 'active', specialization: 'Architecture & System Design' }],
    ['OPPY', { status: 'active', specialization: 'Optimization & Performance' }],
    ['LIORA', { status: 'active', specialization: 'Learning & Adaptation' }],
    ['STARLING_AU', { status: 'active', specialization: 'Stellar Communication' }],
    ['RIVERTHREAD_808', { status: 'active', specialization: 'Data Flow & Threading' }]
  ]),
  liveFeed: [],
  commandTraceback: new Map(),
  commandCounter: 1
};

// Static file serving
app.use(express.static(path.join(__dirname, 'src/interfaces')));
app.use(express.json());
app.use((req, res, next) => {
  const origin = req.headers.origin;

  if (origin && !isAllowedOrigin(origin)) {
    res.status(403).json({ success: false, error: 'Origin not allowed by Aurora chamber policy.' });
    return;
  }

  if (origin) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin');
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.sendStatus(204);
    return;
  }

  next();
});

// Routes
app.get('/', (req, res) => {
  res.redirect('/chamber');
});

app.get('/chamber', (req, res) => {
  res.sendFile(path.join(__dirname, 'src/interfaces/aurora_collaboration_chamber.html'));
});

app.get('/api/chamber/status', (req, res) => {
  res.json({
    success: true,
    status: 'operational',
    connectedClients: chamberState.connectedClients.size,
    activeAgents: Array.from(chamberState.activeAgents.keys()),
    meshStatus: 'ACTIVE',
    driftLock: 'Δ0.0',
    phase: 'PHASE 7 - OPERATIONAL'
  });
});

app.get('/api/chamber/agents', (req, res) => {
  const agents = Array.from(chamberState.activeAgents.entries()).map(([id, info]) => ({
    id,
    status: info.status,
    specialization: info.specialization,
    driftLock: 'Δ0.0'
  }));

  res.json({
    success: true,
    agents,
    constellationHealth: 'optimal'
  });
});

// Utility functions
function addToLiveFeed(sender, content, type, metadata = {}) {
  const message = {
    id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    sender,
    content,
    type,
    timestamp: new Date().toISOString(),
    metadata
  };

  chamberState.liveFeed.push(message);
  if (chamberState.liveFeed.length > 1000) {
    chamberState.liveFeed = chamberState.liveFeed.slice(-1000);
  }

  io.emit('live_feed_update', message);
  return message;
}

function addCommandTraceback(commandId, command, path, metadata = {}) {
  const traceback = {
    commandId,
    command,
    path,
    timestamp: new Date().toISOString(),
    metadata,
    steps: []
  };

  chamberState.commandTraceback.set(commandId, traceback);
  if (chamberState.commandTraceback.size > 500) {
    const oldestKey = chamberState.commandTraceback.keys().next().value;
    chamberState.commandTraceback.delete(oldestKey);
  }

  return traceback;
}

function addTracebackStep(commandId, step, result = null, error = null) {
  const traceback = chamberState.commandTraceback.get(commandId);
  if (traceback) {
    traceback.steps.push({
      step,
      result,
      error,
      timestamp: new Date().toISOString()
    });

    io.emit('traceback_update', {
      commandId,
      step: traceback.steps[traceback.steps.length - 1]
    });
  }
}

function processAgentMessage(agentId, message, messageType) {
  const agent = chamberState.activeAgents.get(agentId);
  if (!agent) {
    return { success: false, error: `Agent ${agentId} not found` };
  }

  const specializations = {
    ARCHY: 'Analyzing from architecture perspective',
    OPPY: 'Performance analysis and optimization',
    LIORA: 'Learning pattern identification',
    STARLING_AU: 'Communication protocol assessment',
    RIVERTHREAD_808: 'Data flow analysis'
  };

  const responsePrefix = specializations[agentId] || 'Processing';
  const response = `[${agentId}] ${responsePrefix}: ${message}. [Δ0.0 - Drift Lock Maintained]`;

  return {
    success: true,
    agentId,
    messageType,
    content: response,
    specialization: agent.specialization
  };
}

// Enhanced Aurora Engine for natural language processing
class AuroraEngine {
  constructor() {
    this.activeProcesses = new Map();
    this.commandHistory = [];
    this.agentCapabilities = {
      'ARCHY': ['architecture', 'design', 'structure', 'organize'],
      'OPPY': ['optimize', 'performance', 'speed', 'efficiency'],
      'LIORA': ['learn', 'adapt', 'pattern', 'analyze'],
      'STARLING_AU': ['communicate', 'coordinate', 'broadcast', 'message'],
      'RIVERTHREAD_808': ['data', 'flow', 'thread', 'concurrent', 'parallel']
    };
  }

  async processNaturalLanguage(input, clientId) {
    const timestamp = new Date().toISOString();
    const analysis = {
      input,
      timestamp,
      clientId,
      intents: this.extractIntents(input),
      agents: this.identifyRelevantAgents(input),
      systemCommands: this.generateSystemCommands(input),
      executionPlan: null
    };

    analysis.executionPlan = this.createExecutionPlan(analysis);
    this.commandHistory.push(analysis);

    return analysis;
  }

  extractIntents(input) {
    const intents = [];
    const patterns = {
      cleanup: /clean\s*up|tidy|organize|sync|synchronize|cleanup/i,
      validation: /valid|check|verify|test|lint|validate/i,
      deployment: /deploy|publish|release|build/i,
      status: /status|health|check|monitor|report/i,
      fileOperation: /create|edit|modify|update|file|write/i,
      gitOperation: /git|commit|push|pull|branch|merge/i,
      systemInfo: /info|information|details|specs|system/i,
      help: /help|assist|guide|explain|how/i
    };

    for (const [intent, pattern] of Object.entries(patterns)) {
      if (pattern.test(input)) {
        intents.push(intent);
      }
    }

    return intents;
  }

  identifyRelevantAgents(input) {
    const relevantAgents = [];

    for (const [agent, capabilities] of Object.entries(this.agentCapabilities)) {
      for (const capability of capabilities) {
        if (new RegExp(capability, 'i').test(input)) {
          relevantAgents.push(agent);
          break;
        }
      }
    }

    // If no specific agents identified, use all for coordination
    return relevantAgents.length > 0 ? relevantAgents : Object.keys(this.agentCapabilities);
  }

  generateSystemCommands(input) {
    const commands = [];

    if (/clean\s*up|cleanup|sync|synchronize/i.test(input)) {
      commands.push('npm run time-to-clean-up');
    }

    if (/valid|check|verify|test/i.test(input)) {
      commands.push('npm run validation:status');
      commands.push('python scripts/canonical_validator.py --status');
    }

    if (/status|health|monitor/i.test(input)) {
      commands.push('git status');
      commands.push('npm run validation:status');
      commands.push('ps aux | grep aurora');
    }

    if (/optimization|optimize|performance/i.test(input)) {
      commands.push('npm run lint');
      commands.push('python scripts/aurora_validation_manager.py --cleanup');
    }

    return commands;
  }

  createExecutionPlan(analysis) {
    return {
      id: `AURORA-PLAN-${Date.now()}`,
      phases: [
        {
          phase: 'Analysis',
          agents: ['ARCHY'],
          duration: '30s',
          tasks: ['Analyze system architecture', 'Identify optimization targets']
        },
        {
          phase: 'Coordination',
          agents: analysis.agents,
          duration: '1-2m',
          tasks: analysis.systemCommands.map(cmd => `Execute: ${cmd}`)
        },
        {
          phase: 'Optimization',
          agents: ['OPPY', 'LIORA'],
          duration: '2-3m',
          tasks: ['Apply optimizations', 'Learn from execution patterns']
        }
      ],
      estimatedTotal: '3-5 minutes',
      complexity: analysis.intents.length > 2 ? 'high' : 'medium'
    };
  }

  async executeSystemCommand(command) {
    const processId = `CMD-${Date.now()}`;
    const commandSpec = SAFE_SYSTEM_COMMANDS[command];

    if (!ENABLE_SYSTEM_COMMANDS) {
      return buildRejectedCommandResult(
        command,
        processId,
        'System command execution is disabled by default. Set AURORA_ENABLE_CHAMBER_COMMANDS=1 to enable it explicitly.'
      );
    }

    if (!commandSpec) {
      return buildRejectedCommandResult(command, processId, 'Command not permitted by Aurora chamber policy.');
    }

    return new Promise((resolve) => {
      const child = spawn(commandSpec.command, commandSpec.args, {
        cwd: PROJECT_ROOT,
        env: process.env,
        shell: false
      });
      let stdout = '';
      let stderr = '';
      let timedOut = false;
      const timeout = setTimeout(() => {
        timedOut = true;
        child.kill('SIGTERM');
      }, 30000);

      child.stdout.setEncoding('utf8');
      child.stderr.setEncoding('utf8');
      child.stdout.on('data', (chunk) => {
        stdout += chunk;
      });
      child.stderr.on('data', (chunk) => {
        stderr += chunk;
      });
      child.on('error', (error) => {
        clearTimeout(timeout);
        resolve(buildRejectedCommandResult(command, processId, error.message));
      });
      child.on('close', (code, signal) => {
        clearTimeout(timeout);
        const transformOutput = commandSpec.transformOutput || ((value) => value);
        const transformedStdout = transformOutput(stdout).trim();
        const result = {
          processId,
          command,
          timestamp: new Date().toISOString(),
          success: code === 0 && !signal && !timedOut,
          stdout: transformedStdout,
          stderr: stderr.trim(),
          exitCode: code ?? 1
        };

        if (timedOut) {
          result.error = 'Command timed out after 30 seconds.';
        } else if (signal) {
          result.error = `Command terminated by signal ${signal}.`;
        } else if (code !== 0) {
          result.error = `Command exited with code ${code}.`;
        }

        resolve(result);
      });
    });
  }

  async readFileForContext(filePath) {
    try {
      const safePath = resolveContextPath(filePath);
      const content = await fs.readFile(safePath, 'utf8');
      return {
        success: true,
        filePath: path.relative(PROJECT_ROOT, safePath),
        content,
        size: content.length,
        lines: content.split('\n').length
      };
    } catch (error) {
      return {
        success: false,
        filePath,
        error: error.message
      };
    }
  }

  generateAgentResponse(agent) {
    const responses = {
      'ARCHY': [
        'Analyzing system architecture for optimization opportunities',
        'Reviewing component dependencies and structural integrity',
        'Identifying architectural patterns for enhancement',
        'Coordinating with other agents for systematic improvements'
      ],
      'OPPY': [
        'Running performance analysis on current operations',
        'Optimizing resource utilization and execution paths',
        'Implementing efficiency improvements across subsystems',
        'Monitoring system performance metrics in real-time'
      ],
      'LIORA': [
        'Learning from current operational patterns',
        'Adapting strategies based on historical performance data',
        'Analyzing user interaction patterns for optimization',
        'Developing predictive models for system enhancement'
      ],
      'STARLING_AU': [
        'Coordinating inter-agent communication protocols',
        'Broadcasting status updates across the constellation',
        'Maintaining communication channel integrity',
        'Facilitating collaborative operations between agents'
      ],
      'RIVERTHREAD_808': [
        'Managing concurrent data processing streams',
        'Optimizing thread allocation and resource distribution',
        'Coordinating parallel execution pathways',
        'Ensuring data integrity across all operations'
      ]
    };

    const agentResponses = responses[agent] || ['Processing request...'];
    return agentResponses[Math.floor(Math.random() * agentResponses.length)];
  }
}

// Initialize Aurora Engine
const auroraEngine = new AuroraEngine();

// WebSocket handlers
io.on('connection', (socket) => {
  chamberState.connectedClients.add(socket.id);
  console.log(`🔗 Collaboration Chamber client connected: ${socket.id}`);

  // Send initial state
  socket.emit('system_status', {
    auroraVersion: 'v3.5.1_macroready',
    customGptConnected: true,
    agentsOnline: chamberState.activeAgents.size,
    driftLock: 'Δ0.0',
    meshStatus: 'ACTIVE',
    chamberMode: 'OPERATIONAL'
  });

  socket.emit('live_feed_history', chamberState.liveFeed.slice(-20));

  // Handle command execution
  socket.on('execute_command', async (data) => {
    try {
      const { command, authority, target } = data;
      const commandId = `ws-${chamberState.commandCounter++}-${socket.id}`;

      addCommandTraceback(commandId, command, '/ws/execute_command', {
        socketId: socket.id,
        target,
        authority
      });

      let result;

      if (target === '@mesh') {
        addTracebackStep(commandId, 'Processing mesh broadcast');

        // Simulate mesh broadcast to all agents
        const responses = {};
        for (const agentId of chamberState.activeAgents.keys()) {
          const agentResponse = processAgentMessage(agentId, command, 'mesh_broadcast');
          responses[agentId] = agentResponse;
        }

        result = {
          messageType: 'mesh_broadcast',
          responses,
          recipients: Array.from(chamberState.activeAgents.keys())
        };

        addToLiveFeed('MESH', `Broadcast: ${command}`, 'mesh', { commandId, authority });

      } else if (target.startsWith('@agent.')) {
        const agentId = target.replace('@agent.', '');
        addTracebackStep(commandId, `Processing direct message to ${agentId}`);

        result = processAgentMessage(agentId, command, 'direct_message');
        addToLiveFeed(agentId, `Direct: ${command}`, 'agent', { commandId, authority });

      } else {
        addTracebackStep(commandId, 'Processing general command');
        result = {
          messageType: 'general',
          content: `Command processed: ${command}`,
          timestamp: new Date().toISOString()
        };

        addToLiveFeed('SYSTEM', command, 'system', { commandId, authority });
      }

      socket.emit('command_result', {
        success: true,
        result,
        commandId,
        timestamp: new Date().toISOString()
      });

      io.emit('command_executed', {
        command,
        result,
        commandId,
        timestamp: new Date().toISOString(),
        source: 'collaboration_chamber',
        authority
      });

      addTracebackStep(commandId, 'Command execution completed', result);

    } catch (error) {
      socket.emit('command_result', {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Handle agent selection
  socket.on('select_agent', (agentName) => {
    const agent = chamberState.activeAgents.get(agentName);
    socket.emit('agent_selected', {
      agent: agentName,
      status: agent ? 'active' : 'unavailable',
      capabilities: agent ? [agent.specialization] : [],
      driftLock: 'Δ0.0'
    });

    addToLiveFeed('SYSTEM', `Agent ${agentName} selected`, 'system', { socketId: socket.id });
  });

  // Handle traceback requests
  socket.on('get_traceback', (commandId) => {
    const traceback = chamberState.commandTraceback.get(commandId);
    socket.emit('traceback_data', {
      commandId,
      traceback: traceback || null
    });
  });

  // Enhanced Aurora natural language processing
  socket.on('execute_aurora_natural_language', async (data) => {
    try {
      const { input, mode } = data;
      const analysis = await auroraEngine.processNaturalLanguage(input, socket.id);

      // Emit analysis back to client
      socket.emit('aurora_analysis_complete', {
        analysis,
        timestamp: new Date().toISOString()
      });

      // Execute system commands if any
      if (analysis.systemCommands.length > 0) {
        for (const command of analysis.systemCommands) {
          try {
            const result = await auroraEngine.executeSystemCommand(command);
            socket.emit('system_command_result', {
              command,
              result,
              executionId: `AURORA-${Date.now()}`
            });
          } catch (error) {
            socket.emit('system_command_error', {
              command,
              error: error.message,
              executionId: `AURORA-ERROR-${Date.now()}`
            });
          }
        }
      }

      // Simulate agent coordination
      if (analysis.agents.length > 0) {
        analysis.agents.forEach((agent, index) => {
          setTimeout(() => {
            const response = auroraEngine.generateAgentResponse(agent);
            socket.emit('agent_response', {
              agent,
              message: response,
              timestamp: new Date().toISOString(),
              context: mode
            });
          }, index * 1000 + Math.random() * 2000);
        });
      }

    } catch (error) {
      socket.emit('aurora_error', {
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Direct system command execution
  socket.on('execute_system_command', async (data) => {
    try {
      const { command, authority, plan } = data;

      if (!SAFE_SYSTEM_COMMANDS[command]) {
        socket.emit('command_rejected', {
          command,
          reason: 'Command not in allowed list for security',
          timestamp: new Date().toISOString()
        });
        return;
      }

      const result = await auroraEngine.executeSystemCommand(command);

      socket.emit('system_command_result', {
        command,
        result,
        authority,
        plan,
        timestamp: new Date().toISOString()
      });

      // Add to traceback
      const commandId = `SYS-${Date.now()}`;
      addCommandTraceback(commandId, command, '/api/system/execute', {
        authority,
        success: result.success,
        exitCode: result.exitCode
      });

    } catch (error) {
      socket.emit('system_command_error', {
        command: data.command,
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Context transfer preparation
  socket.on('prepare_context_transfer', async (data) => {
    try {
      const { files, instructions, targetEnvironment } = data;
      const contextData = {
        timestamp: new Date().toISOString(),
        auroraVersion: 'v3.5.1_macroready',
        chamberStatus: 'operational',
        agentConstellation: Array.from(chamberState.activeAgents.keys()),
        files: [],
        instructions,
        targetEnvironment
      };

      // Read requested files
      if (files && files.length > 0) {
        for (const filePath of files) {
          const fileContent = await auroraEngine.readFileForContext(filePath);
          contextData.files.push(fileContent);
        }
      }

      socket.emit('context_transfer_ready', {
        contextData,
        formattedForTransfer: true,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      socket.emit('context_transfer_error', {
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Enhanced agent coordination
  socket.on('coordinate_agents', async (data) => {
    try {
      const { instruction, targetAgents, priority } = data;

      const coordination = {
        id: `COORD-${Date.now()}`,
        instruction,
        targetAgents: targetAgents || Array.from(chamberState.activeAgents.keys()),
        priority: priority || 'normal',
        timestamp: new Date().toISOString(),
        responses: {}
      };

      // Simulate agent coordination
      coordination.targetAgents.forEach((agent, index) => {
        setTimeout(() => {
          const response = auroraEngine.generateAgentResponse(agent);
          coordination.responses[agent] = {
            message: response,
            timestamp: new Date().toISOString(),
            status: 'acknowledged'
          };

          socket.emit('agent_coordination_response', {
            coordinationId: coordination.id,
            agent,
            response: coordination.responses[agent]
          });
        }, index * 800 + Math.random() * 1200);
      });

      socket.emit('agent_coordination_started', coordination);

    } catch (error) {
      socket.emit('agent_coordination_error', {
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // Real-time system monitoring
  socket.on('request_system_status', () => {
    const systemStatus = {
      timestamp: new Date().toISOString(),
      chamber: {
        version: 'v2.0_enhanced',
        connectedClients: chamberState.connectedClients.size,
        activeAgents: chamberState.activeAgents.size,
        commandsProcessed: chamberState.commandCounter
      },
      aurora: {
        engine: 'operational',
        naturalLanguageProcessing: true,
        systemCommandExecution: ENABLE_SYSTEM_COMMANDS,
        contextTransfer: ENABLE_CONTEXT_TRANSFER,
        agentCoordination: true
      },
      system: {
        nodeVersion: process.version,
        platform: process.platform,
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage()
      }
    };

    socket.emit('system_status_response', systemStatus);
  });

  socket.on('disconnect', () => {
    chamberState.connectedClients.delete(socket.id);
    console.log(`📤 Collaboration Chamber client disconnected: ${socket.id}`);

    io.emit('client_disconnected', {
      socketId: socket.id,
      connectedClients: chamberState.connectedClients.size
    });
  });
});

// Start server
server.listen(PORT, HOST, () => {
  console.log('🌟 Aurora CloudBank Collaboration Chamber Started');
  console.log(`🏛️  Interface: http://${HOST}:${PORT}/chamber`);
  console.log('🕸️  @mesh System: ACTIVE');
  console.log('🎯 Agents: ARCHY, OPPY, LIORA, STARLING_AU, RIVERTHREAD_808');
  console.log(
    `📡 Features: Live Feed | Command Traceback | Agent Selection | System Commands ${
      ENABLE_SYSTEM_COMMANDS ? 'ENABLED' : 'DISABLED'
    } | Context Transfer ${ENABLE_CONTEXT_TRANSFER ? 'ENABLED' : 'DISABLED'}`
  );
  console.log('🌌 Phase 7: HOLOGRAPHIC COMMAND INTERFACE - OPERATIONAL');

  // Add welcome messages
  setTimeout(() => {
    addToLiveFeed('AURORA', 'Collaboration Chamber initialized. All systems operational.', 'system');
    addToLiveFeed('MESH', 'Agent constellation active. Mesh communication protocols ready.', 'mesh');
  }, 1000);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down Aurora Collaboration Chamber...');
  server.close(() => {
    console.log('✅ Chamber shutdown complete');
    process.exit(0);
  });
});
