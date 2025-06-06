import { useState, useCallback, useEffect } from 'react';
import { WorkflowExecutionResult } from '../../utils/workflow/execution';
import { Node, Edge, AIComponent } from '../../types/workflow';

/**
 * Custom hook for workflow execution
 * @param nodes - Array of workflow nodes
 * @param edges - Array of workflow edges
 * @param components - Available AI components
 * @returns Execution state and execution methods
 */
export const useWorkflowExecution = (
  nodes: Node[],
  edges: Edge[],
  components: AIComponent[]
) => {
  const [executionResult, setExecutionResult] = useState<WorkflowExecutionResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (options: {
    parallel?: boolean;
    timeout?: number;
    retry?: number;
  } = {}) => {
    setIsExecuting(true);
    setError(null);

    try {
      const result = await WorkflowExecutor.execute(nodes, edges, {
        ...options,
        components,
      });

      setExecutionResult(result);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
      throw err;
    } finally {
      setIsExecuting(false);
    }
  }, [nodes, edges, components]);

  const executeNode = useCallback(
    async (nodeId: string, options: {
      timeout?: number;
      retry?: number;
    } = {}) => {
      const node = nodes.find(n => n.id === nodeId);
      if (!node) {
        throw new Error(`Node not found: ${nodeId}`);
      }

      const component = components.find(c => c.id === node.data.componentId);
      if (!component) {
        throw new Error(`Component not found: ${node.data.componentId}`);
      }

      const config = node.data.config || {};
      const inputs = WorkflowTransformer.getInputs(node, {}, new Map());

      try {
        const result = await WorkflowExecutor.executeComponent(
          component,
          inputs,
          config,
          options
        );

        return result;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Node execution failed');
        throw err;
      }
    },
    [nodes, components]
  );

  const clearExecution = useCallback(() => {
    setExecutionResult(null);
    setError(null);
  }, []);

  // Auto-clear execution state when nodes or edges change
  useEffect(() => {
    clearExecution();
  }, [nodes, edges, clearExecution]);

  return {
    executionResult,
    isExecuting,
    error,
    execute,
    executeNode,
    clearExecution,
  };
};
