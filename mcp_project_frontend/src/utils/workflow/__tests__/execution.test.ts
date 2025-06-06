import { WorkflowExecutor } from '../execution';
import { 
  mockNode,
  mockEdge,
  mockComponent,
  mockWorkflow,
  mockWorkflowValidationResult,
  mockWorkflowExecutionResult,
} from '../../../test/utils/workflow.testUtils';

// Mock console.error
describe('WorkflowExecutor', () => {
  let originalConsoleError: typeof console.error;

  beforeEach(() => {
    originalConsoleError = console.error;
    console.error = jest.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  describe('execute', () => {
    it('should execute workflow', async () => {
      const { nodes, edges } = mockWorkflow;
      const result = await WorkflowExecutor.execute(nodes, edges, {
        components: [mockComponent],
      });

      expect(result.success).toBe(true);
      expect(result.output).toHaveProperty('node1');
      expect(result.output).toHaveProperty('node2');
    });

    it('should handle parallel execution', async () => {
      const { nodes, edges } = mockWorkflow;
      const result = await WorkflowExecutor.execute(nodes, edges, {
        components: [mockComponent],
        parallel: true,
      });

      expect(result.success).toBe(true);
      expect(result.metadata).toHaveProperty('parallelExecution');
    });

    it('should handle timeouts', async () => {
      const { nodes, edges } = mockWorkflow;
      const result = await WorkflowExecutor.execute(nodes, edges, {
        components: [mockComponent],
        timeout: 1, // 1ms timeout
      });

      expect(result.success).toBe(false);
      expect(result.errors).toHaveProperty('node1');
      expect(result.errors['node1']).toContain('Timeout');
    });

    it('should handle retries', async () => {
      const { nodes, edges } = mockWorkflow;
      const result = await WorkflowExecutor.execute(nodes, edges, {
        components: [mockComponent],
        retry: 2,
      });

      expect(result.success).toBe(true);
      expect(result.metadata).toHaveProperty('retryCount');
    });
  });

  describe('executeComponent', () => {
    it('should execute component', async () => {
      const result = await WorkflowExecutor.executeComponent(
        mockComponent,
        {},
        {},
        {}
      );

      expect(result.success).toBe(true);
      expect(result.output).toBeDefined();
    });

    it('should handle component errors', async () => {
      const errorComponent = { ...mockComponent, execute: () => { throw new Error('Test'); } };
      const result = await WorkflowExecutor.executeComponent(
        errorComponent,
        {},
        {},
        {}
      );

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
    });

    it('should handle retries', async () => {
      const errorComponent = {
        ...mockComponent,
        execute: (inputs, config, context) => {
          if (context.retryCount < 2) {
            throw new Error('Test');
          }
          return { output1: 'result' };
        },
      };

      const result = await WorkflowExecutor.executeComponent(
        errorComponent,
        {},
        {},
        { retry: 3 }
      );

      expect(result.success).toBe(true);
      expect(result.output).toBeDefined();
    });
  });

  describe('getInputs', () => {
    it('should get component inputs', () => {
      const inputs = WorkflowTransformer.getInputs(
        mockNode,
        {},
        new Map()
      );

      expect(inputs).toBeDefined();
      expect(inputs).toHaveProperty('input1');
    });

    it('should handle default values', () => {
      const inputs = WorkflowTransformer.getInputs(
        { ...mockNode, data: { config: {} } },
        {},
        new Map()
      );

      expect(inputs).toBeDefined();
      expect(inputs).toHaveProperty('input1');
      expect(inputs.input1).toBe('default1');
    });
  });

  describe('getOutputs', () => {
    it('should get component outputs', () => {
      const outputs = WorkflowTransformer.getOutputs(
        mockNode,
        { output1: 'result' },
        new Map()
      );

      expect(outputs).toBeDefined();
      expect(outputs).toHaveProperty('output1');
    });

    it('should handle missing outputs', () => {
      const outputs = WorkflowTransformer.getOutputs(
        mockNode,
        {},
        new Map()
      );

      expect(outputs).toBeDefined();
      expect(outputs).toHaveProperty('output1');
      expect(outputs.output1).toBeUndefined();
    });
  });
});
