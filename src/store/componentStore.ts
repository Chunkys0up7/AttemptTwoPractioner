import { create } from 'zustand';
import { AIComponent } from '../../types';

interface ComponentStoreState {
  components: AIComponent[];
  addComponent: (component: AIComponent) => void;
  updateComponent: (id: string, updates: Partial<AIComponent>) => void;
  deleteComponent: (id: string) => void;
  getComponentById: (id: string) => AIComponent | undefined;
  setComponents: (components: AIComponent[]) => void;
}

export const useComponentStore = create<ComponentStoreState>((set: any, get: any) => ({
  components: [],
  addComponent: (component: AIComponent) => set((state: ComponentStoreState) => ({ components: [...state.components, component] })),
  updateComponent: (id: string, updates: Partial<AIComponent>) => set((state: ComponentStoreState) => ({
    components: state.components.map((c) => c.id === id ? { ...c, ...updates } : c),
  })),
  deleteComponent: (id: string) => set((state: ComponentStoreState) => ({
    components: state.components.filter((c) => c.id !== id),
  })),
  getComponentById: (id: string) => get().components.find((c: AIComponent) => c.id === id),
  setComponents: (components: AIComponent[]) => set({ components }),
})); 