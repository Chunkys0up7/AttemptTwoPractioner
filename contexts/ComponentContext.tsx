import React, { createContext, useState, useEffect, ReactNode, useContext, useCallback, useMemo } from 'react';
import { AIComponent, SpecificComponentType } from '../types';
import { DUMMY_COMPONENTS_PRESET, LOCAL_STORAGE_CUSTOM_COMPONENTS_KEY, getIconForComponentType, DEFAULT_COMPONENT_ICON } from '../constants';

interface ComponentContextType {
  allComponents: AIComponent[];
  addCustomComponent: (componentData: Omit<AIComponent, 'id' | 'icon' | 'isCustom'>) => void;
  getComponentById: (id: string) => AIComponent | undefined;
}

export const ComponentContext = createContext<ComponentContextType | undefined>(undefined);

interface ComponentProviderProps {
  children: ReactNode;
}

/**
 * Provides a context for managing AI components, including both preset and custom components.
 * Custom components are loaded from and saved to localStorage.
 * @param {ComponentProviderProps} props - The provider props.
 * @returns {JSX.Element} The ComponentProvider component.
 */
export const ComponentProvider: React.FC<ComponentProviderProps> = ({ children }) => {
  const [customComponents, setCustomComponents] = useState<AIComponent[]>([]);

  useEffect(() => {
    try {
      const storedComponents = localStorage.getItem(LOCAL_STORAGE_CUSTOM_COMPONENTS_KEY);
      if (storedComponents) {
        const parsedComponents: AIComponent[] = JSON.parse(storedComponents);
        const componentsWithIcons = parsedComponents.map(comp => ({
          ...comp,
          icon: getIconForComponentType(comp.type, { className: "w-8 h-8 text-gray-500" }),
          isCustom: true,
        }));
        setCustomComponents(componentsWithIcons);
      }
    } catch (error) {
      console.error("Failed to load custom components from localStorage:", error);
      setCustomComponents([]); 
    }
  }, []);

  const saveCustomComponents = useCallback((components: AIComponent[]) => {
    try {
      // Strip ReactNode icons before saving to localStorage
      const serializableComponents = components.map(({ icon, ...comp }) => comp);
      localStorage.setItem(LOCAL_STORAGE_CUSTOM_COMPONENTS_KEY, JSON.stringify(serializableComponents));
    } catch (error) {
      console.error("Failed to save custom components to localStorage:", error);
    }
  }, []);
  

  /**
   * Adds a new custom component to the list and saves it to localStorage.
   * @param {Omit<AIComponent, 'id' | 'icon' | 'isCustom'>} componentData - The data for the new component.
   */
  const addCustomComponent = useCallback((componentData: Omit<AIComponent, 'id' | 'icon' | 'isCustom'>) => {
    const newComponent: AIComponent = {
      ...componentData,
      id: `custom-${Date.now().toString(36)}-${Math.random().toString(36).substring(2)}`,
      icon: getIconForComponentType(componentData.type, { className: "w-8 h-8 text-slate-500" }),
      isCustom: true,
    };
    setCustomComponents(prevComponents => {
      const updatedComponents = [...prevComponents, newComponent];
      saveCustomComponents(updatedComponents);
      return updatedComponents;
    });
  }, [saveCustomComponents]);

  const allComponents = useMemo(() => {
    const presetsWithDefaults: AIComponent[] = DUMMY_COMPONENTS_PRESET.map(comp => ({
        ...comp,
        isCustom: false,
        visibility: comp.visibility || 'Public',
        icon: comp.icon || getIconForComponentType(comp.type, { className: "w-8 h-8 text-gray-400" }) || DEFAULT_COMPONENT_ICON,
    }));
    
    // Re-apply icons to custom components as they are not stored in localStorage
    const customComponentsWithIcons = customComponents.map(comp => ({
        ...comp,
        icon: getIconForComponentType(comp.type, { className: "w-8 h-8 text-slate-500" }) || DEFAULT_COMPONENT_ICON,
    }));
    
    return [...presetsWithDefaults, ...customComponentsWithIcons];
  }, [customComponents]);


  /**
   * Retrieves a component by its ID from all available components.
   * @param {string} id - The ID of the component to retrieve.
   * @returns {AIComponent | undefined} The found component or undefined.
   */
  const getComponentById = useCallback((id: string): AIComponent | undefined => {
    return allComponents.find(comp => comp.id === id);
  }, [allComponents]);


  return (
    <ComponentContext.Provider value={{ allComponents, addCustomComponent, getComponentById }}>
      {children}
    </ComponentContext.Provider>
  );
};

/**
 * Custom hook to access the ComponentContext.
 * Throws an error if used outside of a ComponentProvider.
 * @returns {ComponentContextType} The component context.
 */
export const useComponents = (): ComponentContextType => {
  const context = useContext(ComponentContext);
  if (context === undefined) {
    throw new Error('useComponents must be used within a ComponentProvider');
  }
  return context;
};