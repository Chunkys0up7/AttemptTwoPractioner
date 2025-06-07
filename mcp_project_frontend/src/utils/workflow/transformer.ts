import { EventEmitter } from 'events';
import { WorkflowNode, WorkflowEdge, WorkflowTransformationOptions, WorkflowError, AIComponent } from '../types/workflow';
import { WorkflowValidator } from './validator';
import { WorkflowCacheManager } from './cache-manager';

export class WorkflowTransformer extends EventEmitter {
  private static instance: WorkflowTransformer;
  private options: WorkflowTransformationOptions;
  private cacheManager: WorkflowCacheManager;

  private constructor() {
    super();
    this.options = {
      optimize: true,
      validate: true,
      components: [],
      metadata: {},
      errorHandler: undefined
    };
    this.cacheManager = WorkflowCacheManager.getInstance();
  }

  public static getInstance(): WorkflowTransformer {
    if (!WorkflowTransformer.instance) {
      WorkflowTransformer.instance = new WorkflowTransformer();
    }
    return WorkflowTransformer.instance;
  }

  public async transform(
    nodes: WorkflowNode[],
    edges: WorkflowEdge[],
    options: Partial<WorkflowTransformationOptions> = {}
  ): Promise<{ nodes: WorkflowNode[]; edges: WorkflowEdge[] }> {
    try {
      // Merge options with defaults
      const opts = {
        ...this.options,
        ...options
      };

      const key = this.generateCacheKey(nodes, edges);
      const cached = await this.cacheManager.retrieve(key);
      if (cached) {
        return cached;
      }

      if (opts.validate) {
        const validation = await WorkflowValidator.validateWorkflow(
          nodes,
          edges,
          opts.components
        );
        if (validation.errors.length > 0) {
          const error = new WorkflowError('Workflow validation failed', validation.errors);
          if (opts.errorHandler) {
            opts.errorHandler(error);
          }
          throw error;
        }
      }

      let transformedNodes = nodes;
      let transformedEdges = edges;

      if (opts.optimize) {
        transformedNodes = await this.optimizeNodes(nodes);
        transformedEdges = await this.optimizeEdges(edges);
      }

      await this.cacheManager.store(key, { nodes: transformedNodes, edges: transformedEdges });
      return { nodes: transformedNodes, edges: transformedEdges };
    } catch (error) {
      const workflowError = error instanceof WorkflowError 
        ? error 
        : new WorkflowError('Workflow transformation failed', error instanceof Error ? error.message : String(error));
      
      if (this.options.errorHandler) {
        this.options.errorHandler(workflowError);
      }
      throw workflowError;
    }
  }

  private async optimizeNodes(nodes: WorkflowNode[]): Promise<WorkflowNode[]> {
    const optimizedNodes = [...nodes];
    for (const node of optimizedNodes) {
      if (node.data?.metadata) {
        node.data.metadata = await this.optimizeMetadata(node.data.metadata);
      }
      if (node.data?.validation) {
        node.data.validation = await this.optimizeValidation(node.data.validation);
      }
      if (node.data?.config) {
        node.data.config = await this.optimizeComponentConfig(node.data.config);
      }
    }
    return optimizedNodes;
  }

  private async optimizeEdges(edges: WorkflowEdge[]): Promise<WorkflowEdge[]> {
    const optimizedEdges = [...edges];
    for (const edge of optimizedEdges) {
      if (edge.data?.conditions) {
        edge.data.conditions = await this.optimizeConditions(edge.data.conditions);
      }
    }
    return optimizedEdges;
  }

  private async optimizeMetadata(metadata: Record<string, any>): Promise<Record<string, any>> {
    if (!metadata) return {};
    
    const optimizedMetadata = { ...metadata };
    Object.keys(optimizedMetadata).forEach(key => {
      if (optimizedMetadata[key] === undefined || optimizedMetadata[key] === null) {
        delete optimizedMetadata[key];
      }
    });
    return optimizedMetadata;
  }

  private async optimizeValidation(validation: Record<string, any>): Promise<Record<string, any>> {
    if (!validation) return {};
    
    const optimizedValidation = { ...validation };
    Object.keys(optimizedValidation).forEach(key => {
      if (optimizedValidation[key] === undefined || optimizedValidation[key] === null) {
        delete optimizedValidation[key];
      }
    });
    return optimizedValidation;
  }

