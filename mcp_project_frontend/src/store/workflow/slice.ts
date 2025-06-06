import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Node, Edge, WorkflowState } from '../../types/workflow';

interface WorkflowState {
  nodes: Node[];
  edges: Edge[];
  selectedNode: Node | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: WorkflowState = {
  nodes: [],
  edges: [],
  selectedNode: null,
  isLoading: false,
  error: null,
};

const workflowSlice = createSlice({
  name: 'workflow',
  initialState,
  reducers: {
    setNodes: (state, action: PayloadAction<Node[]>) => {
      state.nodes = action.payload;
    },
    setEdges: (state, action: PayloadAction<Edge[]>) => {
      state.edges = action.payload;
    },
    setSelectedNode: (state, action: PayloadAction<Node | null>) => {
      state.selectedNode = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    addNode: (state, action: PayloadAction<Node>) => {
      state.nodes.push(action.payload);
    },
    removeNode: (state, action: PayloadAction<string>) => {
      state.nodes = state.nodes.filter((node) => node.id !== action.payload);
    },
    addEdge: (state, action: PayloadAction<Edge>) => {
      state.edges.push(action.payload);
    },
    removeEdge: (state, action: PayloadAction<string>) => {
      state.edges = state.edges.filter((edge) => edge.id !== action.payload);
    },
  },
});

export const {
  setNodes,
  setEdges,
  setSelectedNode,
  setLoading,
  setError,
  addNode,
  removeNode,
  addEdge,
  removeEdge,
} = workflowSlice.actions;

export default workflowSlice.reducer;
