import React, { createContext, useState, ReactNode } from 'react';
import { AIComponent, SpecificComponentType, AIComponentCostTier } from '../types';

export interface ComponentContextType {
  components: AIComponent[];
  selectedComponent: AIComponent | null;
  loading: boolean;
  error: string | null;
  fetchComponents: () => Promise<void>;
  selectComponent: (component: AIComponent) => void;
  clearSelection: () => void;
}

export const ComponentContext = createContext<ComponentContextType | undefined>(undefined);

interface ComponentProviderProps {
  children: ReactNode;
}

export const ComponentProvider: React.FC<ComponentProviderProps> = ({ children }) => {
  const [components, setComponents] = useState<AIComponent[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<AIComponent | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComponents = async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Implement actual API call to fetch components
      const mockComponents: AIComponent[] = [
        {
          id: '1',
          name: 'Example Component',
          description: 'A sample AI component',
          type: SpecificComponentType.Python,
          typeSpecificData: { python: { requirements: [] } },
          costTier: AIComponentCostTier.Low,
          visibility: 'public',
          tags: ['example', 'demo'],
          createdAt: new Date(),
          updatedAt: new Date(),
          inputs: {
            input1: { type: 'string', description: 'Input parameter 1' }
          },
          outputs: {
            output1: { type: 'string', description: 'Output result' }
          },
          configSchema: {
            parameter1: {
              type: 'string',
              description: 'Configuration parameter 1'
            }
          }
        }
      ];
      setComponents(mockComponents);
    } catch (err) {
      setError('Failed to fetch components');
    } finally {
      setLoading(false);
    }
  };

  const selectComponent = (component: AIComponent) => {
    setSelectedComponent(component);
  };

  const clearSelection = () => {
    setSelectedComponent(null);
  };

  return (
    <ComponentContext.Provider value={{
      components,
      selectedComponent,
      loading,
      error,
      fetchComponents,
      selectComponent,
      clearSelection
    }}>
      {children}
    </ComponentContext.Provider>
  );
};
