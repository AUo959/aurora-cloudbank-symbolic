const assert = require('assert');
const { encrypt, decrypt } = require('../crypto_refactored');

const plaintext = 'Encryption test string';
const { encryptedData, iv } = encrypt(plaintext);
const decrypted = decrypt(encryptedData, iv);

assert.strictEqual(
  decrypted,
  plaintext,
  'decrypted text should match original'
);
console.log('Encryption round-trip successful');
