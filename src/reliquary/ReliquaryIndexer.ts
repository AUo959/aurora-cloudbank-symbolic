/**
 * Aurora/GUMAS Reliquary Indexing System
 * Archive and restoration system with thread preservation
 * Operator: AUo959
 */

export interface ThreadArchive {
  threadId: string;
  sealedState: any; // sealed symbolic state
  metadata: {
    createdAt: Date;
    sealedAt: Date;
    operatorId: string;
    classification: string;
    retentionPolicy: string;
  };
  dependencies: string[]; // related thread IDs
  tags: string[];
  searchableContent: string;
}

export interface CrossThreadDependency {
  sourceThread: string;
  targetThread: string;
  dependencyType: 'requires' | 'extends' | 'supersedes' | 'references';
  strength: number; // 1-10 scale
  metadata: Record<string, any>;
  createdAt: Date;
  operatorId: string;
}

export interface ReliquaryIndex {
  id: string;
  name: string;
  description: string;
  archives: Map<string, ThreadArchive>;
  dependencies: CrossThreadDependency[];
  searchIndex: Map<string, string[]>; // keyword -> thread IDs
  metadata: Record<string, any>;
  createdAt: Date;
  lastUpdated: Date;
  operatorId: string;
}

export interface SearchQuery {
  keywords?: string[];
  classification?: string;
  dateRange?: { start: Date; end: Date };
  tags?: string[];
  operatorId?: string;
  dependencyType?: string;
  maxResults?: number;
}

export interface SearchResult {
  threadId: string;
  archive: ThreadArchive;
  relevanceScore: number;
  matchingKeywords: string[];
  dependencies: CrossThreadDependency[];
}

/**
 * Reliquary indexing for thread preservation and search
 */
export class ReliquaryIndexer {
  private readonly operatorId = 'AUo959';
  private indices: Map<string, ReliquaryIndex> = new Map();
  private globalSearchIndex: Map<string, Set<string>> = new Map(); // keyword -> reliquary IDs

  /**
   * Create new reliquary index
   */
  createReliquary(name: string, description: string, metadata: Record<string, any> = {}): ReliquaryIndex {
    const reliquary: ReliquaryIndex = {
      id: this.generateReliquaryId(),
      name,
      description,
      archives: new Map(),
      dependencies: [],
      searchIndex: new Map(),
      metadata: {
        ...metadata,
        auroraCompliant: true,
        gumasVersion: '2024.1'
      },
      createdAt: new Date(),
      lastUpdated: new Date(),
      operatorId: this.operatorId
    };

    this.indices.set(reliquary.id, reliquary);
    this.updateGlobalSearchIndex(reliquary.id, [name, description]);
    
    return reliquary;
  }

  /**
   * Archive thread with sealed symbolic state
   */
  archiveThread(
    reliquaryId: string,
    threadId: string,
    sealedState: any,
    metadata: Record<string, any> = {},
    tags: string[] = []
  ): boolean {
    const reliquary = this.indices.get(reliquaryId);
    if (!reliquary) return false;

    const archive: ThreadArchive = {
      threadId,
      sealedState,
      metadata: {
        createdAt: new Date(),
        sealedAt: new Date(),
        operatorId: this.operatorId,
        classification: metadata.classification || 'internal',
        retentionPolicy: metadata.retentionPolicy || 'default',
        ...metadata
      },
      dependencies: [],
      tags,
      searchableContent: this.generateSearchableContent(sealedState, metadata, tags)
    };

    reliquary.archives.set(threadId, archive);
    this.updateSearchIndex(reliquary, threadId, archive.searchableContent);
    reliquary.lastUpdated = new Date();

    return true;
  }

