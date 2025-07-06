// command_node.js – Orion CORE Node Command Dispatcher
// 🧬🛡️ Version: v1.0.0 – Symbolic Secure Bootstrap

require('dotenv').config();
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// --- CONFIG ---
const AES_KEY = process.env.AES_KEY_256_HEX;
if (!AES_KEY || AES_KEY.length !== 64) {
  throw new Error('AES_KEY_256_HEX missing or invalid. Please provide a 256-bit key as a hex string in .env');
}

const SYMBOLIC_NODE_METADATA = {
  node: 'ORION_CORE_COMMAND',
  version: 'v1.0.0',
  mode: 'secure',
  deploy_timestamp: new Date().toISOString(),
  linked_agents: ['ZIPWIZ', 'PATCHWEAVER'],
  status: 'live',
};

// --- ENCRYPTION UTILITY ---
function encryptSymbolicPayload(payload) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(AES_KEY, 'hex'), iv);
  let encrypted = cipher.update(JSON.stringify(payload));
  encrypted = Buffer.concat([encrypted, cipher.final()]);
  return {
    iv: iv.toString('hex'),
    data: encrypted.toString('hex')
  };
}

// --- MAIN COMMAND DISPATCH ---
function dispatchSymbolicCommand(symbolicCommand) {
  console.log('🧬 Dispatching symbolic command node...');
  const encrypted = encryptSymbolicPayload({
    metadata: SYMBOLIC_NODE_METADATA,
    command: symbolicCommand,
    anchor: 'EOS_SEED_ORION'
  });

  fs.writeFileSync(
    path.join(__dirname, 'dispatch.encrypted.json'),
    JSON.stringify(encrypted, null, 2)
  );

  console.log('✅ Symbolic command encrypted and stored at /src/nodes/dispatch.encrypted.json');
}

// EXAMPLE USAGE (trigger)
if (require.main === module) {
  const sampleCommand = {
    action: 'SEAL_SYMBOLIC_THREAD',
    glyph: 'Caelion',
    message: 'Anchor locked. Awaiting ZIPWIZ confirmation.'
  };

  dispatchSymbolicCommand(sampleCommand);
}

module.exports = {
  dispatchSymbolicCommand,
};
