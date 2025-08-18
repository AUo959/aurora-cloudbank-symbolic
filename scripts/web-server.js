#!/usr/bin/env node
/**
 * Aurora CloudBank Web Server
 * Enhanced development server with logging and WebSocket support
 */

import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

class AuroraWebServer {
    constructor(port = 8000) {
        this.port = port;
        this.app = express();
        this.server = createServer(this.app);
        this.wss = new WebSocketServer({ server: this.server });
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupWebSockets();
    }

    setupMiddleware() {
        // Enable CORS for development
        this.app.use(cors());
        
        // Parse JSON bodies
        this.app.use(express.json({ limit: '10mb' }));
        
        // Security headers
        this.app.use((req, res, next) => {
            res.setHeader('X-Content-Type-Options', 'nosniff');
            res.setHeader('X-Frame-Options', 'SAMEORIGIN');
            res.setHeader('X-XSS-Protection', '1; mode=block');
            res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
            next();
        });

        // Request logging
        this.app.use((req, res, next) => {
            const start = Date.now();
            res.on('finish', () => {
                const duration = Date.now() - start;
                console.log(`[${new Date().toISOString()}] ${req.method} ${req.url} - ${res.statusCode} (${duration}ms)`);
            });
            next();
        });

        // Serve static files
        this.app.use('/static', express.static(path.join(projectRoot, 'static')));
        this.app.use('/build', express.static(path.join(projectRoot, 'build')));
    }

