const { describe, test, expect } = require('@jest/globals');
const { encrypt, decrypt } = require('../crypto_refactored');

describe('crypto_refactored', () => {
  test('performs an AES-256 round trip', () => {
    const plaintext = 'Encryption test string';
    const { encryptedData, iv } = encrypt(plaintext);
    const decrypted = decrypt(encryptedData, iv);

    expect(decrypted).toBe(plaintext);
    expect(iv).toMatch(/^[0-9a-f]{32}$/i);
    expect(encryptedData).toMatch(/^[0-9a-f]+$/i);
  });
});
