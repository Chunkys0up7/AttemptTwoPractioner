import { Node as ReactFlowNode, Edge as ReactFlowEdge, Connection } from 'reactflow';

/**
 * Types for the workflow builder functionality
 */

// Constraint type for validation rules
export interface Constraint {
  type?: string;
  min?: number;
  max?: number;
  enum?: string[];
}

// Core Workflow Types
export enum NodeType {
  START = 'start',
  END = 'end',
  ACTION = 'action',
  DECISION = 'decision',
  DATA = 'data',
  CUSTOM = 'custom'
}

export enum EdgeType {
  DEFAULT = 'default',
  SUCCESS = 'success',
  FAILURE = 'failure',
  CONDITIONAL = 'conditional'
}

export interface WorkflowNode extends ReactFlowNode {
  type: NodeType;
  data: {
    config: Record<string, any>;
    state: Record<string, any>;
    metadata: Record<string, any>;
    validation: {
      isValid: boolean;
      errors: string[];
    };
    performance: {
      executionTime: number;
      memoryUsage: number;
    };
  };
}

export interface WorkflowEdge extends ReactFlowEdge {
  type: EdgeType;
  data: {
    metadata: Record<string, any>;
    validation: {
      isValid: boolean;
      errors: string[];
    };
    conditions: Record<string, any>;
  };
}

// Workflow State Types
export interface WorkflowState {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  selectedNode: WorkflowNode | null;
  isLoading: boolean;
  error: string | null;
  executionState: {
    current: string | null;
    history: string[];
    status: 'running' | 'completed' | 'failed' | 'idle';
    progress: number;
  };
  validation: {
    isValid: boolean;
    errors: string[];
  };
}

// Workflow Config Types
export interface WorkflowConfig {
  id: string;
  name: string;
  description: string;
  version: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  metadata: Record<string, any>;
  validationRules: {
    node: Record<NodeType, Record<string, any>>;
    edge: Record<EdgeType, Record<string, any>>;
  };
  executionOptions: {
    parallel: boolean;
    timeout: number;
    retry: {
      maxAttempts: number;
      delay: number;
    };
  };
}

// Workflow Execution Types
export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'running' | 'completed' | 'failed' | 'idle';
  startTime: number;
  endTime: number | null;
  duration: number;
  result: any;
  error: string | null;
  metadata: Record<string, any>;
}

// Workflow Validation Types
export interface WorkflowValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  nodeErrors: Record<string, string[]>;
  edgeErrors: Record<string, string[]>;
}

export interface WorkflowTransformationOptions {
  optimize: boolean;
  validate: boolean;
  components: AIComponent[];
  metadata: Record<string, any>;
  errorHandler?: (error: any) => void;
}

export class WorkflowError extends Error {
  constructor(message: string, public details?: any) {
    super(message);
    this.name = 'WorkflowError';
  }
}

// AI Component Types
export interface AIComponent {
  id: string;
  name: string;
  type: string;
  description: string;
  inputs: string[];
  outputs: string[];
  config: Record<string, any>;
  metadata: Record<string, any>;
  validation: {
    rules: {
      required: Record<string, any>;
    };
    constraints: Record<string, Constraint>;
  };
  compatibility: {
    canConnectTo: string[];
  };
}

// Event Types
export interface WorkflowEvent {
  type: 'node' | 'edge' | 'workflow';
  action: 'add' | 'remove' | 'update' | 'execute';
  payload: any;
  timestamp: number;
  metadata: Record<string, any>;
}

// Error Types
export interface WorkflowError {
  code: string;
  message: string;
  type: 'validation' | 'execution' | 'configuration' | 'runtime';
  node: WorkflowNode | null;
  edge: WorkflowEdge | null;
  metadata: Record<string, any>;
}

export interface WorkflowActions {
  /** Handler for node state changes */
  onNodesChange: (nodes: WorkflowNode[]) => void;
  /** Handler for edge state changes */
  onEdgesChange: (edges: WorkflowEdge[]) => void;
  /** Handler for connecting nodes */
  onConnect: (params: WorkflowEdge | Connection) => void;
  /** Handler for dropping components onto the canvas */
  onDrop: (event: React.DragEvent) => void;
  /** Handler for selecting a node */
  setSelectedNode: (node: WorkflowNode | null) => void;
}

export interface WorkflowBuilderProps {
  /** Initial nodes to render */
  initialNodes?: WorkflowNode[];
  /** Custom node change handler */
  onNodesChange?: (nodes: WorkflowNode[]) => void;
  /** Custom edge change handler */
  onEdgesChange?: (edges: WorkflowEdge[]) => void;
  /** Custom node selection handler */
  onNodeSelect?: (node: WorkflowNode | null) => void;
}

export interface WorkflowContextType {
  state: WorkflowState;
  actions: WorkflowActions;
  config: WorkflowConfig;
  saveWorkflow: () => Promise<void>;
  loadWorkflow: (id: string) => Promise<void>;
}

export type Node = {
  /** Unique identifier for the node */
}
