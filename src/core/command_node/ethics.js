/**
 * Aurora CommandNode - Ethics Validation Integration
 * Provides ethics checking and anchor resolution for command execution
 * Part of unified CommandNode architecture
 */

// Default forbidden commands
export const DEFAULT_FORBIDDEN_COMMANDS = ['blacklist', 'override'];

// Default ethics protocol
export const DEFAULT_ETHICS_PROTOCOL = 'Picard_Delta_3';

/**
 * Check if a command passes ethics validation
 * @param {object} command - The command to validate
 * @param {object} options - Options for validation
 * @param {string[]} options.forbiddenCommands - List of forbidden command names
 * @returns {boolean} True if command passes ethics check
 */
export function ethicsCheck(command, options = {}) {
  const forbiddenCommands = options.forbiddenCommands || DEFAULT_FORBIDDEN_COMMANDS;
  const commandName = command.name || command.action || '';
  return !forbiddenCommands.includes(commandName.toLowerCase());
}

/**
 * Resolve the anchor for a given context
 * @param {string} context - The context to resolve anchor for
 * @returns {string} The resolved anchor identifier
 */
export function anchorResolve(context) {
  const ctx = context || 'AUTO';
  return `ANCHOR_${ctx}_HASH`;
}

/**
 * Validate command against ethics protocol
 * @param {object} command - The command to validate
 * @param {string} protocol - Ethics protocol to use
 * @returns {object} Validation result with status and details
 */
export function validateEthics(command, protocol = DEFAULT_ETHICS_PROTOCOL) {
  const isValid = ethicsCheck(command);
  const anchor = anchorResolve(command.context || 'AUTO');

  return {
    valid: isValid,
    protocol: protocol,
    anchor: anchor,
    timestamp: Date.now(),
    details: isValid
      ? 'Command passed ethics validation'
      : 'Command failed ethics validation - forbidden action',
  };
}

/**
 * Get the default ethics protocol name
 * @returns {string} The default ethics protocol
 */
export function getDefaultProtocol() {
  return DEFAULT_ETHICS_PROTOCOL;
}

export default {
  ethicsCheck,
  anchorResolve,
  validateEthics,
  getDefaultProtocol,
  DEFAULT_FORBIDDEN_COMMANDS,
  DEFAULT_ETHICS_PROTOCOL,
};
