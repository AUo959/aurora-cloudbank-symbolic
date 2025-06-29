const assert = require('assert');
const { loadDiagnostics, saveDiagnostics } = require('../src/core/diagnostics');
const { runPASCycle } = require('../src/core/parasym_activation');

let diag = loadDiagnostics();
diag.symbolicDrift = 0.5;
diag.lastAnchorSync = Date.now() - (11 * 60 * 1000);
diag.ethicsFlags = ['violation'];
diag.load = 10;
saveDiagnostics(diag);

runPASCycle();

diag = loadDiagnostics();
assert.ok(diag.symbolicDrift <= 0.5, 'drift should not increase');
assert.strictEqual(diag.ethicsFlags.length, 0, 'ethics flags should be cleared');
assert.ok(Date.now() - diag.lastAnchorSync < 1000, 'anchor should be resynced');
console.log('PAS cycle test passed');
