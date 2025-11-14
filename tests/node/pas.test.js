import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { loadCommonJsModule } from './utils/cjs-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const diagnosticsModulePromise = import('../../src/core/diagnostics.js');
const parasymPath = path.join(
  __dirname,
  '..',
  '..',
  'src',
  'core',
  'parasym_activation.js'
);

async function buildRequireMap() {
  const diagnosticsModule = await diagnosticsModulePromise;
  const diagnosticsShim = {
    loadDiagnostics: diagnosticsModule.loadDiagnostics,
    saveDiagnostics: diagnosticsModule.saveDiagnostics,
    DIAG_PATH: diagnosticsModule.DIAG_PATH,
  };

  const baseDir = path.dirname(parasymPath);
  const mappings = new Map();
  mappings.set('./diagnostics', diagnosticsShim);
  mappings.set('../core/diagnostics', diagnosticsShim);
  mappings.set(path.resolve(baseDir, 'diagnostics'), diagnosticsShim);
  mappings.set(path.resolve(baseDir, 'diagnostics.js'), diagnosticsShim);
  mappings.set(path.resolve(baseDir, 'diagnostics.mjs'), diagnosticsShim);
  mappings.set(path.resolve(baseDir, 'diagnostics.cjs'), diagnosticsShim);
  return mappings;
}

async function loadPasModule() {
  const requireMap = await buildRequireMap();
  return loadCommonJsModule(parasymPath, { requireMap });
}

test('PAS cycle realigns diagnostics state and clears alerts', async () => {
  const diagnosticsModule = await diagnosticsModulePromise;
  const { DIAG_PATH, loadDiagnostics, saveDiagnostics } = diagnosticsModule;
  const { runPASCycle } = await loadPasModule();

  const backup = fs.existsSync(DIAG_PATH)
    ? fs.readFileSync(DIAG_PATH, 'utf8')
    : null;

  try {
    const diag = loadDiagnostics();
    diag.symbolicDrift = 0.5;
    diag.lastAnchorSync = Date.now() - 11 * 60 * 1000;
    diag.ethicsFlags = ['violation'];
    diag.load = 10;

    saveDiagnostics(diag);
    runPASCycle();

    const updated = loadDiagnostics();
    assert.ok(updated.symbolicDrift <= 0.5, 'drift should not increase');
    assert.equal(updated.ethicsFlags.length, 0, 'ethics flags should clear');
    assert.ok(
      Date.now() - updated.lastAnchorSync < 2_000,
      'anchor should resync promptly'
    );
    assert.ok(updated.load <= 9, 'workload should throttle when above threshold');
  } finally {
    if (backup !== null) {
      fs.writeFileSync(DIAG_PATH, backup);
    } else if (fs.existsSync(DIAG_PATH)) {
      fs.unlinkSync(DIAG_PATH);
    }
  }
});
