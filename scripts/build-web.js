#!/usr/bin/env node
/**
 * Aurora CloudBank Web Build Script
 * Optimizes GitHub Pages assets for production deployment
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const BUILD_HTML_FILES = ['index.html', 'aurora_dashboard.html', '404.html'];

class AuroraWebBuilder {
  constructor() {
    this.buildDir = path.join(projectRoot, 'build');
    this.staticDir = path.join(projectRoot, 'static');
    this.isProduction = process.env.NODE_ENV === 'production';
    this.generatedAt = new Date().toISOString();
    this.version = this.readVersion();
    this.revision = this.resolveRevision();
    this.siteData = null;
  }

  async build() {
    console.log('🚀 Starting Aurora CloudBank Web Build...');

    // Create build directory
    await this.createBuildDirectory();

    this.siteData = this.generateSiteData();

    // Process HTML files
    await this.processHtmlFiles();

    // Process JavaScript files
    await this.processJavaScriptFiles();

    // Process CSS and static assets
    await this.processStylesheets();
    await this.processStaticAssets();

    // Generate Pages metadata and support files
    await this.writeSiteData();
    await this.generateRobotsTxt();
    await this.generateSitemap();
    await this.generateNoJekyllFile();
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
    for (const file of BUILD_HTML_FILES) {
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
        content = content.replace(/static\/icon\.svg/g, 'icon.svg');

        fs.writeFileSync(path.join(this.buildDir, file), content);
        console.log(`📄 Processed: ${file}`);
      }
    }
  }

  async processJavaScriptFiles() {
    const jsDir = path.join(projectRoot, 'static', 'js');
    const jsFiles = this.collectFiles(jsDir, filePath => filePath.endsWith('.js'));

    for (const filePath of jsFiles) {
      let content = fs.readFileSync(filePath, 'utf8');

      if (this.isProduction) {
        content = this.minifyJavaScript(content);
      }

      const relativePath = path.relative(jsDir, filePath);
      const outputPath = path.join(this.buildDir, 'js', relativePath);
      fs.mkdirSync(path.dirname(outputPath), { recursive: true });
      fs.writeFileSync(outputPath, content);
      console.log(`🔧 Processed: static/js/${relativePath}`);
    }
  }

  async processStylesheets() {
    const cssDir = path.join(projectRoot, 'static', 'css');
    const cssFiles = this.collectFiles(cssDir, filePath => filePath.endsWith('.css'));

    for (const filePath of cssFiles) {
      let content = fs.readFileSync(filePath, 'utf8');

      if (this.isProduction) {
        content = this.minifyCss(content);
      }

      const relativePath = path.relative(cssDir, filePath);
      const outputPath = path.join(this.buildDir, 'css', relativePath);
      fs.mkdirSync(path.dirname(outputPath), { recursive: true });
      fs.writeFileSync(outputPath, content);
      console.log(`🎨 Processed: static/css/${relativePath}`);
    }
  }

  async processStaticAssets() {
    if (!fs.existsSync(this.staticDir)) {
      return;
    }

    this.copyDirectory(this.staticDir, this.buildDir, relativePath => {
      const normalizedPath = relativePath.split(path.sep).join('/');
      if (normalizedPath === 'index.html') {
        return false;
      }
      if (normalizedPath.startsWith('js/') || normalizedPath.startsWith('css/')) {
        return false;
      }
      return true;
    });

    console.log('📂 Static assets copied');
  }

  async generateServiceWorker() {
    const cacheName = `aurora-cloudbank-v${this.version}${this.revision ? `-${this.revision}` : ''}`;
    const urlsToCache = [
      './',
      'index.html',
      '404.html',
      'aurora_dashboard.html',
      'manifest.json',
      'site-data.json',
      'robots.txt',
      'sitemap.xml',
      'icon.svg',
      'css/site.css',
      'js/aurora-security.js',
      'js/aurora-web-logger.js',
      'js/site-launchpad.js',
      'js/synergy-dashboard.js',
      'quantum-vsa-demo.html',
      'social-preview.html',
      'synergy-dashboard.html'
    ].filter(asset => fs.existsSync(path.join(this.buildDir, asset)));

    const swContent = `
// Aurora CloudBank Service Worker v${this.version}
const CACHE_NAME = ${JSON.stringify(cacheName)};
const URLS_TO_CACHE = ${JSON.stringify(urlsToCache, null, 2)};

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(URLS_TO_CACHE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => Promise.all(
      cacheNames
        .filter(cacheName => cacheName !== CACHE_NAME)
        .map(cacheName => caches.delete(cacheName))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request)
        .then(networkResponse => {
          if (
            event.request.url.startsWith(self.location.origin) &&
            networkResponse.ok
          ) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
          }
          return networkResponse;
        })
        .catch(() => {
          if (event.request.mode === 'navigate') {
            return caches.match('404.html');
          }
          return Response.error();
        });
    })
  );
});
`;

    fs.writeFileSync(path.join(this.buildDir, 'sw.js'), swContent);
    console.log('⚙️ Service worker generated');
  }

  async createBuildManifest() {
    const manifest = {
      name: this.siteData.site.name,
      short_name: 'Aurora',
      description: this.siteData.site.description,
      start_url: './',
      scope: './',
      display: 'standalone',
      background_color: '#07141b',
      theme_color: '#07141b',
      icons: [
        {
          src: 'icon.svg',
          sizes: 'any',
          type: 'image/svg+xml',
          purpose: 'any'
        }
      ],
      shortcuts: [
        {
          name: 'Launchpad',
          short_name: 'Launchpad',
          url: './index.html'
        },
        {
          name: 'Deployment Dashboard',
          short_name: 'Dashboard',
          url: './aurora_dashboard.html'
        },
        {
          name: 'Quantum VSA Demo',
          short_name: 'Quantum Demo',
          url: './quantum-vsa-demo.html'
        }
      ]
    };

    fs.writeFileSync(
      path.join(this.buildDir, 'manifest.json'),
      JSON.stringify(manifest, null, 2)
    );

    // Build info
    const buildInfo = {
      version: this.version,
      revision: this.revision,
      buildTime: this.generatedAt,
      environment: this.isProduction ? 'production' : 'development',
      pagesUrl: this.siteData.site.pagesUrl,
      deployment: this.siteData.generated.deployment,
      metrics: this.siteData.generated.metrics
    };

    fs.writeFileSync(
      path.join(this.buildDir, 'build-info.json'),
      JSON.stringify(buildInfo, null, 2)
    );

    console.log('📋 Build manifest created');
  }

  async writeSiteData() {
    fs.writeFileSync(
      path.join(this.buildDir, 'site-data.json'),
      JSON.stringify(this.siteData, null, 2)
    );
    console.log('🧭 Site data generated');
  }

  async generateRobotsTxt() {
    const robotsContent = [
      'User-agent: *',
      'Allow: /',
      `Sitemap: ${this.toSiteUrl('sitemap.xml')}`
    ].join('\n');

    fs.writeFileSync(path.join(this.buildDir, 'robots.txt'), `${robotsContent}\n`);
    console.log('🤖 robots.txt generated');
  }

  async generateSitemap() {
    const pages = [
      '',
      'aurora_dashboard.html',
      'quantum-vsa-demo.html',
      'social-preview.html',
      'synergy-dashboard.html'
    ].filter(relativePath => relativePath === '' || fs.existsSync(path.join(this.buildDir, relativePath)));

    const urls = pages.map(relativePath => {
      const location = relativePath ? this.toSiteUrl(relativePath) : this.normalizeSiteUrl(this.siteData.site.pagesUrl);
      return [
        '  <url>',
        `    <loc>${this.escapeXml(location)}</loc>`,
        `    <lastmod>${this.generatedAt}</lastmod>`,
        '  </url>'
      ].join('\n');
    }).join('\n');

    const sitemap = [
      '<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
      urls,
      '</urlset>'
    ].join('\n');

    fs.writeFileSync(path.join(this.buildDir, 'sitemap.xml'), `${sitemap}\n`);
    console.log('🗺️ Sitemap generated');
  }

  async generateNoJekyllFile() {
    fs.writeFileSync(path.join(this.buildDir, '.nojekyll'), '');
  }

  optimizeHtml(content) {
    // Remove comments and extra whitespace
    let previous;
    do {
      previous = content;
      content = content.replace(/<!--[\s\S]*?-->/g, '');
    } while (content !== previous);
    return content
      .replace(/\s+/g, ' ')
      .replace(/>\s+</g, '><')
      .trim();
  }

  minifyCss(content) {
    return content
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/\s+/g, ' ')
      .replace(/\s*([{}:;,])\s*/g, '$1')
      .replace(/;}/g, '}')
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

  generateSiteData() {
    const siteResources = this.readJsonFile(path.join(this.staticDir, 'data', 'site-resources.json'));
    const deploymentReceipt = this.readJsonFile(path.join(projectRoot, 'deployment', 'status', 'latest_check.json'), { deployment_check: {} });
    const deployment = deploymentReceipt.deployment_check || {};
    const apiCatalog = this.readJsonFile(path.join(projectRoot, 'docs', 'api', 'API_CATALOG.json'), {});
    const routeEntries = Array.isArray(apiCatalog.routes) ? apiCatalog.routes.length : 0;
    const reportedRouteCount = typeof apiCatalog.total_routes === 'number' ? apiCatalog.total_routes : null;
    const notes = [];

    if (reportedRouteCount !== null && reportedRouteCount !== routeEntries) {
      notes.push(`API catalog mismatch: docs/api/API_CATALOG.json reports total_routes=${reportedRouteCount}, but the routes array currently contains ${routeEntries} entries.`);
    }

    if (deployment.timestamp) {
      const ageInDays = this.calculateAgeInDays(deployment.timestamp);
      if (ageInDays >= 30) {
        notes.push(`Latest tracked deployment receipt is dated ${this.formatCalendarDate(deployment.timestamp)}. Treat it as committed evidence, not live runtime state.`);
      }
    } else {
      notes.push('No tracked deployment receipt was found in deployment/status/latest_check.json.');
    }

    return {
      ...siteResources,
      generated: {
        buildTime: this.generatedAt,
        version: this.version,
        revision: this.revision,
        deployment: {
          status: deployment.status || 'UNKNOWN',
          readinessPercent: deployment.readiness_percent ?? 0,
          readinessScore: deployment.readiness_score ?? null,
          timestamp: deployment.timestamp || null,
          l1Ready: Boolean(deployment.l1_ready),
          l3Ready: Boolean(deployment.l3_ready),
          crewReady: Boolean(deployment.crew_ready)
        },
        metrics: {
          apiRouteEntries: routeEntries,
          apiRouteEntriesReported: reportedRouteCount,
          moduleCount: this.countTopLevelDirectories(path.join(projectRoot, 'modules')),
          docsCount: this.countTrackedFiles('docs'),
          testCount: this.countTrackedFiles('tests'),
          resourceCount: Array.isArray(siteResources.resources) ? siteResources.resources.length : 0,
          staticExperienceCount: Array.isArray(siteResources.experiences) ? siteResources.experiences.length : 0
        },
        notes
      }
    };
  }

  readVersion() {
    const versionPath = path.join(projectRoot, 'VERSION');
    if (!fs.existsSync(versionPath)) {
      return '0.0.0';
    }

    return fs.readFileSync(versionPath, 'utf8').trim() || '0.0.0';
  }

  resolveRevision() {
    const revision = process.env.GITHUB_SHA?.trim();
    if (revision) {
      return revision.slice(0, 7);
    }

    try {
      return execSync('git rev-parse --short HEAD', {
        cwd: projectRoot,
        stdio: ['ignore', 'pipe', 'ignore']
      }).toString().trim();
    } catch {
      return null;
    }
  }

  readJsonFile(filePath, fallback = null) {
    if (!fs.existsSync(filePath)) {
      if (fallback !== null) {
        return fallback;
      }
      throw new Error(`Missing required JSON file: ${filePath}`);
    }

    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  }

  calculateAgeInDays(timestamp) {
    const parsed = new Date(timestamp);
    if (Number.isNaN(parsed.getTime())) {
      return 0;
    }

    const deltaMs = new Date(this.generatedAt).getTime() - parsed.getTime();
    return Math.max(0, Math.floor(deltaMs / (1000 * 60 * 60 * 24)));
  }

  formatCalendarDate(timestamp) {
    const parsed = new Date(timestamp);
    if (Number.isNaN(parsed.getTime())) {
      return timestamp;
    }

    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timeZone: 'UTC'
    }).format(parsed);
  }

  countTrackedFiles(relativeDir) {
    try {
      const output = execSync(`git ls-files ${relativeDir}`, {
        cwd: projectRoot,
        stdio: ['ignore', 'pipe', 'ignore']
      }).toString().trim();

      if (!output) {
        return 0;
      }

      return output.split('\n').filter(Boolean).length;
    } catch {
      return this.collectFiles(path.join(projectRoot, relativeDir)).length;
    }
  }

  countTopLevelDirectories(targetDir) {
    if (!fs.existsSync(targetDir)) {
      return 0;
    }

    return fs.readdirSync(targetDir, { withFileTypes: true })
      .filter(entry => entry.isDirectory())
      .length;
  }

  collectFiles(targetDir, predicate = () => true) {
    if (!targetDir || !fs.existsSync(targetDir)) {
      return [];
    }

    const files = [];
    const entries = fs.readdirSync(targetDir, { withFileTypes: true });

    for (const entry of entries) {
      const entryPath = path.join(targetDir, entry.name);
      if (entry.isDirectory()) {
        files.push(...this.collectFiles(entryPath, predicate));
      } else if (predicate(entryPath)) {
        files.push(entryPath);
      }
    }

    return files;
  }

  normalizeSiteUrl(siteUrl) {
    return siteUrl.endsWith('/') ? siteUrl : `${siteUrl}/`;
  }

  toSiteUrl(relativePath) {
    return new URL(relativePath, this.normalizeSiteUrl(this.siteData.site.pagesUrl)).toString();
  }

  escapeXml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/'/g, '&apos;');
  }

  copyDirectory(src, dest, shouldCopy = () => true, rootDir = src) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }

    const entries = fs.readdirSync(src, { withFileTypes: true });

    for (const entry of entries) {
      const srcPath = path.join(src, entry.name);
      const destPath = path.join(dest, entry.name);

      if (entry.isDirectory()) {
        this.copyDirectory(srcPath, destPath, shouldCopy, rootDir);
      } else if (shouldCopy(path.relative(rootDir, srcPath))) {
        fs.copyFileSync(srcPath, destPath);
      }
    }
  }
}

// Resolve relative CLI paths so `node scripts/build-web.js` works in CI and locally.
const invokedModuleUrl = process.argv[1]
  ? pathToFileURL(path.resolve(process.argv[1])).href
  : null;

// Run build if called directly
if (invokedModuleUrl && import.meta.url === invokedModuleUrl) {
  const builder = new AuroraWebBuilder();
  builder.build().catch(console.error);
}

export default AuroraWebBuilder;
