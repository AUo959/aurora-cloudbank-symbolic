/**
 * Aurora CloudBank Security Middleware
 * Provides comprehensive security headers and protection
 */

const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const sanitizeHtml = require('sanitize-html');

class AuroraSecurityMiddleware {
  constructor(app) {
    this.app = app;
    this.setupSecurityHeaders();
    this.setupRateLimiting();
    this.setupCSP();
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
   * Sanitize input string
   */
  sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    // Use sanitize-html to remove all HTML tags and dangerous protocols
    return sanitizeHtml(input, {
      allowedTags: [],
      allowedAttributes: {},
      // Disallow all protocols that could be dangerous. Remove href/src attributes.
      allowedSchemes: [],
    });
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
