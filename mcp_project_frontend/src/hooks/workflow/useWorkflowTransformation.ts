import { useState, useCallback, useEffect } from 'react';
import { Node, Edge } from '../../types/workflow';

/**
 * Custom hook for workflow transformation
 * @param nodes - Array of workflow nodes
 * @param edges - Array of workflow edges
 * @returns Transformation state and transformation methods
 */
export const useWorkflowTransformation = (nodes: Node[], edges: Edge[]) => {
  const [transformedNodes, setTransformedNodes] = useState<Node[]>(nodes);
  const [transformedEdges, setTransformedEdges] = useState<Edge[]>(edges);
  const [hierarchy, setHierarchy] = useState<any[]>([]);
  const [metadata, setMetadata] = useState<Record<string, any>>({});

  const transform = useCallback(() => {
    const { nodes: transformed, edges: transformedEdges } = 
      WorkflowTransformer.transform(nodes, edges);
    
    setTransformedNodes(transformed);
    setTransformedEdges(transformedEdges);
    return { nodes: transformed, edges: transformedEdges };
  }, [nodes, edges]);

  const toHierarchy = useCallback(() => {
    const hierarchy = WorkflowTransformer.toHierarchy(nodes, edges);
    setHierarchy(hierarchy);
    return hierarchy;
  }, [nodes, edges]);

  const fromHierarchy = useCallback(
    (hierarchy: any[]) => {
      const { nodes, edges } = WorkflowTransformer.fromHierarchy(hierarchy);
      setTransformedNodes(nodes);
      setTransformedEdges(edges);
      return { nodes, edges };
    },
    []
  );

  const generateMetadata = useCallback(() => {
    const metadata = WorkflowTransformer.generateMetadata(nodes, edges);
    setMetadata(metadata);
    return metadata;
  }, [nodes, edges]);

  const optimize = useCallback(() => {
    const optimizedNodes = WorkflowTransformer.optimizeNodes(nodes);
    const optimizedEdges = WorkflowTransformer.optimizeEdges(edges);
    setTransformedNodes(optimizedNodes);
    setTransformedEdges(optimizedEdges);
    return { nodes: optimizedNodes, edges: optimizedEdges };
  }, [nodes, edges]);

  // Auto-transform when nodes or edges change
  useEffect(() => {
    transform();
  }, [nodes, edges, transform]);

  return {
    transformedNodes,
    transformedEdges,
    hierarchy,
    metadata,
    transform,
    toHierarchy,
    fromHierarchy,
    generateMetadata,
    optimize,
  };
};
