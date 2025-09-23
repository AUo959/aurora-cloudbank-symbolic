const assert = require('assert');

// Provide a deterministic key for testing before loading the module.
process.env.AES_KEY_256_HEX =
  '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef';
let { encrypt, decrypt } = require('../crypto_refactored');

const plaintext = 'Encryption test string';
const { encryptedData, iv } = encrypt(plaintext);
const decrypted = decrypt(encryptedData, iv);
assert.strictEqual(decrypted, plaintext, 'decrypted text should match original');

// Changing the key should make decryption fail, proving the env var is used.
delete require.cache[require.resolve('../crypto_refactored')];
process.env.AES_KEY_256_HEX =
  'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff';
({ decrypt } = require('../crypto_refactored'));
assert.throws(() => decrypt(encryptedData, iv));

console.log('Environment-based encryption test passed');
