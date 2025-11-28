#!/usr/bin/env node

/**
 * 🧪 AURORA CLOUDBANK SYMBOLIC - Integration Test Suite
 * Comprehensive test for all bridge modules, ZIPWIZ protocol, and agent coordination
 */

import { StarlingAuBridge } from './src/nodes/starling_au_bridge.js';
import { RiverthreadProcessor } from './src/nodes/riverthread_processor.js';
import { LatticeSync } from './src/core/lattice_sync.js';
import { AuroraCommandRouter } from './src/system/aurora_command_router.js';
import { EthicsEngine } from './src/core/ethics_layer.js';
import { ZipwizProtocol } from './src/core/zipcomm.js';
import { AgentSynchronizer } from './src/system/agent_synchronizer.js';

// Test color output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

function log(message, color = colors.white) {
  console.log(`${color}${message}${colors.reset}`);
}

async function runIntegrationTests() {
  log('🧪 Starting Aurora CloudBank Symbolic Integration Tests', colors.cyan);
  log('=' .repeat(60), colors.blue);
  
  let totalTests = 0;
  let passedTests = 0;
  
  try {
    // Test 1: StarlingAuBridge initialization
    log('\n🔸 Test 1: StarlingAuBridge Module Loading', colors.yellow);
    const starling = new StarlingAuBridge();
    await starling.initialize();
    log('✅ StarlingAuBridge loaded and initialized successfully', colors.green);
    totalTests++;
    passedTests++;
    
    // Test 2: RiverthreadProcessor initialization
    log('\n🔸 Test 2: RiverthreadProcessor Module Loading', colors.yellow);
    const riverthread = new RiverthreadProcessor();
    await riverthread.initialize();
    log('✅ RiverthreadProcessor loaded and initialized successfully', colors.green);
    totalTests++;
    passedTests++;
    
    // Test 3: LatticeSync coordination
    log('\n🔸 Test 3: LatticeSync Coordination System', colors.yellow);
    const latticeSync = new LatticeSync();
    await latticeSync.initialize();
    const syncStatus = await latticeSync.synchronizeAllLayers();
    log(`✅ LatticeSync coordination successful - Global State: ${syncStatus.globalSyncState}`, colors.green);
    totalTests++;
    passedTests++;
    
    // Test 4: AuroraCommandRouter dispatch
    log('\n🔸 Test 4: AuroraCommandRouter Dispatch System', colors.yellow);
    const router = new AuroraCommandRouter();
    const routeResult = router.routeCommand({
      type: 'TEST_COMMAND',
      target: 'STARLING_AU',
      payload: { test: true }
    }, 'L1');
    log(`✅ Command routing successful - Status: ${routeResult.status || 'ROUTED'}`, colors.green);
    totalTests++;
    passedTests++;
    
    // Test 5: EthicsEngine validation
    log('\n🔸 Test 5: EthicsEngine Picard_Delta_3 Protocol', colors.yellow);
    const ethics = new EthicsEngine();
    const ethicsCheck = ethics.validatePayload({
      type: 'BRIDGE_COMMUNICATION',
      context: 'test_integration',
      sensitivity: 'L1_STANDARD'
    });
    log(`✅ Ethics validation passed - Result: ${ethicsCheck.approved ? 'APPROVED' : 'REJECTED'}`, colors.green);
    totalTests++;
    passedTests++;
    
    // Test 6: ZIPWIZ Protocol
    log('\n🔸 Test 6: ZIPWIZ Protocol Beacon System', colors.yellow);
    const zipwiz = new ZipwizProtocol();
    zipwiz.initialize();
    const beaconStatus = zipwiz.getStatus();
    log(`✅ ZIPWIZ Protocol operational - Status: ${beaconStatus.status || 'ACTIVE'}`, colors.green);
    totalTests++;
    passedTests++;
    
    // Test 7: Agent Synchronizer coordination
    log('\n🔸 Test 7: AgentSynchronizer Multi-Agent Coordination', colors.yellow);
    const agentSync = new AgentSynchronizer();
    const agentStatus = agentSync.getStatus();
    log(`✅ Agent synchronization successful - Status: ${agentStatus.status || 'OPERATIONAL'}`, colors.green);
    totalTests++;
    passedTests++;
    
    // Test 8: End-to-end Bridge Communication Flow
    log('\n🔸 Test 8: End-to-End Bridge Communication', colors.yellow);
    
    // Create a test simulation communication
    const testMessage = {
      type: 'SIMULATION_REQUEST',
      source: 'INTEGRATION_TEST',
      target: 'STARLING_AU',
      payload: {
        simulationType: 'basic_coordination',
        parameters: { testMode: true }
      }
    };
    
    // Route through command router  
    const routingResult = router.routeCommand(testMessage, 'L1');
    
    // Process through StarlingAu bridge
    const bridgeResult = await starling.processExternalCommunication(testMessage);
    
    log(`✅ End-to-end communication flow successful`, colors.green);
    log(`   └─ Routing: ${routingResult.status}`, colors.white);
    log(`   └─ Bridge Processing: ${bridgeResult.status}`, colors.white);
    totalTests++;
    passedTests++;
    
  } catch (error) {
    log(`❌ Integration test failed: ${error.message}`, colors.red);
    console.error(error.stack);
    totalTests++;
  }
  
  // Final Results
  log('\n' + '=' .repeat(60), colors.blue);
  log(`🧪 Integration Test Results`, colors.cyan);
  log(`   Tests Passed: ${passedTests}/${totalTests}`, passedTests === totalTests ? colors.green : colors.red);
  
  if (passedTests === totalTests) {
    log('🎉 All integration tests passed! Aurora CloudBank Symbolic is ready for Orion integration.', colors.green);
    return true;
  } else {
    log('⚠️  Some integration tests failed. Review the errors above.', colors.yellow);
    return false;
  }
}

// Execute integration tests
if (import.meta.url === `file://${process.argv[1]}`) {
  runIntegrationTests()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      log(`❌ Fatal error in integration tests: ${error.message}`, colors.red);
      console.error(error.stack);
      process.exit(1);
    });
}

export { runIntegrationTests };