    setupRoutes() {
        // Main application routes
        this.app.get('/', (req, res) => {
            res.sendFile(path.join(projectRoot, 'index.html'));
        });

        this.app.get('/dashboard', (req, res) => {
            res.sendFile(path.join(projectRoot, 'aurora_dashboard.html'));
        });

        // API endpoints for web logging
        this.app.post('/api/logs', (req, res) => {
            const logEntry = req.body;
            this.handleWebLog(logEntry);
            res.json({ status: 'logged' });
        });

        // Mock API endpoints for demo functionality
        this.app.post('/api/vsa/generate', (req, res) => {
            const { symbol, dimension = 32 } = req.body;
            
            // Generate mock vector
            const vector = Array.from({ length: dimension }, () => 
                Math.random() > 0.5 ? 1 : -1
            );
            
            res.json({
                symbol,
                dimension,
                vector: vector.slice(0, 32), // Show first 32 elements
                vector_full_length: dimension,
                vector_type: 'bipolar',
                quantum_generated: true,
                timestamp: new Date().toISOString()
            });
        });

        this.app.post('/api/vsa/bind', (req, res) => {
            const { symbol_a, symbol_b, result_name, dimension = 256 } = req.body;
            
            // Generate mock binding result
            const resultVector = Array.from({ length: Math.min(32, dimension) }, () => 
                Math.random() > 0.5 ? 1 : -1
            );
            
            res.json({
                result_name,
                dimension,
                result_vector: resultVector,
                similarity_a: Math.random() * 0.5 + 0.3,
                similarity_b: Math.random() * 0.5 + 0.3,
                timestamp: new Date().toISOString()
            });
        });

        this.app.post('/api/vsa/similarity', (req, res) => {
            const { symbol_a, symbol_b } = req.body;
            
            res.json({
                cosine_similarity: Math.random() * 0.8 + 0.1,
                hamming_distance: Math.random() * 0.5,
                dot_product: Math.random() * 100 - 50,
                symbols: [symbol_a, symbol_b],
                timestamp: new Date().toISOString()
            });
        });

        this.app.get('/api/vsa/list', (req, res) => {
            res.json({
                count: 5,
                vectors: [
                    { symbol: 'aurora', dimension: 256 },
                    { symbol: 'quantum', dimension: 256 },
                    { symbol: 'symbolic', dimension: 128 },
                    { symbol: 'intelligence', dimension: 512 },
                    { symbol: 'processing', dimension: 256 }
                ]
            });
        });

        this.app.delete('/api/vsa/clear', (req, res) => {
            res.json({
                message: '🧹 VSA vector store cleared (5 vectors removed)',
                timestamp: new Date().toISOString()
            });
        });

        this.app.post('/api/geometric/advanced', (req, res) => {
            const { operation, vectors } = req.body;
            
            let result = '';
            if (operation === 'product') {
                result = `${vectors[0].e1 * vectors[1].e1} + ${vectors[0].e2 * vectors[1].e2}e12`;
            } else if (operation === 'commutator') {
                result = `${vectors[0].e1 - vectors[1].e1}e1 + ${vectors[0].e2 - vectors[1].e2}e2`;
            }
            
            res.json({
                operation,
                input_vectors: vectors,
                results: [{ result }],
                mock_mode: true,
                timestamp: new Date().toISOString()
            });
        });

        this.app.post('/api/quantum/circuit', (req, res) => {
            const { symbol, depth = 3, qubits = 8 } = req.body;
            
            res.json({
                symbol,
                circuit_gates: depth * qubits,
                most_frequent_state: '|' + Math.floor(Math.random() * Math.pow(2, qubits)).toString(2).padStart(qubits, '0') + '⟩',
                most_frequent_probability: Math.random() * 0.3 + 0.2,
                timestamp: new Date().toISOString()
            });
        });

        // Health check
        this.app.get('/api/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                version: '1.0.0'
            });
        });

        // 404 handler
        this.app.use('*', (req, res) => {
            res.status(404).json({ error: 'Not Found' });
        });
    }

    setupWebSockets() {
        this.wss.on('connection', (ws, req) => {
            console.log(`[${new Date().toISOString()}] WebSocket connection established from ${req.connection.remoteAddress}`);
            
            // Send welcome message
            ws.send(JSON.stringify({
                type: 'welcome',
                message: 'Connected to Aurora VSA collaboration hub',
                current_vectors: 5,
                timestamp: new Date().toISOString()
            }));

            ws.on('message', (data) => {
                try {
                    const message = JSON.parse(data);
                    console.log(`[${new Date().toISOString()}] WebSocket message:`, message);
                    
                    // Broadcast to all connected clients
                    this.wss.clients.forEach((client) => {
                        if (client.readyState === client.OPEN) {
                            client.send(JSON.stringify({
                                type: 'vsa_update',
                                user: message.user || 'anonymous',
                                operation: message.operation || 'unknown',
                                symbol: message.symbol || 'unknown',
                                timestamp: new Date().toISOString()
                            }));
                        }
                    });
                } catch (error) {
                    console.error('WebSocket message error:', error);
                }
            });

            ws.on('close', () => {
                console.log(`[${new Date().toISOString()}] WebSocket connection closed`);
            });

            ws.on('error', (error) => {
                console.error(`[${new Date().toISOString()}] WebSocket error:`, error);
            });
        });
    }

    handleWebLog(logEntry) {
        // Store web logs in a separate file
        const logDir = path.join(projectRoot, 'logs');
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        
        const logFile = path.join(logDir, 'web-client.log');
        const logLine = JSON.stringify(logEntry) + '\n';
        
        fs.appendFileSync(logFile, logLine);
    }

    start() {
        this.server.listen(this.port, () => {
            console.log(`🌟 Aurora CloudBank Web Server running on http://localhost:${this.port}`);
            console.log(`📊 Dashboard: http://localhost:${this.port}/dashboard`);
            console.log(`🔌 WebSocket: ws://localhost:${this.port}`);
            console.log(`🔧 API Health: http://localhost:${this.port}/api/health`);
        });

        // Graceful shutdown
        process.on('SIGTERM', () => {
            console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
            this.server.close(() => {
                console.log('✅ Server closed');
                process.exit(0);
            });
        });

        process.on('SIGINT', () => {
            console.log('\n🛑 Received SIGINT, shutting down gracefully...');
            this.server.close(() => {
                console.log('✅ Server closed');
                process.exit(0);
            });
        });
    }
}

// Start server if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const port = process.env.PORT || 8000;
    const server = new AuroraWebServer(port);
    server.start();
}

export default AuroraWebServer;