import { WorkflowNode, WorkflowEdge, WorkflowValidationResult, NodeType, EdgeType, AIComponent } from '../types/workflow';

export class WorkflowValidator {
  private static validateNodeConfig(
    config: Record<string, any>,
    component: AIComponent
  ): string[] {
    const errors: string[] = [];

    // Check required fields
    if (component.validation?.rules?.required) {
      Object.entries(component.validation.rules.required).forEach(([field]) => {
        if (!(field in config)) {
          errors.push(`Missing required field: ${field}`);
        }
      });
    }

    // Check field constraints
    if (component.validation?.constraints) {
      Object.entries(component.validation.constraints).forEach(([field, constraints]) => {
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
    }

    return errors;
  }

  private static validateEdgeConditions(conditions: Record<string, any>): string[] {
    const errors: string[] = [];
    
    // Add validation logic for edge conditions here
    // This is a placeholder for now
    return errors;
  }

  private static validateComponentCompatibility(
    sourceComponent: AIComponent,
    targetComponent: AIComponent
  ): string[] {
    const errors: string[] = [];
    
    // Check if target component can be connected to source component
    if (!targetComponent.compatibility?.canConnectTo?.includes(sourceComponent.type)) {
      errors.push(`Component ${targetComponent.id} cannot be connected to component ${sourceComponent.id}`);
    }
    
    // Check input/output compatibility
    const missingInputs = targetComponent.inputs?.filter((input: string) => 
      !sourceComponent.outputs?.includes(input)
    ) || [];
    
    if (missingInputs.length > 0) {
      errors.push(`Missing required inputs: ${missingInputs.join(', ')}`);
    }
    
    return errors;
  }

  private static validateWorkflowStructure(
    nodes: WorkflowNode[],
    edges: WorkflowEdge[]
  ): string[] {
    const errors: string[] = [];
    
    // Create adjacency list
    const adjList: Record<string, string[]> = {};
    nodes.forEach((node: WorkflowNode) => adjList[node.id] = []);
    
    edges.forEach((edge: WorkflowEdge) => {
      adjList[edge.source].push(edge.target);
    });
    
    // Check for cycles using DFS
    const visited = new Set<string>();
    const recStack = new Set<string>();
    
    const hasCycle = (node: string): boolean => {
      if (recStack.has(node)) return true;
      if (visited.has(node)) return false;
      
      visited.add(node);
      recStack.add(node);
      
      for (const neighbor of adjList[node]) {
        if (hasCycle(neighbor)) {
          errors.push(`Cycle detected between nodes ${node} and ${neighbor}`);
          return true;
        }
      }
      
      recStack.delete(node);
      return false;
    };
    
    nodes.forEach((node: WorkflowNode) => {
      if (!visited.has(node.id)) {
        hasCycle(node.id);
      }
    });
    
    return errors;
  }

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

    // Validate node IDs uniqueness
    const nodeIds = nodes.map((n: WorkflowNode) => n.id);
    const duplicateIds = nodeIds.filter((id: string, index: number) => nodeIds.indexOf(id) !== index);
    if (duplicateIds.length > 0) {
      result.errors.push(`Duplicate node IDs found: ${duplicateIds.join(', ')}`);
      result.isValid = false;
    }

    // Validate start/end nodes
    const startNodes = nodes.filter((n: WorkflowNode) => n.type === NodeType.START);
    const endNodes = nodes.filter((n: WorkflowNode) => n.type === NodeType.END);

    if (startNodes.length === 0) {
      result.errors.push('Workflow must contain exactly one start node');
      result.isValid = false;
    } else if (startNodes.length > 1) {
      result.errors.push('Workflow cannot contain more than one start node');
      result.isValid = false;
    }

    if (endNodes.length === 0) {
      result.errors.push('Workflow must contain at least one end node');
      result.isValid = false;
    }

    // Node validation
    nodes.forEach((node: WorkflowNode) => {
      const nodeErrors: string[] = [];
      
      // Validate node type
      if (!Object.values(NodeType).includes(node.type)) {
        nodeErrors.push(`Invalid node type: ${node.type}`);
      }

      // Validate node connections
      const incoming = edges.filter((e: WorkflowEdge) => e.target === node.id).length;
      const outgoing = edges.filter((e: WorkflowEdge) => e.source === node.id).length;

      if (node.type === NodeType.START) {
        if (incoming > 0) {
          nodeErrors.push('Start node cannot have incoming connections');
        }
        if (outgoing === 0) {
          nodeErrors.push('Start node must have at least one outgoing connection');
        }
      }

      if (node.type === NodeType.END) {
        if (outgoing > 0) {
          nodeErrors.push('End node cannot have outgoing connections');
        }
        if (incoming === 0) {
          nodeErrors.push('End node must have at least one incoming connection');
        }
      }

      // Validate node configuration against component
      if (node.data.componentId) {
        const component = components.find((c: AIComponent) => c.id === node.data.componentId);
        if (!component) {
          nodeErrors.push(`Component not found for node: ${node.data.componentId}`);
        } else {
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
    edges.forEach((edge: WorkflowEdge) => {
      const edgeErrors: string[] = [];
      
      // Validate edge type
      if (!Object.values(EdgeType).includes(edge.type)) {
        edgeErrors.push(`Invalid edge type: ${edge.type}`);
      }

      // Validate edge connections
      const sourceNode = nodes.find((n: WorkflowNode) => n.id === edge.source);
      const targetNode = nodes.find((n: WorkflowNode) => n.id === edge.target);

      if (!sourceNode) {
        edgeErrors.push(`Source node ${edge.source} not found`);
      }

      if (!targetNode) {
        edgeErrors.push(`Target node ${edge.target} not found`);
      }

      // Validate edge directionality
      if (sourceNode && targetNode) {
        if (sourceNode.type === NodeType.END) {
          edgeErrors.push('End node cannot have outgoing connections');
        }
        if (targetNode.type === NodeType.START) {
          edgeErrors.push('Start node cannot have incoming connections');
        }
      }

      // Validate edge conditions
      if (edge.data.conditions) {
        const conditionErrors = this.validateEdgeConditions(edge.data.conditions);
        if (conditionErrors.length > 0) {
          edgeErrors.push(...conditionErrors);
        }
      }

      // Validate component compatibility
      if (sourceNode && targetNode && sourceNode.data.componentId && targetNode.data.componentId) {
        const sourceComponent = components.find((c: AIComponent) => c.id === sourceNode.data.componentId);
        const targetComponent = components.find((c: AIComponent) => c.id === targetNode.data.componentId);
        
        if (sourceComponent && targetComponent) {
          const compatibilityErrors = this.validateComponentCompatibility(sourceComponent, targetComponent);
          if (compatibilityErrors.length > 0) {
            edgeErrors.push(...compatibilityErrors);
          }
        }
      }

      if (edgeErrors.length > 0) {
        result.edgeErrors[edge.id] = edgeErrors;
        result.errors.push(...edgeErrors.map(err => `Edge ${edge.id}: ${err}`));
        result.isValid = false;
      }
    });

    // Validate workflow structure (acyclic)
    const cycleErrors = this.validateWorkflowStructure(nodes, edges);
    if (cycleErrors.length > 0) {
      result.errors.push(...cycleErrors);
      result.isValid = false;
    }

    return result;
  }
}

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

  private static validateComponentCompatibility(
    sourceComponent: AIComponent,
    targetComponent: AIComponent
  ): string[] {
    const errors: string[] = [];

    // Check if components can be connected
    if (!sourceComponent.compatibility?.canConnectTo?.includes(targetComponent.type)) {
      errors.push(`Component ${sourceComponent.id} cannot connect to component ${targetComponent.id}`);
    }

    // Check data flow compatibility
    if (sourceComponent.outputs && targetComponent.inputs) {
      const missingInputs = targetComponent.inputs.filter(input =>
        !sourceComponent.outputs.includes(input)
      );
      if (missingInputs.length > 0) {
        errors.push(`Component ${targetComponent.id} requires inputs that ${sourceComponent.id} doesn't provide: ${missingInputs.join(', ')}`);
      }
    }

    return errors;
  }

  private static validateWorkflowStructure(
    nodes: WorkflowNode[],
    edges: WorkflowEdge[]
  ): string[] {
    const errors: string[] = [];
    const visited = new Set<string>();
    const visiting = new Set<string>();

    const hasCycle = (nodeId: string): boolean => {
      if (visited.has(nodeId)) return false;
      if (visiting.has(nodeId)) return true;

      visiting.add(nodeId);
      
      const outgoingEdges = edges.filter(e => e.source === nodeId);
      for (const edge of outgoingEdges) {
        const targetNode = nodes.find(n => n.id === edge.target);
        if (targetNode && hasCycle(targetNode.id)) {
          errors.push(`Cycle detected in workflow at node: ${nodeId}`);
          return true;
        }
      }

      visiting.delete(nodeId);
      visited.add(nodeId);
      return false;
    };

    // Check for cycles starting from each node
    nodes.forEach(node => {
      if (!visited.has(node.id)) {
        hasCycle(node.id);
      }
    });

    return errors;
  }
}
