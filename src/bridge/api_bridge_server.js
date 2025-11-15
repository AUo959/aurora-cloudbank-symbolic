/**
 * 🌐 API BRIDGE SERVER - Communication Hub
 * Emergency deployment for Agent Constellation communication
 */

import http from 'http';
import { AgentSynchronizer } from '../system/agent_synchronizer.js';

class ApiBridgeServer {
  constructor(port = 3838, synchronizer = new AgentSynchronizer()) {
    this.port = port;
    this.server = null;
    this.synchronizer = synchronizer;
    this.status = 'INITIALIZING';
  }

  start() {
    if (this.server) {
      return this.server;
    }

    this.server = http.createServer((req, res) => {
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Access-Control-Allow-Origin', '*');

      if (req.url === '/agent-status' && req.method === 'GET') {
        this.handleAgentStatus(req, res);
      } else if (req.url === '/drift-report' && req.method === 'GET') {
        this.handleDriftReport(req, res);
      } else if (req.url === '/sync' && req.method === 'POST') {
        this.handleSync(req, res);
      } else {
        res.writeHead(404);
        res.end(JSON.stringify({ error: 'Endpoint not found' }));
      }
    });

    this.server.listen(this.port, () => {
      this.status = 'OPERATIONAL';
      process.stdout.write(`🌐 [API_BRIDGE] Server running on port ${this.port}\n`);
    });

    return this.server;
  }

  async handleAgentStatus(req, res) {
    try {
      const status = this.synchronizer.getStatus();
      res.writeHead(200);
      res.end(JSON.stringify(status));
    } catch (error) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: error.message }));
    }
  }

  async handleDriftReport(req, res) {
    try {
      const report = await this.synchronizer.getDriftReport();
      res.writeHead(200);
      res.end(JSON.stringify(report));
    } catch (error) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: error.message }));
    }
  }

  async handleSync(req, res) {
    try {
      const syncResult = await this.synchronizer.synchronizeAllLayers();
      res.writeHead(200);
      res.end(JSON.stringify(syncResult));
    } catch (error) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: error.message }));
    }
  }

  stop() {
    if (this.server) {
      this.server.close();
      this.server = null;
      this.status = 'STOPPED';
    }
  }
}

export default ApiBridgeServer;

// Emergency deployment
if (import.meta.url === `file://${process.argv[1]}`) {
  const bridge = new ApiBridgeServer();
  bridge.start();

  process.on('SIGINT', () => {
    bridge.stop();
    process.exit(0);
  });
}
