/**
 * Constellation API Server
 * Symbolic Anchor: T1_CONSTELLATION_PRIME
 * 
 * Main API server with REST and WebSocket endpoints for constellation management
 */

import express, { Request, Response } from 'express';
import { WebSocketServer, WebSocket } from 'ws';
import http from 'http';
import constellationConfig from '../constellation.config.js';
import { ServiceRegistry } from './core/service-registry.js';
import { Orchestrator } from './core/orchestrator.js';
import { AuroraOSBridge } from './bridges/aurora-os/bridge.js';
import { ZipWizardBridge } from './bridges/zip-wizard/bridge.js';
import { QuantumBridge } from './bridges/quantum-en/bridge.js';

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// Middleware
app.use(express.json());

// Initialize constellation components
const serviceRegistry = new ServiceRegistry({
  healthCheckInterval: constellationConfig.monitoring.healthCheckInterval,
  driftThreshold: constellationConfig.monitoring.driftThreshold
});

const orchestrator = new Orchestrator({
  maxConcurrentTasks: constellationConfig.orchestration.maxConcurrentTasks,
  taskQueueSize: constellationConfig.orchestration.taskQueueSize
});

// Initialize bridges (these will be connected when services are available)
const bridges = {
  auroraOS: new AuroraOSBridge({
    endpoint: constellationConfig.constellation.satellites[0].endpoint,
    reconnectInterval: 5000,
    maxReconnectAttempts: 5
  }),
  zipWizard: new ZipWizardBridge({
    endpoint: constellationConfig.constellation.satellites[1].endpoint,
    timeout: 30000
  }),
  quantum: new QuantumBridge({
    endpoint: constellationConfig.constellation.satellites[2].endpoint,
    timeout: 30000
  })
};

// Register services
serviceRegistry.registerService(constellationConfig.constellation.hub);
constellationConfig.constellation.satellites.forEach(satellite => {
  serviceRegistry.registerService(satellite);
});

// Start health monitoring
serviceRegistry.startHealthMonitoring();

// Event forwarding to WebSocket clients
const wsClients: Set<WebSocket> = new Set();

serviceRegistry.on('healthUpdate', (health) => {
  broadcastToClients({
    type: 'healthUpdate',
    data: health,
    timestamp: new Date().toISOString()
  });
});

serviceRegistry.on('driftDetected', (drift) => {
  broadcastToClients({
    type: 'driftDetected',
    data: drift,
    timestamp: new Date().toISOString()
  });
});

orchestrator.on('taskSubmitted', (task) => {
  broadcastToClients({
    type: 'taskSubmitted',
    data: task,
    timestamp: new Date().toISOString()
  });
});

orchestrator.on('taskCompleted', (task) => {
  broadcastToClients({
    type: 'taskCompleted',
    data: task,
    timestamp: new Date().toISOString()
  });
});

// WebSocket connection handling
wss.on('connection', (ws: WebSocket) => {
  console.log('[T1_CONSTELLATION_PRIME] WebSocket client connected');
  wsClients.add(ws);

  ws.on('close', () => {
    console.log('[T1_CONSTELLATION_PRIME] WebSocket client disconnected');
    wsClients.delete(ws);
  });

  // Send initial state
  ws.send(JSON.stringify({
    type: 'connected',
    data: {
      services: serviceRegistry.getServices(),
      health: serviceRegistry.getHealthStatus(),
      stats: orchestrator.getStats()
    },
    timestamp: new Date().toISOString()
  }));
});

function broadcastToClients(message: any): void {
  const data = JSON.stringify(message);
  wsClients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(data);
    }
  });
}

// REST API Endpoints

/**
 * Health check endpoint
 */
app.get('/api/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    anchor: 'T1_CONSTELLATION_PRIME',
    timestamp: new Date().toISOString()
  });
});

/**
 * Get constellation configuration
 */
app.get('/api/constellation/config', (req: Request, res: Response) => {
  res.json({
    success: true,
    config: constellationConfig,
    anchor: 'T1_CONSTELLATION_PRIME'
  });
});

/**
 * Get constellation status
 */
app.get('/api/constellation/status', (req: Request, res: Response) => {
  res.json({
    success: true,
    status: {
      services: serviceRegistry.getServices().length,
      health: serviceRegistry.getHealthStatus(),
      orchestrator: orchestrator.getStats(),
      bridges: {
        auroraOS: bridges.auroraOS.getStats(),
        zipWizard: bridges.zipWizard.getStats(),
        quantum: bridges.quantum.getStats()
      }
    },
    anchor: 'T1_CONSTELLATION_PRIME',
    timestamp: new Date().toISOString()
  });
});

/**
 * Get all services
 */
app.get('/api/services', (req: Request, res: Response) => {
  res.json({
    success: true,
    services: serviceRegistry.getServices(),
    anchor: 'T1_SERVICE_DISCOVERY'
  });
});

