// command_node.js – ORION CORE CPU Relay
// THREADCORE v3.5.1 integration – Symbolic Command Node

const { glyphSync } = require('../lib/glyph_engine');
const { anchorResolve, ethicsCheck } = require('../auth/ethics_layer');
const { zipBeaconPing } = require('../lib/zipcomm');

module.exports = {
  executeCommand(command) {
    if (!ethicsCheck(command)) throw new Error('Ethics violation detected');
    const anchor = anchorResolve(command.context || "AUTO");
    glyphSync(anchor);
    zipBeaconPing("ORION_CORE");
    return `Command ${command.name} executed with anchor ${anchor}`;
  }
};
