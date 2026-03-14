/**
 * 🌐 API BRIDGE SERVER - Communication Hub
 * Emergency deployment for Agent Constellation communication
 */

const crypto = require('crypto');
const http = require('http');
const AgentSynchronizer = require('../system/agent_synchronizer');

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim() !== '';
}

function parseAllowedOrigins(rawValue, port) {
  if (isNonEmptyString(rawValue)) {
    const configuredOrigins = rawValue
      .split(',')
      .map(origin => origin.trim().replace(/\/$/, ''))
      .filter(origin => origin && origin !== '*');

    if (configuredOrigins.length > 0) {
      return configuredOrigins;
    }
  }

  return [
    `http://127.0.0.1:${port}`,
    `http://localhost:${port}`,
    'http://127.0.0.1:8080',
    'http://localhost:8080'
  ];
}

function isOriginAllowed(origin, allowedOrigins) {
  return !origin || allowedOrigins.includes(origin.replace(/\/$/, ''));
}

function timingSafeEqualString(expected, provided) {
  if (!isNonEmptyString(expected) || !isNonEmptyString(provided)) {
    return false;
  }

  const expectedBuffer = Buffer.from(expected, 'utf8');
  const providedBuffer = Buffer.from(provided, 'utf8');

  if (expectedBuffer.length !== providedBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(expectedBuffer, providedBuffer);
}

function extractBearerToken(req) {
  const authHeader = req.headers.authorization;
  if (!isNonEmptyString(authHeader)) {
    return '';
  }

  const [scheme, token] = authHeader.split(' ');
  if (scheme !== 'Bearer' || !isNonEmptyString(token)) {
    return '';
  }

  return token.trim();
}

class ApiBridgeServer {
  constructor(port = 3838) {
    this.port = port;
    this.host = process.env.AURORA_API_BRIDGE_HOST || '127.0.0.1';
    this.allowedOrigins = parseAllowedOrigins(process.env.AURORA_API_BRIDGE_ALLOWED_ORIGINS, port);
    this.syncEnabled = process.env.AURORA_ENABLE_API_BRIDGE_SYNC === 'true';
    this.syncToken = (process.env.AURORA_API_BRIDGE_TOKEN || '').trim();
    this.server = null;
    this.synchronizer = new AgentSynchronizer();
    this.status = 'INITIALIZING';
  }

  start() {
    this.server = http.createServer((req, res) => {
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Vary', 'Origin');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');

      const origin = req.headers.origin;
      if (origin) {
        if (!isOriginAllowed(origin, this.allowedOrigins)) {
          res.writeHead(403);
          res.end(JSON.stringify({ error: 'Origin not allowed' }));
          return;
        }

        res.setHeader('Access-Control-Allow-Origin', origin);
      }

      if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
      }

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

    this.server.listen(this.port, this.host, () => {
      this.status = 'OPERATIONAL';
      process.stdout.write(`🌐 [API_BRIDGE] Server running on ${this.host}:${this.port}\n`);
    });
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
      if (!this.syncEnabled) {
        res.writeHead(503);
        res.end(JSON.stringify({
          error: 'Sync endpoint disabled. Set AURORA_ENABLE_API_BRIDGE_SYNC=true to enable it.'
        }));
        return;
      }

      if (!isNonEmptyString(this.syncToken)) {
        res.writeHead(503);
        res.end(JSON.stringify({
          error: 'Sync endpoint token not configured'
        }));
        return;
      }

      const providedToken = extractBearerToken(req);
      if (!timingSafeEqualString(this.syncToken, providedToken)) {
        res.writeHead(401);
        res.end(JSON.stringify({
          error: isNonEmptyString(providedToken) ? 'Invalid bridge sync token' : 'Missing bridge sync token'
        }));
        return;
      }

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
      this.status = 'STOPPED';
    }
  }
}

module.exports = ApiBridgeServer;

// Emergency deployment
if (require.main === module) {
  const bridge = new ApiBridgeServer();
  bridge.start();

  process.on('SIGINT', () => {
    bridge.stop();
    process.exit(0);
  });
}
