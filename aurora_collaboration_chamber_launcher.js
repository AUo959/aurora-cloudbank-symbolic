#!/usr/bin/env node

/**
 * Aurora Collaboration Chamber Launcher
 * Enhanced Aurora CloudBank holographic interface with @mesh system integration
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

const PORT = 8080;

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
server.listen(PORT, () => {
  console.log('🌟 Aurora CloudBank Collaboration Chamber Started');
  console.log(`🏛️  Interface: http://localhost:${PORT}/chamber`);
  console.log('🕸️  @mesh System: ACTIVE');
  console.log('🎯 Agents: ARCHY, OPPY, LIORA, STARLING_AU, RIVERTHREAD_808');
  console.log('📡 Features: Live Feed | Command Traceback | Agent Selection');
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
