import test from 'node:test';
import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';

import {
  decryptPayload,
  encryptPayload,
} from '../../src/core/command_node/encryption.js';

if (!process.env.AES_KEY_256_HEX) {
  process.env.AES_KEY_256_HEX = randomBytes(32).toString('hex');
}

test('encrypt/decrypt round trip uses AES-256 key material', () => {
  const payload = { message: 'Encryption test string' };
  const encrypted = encryptPayload(payload);
  const decrypted = decryptPayload(encrypted);

  assert.deepEqual(decrypted, payload);
  assert.match(encrypted.iv, /^[0-9a-f]{32}$/i);
  assert.match(encrypted.data, /^[0-9a-f]+$/i);
});
