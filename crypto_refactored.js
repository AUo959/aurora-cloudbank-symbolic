
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Load key from ENV or fallback to static dev key (DO NOT USE IN PRODUCTION)
const keyHex = process.env.AES_KEY_256_HEX || '00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff';
const key = Buffer.from(keyHex, 'hex');

// Encrypt data with a fresh IV
function encrypt(data) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return { encryptedData: encrypted, iv: iv.toString('hex') };
}

// Decrypt data using the provided IV
function decrypt(encryptedData, ivHex) {
    const iv = Buffer.from(ivHex, 'hex');
    const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
    let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
}

// CLI usage: node crypto.js encrypt "Hello world"
//             node crypto.js decrypt "<data>" "<iv>"
if (require.main === module) {
    const [,, cmd, ...args] = process.argv;
    if (cmd === 'encrypt') {
        const input = args.join(' ');
        const result = encrypt(input);
        console.log('Encrypted:', result.encryptedData);
        console.log('IV:', result.iv);
    } else if (cmd === 'decrypt') {
        const [encryptedData, iv] = args;
        if (!encryptedData || !iv) {
            console.error('Usage: decrypt <encryptedData> <iv>');
            process.exit(1);
        }
        try {
            const result = decrypt(encryptedData, iv);
            console.log('Decrypted:', result);
        } catch (err) {
            console.error('Decryption failed:', err.message);
        }
    } else {
        console.log('Usage:
  node crypto.js encrypt "your text"
  node crypto.js decrypt <encryptedData> <iv>');
    }
}

module.exports = { encrypt, decrypt };
