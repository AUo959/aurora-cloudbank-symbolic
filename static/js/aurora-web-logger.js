/**
 * Aurora CloudBank Web Logger
 * Browser-compatible logging system with Aurora anchoring
 */

class AuroraWebLogger {
    constructor(component = 'WEB_CLIENT', options = {}) {
        this.component = component;
        this.logLevel = options.level || 'INFO';
        this.enableConsole = options.console !== false;
        this.enableStorage = options.storage !== false;
        this.anchorSeed = options.anchorSeed || 'EOS_SEED_ORION';
        this.ethicsProtocol = options.ethicsProtocol || 'Picard_Delta_3';
        this.maxStorageEntries = options.maxStorageEntries || 1000;
        
        this.sessionId = this.generateSessionId();
        this.logBuffer = [];
        
        // Initialize web-specific features
        this.initializeWebFeatures();
    }

    generateSessionId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    initializeWebFeatures() {
        // Set up performance monitoring
        if (typeof window !== 'undefined' && window.performance) {
            this.startTime = window.performance.now();
        }
        
        // Set up error capture
        if (typeof window !== 'undefined') {
            window.addEventListener('error', (event) => {
                this.error('Uncaught error', {
                    message: event.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno,
                    error: event.error?.stack
                });
            });
            
            window.addEventListener('unhandledrejection', (event) => {
                this.error('Unhandled promise rejection', {
                    reason: event.reason,
                    promise: event.promise
                });
            });
        }
    }

    formatMessage(level, message, metadata = {}) {
        const timestamp = new Date().toISOString();
        const performance = this.getPerformanceMetrics();
        
        return {
            timestamp,
            level,
            component: this.component,
            message,
            sessionId: this.sessionId,
            anchorSeed: this.anchorSeed,
            ethicsProtocol: this.ethicsProtocol,
            performance,
            ...metadata
        };
    }

    getPerformanceMetrics() {
        if (typeof window === 'undefined' || !window.performance) {
            return { timing: 'unavailable' };
        }
        
        const now = window.performance.now();
        return {
            sessionDuration: Math.round(now - this.startTime),
            memoryUsage: window.performance.memory ? {
                used: Math.round(window.performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(window.performance.memory.totalJSHeapSize / 1024 / 1024),
                limit: Math.round(window.performance.memory.jsHeapSizeLimit / 1024 / 1024)
            } : 'unavailable'
        };
    }

    log(level, message, metadata = {}) {
        const logEntry = this.formatMessage(level, message, metadata);
        
        // Add to buffer
        this.logBuffer.push(logEntry);
        if (this.logBuffer.length > this.maxStorageEntries) {
            this.logBuffer.shift();
        }
        
        // Store in localStorage if enabled
        if (this.enableStorage && typeof localStorage !== 'undefined') {
            this.storeLogEntry(logEntry);
        }
        
        // Console output if enabled
        if (this.enableConsole && this.shouldLog(level)) {
            this.consoleOutput(level, logEntry);
        }
        
        // Send to backend if endpoint available
        this.sendToBackend(logEntry);
    }

    storeLogEntry(logEntry) {
        try {
            const storageKey = `aurora_logs_${this.component.toLowerCase()}`;
            let storedLogs = JSON.parse(localStorage.getItem(storageKey) || '[]');
            
            storedLogs.push(logEntry);
            if (storedLogs.length > this.maxStorageEntries) {
                storedLogs = storedLogs.slice(-this.maxStorageEntries);
            }
            
            localStorage.setItem(storageKey, JSON.stringify(storedLogs));
        } catch (error) {
            // Fallback if localStorage is full or unavailable
            console.warn('Failed to store log entry:', error);
        }
    }

    consoleOutput(level, logEntry) {
        const style = this.getConsoleStyle(level);
        const prefix = `[${logEntry.timestamp}] ${logEntry.component}`;
        
        switch (level) {
            case 'ERROR':
                console.error(`%c${prefix}`, style, logEntry.message, logEntry);
                break;
            case 'WARN':
                console.warn(`%c${prefix}`, style, logEntry.message, logEntry);
                break;
            case 'INFO':
                console.info(`%c${prefix}`, style, logEntry.message, logEntry);
                break;
            case 'DEBUG':
                console.debug(`%c${prefix}`, style, logEntry.message, logEntry);
                break;
            default:
                console.log(`%c${prefix}`, style, logEntry.message, logEntry);
        }
    }

    getConsoleStyle(level) {
        const baseStyle = 'font-weight: bold; padding: 2px 6px; border-radius: 3px;';
        switch (level) {
            case 'ERROR': return baseStyle + 'background: #ff4444; color: white;';
            case 'WARN': return baseStyle + 'background: #ff8800; color: white;';
            case 'INFO': return baseStyle + 'background: #0099ff; color: white;';
            case 'DEBUG': return baseStyle + 'background: #888888; color: white;';
            default: return baseStyle + 'background: #333333; color: white;';
        }
    }

    async sendToBackend(logEntry) {
        try {
            if (typeof fetch !== 'undefined') {
                await fetch('/api/logs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(logEntry)
                }).catch(() => {}); // Fail silently if backend unavailable
            }
        } catch (error) {
            // Fail silently - logging should not break the app
        }
    }

