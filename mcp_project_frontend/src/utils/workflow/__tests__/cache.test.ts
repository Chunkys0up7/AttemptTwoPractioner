import { WorkflowCacheManager } from '../cache';
import { Node, Edge } from '../../../types/workflow';

describe('WorkflowCacheManager', () => {
  let cacheManager: WorkflowCacheManager;

  beforeEach(() => {
    cacheManager = WorkflowCacheManager.getInstance();
    cacheManager.clearAll();
  });

  test('should create singleton instance', () => {
    const instance1 = WorkflowCacheManager.getInstance();
    const instance2 = WorkflowCacheManager.getInstance();
    expect(instance1).toBe(instance2);
  });

  test('should store and retrieve workflow data', () => {
    const workflowId = 'test-workflow';
    const nodes: Node[] = [
      {
        id: '1',
        type: 'start',
        position: { x: 0, y: 0 },
        data: { name: 'Start', componentId: 'start', config: {} },
      },
    ];
    const edges: Edge[] = [
      {
        id: '1-2',
        source: '1',
        target: '2',
      },
    ];
    const metadata = { version: 1, createdBy: 'test' };

    cacheManager.store(workflowId, nodes, edges, metadata);
    const cachedData = cacheManager.retrieve(workflowId);

    expect(cachedData).not.toBeNull();
    expect(cachedData?.nodes['1']).toEqual(nodes[0]);
    expect(cachedData?.edges['1-2']).toEqual(edges[0]);
    expect(cachedData?.metadata).toEqual(metadata);
  });

  test('should expire cache after timeout', async () => {
    const workflowId = 'test-workflow';
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    cacheManager.store(workflowId, nodes, edges);
    expect(cacheManager.retrieve(workflowId)).not.toBeNull();

    // Wait for cache to expire (5 minutes + 1 second)
    await new Promise(resolve => setTimeout(resolve, 301000));
    expect(cacheManager.retrieve(workflowId)).toBeNull();
  });

  test('should generate unique workflow IDs', () => {
    const id1 = cacheManager.generateWorkflowId();
    const id2 = cacheManager.generateWorkflowId();
    expect(id1).not.toEqual(id2);
  });

  test('should update metadata', () => {
    const workflowId = 'test-workflow';
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    cacheManager.store(workflowId, nodes, edges);
    cacheManager.updateMetadata(workflowId, { version: 2 });

    const cachedData = cacheManager.retrieve(workflowId);
    expect(cachedData?.metadata).toEqual({ version: 2 });
  });

  test('should clear cache', () => {
    const workflowId = 'test-workflow';
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    cacheManager.store(workflowId, nodes, edges);
    cacheManager.clear(workflowId);
    expect(cacheManager.retrieve(workflowId)).toBeNull();
  });

  test('should get cache size', () => {
    const workflowId = 'test-workflow';
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    cacheManager.store(workflowId, nodes, edges);
    const size = cacheManager.getCacheSize();
    expect(size).toBeGreaterThan(0);
  });

  test('should get cached workflow count', () => {
    const workflowId1 = 'test-workflow-1';
    const workflowId2 = 'test-workflow-2';
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    cacheManager.store(workflowId1, nodes, edges);
    cacheManager.store(workflowId2, nodes, edges);
    expect(cacheManager.getCachedCount()).toBe(2);
  });
});
