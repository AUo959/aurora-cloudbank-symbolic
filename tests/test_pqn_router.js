const assert = require('assert');
process.env.PQN_OFFLINE_TEST = '1';
const { handleQuery } = require('../src/pqn/pqn_router');

(async () => {
  const result = await handleQuery('quantum testing');
  assert.strictEqual(result.anchor, 'EOS_SEED_ORION');
  assert.ok(Array.isArray(result.results));
  console.log('pqn router test passed');
})();
