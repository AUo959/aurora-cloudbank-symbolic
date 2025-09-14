/**
 * Aurora CloudBank Web Interface Tests
 * Basic tests for web components and API endpoints
 */

import { test, mock } from 'node:test';
import assert from 'node:assert';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../..');

// Mock DOM globals for testing
global.window = {
  location: { host: 'localhost:8000', origin: 'http://localhost:8000' },
  performance: { now: () => Date.now() },
  addEventListener: () => {},
  WebSocket: class MockWebSocket {
    constructor(url) { this.url = url; this.readyState = 1; }
    send() {}
    close() {}
  }
};

global.document = {
  getElementById: (id) => ({ 
    value: 'test-value',
    textContent: '',
    appendChild: () => {},
    scrollTop: 0,
    scrollHeight: 100
  }),
  createElement: (tag) => ({
    className: '',
    textContent: '',
    style: {},
    appendChild: () => {},
    title: ''
  }),
  createTextNode: (text) => ({ textContent: text }),
  addEventListener: () => {}
};

global.localStorage = {
  data: {},
  getItem: function(key) { return this.data[key] || null; },
  setItem: function(key, value) { this.data[key] = value; },
  removeItem: function(key) { delete this.data[key]; }
};

global.fetch = mock.fn(() => Promise.resolve({
  ok: true,
  json: () => Promise.resolve({ status: 'success' })
}));

test('Aurora Web Logger - Basic functionality', async (t) => {
  // Load Aurora Web Logger
  const loggerPath = path.join(projectRoot, 'static/js/aurora-web-logger.js');
  const loggerCode = fs.readFileSync(loggerPath, 'utf8');
    
  // Execute in test environment
  eval(loggerCode);
    
  await t.test('Logger initialization', () => {
    assert.ok(global.AuroraWebLogger, 'AuroraWebLogger class should be available');
        
    const logger = new global.AuroraWebLogger('TEST_COMPONENT');
    assert.strictEqual(logger.component, 'TEST_COMPONENT');
    assert.strictEqual(logger.logLevel, 'INFO');
    assert.ok(logger.sessionId);
  });

  await t.test('Logging methods', () => {
    const logger = new global.AuroraWebLogger('TEST_COMPONENT');
        
    // Test each logging method
    assert.doesNotThrow(() => logger.info('Test info message'));
    assert.doesNotThrow(() => logger.warn('Test warning message'));
    assert.doesNotThrow(() => logger.error('Test error message'));
    assert.doesNotThrow(() => logger.debug('Test debug message'));
  });

  await t.test('Aurora-specific methods', () => {
    const logger = new global.AuroraWebLogger('TEST_COMPONENT');
        
    assert.doesNotThrow(() => logger.drift('Drift detected', 0.03));
    assert.doesNotThrow(() => logger.ethics('Ethics validation'));
    assert.doesNotThrow(() => logger.anchor('Anchor established'));
    assert.doesNotThrow(() => logger.bridge('Bridge established', 'L1', 'L2'));
  });

  await t.test('Log storage', () => {
    const logger = new global.AuroraWebLogger('TEST_COMPONENT', { storage: true });
        
    logger.info('Test storage message');
    const storedLogs = logger.getStoredLogs();
        
    assert.ok(Array.isArray(storedLogs));
    assert.strictEqual(storedLogs.length, 1);
    assert.strictEqual(storedLogs[0].message, 'Test storage message');
  });
});

test('Aurora Security - Basic functionality', async (t) => {
  // Load Aurora Security
  const securityPath = path.join(projectRoot, 'static/js/aurora-security.js');
  const securityCode = fs.readFileSync(securityPath, 'utf8');
    
  // Execute in test environment
  eval(securityCode);
    
  await t.test('HTML sanitization', () => {
    assert.ok(global.AuroraSecurity, 'AuroraSecurity should be available');
        
    const cleanHtml = global.AuroraSecurity.sanitizeHTML('<script>alert("xss")</script><p>Safe content</p>');
    assert.ok(!cleanHtml.includes('<script>'), 'Scripts should be removed');
    assert.ok(cleanHtml.includes('Safe content'), 'Safe content should remain');
  });

  await t.test('HTML escaping', () => {
    const escaped = global.AuroraSecurity.escapeHtml('<script>alert("test")</script>');
    assert.strictEqual(escaped, '&lt;script&gt;alert(&quot;test&quot;)&lt;/script&gt;');
  });

  await t.test('Safe element creation', () => {
    const element = global.AuroraSecurity.createSafeElement('div', 'Test content');
    assert.ok(element);
    assert.strictEqual(element.textContent, 'Test content');
  });
});

test('HTML file validation', async (t) => {
  await t.test('index.html exists and is valid', () => {
    const indexPath = path.join(projectRoot, 'index.html');
    assert.ok(fs.existsSync(indexPath), 'index.html should exist');
        
    const content = fs.readFileSync(indexPath, 'utf8');
    assert.ok(content.includes('<!DOCTYPE html>'), 'Should have DOCTYPE');
    assert.ok(content.includes('Aurora'), 'Should contain Aurora branding');
    assert.ok(content.includes('aurora-security.js'), 'Should include security script');
    assert.ok(content.includes('aurora-web-logger.js'), 'Should include web logger');
  });

  await t.test('aurora_dashboard.html exists and is valid', () => {
    const dashboardPath = path.join(projectRoot, 'aurora_dashboard.html');
    assert.ok(fs.existsSync(dashboardPath), 'aurora_dashboard.html should exist');
        
    const content = fs.readFileSync(dashboardPath, 'utf8');
    assert.ok(content.includes('<!DOCTYPE html>'), 'Should have DOCTYPE');
    assert.ok(content.includes('Aurora'), 'Should contain Aurora branding');
  });
});

test('Build system validation', async (t) => {
  await t.test('Build script exists', () => {
    const buildScriptPath = path.join(projectRoot, 'scripts/build-web.js');
    assert.ok(fs.existsSync(buildScriptPath), 'Build script should exist');
  });

  await t.test('Web server script exists', () => {
    const serverScriptPath = path.join(projectRoot, 'scripts/web-server.js');
    assert.ok(fs.existsSync(serverScriptPath), 'Web server script should exist');
  });

  await t.test('Package.json has proper web scripts', () => {
    const packagePath = path.join(projectRoot, 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        
    assert.ok(packageJson.scripts.build, 'Should have build script');
    assert.ok(packageJson.scripts.start, 'Should have start script');
    assert.ok(packageJson.scripts.lint, 'Should have lint script');
    assert.ok(packageJson.type === 'module', 'Should be ES module');
  });
});

test('Static assets validation', async (t) => {
  await t.test('Static directory structure', () => {
    const staticPath = path.join(projectRoot, 'static');
    assert.ok(fs.existsSync(staticPath), 'Static directory should exist');
        
    const jsPath = path.join(staticPath, 'js');
    assert.ok(fs.existsSync(jsPath), 'Static js directory should exist');
  });

  await t.test('Required JS files exist', () => {
    const requiredFiles = [
      'static/js/aurora-security.js',
      'static/js/aurora-web-logger.js'
    ];
        
    for (const file of requiredFiles) {
      const filePath = path.join(projectRoot, file);
      assert.ok(fs.existsSync(filePath), `${file} should exist`);
    }
  });
});