/**
 * Constellation Architecture Basic Tests
 * Symbolic Anchor: T1_CONSTELLATION_PRIME
 * 
 * Basic validation tests for the constellation architecture components
 */

import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';
import { ServiceRegistry } from '../src/core/service-registry.js';
import { Orchestrator } from '../src/core/orchestrator.js';
import constellationConfig from '../constellation.config.js';

describe('Constellation Architecture', () => {
  describe('Configuration', () => {
    it('should have valid constellation configuration', () => {
      expect(constellationConfig).toBeDefined();
      expect(constellationConfig.version).toBe('1.0.0');
      expect(constellationConfig.constellation.hub.name).toBe('aurora-cloudbank-symbolic');
      expect(constellationConfig.constellation.satellites).toHaveLength(3);
    });

    it('should have correct symbolic anchors', () => {
      expect(constellationConfig.symbolicAnchors.primary).toBe('T1_CONSTELLATION_PRIME');
      expect(constellationConfig.symbolicAnchors.serviceDiscovery).toBe('T1_SERVICE_DISCOVERY');
      expect(constellationConfig.symbolicAnchors.orchestrator).toBe('T1_ORCHESTRATOR_PRIME');
    });

    it('should have correct ethics protocol', () => {
      expect(constellationConfig.security.ethicsProtocol).toBe('Picard_Delta_3');
      expect(constellationConfig.security.seed).toBe('EOS_SEED_ORION');
    });
  });

  describe('Service Registry', () => {
    let registry: ServiceRegistry;

    beforeAll(() => {
      registry = new ServiceRegistry({
        healthCheckInterval: 30000,
        driftThreshold: 0.15
      });
    });

    it('should create a service registry', () => {
      expect(registry).toBeDefined();
    });

    it('should register services', () => {
      registry.registerService(constellationConfig.constellation.hub);
      const services = registry.getServices();
      expect(services).toHaveLength(1);
      expect(services[0].name).toBe('aurora-cloudbank-symbolic');
    });

    it('should get registered service by name', () => {
      const service = registry.getService('aurora-cloudbank-symbolic');
      expect(service).toBeDefined();
      expect(service?.symbolicAnchor).toBe('T1_CONSTELLATION_PRIME');
    });

    it('should create memory seals', () => {
      const seal = registry.sealMemoryState();
      expect(seal).toBeDefined();
      expect(seal.stateHash).toBeDefined();
      expect(seal.anchor).toBe('T1_SERVICE_DISCOVERY');
    });

    it('should track health status', () => {
      const health = registry.getHealthStatus();
      expect(health).toBeDefined();
      expect(Array.isArray(health)).toBe(true);
    });
  });

  describe('Orchestrator', () => {
    let orchestrator: Orchestrator;

    beforeAll(() => {
      orchestrator = new Orchestrator({
        maxConcurrentTasks: 10,
        taskQueueSize: 1000
      });
    });

    it('should create an orchestrator', () => {
      expect(orchestrator).toBeDefined();
    });

    it('should submit tasks', () => {
      const taskId = orchestrator.submitTask(
        'test-task',
        'AuroraOS',
        { test: true },
        'normal',
        ['T1_CONSTELLATION_PRIME']
      );

      expect(taskId).toBeDefined();
      expect(typeof taskId).toBe('string');
    });

    it('should retrieve submitted tasks', () => {
      const tasks = orchestrator.getAllTasks();
      expect(tasks.length).toBeGreaterThan(0);
    });

    it('should get task by ID', () => {
      const tasks = orchestrator.getAllTasks();
      const taskId = tasks[0].id;
      const task = orchestrator.getTask(taskId);
      expect(task).toBeDefined();
      expect(task?.id).toBe(taskId);
    });

    it('should provide queue statistics', () => {
      const stats = orchestrator.getQueueStats();
      expect(stats).toBeDefined();
      expect(stats).toHaveProperty('high');
      expect(stats).toHaveProperty('normal');
      expect(stats).toHaveProperty('low');
      expect(stats).toHaveProperty('running');
      expect(stats).toHaveProperty('total');
    });

    it('should create memory snapshots', () => {
      const snapshot = orchestrator.createMemorySnapshot();
      expect(snapshot).toBeDefined();
      expect(snapshot.snapshotHash).toBeDefined();
      expect(snapshot.anchor).toBe('T1_ORCHESTRATOR_PRIME');
    });

    it('should track tasks by status', () => {
      const pendingTasks = orchestrator.getTasksByStatus('pending');
      expect(Array.isArray(pendingTasks)).toBe(true);
    });

    it('should track tasks by service', () => {
      const auroraOSTasks = orchestrator.getTasksByService('AuroraOS');
      expect(Array.isArray(auroraOSTasks)).toBe(true);
    });
  });
});
