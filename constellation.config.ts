/**
 * Constellation Architecture Configuration
 * Symbolic Anchor: T1_CONSTELLATION_PRIME
 * Ethics Protocol: Picard_Delta_3
 * Seed: EOS_SEED_ORION
 * 
 * This configuration defines the multi-repository orchestration topology
 * for the Aurora CloudBank Symbolic ecosystem.
 */

export interface ServiceConfig {
  name: string;
  repository: string;
  endpoint: string;
  protocol: 'http' | 'https' | 'ws' | 'wss' | 'grpc';
  healthCheck: string;
  capabilities: string[];
  symbolicAnchor: string;
}

export interface ConstellationConfig {
  version: string;
  constellation: {
    hub: ServiceConfig;
    satellites: ServiceConfig[];
  };
  orchestration: {
    taskQueueSize: number;
    maxConcurrentTasks: number;
    priorityLevels: string[];
  };
  monitoring: {
    healthCheckInterval: number;
    driftThreshold: number;
    memorySnapshotInterval: number;
  };
  security: {
    ethicsProtocol: string;
    seed: string;
  };
  symbolicAnchors: {
    primary: string;
    serviceDiscovery: string;
    orchestrator: string;
    bridges: {
      auroraOS: string;
      zipWizard: string;
      quantumEN: string;
    };
  };
}

export const constellationConfig: ConstellationConfig = {
  version: "1.0.0",
  
  constellation: {
    hub: {
      name: "aurora-cloudbank-symbolic",
      repository: "AUo959/aurora-cloudbank-symbolic",
      endpoint: "http://localhost:5000",
      protocol: "http",
      healthCheck: "/api/health",
      capabilities: [
        "orchestration",
        "service-discovery",
        "memory-management",
        "symbolic-processing",
        "drift-detection"
      ],
      symbolicAnchor: "T1_CONSTELLATION_PRIME"
    },
    
    satellites: [
      {
        name: "AuroraOS",
        repository: "AUo959/AuroraOS",
        endpoint: "ws://localhost:3000",
        protocol: "ws",
        healthCheck: "/health",
        capabilities: [
          "runtime-execution",
          "module-loading",
          "agent-execution",
          "real-time-events"
        ],
        symbolicAnchor: "T1_AURORA_BRIDGE"
      },
      {
        name: "zip_wizard",
        repository: "AUo959/zip_wizard",
        endpoint: "http://localhost:8080",
        protocol: "http",
        healthCheck: "/api/status",
        capabilities: [
          "archive-creation",
          "file-compression",
          "batch-processing"
        ],
        symbolicAnchor: "T1_ZIP_BRIDGE"
      },
      {
        name: "cloudbank-quantum-en",
        repository: "AUo959/cloudbank-quantum-en",
        endpoint: "http://localhost:9000",
        protocol: "http",
        healthCheck: "/api/health",
        capabilities: [
          "quantum-operations",
          "encryption",
          "key-management"
        ],
        symbolicAnchor: "T1_QUANTUM_BRIDGE"
      }
    ]
  },
  
  orchestration: {
    taskQueueSize: 1000,
    maxConcurrentTasks: 10,
    priorityLevels: ["high", "normal", "low"]
  },
  
  monitoring: {
    healthCheckInterval: 30000, // 30 seconds
    driftThreshold: 0.15, // 15% divergence triggers alert
    memorySnapshotInterval: 300000 // 5 minutes
  },
  
  security: {
    ethicsProtocol: "Picard_Delta_3",
    seed: "EOS_SEED_ORION"
  },
  
  symbolicAnchors: {
    primary: "T1_CONSTELLATION_PRIME",
    serviceDiscovery: "T1_SERVICE_DISCOVERY",
    orchestrator: "T1_ORCHESTRATOR_PRIME",
    bridges: {
      auroraOS: "T1_AURORA_BRIDGE",
      zipWizard: "T1_ZIP_BRIDGE",
      quantumEN: "T1_QUANTUM_BRIDGE"
    }
  }
};

export default constellationConfig;
