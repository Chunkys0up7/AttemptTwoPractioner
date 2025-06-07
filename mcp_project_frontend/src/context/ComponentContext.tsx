import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { AIComponent, SpecificComponentType, AIComponentCostTier } from '../types/index';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface ComponentCache {
  timestamp: number;
  data: AIComponent[];
};

export interface ComponentContextType {
  components: AIComponent[];
  selectedComponent: AIComponent | null;
  loading: boolean;
  error: string | null;
  hasError: boolean;
  isFetching: boolean;
  isCached: boolean;
  fetchComponents: () => Promise<void>;
  selectComponent: (component: AIComponent) => void;
  clearSelection: () => void;
  refreshComponents: () => Promise<void>;
  filterComponents: (searchTerm: string, types?: SpecificComponentType[]) => AIComponent[];
  sortComponents: (field: keyof AIComponent, direction: 'asc' | 'desc') => void;
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
  const [isFetching, setIsFetching] = useState(false);
  const [isCached, setIsCached] = useState(false);
  const [cache, setCache] = useState<ComponentCache | null>(null);
  const [sortField, setSortField] = useState<keyof AIComponent>('name');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const fetchComponents = async () => {
    try {
      setIsFetching(true);
      setError(null);
      
      // Check cache first
      const now = Date.now();
      if (cache && now - cache.timestamp < 5 * 60 * 1000) { // 5 minutes cache
        setComponents(cache.data);
        setIsCached(true);
        return;
      }

      const response = await axios.get<AIComponent[]>(`${API_BASE_URL}/components`);
      const fetchedComponents = response.data;
      
      // Sort components based on current sort field
      const sortedComponents = [...fetchedComponents].sort((a, b) => {
        const aValue = a[sortField];
        const bValue = b[sortField];
        if (aValue === bValue) return 0;
        if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
        return sortDirection === 'asc' ? 1 : -1;
      });

      setComponents(sortedComponents);
      setIsCached(false);
      setCache({ timestamp: now, data: sortedComponents });
    } catch (err) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'Failed to fetch components';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsFetching(false);
    }
  };

  const refreshComponents = async () => {
    setCache(null);
    setIsCached(false);
    return fetchComponents();
  };

  const filterComponents = (searchTerm: string, types?: SpecificComponentType[]): AIComponent[] => {
    return components.filter(component => {
      const matchesSearch = component.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        component.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (component.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())) ?? false);
      
      const matchesType = types ? types.includes(component.type) : true;
      
      return matchesSearch && matchesType;
    });
  };

  const sortComponents = (field: keyof AIComponent, direction: 'asc' | 'desc') => {
    setSortField(field);
    setSortDirection(direction);
    const sortedComponents = [...components].sort((a, b) => {
      const aValue = a[field];
      const bValue = b[field];
      if (aValue === bValue) return 0;
      if (aValue < bValue) return direction === 'asc' ? -1 : 1;
      return direction === 'asc' ? 1 : -1;
    });
    setComponents(sortedComponents);
  };

  const selectComponent = (component: AIComponent) => {
    setSelectedComponent(component);
  };

  const clearSelection = () => {
    setSelectedComponent(null);
  };

  const value: ComponentContextType = {
    components,
    selectedComponent,
    loading,
    error,
    fetchComponents,
    selectComponent,
    clearSelection
  };

  return (
    <ComponentContext.Provider value={value}>
      {children}
    </ComponentContext.Provider>
  );
};

export const useComponents = () => {
  const context = React.useContext(ComponentContext);
  if (!context) {
    throw new Error('useComponents must be used within a ComponentProvider');
  }
  return context;
};
