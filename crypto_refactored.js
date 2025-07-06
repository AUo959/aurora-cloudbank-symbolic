const crypto = require('crypto');

// Require a key from the environment. Fail fast if missing to avoid insecure
// encryption defaults. Use a secret manager or injected environment variable
// in production deployments.
const keyHex = process.env.AES_KEY_256_HEX;
if (!keyHex) {
  throw new Error('AES_KEY_256_HEX environment variable must be set. See .env.example for details.');
}
const key = Buffer.from(keyHex, 'hex');
if (key.length !== 32) {
  throw new Error('AES_KEY_256_HEX must be 64 hex characters (32 bytes for AES-256).');
}

/**
 * Encrypt a UTF-8 string using AES-256-CBC with a random IV.
 * @param {string} data - Plaintext to encrypt.
 * @returns {{ encryptedData: string, iv: string }}
 */
function encrypt(data) {
  if (typeof data !== 'string' || !data.length) {
    throw new Error('Input data must be a non-empty string.');
  }
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
  let encrypted = cipher.update(data, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return { encryptedData: encrypted, iv: iv.toString('hex') };
}

/**
 * Decrypt AES-256-CBC encrypted data with provided IV.
 * @param {string} encryptedData - Hex-encoded ciphertext.
 * @param {string} ivHex - Hex-encoded IV (32 chars).
 * @returns {string} - Decrypted plaintext.
 */
function decrypt(encryptedData, ivHex) {
  if (!/^[0-9a-fA-F]+$/.test(encryptedData) || !/^[0-9a-fA-F]{32}$/.test(ivHex)) {
    throw new Error('Invalid encrypted data or IV format.');
  }
  const iv = Buffer.from(ivHex, 'hex');
  if (iv.length !== 16) {
    throw new Error('IV must be 16 bytes (32 hex characters).');
  }
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

/**
 * Helper to export a symbolic anchor manifest to disk.
 * @param {object} manifest - Anchor manifest object.
 * @param {string} [prefix='anchor'] - File prefix.
 * @returns {string} - Path to exported file.
 */
function exportAnchorManifest(manifest, prefix = 'anchor') {
  const exportPath = require('path').join(__dirname, `${prefix}_${Date.now()}.json`);
  require('fs').writeFileSync(exportPath, JSON.stringify(manifest, null, 2));
  return exportPath;
}

// CLI usage: node crypto_refactored.js encrypt "Hello world"
//             node crypto_refactored.js decrypt "<data>" "<iv>"
if (require.main === module) {
  const [,, cmd, ...args] = process.argv;
  if (cmd === 'encrypt') {
    const input = args.join(' ');
    try {
      const result = encrypt(input);
      console.log('Encrypted:', result.encryptedData);
      console.log('IV:', result.iv);
    } catch (err) {
      console.error('Encryption failed:', err.message);
    }
  } else if (cmd === 'decrypt') {
    let [encryptedData, iv] = args;
    if (!encryptedData || !iv) {
      console.error('Usage: decrypt <encryptedData> <iv>');
      process.exit(1);
    }
    // DLP_TAG:SRB,T1 | Symbolic Anchor: DECRYPT_RESULT
    try {
      const result = decrypt(encryptedData, iv);
      const anchorManifest = {
        tag: ['SRB', 'T1'],
        anchor: 'DECRYPT_RESULT',
        timestamp: new Date().toISOString(),
        decrypted: result,
        encryptedData,
        iv,
        continuity: 'preserved',
        entropy_state: 'post-decrypt'
      };
      const exportPath = exportAnchorManifest(anchorManifest, 'anchor_decrypt');
      encryptedData = null;
      iv = null;
      console.log('Decrypted:', result);
      console.log('Anchor manifest exported to:', exportPath);
    } catch (err) {
      console.error('Decryption failed:', err.message);
      const errorAnchor = {
        tag: ['SRB', 'T1', 'DECRYPT_ERROR'],
        anchor: 'DECRYPT_ERROR',
        timestamp: new Date().toISOString(),
        error: err.message,
        encryptedData,
        iv
      };
      exportAnchorManifest(errorAnchor, 'anchor_decrypt_error');
    }
  } else {
    console.log('Usage:\n  node crypto_refactored.js encrypt "your text"\n  node crypto_refactored.js decrypt <encryptedData> <iv>');
  }
}

module.exports = { encrypt, decrypt };
