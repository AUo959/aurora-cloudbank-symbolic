import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { loadCommonJsModule } from './utils/cjs-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test('MeshAgent#setLive logs sanitized activation metadata', async () => {
  const bridgeEvents = [];

  const stubBridgeLogger = {
    info: () => {},
    warn: () => {},
    error: () => {},
    bridge: (message, metadata = {}) => {
      bridgeEvents.push({ message, metadata });
    }
  };

  const stubSystemLogger = {
    info: () => {},
    warn: () => {},
    error: () => {}
  };

  const stubEthicsLogger = {
    info: () => {},
    warn: () => {},
    error: () => {}
  };

  const { MeshAgent } = loadCommonJsModule(
    path.join(__dirname, '..', '..', 'src', 'core', 'mesh_agent.js'),
    {
      requireMap: new Map([
        [
          '../utils/aurora_logger.js',
          {
            systemLogger: stubSystemLogger,
            bridgeLogger: stubBridgeLogger,
            ethicsLogger: stubEthicsLogger
          }
        ]
      ])
    }
  );

  const activationSecret = 'ORION_TEST_AGENT_ACTIVATE//';

  const agent = new MeshAgent(
    'TEST_MESH_AGENT',
    'Test Mesh Role',
    '/api/mesh/test',
    activationSecret
  );

  bridgeEvents.length = 0;

  await agent.setLive();

  assert.equal(agent.status, 'LIVE');
  assert.equal(agent.meshConnected, true);
  assert.ok(bridgeEvents.length > 0, 'bridge logger should be invoked');

  const { metadata } = bridgeEvents[bridgeEvents.length - 1];
  const serializedMetadata = JSON.stringify(metadata);

  assert.ok(!serializedMetadata.includes(activationSecret), 'activation phrase leaked to logs');
  assert.strictEqual(metadata.activationPhrase, undefined);
  assert.ok(metadata.activation, 'sanitized activation metadata missing');
  assert.strictEqual(metadata.activation.hasActivationPhrase, true);
  assert.ok(typeof metadata.activation.activationHashPreview === 'string');
  assert.notStrictEqual(metadata.activation.activationHashPreview, activationSecret);
  assert.ok(metadata.activation.activationHashPreview.length > 0);
});
