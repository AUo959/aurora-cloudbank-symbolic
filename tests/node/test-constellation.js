#!/usr/bin/env node
/**
 * Constellation Architecture Validation Script
 * Symbolic Anchor: T1_CONSTELLATION_PRIME
 * 
 * Simple validation script to test core constellation components
 */

import { ServiceRegistry } from './dist/src/core/service-registry.js';
import { Orchestrator } from './dist/src/core/orchestrator.js';
import constellationConfig from './dist/constellation.config.js';

console.log('🌟 Constellation Architecture Validation');
console.log('=========================================\n');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (error) {
    console.log(`❌ ${name}`);
    console.error(`   Error: ${error.message}`);
    failed++;
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(message || `Expected ${expected}, got ${actual}`);
  }
}

function assertTrue(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

// Test Configuration
console.log('📋 Testing Configuration');
test('Configuration is defined', () => {
  assertTrue(constellationConfig !== undefined, 'Config should be defined');
});

test('Configuration has correct version', () => {
  assertEqual(constellationConfig.version, '1.0.0', 'Version should be 1.0.0');
});

test('Hub configuration is correct', () => {
  assertEqual(
    constellationConfig.constellation.hub.name,
    'aurora-cloudbank-symbolic',
    'Hub name should be aurora-cloudbank-symbolic'
  );
});

test('Has 3 satellite services', () => {
  assertEqual(
    constellationConfig.constellation.satellites.length,
    3,
    'Should have 3 satellites'
  );
});

test('Symbolic anchors are correct', () => {
  assertEqual(
    constellationConfig.symbolicAnchors.primary,
    'T1_CONSTELLATION_PRIME',
    'Primary anchor should be T1_CONSTELLATION_PRIME'
  );
});

test('Ethics protocol is Picard_Delta_3', () => {
  assertEqual(
    constellationConfig.security.ethicsProtocol,
    'Picard_Delta_3',
    'Ethics protocol should be Picard_Delta_3'
  );
});

test('Seed is EOS_SEED_ORION', () => {
  assertEqual(
    constellationConfig.security.seed,
    'EOS_SEED_ORION',
    'Seed should be EOS_SEED_ORION'
  );
});

console.log('\n📊 Testing Service Registry');
const registry = new ServiceRegistry({
  healthCheckInterval: 30000,
  driftThreshold: 0.15
});

test('Service registry is created', () => {
  assertTrue(registry !== undefined, 'Registry should be created');
});

test('Can register a service', () => {
  registry.registerService(constellationConfig.constellation.hub);
  const services = registry.getServices();
  assertEqual(services.length, 1, 'Should have 1 registered service');
});

test('Can retrieve service by name', () => {
  const service = registry.getService('aurora-cloudbank-symbolic');
  assertTrue(service !== undefined, 'Service should be found');
  assertEqual(
    service.symbolicAnchor,
    'T1_CONSTELLATION_PRIME',
    'Service should have correct anchor'
  );
});

test('Can create memory seal', () => {
  const seal = registry.sealMemoryState();
  assertTrue(seal !== undefined, 'Seal should be created');
  assertTrue(seal.stateHash !== undefined, 'Seal should have hash');
  assertEqual(seal.anchor, 'T1_SERVICE_DISCOVERY', 'Seal should have correct anchor');
});

test('Can get health status', () => {
  const health = registry.getHealthStatus();
  assertTrue(Array.isArray(health), 'Health should be an array');
  assertTrue(health.length > 0, 'Health array should not be empty');
});

console.log('\n🎯 Testing Orchestrator');
const orchestrator = new Orchestrator({
  maxConcurrentTasks: 10,
  taskQueueSize: 1000
});

test('Orchestrator is created', () => {
  assertTrue(orchestrator !== undefined, 'Orchestrator should be created');
});

test('Can submit a task', () => {
  const taskId = orchestrator.submitTask(
    'test-task',
    'AuroraOS',
    { test: true },
    'normal',
    ['T1_CONSTELLATION_PRIME']
  );
  assertTrue(typeof taskId === 'string', 'Task ID should be a string');
  assertTrue(taskId.length > 0, 'Task ID should not be empty');
});

test('Can retrieve all tasks', () => {
  const tasks = orchestrator.getAllTasks();
  assertTrue(Array.isArray(tasks), 'Tasks should be an array');
  assertTrue(tasks.length > 0, 'Should have at least one task');
});

test('Can get task by ID', () => {
  const tasks = orchestrator.getAllTasks();
  const task = orchestrator.getTask(tasks[0].id);
  assertTrue(task !== undefined, 'Task should be found');
  assertEqual(task.id, tasks[0].id, 'Task ID should match');
});

test('Can get queue statistics', () => {
  const stats = orchestrator.getQueueStats();
  assertTrue(stats !== undefined, 'Stats should be defined');
  assertTrue(typeof stats.high === 'number', 'High priority count should be a number');
  assertTrue(typeof stats.normal === 'number', 'Normal priority count should be a number');
  assertTrue(typeof stats.low === 'number', 'Low priority count should be a number');
});

test('Can create memory snapshot', () => {
  const snapshot = orchestrator.createMemorySnapshot();
  assertTrue(snapshot !== undefined, 'Snapshot should be created');
  assertTrue(snapshot.snapshotHash !== undefined, 'Snapshot should have hash');
  assertEqual(snapshot.anchor, 'T1_ORCHESTRATOR_PRIME', 'Snapshot should have correct anchor');
});

test('Can submit high priority task', () => {
  const taskId = orchestrator.submitTask(
    'high-priority-task',
    'AuroraOS',
    { urgent: true },
    'high',
    ['T1_CONSTELLATION_PRIME']
  );
  assertTrue(typeof taskId === 'string', 'Task ID should be a string');
  
  const stats = orchestrator.getQueueStats();
  assertTrue(stats.high > 0 || stats.running > 0, 'High priority queue should have tasks or be running');
});

test('Can get tasks by status', () => {
  const pendingTasks = orchestrator.getTasksByStatus('pending');
  assertTrue(Array.isArray(pendingTasks), 'Pending tasks should be an array');
});

test('Can get tasks by service', () => {
  const auroraOSTasks = orchestrator.getTasksByService('AuroraOS');
  assertTrue(Array.isArray(auroraOSTasks), 'Service tasks should be an array');
  assertTrue(auroraOSTasks.length > 0, 'Should have tasks for AuroraOS');
});

// Summary
console.log('\n' + '='.repeat(50));
console.log(`✅ Passed: ${passed}`);
console.log(`❌ Failed: ${failed}`);
console.log(`📊 Total: ${passed + failed}`);
console.log('='.repeat(50));

if (failed > 0) {
  console.log('\n❌ Validation FAILED');
  process.exit(1);
} else {
  console.log('\n✅ All validations PASSED');
  console.log('\n🌟 Constellation Architecture is ready!');
  console.log('   Symbolic Anchor: T1_CONSTELLATION_PRIME');
  console.log('   Ethics Protocol: Picard_Delta_3');
  console.log('   Seed: EOS_SEED_ORION');
  process.exit(0);
}
