const assert = require('assert');

// Use a known 256-bit key for deterministic testing.
process.env.AES_KEY_256_HEX =
  '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef';

const { encrypt, decrypt } = require('../crypto_refactored');

const plaintext = 'Encryption test string';
const { encryptedData, iv } = encrypt(plaintext);
const decrypted = decrypt(encryptedData, iv);

assert.strictEqual(decrypted, plaintext, 'decrypted text should match original');
console.log('Encryption round-trip successful');
