const crypto = require("crypto");

// Key generation; replace with a secure KMS in production. The IV will be
// generated for each encryption call to ensure uniqueness.
const key = crypto.randomBytes(32); // AES-256 requires 32-byte key

/**
 * Encrypts data using AES-256-CBC.
 * @param {string} data - The data to encrypt.
 * @returns {object} - The encrypted data and IV.
 */
function encrypt(data) {
  // Generate a unique IV for each encryption call
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv("aes-256-cbc", key, iv);
  let encrypted = cipher.update(data, "utf-8", "hex");
  encrypted += cipher.final("hex");
  return { encryptedData: encrypted, iv: iv.toString("hex") };
}

/**
 * Decrypts data using AES-256-CBC.
 * @param {string} encryptedData - The encrypted data.
 * @param {string} ivHex - The Initialization Vector in hex format returned by
 * encrypt().
 * @returns {string} - The decrypted data.
 */
function decrypt(encryptedData, ivHex) {
  const decipher = crypto.createDecipheriv(
    "aes-256-cbc",
    key,
    Buffer.from(ivHex, "hex")
  );
  let decrypted = decipher.update(encryptedData, "hex", "utf-8");
  decrypted += decipher.final("utf-8");
  return decrypted;
}

module.exports = { encrypt, decrypt };