import { useState, useCallback, useEffect } from 'react';
import { WorkflowValidationResult } from '../../utils/workflow/validation';
import { Node, Edge, AIComponent } from '../../types/workflow';

/**
 * Custom hook for workflow validation
 * @param nodes - Array of workflow nodes
 * @param edges - Array of workflow edges
 * @param components - Available AI components
 * @returns Validation state and validation methods
 */
export const useWorkflowValidation = (
  nodes: Node[],
  edges: Edge[],
  components: AIComponent[]
) => {
  const [validationResult, setValidationResult] = useState<WorkflowValidationResult>({
    isValid: false,
    errors: [],
    warnings: [],
  });

  const validate = useCallback(() => {
    const result = WorkflowValidator.validateWorkflow(nodes, edges, components);
    setValidationResult(result);
    return result;
  }, [nodes, edges, components]);

  const validateNode = useCallback(
    (nodeId: string) => {
      const node = nodes.find(n => n.id === nodeId);
      if (!node) return;

      const result = WorkflowValidator.validateNodes(
        [node],
        components,
        [],
        []
      );

      // Update validation result if node is invalid
      if (!result.isValid) {
        setValidationResult(prev => ({
          ...prev,
          errors: [...prev.errors, ...result.errors],
          warnings: [...prev.warnings, ...result.warnings],
        }));
      }
    },
    [nodes, components]
  );

  const validateEdge = useCallback(
    (edgeId: string) => {
      const edge = edges.find(e => e.id === edgeId);
      if (!edge) return;

      const result = WorkflowValidator.validateEdges(
        nodes,
        [edge],
        [],
        []
      );

      // Update validation result if edge is invalid
      if (!result.isValid) {
        setValidationResult(prev => ({
          ...prev,
          errors: [...prev.errors, ...result.errors],
          warnings: [...prev.warnings, ...result.warnings],
        }));
      }
    },
    [nodes, edges]
  );

  const clearValidation = useCallback(() => {
    setValidationResult({
      isValid: false,
      errors: [],
      warnings: [],
    });
  }, []);

  // Auto-validate when nodes or edges change
  useEffect(() => {
    validate();
  }, [nodes, edges, validate]);

  return {
    validationResult,
    validate,
    validateNode,
    validateEdge,
    clearValidation,
    isValid: validationResult.isValid,
    errors: validationResult.errors,
    warnings: validationResult.warnings,
  };
};
