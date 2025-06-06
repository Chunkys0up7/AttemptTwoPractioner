import { renderHook, act } from '@testing-library/react-hooks';
import { useAccessibility } from '../../hooks/useAccessibility';
import { AccessibilityState, KeyboardMode, PanelType } from '../../types/accessibility';

export const mockNodes = [
  { id: 'node1', type: 'start', position: { x: 0, y: 0 } },
  { id: 'node2', type: 'process', position: { x: 200, y: 0 } },
];

export const mockEdges = [
  { id: 'edge1', source: 'node1', target: 'node2' },
];

export const mockWorkflowState = {
  nodes: mockNodes,
  edges: mockEdges,
  selectedNode: mockNodes[0],
  selectedEdge: null,
};

export const mockAccessibilityState: AccessibilityState = {
  isKeyboardNavigation: false,
  isScreenReaderActive: false,
  currentFocus: null,
  previousFocus: null,
  keyboardMode: KeyboardMode.NAVIGATION,
  selectedNode: mockNodes[0].id,
  selectedEdge: null,
  activePanel: null,
};

export const renderUseAccessibility = () => {
  return renderHook(() => useAccessibility());
};

export const simulateKeyboardEvent = (key: string) => {
  const event = new KeyboardEvent('keydown', { key });
  act(() => {
    window.dispatchEvent(event);
  });
};

export const simulateScreenReaderDetection = () => {
  act(() => {
    window.sr = true;
  });
};

export const testKeyboardNavigation = (
  hookResult: ReturnType<typeof renderUseAccessibility>,
  direction: 'up' | 'down' | 'left' | 'right'
) => {
  const { result } = hookResult;
  const { navigation } = result.current;

  act(() => {
    navigation.moveFocus(direction as any);
  });

  return result.current;
};
