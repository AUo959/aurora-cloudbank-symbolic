/**
 * Aurora CloudBank Web Interface Tests
 * Basic tests for web components and API endpoints
 */
/* eslint-env browser */
/* global document */
import { mock } from 'node:test';
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
  getElementById: () => ({ 
    value: 'test-value',
    textContent: '',
    appendChild: () => {},
    scrollTop: 0,
    scrollHeight: 100
  }),
  createElement: () => ({
    className: '',
    textContent: '',
    style: {},
    appendChild: () => {},
    title: '',
    setAttribute: () => {},
    removeAttribute: () => {}
  }),
  createTextNode: (text) => ({ textContent: text }),
  createDocumentFragment: () => ({ appendChild: () => {} }),
  createTreeWalker: () => ({ nextNode: () => null }),
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

global.NodeFilter = {
  SHOW_ELEMENT: 1,
  FILTER_ACCEPT: 1,
  FILTER_REJECT: 2
};

/**
 * Enhanced multi-pass sanitization for security
 * 
 * This function implements defense-in-depth sanitization:
 * - Removes control characters (null bytes, carriage returns, etc.)
 * - Strips script tags and JavaScript protocols
 * - Removes event handler attributes
 * - Uses replaceAll() for reliable, complete replacements
 * - Employs iterative sanitization to prevent bypass attempts
 * 
 * @param {string} input - The input string to sanitize
 * @returns {string} The sanitized string, truncated to 1000 characters
 */
function sanitizeInput(input) {
  if (typeof input !== 'string') return '';
  
  let sanitized = input;
  let previousLength;
  
  // SECURITY: Repeat sanitization until no more changes occur
  // This prevents bypass via nested patterns like <scr<script>ipt>
  do {
    previousLength = sanitized.length;
    
    // Remove control characters and potential XSS vectors
    sanitized = sanitized
      // Control characters: Remove ASCII control chars (0x00-0x1F) and 
      // extended control chars (0x7F-0x9F) which can be used to hide malicious
      // content or bypass filters (null bytes, carriage returns, line feeds, etc.)
      .replace(/[\x00-\x1f\x7f-\x9f]/g, '')
      // Script tags: Remove all script tags and their content
      .replace(/<script[^>]*>.*?<\/script>/gi, '')
      // JavaScript protocol: Remove javascript: pseudo-protocol from URLs
      .replace(/javascript:/gi, '')
      // Event handlers: Remove inline event handler attributes (onclick, onload, etc.)
      .replace(/on\w+\s*=/gi, '');
  } while (sanitized.length !== previousLength);
  
  // Truncate to reasonable length to prevent DoS
  return sanitized.substring(0, 1000);
}