    shouldLog(level) {
        const levels = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };
        return levels[level] >= levels[this.logLevel];
    }

    // Aurora-specific logging methods
    drift(message, driftValue, metadata = {}) {
        this.log('WARN', message, {
            drift: driftValue,
            threshold: 0.02,
            type: 'DRIFT_MONITORING',
            ...metadata
        });
    }

    ethics(message, protocol = this.ethicsProtocol, metadata = {}) {
        this.log('INFO', message, {
            ethicsProtocol: protocol,
            type: 'ETHICS_VALIDATION',
            ...metadata
        });
    }

    anchor(message, seed = this.anchorSeed, metadata = {}) {
        this.log('INFO', message, {
            anchorSeed: seed,
            type: 'ANCHOR_VALIDATION',
            ...metadata
        });
    }

    bridge(message, fromLayer, toLayer, metadata = {}) {
        this.log('INFO', message, {
            fromLayer,
            toLayer,
            type: 'BRIDGE_COMMUNICATION',
            ...metadata
        });
    }

    // Standard logging methods
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

    // Utility methods
    getStoredLogs() {
        const storageKey = `aurora_logs_${this.component.toLowerCase()}`;
        try {
            return JSON.parse(localStorage.getItem(storageKey) || '[]');
        } catch {
            return [];
        }
    }

    clearStoredLogs() {
        const storageKey = `aurora_logs_${this.component.toLowerCase()}`;
        try {
            localStorage.removeItem(storageKey);
        } catch {
            // Fail silently
        }
    }

    exportLogs() {
        const logs = this.getStoredLogs();
        const blob = new Blob([JSON.stringify(logs, null, 2)], { 
            type: 'application/json' 
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `aurora-logs-${this.component}-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Create singleton instances for different components
const webLogger = new AuroraWebLogger('WEB_CLIENT');
const quantumLogger = new AuroraWebLogger('QUANTUM_VSA');
const bridgeLogger = new AuroraWebLogger('BRIDGE_CLIENT');
const uiLogger = new AuroraWebLogger('UI_COMPONENTS');

// Export for both ES modules and CommonJS
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuroraWebLogger;
    module.exports.webLogger = webLogger;
    module.exports.quantumLogger = quantumLogger;
    module.exports.bridgeLogger = bridgeLogger;
    module.exports.uiLogger = uiLogger;
}

// Global assignment for browser use
if (typeof window !== 'undefined') {
    window.AuroraWebLogger = AuroraWebLogger;
    window.auroraLogger = webLogger;
    window.quantumLogger = quantumLogger;
    window.bridgeLogger = bridgeLogger;
    window.uiLogger = uiLogger;
}