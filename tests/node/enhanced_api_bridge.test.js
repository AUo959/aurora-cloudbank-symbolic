import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { loadCommonJsModule } from './utils/cjs-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const normalizeMetadata = candidate => {
  if (candidate && typeof candidate === 'object' && !Array.isArray(candidate)) {
    return candidate;
  }
  return {};
};

const createBridgeLoggerMock = collected => ({
  bridge(message, fromLayerOrMeta, toLayerMaybe, metadataMaybe) {
    let metadata = {};
    if (metadataMaybe && typeof metadataMaybe === 'object') {
      metadata = metadataMaybe;
    } else if (fromLayerOrMeta && typeof fromLayerOrMeta === 'object') {
      metadata = fromLayerOrMeta;
    }
    collected.push({ level: 'bridge', message, metadata: normalizeMetadata(metadata) });
  },
  error(message, metadata) {
    collected.push({ level: 'error', message, metadata: normalizeMetadata(metadata) });
  },
  info(message, metadata) {
    collected.push({ level: 'info', message, metadata: normalizeMetadata(metadata) });
  },
  warn(message, metadata) {
    collected.push({ level: 'warn', message, metadata: normalizeMetadata(metadata) });
  }
});

const createSystemLoggerMock = () => ({
  info() {},
  error() {},
  warn() {},
  debug() {}
});

class StubMeshFederation {
  constructor() {
    this.relayMessage = async () => ({ success: true, status: 'mocked', messageId: 'mocked' });
  }

  getSystemStatus() {
    return { status: 'mocked' };
  }
}

const loadBridgeModule = loggerCalls => {
  const bridgeLogger = createBridgeLoggerMock(loggerCalls);
  const systemLogger = createSystemLoggerMock();

  const requireMap = new Map([
    ['../utils/aurora_logger.js', { systemLogger, bridgeLogger }],
    [path.resolve(__dirname, '..', '..', 'src', 'utils', 'aurora_logger.js'), { systemLogger, bridgeLogger }],
    ['../core/mesh_agent.js', { MeshFederation: StubMeshFederation }],
    [path.resolve(__dirname, '..', '..', 'src', 'core', 'mesh_agent.js'), { MeshFederation: StubMeshFederation }]
  ]);

  return loadCommonJsModule(
    path.join(__dirname, '..', '..', 'src', 'bridge', 'enhanced_api_bridge.js'),
    { requireMap }
  );
};

const createResponse = () => {
  return {
    statusCode: 200,
    body: null,
    status(code) {
      this.statusCode = code;
      return this;
    },
    json(payload) {
      this.body = payload;
      return this;
    }
  };
};

test('connectCustomGpt redacts activation phrases on invalid attempts', async () => {
  const loggerCalls = [];
  const { EnhancedApiBridge } = loadBridgeModule(loggerCalls);
  const bridge = new EnhancedApiBridge();

  const req = {
    params: { agentId: 'ARCHY' },
    body: { activationPhrase: 'INVALID_PHRASE', capabilities: ['telemetry'] }
  };
  const res = createResponse();

  await bridge.connectCustomGpt(req, res);

  assert.equal(res.statusCode, 401);
  assert.equal(res.body.error, 'Invalid activation phrase');
  assert.equal(res.body.agentId, 'ARCHY');
  assert.ok(!JSON.stringify(res.body).includes('ORION_ARCHY_RELAY_ACTIVATE//'));

  const serializedLogs = loggerCalls.map(entry => JSON.stringify(entry));
  for (const record of serializedLogs) {
    assert.ok(!record.includes('ORION_ARCHY_RELAY_ACTIVATE//'));
  }

  const errorLog = loggerCalls.find(
    entry => entry.level === 'error' && entry.message.includes('Invalid activation attempt')
  );
  assert.ok(errorLog, 'expected invalid activation attempt to be logged');
  assert.equal(errorLog.metadata.phraseRedacted, true);
});
