import test from 'node:test';
import assert from 'node:assert/strict';
import { randomBytes } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { loadCommonJsModule } from './utils/cjs-loader.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

if (!process.env.AES_KEY_256_HEX) {
  process.env.AES_KEY_256_HEX = randomBytes(32).toString('hex');
}

const { encrypt, decrypt } = loadCommonJsModule(
  path.join(__dirname, '..', '..', 'lib', 'crypto_refactored.js')
);

test('encrypt/decrypt round trip uses AES-256 key material', () => {
  const message = 'Encryption test string';
  const { encryptedData, iv } = encrypt(message);
  const decrypted = decrypt(encryptedData, iv);

  assert.equal(decrypted, message);
  assert.match(iv, /^[0-9a-f]{32}$/i);
  assert.match(encryptedData, /^[0-9a-f]+$/i);
});
