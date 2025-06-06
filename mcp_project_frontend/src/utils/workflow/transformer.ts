import { Node, Edge, AIComponent } from '../../types/workflow';

/**
 * Workflow transformation utility functions
 */
export interface WorkflowTransformationOptions {
  optimize?: boolean;
  validate?: boolean;
  components?: AIComponent[];
}

export class WorkflowTransformer {
  /**
   * Transform workflow data into a more optimized format
   * @param nodes - Array of workflow nodes
   * @param edges - Array of workflow edges
   * @param options - Transformation options
   * @returns Transformed workflow data
   */
  static transform(
    nodes: Node[],
    edges: Edge[],
    options: WorkflowTransformationOptions = {}
  ): { nodes: Node[]; edges: Edge[] } {
    const { optimize = true, validate = true, components = [] } = options;

    if (validate) {
      const validationResult = WorkflowValidator.validateWorkflow(nodes, edges, components);
      if (!validationResult.isValid) {
        throw new Error(`Workflow validation failed: ${validationResult.errors.join(', ')}`);
      }
    }

    let transformedNodes = [...nodes];
    let transformedEdges = [...edges];

    if (optimize) {
      transformedNodes = this.optimizeNodes(transformedNodes);
      transformedEdges = this.optimizeEdges(transformedEdges);
    }

    return { nodes: transformedNodes, edges: transformedEdges };
  }

  private static optimizeNodes(nodes: Node[]): Node[] {
    return nodes.map(node => ({
      ...node,
      data: {
        ...node.data,
        // Remove empty configuration
        config: node.data.config && Object.keys(node.data.config).length > 0
          ? node.data.config
          : undefined,
      },
    }));
  }

  private static optimizeEdges(edges: Edge[]): Edge[] {
    return edges.map(edge => ({
      ...edge,
      // Remove empty handles if not needed
      sourceHandle: edge.sourceHandle || undefined,
      targetHandle: edge.targetHandle || undefined,
    }));
  }

  /**
   * Convert workflow to a hierarchical structure
   * @param nodes - Array of workflow nodes
   * @param edges - Array of workflow edges
   * @returns Hierarchical workflow structure
   */
  static toHierarchy(nodes: Node[], edges: Edge[]): Record<string, any> {
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
      };
    };

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
