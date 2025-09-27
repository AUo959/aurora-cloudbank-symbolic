import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DIAG_PATH = path.join(
  __dirname,
  '..',
  '..',
  'live_threads',
  'diagnostics.json'
);

function loadDiagnostics() {
  if (!fs.existsSync(DIAG_PATH)) {
    const init = {
      symbolicDrift: 0,
      lastAnchorSync: Date.now(),
      ethicsFlags: [],
      load: 0,
      commandCount: 0,
      glyphCount: 0,
      bundleCount: 0,
    };
    fs.writeFileSync(DIAG_PATH, JSON.stringify(init, null, 2));
    return init;
  }
  return JSON.parse(fs.readFileSync(DIAG_PATH, 'utf8'));
}

function saveDiagnostics(data) {
  fs.writeFileSync(DIAG_PATH, JSON.stringify(data, null, 2));
}

export { DIAG_PATH, loadDiagnostics, saveDiagnostics };