  /**
   * Add cross-thread dependency
   */
  addDependency(
    reliquaryId: string,
    sourceThread: string,
    targetThread: string,
    dependencyType: 'requires' | 'extends' | 'supersedes' | 'references',
    strength: number = 5,
    metadata: Record<string, any> = {}
  ): boolean {
    const reliquary = this.indices.get(reliquaryId);
    if (!reliquary) return false;

    // Verify both threads exist in the reliquary
    if (!reliquary.archives.has(sourceThread) || !reliquary.archives.has(targetThread)) {
      return false;
    }

    const dependency: CrossThreadDependency = {
      sourceThread,
      targetThread,
      dependencyType,
      strength: Math.max(1, Math.min(10, strength)),
      metadata: {
        ...metadata,
        operatorId: this.operatorId
      },
      createdAt: new Date(),
      operatorId: this.operatorId
    };

    reliquary.dependencies.push(dependency);
    
    // Update archive dependencies
    const sourceArchive = reliquary.archives.get(sourceThread);
    if (sourceArchive && !sourceArchive.dependencies.includes(targetThread)) {
      sourceArchive.dependencies.push(targetThread);
    }

    reliquary.lastUpdated = new Date();
    return true;
  }

  /**
   * Search across reliquaries
   */
  search(query: SearchQuery): SearchResult[] {
    const results: SearchResult[] = [];

    for (const reliquary of this.indices.values()) {
      const reliquaryResults = this.searchReliquary(reliquary, query);
      results.push(...reliquaryResults);
    }

    // Sort by relevance score
    results.sort((a, b) => b.relevanceScore - a.relevanceScore);

    // Apply max results limit
    if (query.maxResults) {
      return results.slice(0, query.maxResults);
    }

    return results;
  }

  /**
   * Restore thread from archive
   */
  restoreThread(reliquaryId: string, threadId: string): ThreadArchive | null {
    const reliquary = this.indices.get(reliquaryId);
    if (!reliquary) return null;

    return reliquary.archives.get(threadId) || null;
  }

  /**
   * Get thread dependencies
   */
  getThreadDependencies(reliquaryId: string, threadId: string): CrossThreadDependency[] {
    const reliquary = this.indices.get(reliquaryId);
    if (!reliquary) return [];

    return reliquary.dependencies.filter(
      dep => dep.sourceThread === threadId || dep.targetThread === threadId
    );
  }

  /**
   * Get dependency graph for thread
   */
  getDependencyGraph(reliquaryId: string, threadId: string, maxDepth: number = 3): Map<string, CrossThreadDependency[]> {
    const graph = new Map<string, CrossThreadDependency[]>();
    const visited = new Set<string>();
    
    this.buildDependencyGraph(reliquaryId, threadId, graph, visited, 0, maxDepth);
    
    return graph;
  }

  /**
   * Export reliquary index
   */
  exportReliquary(reliquaryId: string): ReliquaryIndex | null {
    const reliquary = this.indices.get(reliquaryId);
    if (!reliquary) return null;

    return {
      ...reliquary,
      archives: new Map(reliquary.archives),
      dependencies: [...reliquary.dependencies],
      searchIndex: new Map(reliquary.searchIndex)
    };
  }

