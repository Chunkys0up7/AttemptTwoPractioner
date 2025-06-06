import { useState, useCallback, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  AccessibilityContextType, 
  KeyboardNavigation, 
  FocusManager,
  KeyboardMode,
  PanelType,
} from '../../types/accessibility';
import { useWorkflowBuilder } from '../workflow/useWorkflowBuilder';

/**
 * Custom hook for accessibility features
 * @returns Accessibility state and utilities
 */
export const useAccessibility = (): AccessibilityContextType => {
  const location = useLocation();
  const { nodes, edges, selectedNode, selectedEdge } = useWorkflowBuilder();
  const [isKeyboardNavigation, setIsKeyboardNavigation] = useState(false);
  const [isScreenReaderActive, setIsScreenReaderActive] = useState(false);
  const [currentFocus, setCurrentFocus] = useState<string | null>(null);
  const [previousFocus, setPreviousFocus] = useState<string | null>(null);
  const [keyboardMode, setKeyboardMode] = useState<KeyboardMode>(KeyboardMode.NAVIGATION);
  const [activePanel, setActivePanel] = useState<PanelType | null>(null);

  const keyboardNavigation: KeyboardNavigation = {
    moveFocus: useCallback((direction: Direction) => {
      // Implement focus movement logic based on direction
      // This would typically involve finding the next/previous focusable element
      // and updating the currentFocus state
    }, []),

    selectNode: useCallback((nodeId: string) => {
      setCurrentFocus(`node-${nodeId}`);
    }, []),

    selectEdge: useCallback((edgeId: string) => {
      setCurrentFocus(`edge-${edgeId}`);
    }, []),

    activatePanel: useCallback((panel: PanelType) => {
      setActivePanel(panel);
      setCurrentFocus(`panel-${panel}`);
    }, []),

    toggleKeyboardMode: useCallback(() => {
      setKeyboardMode(prev => 
        prev === KeyboardMode.NAVIGATION ? KeyboardMode.SELECTION : KeyboardMode.NAVIGATION
      );
    }, []),

    resetNavigation: useCallback(() => {
      setCurrentFocus(null);
      setActivePanel(null);
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
      setCurrentFocus(null);
      setPreviousFocus(null);
    }, []),

    getFocusableElements: useCallback(() => {
      return Array.from(document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      ));
    }, []),
  };

  // Handle keyboard navigation mode
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        setIsKeyboardNavigation(true);
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        setIsKeyboardNavigation(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // Handle screen reader detection
  useEffect(() => {
    const detectScreenReader = () => {
      setIsScreenReaderActive(true);
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

  return {
    state: {
      isKeyboardNavigation,
      isScreenReaderActive,
      currentFocus,
      previousFocus,
      keyboardMode,
      selectedNode: selectedNode?.id || null,
      selectedEdge: selectedEdge?.id || null,
      activePanel,
    },
    navigation: keyboardNavigation,
    focus: focusManager,
    setIsKeyboardNavigation,
    setIsScreenReaderActive,
    setKeyboardMode,
    setActivePanel,
  };
};
