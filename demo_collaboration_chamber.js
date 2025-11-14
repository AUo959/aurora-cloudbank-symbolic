#!/usr/bin/env node

/**
 * Aurora Collaboration Chamber Demo Script
 * Demonstrates @mesh system interactions and command traceback
 */

const io = require('socket.io-client');

const socket = io('http://localhost:8080');

console.log('🎯 Aurora Collaboration Chamber Demo');
console.log('=====================================');

socket.on('connect', () => {
  console.log('✅ Connected to Collaboration Chamber');
  console.log('🌌 Phase 7 Holographic Interface Active\n');

  // Demo sequence
  setTimeout(() => demoMeshBroadcast(), 1000);
  setTimeout(() => demoDirectAgentMessage(), 3000);
  setTimeout(() => demoTraceback(), 5000);
  setTimeout(() => {
    console.log('\n🎉 Demo completed! Chamber is ready for your interactions.');
    process.exit(0);
  }, 7000);
});

socket.on('system_status', (data) => {
  console.log('📊 System Status:', data);
});

socket.on('command_result', (data) => {
  console.log('📝 Command Result:', data.success ? '✅' : '❌');
  if (data.result) {
    console.log('   Response:', JSON.stringify(data.result, null, 2));
  }
});

socket.on('live_feed_update', (message) => {
  console.log(`📡 Live Feed [${message.sender}]: ${message.content}`);
});

socket.on('traceback_update', (data) => {
  console.log(`🔍 Traceback [${data.commandId}]: ${data.step.step}`);
});

function demoMeshBroadcast() {
  console.log('\n🕸️ Demo 1: Mesh Broadcast (@mesh system)');
  console.log('Broadcasting to all agents...');

  socket.emit('execute_command', {
    command: 'System status report and performance optimization recommendations',
    authority: 'operator',
    target: '@mesh'
  });
}

function demoDirectAgentMessage() {
  console.log('\n🤖 Demo 2: Direct Agent Communication');
  console.log('Sending direct message to ARCHY...');

  socket.emit('execute_command', {
    command: 'Analyze the current system architecture and suggest improvements',
    authority: 'user',
    target: '@agent.ARCHY'
  });
}

function demoTraceback() {
  console.log('\n🔍 Demo 3: Command Traceback System');
  console.log('Executing complex command with full traceback...');

  socket.emit('execute_command', {
    command: 'Initialize quantum-aware symbolic processing pipeline',
    authority: 'system',
    target: '@mesh'
  });
}

socket.on('disconnect', () => {
  console.log('📤 Disconnected from Collaboration Chamber');
});

socket.on('error', (error) => {
  console.error('❌ Socket error:', error);
});