  private async optimizeConditions(conditions: Record<string, any>): Promise<Record<string, any>> {
    if (!conditions) return {};
    
    const optimizedConditions = { ...conditions };
    Object.keys(optimizedConditions).forEach(key => {
      if (!optimizedConditions[key] || Object.keys(optimizedConditions[key]).length === 0) {
        delete optimizedConditions[key];
      }
    });
    return optimizedConditions;
  }

  private async optimizeComponentConfig(config: Record<string, any>): Promise<Record<string, any>> {
    if (!config) return {};
    
    const optimizedConfig = { ...config };
    Object.keys(optimizedConfig).forEach(key => {
      if (optimizedConfig[key] === undefined || optimizedConfig[key] === null) {
        delete optimizedConfig[key];
      }
    });
    return optimizedConfig;
  }

  private generateCacheKey(nodes: WorkflowNode[], edges: WorkflowEdge[]): string {
    return `${nodes.map(n => n.id).join(',')}-${edges.map(e => e.id).join(',')}`;
  }

  private async toHierarchy(nodes: WorkflowNode[], edges: WorkflowEdge[]): Promise<Record<string, any>> {
    const hierarchy: Record<string, any>[] = [];
    const nodeMap = new Map(nodes.map(node => [node.id, node]));
    const edgeMap = new Map(edges.map(edge => [edge.id, edge]));

    // Find root nodes (nodes with no incoming edges)
    const rootNodes = nodes.filter(node => {
      return !edges.some(edge => edge.target === node.id);
    });

    // Helper function to build the hierarchy recursively
    const buildNodeHierarchy = (node: WorkflowNode): Record<string, any> => {
      const nodeData = { ...node };
      const outgoingEdges = Array.from(edgeMap.values()).filter(edge => edge.source === node.id);
      
      if (outgoingEdges.length > 0) {
        nodeData.children = outgoingEdges.map(edge => {
          const targetNode = nodeMap.get(edge.target);
          return targetNode ? buildNodeHierarchy(targetNode) : null;
        }).filter(Boolean);
      }

      return nodeData;
    };

    // Build the hierarchy from root nodes
    rootNodes.forEach(root => {
      hierarchy.push(buildNodeHierarchy(root));
    });

    return hierarchy;
  }

  private constructor() {
    super();
    this.options = {
      optimize: true,
      validate: true,
      components: [],
      metadata: {},
      errorHandler: undefined
    };
    this.cacheManager = WorkflowCacheManager.getInstance();
  }

  public static getInstance(): WorkflowTransformer {
    if (!WorkflowTransformer.instance) {
      WorkflowTransformer.instance = new WorkflowTransformer();
    }
    return WorkflowTransformer.instance;
  }

  public async transform(
    nodes: WorkflowNode[],
    edges: WorkflowEdge[],
    options: Partial<WorkflowTransformationOptions> = {}
  ): Promise<{ nodes: WorkflowNode[]; edges: WorkflowEdge[] }> {
    try {
      // Merge options with defaults
      const opts = {
        ...this.options,
        ...options
      };

      const key = this.generateCacheKey(nodes, edges);
      const cached = await this.cacheManager.retrieve(key);
      if (cached) {
        return cached;
      }

      if (opts.validate) {
        const validation = await WorkflowValidator.validateWorkflow(
          nodes,
          edges,
          opts.components
        );
        if (validation.errors.length > 0) {
          const error = new WorkflowError('Workflow validation failed', validation.errors);
          if (opts.errorHandler) {
            opts.errorHandler(error);
          }
          throw error;
        }
      }

      let transformedNodes = nodes;
      let transformedEdges = edges;

      if (opts.optimize) {
        transformedNodes = await this.optimizeNodes(nodes);
      }

      await this.cacheManager.store(key, { nodes: transformedNodes, edges: transformedEdges });
      return { nodes: transformedNodes, edges: transformedEdges };
    } catch (error) {
      const workflowError = error instanceof WorkflowError 
        ? error 
        : new WorkflowError('Workflow transformation failed', error instanceof Error ? error.message : String(error));
      
      if (this.options.errorHandler) {
        this.options.errorHandler(workflowError);
      }
      throw workflowError;
    }
  }

  private async optimizeNodes(nodes: WorkflowNode[]): Promise<WorkflowNode[]> {
    const optimizedNodes = [...nodes];
    for (const node of optimizedNodes) {
      if (node.data?.metadata) {
        node.data.metadata = await this.optimizeMetadata(node.data.metadata);
      }
      if (node.data?.validation) {
        node.data.validation = await this.optimizeValidation(node.data.validation);
      }
      if (node.data?.config) {
        node.data.config = await this.optimizeComponentConfig(node.data.config);
      }
    }
    return optimizedNodes;
  }

