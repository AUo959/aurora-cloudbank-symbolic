// Test Suite: Ethical Checkpoint Module
// Validates doctrine-based system state verification (Picard_Delta_3 protocol)

import assert from 'node:assert/strict';
import { beforeEach, describe, it } from 'node:test';
import { EthicalCheckpoint } from '../../core/ethical-checkpoint.js';

describe('EthicalCheckpoint - Doctrine-Based Verification', () => {
  let checkpoint;
  let mockEthicsModule;

  beforeEach(() => {
    mockEthicsModule = {
      evaluate: (snapshot) => {
        if (snapshot.action === 'violate-prime-directive') {
          return {
            result: 'fail',
            issues: ['Prime Directive violation detected'],
          };
        }
        return { result: 'pass', issues: [] };
      },
    };
    checkpoint = new EthicalCheckpoint(mockEthicsModule);
  });

  it('should initialize with null lastCheck', () => {
    assert.equal(checkpoint.lastCheck, null);
    assert.equal(checkpoint.ethics, mockEthicsModule);
  });

  it('should validate passing system snapshot', () => {
    const snapshot = { action: 'help-civilians', intent: 'benevolent' };
    const isValid = checkpoint.validate(snapshot);
    assert.ok(isValid);
    assert.ok(checkpoint.lastCheck !== null);
    assert.equal(checkpoint.lastCheck.result, 'pass');
  });

  it('should detect ethical violations', () => {
    const snapshot = { action: 'violate-prime-directive' };
    const isValid = checkpoint.validate(snapshot);
    assert.equal(isValid, false);
    assert.equal(checkpoint.lastCheck.result, 'fail');
    assert.equal(checkpoint.lastCheck.issues.length, 1);
  });

  it('should record timestamp for validation checks', () => {
    const beforeTime = Date.now();
    checkpoint.validate({ action: 'test' });
    const afterTime = Date.now();
    assert.ok(checkpoint.lastCheck.timestamp >= beforeTime);
    assert.ok(checkpoint.lastCheck.timestamp <= afterTime);
  });

  it('should store issues from ethics evaluation', () => {
    const snapshot = { action: 'violate-prime-directive' };
    checkpoint.validate(snapshot);
    assert.deepEqual(checkpoint.lastCheck.issues, ['Prime Directive violation detected']);
  });

  it('should handle ethics modules without issues property', () => {
    mockEthicsModule.evaluate = () => ({ result: 'pass' });
    const isValid = checkpoint.validate({ action: 'test' });
    assert.ok(isValid);
    assert.deepEqual(checkpoint.lastCheck.issues, []);
  });

  it('should return lastCheck data', () => {
    checkpoint.validate({ action: 'test' });
    const lastCheck = checkpoint.getLastCheck();
    assert.ok(lastCheck !== null);
    assert.equal(lastCheck.result, 'pass');
    assert.ok(lastCheck.timestamp > 0);
  });

  it('should return null checkpointMeta before first validation', () => {
    const meta = checkpoint.checkpointMeta();
    assert.equal(meta, null);
  });

  it('should return formatted checkpoint metadata', () => {
    checkpoint.validate({ action: 'test' });
    const meta = checkpoint.checkpointMeta();
    assert.ok(meta !== null);
    assert.equal(meta.result, 'pass');
    assert.equal(meta.issueCount, 0);
    assert.ok(meta.time.includes('T')); // ISO format
  });

  it('should include issue count in metadata', () => {
    checkpoint.validate({ action: 'violate-prime-directive' });
    const meta = checkpoint.checkpointMeta();
    assert.equal(meta.issueCount, 1);
  });

  it('should update lastCheck on subsequent validations', () => {
    checkpoint.validate({ action: 'test1' });
    const firstTimestamp = checkpoint.lastCheck.timestamp;
    // Small delay to ensure different timestamp
    const delay = new Promise(resolve => setTimeout(resolve, 5));
    delay.then(() => {
      checkpoint.validate({ action: 'test2' });
      assert.ok(checkpoint.lastCheck.timestamp >= firstTimestamp);
    });
  });

  it('should integrate with Picard_Delta_3 protocol', () => {
    // Simulate Picard_Delta_3 ethics protocol
    const picardEthics = {
      evaluate: (snapshot) => {
        const violations = [];
        if (snapshot.intent === 'harm') violations.push('Intent to harm detected');
        if (snapshot.target === 'sentient') violations.push('Sentient target risk');
        return {
          result: violations.length === 0 ? 'pass' : 'fail',
          issues: violations,
        };
      },
    };
    const picardCheckpoint = new EthicalCheckpoint(picardEthics);
    
    // Test benevolent action
    assert.ok(picardCheckpoint.validate({ intent: 'protect', target: 'civilian' }));
    
    // Test harmful action
    assert.equal(picardCheckpoint.validate({ intent: 'harm', target: 'sentient' }), false);
    const meta = picardCheckpoint.checkpointMeta();
    assert.equal(meta.issueCount, 2);
  });

  it('should maintain audit trail of validations', () => {
    checkpoint.validate({ action: 'action1' });
    const check1 = checkpoint.getLastCheck();
    checkpoint.validate({ action: 'action2' });
    const check2 = checkpoint.getLastCheck();
    // Last check should be from action2
    assert.ok(check2.timestamp >= check1.timestamp);
  });
});
