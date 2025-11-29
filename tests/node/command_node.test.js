/**
 * Tests for unified CommandNode architecture
 * Tests all consolidated functionality from 4 previous implementations
 */

import { test, describe, beforeEach } from 'node:test';
import assert from 'node:assert';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Import the unified CommandNode
import CommandNode, {
  CommandRouter,
  ethicsCheck,
  anchorResolve,
  validateEthics,
  isEncryptionAvailable,
  ThreadcoreAdapter,
  PatchweaverAdapter,
  ZipwizAdapter,
} from '../../src/core/command_node/index.js';

// Test logs directory
const TEST_LOGS_DIR = path.join(process.cwd(), 'logs', 'test');

describe('CommandNode - Unified Architecture', () => {
  let commandNode;

  beforeEach(() => {
    // Create fresh instance for each test
    commandNode = new CommandNode({
      logsDir: TEST_LOGS_DIR,
      enableEncryption: false, // Disable encryption for tests (no key in test env)
    });
  });

  // =====================================================
  // Basic Instance Tests
  // =====================================================

  test('creates instance with default options', () => {
    const node = new CommandNode();
    assert.ok(node);
    assert.strictEqual(node.nodeId, 'AURORA_COMMAND_NODE');
    assert.ok(node.version.startsWith('v'));
  });

  test('creates instance with custom options', () => {
    const node = new CommandNode({
      nodeId: 'CUSTOM_NODE',
      anchorSeed: 'CUSTOM_SEED',
    });
    assert.strictEqual(node.nodeId, 'CUSTOM_NODE');
    assert.strictEqual(node.anchorSeed, 'CUSTOM_SEED');
  });

  // =====================================================
  // Simple Routing Tests (aurora_command_router.js compatibility)
  // =====================================================

  test('routeCommand returns valid result', () => {
    const result = commandNode.routeCommand('TEST_COMMAND', { data: 'test' });

    assert.ok(result.commandId);
    assert.strictEqual(result.status, 'routed');
    assert.ok(result.timestamp);
  });

  test('initWebEnvironment routes properly', () => {
    const result = commandNode.initWebEnvironment({ step: 'test' });

    assert.ok(result.commandId);
    assert.strictEqual(result.status, 'routed');
  });

  test('coordinateMultiAgent routes with agents', () => {
    const result = commandNode.coordinateMultiAgent(['AGENT_1', 'AGENT_2']);

    assert.ok(result.commandId);
    assert.strictEqual(result.status, 'routed');
  });

  test('establishQuantumAnchor routes properly', () => {
    const result = commandNode.establishQuantumAnchor({ type: 'test' });

    assert.ok(result.commandId);
    assert.strictEqual(result.status, 'routed');
  });

  // =====================================================
  // Ethics Validation Tests (src/core/command_node.js compatibility)
  // =====================================================

  test('executeCommand passes for valid commands', () => {
    const command = { name: 'test_action', context: 'TEST' };
    const result = commandNode.executeCommand(command);

    assert.ok(result.includes('executed'));
    assert.ok(result.includes('ANCHOR_TEST_HASH'));
  });

  test('executeCommand throws for forbidden commands', () => {
    const command = { name: 'blacklist', context: 'TEST' };

    assert.throws(() => {
      commandNode.executeCommand(command);
    }, /Ethics violation detected/);
  });

  test('validateCommand returns validation result', () => {
    const command = { name: 'test_action' };
    const result = commandNode.validateCommand(command);

    assert.strictEqual(result.valid, true);
    assert.ok(result.protocol);
    assert.ok(result.anchor);
  });

  test('validateCommand detects invalid commands', () => {
    const command = { name: 'override' };
    const result = commandNode.validateCommand(command);

    assert.strictEqual(result.valid, false);
  });

  // =====================================================
  // Layer Dispatch Tests (src/system/aurora_command_router.js compatibility)
  // =====================================================

  test('dispatch routes to L1 layer', async () => {
    const result = await commandNode.dispatch({
      agent: 'ARCHY',
      layer: 'L1_ONLY',
      command: { type: 'test' },
    });

    assert.strictEqual(result.success, true);
    assert.strictEqual(result.layer, 'L1');
    assert.strictEqual(result.agentId, 'ARCHY');
  });

  test('dispatch routes to L2 layer', async () => {
    const result = await commandNode.dispatch({
      agent: 'DAEDALUS',
      layer: 'L2_L3_BRIDGE',
      command: { type: 'test' },
    });

    assert.strictEqual(result.success, true);
    assert.strictEqual(result.layer, 'L2');
  });

  test('dispatch routes to L3 layer', async () => {
    const result = await commandNode.dispatch({
      agent: 'Glyphon',
      layer: 'L3_SYMBOLIC',
      command: { type: 'validation' },
    });

    assert.strictEqual(result.success, true);
    assert.strictEqual(result.layer, 'L3');
  });

  test('dispatch handles unknown agent with default response', async () => {
    const result = await commandNode.dispatch({
      agent: 'UNKNOWN_AGENT',
      layer: 'L2_L3_BRIDGE',
      command: { type: 'test' },
    });

    assert.strictEqual(result.success, true);
    assert.strictEqual(result.default, true);
  });

  test('dispatch fails for missing agent', async () => {
    const result = await commandNode.dispatch({
      layer: 'L1_ONLY',
      command: { type: 'test' },
    });

    assert.strictEqual(result.success, false);
    assert.ok(result.error.includes('Missing agent'));
  });

  test('routeL3Validation dispatches correctly', async () => {
    const result = await commandNode.routeL3Validation('Axiomera', {
      data: 'test',
    });

    assert.strictEqual(result.success, true);
    assert.strictEqual(result.agentId, 'Axiomera');
  });

  test('routeEmergency dispatches to SHADOWFAX', async () => {
    const result = await commandNode.routeEmergency({
      type: 'alert',
      message: 'test',
    });

    assert.strictEqual(result.success, true);
    assert.strictEqual(result.agentId, 'SHADOWFAX');
  });

  // =====================================================
  // THREADCORE Integration Tests (services/command_node/ compatibility)
  // =====================================================

  test('initializeAuroraCore initializes components', () => {
    const result = commandNode.initializeAuroraCore();

    assert.strictEqual(result.status, 'initialized');
    assert.ok(result.components);
    assert.strictEqual(result.components.threadcore, true);
    assert.strictEqual(result.components.patchweaver, true);
  });

  test('relayCommand handles SEED_ANCHOR', () => {
    commandNode.initializeAuroraCore();
    const result = commandNode.relayCommand('SEED_ANCHOR', { data: 'seed' });

    assert.strictEqual(result.status, 'seeded');
  });

  test('relayCommand handles UPDATE_THREAD', () => {
    commandNode.initializeAuroraCore();
    const result = commandNode.relayCommand('UPDATE_THREAD', { data: 'update' });

    assert.strictEqual(result.status, 'updated');
  });

  test('relayCommand handles REFLECT', () => {
    commandNode.initializeAuroraCore();
    const result = commandNode.relayCommand('REFLECT');

    assert.strictEqual(result.status, 'reflected');
    assert.ok(result.state);
  });

  test('relayCommand handles unknown commands', () => {
    const result = commandNode.relayCommand('UNKNOWN_CMD', {});

    assert.strictEqual(result.status, 'unknown_command');
  });

  // =====================================================
  // Status and Metrics Tests
  // =====================================================

  test('getStatus returns complete status', () => {
    const status = commandNode.getStatus();

    assert.ok(status.nodeId);
    assert.ok(status.version);
    assert.ok(status.router);
    assert.ok(status.diagnostics);
    assert.ok(status.components);
  });

  test('getMetrics returns routing metrics', () => {
    // Perform some commands first
    commandNode.routeCommand('TEST', {});
    commandNode.routeCommand('TEST2', {});

    const metrics = commandNode.getMetrics();

    assert.ok(metrics.totalCommands >= 2);
    assert.ok(metrics.successRate >= 0);
  });

  // =====================================================
  // Route Registration Tests
  // =====================================================

  test('registerRoute adds custom route', async () => {
    const customHandler = async (cmd) => ({
      success: true,
      custom: true,
      cmd,
    });

    commandNode.registerRoute('L1', 'CUSTOM_AGENT', customHandler);

    const result = await commandNode.dispatch({
      agent: 'CUSTOM_AGENT',
      layer: 'L1_ONLY',
      command: { type: 'test' },
    });

    assert.strictEqual(result.success, true);
    assert.strictEqual(result.custom, true);
  });

  test('unregisterRoute removes route', () => {
    commandNode.registerRoute('L1', 'TEMP_AGENT', async () => ({}));
    const removed = commandNode.unregisterRoute('L1', 'TEMP_AGENT');

    assert.strictEqual(removed, true);
  });
});

