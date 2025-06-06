import { Node, Edge, AIComponent } from '../../types/workflow';

/**
 * Workflow execution utility functions
 */
export interface WorkflowExecutionOptions {
  parallel?: boolean;
  timeout?: number;
  retry?: number;
  components?: AIComponent[];
}

export interface WorkflowExecutionResult {
  success: boolean;
  results: Record<string, any>;
  errors: Record<string, string[]>;
  timing: {
    start: Date;
    end: Date;
    duration: number;
  };
}

export class WorkflowExecutor {
  /**
   * Execute a workflow
   * @param nodes - Array of workflow nodes
   * @param edges - Array of workflow edges
   * @param options - Execution options
   * @returns Execution result
   */
  static async execute(
    nodes: Node[],
    edges: Edge[],
    options: WorkflowExecutionOptions = {}
  ): Promise<WorkflowExecutionResult> {
    const { parallel = true, timeout = 30000, retry = 3, components = [] } = options;
    const startTime = new Date();
    const results: Record<string, any> = {};
    const errors: Record<string, string[]> = {};

    // Validate workflow before execution
    const validationResult = WorkflowValidator.validateWorkflow(nodes, edges, components);
    if (!validationResult.isValid) {
      return {
        success: false,
        results: {},
        errors: { workflow: validationResult.errors },
        timing: {
          start: startTime,
          end: new Date(),
          duration: 0,
        },
      };
    }

    // Build execution graph
    const graph = this.buildExecutionGraph(nodes, edges);
    const executionOrder = this.getExecutionOrder(graph);

    // Execute nodes in order
    for (const nodeId of executionOrder) {
      const node = nodes.find(n => n.id === nodeId);
      if (!node) continue;

      try {
        const nodeResult = await this.executeNode(
          node,
          results,
          { parallel, timeout, retry },
          components
        );
        results[node.id] = nodeResult;
      } catch (error) {
        errors[node.id] = Array.isArray(error) ? error : [error.message];
      }
    }

    const endTime = new Date();
    const success = Object.keys(errors).length === 0;

    return {
      success,
      results,
      errors,
      timing: {
        start: startTime,
        end: endTime,
        duration: endTime.getTime() - startTime.getTime(),
      },
    };
  }

  private static buildExecutionGraph(nodes: Node[], edges: Edge[]): Map<string, string[]> {
    const graph = new Map();
    nodes.forEach(node => graph.set(node.id, []));

    edges.forEach(edge => {
      const source = graph.get(edge.source) || [];
      source.push(edge.target);
      graph.set(edge.source, source);
    });

    return graph;
  }

  private static getExecutionOrder(graph: Map<string, string[]>): string[] {
    const order: string[] = [];
    const visited = new Set<string>();
    const visiting = new Set<string>();

    const visit = (nodeId: string): void => {
      if (visited.has(nodeId)) return;
      if (visiting.has(nodeId)) throw new Error('Cycle detected');

      visiting.add(nodeId);

      const children = graph.get(nodeId) || [];
      children.forEach(child => visit(child));

      visiting.delete(nodeId);
      visited.add(nodeId);
      order.unshift(nodeId);
    };

    // Start from all nodes (in case of multiple disconnected graphs)
    graph.forEach((_, nodeId) => {
      if (!visited.has(nodeId)) {
        visit(nodeId);
      }
    });

    return order;
  }

  private static async executeNode(
    node: Node,
    results: Record<string, any>,
    options: {
      parallel: boolean;
      timeout: number;
      retry: number;
    },
    components: AIComponent[]
  ): Promise<any> {
    const component = components.find(c => c.id === node.data.componentId);
    if (!component) {
      throw new Error(`Component not found: ${node.data.componentId}`);
    }

    const config = node.data.config || {};
    const inputs = this.getInputs(node, results, graph);

    let result;
    let attempts = 0;

    while (attempts < options.retry) {
      try {
        result = await this.executeComponent(component, inputs, config, options);
        break;
      } catch (error) {
        attempts++;
        if (attempts === options.retry) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, 1000 * attempts));
      }
    }

    return result;
  }

  private static getInputs(
    node: Node,
    results: Record<string, any>,
    graph: Map<string, string[]>
  ): Record<string, any> {
    const inputs: Record<string, any> = {};
    const parentNodes = Array.from(graph.entries())
      .filter(([_, children]) => children.includes(node.id))
      .map(([id]) => id);

    parentNodes.forEach(parentId => {
      if (results[parentId]) {
        const parentResult = results[parentId];
        if (parentResult.output) {
          inputs[parentId] = parentResult.output;
        } else {
          inputs[parentId] = parentResult;
        }
      }
    });

    return inputs;
  }

  private static async executeComponent(
    component: AIComponent,
    inputs: Record<string, any>,
    config: Record<string, any>,
    options: {
      parallel: boolean;
      timeout: number;
    }
  ): Promise<any> {
    // Simulate component execution with timeout
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error('Execution timeout'));
      }, options.timeout);

      // Simulate execution time based on component type
      const executionTime = component.type === 'ai' ? 2000 : 500;
      setTimeout(() => {
        clearTimeout(timeoutId);
        resolve({
          componentId: component.id,
          inputs,
          config,
          output: this.generateMockOutput(component),
          timestamp: new Date(),
        });
      }, executionTime);
    });
  }

  private static generateMockOutput(component: AIComponent): any {
    const output: any = {};
    
    // Generate mock output based on component type
    switch (component.type) {
      case 'ai':
        output.result = 'Success';
        output.metrics = {
          accuracy: Math.random(),
          confidence: Math.random(),
        };
        break;
      case 'data':
        output.data = Array.from({ length: 5 }, () => Math.random());
        break;
      case 'action':
        output.status = 'completed';
        output.timestamp = new Date().toISOString();
        break;
      default:
        output.message = 'Execution completed';
    }

    return output;
  }
}
