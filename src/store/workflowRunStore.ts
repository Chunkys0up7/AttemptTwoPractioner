import { create } from 'zustand';
import { WorkflowRun } from '../../types';

interface WorkflowRunStoreState {
  runs: WorkflowRun[];
  addRun: (run: WorkflowRun) => void;
  updateRun: (id: string, updates: Partial<WorkflowRun>) => void;
  deleteRun: (id: string) => void;
  setRuns: (runs: WorkflowRun[]) => void;
  bulkUpdateRuns: (updates: Partial<WorkflowRun>[]) => void;
  getRunById: (id: string) => WorkflowRun | undefined;
}

export const useWorkflowRunStore = create<WorkflowRunStoreState>((set: any, get: any) => ({
  runs: [],
  addRun: (run: WorkflowRun) => set((state: WorkflowRunStoreState) => ({ runs: [...state.runs, run] })),
  updateRun: (id: string, updates: Partial<WorkflowRun>) => set((state: WorkflowRunStoreState) => ({
    runs: state.runs.map((r) => r.id === id ? { ...r, ...updates } : r),
  })),
  deleteRun: (id: string) => set((state: WorkflowRunStoreState) => ({
    runs: state.runs.filter((r) => r.id !== id),
  })),
  setRuns: (runs: WorkflowRun[]) => set({ runs }),
  bulkUpdateRuns: (updates: Partial<WorkflowRun>[]) => set((state: WorkflowRunStoreState) => ({
    runs: state.runs.map((r) => {
      const update = updates.find(u => u.id === r.id);
      return update ? { ...r, ...update } : r;
    }),
  })),
  getRunById: (id: string) => get().runs.find((r: WorkflowRun) => r.id === id),
})); 