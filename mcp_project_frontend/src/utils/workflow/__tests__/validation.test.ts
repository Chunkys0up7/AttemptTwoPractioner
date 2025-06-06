import { WorkflowValidator } from '../validation';
import { 
  mockNode,
  mockEdge,
  mockComponent,
  mockWorkflow,
  mockWorkflowValidationResult,
  mockWorkflowError,
} from '../../../test/utils/workflow.testUtils';

// Mock console.error
describe('WorkflowValidator', () => {
  let originalConsoleError: typeof console.error;

  beforeEach(() => {
    originalConsoleError = console.error;
    console.error = jest.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  describe('validateWorkflow', () => {
    it('should validate valid workflow', () => {
      const result = WorkflowValidator.validateWorkflow(
        mockWorkflow.nodes,
        mockWorkflow.edges,
        [mockComponent]
      );
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should detect missing start node', () => {
      const { nodes, edges } = mockWorkflow;
      const result = WorkflowValidator.validateWorkflow(
        nodes.filter(n => n.type !== 'start'),
        edges,
        [mockComponent]
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('No start node found');
    });

    it('should detect invalid edges', () => {
      const { nodes } = mockWorkflow;
      const invalidEdge = { ...mockEdge, source: 'nonexistent' };
      const result = WorkflowValidator.validateWorkflow(
        nodes,
        [invalidEdge],
        [mockComponent]
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Source node not found');
    });

    it('should detect cycles', () => {
      const { nodes } = mockWorkflow;
      const cycleEdge = { ...mockEdge, source: 'node2', target: 'node1' };
      const result = WorkflowValidator.validateWorkflow(
        nodes,
        [mockEdge, cycleEdge],
        [mockComponent]
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Cycle detected');
    });

    it('should validate node configuration', () => {
      const { nodes, edges } = mockWorkflow;
      const invalidNode = { ...mockNode, data: { config: { invalidProp: true } } };
      const result = WorkflowValidator.validateWorkflow(
        [invalidNode],
        edges,
        [mockComponent]
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Invalid configuration');
    });
  });

  describe('validateNodes', () => {
    it('should validate valid nodes', () => {
      const result = WorkflowValidator.validateNodes(
        mockWorkflow.nodes,
        [mockComponent],
        [],
        []
      );
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should detect duplicate nodes', () => {
      const result = WorkflowValidator.validateNodes(
        [mockNode, mockNode],
        [mockComponent],
        [],
        []
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Duplicate node ID');
    });

    it('should validate node types', () => {
      const invalidNode = { ...mockNode, type: 'invalid' };
      const result = WorkflowValidator.validateNodes(
        [invalidNode],
        [mockComponent],
        [],
        []
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Invalid node type');
    });
  });

  describe('validateEdges', () => {
    it('should validate valid edges', () => {
      const result = WorkflowValidator.validateEdges(
        mockWorkflow.nodes,
        mockWorkflow.edges,
        [],
        []
      );
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should detect orphaned edges', () => {
      const invalidEdge = { ...mockEdge, source: 'nonexistent' };
      const result = WorkflowValidator.validateEdges(
        mockWorkflow.nodes,
        [invalidEdge],
        [],
        []
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Source node not found');
    });

    it('should validate edge direction', () => {
      const invalidEdge = { ...mockEdge, target: 'node1' };
      const result = WorkflowValidator.validateEdges(
        mockWorkflow.nodes,
        [invalidEdge],
        [],
        []
      );
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Invalid edge direction');
    });
  });
});
