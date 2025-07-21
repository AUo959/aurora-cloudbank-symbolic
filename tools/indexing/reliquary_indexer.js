#!/usr/bin/env node
/**
 * Reliquary Indexer - Fast semantic search and anchor cross-reference
 * Part of T71 Symbolic Infrastructure Genesis
 *
 * Primary functions:
 * - Semantic search across all documentation/code
 * - Anchor cross-reference resolution
 * - Diff manifest generation between states
 * - Archive organization and fast retrieval
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class ReliquaryIndexer {
    constructor(repoPath = '.') {
        this.repoPath = path.resolve(repoPath);
        this.indexPath = path.join(this.repoPath, '.aurora', 'index');
        this.searchIndex = new Map();
        this.anchorIndex = new Map();
        this.fileIndex = new Map();
        this.semanticIndex = new Map();

        this.version = '1.0.0';

        // File extensions to index
        this.indexableExtensions = [
            '.py', '.js', '.ts', '.md', '.txt', '.json',
            '.yaml', '.yml', '.html', '.css', '.sh'
        ];

        // Patterns for different content types
        this.patterns = {
            anchor: /([A-Z]\d+_[A-Z_]+|[A-Z_]+_ANCHOR|ANCHOR_[A-Z_]+|SRB_[A-Z_]+)/g,
            function: /(def\s+|function\s+|const\s+\w+\s*=|class\s+)([a-zA-Z_]\w*)/g,
            comment: /(#.*$|\/\/.*$|\/\*[\s\S]*?\*\/)/gm,
            string: /(["'])((?:(?!\1)[^\\]|\\.)*)(\1)/g,
            import: /(import\s+.*?from\s+|require\s*\(|import\s+)/g
        };

        this.ensureIndexDirectory();
    }

    ensureIndexDirectory() {
        const auroraDir = path.join(this.repoPath, '.aurora');
        if (!fs.existsSync(auroraDir)) {
            fs.mkdirSync(auroraDir, { recursive: true });
        }
        if (!fs.existsSync(this.indexPath)) {
            fs.mkdirSync(this.indexPath, { recursive: true });
        }
    }

    /**
     * Build comprehensive search index
     */
    async buildIndex() {
        console.log('🔍 Building comprehensive search index...');

        const startTime = Date.now();
        let processedFiles = 0;
        let indexedTerms = 0;

        this.searchIndex.clear();
        this.anchorIndex.clear();
        this.fileIndex.clear();
        this.semanticIndex.clear();

        await this.walkDirectory(this.repoPath, async (filePath) => {
            const relativePath = path.relative(this.repoPath, filePath);

            // Skip hidden files, build artifacts, and dependencies
            if (this.shouldSkipFile(relativePath)) {
                return;
            }

            const ext = path.extname(filePath);
            if (!this.indexableExtensions.includes(ext)) {
                return;
            }

            try {
                const content = fs.readFileSync(filePath, 'utf8');
                const fileInfo = await this.indexFile(filePath, content);

                this.fileIndex.set(relativePath, fileInfo);
                processedFiles++;
                indexedTerms += fileInfo.termCount;

                if (processedFiles % 50 === 0) {
                    process.stdout.write(`\r   Processed ${processedFiles} files...`);
                }

            } catch (error) {
                console.warn(`Warning: Could not index ${relativePath}: ${error.message}`);
            }
        });

        const duration = Date.now() - startTime;
        console.log(`\n✅ Index built: ${processedFiles} files, ${indexedTerms} terms (${duration}ms)`);

        // Save index to disk
        await this.saveIndex();

        return {
            files: processedFiles,
            terms: indexedTerms,
            duration: duration
        };
    }

    /**
     * Index a single file
     */
    async indexFile(filePath, content) {
        const relativePath = path.relative(this.repoPath, filePath);
        const ext = path.extname(filePath);
        const stats = fs.statSync(filePath);

        const fileInfo = {
            path: relativePath,
            size: stats.size,
            modified: stats.mtime.toISOString(),
            extension: ext,
            contentHash: crypto.createHash('sha256').update(content).digest('hex'),
            termCount: 0,
            anchors: [],
            functions: [],
            imports: [],
            semanticTokens: []
        };

        // Extract anchors
        let match;
        while ((match = this.patterns.anchor.exec(content)) !== null) {
            const anchor = {
                id: match[1],
                line: this.getLineNumber(content, match.index),
                context: this.getContext(content, match.index, 50)
            };

            fileInfo.anchors.push(anchor);

            // Add to anchor cross-reference index
            if (!this.anchorIndex.has(anchor.id)) {
                this.anchorIndex.set(anchor.id, []);
            }
            this.anchorIndex.get(anchor.id).push({
                file: relativePath,
                line: anchor.line,
                context: anchor.context
            });
        }

        // Extract functions/classes
        this.patterns.function.lastIndex = 0;
        while ((match = this.patterns.function.exec(content)) !== null) {
            const func = {
                type: match[1].trim(),
                name: match[2],
                line: this.getLineNumber(content, match.index)
            };
            fileInfo.functions.push(func);
        }

        // Extract imports
        this.patterns.import.lastIndex = 0;
        while ((match = this.patterns.import.exec(content)) !== null) {
            const imp = {
                statement: match[0],
                line: this.getLineNumber(content, match.index)
            };
            fileInfo.imports.push(imp);
        }

        // Create searchable terms
        const terms = this.extractSearchTerms(content, ext);
        fileInfo.termCount = terms.length;

        // Add terms to search index
        for (const term of terms) {
            if (!this.searchIndex.has(term.toLowerCase())) {
                this.searchIndex.set(term.toLowerCase(), new Set());
            }
            this.searchIndex.get(term.toLowerCase()).add(relativePath);
        }

        // Generate semantic tokens for advanced search
        fileInfo.semanticTokens = this.generateSemanticTokens(content, ext);
        for (const token of fileInfo.semanticTokens) {
            if (!this.semanticIndex.has(token)) {
                this.semanticIndex.set(token, new Set());
            }
            this.semanticIndex.get(token).add(relativePath);
        }

        return fileInfo;
    }

    /**
     * Search across indexed content
     */
    search(query, options = {}) {
        const {
            type = 'all', // 'all', 'anchor', 'function', 'content'
            caseSensitive = false,
            fuzzy = false,
            maxResults = 50
        } = options;

        console.log(`🔍 Searching for: "${query}" (type: ${type})`);

        const results = {
            query: query,
            type: type,
            totalFiles: 0,
            matches: [],
            anchors: [],
            functions: [],
            semanticMatches: []
        };

        const searchTerm = caseSensitive ? query : query.toLowerCase();

        // Search anchors
        if (type === 'all' || type === 'anchor') {
            for (const [anchorId, locations] of this.anchorIndex) {
                const anchorMatch = caseSensitive ? anchorId : anchorId.toLowerCase();
                if (anchorMatch.includes(searchTerm) || (fuzzy && this.fuzzyMatch(anchorMatch, searchTerm))) {
                    results.anchors.push({
                        id: anchorId,
                        locations: locations,
                        relevance: this.calculateRelevance(anchorId, query)
                    });
                }
            }
        }

        // Search file content
        if (type === 'all' || type === 'content') {
            const matchedFiles = new Set();

            // Exact term search
            if (this.searchIndex.has(searchTerm)) {
                for (const filePath of this.searchIndex.get(searchTerm)) {
                    matchedFiles.add(filePath);
                }
            }

            // Fuzzy search if enabled
            if (fuzzy) {
                for (const [term, files] of this.searchIndex) {
                    if (this.fuzzyMatch(term, searchTerm)) {
                        for (const filePath of files) {
                            matchedFiles.add(filePath);
                        }
                    }
                }
            }

            // Get file details for matches
            for (const filePath of Array.from(matchedFiles).slice(0, maxResults)) {
                const fileInfo = this.fileIndex.get(filePath);
                if (fileInfo) {
                    results.matches.push({
                        file: filePath,
                        relevance: this.calculateFileRelevance(fileInfo, query),
                        anchors: fileInfo.anchors,
                        functions: fileInfo.functions,
                        size: fileInfo.size,
                        modified: fileInfo.modified
                    });
                }
            }
        }

        // Search functions
        if (type === 'all' || type === 'function') {
            for (const [filePath, fileInfo] of this.fileIndex) {
                for (const func of fileInfo.functions) {
                    const funcMatch = caseSensitive ? func.name : func.name.toLowerCase();
                    if (funcMatch.includes(searchTerm)) {
                        results.functions.push({
                            name: func.name,
                            type: func.type,
                            file: filePath,
                            line: func.line,
                            relevance: this.calculateRelevance(func.name, query)
                        });
                    }
                }
            }
        }

        // Semantic search
        const semanticMatches = this.searchSemantic(query);
        results.semanticMatches = semanticMatches.slice(0, 10);

        results.totalFiles = new Set([
            ...results.matches.map(m => m.file),
            ...results.functions.map(f => f.file),
            ...results.anchors.flatMap(a => a.locations.map(l => l.file))
        ]).size;

        // Sort results by relevance
        results.matches.sort((a, b) => b.relevance - a.relevance);
        results.anchors.sort((a, b) => b.relevance - a.relevance);
        results.functions.sort((a, b) => b.relevance - a.relevance);

        console.log(`✅ Found ${results.totalFiles} files with matches`);
        return results;
    }

    /**
     * Generate diff manifest between two states
     */
    generateDiffManifest(anchor1, anchor2) {
        console.log(`📊 Generating diff manifest: ${anchor1} vs ${anchor2}`);

        const diff = {
            timestamp: new Date().toISOString(),
            comparison: { anchor1, anchor2 },
            changes: {
                added: [],
                modified: [],
                removed: [],
                moved: []
            },
            statistics: {
                totalChanges: 0,
                filesAffected: new Set()
            }
        };

        // For now, generate a basic diff based on current state
        // In a full implementation, this would compare against stored snapshots

        const anchor1Files = this.getFilesForAnchor(anchor1);
        const anchor2Files = this.getFilesForAnchor(anchor2);

        // Find files unique to each anchor
        const onlyInAnchor1 = anchor1Files.filter(f => !anchor2Files.includes(f));
        const onlyInAnchor2 = anchor2Files.filter(f => !anchor1Files.includes(f));
        const common = anchor1Files.filter(f => anchor2Files.includes(f));

        diff.changes.added = onlyInAnchor2.map(file => ({ file, reason: 'unique_to_anchor2' }));
        diff.changes.removed = onlyInAnchor1.map(file => ({ file, reason: 'unique_to_anchor1' }));

        // Analyze common files for modifications
        for (const file of common) {
            const fileInfo = this.fileIndex.get(file);
            if (fileInfo) {
                const anchor1Refs = fileInfo.anchors.filter(a => a.id === anchor1).length;
                const anchor2Refs = fileInfo.anchors.filter(a => a.id === anchor2).length;

                if (anchor1Refs !== anchor2Refs) {
                    diff.changes.modified.push({
                        file,
                        anchor1_refs: anchor1Refs,
                        anchor2_refs: anchor2Refs
                    });
                }
            }
        }

        diff.statistics.totalChanges =
            diff.changes.added.length +
            diff.changes.modified.length +
            diff.changes.removed.length +
            diff.changes.moved.length;

        diff.statistics.filesAffected = new Set([
            ...diff.changes.added.map(c => c.file),
            ...diff.changes.modified.map(c => c.file),
            ...diff.changes.removed.map(c => c.file)
        ]);

        diff.statistics.filesAffected = Array.from(diff.statistics.filesAffected);

        return diff;
    }

    /**
     * Get cross-references for an anchor
     */
    getCrossReferences(anchorId) {
        const refs = {
            anchor: anchorId,
            timestamp: new Date().toISOString(),
            directReferences: [],
            relatedAnchors: [],
            containingFiles: []
        };

        // Direct references
        if (this.anchorIndex.has(anchorId)) {
            refs.directReferences = this.anchorIndex.get(anchorId);
            refs.containingFiles = refs.directReferences.map(ref => ref.file);
        }

        // Find related anchors (appearing in same files)
        const relatedSet = new Set();
        for (const file of refs.containingFiles) {
            const fileInfo = this.fileIndex.get(file);
            if (fileInfo) {
                for (const anchor of fileInfo.anchors) {
                    if (anchor.id !== anchorId) {
                        relatedSet.add(anchor.id);
                    }
                }
            }
        }

        refs.relatedAnchors = Array.from(relatedSet).map(relatedId => ({
            id: relatedId,
            sharedFiles: refs.containingFiles.filter(file =>
                this.getFilesForAnchor(relatedId).includes(file)
            ).length
        })).sort((a, b) => b.sharedFiles - a.sharedFiles);

        return refs;
    }

    // Helper methods

    shouldSkipFile(relativePath) {
        const skipPatterns = [
            /^\./, // Hidden files/directories
            /node_modules/,
            /__pycache__/,
            /\.pyc$/,
            /\.git/,
            /build/,
            /dist/,
            /\.vscode/,
            /\.pytest_cache/
        ];

        return skipPatterns.some(pattern => pattern.test(relativePath));
    }

    async walkDirectory(dir, callback) {
        const entries = fs.readdirSync(dir, { withFileTypes: true });

        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);

            if (entry.isDirectory()) {
                await this.walkDirectory(fullPath, callback);
            } else if (entry.isFile()) {
                await callback(fullPath);
            }
        }
    }

    extractSearchTerms(content, ext) {
        const terms = new Set();

        // Remove comments and strings to focus on meaningful content
        let cleanContent = content;
        cleanContent = cleanContent.replace(this.patterns.comment, '');
        cleanContent = cleanContent.replace(this.patterns.string, '');

        // Extract words (alphanumeric + underscore, at least 2 chars)
        const wordPattern = /[a-zA-Z_][a-zA-Z0-9_]{1,}/g;
        let match;
        while ((match = wordPattern.exec(cleanContent)) !== null) {
            const term = match[0];
            if (term.length >= 2 && !this.isCommonWord(term)) {
                terms.add(term);
            }
        }

        return Array.from(terms);
    }

    generateSemanticTokens(content, ext) {
        const tokens = new Set();

        // File type tokens
        tokens.add(`filetype:${ext.slice(1)}`);

        // Language-specific tokens
        if (ext === '.py') {
            if (content.includes('def ')) tokens.add('lang:function-definition');
            if (content.includes('class ')) tokens.add('lang:class-definition');
            if (content.includes('import ')) tokens.add('lang:imports');
            if (content.includes('async ')) tokens.add('lang:async');
        } else if (ext === '.js') {
            if (content.includes('function ')) tokens.add('lang:function-definition');
            if (content.includes('const ')) tokens.add('lang:constants');
            if (content.includes('require(')) tokens.add('lang:requires');
            if (content.includes('async ')) tokens.add('lang:async');
        }

        // Content type tokens
        if (content.includes('TODO') || content.includes('FIXME')) {
            tokens.add('content:todos');
        }
        if (content.includes('test') || content.includes('Test')) {
            tokens.add('content:tests');
        }
        if (content.includes('config') || content.includes('Config')) {
            tokens.add('content:config');
        }

        return Array.from(tokens);
    }

    searchSemantic(query) {
        const matches = [];
        const queryLower = query.toLowerCase();

        // Search semantic tokens
        for (const [token, files] of this.semanticIndex) {
            if (token.includes(queryLower)) {
                for (const file of files) {
                    matches.push({
                        file,
                        semanticToken: token,
                        relevance: this.calculateRelevance(token, query)
                    });
                }
            }
        }

        return matches.sort((a, b) => b.relevance - a.relevance);
    }

    getFilesForAnchor(anchorId) {
        if (this.anchorIndex.has(anchorId)) {
            return this.anchorIndex.get(anchorId).map(ref => ref.file);
        }
        return [];
    }

    getLineNumber(content, index) {
        return content.slice(0, index).split('\n').length;
    }

    getContext(content, index, length = 50) {
        const start = Math.max(0, index - length);
        const end = Math.min(content.length, index + length);
        return content.slice(start, end).replace(/\n/g, ' ').trim();
    }

    calculateRelevance(text, query) {
        const textLower = text.toLowerCase();
        const queryLower = query.toLowerCase();

        if (textLower === queryLower) return 100;
        if (textLower.startsWith(queryLower)) return 90;
        if (textLower.includes(queryLower)) return 70;

        // Simple fuzzy matching score
        let score = 0;
        let queryIndex = 0;

        for (let i = 0; i < textLower.length && queryIndex < queryLower.length; i++) {
            if (textLower[i] === queryLower[queryIndex]) {
                score++;
                queryIndex++;
            }
        }

        return Math.floor((score / queryLower.length) * 50);
    }

    calculateFileRelevance(fileInfo, query) {
        let relevance = 0;

        // Boost for anchor matches
        relevance += fileInfo.anchors.length * 10;

        // Boost for file name matches
        if (fileInfo.path.toLowerCase().includes(query.toLowerCase())) {
            relevance += 20;
        }

        // Boost for recent files
        const daysSinceModified = (Date.now() - new Date(fileInfo.modified)) / (1000 * 60 * 60 * 24);
        if (daysSinceModified < 7) relevance += 5;

        return relevance;
    }

    fuzzyMatch(text, query, threshold = 0.6) {
        if (text.length === 0 || query.length === 0) return false;

        let matches = 0;
        let queryIndex = 0;

        for (let i = 0; i < text.length && queryIndex < query.length; i++) {
            if (text[i] === query[queryIndex]) {
                matches++;
                queryIndex++;
            }
        }

        return (matches / query.length) >= threshold;
    }

    isCommonWord(word) {
        const commonWords = new Set([
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'this', 'that', 'these', 'those', 'a', 'an', 'if', 'else', 'then',
            'true', 'false', 'null', 'undefined', 'var', 'let', 'const'
        ]);

        return commonWords.has(word.toLowerCase());
    }

    async saveIndex() {
        const indexData = {
            timestamp: new Date().toISOString(),
            version: this.version,
            stats: {
                files: this.fileIndex.size,
                searchTerms: this.searchIndex.size,
                anchors: this.anchorIndex.size,
                semanticTokens: this.semanticIndex.size
            }
        };

        // Save index metadata
        fs.writeFileSync(
            path.join(this.indexPath, 'index_meta.json'),
            JSON.stringify(indexData, null, 2)
        );

        console.log('💾 Search index saved to disk');
    }
}

