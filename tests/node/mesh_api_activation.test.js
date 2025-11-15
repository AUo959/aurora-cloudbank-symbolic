import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import express from 'express';

import { loadCommonJsModule } from './utils/cjs-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test('mesh activation logging redacts activation phrases', async () => {
  const bridgeEvents = [];
  const stubBridgeLogger = {
    bridge(message, metadata) {
      bridgeEvents.push({ message, metadata });
    }
  };

  const stubSystemLogger = {
    info() {},
    error() {}
  };

  class MockAgent {
    constructor(id) {
      this.id = id;
      this.status = 'LIVE';
      this.role = 'Sentinel';
      this.ethicsStatus = 'Nominal';
      this.driftLevel = 0;
      this.lastSync = Date.now();
      this.meshConnected = true;
      this.apiEndpoint = 'mock://endpoint';
      this.sessionId = 'session-anchor';
    }

    async handshake() {
      this.status = 'LIVE';
    }
  }

  class MockMeshFederation {
    constructor() {
      this.status = 'ACTIVE';
      this.agents = new Map([[
        'agent-7',
        new MockAgent('agent-7')
      ]]);
    }

    async initializeMesh() {
      return this;
    }

    getStatus() {
      return {
        meshStatus: this.status,
        agentCount: this.agents.size
      };
    }
  }

  const meshModule = loadCommonJsModule(
    path.join(__dirname, '..', '..', 'src', 'api', 'mesh_api.js'),
    {
      requireMap: new Map([
        [
          '../core/mesh_agent.js',
          {
            MESH_CONFIG: {
              activationPhrases: { 'agent-7': 'super-secret-phrase' },
              relayApiEndpoints: [],
              version: '1.0.0-test',
              anchorSeed: 'T1-anchor',
              ethicsProtocol: 'Picard_Delta_3',
              constellation: [],
              commProtocol: 'quantum-mesh'
            },
            MeshFederation: MockMeshFederation
          }
        ],
        [
          '../utils/aurora_logger.js',
          {
            systemLogger: stubSystemLogger,
            bridgeLogger: stubBridgeLogger
          }
        ]
      ])
    }
  );

  const app = express();
  app.use(express.json());
  app.use('/api/mesh', meshModule.router);

  const server = app.listen(0);
  await new Promise(resolve => server.once('listening', resolve));

  try {
    const { port } = server.address();
    const response = await fetch(`http://127.0.0.1:${port}/api/mesh/agents/agent-7/activate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ activationPhrase: 'super-secret-phrase' })
    });

    const body = await response.json();

    assert.equal(response.status, 200);
    assert.equal(body.success, true);
    assert.equal(body.agent?.activated, true);
    assert.ok(bridgeEvents.length >= 1, 'bridge logger should capture activation event');

    const activationEvent = bridgeEvents.at(-1);
    const serializedMetadata = JSON.stringify(activationEvent.metadata);
    assert.ok(!serializedMetadata.includes('super-secret-phrase'), 'metadata should not leak the raw activation phrase');
    assert.ok(activationEvent.metadata.activationVerification, 'activation verification metadata is present');
    assert.equal(activationEvent.metadata.activationVerification.method, 'sha256');
    assert.match(activationEvent.metadata.activationVerification.digest, /^[0-9a-f]{64}$/i);
  } finally {
    await new Promise((resolve, reject) => {
      server.close(error => (error ? reject(error) : resolve()));
    });
  }
});