/**
 * Get service health
 */
app.get('/api/services/health', (req: Request, res: Response) => {
  res.json({
    success: true,
    health: serviceRegistry.getHealthStatus(),
    anchor: 'T1_SERVICE_DISCOVERY'
  });
});

/**
 * Get specific service
 */
app.get('/api/services/:name', (req: Request, res: Response) => {
  const service = serviceRegistry.getService(req.params.name);
  
  if (!service) {
    return res.status(404).json({
      success: false,
      error: 'Service not found',
      serviceName: req.params.name
    });
  }

  res.json({
    success: true,
    service,
    health: serviceRegistry.getServiceHealth(req.params.name),
    anchor: 'T1_SERVICE_DISCOVERY'
  });
});

/**
 * Submit task
 */
app.post('/api/tasks', (req: Request, res: Response) => {
  try {
    const { name, targetService, payload, priority, symbolicChain } = req.body;
    
    if (!name || !targetService) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: name, targetService'
      });
    }

    const taskId = orchestrator.submitTask(
      name,
      targetService,
      payload,
      priority || 'normal',
      symbolicChain || []
    );

    res.json({
      success: true,
      taskId,
      anchor: 'T1_ORCHESTRATOR_PRIME'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * Get task by ID
 */
app.get('/api/tasks/:taskId', (req: Request, res: Response) => {
  const task = orchestrator.getTask(req.params.taskId);
  
  if (!task) {
    return res.status(404).json({
      success: false,
      error: 'Task not found',
      taskId: req.params.taskId
    });
  }

  res.json({
    success: true,
    task,
    anchor: 'T1_ORCHESTRATOR_PRIME'
  });
});

/**
 * Get all tasks
 */
app.get('/api/tasks', (req: Request, res: Response) => {
  const { status, service } = req.query;
  
  let tasks = orchestrator.getAllTasks();
  
  if (status && typeof status === 'string') {
    tasks = orchestrator.getTasksByStatus(status as any);
  }
  
  if (service && typeof service === 'string') {
    tasks = tasks.filter(t => t.targetService === service);
  }

  res.json({
    success: true,
    tasks,
    count: tasks.length,
    anchor: 'T1_ORCHESTRATOR_PRIME'
  });
});

/**
 * Cancel task
 */
app.post('/api/tasks/:taskId/cancel', (req: Request, res: Response) => {
  const cancelled = orchestrator.cancelTask(req.params.taskId);
  
  res.json({
    success: cancelled,
    taskId: req.params.taskId,
    anchor: 'T1_ORCHESTRATOR_PRIME'
  });
});

/**
 * Get orchestrator stats
 */
app.get('/api/orchestrator/stats', (req: Request, res: Response) => {
  res.json({
    success: true,
    stats: orchestrator.getStats(),
    anchor: 'T1_ORCHESTRATOR_PRIME'
  });
});

/**
 * Create memory snapshot
 */
app.post('/api/memory/snapshot', (req: Request, res: Response) => {
  const registrySeal = serviceRegistry.sealMemoryState();
  const orchestratorSnapshot = orchestrator.createMemorySnapshot();
  
  res.json({
    success: true,
    snapshots: {
      registry: registrySeal,
      orchestrator: orchestratorSnapshot
    },
    anchor: 'T1_CONSTELLATION_PRIME'
  });
});

/**
 * Get memory seals
 */
app.get('/api/memory/seals', (req: Request, res: Response) => {
  res.json({
    success: true,
    seals: {
      registry: serviceRegistry.getMemorySeals(),
      orchestrator: orchestrator.getMemorySnapshots()
    },
    anchor: 'T1_CONSTELLATION_PRIME'
  });
});

// Start server
const PORT = process.env.PORT || 5000;

server.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════════╗
║  🌟 Constellation API Server Running                          ║
║                                                                ║
║  Symbolic Anchor: T1_CONSTELLATION_PRIME                      ║
║  Ethics Protocol: Picard_Delta_3                              ║
║  Seed: EOS_SEED_ORION                                         ║
║                                                                ║
║  HTTP API: http://localhost:${PORT}                              ║
║  WebSocket: ws://localhost:${PORT}                               ║
║                                                                ║
║  Services Registered: ${serviceRegistry.getServices().length}                                 ║
║  Health Monitoring: Active                                    ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n[T1_CONSTELLATION_PRIME] Shutting down gracefully...');
  
  serviceRegistry.stopHealthMonitoring();
  
  await Promise.allSettled([
    bridges.auroraOS.disconnect().catch(() => {}),
    bridges.zipWizard.disconnect().catch(() => {}),
    bridges.quantum.disconnect().catch(() => {})
  ]);
  
  server.close(() => {
    console.log('[T1_CONSTELLATION_PRIME] Server closed');
    process.exit(0);
  });
});

export { app, server, serviceRegistry, orchestrator, bridges };
