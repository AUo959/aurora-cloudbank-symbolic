const fs = require('fs');
const crypto = require('crypto');
const filePath = process.argv[2];
if (!filePath) {
  console.error('Usage: node scripts/hash_bundle.js <file>');
  process.exit(1);
}
const hash = crypto.createHash('sha256');
const stream = fs.createReadStream(filePath);
stream.on('data', chunk => hash.update(chunk));
stream.on('end', () => {
  console.log(`SHA256 (${filePath}):`, hash.digest('hex'));
});