// CLI interface
function main() {
    const args = process.argv.slice(2);
    const command = args[0];

    if (!command) {
        console.log(`
╔═══════════════════════════════════════════════════╗
║             Reliquary Indexer CLI                 ║
║        T71 Symbolic Infrastructure Genesis        ║
║                Version 1.0.0                      ║
╚═══════════════════════════════════════════════════╝

🔍 Fast Semantic Search & Cross-Reference Engine

Commands:
  index [--rebuild]     Build/rebuild search index
  search <query>        Search indexed content
  anchor <anchor_id>    Get anchor cross-references
  diff <anchor1> <anchor2>  Generate diff manifest

Examples:
  node reliquary_indexer.js index --rebuild
  node reliquary_indexer.js search "T70_DOC"
  node reliquary_indexer.js anchor T71_INFRA_SYMBOLIC
  node reliquary_indexer.js diff T70_DOC_REORG T71_INFRA
`);
        return;
    }

    const indexer = new ReliquaryIndexer();

    switch (command) {
        case 'index':
            const rebuild = args.includes('--rebuild');
            indexer.buildIndex()
                .then(stats => {
                    console.log(`✅ Indexing complete: ${stats.files} files, ${stats.terms} terms`);
                })
                .catch(error => {
                    console.error('❌ Indexing failed:', error.message);
                    process.exit(1);
                });
            break;

        case 'search':
            const query = args[1];
            if (!query) {
                console.error('❌ Search query required');
                process.exit(1);
            }

            const options = {};
            if (args.includes('--fuzzy')) options.fuzzy = true;
            if (args.includes('--case-sensitive')) options.caseSensitive = true;

            const typeIndex = args.indexOf('--type');
            if (typeIndex !== -1 && typeIndex + 1 < args.length) {
                options.type = args[typeIndex + 1];
            }

            try {
                indexer.buildIndex().then(() => {
                    const results = indexer.search(query, options);

                    console.log(`\n📊 Search Results for "${query}":`);
                    console.log(`   Total files: ${results.totalFiles}`);

                    if (results.anchors.length > 0) {
                        console.log(`\n⚓ Anchors (${results.anchors.length}):`);
                        results.anchors.slice(0, 5).forEach(anchor => {
                            console.log(`   ${anchor.id} (${anchor.locations.length} references)`);
                        });
                    }

                    if (results.functions.length > 0) {
                        console.log(`\n🔧 Functions (${results.functions.length}):`);
                        results.functions.slice(0, 5).forEach(func => {
                            console.log(`   ${func.name} in ${func.file}:${func.line}`);
                        });
                    }

                    if (results.matches.length > 0) {
                        console.log(`\n📁 Files (${results.matches.length}):`);
                        results.matches.slice(0, 10).forEach(match => {
                            console.log(`   ${match.file} (${match.anchors.length} anchors)`);
                        });
                    }
                });
            } catch (error) {
                console.error('❌ Search failed:', error.message);
                process.exit(1);
            }
            break;

        case 'anchor':
            const anchorId = args[1];
            if (!anchorId) {
                console.error('❌ Anchor ID required');
                process.exit(1);
            }

            try {
                indexer.buildIndex().then(() => {
                    const refs = indexer.getCrossReferences(anchorId);

                    console.log(`\n🔗 Cross-references for ${anchorId}:`);
                    console.log(`   Direct references: ${refs.directReferences.length}`);
                    console.log(`   Related anchors: ${refs.relatedAnchors.length}`);
                    console.log(`   Containing files: ${refs.containingFiles.length}`);

                    if (refs.directReferences.length > 0) {
                        console.log(`\n📍 References:`);
                        refs.directReferences.forEach(ref => {
                            console.log(`   ${ref.file}:${ref.line} - ${ref.context.slice(0, 80)}...`);
                        });
                    }

                    if (refs.relatedAnchors.length > 0) {
                        console.log(`\n🔗 Related anchors:`);
                        refs.relatedAnchors.slice(0, 5).forEach(related => {
                            console.log(`   ${related.id} (${related.sharedFiles} shared files)`);
                        });
                    }
                });
            } catch (error) {
                console.error('❌ Cross-reference lookup failed:', error.message);
                process.exit(1);
            }
            break;

        case 'diff':
            const anchor1 = args[1];
            const anchor2 = args[2];

            if (!anchor1 || !anchor2) {
                console.error('❌ Two anchor IDs required for diff');
                process.exit(1);
            }

            try {
                indexer.buildIndex().then(() => {
                    const diff = indexer.generateDiffManifest(anchor1, anchor2);

                    console.log(`\n📊 Diff Manifest: ${anchor1} vs ${anchor2}`);
                    console.log(`   Total changes: ${diff.statistics.totalChanges}`);
                    console.log(`   Files affected: ${diff.statistics.filesAffected.length}`);

                    if (diff.changes.added.length > 0) {
                        console.log(`\n➕ Added files (${diff.changes.added.length}):`);
                        diff.changes.added.forEach(change => {
                            console.log(`   ${change.file}`);
                        });
                    }

                    if (diff.changes.modified.length > 0) {
                        console.log(`\n📝 Modified files (${diff.changes.modified.length}):`);
                        diff.changes.modified.forEach(change => {
                            console.log(`   ${change.file} (${change.anchor1_refs} → ${change.anchor2_refs} refs)`);
                        });
                    }

                    if (diff.changes.removed.length > 0) {
                        console.log(`\n➖ Removed files (${diff.changes.removed.length}):`);
                        diff.changes.removed.forEach(change => {
                            console.log(`   ${change.file}`);
                        });
                    }

                    // Save diff manifest
                    const outputPath = `diff_${anchor1}_${anchor2}_${Date.now()}.json`;
                    fs.writeFileSync(outputPath, JSON.stringify(diff, null, 2));
                    console.log(`\n💾 Diff manifest saved to: ${outputPath}`);
                });
            } catch (error) {
                console.error('❌ Diff generation failed:', error.message);
                process.exit(1);
            }
            break;

        default:
            console.error(`❌ Unknown command: ${command}`);
            process.exit(1);
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReliquaryIndexer;
}

// Run CLI if called directly
if (require.main === module) {
    main();
}
