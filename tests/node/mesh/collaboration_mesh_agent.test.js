import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { loadCommonJsModule } from '../utils/cjs-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function createLoggerStubs() {
  const systemEntries = [];
  const bridgeEntries = [];
  const ethicsEntries = [];

  return {
    stubs: {
      systemLogger: {
        info: (message, metadata = {}) => {
          systemEntries.push({ level: 'info', message, metadata });
        },
        error: (message, metadata = {}) => {
          systemEntries.push({ level: 'error', message, metadata });
        }
      },
      bridgeLogger: {
        bridge: (message, metadata = {}) => {
          bridgeEntries.push({ level: 'bridge', message, metadata });
        }
      },
      ethicsLogger: {
        ethics: (message, metadata = {}) => {
          ethicsEntries.push({ level: 'ethics', message, metadata });
        }
      }
    },
    systemEntries,
    bridgeEntries,
    ethicsEntries
  };
}

function loadMeshAgentsWithStubs() {
  const loggerStubs = createLoggerStubs();
  const modulePath = path.join(__dirname, '..', '..', '..', 'src', 'core', 'mesh_agent.js');
  const meshModule = loadCommonJsModule(modulePath, {
    requireMap: new Map([
      [
        '../utils/aurora_logger.js',
        {
          systemLogger: loggerStubs.stubs.systemLogger,
          bridgeLogger: loggerStubs.stubs.bridgeLogger,
          ethicsLogger: loggerStubs.stubs.ethicsLogger
        }
      ]
    ])
  });

  return { ...meshModule, loggerStubs };
}

test('CollaborationMeshAgent messages use the agent id as the sender', async () => {
  const { CollaborationMeshAgent } = loadMeshAgentsWithStubs();
  const agent = new CollaborationMeshAgent('ARCHY');

  const message = await agent.sendMessage('OPPY', 'Testing vector routing');

  assert.equal(agent.id, 'ARCHY');
  assert.equal(agent.agentId, 'ARCHY');
  assert.equal(message.from, 'ARCHY');
});

test('CollaborationMeshAgent handshake logs include the resolved agent id', async () => {
  const { CollaborationMeshAgent, loggerStubs } = loadMeshAgentsWithStubs();
  const agent = new CollaborationMeshAgent('ARCHY');

  await agent.handshake();

  const handshakeLog = loggerStubs.systemEntries.find(entry =>
    entry.message.includes('Starting handshake sequence')
  );

  assert.ok(handshakeLog, 'Expected handshake log entry to be recorded');
  assert.ok(
    handshakeLog.message.includes('ARCHY'),
    'Handshake log should reference the resolved agent id'
  );
});
