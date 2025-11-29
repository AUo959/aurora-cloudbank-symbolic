/**
 * Aurora CommandNode - Encryption Utilities
 * AES-256 encryption for secure symbolic command dispatch
 * Part of unified CommandNode architecture
 */

import crypto from 'crypto';

/**
 * Get the AES encryption key from environment
 * @returns {Buffer|null} The encryption key or null if not configured
 */
export function getEncryptionKey() {
  const AES_KEY = process.env.AES_KEY_256_HEX;
  if (!AES_KEY || AES_KEY.length !== 64) {
    return null;
  }
  return Buffer.from(AES_KEY, 'hex');
}

/**
 * Check if encryption is available
 * @returns {boolean} True if encryption key is configured
 */
export function isEncryptionAvailable() {
  return getEncryptionKey() !== null;
}

/**
 * Encrypt a payload using AES-256-CBC
 * @param {object} payload - The payload to encrypt
 * @returns {object} Object with iv and encrypted data in hex format
 * @throws {Error} If encryption key is not configured
 */
export function encryptPayload(payload) {
  const key = getEncryptionKey();
  if (!key) {
    throw new Error(
      'AES_KEY_256_HEX missing or invalid. Please provide a 256-bit key as a hex string in .env'
    );
  }

  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
  let encrypted = cipher.update(JSON.stringify(payload));
  encrypted = Buffer.concat([encrypted, cipher.final()]);

  return {
    iv: iv.toString('hex'),
    data: encrypted.toString('hex'),
  };
}

/**
 * Decrypt an encrypted payload
 * @param {object} encryptedData - Object with iv and data in hex format
 * @returns {object} The decrypted payload
 * @throws {Error} If encryption key is not configured or decryption fails
 */
export function decryptPayload(encryptedData) {
  const key = getEncryptionKey();
  if (!key) {
    throw new Error(
      'AES_KEY_256_HEX missing or invalid. Please provide a 256-bit key as a hex string in .env'
    );
  }

  const iv = Buffer.from(encryptedData.iv, 'hex');
  const encryptedText = Buffer.from(encryptedData.data, 'hex');
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  let decrypted = decipher.update(encryptedText);
  decrypted = Buffer.concat([decrypted, decipher.final()]);

  return JSON.parse(decrypted.toString());
}

export default {
  getEncryptionKey,
  isEncryptionAvailable,
  encryptPayload,
  decryptPayload,
};
