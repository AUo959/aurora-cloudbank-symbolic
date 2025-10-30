#!/usr/bin/env node
/**
 * Constellation Memory Seal CLI
 * Symbolic Anchor: T1_CONSTELLATION_PRIME
 */

interface SealResponse {
  success: boolean;
  snapshots: {
    registry: {
      stateHash: string;
      timestamp: string;
    };
    orchestrator: {
      snapshotHash: string;
    };
  };
}

async function sealState() {
  const baseUrl = process.env.CONSTELLATION_URL || 'http://localhost:5000';
  
  try {
    console.log('[T1_CONSTELLATION_PRIME] Creating memory seal...');
    
    const response = await fetch(`${baseUrl}/api/memory/snapshot`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json() as SealResponse;
    
    if (data.success) {
      console.log('✅ Memory state sealed');
      console.log(`   Registry Hash: ${data.snapshots.registry.stateHash.substring(0, 16)}...`);
      console.log(`   Orchestrator Hash: ${data.snapshots.orchestrator.snapshotHash.substring(0, 16)}...`);
      console.log(`   Timestamp: ${data.snapshots.registry.timestamp}`);
      process.exit(0);
    } else {
      console.error('❌ Failed to seal memory state');
      process.exit(1);
    }
  } catch (error) {
    console.error('❌ Failed to connect to Constellation:', error);
    process.exit(1);
  }
}

sealState();
