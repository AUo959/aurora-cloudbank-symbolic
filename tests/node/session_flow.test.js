import test from 'node:test';
import assert from 'node:assert/strict';

import {
  createSession,
  runFlow,
  shareSession,
  forkSession,
  defaultRedaction
} from '../../src/utils/session_flow.js';

test('session creation includes anchors and default redaction', () => {
  const session = createSession({
    full_name: 'Grace Hopper',
    preference: 'quantum-memory',
    anchor_seed: 'T1-THREAD-BRIDGE'
  });

  assert.ok(session.sessionId);
  assert.equal(session.state.full_name, defaultRedaction.mask);
  assert.equal(session.metadata_anchor.anchor_seed, 'T1-THREAD-BRIDGE');
  assert.equal(session.state.pii_redaction.strategy, 'mask');
});

test('run flow preserves anchor and applies continuity seal', () => {
  const session = createSession({ preference: 'decision-gate' });
  const run = runFlow(session, [
    { name: 'quantum', action: 'prepare' },
    { name: 'bridge', action: 'transfer' }
  ]);

  assert.equal(run.anchor_seed, session.metadata_anchor.anchor_seed);
  assert.equal(run.steps.length, 2);
  assert.match(run.continuity_seal, /^[0-9a-f]{16}$/);
});

test('share and fork paths keep PII redacted', () => {
  const session = createSession({
    full_name: 'Niels Bohr',
    email: 'niels.bohr@example.com',
    preference: 'decision-lattice'
  });

  const shared = shareSession(session);
  assert.equal(shared.state.full_name, defaultRedaction.mask);
  assert.equal(shared.state.email, defaultRedaction.mask);

  const forked = forkSession(session, shared.shareToken);
  assert.notEqual(forked.sessionId, session.sessionId);
  assert.equal(forked.state.pii_redaction.strategy, 'mask');
  assert.equal(forked.state.metadata_anchor.anchor_seed, session.metadata_anchor.anchor_seed);
  assert.equal(forked.forked_from, session.sessionId);
});
