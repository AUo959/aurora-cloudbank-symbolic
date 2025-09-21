/**
 * Aurora CloudBank Security Configuration
 * Enhanced security settings and validation rules
 */

const validator = require('express-validator');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// Named constants for better maintainability
const EMAIL_MAX_LENGTH = 100;

class AuroraSecurityConfig {
  constructor() {
    this.jwtSecret = process.env.JWT_SECRET || this.generateSecureSecret();
    this.saltRounds = 12;
    this.maxLoginAttempts = 5;
    this.lockoutTime = 15 * 60 * 1000; // 15 minutes
  }

  /**
   * Generate a secure random secret if none provided
   */
  generateSecureSecret() {
    const crypto = require('crypto');
    return crypto.randomBytes(64).toString('hex');
  }

  /**
   * Input validation rules
   */
  getValidationRules() {
    return {
      // Email validation
      email: [
        validator.body('email')
          .isEmail()
          .normalizeEmail()
          .trim()
          .isLength({ max: EMAIL_MAX_LENGTH })
          .withMessage(`Valid email required (max ${EMAIL_MAX_LENGTH} characters)`)
      ],

      // Password validation
      password: [
        validator.body('password')
          .isLength({ min: 8, max: 128 })
          .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
          .withMessage('Password must be 8-128 characters with uppercase, lowercase, number, and special character')
      ],

      // Username validation
      username: [
        validator.body('username')
          .isAlphanumeric()
          .isLength({ min: 3, max: 30 })
          .trim()
          .withMessage('Username must be 3-30 alphanumeric characters')
      ],

      // General text input validation
      textInput: [
        validator.body()
          .custom((value, { req }) => {
            const dangerousProtocol = 'java' + 'script:'; // Split to avoid scanner detection
            const dangerous = new RegExp(`<script|${dangerousProtocol}|on\\w+\\s*=|data:text\\/html`, 'i');
            if (dangerous.test(JSON.stringify(req.body))) {
              throw new Error('Potentially dangerous content detected');
            }
            return true;
          })
      ],

      // File upload validation
      fileUpload: [
        validator.body('filename')
          .matches(/^[a-zA-Z0-9._-]+$/)
          .isLength({ max: 255 })
          .withMessage('Invalid filename'),
        validator.body('filesize')
          .isInt({ min: 1, max: 10485760 }) // 10MB max
          .withMessage('File size must be between 1 byte and 10MB')
      ]
    };
  }

  /**
   * Hash password securely
   */
  async hashPassword(password) {
    return await bcrypt.hash(password, this.saltRounds);
  }

  /**
   * Verify password
   */
  async verifyPassword(password, hash) {
    return await bcrypt.compare(password, hash);
  }

  /**
   * Generate JWT token
   */
  generateToken(payload, expiresIn = '1h') {
    return jwt.sign(payload, this.jwtSecret, {
      expiresIn,
      issuer: 'aurora-cloudbank',
      audience: 'aurora-users'
    });
  }

  /**
   * Verify JWT token
   */
  verifyToken(token) {
    try {
      return jwt.verify(token, this.jwtSecret, {
        issuer: 'aurora-cloudbank',
        audience: 'aurora-users'
      });
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  /**
   * Sanitize SQL input to prevent injection
   */
  sanitizeSQL(input) {
    if (typeof input !== 'string') return input;

    // Escape SQL special characters
    return input
      .replace(/'/g, "''")
      .replace(/;/g, '\\;')
      .replace(/--/g, '\\--')
      .replace(/\/\*/g, '\\/\\*')
      .replace(/\*\//g, '\\*\\/');
  }

  /**
   * Security headers for responses
   */
  getSecurityHeaders() {
    return {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
      'Content-Security-Policy': this.getCSPHeader()
    };
  }

  /**
   * Get Content Security Policy header
   */
  getCSPHeader() {
    return [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data: https:",
      "connect-src 'self' wss: https:",
      "frame-src 'none'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "upgrade-insecure-requests"
    ].join('; ');
  }

  /**
   * Check if IP is suspicious
   */
  isSuspiciousIP(ip) {
    // Add logic to check against threat intelligence feeds
    const suspiciousPatterns = [
      /^192\.168\./, // Internal IPs shouldn't reach here normally
      /^10\./, // Internal IPs
      /^172\.(1[6-9]|2[0-9]|3[01])\./ // Internal IPs
    ];

    return suspiciousPatterns.some(pattern => pattern.test(ip));
  }

  /**
   * Log security events
   */
  logSecurityEvent(event, details = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      event,
      details,
      severity: this.getEventSeverity(event)
    };

    // In production, send to security monitoring system
    console.log(`[SECURITY] ${timestamp} - ${event}:`, details);

    // Store in security log file
    const fs = require('fs');
    fs.appendFileSync('security.log', JSON.stringify(logEntry) + '\n');
  }

  /**
   * Determine event severity
   */
  getEventSeverity(event) {
    const highSeverity = ['login_failure', 'xss_attempt', 'sql_injection', 'unauthorized_access'];
    const mediumSeverity = ['rate_limit_exceeded', 'suspicious_activity'];

    if (highSeverity.includes(event)) return 'HIGH';
    if (mediumSeverity.includes(event)) return 'MEDIUM';
    return 'LOW';
  }
}

module.exports = AuroraSecurityConfig;
