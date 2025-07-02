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
            "'": '&#x27;',
            '/': '&#x2F;'
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
        return text.replace(/[&<>"'\/]/g, (char) => this.htmlEntities[char]);
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

        // Use DOMPurify to sanitize the input
        const DOMPurify = require('dompurify');
        const { JSDOM } = require('jsdom');
        const window = new JSDOM('').window;
        const purify = DOMPurify(window);

        const sanitized = purify.sanitize(text);
        return sanitized;
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

        // Create a temporary element to parse and clean the HTML
        const temp = document.createElement('div');
        temp.innerHTML = this.sanitizeText(content);

        // Only allow safe elements
        const allowedTags = ['p', 'span', 'strong', 'em', 'br'];
        const walker = document.createTreeWalker(
            temp,
            NodeFilter.SHOW_ELEMENT,
            {
                acceptNode: (node) => {
                    return allowedTags.includes(node.tagName.toLowerCase())
                        ? NodeFilter.FILTER_ACCEPT
                        : NodeFilter.FILTER_REJECT;
                }
            }
        );

        const safeContent = document.createDocumentFragment();
        let node;
        while (node = walker.nextNode()) {
            const clone = node.cloneNode(true);
            // Remove all attributes except safe ones
            for (let i = clone.attributes.length - 1; i >= 0; i--) {
                const attr = clone.attributes[i];
                if (!this.isValidAttribute(attr.name)) {
                    clone.removeAttribute(attr.name);
                }
            }
            safeContent.appendChild(clone);
        }

        element.innerHTML = '';
        element.appendChild(safeContent);
    }

    /**
     * Check if an attribute is safe to use
     * @param {string} attrName - Attribute name
     * @returns {boolean} - Whether the attribute is safe
     */
    isValidAttribute(attrName) {
        const safeAttributes = [
            'class', 'id', 'style', 'title', 'alt', 'src', 'href',
            'data-', 'aria-', 'role'
        ];

        const lowerAttr = attrName.toLowerCase();
        return safeAttributes.some(safe =>
            lowerAttr === safe || lowerAttr.startsWith(safe)
        ) && !lowerAttr.startsWith('on'); // No event handlers
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
            } catch (e) {
                return { error: 'Invalid JSON data' };
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
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'", // Note: This should be made stricter in production
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "connect-src 'self' ws: wss:",
            "font-src 'self'",
            "object-src 'none'",
            "media-src 'self'",
            "frame-src 'none'"
        ].join('; ');

        return this.createSafeElement('meta', '', {
            'http-equiv': 'Content-Security-Policy',
            'content': csp
        });
    }
}

// Global instance
window.AuroraSecurity = new AuroraSecurityUtils();

// Export for Node.js environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuroraSecurityUtils;
}
