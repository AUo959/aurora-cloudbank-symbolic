#!/usr/bin/env node
/**
 * Aurora CloudBank Web Build Script
 * Optimizes GitHub Pages assets for production deployment
 */

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const BUILD_HTML_FILES = ['index.html', 'aurora_dashboard.html', '404.html'];
const BUILD_SUBDIRECTORIES = Object.freeze({
  js: 'js',
  css: 'css'
});
const PROJECT_FILE_MAP = Object.freeze({
  version: ['VERSION'],
  siteResources: ['static', 'data', 'site-resources.json'],
  deploymentReceipt: ['deployment', 'status', 'latest_check.json'],
  apiCatalog: ['docs', 'api', 'API_CATALOG.json'],
  modules: ['modules'],
  docs: ['docs'],
  tests: ['tests']
});

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
    fs.mkdirSync(this.buildPath(BUILD_SUBDIRECTORIES.js), { recursive: true }); // nosemgrep NOSONAR -- Build output paths are constrained to fixed in-repo directories.
    fs.mkdirSync(this.buildPath(BUILD_SUBDIRECTORIES.css), { recursive: true }); // nosemgrep NOSONAR -- Build output paths are constrained to fixed in-repo directories.
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
        content = content.replaceAll(/static\/js\//g, 'js/');
        content = content.replaceAll(/static\/css\//g, 'css/');
        content = content.replaceAll('static/icon.svg', 'icon.svg');

        fs.writeFileSync(this.buildPath(file), content); // nosemgrep NOSONAR -- HTML outputs are restricted to the checked-in Pages artifact set.
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
      const outputPath = this.buildAssetPath(BUILD_SUBDIRECTORIES.js, relativePath);
      fs.mkdirSync(path.dirname(outputPath), { recursive: true }); // nosemgrep NOSONAR -- The directory is derived from a normalized path under build/js.
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
      const outputPath = this.buildAssetPath(BUILD_SUBDIRECTORIES.css, relativePath);
      fs.mkdirSync(path.dirname(outputPath), { recursive: true }); // nosemgrep NOSONAR -- The directory is derived from a normalized path under build/css.
      fs.writeFileSync(outputPath, content);
      console.log(`🎨 Processed: static/css/${relativePath}`);
    }
  }

  async processStaticAssets() {
    if (!fs.existsSync(this.staticDir)) { // nosemgrep NOSONAR -- staticDir is a fixed repository path.
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
    const cacheSuffix = this.revision ? `-${this.revision}` : '';
    const cacheName = `aurora-cloudbank-v${this.version}${cacheSuffix}`;
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
    ].filter(asset => fs.existsSync(this.buildPath(this.normalizeRelativePath(asset)))); // nosemgrep NOSONAR -- Cache candidates come from a fixed allowlist of Pages assets.

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

    fs.writeFileSync(this.buildPath('sw.js'), swContent); // nosemgrep NOSONAR -- Service worker output path is fixed.
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
      this.buildPath('manifest.json'),
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
      this.buildPath('build-info.json'),
      JSON.stringify(buildInfo, null, 2)
    );

    console.log('📋 Build manifest created');
  }

  async writeSiteData() {
    fs.writeFileSync(
      this.buildPath('site-data.json'),
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

    fs.writeFileSync(this.buildPath('robots.txt'), `${robotsContent}\n`); // nosemgrep NOSONAR -- robots.txt is emitted to a fixed build path.
    console.log('🤖 robots.txt generated');
  }

  async generateSitemap() {
    const pages = [
      '',
      'aurora_dashboard.html',
      'quantum-vsa-demo.html',
      'social-preview.html',
      'synergy-dashboard.html'
    ].filter(relativePath => relativePath === '' || fs.existsSync(this.buildPath(this.normalizeRelativePath(relativePath)))); // nosemgrep NOSONAR -- Sitemap entries come from a fixed Pages allowlist.

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

    fs.writeFileSync(this.buildPath('sitemap.xml'), `${sitemap}\n`); // nosemgrep NOSONAR -- sitemap.xml is emitted to a fixed build path.
    console.log('🗺️ Sitemap generated');
  }

  async generateNoJekyllFile() {
    fs.writeFileSync(this.buildPath('.nojekyll'), ''); // nosemgrep NOSONAR -- .nojekyll is emitted to a fixed build path.
  }

  optimizeHtml(content) {
    // Remove comments and extra whitespace
    let previous;
    do {
      previous = content;
      content = content.replaceAll(/<!--[\s\S]*?-->/g, '');
    } while (content !== previous);
    return content
      .replaceAll(/\s+/g, ' ')
      .replaceAll(/>\s+</g, '><')
      .trim();
  }

  minifyCss(content) {
    return content
      .replaceAll(/\/\*[\s\S]*?\*\//g, '')
      .replaceAll(/\s+/g, ' ')
      .replaceAll(/\s*([{}:;,])\s*/g, '$1')
      .replaceAll(/;}/g, '}')
      .trim();
  }

  minifyJavaScript(content) {
    // Basic minification - remove comments and extra whitespace
    return content
      .replaceAll(/\/\*[\s\S]*?\*\//g, '')
      .replaceAll(/\/\/.*$/gm, '')
      .replaceAll(/\s+/g, ' ')
      .replaceAll(/;\s+/g, ';')
      .trim();
  }

  generateSiteData() {
    const siteResources = this.readJsonFromProject(PROJECT_FILE_MAP.siteResources);
    const deploymentReceipt = this.readJsonFromProject(PROJECT_FILE_MAP.deploymentReceipt, { deployment_check: {} });
    const deployment = deploymentReceipt.deployment_check || {};
    const apiCatalog = this.readJsonFromProject(PROJECT_FILE_MAP.apiCatalog, {});
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
          moduleCount: this.countTopLevelDirectories(this.projectPath(...PROJECT_FILE_MAP.modules)),
          docsCount: this.countProjectFiles('docs'),
          testCount: this.countProjectFiles('tests'),
          resourceCount: Array.isArray(siteResources.resources) ? siteResources.resources.length : 0,
          staticExperienceCount: Array.isArray(siteResources.experiences) ? siteResources.experiences.length : 0
        },
        notes
      }
    };
  }

  readVersion() {
    const versionPath = this.projectPath(...PROJECT_FILE_MAP.version); // nosemgrep NOSONAR -- VERSION is a fixed repository file.
    if (!fs.existsSync(versionPath)) {
      return '0.0.0';
    }

    return fs.readFileSync(versionPath, 'utf8').trim() || '0.0.0'; // nosemgrep NOSONAR -- VERSION is a fixed repository file.
  }

  resolveRevision() {
    const revision = process.env.GITHUB_SHA?.trim();
    if (revision) {
      return revision.slice(0, 7);
    }

    try {
      return execFileSync('git', ['rev-parse', '--short', 'HEAD'], {
        cwd: projectRoot,
        stdio: ['ignore', 'pipe', 'ignore']
      }).toString().trim();
    } catch {
      return null;
    }
  }

  readJsonFile(filePath, fallback = null) {
    if (!fs.existsSync(filePath)) { // nosemgrep NOSONAR -- JSON reads are limited to fixed repository files.
      if (fallback !== null) {
        return fallback;
      }
      throw new Error(`Missing required JSON file: ${filePath}`);
    }

    return JSON.parse(fs.readFileSync(filePath, 'utf8')); // nosemgrep NOSONAR -- JSON reads are limited to fixed repository files.
  }

  readJsonFromProject(relativeSegments, fallback = null) {
    return this.readJsonFile(this.projectPath(...relativeSegments), fallback);
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

  countProjectFiles(relativeDir) {
    if (!Object.hasOwn(PROJECT_FILE_MAP, relativeDir)) {
      throw new Error(`Unsupported project file count target: ${relativeDir}`);
    }

    return this.collectFiles(this.projectPath(...PROJECT_FILE_MAP[relativeDir])).length;
  }

  countTopLevelDirectories(targetDir) {
    if (!fs.existsSync(targetDir)) { // nosemgrep NOSONAR -- Directory counting is limited to fixed repository paths.
      return 0;
    }

    return fs.readdirSync(targetDir, { withFileTypes: true }) // nosemgrep NOSONAR -- Directory counting is limited to fixed repository paths.
      .filter(entry => entry.isDirectory())
      .length;
  }

  collectFiles(targetDir, predicate = () => true) {
    if (!targetDir || !fs.existsSync(targetDir)) { // nosemgrep NOSONAR -- Recursive scans only traverse repository-owned directories.
      return [];
    }

    const files = [];
    const entries = fs.readdirSync(targetDir, { withFileTypes: true }); // nosemgrep NOSONAR -- Recursive scans only traverse repository-owned directories.

    for (const entry of entries) {
      const entryPath = path.resolve(targetDir, entry.name);
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
      .replaceAll('&', '&amp;')
      .replaceAll('"', '&quot;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll("'", '&apos;');
  }

  copyDirectory(src, dest, shouldCopy = () => true, rootDir = src) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }

    const entries = fs.readdirSync(src, { withFileTypes: true });

    for (const entry of entries) {
      const srcPath = path.resolve(src, entry.name);
      const relativePath = this.normalizeRelativePath(path.relative(rootDir, srcPath));
      const destPath = path.resolve(dest, entry.name);

      if (entry.isDirectory()) {
        this.copyDirectory(srcPath, destPath, shouldCopy, rootDir);
      } else if (shouldCopy(relativePath)) {
        fs.copyFileSync(srcPath, destPath);
      }
    }
  }

  normalizeRelativePath(relativePath) {
    const normalizedPath = relativePath.split(path.sep).join('/');
    const safePath = path.posix.normalize(normalizedPath);
    if (
      safePath === '..' ||
      safePath.startsWith('../') ||
      path.posix.isAbsolute(safePath) ||
      safePath.includes('\0')
    ) {
      throw new Error(`Unsafe relative path: ${relativePath}`);
    }
    return safePath;
  }

  safeJoin(baseDir, relativePath) {
    const safeRelativePath = this.normalizeRelativePath(relativePath);
    return path.join(baseDir, ...safeRelativePath.split('/'));
  }

  buildPath(relativePath) {
    return this.safeJoin(this.buildDir, relativePath);
  }

  buildAssetPath(assetDir, relativePath) {
    return this.safeJoin(this.buildPath(assetDir), relativePath);
  }

  projectPath(...segments) {
    return path.join(projectRoot, ...segments);
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
