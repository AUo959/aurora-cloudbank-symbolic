#!/usr/bin/env node

/**
 * Aurora CloudBank - Natural Language Command Handler
 * Interprets user commands and executes appropriate actions
 */

const { execSync } = require('child_process');
const path = require('path');

// Command mapping
const COMMAND_PATTERNS = {
  'time to clean up': {
    script: './scripts/aurora_cleanup_command.sh',
    description: 'Complete repository cleanup: pull, stage, commit, push, sync branches'
  },
  'cleanup': {
    script: './scripts/aurora_cleanup_command.sh',
    description: 'Complete repository cleanup: pull, stage, commit, push, sync branches'
  },
  'clean up': {
    script: './scripts/aurora_cleanup_command.sh',
    description: 'Complete repository cleanup: pull, stage, commit, push, sync branches'
  }
};

function executeCommand(userInput) {
  const normalizedInput = userInput.toLowerCase().trim();

  console.log('🌟 Aurora CloudBank Command Interpreter');
  console.log('=====================================');
  console.log(`📝 User said: "${userInput}"`);

  // Check for exact matches
  if (COMMAND_PATTERNS[normalizedInput]) {
    const command = COMMAND_PATTERNS[normalizedInput];
    console.log(`🎯 Recognized command: ${command.description}`);
    console.log(`🚀 Executing: ${command.script}`);
    console.log('');

    try {
      execSync(command.script, {
        stdio: 'inherit',
        cwd: path.dirname(__dirname)
      });
    } catch (error) {
      console.error('❌ Command execution failed:', error.message);
      process.exit(1);
    }
    return;
  }

  // Check for partial matches
  for (const [pattern, command] of Object.entries(COMMAND_PATTERNS)) {
    if (normalizedInput.includes(pattern) || pattern.includes(normalizedInput)) {
      console.log(`🎯 Partial match found for: "${pattern}"`);
      console.log(`📋 Description: ${command.description}`);
      console.log(`❓ Did you mean to run the cleanup command? (y/n)`);

      // For now, just run it - in a real implementation you might want confirmation
      console.log('🚀 Executing cleanup command...');
      console.log('');

      try {
        execSync(command.script, {
          stdio: 'inherit',
          cwd: path.dirname(__dirname)
        });
      } catch (error) {
        console.error('❌ Command execution failed:', error.message);
        process.exit(1);
      }
      return;
    }
  }

  // No matches found
  console.log('❓ Command not recognized');
  console.log('📚 Available commands:');
  for (const [pattern, command] of Object.entries(COMMAND_PATTERNS)) {
    console.log(`  • "${pattern}" - ${command.description}`);
  }
}

// Get command from command line arguments
const userCommand = process.argv.slice(2).join(' ');

if (!userCommand) {
  console.log('🌟 Aurora CloudBank Command Interpreter');
  console.log('Usage: node aurora_command_handler.js <command>');
  console.log('');
  console.log('📚 Available commands:');
  for (const [pattern, command] of Object.entries(COMMAND_PATTERNS)) {
    console.log(`  • "${pattern}" - ${command.description}`);
  }
  process.exit(0);
}

executeCommand(userCommand);
