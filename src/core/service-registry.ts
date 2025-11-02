/**
 * Service Registry with Health Monitoring and Drift Detection
 * Symbolic Anchor: T1_SERVICE_DISCOVERY
 * 
 * Manages service discovery, health monitoring, and drift detection
 * for all services in the Constellation.
 */

import crypto from 'crypto';
import { EventEmitter } from 'events';
import { ServiceConfig } from '../../constellation.config.js';

export interface ServiceHealth {
  serviceName: string;
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  lastCheck: Date;
  responseTime: number;
  consecutiveFailures: number;
}

export interface DriftDetection {
  serviceName: string;
  baselineHash: string;
  currentHash: string;
  divergence: number;
  timestamp: Date;
  details: string;
}

export interface MemorySeal {
  timestamp: Date;
  stateHash: string;
  services: string[];
  anchor: string;
}

export class ServiceRegistry extends EventEmitter {
  private services: Map<string, ServiceConfig> = new Map();
  private healthStatus: Map<string, ServiceHealth> = new Map();
  private driftBaselines: Map<string, string> = new Map();
  private memorySeals: MemorySeal[] = [];
  private healthCheckInterval: NodeJS.Timeout | null = null;

  constructor(private config: { healthCheckInterval: number; driftThreshold: number }) {
    super();
  }

  /**
   * Register a service in the registry
   */
  registerService(service: ServiceConfig): void {
    console.log(`[T1_SERVICE_DISCOVERY] Registering service: ${service.name}`);
    this.services.set(service.name, service);
    
    this.healthStatus.set(service.name, {
      serviceName: service.name,
      status: 'unknown',
      lastCheck: new Date(),
      responseTime: 0,
      consecutiveFailures: 0
    });

    // Set initial drift baseline
    const baseline = this.generateServiceHash(service);
    this.driftBaselines.set(service.name, baseline);
    
    this.emit('serviceRegistered', service.name);
  }

  /**
   * Unregister a service
   */
  unregisterService(serviceName: string): void {
    console.log(`[T1_SERVICE_DISCOVERY] Unregistering service: ${serviceName}`);
    this.services.delete(serviceName);
    this.healthStatus.delete(serviceName);
    this.driftBaselines.delete(serviceName);
    this.emit('serviceUnregistered', serviceName);
  }

  /**
   * Get all registered services
   */
  getServices(): ServiceConfig[] {
    return Array.from(this.services.values());
  }

  /**
   * Get a specific service by name
   */
  getService(name: string): ServiceConfig | undefined {
    return this.services.get(name);
  }

