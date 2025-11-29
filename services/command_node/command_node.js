// command_node.js
// Aurora Command Node v1.0 — Main CPU Interface for Orion Core
//
// @deprecated This file is maintained for backward compatibility.
// Use the unified CommandNode from 'src/core/command_node/' for new code.
// Migration: Import CommandNode from '../../src/core/command_node/index.js'
//
// The unified CommandNode provides:
// - initializeAuroraCore() - same THREADCORE initialization
// - relayCommand() - same command relay
// - ThreadcoreAdapter, PatchweaverAdapter, ZipwizAdapter - same modules
// - Plus routing, encryption, and ethics features

const fs = require('fs');
const path = require('path');

const THREADCORE = require('./modules/threadcore'); // Ensure this path matches your repo structure
const PATCHWEAVER = require('./modules/patchweaver');
const ZIPWIZ = require('./modules/zipwiz');
const { ETHICS_PROTOCOL, GLYPH_AGENTS } = require('./config/constants');

const ANCHOR_SEED = 'EOS_SEED_ORION';
const LOG_PATH = './logs/aurora-core.log';

function initializeAuroraCore() {
  console.log('🧬 Initializing Aurora Command Node…');

  THREADCORE.init({
    seed: ANCHOR_SEED,
    ethics: ETHICS_PROTOCOL,
    glyphAgents: GLYPH_AGENTS,
  });

  PATCHWEAVER.connect();
  ZIPWIZ.pingBeacon('constellation');

  logEvent('Aurora Command Node initialized.');
}

function logEvent(message) {
  const timestamp = new Date().toISOString();
  const entry = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(LOG_PATH, entry);
}

// Relay function — routes symbolic commands
function relayCommand(command, payload) {
  switch (command) {
    case 'SEED_ANCHOR':
      THREADCORE.seed(payload);
      break;
    case 'UPDATE_THREAD':
      THREADCORE.update(payload);
      break;
    case 'REFLECT':
      THREADCORE.reflect();
      break;
    default:
      logEvent(`⚠️ Unknown command: ${command}`);
  }
}

function AuroraStartup() {
  initializeConstellationRoutes();
  activateEthicsRelay('Picard_Delta_3');
  bootSymbolicCore();
}

module.exports = {
  initializeAuroraCore,
  relayCommand,
  logEvent,
};
