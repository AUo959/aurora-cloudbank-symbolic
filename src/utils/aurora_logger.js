/**
 * Aurora CloudBank Symbolic - Enhanced Logging System
 * ORION CORE v3.5.1 Compliant Structured Logging
 *
 * Provides ethical, traceable logging with anchor validation
 * Supports L1/L2/L3 layer context and drift monitoring
 */

const fs = require('fs');
const path = require('path');

class AuroraLogger {
  constructor(component = 'AURORA_SYSTEM', options = {}) {
    this.component = component;
    this.logLevel = process.env.LOG_LEVEL || options.level || 'INFO';
    this.enableConsole = options.console !== false;
    this.enableFile = options.file !== false;
    this.anchorSeed = options.anchorSeed || 'EOS_SEED_ORION';
    this.ethicsProtocol = options.ethicsProtocol || 'Picard_Delta_3';

    // Create logs directory if it doesn't exist
    this.logDir = path.join(process.cwd(), 'logs');
    if (this.enableFile && !fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }

    // Log rotation settings
    this.maxFileSize = options.maxFileSize || 10 * 1024 * 1024; // 10MB
    this.maxFiles = options.maxFiles || 5;

    this.sessionId = this.generateSessionId();
  }

  generateSessionId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  formatMessage(level, message, metadata = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      component: this.component,
      message,
      sessionId: this.sessionId,
      anchorSeed: this.anchorSeed,
      ethicsProtocol: this.ethicsProtocol,
      ...metadata,
    };

    return {
      console: `[${timestamp}] ${level} [${this.component}] ${message}${Object.keys(metadata).length ? ' ' + JSON.stringify(metadata) : ''}`,
      structured: logEntry,
    };
  }

  writeToFile(formattedLog) {
    if (!this.enableFile) return;

    try {
      const logFile = path.join(
        this.logDir,
        `aurora-${this.component.toLowerCase()}.log`
      );
      const logLine = JSON.stringify(formattedLog.structured) + '\n';

      // Check file size and rotate if necessary
      if (fs.existsSync(logFile)) {
        const stats = fs.statSync(logFile);
        if (stats.size > this.maxFileSize) {
          this.rotateLogFile(logFile);
        }
      }

      fs.appendFileSync(logFile, logLine);
    } catch (error) {
      // Fallback - minimal error handling to prevent logging loops
      /* eslint-disable no-console */
      if (this.enableConsole) {
        console.error(`[AURORA_LOGGER] File logging failed: ${error.message}`);
      }
      /* eslint-enable no-console */
    }
  }

  rotateLogFile(logFile) {
    try {
      // Move current log to .1, .2, etc.
      for (let i = this.maxFiles - 1; i >= 1; i--) {
        const oldFile = `${logFile}.${i}`;
        const newFile = `${logFile}.${i + 1}`;
        if (fs.existsSync(oldFile)) {
          if (i === this.maxFiles - 1) {
            fs.unlinkSync(oldFile); // Delete oldest
          } else {
            fs.renameSync(oldFile, newFile);
          }
        }
      }

      // Move current log to .1
      if (fs.existsSync(logFile)) {
        fs.renameSync(logFile, `${logFile}.1`);
      }
    } catch {
      // Ignore rotation errors to prevent logging loops
    }
  }

  log(level, message, metadata = {}) {
    if (!this.shouldLog(level)) return;

    const formatted = this.formatMessage(level, message, metadata);

    // Write to console if enabled (ESLint exception for logging utility)
    if (this.enableConsole) {
      /* eslint-disable no-console */
      const consoleMethod =
        level === 'ERROR'
          ? console.error
          : level === 'WARN'
            ? console.warn
            : console.log;
      consoleMethod(formatted.console);
      /* eslint-enable no-console */
    }

    // Write to file
    this.writeToFile(formatted);
  }

  debug(message, metadata = {}) {
    this.log('DEBUG', message, metadata);
  }

  info(message, metadata = {}) {
    this.log('INFO', message, metadata);
  }

  warn(message, metadata = {}) {
    this.log('WARN', message, metadata);
  }

  error(message, metadata = {}) {
    this.log('ERROR', message, metadata);
  }

  // Aurora-specific logging methods
  drift(message, driftValue, metadata = {}) {
    this.log('WARN', message, {
      drift: driftValue,
      threshold: 0.02,
      type: 'DRIFT_MONITORING',
      ...metadata,
    });
  }

  ethics(message, protocol = this.ethicsProtocol, metadata = {}) {
    this.log('INFO', message, {
      ethicsProtocol: protocol,
      type: 'ETHICS_VALIDATION',
      ...metadata,
    });
  }

  anchor(message, seed = this.anchorSeed, metadata = {}) {
    this.log('INFO', message, {
      anchorSeed: seed,
      type: 'ANCHOR_VALIDATION',
      ...metadata,
    });
  }

  bridge(message, fromLayer, toLayer, metadata = {}) {
    this.log('INFO', message, {
      fromLayer,
      toLayer,
      type: 'BRIDGE_COMMUNICATION',
      ...metadata,
    });
  }

  shouldLog(level) {
    const levels = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };
    return levels[level] >= levels[this.logLevel];
  }

  // Graceful shutdown
  shutdown() {
    this.info('Logger shutting down', { component: this.component });
  }
}

// Create singleton instances for common components
const systemLogger = new AuroraLogger('AURORA_SYSTEM');
const bridgeLogger = new AuroraLogger('BRIDGE_AGENTS');
const commandLogger = new AuroraLogger('COMMAND_NODE');
const ethicsLogger = new AuroraLogger('ETHICS_ENGINE');

module.exports = AuroraLogger;
module.exports.systemLogger = systemLogger;
module.exports.bridgeLogger = bridgeLogger;
module.exports.commandLogger = commandLogger;
module.exports.ethicsLogger = ethicsLogger;
