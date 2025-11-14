/**
 * 🚦 AURORA COMMAND ROUTER - Multi-Layer Command Dispatch System
 * Handles routing and validation of commands across L1, L2, and L3 layers
 * Aurora CloudBank Symbolic v3.5.1 - Core Implementation
 */

import { bridgeLogger } from '../utils/aurora_logger.js';

class AuroraCommandRouter {
  constructor() {
    this.routerId = 'AURORA_COMMAND_ROUTER';
    this.version = '3.5.1';
    this.status = 'OPERATIONAL';
    
    // Command routing tables
    this.routingTables = {
      l1: new Map(),
      l2: new Map(),
      l3: new Map()
    };
    
    // Command history and metrics
    this.commandHistory = [];
    this.routingMetrics = {
      totalCommands: 0,
      successfulRoutes: 0,
      failedRoutes: 0,
      averageLatency: 0
    };
    
    // Layer clearance mapping
    this.clearanceLevels = {
      'L1_ONLY': ['L1'],
      'L1_L2_BRIDGE': ['L1', 'L2'],
      'L1_L3_INTEGRATION': ['L1', 'L2', 'L3'],
      'L2_L3_BRIDGE': ['L2', 'L3'],
      'L3_SYMBOLIC': ['L3'],
      'EMERGENCY_PROTOCOL': ['L1', 'L2', 'L3', 'EMERGENCY']
    };
    
    this.initialize();
  }

  initialize() {
    // Set up default routing handlers
    this.setupDefaultRoutes();
    
    bridgeLogger.bridge('Aurora Command Router initialized', {
      routerId: this.routerId,
      version: this.version,
      clearanceLevels: Object.keys(this.clearanceLevels).length
    });
  }

  setupDefaultRoutes() {
    // L1 layer routes (Agent bridges)
    this.routingTables.l1.set('ARCHY', this.createAgentHandler('ARCHY', 'L1'));
    this.routingTables.l1.set('LIORA', this.createAgentHandler('LIORA', 'L1'));
    this.routingTables.l1.set('OPPY', this.createAgentHandler('OPPY', 'L1'));
    this.routingTables.l1.set('STARLING_AU', this.createAgentHandler('STARLING_AU', 'L1'));
    this.routingTables.l1.set('RIVERTHREAD_808', this.createAgentHandler('RIVERTHREAD_808', 'L1'));
    
    // L2 layer routes (Cognitive agents)
    this.routingTables.l2.set('ARCHY', this.createAgentHandler('ARCHY', 'L2'));
    this.routingTables.l2.set('LIORA', this.createAgentHandler('LIORA', 'L2'));
    this.routingTables.l2.set('OPPY', this.createAgentHandler('OPPY', 'L2'));
    this.routingTables.l2.set('STARLING_AU', this.createAgentHandler('STARLING_AU', 'L2'));
    this.routingTables.l2.set('RIVERTHREAD_808', this.createAgentHandler('RIVERTHREAD_808', 'L2'));
    this.routingTables.l2.set('DAEDALUS', this.createAgentHandler('DAEDALUS', 'L2'));
    this.routingTables.l2.set('VOIDWHISPER', this.createAgentHandler('VOIDWHISPER', 'L2'));
    
    // L3 layer routes (Symbolic agents)
    this.routingTables.l3.set('Glyphon', this.createAgentHandler('Glyphon', 'L3'));
    this.routingTables.l3.set('Axiomera', this.createAgentHandler('Axiomera', 'L3'));
    this.routingTables.l3.set('Sentari', this.createAgentHandler('Sentari', 'L3'));
    this.routingTables.l3.set('Caelion', this.createAgentHandler('Caelion', 'L3'));
    this.routingTables.l3.set('Velatrix', this.createAgentHandler('Velatrix', 'L3'));
    this.routingTables.l3.set('Harmion', this.createAgentHandler('Harmion', 'L3'));
    
    // Special routes
    this.routingTables.l1.set('SHADOWFAX', this.createEmergencyHandler('SHADOWFAX'));
  }

