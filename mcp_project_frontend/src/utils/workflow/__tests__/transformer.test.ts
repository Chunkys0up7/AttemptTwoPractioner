import { WorkflowTransformer } from '../transformer';
import { 
  mockNode,
  mockEdge,
  mockComponent,
  mockWorkflow,
  mockWorkflowValidationResult,
  mockWorkflowExecutionResult,
} from '../../../test/utils/workflow.testUtils';

// Mock console.error
describe('WorkflowTransformer', () => {
  let originalConsoleError: typeof console.error;

  beforeEach(() => {
    originalConsoleError = console.error;
    console.error = jest.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  describe('transform', () => {
    it('should transform workflow', () => {
      const { nodes, edges } = mockWorkflow;
      const { nodes: transformedNodes, edges: transformedEdges } = 
        WorkflowTransformer.transform(nodes, edges);

      expect(transformedNodes).toHaveLength(nodes.length);
      expect(transformedEdges).toHaveLength(edges.length);
      expect(transformedNodes[0].data).toHaveProperty('metadata');
      expect(transformedEdges[0].data).toHaveProperty('metadata');
    });

    it('should optimize nodes', () => {
      const { nodes } = mockWorkflow;
      const optimizedNodes = WorkflowTransformer.optimizeNodes(nodes);

      expect(optimizedNodes).toHaveLength(nodes.length);
      expect(optimizedNodes[0].data).toHaveProperty('optimized');
    });

    it('should optimize edges', () => {
      const { edges } = mockWorkflow;
      const optimizedEdges = WorkflowTransformer.optimizeEdges(edges);

      expect(optimizedEdges).toHaveLength(edges.length);
      expect(optimizedEdges[0].data).toHaveProperty('optimized');
    });
  });

  describe('toHierarchy', () => {
    it('should convert to hierarchical structure', () => {
      const { nodes, edges } = mockWorkflow;
      const hierarchy = WorkflowTransformer.toHierarchy(nodes, edges);

      expect(hierarchy).toHaveProperty('root');
      expect(hierarchy).toHaveProperty('children');
      expect(hierarchy.children).toHaveLength(1);
    });

    it('should handle complex hierarchies', () => {
      const complexWorkflow = {
        nodes: [
          { ...mockNode, id: 'node1' },
          { ...mockNode, id: 'node2', position: { x: 200, y: 0 } },
          { ...mockNode, id: 'node3', position: { x: 400, y: 0 } },
        ],
        edges: [
          { ...mockEdge, id: 'edge1', source: 'node1', target: 'node2' },
          { ...mockEdge, id: 'edge2', source: 'node2', target: 'node3' },
        ],
      };

      const hierarchy = WorkflowTransformer.toHierarchy(
        complexWorkflow.nodes,
        complexWorkflow.edges
      );

      expect(hierarchy.children[0].children).toHaveLength(1);
      expect(hierarchy.children[0].children[0].children).toHaveLength(1);
    });
  });

  describe('fromHierarchy', () => {
    it('should convert from hierarchical structure', () => {
      const hierarchy = {
        id: 'root',
        children: [
          {
            id: 'node1',
            children: [
              {
                id: 'node2',
                children: [],
              },
            ],
          },
        ],
      };

      const { nodes, edges } = WorkflowTransformer.fromHierarchy(hierarchy);

      expect(nodes).toHaveLength(2);
      expect(edges).toHaveLength(1);
      expect(edges[0].source).toBe('node1');
      expect(edges[0].target).toBe('node2');
    });
  });

  describe('generateMetadata', () => {
    it('should generate workflow metadata', () => {
      const { nodes, edges } = mockWorkflow;
      const metadata = WorkflowTransformer.generateMetadata(nodes, edges);

      expect(metadata).toHaveProperty('nodeCount');
      expect(metadata).toHaveProperty('edgeCount');
      expect(metadata).toHaveProperty('typeCounts');
      expect(metadata).toHaveProperty('complexity');
    });

    it('should calculate complexity', () => {
      const complexWorkflow = {
        nodes: [
          { ...mockNode, id: 'node1' },
          { ...mockNode, id: 'node2', position: { x: 200, y: 0 } },
          { ...mockNode, id: 'node3', position: { x: 400, y: 0 } },
        ],
        edges: [
          { ...mockEdge, id: 'edge1', source: 'node1', target: 'node2' },
          { ...mockEdge, id: 'edge2', source: 'node2', target: 'node3' },
        ],
      };

      const metadata = WorkflowTransformer.generateMetadata(
        complexWorkflow.nodes,
        complexWorkflow.edges
      );

      expect(metadata.complexity).toBeGreaterThan(1);
    });
  });
});
