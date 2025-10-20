/**
 * Aurora CloudBank Web Interface Tests
 * Basic tests for web components and API endpoints
 */
/* eslint-env browser */
/* global document */
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

// Enhanced multi-character sanitization for security - FIXED
function sanitizeInput(input) {
  if (typeof input !== 'string') return '';
  
  let sanitized = input;
  let previousLength;
  
  // SECURITY FIX: Repeat sanitization until no more changes occur
  // This prevents bypass via nested patterns like <scr<script>ipt>
  do {
    previousLength = sanitized.length;
    
    // Remove control characters and potential XSS vectors
    sanitized = sanitized
      .replace(/[\x00-\x1f\x7f-\x9f]/g, '') // Control chars
      .replace(/<script[^>]*>.*?<\/script>/gi, '') // Script tags
      .replace(/javascript:/gi, '') // JavaScript protocol
      .replace(/on\w+\s*=/gi, ''); // Event handlers
  } while (sanitized.length !== previousLength);
  
  // Truncate to reasonable length
  return sanitized.substring(0, 1000);
}