  /**
   * Start health monitoring
   */
  startHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      console.warn('[T1_SERVICE_DISCOVERY] Health monitoring already running');
      return;
    }

    console.log(`[T1_SERVICE_DISCOVERY] Starting health monitoring (interval: ${this.config.healthCheckInterval}ms)`);
    
    // Perform initial check
    this.performHealthCheck();
    
    // Schedule periodic checks
    this.healthCheckInterval = setInterval(
      () => this.performHealthCheck(),
      this.config.healthCheckInterval
    );
  }

  /**
   * Stop health monitoring
   */
  stopHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
      console.log('[T1_SERVICE_DISCOVERY] Health monitoring stopped');
    }
  }

  /**
   * Perform health check on all services
   */
  private async performHealthCheck(): Promise<void> {
    console.log('[T1_SERVICE_DISCOVERY] Performing health check on all services');
    
    for (const [name, service] of this.services) {
      const startTime = Date.now();
      let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
      let consecutiveFailures = this.healthStatus.get(name)?.consecutiveFailures || 0;

      try {
        // Simulate health check (in real implementation, would make HTTP/WS request)
        const isHealthy = await this.checkServiceHealth(service);
        
        if (isHealthy) {
          consecutiveFailures = 0;
          status = 'healthy';
        } else {
          consecutiveFailures++;
          status = consecutiveFailures > 2 ? 'unhealthy' : 'degraded';
        }
      } catch (error) {
        consecutiveFailures++;
        status = 'unhealthy';
        console.error(`[T1_SERVICE_DISCOVERY] Health check failed for ${name}:`, error);
      }

      const responseTime = Date.now() - startTime;
      
      const health: ServiceHealth = {
        serviceName: name,
        status,
        lastCheck: new Date(),
        responseTime,
        consecutiveFailures
      };

      this.healthStatus.set(name, health);
      this.emit('healthUpdate', health);

      // Check for drift
      await this.checkDrift(name, service);
    }
  }

  /**
   * Check service health (stub implementation)
   */
  private async checkServiceHealth(service: ServiceConfig): Promise<boolean> {
    // In real implementation, would make actual HTTP/WS request
    // For now, simulating a health check
    return new Promise((resolve) => {
      setTimeout(() => resolve(true), Math.random() * 100);
    });
  }

  /**
   * Check for drift in service state
   */
  private async checkDrift(serviceName: string, service: ServiceConfig): Promise<void> {
    const baseline = this.driftBaselines.get(serviceName);
    if (!baseline) return;

    const currentHash = this.generateServiceHash(service);
    
    if (currentHash !== baseline) {
      const divergence = this.calculateDivergence(baseline, currentHash);
      
      const drift: DriftDetection = {
        serviceName,
        baselineHash: baseline,
        currentHash,
        divergence,
        timestamp: new Date(),
        details: `Service configuration or state has diverged by ${(divergence * 100).toFixed(2)}%`
      };

      if (divergence > this.config.driftThreshold) {
        console.warn(`[T1_SERVICE_DISCOVERY] Drift detected for ${serviceName}: ${(divergence * 100).toFixed(2)}%`);
        this.emit('driftDetected', drift);
      }
    }
  }

  /**
   * Generate hash of service state for drift detection
   */
  private generateServiceHash(service: ServiceConfig): string {
    const content = JSON.stringify({
      name: service.name,
      endpoint: service.endpoint,
      capabilities: service.capabilities.sort()
    });
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Calculate divergence between two hashes
   */
  private calculateDivergence(hash1: string, hash2: string): number {
    let differences = 0;
    const length = Math.min(hash1.length, hash2.length);
    
    for (let i = 0; i < length; i++) {
      if (hash1[i] !== hash2[i]) differences++;
    }
    
    return differences / length;
  }

  /**
   * Get health status for all services
   */
  getHealthStatus(): ServiceHealth[] {
    return Array.from(this.healthStatus.values());
  }

  /**
   * Get health status for a specific service
   */
  getServiceHealth(serviceName: string): ServiceHealth | undefined {
    return this.healthStatus.get(serviceName);
  }

  /**
   * Create memory seal of current state
   */
  sealMemoryState(): MemorySeal {
    const services = Array.from(this.services.keys());
    const stateContent = JSON.stringify({
      services: services.sort(),
      health: Array.from(this.healthStatus.entries()),
      timestamp: new Date().toISOString()
    });
    
    const seal: MemorySeal = {
      timestamp: new Date(),
      stateHash: crypto.createHash('sha256').update(stateContent).digest('hex'),
      services,
      anchor: 'T1_SERVICE_DISCOVERY'
    };

    this.memorySeals.push(seal);
    console.log(`[T1_SERVICE_DISCOVERY] Memory state sealed: ${seal.stateHash.substring(0, 16)}...`);
    
    return seal;
  }

  /**
   * Verify memory seal integrity
   */
  verifyMemorySeal(seal: MemorySeal): boolean {
    const currentServices = Array.from(this.services.keys()).sort();
    const sealServices = seal.services.sort();
    
    return JSON.stringify(currentServices) === JSON.stringify(sealServices);
  }

  /**
   * Get all memory seals
   */
  getMemorySeals(): MemorySeal[] {
    return [...this.memorySeals];
  }
}