// =====================================================
// Ethics Module Tests
// =====================================================

describe('Ethics Module', () => {
  test('ethicsCheck passes valid commands', () => {
    assert.strictEqual(ethicsCheck({ name: 'test' }), true);
    assert.strictEqual(ethicsCheck({ action: 'deploy' }), true);
  });

  test('ethicsCheck fails forbidden commands', () => {
    assert.strictEqual(ethicsCheck({ name: 'blacklist' }), false);
    assert.strictEqual(ethicsCheck({ name: 'override' }), false);
    assert.strictEqual(ethicsCheck({ name: 'BLACKLIST' }), false);
  });

  test('anchorResolve generates anchor hash', () => {
    const anchor = anchorResolve('TEST');
    assert.strictEqual(anchor, 'ANCHOR_TEST_HASH');
  });

  test('anchorResolve uses AUTO for empty context', () => {
    const anchor = anchorResolve();
    assert.strictEqual(anchor, 'ANCHOR_AUTO_HASH');
  });

  test('validateEthics returns complete result', () => {
    const result = validateEthics({ name: 'test' });

    assert.strictEqual(result.valid, true);
    assert.ok(result.protocol);
    assert.ok(result.anchor);
    assert.ok(result.timestamp);
    assert.ok(result.details);
  });
});

