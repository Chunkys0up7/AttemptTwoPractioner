import { Node, Edge, AIComponent } from '../../types/workflow';

/**
 * Workflow validation utility functions
 */
export interface WorkflowValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export class WorkflowValidator {
  /**
   * Validate workflow structure
   * @param nodes - Array of workflow nodes
   * @param edges - Array of workflow edges
   * @param components - Available AI components
   * @returns Validation result
   */
  static validateWorkflow(nodes: Node[], edges: Edge[], components: AIComponent[]): WorkflowValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Validate nodes
    this.validateNodes(nodes, components, errors, warnings);

    // Validate edges
    this.validateEdges(nodes, edges, errors, warnings);

    // Validate workflow structure
    this.validateWorkflowStructure(nodes, edges, errors, warnings);

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  private static validateNodes(nodes: Node[], components: AIComponent[], errors: string[], warnings: string[]): void {
    const componentMap = new Map(components.map(c => [c.id, c]));

    nodes.forEach(node => {
      // Validate required fields
      if (!node.id) errors.push(`Node is missing required id`);
      if (!node.type) errors.push(`Node ${node.id} is missing required type`);
      if (!node.position) errors.push(`Node ${node.id} is missing required position`);
      if (!node.data) errors.push(`Node ${node.id} is missing required data`);

      // Validate component existence
      const component = componentMap.get(node.data.componentId);
      if (!component) {
        errors.push(`Node ${node.id} uses non-existent component: ${node.data.componentId}`);
      } else {
        // Validate component compatibility
        if (node.type !== component.type) {
          warnings.push(`Node ${node.id} type (${node.type}) doesn't match component type (${component.type})`);
        }
      }

      // Validate configuration
      if (node.data.config) {
        this.validateConfiguration(node.data.config, component?.typeSpecificData?.schema || {}, errors, warnings);
      }
    });
  }

  private static validateEdges(nodes: Node[], edges: Edge[], errors: string[], warnings: string[]): void {
    const nodeIds = new Set(nodes.map(n => n.id));

    edges.forEach(edge => {
      // Validate edge connections
      if (!nodeIds.has(edge.source)) {
        errors.push(`Edge ${edge.id} references non-existent source node: ${edge.source}`);
      }
      if (!nodeIds.has(edge.target)) {
        errors.push(`Edge ${edge.id} references non-existent target node: ${edge.target}`);
      }

      // Check for self-loops
      if (edge.source === edge.target) {
        warnings.push(`Edge ${edge.id} creates a self-loop`);
      }

      // Check for duplicate edges
      const duplicate = edges.find(
        e => e !== edge && e.source === edge.source && e.target === edge.target
      );
      if (duplicate) {
        warnings.push(`Duplicate edge found between ${edge.source} and ${edge.target}`);
      }
    });
  }

  private static validateWorkflowStructure(nodes: Node[], edges: Edge[], errors: string[], warnings: string[]): void {
    // Check for start node
    const startNodes = nodes.filter(n => n.type === 'start');
    if (startNodes.length === 0) {
      errors.push('Workflow must have at least one start node');
    } else if (startNodes.length > 1) {
      warnings.push('Workflow has multiple start nodes');
    }

    // Check for cycles
    if (this.hasCycles(nodes, edges)) {
      errors.push('Workflow contains cycles');
    }

    // Check for orphaned nodes
    const connectedNodes = new Set<string>();
    edges.forEach(edge => {
      connectedNodes.add(edge.source);
      connectedNodes.add(edge.target);
    });

    const orphanedNodes = nodes.filter(n => !connectedNodes.has(n.id));
    if (orphanedNodes.length > 0) {
      warnings.push(`Found ${orphanedNodes.length} orphaned nodes`);
    }
  }

  private static validateConfiguration(
    config: Record<string, any>,
    schema: Record<string, any>,
    errors: string[],
    warnings: string[]
  ): void {
    // Validate required fields
    Object.entries(schema).forEach(([key, value]) => {
      if (value.required && config[key] === undefined) {
        errors.push(`Required configuration field '${key}' is missing`);
      }

      // Validate types
      if (config[key] !== undefined && typeof config[key] !== value.type) {
        warnings.push(`Configuration field '${key}' has incorrect type`);
      }
    });

    // Check for unknown fields
    const unknownFields = Object.keys(config).filter(key => !schema[key]);
    if (unknownFields.length > 0) {
      warnings.push(`Unknown configuration fields: ${unknownFields.join(', ')}`);
    }
  }

  private static hasCycles(nodes: Node[], edges: Edge[]): boolean {
    const graph = new Map<string, Set<string>>();
    nodes.forEach(node => graph.set(node.id, new Set()));

    edges.forEach(edge => {
      const source = graph.get(edge.source) || new Set();
      source.add(edge.target);
      graph.set(edge.source, source);
    });

    const visited = new Set<string>();
    const visiting = new Set<string>();

    const visit = (node: string): boolean => {
      if (visited.has(node)) return false;
      if (visiting.has(node)) return true;

      visiting.add(node);
      const children = graph.get(node) || new Set();
      
      for (const child of children) {
        if (visit(child)) return true;
      }

      visiting.delete(node);
      visited.add(node);
      return false;
    };

    for (const node of nodes) {
      if (visit(node.id)) return true;
    }

    return false;
  }
}
