import React, { useState, useCallback, useEffect } from 'react';
import { 
  AccessibilityContextType, 
  AccessibilityProviderProps, 
  AccessibilityProviderState, 
  KeyboardNavigation, 
  FocusManager,
  AccessibilityState,
  KeyboardMode,
  PanelType,
  Direction,
} from '../../types/accessibility';

/**
 * Accessibility context provider
 * @param props - AccessibilityProviderProps
 * @returns Accessibility context provider component
 */
export const AccessibilityContext = React.createContext<AccessibilityContextType>({
  state: {
    isKeyboardNavigation: false,
    isScreenReaderActive: false,
    currentFocus: null,
    previousFocus: null,
    keyboardMode: KeyboardMode.NAVIGATION,
    selectedNode: null,
    selectedEdge: null,
    activePanel: null,
  },
  navigation: {
    moveFocus: () => {},
    selectNode: () => {},
    selectEdge: () => {},
    activatePanel: () => {},
    toggleKeyboardMode: () => {},
    resetNavigation: () => {},
  },
  focus: {
    focusNode: () => {},
    focusEdge: () => {},
    focusPanel: () => {},
    clearFocus: () => {},
    getFocusableElements: () => [],
  },
  setIsKeyboardNavigation: () => {},
  setIsScreenReaderActive: () => {},
  setKeyboardMode: () => {},
  setActivePanel: () => {},
});

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children, initialState }) => {
  const [state, setState] = useState<AccessibilityState>({
    isKeyboardNavigation: false,
    isScreenReaderActive: false,
    currentFocus: null,
    previousFocus: null,
    keyboardMode: KeyboardMode.NAVIGATION,
    selectedNode: null,
    selectedEdge: null,
    activePanel: null,
    ...initialState,
  });

  const keyboardNavigation: KeyboardNavigation = {
    moveFocus: useCallback((direction: Direction) => {
      // Implement focus movement logic based on direction
      // This would typically involve finding the next/previous focusable element
      // and updating the currentFocus state
    }, []),

    selectNode: useCallback((nodeId: string) => {
      setState(prev => ({
        ...prev,
        selectedNode: nodeId,
        selectedEdge: null,
        currentFocus: `node-${nodeId}`,
      }));
    }, []),

    selectEdge: useCallback((edgeId: string) => {
      setState(prev => ({
        ...prev,
        selectedEdge: edgeId,
        selectedNode: null,
        currentFocus: `edge-${edgeId}`,
      }));
    }, []),

    activatePanel: useCallback((panel: PanelType) => {
      setState(prev => ({
        ...prev,
        activePanel: panel,
        currentFocus: `panel-${panel}`,
      }));
    }, []),

    toggleKeyboardMode: useCallback(() => {
      setState(prev => ({
        ...prev,
        keyboardMode: prev.keyboardMode === KeyboardMode.NAVIGATION 
          ? KeyboardMode.SELECTION 
          : KeyboardMode.NAVIGATION,
      }));
    }, []),

    resetNavigation: useCallback(() => {
      setState(prev => ({
        ...prev,
        currentFocus: null,
        selectedNode: null,
        selectedEdge: null,
        activePanel: null,
      }));
    }, []),
  };

  const focusManager: FocusManager = {
    focusNode: useCallback((nodeId: string) => {
      const node = document.querySelector(`[data-node-id="${nodeId}"]`);
      if (node) {
        node.focus();
      }
    }, []),

    focusEdge: useCallback((edgeId: string) => {
      const edge = document.querySelector(`[data-edge-id="${edgeId}"]`);
      if (edge) {
        edge.focus();
      }
    }, []),

    focusPanel: useCallback((panel: PanelType) => {
      const panelElement = document.querySelector(`[data-panel="${panel}"]`);
      if (panelElement) {
        panelElement.focus();
      }
    }, []),

    clearFocus: useCallback(() => {
      setState(prev => ({
        ...prev,
        currentFocus: null,
        previousFocus: null,
      }));
    }, []),

    getFocusableElements: useCallback(() => {
      return Array.from(document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      ));
    }, []),
  };

  const setIsKeyboardNavigation = useCallback((value: boolean) => {
    setState(prev => ({
      ...prev,
      isKeyboardNavigation: value,
    }));
  }, []);

  const setIsScreenReaderActive = useCallback((value: boolean) => {
    setState(prev => ({
      ...prev,
      isScreenReaderActive: value,
    }));
  }, []);

  const setKeyboardMode = useCallback((mode: KeyboardMode) => {
    setState(prev => ({
      ...prev,
      keyboardMode: mode,
    }));
  }, []);

  const setActivePanel = useCallback((panel: PanelType | null) => {
    setState(prev => ({
      ...prev,
      activePanel: panel,
    }));
  }, []);

  useEffect(() => {
    // Detect screen reader
    const detectScreenReader = () => {
      setState(prev => ({
        ...prev,
        isScreenReaderActive: true,
      }));
    };

    // Add screen reader detection script
    const script = document.createElement('script');
    script.textContent = `
      if (typeof window.sr === 'undefined') {
        window.sr = true;
        ${detectScreenReader.toString()}();
      }
    `;
    document.body.appendChild(script);

    // Clean up
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <AccessibilityContext.Provider
      value={{
        state,
        navigation: keyboardNavigation,
        focus: focusManager,
        setIsKeyboardNavigation,
        setIsScreenReaderActive,
        setKeyboardMode,
        setActivePanel,
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
};
