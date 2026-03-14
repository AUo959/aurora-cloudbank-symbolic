const assert = require('assert');

const meshApi = require('../src/api/mesh_api.js');
const { EnhancedApiBridge } = require('../src/bridge/enhanced_api_bridge.js');

function createMockResponse() {
  return {
    statusCode: 200,
    payload: null,
    status(code) {
      this.statusCode = code;
      return this;
    },
    json(payload) {
      this.payload = payload;
      return this;
    }
  };
}

async function run() {
  const publicConfig = meshApi.getPublicMeshConfig();

  assert.strictEqual(publicConfig.activationPhraseRequired, true, 'mesh config should require activation phrases');
  assert.deepStrictEqual(
    publicConfig.supportedAgents.sort(),
    Object.keys(meshApi.MESH_CONFIG.activationPhrases).sort(),
    'mesh config should expose supported agents only'
  );
  assert.ok(!Object.prototype.hasOwnProperty.call(publicConfig, 'activationPhrases'), 'mesh config should not expose activation phrase keys');
  assert.strictEqual(meshApi.isValidActivationPhrase('ARCHY', 'ORION_ARCHY_RELAY_ACTIVATE//'), true, 'valid phrase should pass');
  assert.strictEqual(meshApi.isValidActivationPhrase('ARCHY', ''), false, 'empty phrase should fail');

  const bridge = new EnhancedApiBridge();
  bridge.performZipwizHandshake = async () => ({
    success: true,
    log: [],
    driftLock: 0,
    sequence: ['ZIPWIZ_BEACON']
  });
  bridge.meshFederation = {
    relayMessage: async payload => ({
      success: true,
      messageId: 'relay-1',
      status: 'relayed',
      payload
    }),
    getSystemStatus: () => ({ status: 'ok' })
  };

  let response = createMockResponse();
  await bridge.connectCustomGpt(
    {
      params: { agentId: 'ARCHY' },
      body: { capabilities: ['relay'] },
      headers: {}
    },
    response
  );
  assert.strictEqual(response.statusCode, 401, 'missing phrase should be rejected');
  assert.strictEqual(response.payload.error, 'Activation phrase required');

  response = createMockResponse();
  await bridge.connectCustomGpt(
    {
      params: { agentId: 'ARCHY' },
      body: {
        activationPhrase: 'ORION_ARCHY_RELAY_ACTIVATE//',
        capabilities: ['relay']
      },
      headers: {}
    },
    response
  );
  assert.strictEqual(response.statusCode, 200, 'valid phrase should connect');
  assert.ok(typeof response.payload.sessionToken === 'string' && response.payload.sessionToken.length >= 32, 'connect should issue a session token');

  const sessionToken = response.payload.sessionToken;

  response = createMockResponse();
  bridge.getAgentStatus(
    {
      params: { agentId: 'ARCHY' },
      headers: {}
    },
    response
  );
  assert.strictEqual(response.statusCode, 401, 'status should require a bridge session token');
  assert.strictEqual(response.payload.error, 'Missing bridge session token');

  response = createMockResponse();
  await bridge.relayMessage(
    {
      params: { agentId: 'ARCHY' },
      headers: { authorization: `Bearer ${sessionToken}` },
      body: { message: 'test message' }
    },
    response
  );
  assert.strictEqual(response.statusCode, 200, 'relay should succeed with a valid session token');
  assert.strictEqual(response.payload.success, true);

  response = createMockResponse();
  await bridge.disconnectAgent(
    {
      params: { agentId: 'ARCHY' },
      headers: { authorization: 'Bearer wrong-token' }
    },
    response
  );
  assert.strictEqual(response.statusCode, 401, 'disconnect should reject an invalid session token');
}

run().catch(error => {
  process.stderr.write(`${error.stack}\n`);
  process.exitCode = 1;
});