// =====================================================
// THREADCORE Adapter Tests
// =====================================================

describe('THREADCORE Adapters', () => {
  test('ThreadcoreAdapter initializes correctly', () => {
    const tc = new ThreadcoreAdapter();
    assert.strictEqual(tc.isInitialized(), false);

    tc.init();
    assert.strictEqual(tc.isInitialized(), true);
  });

  test('ThreadcoreAdapter handles seed/update/reflect', () => {
    const tc = new ThreadcoreAdapter();
    tc.init();

    const seedResult = tc.seed({ data: 'test' });
    assert.strictEqual(seedResult.status, 'seeded');

    const updateResult = tc.update({ data: 'update' });
    assert.strictEqual(updateResult.status, 'updated');

    const reflectResult = tc.reflect();
    assert.strictEqual(reflectResult.status, 'reflected');
  });

  test('PatchweaverAdapter connects/disconnects', () => {
    const pw = new PatchweaverAdapter();
    assert.strictEqual(pw.isConnected(), false);

    pw.connect();
    assert.strictEqual(pw.isConnected(), true);

    pw.disconnect();
    assert.strictEqual(pw.isConnected(), false);
  });

  test('ZipwizAdapter handles beacons', () => {
    const zw = new ZipwizAdapter();

    zw.pingBeacon('test_beacon');
    const status = zw.getBeaconStatus('test_beacon');

    assert.strictEqual(status.active, true);
    assert.ok(status.lastPing);
  });

  test('ZipwizAdapter lists beacons', () => {
    const zw = new ZipwizAdapter();
    zw.pingBeacon('beacon1');
    zw.pingBeacon('beacon2');

    const beacons = zw.listBeacons();
    assert.strictEqual(beacons.length, 2);
  });
});

// =====================================================
// CommandRouter Tests
// =====================================================

describe('CommandRouter', () => {
  let router;

  beforeEach(() => {
    router = new CommandRouter({ logsDir: TEST_LOGS_DIR });
  });

  test('getStatus returns router info', () => {
    const status = router.getStatus();

    assert.ok(status.routerId);
    assert.ok(status.version);
    assert.ok(status.routingTables);
    assert.ok(status.clearanceLevels);
  });

  test('getMetrics calculates success rate', () => {
    router.routeCommand('TEST', {});

    const metrics = router.getMetrics();
    assert.ok(metrics.successRate >= 0);
  });

  test('routeCommand generates UUID', () => {
    const result1 = router.routeCommand('TEST', {});
    const result2 = router.routeCommand('TEST', {});

    assert.notStrictEqual(result1.commandId, result2.commandId);
  });
});

// =====================================================
// Encryption Module Tests (when available)
// =====================================================

describe('Encryption Module', () => {
  test('isEncryptionAvailable returns boolean', () => {
    const available = isEncryptionAvailable();
    assert.strictEqual(typeof available, 'boolean');
  });
});
