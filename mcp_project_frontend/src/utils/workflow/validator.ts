import { WorkflowNode, WorkflowEdge, WorkflowValidationResult, NodeType, EdgeType, AIComponent } from '../types/workflow';

export class WorkflowValidator {
  static validateWorkflow(
    nodes: WorkflowNode[],
    edges: WorkflowEdge[],
    components: AIComponent[]
  ): WorkflowValidationResult {
    const result: WorkflowValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      nodeErrors: {},
      edgeErrors: {}
    };

    // Basic validation
    if (!nodes.length) {
      result.errors.push('Workflow must contain at least one node');
      result.isValid = false;
    }

    // Node validation
    nodes.forEach(node => {
      const nodeErrors: string[] = [];
      
      // Validate node type
      if (!Object.values(NodeType).includes(node.type)) {
        nodeErrors.push(`Invalid node type: ${node.type}`);
      }

      // Validate node connections
      const incoming = edges.filter(e => e.target === node.id).length;
      const outgoing = edges.filter(e => e.source === node.id).length;

      if (node.type === NodeType.START && incoming > 0) {
        nodeErrors.push('Start node cannot have incoming connections');
      }

      if (node.type === NodeType.END && outgoing > 0) {
        nodeErrors.push('End node cannot have outgoing connections');
      }

      // Validate node configuration against component
      if (node.data.componentId) {
        const component = components.find(c => c.id === node.data.componentId);
        if (component) {
          const configErrors = this.validateNodeConfig(node.data.config, component);
          if (configErrors.length > 0) {
            nodeErrors.push(...configErrors);
          }
        }
      }

      if (nodeErrors.length > 0) {
        result.nodeErrors[node.id] = nodeErrors;
        result.errors.push(...nodeErrors.map(err => `Node ${node.id}: ${err}`));
        result.isValid = false;
      }
    });

    // Edge validation
    edges.forEach(edge => {
      const edgeErrors: string[] = [];
      
      // Validate edge type
      if (!Object.values(EdgeType).includes(edge.type)) {
        edgeErrors.push(`Invalid edge type: ${edge.type}`);
      }

      // Validate edge connections
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);

      if (!sourceNode) {
        edgeErrors.push(`Source node ${edge.source} not found`);
      }

      if (!targetNode) {
        edgeErrors.push(`Target node ${edge.target} not found`);
      }

      // Validate edge conditions
      if (edge.data.conditions) {
        const conditionErrors = this.validateEdgeConditions(edge.data.conditions);
        if (conditionErrors.length > 0) {
          edgeErrors.push(...conditionErrors);
        }
      }

      if (edgeErrors.length > 0) {
        result.edgeErrors[edge.id] = edgeErrors;
        result.errors.push(...edgeErrors.map(err => `Edge ${edge.id}: ${err}`));
        result.isValid = false;
      }
    });

    return result;
  }

  private static validateNodeConfig(
    config: Record<string, any>,
    component: AIComponent
  ): string[] {
    const errors: string[] = [];

    // Check required fields
    Object.entries(component.validation.rules.required || {}).forEach(([field]) => {
      if (!(field in config)) {
        errors.push(`Missing required field: ${field}`);
      }
    });

    // Check field constraints
    Object.entries(component.validation.constraints || {}).forEach(([field, constraints]) => {
      if (field in config) {
        // Check type
        if (constraints.type && typeof config[field] !== constraints.type) {
          errors.push(`Field ${field} must be of type ${constraints.type}`);
        }

        // Check min/max values
        if (constraints.min !== undefined && config[field] < constraints.min) {
          errors.push(`Field ${field} must be at least ${constraints.min}`);
        }

        if (constraints.max !== undefined && config[field] > constraints.max) {
          errors.push(`Field ${field} must be at most ${constraints.max}`);
        }

        // Check enum values
        if (constraints.enum && !constraints.enum.includes(config[field])) {
          errors.push(`Field ${field} must be one of: ${constraints.enum.join(', ')}`);
        }
      }
    });

    return errors;
  }

  private static validateEdgeConditions(
    conditions: Record<string, any>
  ): string[] {
    const errors: string[] = [];

    // Basic condition validation
    if (Object.keys(conditions).length === 0) {
      errors.push('Edge conditions cannot be empty');
    }

    // Validate condition types
    Object.entries(conditions).forEach(([field, value]) => {
      if (typeof value !== 'string' && typeof value !== 'number' && typeof value !== 'boolean') {
        errors.push(`Condition ${field} must be a string, number, or boolean`);
      }
    });

    return errors;
  }
}
