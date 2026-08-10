/**
 * Aurora CloudBank browser utility tests.
 *
 * The harness supplies only the browser primitives used by the maintained
 * static modules; assertions exercise those modules directly.
 */
import test, { mock } from 'node:test';
import assert from 'node:assert/strict';

function createMockElement(tagName) {
  const attributes = new Map();

  return {
    tagName: tagName.toUpperCase(),
    textContent: '',
    innerHTML: '',
    setAttribute(name, value) {
      attributes.set(name, value);
    },
    getAttribute(name) {
      return attributes.get(name) ?? null;
    },
    removeAttribute(name) {
      attributes.delete(name);
    },
  };
}

const storageData = new Map();

global.window = {
  location: { host: 'localhost:8000', origin: 'http://localhost:8000' },
  performance: { now: () => 42 },
  addEventListener: mock.fn(),
};

global.document = {
  createElement: createMockElement,
};

global.localStorage = {
  getItem(key) {
    return storageData.get(key) ?? null;
  },
  setItem(key, value) {
    storageData.set(key, value);
  },
  removeItem(key) {
    storageData.delete(key);
  },
  clear() {
    storageData.clear();
  },
};

global.fetch = mock.fn(async () => ({ ok: true }));

test('maintained browser utilities expose and enforce their contracts', async t => {
  await import('../../static/js/aurora-security.js');
  await import('../../static/js/aurora-web-logger.js');

  const security = global.window.AuroraSecurity;
  const AuroraWebLogger = global.window.AuroraWebLogger;

  await t.test('modules register their browser APIs', () => {
    assert.ok(security);
    assert.equal(typeof AuroraWebLogger, 'function');
  });

  await t.test('HTML-sensitive characters are escaped', () => {
    assert.equal(
      security.escapeHtml('<script>alert("x")</script>'),
      '&lt;script&gt;alert(&quot;x&quot;)&lt;&#x2F;script&gt;'
    );
  });

  await t.test('unsafe control characters are removed from display text', () => {
    assert.equal(security.sanitizeText('anchor\u0000-safe\u007f'), 'anchor-safe');
    assert.equal(security.sanitizeText({ message: 'not text' }), '');
  });

  await t.test('safe elements use text content and reject event attributes', () => {
    const element = security.createSafeElement('button', '<b>Launch</b>', {
      class: 'primary',
      onclick: 'launch()',
    });

    assert.equal(element.textContent, '<b>Launch</b>');
    assert.equal(element.getAttribute('class'), 'primary');
    assert.equal(element.getAttribute('onclick'), null);
  });

  await t.test('WebSocket payloads are normalized without executing markup', () => {
    assert.deepEqual(
      security.sanitizeWebSocketData('{"message":"safe\\u0000text","count":2}'),
      { message: 'safetext', count: 2 }
    );
    assert.match(
      security.sanitizeWebSocketData('{not-json').error,
      /Invalid JSON data/
    );
  });

  await t.test('logger bounds its in-memory and persisted history', () => {
    global.localStorage.clear();
    const logger = new AuroraWebLogger('TEST_COMPONENT', {
      console: false,
      maxStorageEntries: 2,
    });

    logger.info('first');
    logger.warn('second');
    logger.error('third');

    assert.deepEqual(logger.logBuffer.map(entry => entry.message), ['second', 'third']);
    assert.deepEqual(
      logger.getStoredLogs().map(entry => entry.message),
      ['second', 'third']
    );
  });

  await t.test('logger honors configured severity thresholds', () => {
    const logger = new AuroraWebLogger('TEST_COMPONENT', {
      console: false,
      storage: false,
      level: 'WARN',
    });

    assert.equal(logger.shouldLog('INFO'), false);
    assert.equal(logger.shouldLog('ERROR'), true);
  });
});
