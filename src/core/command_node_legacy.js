// command_node_legacy.js – ORION CORE CPU Relay
// THREADCORE v3.5.1 integration – Symbolic Command Node
//
// @deprecated This file is maintained for backward compatibility.
// Use the unified CommandNode from './command_node/' for new code.
// Migration: Import CommandNode from './command_node/index.js'
//
// The unified CommandNode provides:
// - executeCommand() - same ethics-checked execution
// - ethicsCheck() and anchorResolve() - same validation
// - Plus routing, encryption, and THREADCORE features

const { routeGlyph } = require('./glyph_engine');
const { compressBundle } = require('./zipcomm');
const { anchorResolve, ethicsCheck } = require('../../auth/ethics_layer');
const { loadDiagnostics, saveDiagnostics } = require('./diagnostics');
const { runPASCycle, initializePAS } = require('./parasym_activation');

// Start PAS monitoring when this module is loaded
initializePAS();

module.exports = {
  executeCommand(command) {
    if (!ethicsCheck(command)) throw new Error('Ethics violation detected');
    const diag = loadDiagnostics();
    diag.commandCount = (diag.commandCount || 0) + 1;
    diag.lastCommandAt = Date.now();
    diag.load = diag.commandCount - (diag.processedCount || 0);
    saveDiagnostics(diag);

    const anchor = anchorResolve(command.context || 'AUTO');
    routeGlyph(command.name);
    compressBundle('ORION_CORE');

    runPASCycle();
    return `Command ${command.name} executed with anchor ${anchor}`;
  },
};
