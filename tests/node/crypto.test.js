import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';

import {
  decryptPayload,
  encryptPayload,
  isEncryptionAvailable,
} from '../../src/core/command_node/encryption.js';

const originalEncryptionKey = process.env.AES_KEY_256_HEX;
process.env.AES_KEY_256_HEX = randomBytes(32).toString('hex');

after(() => {
  if (originalEncryptionKey === undefined) {
    delete process.env.AES_KEY_256_HEX;
  } else {
    process.env.AES_KEY_256_HEX = originalEncryptionKey;
  }
});

test('encrypt/decrypt round trip uses AES-256 key material', () => {
  const payload = {
    message: 'Encryption test string',
    metadata: { anchor: 'T1', sequence: 7 },
  };
  const encrypted = encryptPayload(payload);
  const decrypted = decryptPayload(encrypted);

  assert.equal(isEncryptionAvailable(), true);
  assert.deepEqual(decrypted, payload);
  assert.match(encrypted.iv, /^[0-9a-f]{32}$/i);
  assert.match(encrypted.data, /^[0-9a-f]+$/i);
});

test('encrypting the same payload uses a fresh IV', () => {
  const payload = { message: 'repeatable plaintext' };
  const first = encryptPayload(payload);
  const second = encryptPayload(payload);

  assert.notEqual(first.iv, second.iv);
  assert.notEqual(first.data, second.data);
});

test('malformed ciphertext is rejected', () => {
  const encrypted = encryptPayload({ message: 'protected payload' });

  assert.throws(
    () => decryptPayload({ ...encrypted, data: '00' }),
    /bad decrypt|wrong final block length/i
  );
});

test('encryption fails closed when key material is absent', () => {
  const testKey = process.env.AES_KEY_256_HEX;
  delete process.env.AES_KEY_256_HEX;

  try {
    assert.equal(isEncryptionAvailable(), false);
    assert.throws(
      () => encryptPayload({ message: 'must not encrypt' }),
      /AES_KEY_256_HEX missing or invalid/
    );
    assert.throws(
      () => decryptPayload({ iv: '00'.repeat(16), data: '00' }),
      /AES_KEY_256_HEX missing or invalid/
    );
  } finally {
    process.env.AES_KEY_256_HEX = testKey;
  }
});
