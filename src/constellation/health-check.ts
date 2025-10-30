#!/usr/bin/env node
/**
 * Constellation Health Check CLI
 * Symbolic Anchor: T1_CONSTELLATION_PRIME
 */

interface HealthResponse {
  status: string;
  anchor: string;
  timestamp: string;
}

async function healthCheck() {
  const baseUrl = process.env.CONSTELLATION_URL || 'http://localhost:5000';
  
  try {
    console.log('[T1_CONSTELLATION_PRIME] Performing health check...');
    
    const response = await fetch(`${baseUrl}/api/health`);
    const data = await response.json() as HealthResponse;
    
    if (data.status === 'healthy') {
      console.log('✅ Constellation is healthy');
      console.log(`   Anchor: ${data.anchor}`);
      console.log(`   Timestamp: ${data.timestamp}`);
      process.exit(0);
    } else {
      console.error('❌ Constellation is unhealthy');
      process.exit(1);
    }
  } catch (error) {
    console.error('❌ Failed to connect to Constellation:', error);
    process.exit(1);
  }
}

healthCheck();
