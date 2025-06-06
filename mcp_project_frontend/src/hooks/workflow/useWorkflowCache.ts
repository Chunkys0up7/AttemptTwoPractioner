import { useState, useEffect } from 'react';
import { Node, Edge } from '../../types/workflow';
import { WorkflowCacheManager } from '../utils/workflow/cache';

/**
 * Custom hook for workflow caching
 * @param workflowId - Unique identifier for the workflow
 * @returns Object containing cached data and cache management functions
 */
export const useWorkflowCache = (workflowId: string) => {
  const cacheManager = WorkflowCacheManager.getInstance();
  const [cachedData, setCachedData] = useState<WorkflowCache | null>(null);

  useEffect(() => {
    const retrieveCache = () => {
      const data = cacheManager.retrieve(workflowId);
      setCachedData(data);
    };

    retrieveCache();

    // Set up periodic cache refresh
    const interval = setInterval(retrieveCache, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [workflowId]);

  /**
   * Store workflow data in cache
   * @param nodes - Array of workflow nodes
   * @param edges - Array of workflow edges
   * @param metadata - Additional workflow metadata
   */
  const store = (nodes: Node[], edges: Edge[], metadata: any = {}) => {
    cacheManager.store(workflowId, nodes, edges, metadata);
  };

  /**
   * Clear cache for this workflow
   */
  const clear = () => {
    cacheManager.clear(workflowId);
  };

  /**
   * Update workflow metadata
   * @param metadata - New metadata to store
   */
  const updateMetadata = (metadata: any) => {
    cacheManager.updateMetadata(workflowId, metadata);
  };

  return {
    cachedData,
    store,
    clear,
    updateMetadata,
    isCached: !!cachedData,
    cacheSize: cachedData ? cacheManager.getCacheSize() : 0,
    cachedCount: cacheManager.getCachedCount(),
  };
};
