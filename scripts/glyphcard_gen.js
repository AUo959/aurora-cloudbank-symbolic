// scripts/glyphcard_gen.js
// Glyphcard generator for symbolic anchor manifests
// Usage: node scripts/glyphcard_gen.js anchor_decrypt_*.json

const fs = require('fs');
const path = require('path');

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function loadAnchors(pattern) {
    const dir = __dirname;
    const safePattern = escapeRegExp(pattern).replace(/\\\*/g, '.*');
    const regex = new RegExp(safePattern);
    const files = fs.readdirSync(dir).filter(f => f.match(regex));
    return files.map(f => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')));
}

function generateGlyphcardSummary(anchors) {
    return anchors.map(anchor => ({
        anchor: anchor.anchor,
        tag: anchor.tag,
        timestamp: anchor.timestamp,
        status: anchor.error ? 'error' : 'success',
        entropy_state: anchor.entropy_state || null
    }));
}

if (require.main === module) {
    const pattern = process.argv[2] || 'anchor_decrypt_*.json';
    const anchors = loadAnchors(pattern);
    const summary = generateGlyphcardSummary(anchors);
    console.log('Glyphcard Summary:', JSON.stringify(summary, null, 2));
}
