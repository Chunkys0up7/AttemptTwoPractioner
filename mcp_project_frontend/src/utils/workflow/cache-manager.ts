import { WorkflowNode, WorkflowEdge } from '../types/workflow';

export class WorkflowCacheManager {
  private static instance: WorkflowCacheManager;
  private cache: Map<string, { nodes: WorkflowNode[]; edges: WorkflowEdge[] }> = new Map();

  private constructor() {}

  public static getInstance(): WorkflowCacheManager {
    if (!WorkflowCacheManager.instance) {
      WorkflowCacheManager.instance = new WorkflowCacheManager();
    }
    return WorkflowCacheManager.instance;
  }

  public async store(key: string, nodes: WorkflowNode[], edges: WorkflowEdge[]): Promise<void> {
    this.cache.set(key, { nodes, edges });
  }

  public async retrieve(key: string): Promise<{ nodes: WorkflowNode[]; edges: WorkflowEdge[] } | null> {
    return WorkflowCacheManager.instance.cache.get(key) || null;
  }

  public async clear(): Promise<void> {
    WorkflowCacheManager.instance.cache.clear();
  }
}
