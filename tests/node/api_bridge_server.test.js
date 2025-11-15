import test from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';

import ApiBridgeServer from '../../src/bridge/api_bridge_server.js';

test('ApiBridgeServer starts and stops cleanly', async t => {
  const synchronizerStub = {
    getStatus: () => ({ status: 'STUBBED' }),
    getDriftReport: async () => ({ drift: 'none' }),
    synchronizeAllLayers: async () => ({ success: true })
  };

  const bridge = new ApiBridgeServer(0, synchronizerStub);
  t.after(() => bridge.stop());

  const server = bridge.start();
  await once(server, 'listening');

  assert.equal(bridge.status, 'OPERATIONAL');

  const address = server.address();
  assert.ok(address && typeof address.port === 'number' && address.port > 0);
});