  /**
   * Import reliquary index
   */
  importReliquary(reliquaryData: any): boolean {
    try {
      const reliquary: ReliquaryIndex = {
        ...reliquaryData,
        archives: new Map(reliquaryData.archives),
        searchIndex: new Map(reliquaryData.searchIndex)
      };

      this.indices.set(reliquary.id, reliquary);
      this.updateGlobalSearchIndex(reliquary.id, [reliquary.name, reliquary.description]);
      
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get all reliquaries
   */
  getAllReliquaries(): ReliquaryIndex[] {
    return Array.from(this.indices.values());
  }

  /**
   * Delete reliquary (with confirmation)
   */
  deleteReliquary(reliquaryId: string): boolean {
    const reliquary = this.indices.get(reliquaryId);
    if (!reliquary) return false;

    // Remove from global search index
    this.removeFromGlobalSearchIndex(reliquaryId);
    
    // Delete the reliquary
    return this.indices.delete(reliquaryId);
  }

  private searchReliquary(reliquary: ReliquaryIndex, query: SearchQuery): SearchResult[] {
    const results: SearchResult[] = [];

    for (const [threadId, archive] of reliquary.archives) {
      let relevanceScore = 0;
      const matchingKeywords: string[] = [];

      // Keyword matching
      if (query.keywords) {
        for (const keyword of query.keywords) {
          if (archive.searchableContent.toLowerCase().includes(keyword.toLowerCase())) {
            relevanceScore += 10;
            matchingKeywords.push(keyword);
          }
        }
      }

      // Classification filter
      if (query.classification && archive.metadata.classification !== query.classification) {
        continue;
      }

      // Date range filter
      if (query.dateRange) {
        const createdAt = archive.metadata.createdAt;
        if (createdAt < query.dateRange.start || createdAt > query.dateRange.end) {
          continue;
        }
      }

      // Tags filter
      if (query.tags) {
        const hasAllTags = query.tags.every(tag => archive.tags.includes(tag));
        if (!hasAllTags) continue;
        relevanceScore += query.tags.length * 5;
      }

      // Operator filter
      if (query.operatorId && archive.metadata.operatorId !== query.operatorId) {
        continue;
      }

      // Get dependencies for this thread
      const dependencies = this.getThreadDependencies(reliquary.id, threadId);

      if (relevanceScore > 0 || query.keywords === undefined) {
        results.push({
          threadId,
          archive,
          relevanceScore,
          matchingKeywords,
          dependencies
        });
      }
    }

    return results;
  }

  private generateSearchableContent(sealedState: any, metadata: Record<string, any>, tags: string[]): string {
    const parts: string[] = [];
    
    // Add metadata values
    Object.values(metadata).forEach(value => {
      if (typeof value === 'string') {
        parts.push(value);
      }
    });

    // Add tags
    parts.push(...tags);

    // Add operator ID
    parts.push(this.operatorId);

    return parts.join(' ').toLowerCase();
  }

  private updateSearchIndex(reliquary: ReliquaryIndex, threadId: string, content: string): void {
    const keywords = this.extractKeywords(content);
    
    for (const keyword of keywords) {
      if (!reliquary.searchIndex.has(keyword)) {
        reliquary.searchIndex.set(keyword, []);
      }
      const threadList = reliquary.searchIndex.get(keyword)!;
      if (!threadList.includes(threadId)) {
        threadList.push(threadId);
      }
    }
  }

  private updateGlobalSearchIndex(reliquaryId: string, content: string[]): void {
    const keywords = content.flatMap(c => this.extractKeywords(c));
    
    for (const keyword of keywords) {
      if (!this.globalSearchIndex.has(keyword)) {
        this.globalSearchIndex.set(keyword, new Set());
      }
      this.globalSearchIndex.get(keyword)!.add(reliquaryId);
    }
  }

  private removeFromGlobalSearchIndex(reliquaryId: string): void {
    for (const reliquarySet of this.globalSearchIndex.values()) {
      reliquarySet.delete(reliquaryId);
    }
  }

  private extractKeywords(content: string): string[] {
    return content
      .toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 2)
      .filter(word => !this.isStopWord(word));
  }

  private isStopWord(word: string): boolean {
    const stopWords = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'];
    return stopWords.includes(word);
  }

  private buildDependencyGraph(
    reliquaryId: string,
    threadId: string,
    graph: Map<string, CrossThreadDependency[]>,
    visited: Set<string>,
    depth: number,
    maxDepth: number
  ): void {
    if (depth >= maxDepth || visited.has(threadId)) return;
    
    visited.add(threadId);
    const dependencies = this.getThreadDependencies(reliquaryId, threadId);
    graph.set(threadId, dependencies);
    
    for (const dep of dependencies) {
      const nextThread = dep.sourceThread === threadId ? dep.targetThread : dep.sourceThread;
      this.buildDependencyGraph(reliquaryId, nextThread, graph, visited, depth + 1, maxDepth);
    }
  }

  private generateReliquaryId(): string {
    return `reliquary_${Date.now()}_${this.operatorId}`;
  }
}