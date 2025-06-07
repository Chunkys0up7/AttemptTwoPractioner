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
        const validation = WorkflowValidator.validateWorkflow(
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
    const sortedNodeIds = nodes.map(n => n.id).sort();
    const sortedEdgeIds = edges.map(e => `${e.source}-${e.target}`).sort();
    
    return `${sortedNodeIds.join(',')}-${sortedEdgeIds.join(',')}`;
  }

  private buildHierarchy(nodes: WorkflowNode[], edges: WorkflowEdge[]): WorkflowNode[] {
    // Create a map of child nodes for each node
    const childrenMap = new Map<string, string[]>();
    
    // Build the children map
    edges.forEach(edge => {
      if (!childrenMap.has(edge.source)) {
        childrenMap.set(edge.source, []);
      }
      childrenMap.get(edge.source)?.push(edge.target);
    });

    // Find root nodes (nodes with no incoming edges)
    const rootNodes = nodes.filter(node => 
      !edges.some(edge => edge.target === node.id)
    );

    // Build hierarchy recursively
    const buildNodeHierarchy = (node: WorkflowNode): WorkflowNode => {
      const children = childrenMap.get(node.id)?.map(childId => {
        const childNode = nodes.find(n => n.id === childId);
        return childNode ? buildNodeHierarchy(childNode) : null;
      }).filter((n): n is WorkflowNode => n !== null);

      return {
        ...node,
        data: {
          ...node.data,
          children: children || []
        }
      };
    };

    // Build the hierarchy from root nodes
    const hierarchy = rootNodes.map(root => buildNodeHierarchy(root));
    return hierarchy;
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
