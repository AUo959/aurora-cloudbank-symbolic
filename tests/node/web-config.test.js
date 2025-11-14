import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../..');

const packageJson = JSON.parse(
  fs.readFileSync(path.join(projectRoot, 'package.json'), 'utf8')
);

const requiredFiles = [
  'scripts/build-web.js',
  'scripts/web-server.js',
  'static/js/aurora-web-logger.js'
];

test('package.json is configured for modern web tooling', () => {
  assert.equal(packageJson.type, 'module');
  assert.ok(packageJson.scripts['start:web'], 'start:web script should exist');
  assert.ok(packageJson.scripts['test:web'], 'test:web script should exist');
  assert.ok(packageJson.dependencies.express, 'express dependency required');
  assert.ok(packageJson.dependencies.ws, 'ws dependency required');
});

test('core web infrastructure files exist', () => {
  for (const file of requiredFiles) {
    const fullPath = path.join(projectRoot, file);
    assert.ok(fs.existsSync(fullPath), `${file} should be present`);
  }
});
