#!/usr/bin/env node
/**
 * Aurora CloudBank Console Logger Migration Tool
 * Automatically replaces console statements with Aurora logging system
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

class ConsoleLogMigrator {
    constructor() {
        this.processedFiles = 0;
        this.replacementsMade = 0;
        this.errors = [];
        
        // Files to skip (tests, build scripts, etc.)
        this.skipPatterns = [
            /node_modules/,
            /\.git/,
            /build/,
            /dist/,
            /logs/,
            /scripts\/migrate-console/,
            /test.*\.js$/,
            /spec.*\.js$/
        ];
        
        // Console method mappings to Aurora logger methods
        this.consoleMappings = {
            'console.log': 'systemLogger.info',
            'console.info': 'systemLogger.info',
            'console.warn': 'systemLogger.warn',
            'console.error': 'systemLogger.error',
            'console.debug': 'systemLogger.debug'
        };
    }

    shouldSkipFile(filePath) {
        return this.skipPatterns.some(pattern => pattern.test(filePath));
    }

    async migrateFile(filePath) {
        if (this.shouldSkipFile(filePath)) {
            return false;
        }

        try {
            const content = fs.readFileSync(filePath, 'utf8');
            let modifiedContent = content;
            let fileModified = false;
            
            // Check if file needs Aurora logger import
            const needsLogger = /console\.(log|info|warn|error|debug)/.test(content);
            
            if (!needsLogger) {
                return false;
            }

            // Add Aurora logger import if needed
            // Robustly check for any import/require of Aurora logger or systemLogger
            const loggerImportRegex = /(?:import\s+(?:.*\bAuroraLogger\b.*|.*\bsystemLogger\b.*)\s+from\s+['"][^'"]*aurora[^'"]*['"])|(?:require\s*\(\s*['"][^'"]*aurora[^'"]*['"]\s*\))/i;
            if (!loggerImportRegex.test(content)) {
                const loggerImport = this.generateLoggerImport(filePath);
                modifiedContent = loggerImport + '\n' + modifiedContent;
                fileModified = true;
            }

            // Replace console statements
            for (const [consoleMethod, loggerMethod] of Object.entries(this.consoleMappings)) {
                const regex = new RegExp(
                    `${consoleMethod.replace('.', '\\.')}\\s*\\(([^)]+)\\)`,
                    'g'
                );
                
                const matches = [...modifiedContent.matchAll(regex)];
                
                for (const match of matches) {
                    const originalCall = match[0];
                    const args = match[1];
                    
                    // Parse arguments to create proper logger call
                    const replacement = this.createLoggerReplacement(loggerMethod, args);
                    modifiedContent = modifiedContent.replace(originalCall, replacement);
                    fileModified = true;
                    this.replacementsMade++;
                }
            }

            if (fileModified) {
                fs.writeFileSync(filePath, modifiedContent);
                this.processedFiles++;
                console.log(`✅ Migrated: ${path.relative(projectRoot, filePath)}`);
                return true;
            }
            
            return false;
        } catch (error) {
            this.errors.push({ file: filePath, error: error.message });
            console.error(`❌ Error processing ${filePath}: ${error.message}`);
            return false;
        }
    }

    generateLoggerImport(filePath) {
        const isNodeModule = !filePath.includes('/static/') && !filePath.includes('/build/');
        
        if (isNodeModule) {
            return `// Aurora Logger Integration
let AuroraLogger;
try {
  AuroraLogger = require('./src/utils/aurora_logger.js');
} catch (error) {
  AuroraLogger = class {
    constructor() {}
    info(msg, meta = {}) { console.log(\`[INFO] \${msg}\`, meta); }
    warn(msg, meta = {}) { console.warn(\`[WARN] \${msg}\`, meta); }
    error(msg, meta = {}) { console.error(\`[ERROR] \${msg}\`, meta); }
    debug(msg, meta = {}) { console.debug(\`[DEBUG] \${msg}\`, meta); }
  };
}
const systemLogger = new AuroraLogger('${this.getComponentName(filePath)}');`;
        } else {
            return `// Aurora Web Logger Integration
const systemLogger = window.auroraLogger || {
  info: (msg, meta) => console.log(\`[INFO] \${msg}\`, meta),
  warn: (msg, meta) => console.warn(\`[WARN] \${msg}\`, meta),
  error: (msg, meta) => console.error(\`[ERROR] \${msg}\`, meta),
  debug: (msg, meta) => console.debug(\`[DEBUG] \${msg}\`, meta)
};`;
        }
    }

    getComponentName(filePath) {
        const fileName = path.basename(filePath, '.js');
        return fileName.toUpperCase().replace(/[^A-Z0-9]/g, '_');
    }

    createLoggerReplacement(loggerMethod, args) {
        // Simple argument parsing - for more complex cases, manual review needed
        const trimmedArgs = args.trim();
        
        // If it's a simple string, convert to proper logger format
        if (trimmedArgs.startsWith("'") || trimmedArgs.startsWith('"') || trimmedArgs.startsWith('`')) {
            return `${loggerMethod}(${trimmedArgs})`;
        }
        
        // If it's a template literal or concatenation, keep as is but use logger
        if (trimmedArgs.includes('${') || trimmedArgs.includes('+')) {
            return `${loggerMethod}(${trimmedArgs})`;
        }
        
        // For multiple arguments, try to format as message + metadata
        const argList = this.parseArguments(trimmedArgs);
        if (argList.length > 1) {
            const message = argList[0];
            const metadata = argList.slice(1).join(', ');
            return `${loggerMethod}(${message}, { details: [${metadata}] })`;
        }
        
        return `${loggerMethod}(${trimmedArgs})`;
    }

    parseArguments(argsString) {
        // Simple argument parsing - splits on comma but respects quotes
        const args = [];
        let current = '';
        let inQuotes = false;
        let quoteChar = '';
        let depth = 0;
        
        for (let i = 0; i < argsString.length; i++) {
            const char = argsString[i];
            
            if (!inQuotes && (char === '"' || char === "'" || char === '`')) {
                inQuotes = true;
                quoteChar = char;
                current += char;
            } else if (inQuotes && char === quoteChar) {
                inQuotes = false;
                current += char;
            } else if (!inQuotes && char === '(') {
                depth++;
                current += char;
            } else if (!inQuotes && char === ')') {
                depth--;
                current += char;
            } else if (!inQuotes && char === ',' && depth === 0) {
                args.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        
        if (current.trim()) {
            args.push(current.trim());
        }
        
        return args;
    }

    async migrateDirectory(dirPath) {
        const entries = fs.readdirSync(dirPath, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dirPath, entry.name);
            
            if (entry.isDirectory()) {
                await this.migrateDirectory(fullPath);
            } else if (entry.isFile() && entry.name.endsWith('.js')) {
                await this.migrateFile(fullPath);
            }
        }
    }

    async migrate() {
        console.log('🚀 Starting Aurora Console Logger Migration...');
        console.log('This will replace console.* statements with Aurora logging system.');
        console.log('');
        
        await this.migrateDirectory(projectRoot);
        
        console.log('');
        console.log('📊 Migration Summary:');
        console.log(`  Files processed: ${this.processedFiles}`);
        console.log(`  Console replacements: ${this.replacementsMade}`);
        console.log(`  Errors: ${this.errors.length}`);
        
        if (this.errors.length > 0) {
            console.log('');
            console.log('❌ Errors encountered:');
            for (const error of this.errors) {
                console.log(`  ${error.file}: ${error.error}`);
            }
        }
        
        console.log('');
        console.log('✅ Migration complete!');
        console.log('📝 Please review the changes and test thoroughly.');
        console.log('🔧 Some complex console statements may need manual adjustment.');
    }
}

// Run migration if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const migrator = new ConsoleLogMigrator();
    migrator.migrate().catch(console.error);
}

export default ConsoleLogMigrator;