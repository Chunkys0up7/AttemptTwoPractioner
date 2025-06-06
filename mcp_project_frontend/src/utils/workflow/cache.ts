import { Node, Edge, WorkflowState } from '../../types/workflow';
import { v4 as uuidv4 } from 'uuid';

/**
 * Workflow cache utility functions
 */
export interface WorkflowCache {
  nodes: Record<string, Node>;
  edges: Record<string, Edge>;
  metadata: Record<string, any>;
  timestamp: number;
}

export class WorkflowCacheManager {
  private static instance: WorkflowCacheManager;
  private cache: Record<string, WorkflowCache> = {};
  private cacheTimeout: number = 5 * 60 * 1000; // 5 minutes

  private constructor() {}

  public static getInstance(): WorkflowCacheManager {
    if (!WorkflowCacheManager.instance) {
      WorkflowCacheManager.instance = new WorkflowCacheManager();
    }
    return WorkflowCacheManager.instance;
  }

  /**
   * Store workflow data in cache
   * @param workflowId - Unique identifier for the workflow
   * @param nodes - Array of workflow nodes
   * @param edges - Array of workflow edges
   * @param metadata - Additional workflow metadata
   */
  public store(workflowId: string, nodes: Node[], edges: Edge[], metadata: any = {}): void {
    this.cache[workflowId] = {
      nodes: nodes.reduce((acc, node) => ({ ...acc, [node.id]: node }), {}),
      edges: edges.reduce((acc, edge) => ({ ...acc, [edge.id]: edge }), {}),
      metadata,
      timestamp: Date.now(),
    };
  }

  /**
   * Retrieve workflow data from cache
   * @param workflowId - Unique identifier for the workflow
   * @returns Cached workflow data or null if expired
   */
  public retrieve(workflowId: string): WorkflowCache | null {
    const cachedData = this.cache[workflowId];
    if (!cachedData) return null;

    // Check if cache is expired
    if (Date.now() - cachedData.timestamp > this.cacheTimeout) {
      delete this.cache[workflowId];
      return null;
    }

    return cachedData;
  }

  /**
   * Clear cache for a specific workflow
   * @param workflowId - Unique identifier for the workflow
   */
  public clear(workflowId: string): void {
    delete this.cache[workflowId];
  }

  /**
   * Clear all caches
   */
  public clearAll(): void {
    this.cache = {};
  }

  /**
   * Generate a unique workflow ID
   * @returns Unique workflow ID
   */
  public generateWorkflowId(): string {
    return uuidv4();
  }

  /**
   * Get all cached workflow IDs
   * @returns Array of workflow IDs
   */
  public getCachedWorkflows(): string[] {
    return Object.keys(this.cache);
  }

  /**
   * Get workflow metadata
   * @param workflowId - Unique identifier for the workflow
   * @returns Workflow metadata or null
   */
  public getMetadata(workflowId: string): any | null {
    const cachedData = this.retrieve(workflowId);
    return cachedData ? cachedData.metadata : null;
  }

  /**
   * Update workflow metadata
   * @param workflowId - Unique identifier for the workflow
   * @param metadata - New metadata to store
   */
  public updateMetadata(workflowId: string, metadata: any): void {
    const cachedData = this.retrieve(workflowId);
    if (cachedData) {
      this.store(workflowId, Object.values(cachedData.nodes), Object.values(cachedData.edges), metadata);
    }
  }

  /**
   * Check if workflow exists in cache
   * @param workflowId - Unique identifier for the workflow
   * @returns boolean indicating if workflow exists
   */
  public hasWorkflow(workflowId: string): boolean {
    return this.cache[workflowId] !== undefined;
  }

  /**
   * Get cache size in bytes
   * @returns Size of cache in bytes
   */
  public getCacheSize(): number {
    return Object.values(this.cache).reduce((acc, cache) => {
      return acc + 
        JSON.stringify(cache.nodes).length +
        JSON.stringify(cache.edges).length +
        JSON.stringify(cache.metadata).length;
    }, 0);
  }

  /**
   * Get number of cached workflows
   * @returns Number of cached workflows
   */
  public getCachedCount(): number {
    return Object.keys(this.cache).length;
  }
}
