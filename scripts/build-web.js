#!/usr/bin/env node
/**
 * Aurora CloudBank Web Build Script
 * Optimizes web assets for production deployment
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

class AuroraWebBuilder {
    constructor() {
        this.buildDir = path.join(projectRoot, 'build');
        this.staticDir = path.join(projectRoot, 'static');
        this.srcDir = path.join(projectRoot, 'src');
        this.isProduction = process.env.NODE_ENV === 'production';
    }

    async build() {
        console.log('🚀 Starting Aurora CloudBank Web Build...');
        
        // Create build directory
        await this.createBuildDirectory();
        
        // Process HTML files
        await this.processHtmlFiles();
        
        // Process JavaScript files  
        await this.processJavaScriptFiles();
        
        // Process CSS and static assets
        await this.processStaticAssets();
        
        // Generate service worker for PWA support
        await this.generateServiceWorker();
        
        // Create build manifest
        await this.createBuildManifest();
        
        console.log('✅ Aurora CloudBank Web Build Complete!');
        console.log(`📦 Build files: ${this.buildDir}`);
    }

    async createBuildDirectory() {
        if (fs.existsSync(this.buildDir)) {
            fs.rmSync(this.buildDir, { recursive: true });
        }
        fs.mkdirSync(this.buildDir, { recursive: true });
        fs.mkdirSync(path.join(this.buildDir, 'js'), { recursive: true });
        fs.mkdirSync(path.join(this.buildDir, 'css'), { recursive: true });
        console.log('📁 Build directory created');
    }

    async processHtmlFiles() {
        const htmlFiles = ['index.html', 'aurora_dashboard.html'];
        
        for (const file of htmlFiles) {
            const filePath = path.join(projectRoot, file);
            if (fs.existsSync(filePath)) {
                let content = fs.readFileSync(filePath, 'utf8');
                
                // Optimize HTML for production
                if (this.isProduction) {
                    content = this.optimizeHtml(content);
                }
                
                // Update asset paths for build
                content = content.replace(/static\/js\//g, 'js/');
                content = content.replace(/static\/css\//g, 'css/');
                
                fs.writeFileSync(path.join(this.buildDir, file), content);
                console.log(`📄 Processed: ${file}`);
            }
        }
    }

    async processJavaScriptFiles() {
        // Process main application files
        const jsFiles = [
            'static/js/aurora-security.js'
        ];
        
        for (const file of jsFiles) {
            const filePath = path.join(projectRoot, file);
            if (fs.existsSync(filePath)) {
                let content = fs.readFileSync(filePath, 'utf8');
                
                // Basic minification for production
                if (this.isProduction) {
                    content = this.minifyJavaScript(content);
                }
                
                const outputPath = path.join(this.buildDir, 'js', path.basename(file));
                fs.writeFileSync(outputPath, content);
                console.log(`🔧 Processed: ${file}`);
            }
        }
    }

    async processStaticAssets() {
        // Copy static assets to build directory
        const staticFiles = path.join(this.staticDir);
        if (fs.existsSync(staticFiles)) {
            this.copyDirectory(staticFiles, path.join(this.buildDir));
            console.log('📂 Static assets copied');
        }
    }

    async generateServiceWorker() {
        const swContent = `
// Aurora CloudBank Service Worker v1.0.0
const CACHE_NAME = 'aurora-cloudbank-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/aurora_dashboard.html',
    '/js/aurora-security.js'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});
`;
        
        fs.writeFileSync(path.join(this.buildDir, 'sw.js'), swContent);
        console.log('⚙️ Service worker generated');
    }

    async createBuildManifest() {
        const manifest = {
            name: "Aurora CloudBank Symbolic",
            short_name: "Aurora CloudBank",
            description: "Quantum-Aware Symbolic Processing Framework",
            start_url: "/",
            display: "standalone",
            background_color: "#1e3c72",
            theme_color: "#2a5298",
            icons: [
                {
                    src: "icon-192.png",
                    sizes: "192x192",
                    type: "image/png"
                },
                {
                    src: "icon-512.png", 
                    sizes: "512x512",
                    type: "image/png"
                }
            ]
        };
        
        fs.writeFileSync(
            path.join(this.buildDir, 'manifest.json'), 
            JSON.stringify(manifest, null, 2)
        );
        
        // Build info
        const buildInfo = {
            version: "1.0.0",
            buildTime: new Date().toISOString(),
            environment: this.isProduction ? 'production' : 'development',
            features: [
                'quantum-vsa-processing',
                'real-time-collaboration',
                'geometric-algebra',
                'symbolic-reasoning'
            ]
        };
        
        fs.writeFileSync(
            path.join(this.buildDir, 'build-info.json'),
            JSON.stringify(buildInfo, null, 2)
        );
        
        console.log('📋 Build manifest created');
    }

    optimizeHtml(content) {
        // Remove comments and extra whitespace
        return content
            .replace(/<!--[\s\S]*?-->/g, '')
            .replace(/\s+/g, ' ')
            .replace(/>\s+</g, '><')
            .trim();
    }

    minifyJavaScript(content) {
        // Basic minification - remove comments and extra whitespace
        return content
            .replace(/\/\*[\s\S]*?\*\//g, '')
            .replace(/\/\/.*$/gm, '')
            .replace(/\s+/g, ' ')
            .replace(/;\s+/g, ';')
            .trim();
    }

    copyDirectory(src, dest) {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        
        const entries = fs.readdirSync(src, { withFileTypes: true });
        
        for (const entry of entries) {
            const srcPath = path.join(src, entry.name);
            const destPath = path.join(dest, entry.name);
            
            if (entry.isDirectory()) {
                this.copyDirectory(srcPath, destPath);
            } else {
                fs.copyFileSync(srcPath, destPath);
            }
        }
    }
}

// Run build if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const builder = new AuroraWebBuilder();
    builder.build().catch(console.error);
}

export default AuroraWebBuilder;