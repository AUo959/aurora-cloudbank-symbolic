/**
 * Aurora CloudBank Security Middleware
 * Provides comprehensive security headers and protection
 */

const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const sanitizeHtml = require('sanitize-html');
const crypto = require('crypto');

class AuroraSecurityMiddleware {
  constructor(app) {
    this.app = app;
    this.csrfTokens = new Map(); // Store CSRF tokens temporarily (use Redis in production)
    this.setupSecurityHeaders();
    this.setupRateLimiting();
    this.setupCSP();
    this.setupCSRFProtection();
    this.setupSessionSecurity();
    this.setupSecureCookies();
    this.setupInputValidation();
  }

  /**
   * Configure security headers using Helmet
   */
  setupSecurityHeaders() {
    this.app.use(helmet({
      // Content Security Policy
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'", 'https://trusted-cdn.com'],
          styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
          fontSrc: ["'self'", 'https://fonts.gstatic.com'],
          imgSrc: ["'self'", 'data:', 'https:'],
          connectSrc: ["'self'", 'wss:', 'https:'],
          frameSrc: ["'none'"],
          objectSrc: ["'none'"],
          baseUri: ["'self'"],
          formAction: ["'self'"],
          upgradeInsecureRequests: [],
        },
      },
      // HTTP Strict Transport Security
      hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
      },
      // X-Frame-Options
      frameguard: { action: 'deny' },
      // X-Content-Type-Options
      noSniff: true,
      // X-XSS-Protection
      xssFilter: true,
      // Referrer Policy
      referrerPolicy: { policy: 'same-origin' },
      // Hide X-Powered-By header
      hidePoweredBy: true
    }));
  }

  /**
   * Configure rate limiting
   */
  setupRateLimiting() {
    // Global rate limit
    const globalLimiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 1000, // limit each IP to 1000 requests per windowMs
      message: {
        error: 'Too many requests, please try again later.',
        retryAfter: 900 // 15 minutes in seconds
      },
      standardHeaders: true,
      legacyHeaders: false,
    });

    // Strict rate limit for sensitive endpoints
    const strictLimiter = rateLimit({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 10, // limit each IP to 10 requests per windowMs
      message: {
        error: 'Too many requests to sensitive endpoint, please try again later.',
        retryAfter: 900
      }
    });

    this.app.use(globalLimiter);
    this.app.use('/api/auth', strictLimiter);
    this.app.use('/api/admin', strictLimiter);
  }

  /**
   * CSRF Protection - SECURITY FIX
   */
  setupCSRFProtection() {
    this.app.use('/api', (req, res, next) => {
      if (req.method === 'GET' || req.method === 'HEAD') {
        return next();
      }

      // Generate CSRF token for new sessions
      if (!req.session?.csrfToken) {
        const token = crypto.randomBytes(32).toString('hex');
        if (req.session) {
          req.session.csrfToken = token;
        } else {
          // Fallback if no session middleware
          this.csrfTokens.set(req.ip, token);
        }
      }

      // Validate CSRF token for state-changing requests
      const clientToken = req.headers['x-csrf-token'] || req.body._csrf;
      const sessionToken = req.session?.csrfToken || this.csrfTokens.get(req.ip);

      if (!clientToken || !sessionToken || clientToken !== sessionToken) {
        return res.status(403).json({ error: 'Invalid CSRF token' });
      }

      next();
    });

    // Provide CSRF token endpoint
    this.app.get('/api/csrf-token', (req, res) => {
      const token = crypto.randomBytes(32).toString('hex');
      if (req.session) {
        req.session.csrfToken = token;
      } else {
        this.csrfTokens.set(req.ip, token);
      }
      res.json({ csrfToken: token });
    });
  }

  /**
   * Configure additional CSP rules for WebSocket and dynamic content
   */
  setupCSP() {
    this.app.use((req, res, next) => {
      // Add CSP nonce for inline scripts if needed
      res.locals.nonce = require('crypto').randomBytes(16).toString('base64');
      res.setHeader('Content-Security-Policy',
        `script-src 'self' 'nonce-${res.locals.nonce}'; object-src 'none';`
      );
      next();
    });
  }

  /**
   * Session Security Enhancement - SECURITY FIX
   */
  setupSessionSecurity() {
    this.app.use((req, res, next) => {
      // Session timeout and regeneration
      if (req.session) {
        const now = Date.now();
        
        // Session timeout (30 minutes)
        if (req.session.lastActivity && (now - req.session.lastActivity) > 30 * 60 * 1000) {
          req.session.destroy((err) => {
            if (err) console.error('Session destroy error:', err);
          });
          return res.status(401).json({ error: 'Session expired' });
        }
        
        // Update last activity
        req.session.lastActivity = now;
        
        // Regenerate session ID periodically (every 15 minutes)
        if (!req.session.lastRegeneration || (now - req.session.lastRegeneration) > 15 * 60 * 1000) {
          req.session.regenerate((err) => {
            if (err) console.error('Session regeneration error:', err);
            req.session.lastRegeneration = now;
            next();
          });
        } else {
          next();
        }
      } else {
        next();
      }
    });
  }

  /**
   * Secure cookie configuration
   */
  setupSecureCookies() {
    this.app.use((req, res, next) => {
      const originalSetHeader = res.setHeader;
      res.setHeader = function(name, value) {
        if (name.toLowerCase() === 'set-cookie') {
          if (Array.isArray(value)) {
            value = value.map(cookie => this.makeSecureCookie(cookie));
          } else {
            value = this.makeSecureCookie(value);
          }
        }
        return originalSetHeader.call(this, name, value);
      }.bind(this);
      next();
    });
  }

  /**
   * Make cookie secure
   */
  makeSecureCookie(cookie) {
    if (typeof cookie === 'string') {
      if (!cookie.includes('Secure')) {
        cookie += '; Secure';
      }
      if (!cookie.includes('HttpOnly')) {
        cookie += '; HttpOnly';
      }
      if (!cookie.includes('SameSite')) {
        cookie += '; SameSite=Strict';
      }
    }
    return cookie;
  }

  /**
   * Input validation middleware
   */
  setupInputValidation() {
    this.app.use((req, res, next) => {
      // Sanitize query parameters
      for (const key in req.query) {
        if (typeof req.query[key] === 'string') {
          req.query[key] = this.sanitizeInput(req.query[key]);
        }
      }

      // Sanitize request body
      if (req.body && typeof req.body === 'object') {
        req.body = this.sanitizeObject(req.body);
      }

      next();
    });
  }

  /**
   * Validate URL scheme - SECURITY FIX for incomplete URL scheme check
   */
  validateURLScheme(url) {
    if (typeof url !== 'string') return false;
    
    try {
      const urlObj = new URL(url);
      
      // Only allow safe schemes
      const allowedSchemes = ['http:', 'https:', 'data:', 'mailto:'];
      
      if (!allowedSchemes.includes(urlObj.protocol)) {
        return false;
      }
      
      // Additional checks for specific schemes
      if (urlObj.protocol === 'data:') {
        // Only allow safe data URLs (images, not JavaScript)
        const mimeType = url.split(',')[0].split(':')[1].split(';')[0];
        const safeMimeTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml'];
        return safeMimeTypes.includes(mimeType);
      }
      
      return true;
    } catch (error) {
      // Invalid URL
      return false;
    }
  }

  /**
   * Sanitize URLs in content - SECURITY FIX
   */
  sanitizeURLs(content) {
    if (typeof content !== 'string') return content;
    
    // Find and validate URLs in href and src attributes
    return content.replace(/(href|src)\s*=\s*["']([^"']*)["']/gi, (match, attr, url) => {
      if (this.validateURLScheme(url)) {
        return match; // URL is safe, keep it
      } else {
        return `${attr}="#"`;  // Replace with safe placeholder
      }
    });
  }

  /**
   * Sanitize input string
   */
  sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    
    // First sanitize URLs
    let sanitized = this.sanitizeURLs(input);
    
    // Use sanitize-html to remove all HTML tags and dangerous protocols
    sanitized = sanitizeHtml(sanitized, {
      allowedTags: [],
      allowedAttributes: {},
      // Disallow all protocols that could be dangerous. Remove href/src attributes.
      allowedSchemes: ['http', 'https', 'mailto'],
    });
    
    // Additional length validation to prevent DoS
    if (sanitized.length > 2000) {
      sanitized = sanitized.substring(0, 2000);
    }
    
    return sanitized;
  }

  /**
   * Recursively sanitize object
   */
  sanitizeObject(obj) {
    if (typeof obj !== 'object' || obj === null) return obj;

    const sanitized = {};
    for (const key in obj) {
      if (typeof obj[key] === 'string') {
        sanitized[key] = this.sanitizeInput(obj[key]);
      } else if (typeof obj[key] === 'object') {
        sanitized[key] = this.sanitizeObject(obj[key]);
      } else {
        sanitized[key] = obj[key];
      }
    }
    return sanitized;
  }
}

module.exports = AuroraSecurityMiddleware;
