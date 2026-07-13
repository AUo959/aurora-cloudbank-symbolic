/**
 * Aurora CloudBank Security Utils
 * Provides XSS protection and input sanitization utilities
 */

class AuroraSecurityUtils {
  constructor() {
    // HTML entities for encoding
    this.htmlEntities = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      '\'': '&#x27;',
      '/': '&#x2F;',
    };
  }

  /**
   * Escape HTML to prevent XSS attacks
   * @param {string} text - Text to escape
   * @returns {string} - Escaped text
   */
  escapeHtml(text) {
    if (typeof text !== 'string') {
      return text;
    }
    return text.replace(/[&<>"'\/]/g, char => this.htmlEntities[char]);
  }

  /**
   * Sanitize text for safe display
   * @param {string} text - Text to sanitize
   * @returns {string} - Sanitized text
   */
  sanitizeText(text) {
    if (typeof text !== 'string') {
      return '';
    }

    // This file runs directly in the browser, so avoid Node-only sanitizers.
    // Callers render the returned value through textContent or safe attributes.
    return text.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '');
  }

  /**
   * Safe DOM element creation with escaped content
   * @param {string} tagName - HTML tag name
   * @param {string} content - Content to add (will be escaped)
   * @param {Object} attributes - Attributes to set
   * @returns {HTMLElement} - Created element
   */
  createSafeElement(tagName, content = '', attributes = {}) {
    const element = document.createElement(tagName);

    // Set content as text (automatically escaped)
    if (content) {
      element.textContent = content;
    }

    // Set attributes safely
    for (const [key, value] of Object.entries(attributes)) {
      if (this.isValidAttribute(key)) {
        element.setAttribute(key, this.escapeHtml(String(value)));
      }
    }

    return element;
  }

  /**
   * Safe innerHTML replacement using textContent
   * @param {HTMLElement} element - Target element
   * @param {string} content - Content to set (will be escaped)
   */
  setSafeContent(element, content) {
    if (!element || typeof content !== 'string') {
      return;
    }
    element.textContent = content;
  }

  /**
   * Safe innerHTML replacement for formatted content
   * @param {HTMLElement} element - Target element
   * @param {string} content - Content to set (will be sanitized)
   */
  setSafeHTML(element, content) {
    if (!element || typeof content !== 'string') {
      return;
    }

    element.innerHTML = this.sanitizeHTML(content);
  }

  /**
   * Sanitize HTML content for safe innerHTML assignment
   * @param {string} html - HTML content to sanitize
   * @returns {string} - Sanitized HTML
   */
  sanitizeHTML(html) {
    if (typeof html !== 'string') {
      return '';
    }

    // Basic HTML sanitization - escapes potentially dangerous content
    // while preserving basic formatting tags
    const allowedTags = new Set([
      'div',
      'span',
      'p',
      'h1',
      'h2',
      'h3',
      'h4',
      'h5',
      'h6',
      'strong',
      'em',
      'br',
    ]);
    const allowedAttributes = new Set(['style', 'class']);

    // DOMParser keeps untrusted markup detached and does not initiate subresource
    // loads while the allowlist pass removes unsafe elements and attributes.
    const parsedDocument = new DOMParser().parseFromString(html, 'text/html');
    const tempDiv = parsedDocument.body;

    const sanitizeChildren = parent => {
      for (const child of Array.from(parent.children)) {
        const tagName = child.tagName.toLowerCase();
        if (!allowedTags.has(tagName)) {
          child.remove();
          continue;
        }

        for (const attr of Array.from(child.attributes)) {
          const attrName = attr.name.toLowerCase();
          if (!allowedAttributes.has(attrName)) {
            child.removeAttribute(attr.name);
            continue;
          }
          if (attrName === 'style') {
            const safeColors = attr.value
              .split(';')
              .map(value => value.trim())
              .filter(value => /^color\s*:\s*(#[0-9a-f]{3,8}|[a-z]+)$/i.test(value));
            if (safeColors.length) {
              child.setAttribute('style', safeColors.join('; '));
            } else {
              child.removeAttribute('style');
            }
          }
        }
        sanitizeChildren(child);
      }
    };

    sanitizeChildren(tempDiv);
    return tempDiv.innerHTML;
  }

  /**
   * Check if an attribute is safe to use
   * @param {string} attrName - Attribute name
   * @returns {boolean} - Whether the attribute is safe
   */
  isValidAttribute(attrName) {
    const safeAttributes = [
      'class',
      'id',
      'style',
      'title',
      'alt',
      'src',
      'href',
      'data-',
      'aria-',
      'role',
    ];

    const lowerAttr = attrName.toLowerCase();
    return (
      safeAttributes.some(
        safe => lowerAttr === safe || lowerAttr.startsWith(safe)
      ) && !lowerAttr.startsWith('on')
    ); // No event handlers
  }

  /**
   * Validate and sanitize WebSocket data
   * @param {any} data - Data from WebSocket
   * @returns {Object} - Sanitized data
   */
  sanitizeWebSocketData(data) {
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data);
      } catch (error) {
        return { error: 'Invalid JSON data', detail: String(error) };
      }
    }

    if (typeof data !== 'object' || data === null) {
      return { error: 'Invalid data type' };
    }

    const sanitized = {};
    for (const [key, value] of Object.entries(data)) {
      if (typeof value === 'string') {
        sanitized[key] = this.sanitizeText(value);
      } else if (typeof value === 'number' || typeof value === 'boolean') {
        sanitized[key] = value;
      } else {
        sanitized[key] = String(value);
      }
    }

    return sanitized;
  }

  /**
   * Create Content Security Policy meta tag
   * @returns {HTMLElement} - CSP meta element
   */
  createCSPMetaTag() {
    const csp = [
      'default-src \'self\'',
      'script-src \'self\' \'unsafe-inline\'', // Note: This should be made stricter in production
      'style-src \'self\' \'unsafe-inline\'',
      'img-src \'self\' data: https:',
      'connect-src \'self\' ws: wss:',
      'font-src \'self\'',
      'object-src \'none\'',
      'media-src \'self\'',
      'frame-src \'none\'',
    ].join('; ');

    return this.createSafeElement('meta', '', {
      'http-equiv': 'Content-Security-Policy',
      content: csp,
    });
  }
}

// Global instance
window.AuroraSecurity = new AuroraSecurityUtils();

// Export for Node.js environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AuroraSecurityUtils;
}