  private async optimizeEdges(edges: WorkflowEdge[]): Promise<WorkflowEdge[]> {
    const optimizedEdges = [...edges];
    for (const edge of optimizedEdges) {
      if (edge.data?.conditions) {
        edge.data.conditions = await this.optimizeConditions(edge.data.conditions);
      }
    }
    return optimizedEdges;
  }

  private async optimizeMetadata(metadata: Record<string, any>): Promise<Record<string, any>> {
    if (!metadata) return {};
    
    const optimizedMetadata = { ...metadata };
    Object.keys(optimizedMetadata).forEach(key => {
      if (optimizedMetadata[key] === undefined || optimizedMetadata[key] === null) {
        delete optimizedMetadata[key];
      }
    });
    return optimizedMetadata;
  }

  private async optimizeValidation(validation: Record<string, any>): Promise<Record<string, any>> {
    if (!validation) return {};
    
    const optimizedValidation = { ...validation };
    Object.keys(optimizedValidation).forEach(key => {
      if (optimizedValidation[key] === undefined || optimizedValidation[key] === null) {
        delete optimizedValidation[key];
      }
    });
    return optimizedValidation;
  }

  private async optimizeConditions(conditions: Record<string, any>): Promise<Record<string, any>> {
    if (!conditions) return {};
    
    const optimizedConditions = { ...conditions };
    Object.keys(optimizedConditions).forEach(key => {
      if (!optimizedConditions[key] || Object.keys(optimizedConditions[key]).length === 0) {
        delete optimizedConditions[key];
      }
    });
    return optimizedConditions;
  }

  private async optimizeComponentConfig(config: Record<string, any>): Promise<Record<string, any>> {
    if (!config) return {};
    
    const optimizedConfig = { ...config };
    Object.keys(optimizedConfig).forEach(key => {
      if (optimizedConfig[key] === undefined || optimizedConfig[key] === null) {
        delete optimizedConfig[key];
      }
    });
    return optimizedConfig;
  }

  private generateCacheKey(nodes: WorkflowNode[], edges: WorkflowEdge[]): string {
    return `${nodes.map(n => n.id).join(',')}-${edges.map(e => e.id).join(',')}`;
  }

