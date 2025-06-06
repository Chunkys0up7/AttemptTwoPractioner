/**
 * Types for the workflow builder functionality
 */

export interface WorkflowState {
  /** List of nodes in the workflow */
  nodes: Node[];
  /** List of edges connecting nodes */
  edges: Edge[];
  /** Currently selected node in the workflow */
  selectedNode: Node | null;
  /** Instance of ReactFlow for canvas manipulation */
  reactFlowInstance: any;
}

export interface WorkflowActions {
  /** Handler for node state changes */
  onNodesChange: (nodes: Node[]) => void;
  /** Handler for edge state changes */
  onEdgesChange: (edges: Edge[]) => void;
  /** Handler for connecting nodes */
  onConnect: (params: Edge | Connection) => void;
  /** Handler for dropping components onto the canvas */
  onDrop: (event: React.DragEvent) => void;
  /** Handler for selecting a node */
  setSelectedNode: (node: Node | null) => void;
}

export interface WorkflowBuilderProps {
  /** Initial nodes configuration */
  initialNodes?: Node[];
  /** Custom node change handler */
  onNodesChange?: (nodes: Node[]) => void;
  /** Custom edge change handler */
  onEdgesChange?: (edges: Edge[]) => void;
  /** Custom node selection handler */
  onNodeSelect?: (node: Node | null) => void;
}

export interface WorkflowContextType {
  /** Current workflow state */
  state: WorkflowState;
  /** Workflow actions */
  actions: WorkflowActions;
  /** Save workflow function */
  saveWorkflow: () => Promise<void>;
  /** Load workflow function */
  loadWorkflow: (id: string) => Promise<void>;
}

export type Node = {
  /** Unique identifier for the node */
  id: string;
  /** Type of the node */
  type: string;
  /** Position of the node on the canvas */
  position: {
    x: number;
    y: number;
  };
  /** Data associated with the node */
  data: {
    name: string;
    componentId: string;
    config: Record<string, any>;
  };
};

export type Edge = {
  /** Unique identifier for the edge */
  id: string;
  /** Source node and port */
  source: string;
  /** Target node and port */
  target: string;
  /** Source handle */
  sourceHandle?: string;
  /** Target handle */
  targetHandle?: string;
};
