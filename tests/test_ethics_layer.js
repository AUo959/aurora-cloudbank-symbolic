const assert = require('assert');
const { ethicsCheck } = require('../auth/ethics_layer');

assert.strictEqual(ethicsCheck({ name: 'launch' }), true, 'valid command should return true');
assert.strictEqual(ethicsCheck(), false, 'missing command should return false');
assert.strictEqual(ethicsCheck({}), false, 'command without name should return false');
assert.strictEqual(ethicsCheck({ name: 42 }), false, 'command name must be a non-empty string');

console.log('ethics layer tests passed');