  private async toHierarchy(nodes: WorkflowNode[], edges: WorkflowEdge[]): Promise<Record<string, any>> {
    const hierarchy: Record<string, any>[] = [];
    const nodeMap = new Map(nodes.map(node => [node.id, node]));
    const edgeMap = new Map(edges.map(edge => [edge.id, edge]));
      let transformedNodes = [...nodes];
      let transformedEdges = [...edges];

      if (optimize) {
        transformedNodes = await this.optimizeNodes(transformedNodes);
        transformedEdges = await this.optimizeEdges(transformedEdges);
      }

      // Cache result
      if (this.options.cache) {
        const cacheKey = this.generateCacheKey(transformedNodes, transformedEdges);
        await this.cacheManager.store(cacheKey, transformedNodes, transformedEdges);
      }

      return { nodes: transformedNodes, edges: transformedEdges };
    } catch (error) {
      if (error instanceof WorkflowError) {
        this.emit('error', error);
        throw error;
      }
      throw new WorkflowError({
        code: 'TRANSFORMATION_FAILED',
        message: error instanceof Error ? error.message : 'Unknown transformation error',
        type: 'runtime',
        metadata: { error }
      });
    }
  }

  private generateCacheKey(nodes: WorkflowNode[], edges: WorkflowEdge[]): string {
    const sortedNodeIds = nodes.map(n => n.id).sort();
    const sortedEdgeIds = edges.map(e => `${e.source}-${e.target}`).sort();
    
    return `${sortedNodeIds.join(',')}-${sortedEdgeIds.join(',')}`;
  }

  private buildHierarchy(nodes: WorkflowNode[], edges: WorkflowEdge[]): WorkflowNode[] {
    const hierarchy: WorkflowNode[] = [];
    const nodeMap = new Map(nodes.map(n => [n.id, n]));

    // Create a map of child nodes for each node
    const childrenMap = new Map<string, string[]>();
    edges.forEach(edge => {
      const source = edge.source;
      const target = edge.target;
      
      if (!childrenMap.has(source)) {
        childrenMap.set(source, []);
      }
      childrenMap.get(source)?.push(target);
    });

    // Find root nodes (nodes with no incoming edges)
    const rootNodes = nodes.filter(node => {
      return !edges.some(edge => edge.target === node.id);
    });

    // Helper function to build the hierarchy recursively
    const buildNodeHierarchy = (node: WorkflowNode): WorkflowNode => {
      const children = childrenMap.get(node.id) || [];
      const childNodes = children
        .map(childId => nodeMap.get(childId))
        .filter((n): n is WorkflowNode => n !== undefined);

      const hierarchicalNode = {
        ...node,
        children: childNodes.map(buildNodeHierarchy)
      } as WorkflowNode;

      return hierarchicalNode;
    };

    // Build the hierarchy from root nodes
    rootNodes.forEach(root => {
      hierarchy.push(buildNodeHierarchy(root));
    });

    return hierarchy;
  }

        // Remove empty handles if not needed
        sourceHandle: edge.sourceHandle || undefined,
        targetHandle: edge.targetHandle || undefined,
        data: {
          ...edge.data,
          // Optimize metadata
          metadata: this.optimizeMetadata(edge.data.metadata),
          // Optimize validation results
          validation: this.optimizeValidation(edge.data.validation)
        }
      };

      // Apply edge type-specific optimizations
      switch (edge.type) {
        case EdgeType.CONDITIONAL:
          optimizedEdge.data.conditions = this.optimizeConditions(edge.data.conditions);
          break;
        case EdgeType.SUCCESS:
        case EdgeType.FAILURE:
          optimizedEdge.data = await this.optimizeResultEdge(optimizedEdge.data);
          break;
      }

      return optimizedEdge;
    });
  }

  private optimizeMetadata(metadata: Record<string, any>): Record<string, any> {
    // Remove empty metadata fields
    const optimized: Record<string, any> = {};
    for (const [key, value] of Object.entries(metadata)) {
      if (value !== undefined && value !== null && value !== '') {
        optimized[key] = value;
      }
    }
    return optimized;
  }

  private optimizeValidation(validation: Record<string, any>): Record<string, any> {
    return {
      isValid: validation.isValid,
      errors: validation.errors.filter(Boolean),
      warnings: validation.warnings?.filter(Boolean) || []
    };
  }

  private optimizeConditions(conditions: Record<string, any>): Record<string, any> {
    return Object.entries(conditions)
      .filter(([_, value]) => value !== undefined && value !== null)
      .reduce((acc, [key, value]) => ({ ...acc, [key]: value }), {});
  }

  private async optimizeResultEdge(data: Record<string, any>): Promise<Record<string, any>> {
    // Add any edge-specific optimizations here
    return data;
  }

  private getComponentById(id: string): AIComponent | undefined {
    // Implementation for retrieving components
    return undefined;
  }

  private async applyComponentOptimizations(
    data: Record<string, any>,
    component: AIComponent
  ): Promise<Record<string, any>> {
    // Implementation for component-specific optimizations
    return data;
  }

  private generateCacheKey(nodes: WorkflowNode[], edges: WorkflowEdge[]): string {
    return JSON.stringify({
      nodes: nodes.map(n => ({ id: n.id, type: n.type })),
      edges: edges.map(e => ({ id: e.id, type: e.type, source: e.source, target: e.target }))
    });
  }

  /**
   * Convert workflow to a hierarchical structure
   * @param nodes - Array of workflow nodes
   * @param edges - Array of workflow edges
   * @returns Hierarchical workflow structure
   */
  static toHierarchy(nodes: WorkflowNode[], edges: WorkflowEdge[]): Record<string, any> {
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const graph = new Map<string, string[]>();

    edges.forEach(edge => {
      const source = graph.get(edge.source) || [];
      source.push(edge.target);
      graph.set(edge.source, source);
    });

    const visited = new Set<string>();
    const hierarchy: any[] = [];

    const buildHierarchy = (nodeId: string, level: number = 0): any => {
      if (visited.has(nodeId)) return null;
      visited.add(nodeId);

      const node = nodeMap.get(nodeId);
      if (!node) return null;

      const children = graph.get(nodeId) || [];
      return {
        ...node,
        children: children
          .map(childId => buildHierarchy(childId, level + 1))
          .filter(Boolean),
        level,
        metadata: {
          depth: level,
          connections: {
            incoming: edges.filter(e => e.target === nodeId).length,
            outgoing: edges.filter(e => e.source === nodeId).length
          }
        }
      };
    };

    // Find root nodes (nodes with no incoming connections)
    const rootNodes = nodes.filter(node => !edges.some(e => e.target === node.id));
    rootNodes.forEach(root => {
      const hierarchyNode = buildHierarchy(root.id);
      if (hierarchyNode) {
        hierarchy.push(hierarchyNode);
      }
    });

    return {
      nodes: hierarchy,
      metadata: {
        totalNodes: nodes.length,
        totalEdges: edges.length,
        depth: Math.max(...hierarchy.map(n => n.level || 0), 0)
      }
    };
  }
}
    // Find root nodes (nodes with no incoming edges)
    const rootNodes = nodes.filter(node => {
      return !edges.some(edge => edge.target === node.id);
    });

    rootNodes.forEach(root => {
      const hierarchyNode = buildHierarchy(root.id);
      if (hierarchyNode) hierarchy.push(hierarchyNode);
    });

    return hierarchy;
  }

  /**
   * Convert hierarchical structure back to flat nodes and edges
   * @param hierarchy - Hierarchical workflow structure
   * @returns Flat workflow data
   */
  static fromHierarchy(hierarchy: any[]): { nodes: Node[]; edges: Edge[] } {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    const idMap: Record<string, string> = {};

    const processNode = (node: any, parentId?: string): string => {
      // Generate new ID if needed
      const nodeId = node.id || `node_${Date.now()}_${nodes.length}`;
      idMap[nodeId] = nodeId;

      const newNode: Node = {
        id: nodeId,
        type: node.type,
        position: node.position || { x: 0, y: 0 },
        data: {
          name: node.name,
          componentId: node.componentId,
          config: node.config || {},
        },
      };

      nodes.push(newNode);

      // Create edge to parent if exists
      if (parentId) {
        edges.push({
          id: `edge_${Date.now()}_${edges.length}`,
          source: parentId,
          target: nodeId,
        });
      }

      // Process children
      node.children?.forEach((child: any) => {
        processNode(child, nodeId);
      });

      return nodeId;
    };

    hierarchy.forEach(root => processNode(root));

    return { nodes, edges };
  }

  /**
   * Generate workflow metadata
   * @param nodes - Array of workflow nodes
   * @param edges - Array of workflow edges
   * @returns Workflow metadata
   */
  static generateMetadata(nodes: Node[], edges: Edge[]): Record<string, any> {
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const edgeMap = new Map(edges.map(e => [e.id, e]));

    return {
      nodes: {
        count: nodes.length,
        types: Array.from(new Set(nodes.map(n => n.type))),
        components: Array.from(new Set(nodes.map(n => n.data.componentId))),
      },
      edges: {
        count: edges.length,
        connections: Array.from(new Set(edges.map(e => `${e.source}-${e.target}`))),
      },
      structure: {
        startNodes: nodes.filter(n => n.type === 'start').length,
        endNodes: nodes.filter(n => n.type === 'end').length,
        orphanedNodes: nodes.filter(
          n => !edges.some(e => e.source === n.id || e.target === n.id)
        ).length,
      },
      complexity: {
        depth: this.calculateDepth(nodes, edges),
        branching: this.calculateBranchingFactor(nodes, edges),
      },
      timestamp: new Date().toISOString(),
    };
  }

  private static calculateDepth(nodes: Node[], edges: Edge[]): number {
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const graph = new Map<string, string[]>();

    edges.forEach(edge => {
      const source = graph.get(edge.source) || [];
      source.push(edge.target);
      graph.set(edge.source, source);
    });

    const visited = new Set<string>();
    let maxDepth = 0;

    const traverse = (nodeId: string, currentDepth: number = 0): void => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);

      maxDepth = Math.max(maxDepth, currentDepth);

      const children = graph.get(nodeId) || [];
      children.forEach(child => traverse(child, currentDepth + 1));
    };

    // Start from all nodes (in case of multiple disconnected graphs)
    nodes.forEach(node => traverse(node.id));

    return maxDepth;
  }

  private static calculateBranchingFactor(nodes: Node[], edges: Edge[]): number {
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const graph = new Map<string, string[]>();

    edges.forEach(edge => {
      const source = graph.get(edge.source) || [];
      source.push(edge.target);
      graph.set(edge.source, source);
    });

    const branchingFactors = Array.from(graph.values())
      .map(children => children.length)
      .filter(count => count > 0);

    if (branchingFactors.length === 0) return 0;

    const sum = branchingFactors.reduce((a, b) => a + b, 0);
    return sum / branchingFactors.length;
  }
}
