const fs = require('fs').promises;
const path = require('path');

const DIAG_PATH = path.join(__dirname, '..', '..', 'live_threads', 'diagnostics.json');

async function loadDiagnostics() {
  try {
    await fs.access(DIAG_PATH);
  } catch {
    const init = {
      symbolicDrift: 0,
      lastAnchorSync: Date.now(),
      ethicsFlags: [],
      load: 0,
      commandCount: 0,
      glyphCount: 0,
      bundleCount: 0
    };
    await fs.writeFile(DIAG_PATH, JSON.stringify(init, null, 2));
    return init;
  }
  const data = await fs.readFile(DIAG_PATH, 'utf8');
  return JSON.parse(data);
}

async function saveDiagnostics(data) {
  await fs.writeFile(DIAG_PATH, JSON.stringify(data, null, 2));
}

module.exports = { DIAG_PATH, loadDiagnostics, saveDiagnostics };