  createAgentHandler(agentId, layer) {
    return async (command, metadata = {}) => {
      // Simulate agent processing
      const processingDelay = Math.random() * 100 + 50; // 50-150ms
      
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            success: true,
            agentId: agentId,
            layer: layer,
            command: command,
            metadata: metadata,
            result: `Processed by ${agentId} on ${layer}`,
            timestamp: Date.now()
          });
        }, processingDelay);
      });
    };
  }

  createEmergencyHandler(agentId) {
    return async (command, metadata = {}) => {
      bridgeLogger.critical(`Emergency protocol activated: ${agentId}`, {
        command: command,
        metadata: metadata
      });
      
      return {
        success: true,
        agentId: agentId,
        layer: 'EMERGENCY',
        command: command,
        emergency: true,
        result: `Emergency handled by ${agentId}`,
        timestamp: Date.now()
      };
    };
  }

  async dispatch(routingRequest) {
    const startTime = Date.now();
    
    try {
      // Validate routing request
      const validation = this.validateRoutingRequest(routingRequest);
      if (!validation.valid) {
        throw new Error(`Routing validation failed: ${validation.reason}`);
      }

      // Determine target layer
      const targetLayer = this.determineTargetLayer(routingRequest.layer);
      
      // Check clearance
      if (!this.checkClearance(routingRequest.metadata?.clearanceLevel, targetLayer)) {
        throw new Error(`Insufficient clearance for ${targetLayer} access`);
      }

      // Route the command
      const result = await this.routeCommand(routingRequest, targetLayer);
      
      // Update metrics
      const latency = Date.now() - startTime;
      this.updateMetrics(true, latency);
      
      // Log successful route
      this.logRoute(routingRequest, result, latency, true);
      
      return result;

    } catch (error) {
      // Update metrics for failed route
      const latency = Date.now() - startTime;
      this.updateMetrics(false, latency);
      
      // Log failed route
      this.logRoute(routingRequest, null, latency, false, error.message);
      
      // Return error response
      return {
        success: false,
        error: error.message,
        routingRequest: routingRequest,
        timestamp: Date.now()
      };
    }
  }

  validateRoutingRequest(request) {
    // Validate required fields
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

  determineTargetLayer(layerSpec) {
    // Parse layer specification
    if (layerSpec.includes('L1')) return 'L1';
    if (layerSpec.includes('L2')) return 'L2';
    if (layerSpec.includes('L3')) return 'L3';
    if (layerSpec === 'EMERGENCY_PROTOCOL') return 'L1';
    if (layerSpec === 'SYNC_BEACON') return 'L1';
    if (layerSpec === 'ANCHOR_SYNC') return 'L1';
    if (layerSpec === 'DRIFT_CHECK') return 'L1';
    if (layerSpec === 'MEMORY_AUDIT') return 'L1';
    
    // Default to L2 if unclear
    return 'L2';
  }

  checkClearance(clearanceLevel, targetLayer) {
    if (!clearanceLevel) return true; // No clearance specified
    
    const allowedLayers = this.clearanceLevels[clearanceLevel];
    if (!allowedLayers) return false;
    
    return allowedLayers.includes(targetLayer) || allowedLayers.includes('EMERGENCY');
  }

  async routeCommand(request, targetLayer) {
    const routingTable = this.routingTables[targetLayer.toLowerCase()];
    if (!routingTable) {
      throw new Error(`No routing table for layer ${targetLayer}`);
    }

    const handler = routingTable.get(request.agent);
    if (!handler) {
      // Create a default handler for unknown agents
      return this.createDefaultResponse(request, targetLayer);
    }

    // Execute the handler
    const result = await handler(request.command, request.metadata);
    
    return {
      ...result,
      routedBy: this.routerId,
      routingLayer: targetLayer,
      routingTimestamp: Date.now()
    };
  }

  createDefaultResponse(request, targetLayer) {
    return {
      success: true,
      agentId: request.agent,
      layer: targetLayer,
      command: request.command,
      result: `Default handling for ${request.agent} on ${targetLayer}`,
      default: true,
      routedBy: this.routerId,
      timestamp: Date.now()
    };
  }

  updateMetrics(success, latency) {
    this.routingMetrics.totalCommands++;
    
    if (success) {
      this.routingMetrics.successfulRoutes++;
    } else {
      this.routingMetrics.failedRoutes++;
    }
    
    // Update average latency
    const totalLatency = this.routingMetrics.averageLatency * (this.routingMetrics.totalCommands - 1) + latency;
    this.routingMetrics.averageLatency = totalLatency / this.routingMetrics.totalCommands;
  }

  logRoute(request, result, latency, success, error = null) {
    const logEntry = {
      timestamp: Date.now(),
      routerId: this.routerId,
      agent: request.agent,
      layer: request.layer,
      success: success,
      latency: latency,
      command: request.command?.type || 'unknown',
      error: error
    };

    this.commandHistory.push(logEntry);
    
    // Keep history manageable
    if (this.commandHistory.length > 1000) {
      this.commandHistory = this.commandHistory.slice(-500);
    }

    // Log to bridge logger
    if (success) {
      bridgeLogger.bridge(`Command routed: ${request.agent}`, {
        layer: request.layer,
        latency: latency,
        commandType: request.command?.type
      });
    } else {
      bridgeLogger.error(`Command routing failed: ${request.agent}`, {
        layer: request.layer,
        error: error,
        latency: latency
      });
    }
  }

  // Special routing methods for different command types
  async routeL3Validation(agentId, validationRequest) {
    return this.dispatch({
      agent: agentId,
      layer: 'L3_SYMBOLIC',
      command: {
        type: 'validation',
        ...validationRequest
      },
      metadata: {
        clearanceLevel: 'L1_L3_INTEGRATION',
        validationType: 'symbolic'
      }
    });
  }

  async routeEmergency(emergencyRequest) {
    return this.dispatch({
      agent: 'SHADOWFAX',
      layer: 'EMERGENCY_PROTOCOL',
      command: emergencyRequest,
      metadata: {
        clearanceLevel: 'EMERGENCY_PROTOCOL',
        priority: 'CRITICAL'
      }
    });
  }

  // Status and monitoring
  getStatus() {
    return {
      routerId: this.routerId,
      version: this.version,
      status: this.status,
      metrics: this.routingMetrics,
      recentCommands: this.commandHistory.slice(-10),
      routingTables: {
        l1: Array.from(this.routingTables.l1.keys()),
        l2: Array.from(this.routingTables.l2.keys()),
        l3: Array.from(this.routingTables.l3.keys())
      },
      clearanceLevels: Object.keys(this.clearanceLevels)
    };
  }

  getMetrics() {
    const successRate = this.routingMetrics.totalCommands > 0 ? 
      (this.routingMetrics.successfulRoutes / this.routingMetrics.totalCommands) * 100 : 0;

    return {
      ...this.routingMetrics,
      successRate: successRate,
      recentLatency: this.commandHistory.slice(-10).map(c => c.latency),
      timestamp: Date.now()
    };
  }

  // Route registration for dynamic agents
  registerRoute(layer, agentId, handler) {
    const routingTable = this.routingTables[layer.toLowerCase()];
    if (!routingTable) {
      throw new Error(`Invalid layer: ${layer}`);
    }

    routingTable.set(agentId, handler);
    
    bridgeLogger.bridge(`Route registered: ${agentId} on ${layer}`, {
      routerId: this.routerId,
      totalRoutes: routingTable.size
    });
  }

  unregisterRoute(layer, agentId) {
    const routingTable = this.routingTables[layer.toLowerCase()];
    if (!routingTable) return false;

    const removed = routingTable.delete(agentId);
    
    if (removed) {
      bridgeLogger.bridge(`Route unregistered: ${agentId} from ${layer}`, {
        routerId: this.routerId,
        remainingRoutes: routingTable.size
      });
    }

    return removed;
  }
}

export { AuroraCommandRouter };
export default AuroraCommandRouter;