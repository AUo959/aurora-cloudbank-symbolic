// Test Suite: Drift-Aware Symbolic Agent
// Validates real-time symbolic state drift monitoring and adaptive responses

import assert from 'node:assert/strict';
import { beforeEach, describe, it } from 'node:test';
import { DriftAwareAgent } from '../../core/drift-aware-agent.js';

describe('DriftAwareAgent - Real-Time Drift Monitoring', () => {
  let agent;
  let mockMemory;

  beforeEach(() => {
    mockMemory = {
      anchorHash: () => 'ANCHOR_HASH_12345',
    };
    agent = new DriftAwareAgent('test-agent-001', mockMemory, 0.05);
  });

  it('should initialize with stable state', () => {
    assert.equal(agent.id, 'test-agent-001');
    assert.equal(agent.state, 'stable');
    assert.equal(agent.driftThreshold, 0.05);
    assert.equal(agent.memory, mockMemory);
  });

  it('should calculate drift between anchor and current hash', () => {
    const anchorHash = 'ABCDEFGHIJ';
    const currentHash = 'ABXDEFGHIJ'; // 1 char different
    const drift = agent.calculateDrift(anchorHash, currentHash);
    assert.equal(drift, 0.1); // 1/10 = 0.1
  });

  it('should detect zero drift for identical hashes', () => {
    const hash = 'IDENTICAL_HASH';
    const drift = agent.calculateDrift(hash, hash);
    assert.equal(drift, 0);
  });

  it('should handle mismatched hash lengths', () => {
    const drift = agent.calculateDrift('SHORT', 'MUCH_LONGER_HASH');
    assert.ok(drift >= 0 && drift <= 1);
  });

  it('should return 1.0 drift for invalid input types', () => {
    assert.equal(agent.calculateDrift(null, 'hash'), 1);
    assert.equal(agent.calculateDrift('hash', undefined), 1);
    assert.equal(agent.calculateDrift(123, 'hash'), 1);
  });

  it('should assess drift and update state to drifting', () => {
    const currentHash = 'XXXXX_HASH_12345'; // High drift
    const drift = agent.assessDrift(currentHash);
    assert.ok(drift > agent.driftThreshold);
    assert.equal(agent.state, 'drifting');
  });

  it('should assess drift and maintain stable state', () => {
    const currentHash = 'ANCHOR_HASH_12345'; // Identical, zero drift
    const drift = agent.assessDrift(currentHash);
    assert.equal(drift, 0);
    assert.equal(agent.state, 'stable');
  });

  it('should respond to drift with onDrift action', () => {
    agent.state = 'drifting';
    let driftHandlerCalled = false;
    const actionMap = {
      onDrift: (id) => {
        driftHandlerCalled = true;
        return `Handled drift for ${id}`;
      },
    };
    const result = agent.respondToDrift(actionMap);
    assert.ok(driftHandlerCalled);
    assert.equal(result, 'Handled drift for test-agent-001');
  });

  it('should respond to stable state with onStable action', () => {
    agent.state = 'stable';
    let stableHandlerCalled = false;
    const actionMap = {
      onStable: (id) => {
        stableHandlerCalled = true;
        return `Stable: ${id}`;
      },
    };
    const result = agent.respondToDrift(actionMap);
    assert.ok(stableHandlerCalled);
    assert.equal(result, 'Stable: test-agent-001');
  });

  it('should return null when no matching action handler', () => {
    agent.state = 'drifting';
    const result = agent.respondToDrift({ onStable: () => 'stable' });
    assert.equal(result, null);
  });

  it('should return null for empty action map', () => {
    const result = agent.respondToDrift({});
    assert.equal(result, null);
  });

  it('should return status with id, state, and anchor', () => {
    const status = agent.status();
    assert.equal(status.id, 'test-agent-001');
    assert.equal(status.state, 'stable');
    assert.equal(status.anchor, 'ANCHOR_HASH_12345');
  });

  it('should update status after drift assessment', () => {
    agent.assessDrift('DRIFTED_HASH_99999');
    const status = agent.status();
    assert.equal(status.state, 'drifting');
  });

  it('should integrate with NEXUS entropy state monitoring', () => {
    // Simulate NEXUS integration pattern
    const nexusMemory = {
      anchorHash: () => 'NEXUS_ANCHOR_T6',
    };
    const nexusAgent = new DriftAwareAgent('nexus-001', nexusMemory, 0.03);
    const drift = nexusAgent.assessDrift('NEXUS_ANCHOR_T6');
    assert.equal(drift, 0);
    assert.equal(nexusAgent.state, 'stable');
  });
});
