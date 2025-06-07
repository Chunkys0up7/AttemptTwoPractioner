import { EventEmitter } from 'events';
import { WorkflowNode, WorkflowEdge } from '../../types/workflow';

// Cache types
interface CacheEntry {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  metadata: {
    timestamp: number;
    size: number;
    ttl: number;
    [key: string]: any;
  };
}

interface CacheConfig {
  timeout: number;
  maxSize: number;
  cleanupInterval: number;
  maxSizeMB: number;
}

interface CacheStats {
  totalEntries: number;
  totalSize: number;
  hitRate: number;
  missRate: number;
  averageTTL: number;
  maxEntrySize: number;
  minEntrySize: number;
}

export class WorkflowCacheManager extends EventEmitter {
  private static instance: WorkflowCacheManager;
  private cache: Record<string, CacheEntry> = {};
  private config: CacheConfig = {
    timeout: 5 * 60 * 1000, // 5 minutes
    maxSize: 100,
    cleanupInterval: 60000, // 1 minute
    maxSizeMB: 50
  };
  private stats: CacheStats = {
    totalEntries: 0,
    totalSize: 0,
    hitRate: 0,
    missRate: 0,
    averageTTL: 0,
    maxEntrySize: 0,
    minEntrySize: Infinity
  };
  private hits: number = 0;
  private misses: number = 0;

  private constructor() {
    super();
    this.initializeCleanup();
  }

  public static getInstance(): WorkflowCacheManager {
    if (!WorkflowCacheManager.instance) {
      WorkflowCacheManager.instance = new WorkflowCacheManager();
    }
    return WorkflowCacheManager.instance;
  }

  public configure(config: Partial<CacheConfig>): void {
    this.config = { ...this.config, ...config };
  }

  public store(workflowId: string, nodes: WorkflowNode[], edges: WorkflowEdge[], metadata: Record<string, any> = {}): void {
    // Remove existing entry if it exists
    if (this.cache[workflowId]) {
      this.remove(workflowId);
    }

    const entry: CacheEntry = {
      nodes,
      edges,
      metadata: {
        timestamp: Date.now(),
        size: this.calculateSize(nodes, edges),
        ttl: this.config.timeout,
        ...metadata
      }
    };

    // Check size limits
    if (entry.metadata.size > this.config.maxSizeMB * 1024 * 1024) {
      this.emit('error', {
        type: 'size_limit',
        error: new Error('Entry exceeds maximum size limit'),
        entry
      });
      return;
    }

    // Add to cache
    this.cache[workflowId] = entry;
    this.stats.totalEntries++;
    this.stats.totalSize += entry.metadata.size;

    // Update statistics
    this.updateStats();

    this.emit('store', { workflowId, entry });
  }

  public retrieve(workflowId: string): CacheEntry | null {
    const entry = this.cache[workflowId];
    if (!entry) {
      this.misses++;
      this.updateStats();
      this.emit('retrieve', { workflowId, found: false });
      return null;
    }

    // Check if entry is expired
    if (Date.now() - entry.metadata.timestamp > entry.metadata.ttl) {
      this.remove(workflowId);
      return null;
    }

    this.hits++;
    this.updateStats();
    this.emit('retrieve', { workflowId, found: true });

    return entry;
  }

  public remove(workflowId: string): void {
    const entry = this.cache[workflowId];
    if (entry) {
      this.stats.totalEntries--;
      this.stats.totalSize -= entry.metadata.size;
      delete this.cache[workflowId];
      this.emit('remove', { workflowId, entry });
    }
  }

  public clear(): void {
    this.cache = {};
    this.stats.totalEntries = 0;
    this.stats.totalSize = 0;
    this.hits = 0;
    this.misses = 0;
    this.updateStats();
    this.emit('clear');
  }

  public has(workflowId: string): boolean {
    return this.cache[workflowId] !== undefined;
  }

  public getAll(): Record<string, CacheEntry> {
    return { ...this.cache };
  }

  public getStats(): CacheStats {
    return { ...this.stats };
  }

  public getCachedCount(): number {
    return Object.keys(this.cache).length;
  }

  private initializeCleanup(): void {
    setInterval(() => {
      this.cleanupExpired();
    }, this.config.cleanupInterval);
  }

  private cleanupExpired(): void {
    const now = Date.now();
    const expired: string[] = [];

    for (const [id, entry] of Object.entries(this.cache)) {
      if (now - entry.metadata.timestamp > entry.metadata.ttl) {
        expired.push(id);
      }
    }

    for (const id of expired) {
      this.remove(id);
    }

    if (expired.length > 0) {
      this.emit('cleanup', { expired });
    }
  }

  private calculateSize(nodes: WorkflowNode[], edges: WorkflowEdge[]): number {
    let size = 0;
    for (const node of nodes) {
      size += JSON.stringify(node).length;
    }
    for (const edge of edges) {
      size += JSON.stringify(edge).length;
    }
    return size;
  }

  private updateStats(): void {
    if (this.stats.totalEntries === 0) {
      this.stats.hitRate = 0;
      this.stats.missRate = 0;
      this.stats.averageTTL = 0;
      this.stats.maxEntrySize = 0;
      this.stats.minEntrySize = Infinity;
      return;
    }

    const totalRequests = this.hits + this.misses;
    this.stats.hitRate = (this.hits / totalRequests) * 100;
    this.stats.missRate = (this.misses / totalRequests) * 100;

    let totalTTL = 0;
    let maxSize = 0;
    let minSize = Infinity;

    for (const entry of Object.values(this.cache)) {
      totalTTL += entry.metadata.ttl;
      maxSize = Math.max(maxSize, entry.metadata.size);
      minSize = Math.min(minSize, entry.metadata.size);
    }

    this.stats.averageTTL = totalTTL / this.stats.totalEntries;
    this.stats.maxEntrySize = maxSize;
    this.stats.minEntrySize = minSize;
  }
}
