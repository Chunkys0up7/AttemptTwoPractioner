import { Node, Edge, AIComponent } from '../../types/workflow';
import { 
  WorkflowValidationResult,
  WorkflowExecutionResult,
  WorkflowError,
  WorkflowErrorType,
} from '../../types/errors';

export const mockNode: Node = {
  id: 'node1',
  type: 'start',
  data: {
    label: 'Start Node',
    componentId: 'component1',
    config: {
      prop1: 'value1',
      prop2: true,
    },
  },
  position: { x: 0, y: 0 },
};

export const mockEdge: Edge = {
  id: 'edge1',
  source: 'node1',
  target: 'node2',
  data: {
    label: 'Connection',
    metadata: {
      type: 'data',
      weight: 1,
    },
  },
};

export const mockComponent: AIComponent = {
  id: 'component1',
  name: 'Start Component',
  type: 'start',
  inputs: {
    input1: {
      type: 'string',
      required: true,
    },
  },
  outputs: {
    output1: {
      type: 'string',
    },
  },
  configSchema: {
    properties: {
      prop1: {
        type: 'string',
        default: 'default1',
      },
      prop2: {
        type: 'boolean',
        default: true,
      },
    },
  },
};

export const mockWorkflow: { nodes: Node[]; edges: Edge[] } = {
  nodes: [
    { ...mockNode },
    { ...mockNode, id: 'node2', type: 'process', position: { x: 200, y: 0 } },
  ],
  edges: [mockEdge],
};

export const mockWorkflowValidationResult: WorkflowValidationResult = {
  isValid: true,
  errors: [],
  warnings: [],
};

export const mockWorkflowExecutionResult: WorkflowExecutionResult = {
  success: true,
  output: {
    node1: {
      output1: 'result1',
    },
    node2: {
      output1: 'result2',
    },
  },
  errors: {},
  warnings: {},
  metadata: {
    executionTime: 100,
    nodeCount: 2,
    edgeCount: 1,
  },
};

export const mockWorkflowError: WorkflowError = {
  id: 'error1',
  type: WorkflowErrorType.EXECUTION,
  message: 'Execution failed',
  details: new Error('Test error'),
  timestamp: new Date(),
  componentId: 'component1',
  nodeId: 'node1',
  edgeId: 'edge1',
  retryCount: 0,
  isFatal: false,
  stack: '',
};

export const createMockWorkflow = (nodes: number = 2, edges: number = 1) => {
  const workflowNodes = Array.from({ length: nodes }, (_, i) => ({
    id: `node${i + 1}`,
    type: i === 0 ? 'start' : 'process',
    data: {
      label: `Node ${i + 1}`,
      componentId: `component${i + 1}`,
      config: {},
    },
    position: { x: i * 200, y: 0 },
  }));

  const workflowEdges = Array.from({ length: edges }, (_, i) => ({
    id: `edge${i + 1}`,
    source: `node${i + 1}`,
    target: `node${i + 2}`,
    data: {
      label: `Connection ${i + 1}`,
      metadata: {},
    },
  }));

  return { nodes: workflowNodes, edges: workflowEdges };
};
