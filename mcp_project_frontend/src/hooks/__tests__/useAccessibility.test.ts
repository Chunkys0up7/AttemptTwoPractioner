import { renderHook, act } from '@testing-library/react-hooks';
import { useAccessibility } from '../useAccessibility';
import { 
  mockAccessibilityState,
  mockWorkflowState,
  renderUseAccessibility,
  simulateKeyboardEvent,
  simulateScreenReaderDetection,
  testKeyboardNavigation,
} from '../../../test/utils/accessibility.testUtils';

// Mock dependencies
document.querySelector = jest.fn();
document.querySelectorAll = jest.fn();

beforeEach(() => {
  jest.clearAllMocks();
});

describe('useAccessibility', () => {
  it('should initialize with default state', () => {
    const { result } = renderUseAccessibility();
    expect(result.current.state).toEqual(mockAccessibilityState);
  });

  it('should detect keyboard navigation', () => {
    const { result } = renderUseAccessibility();
    
    simulateKeyboardEvent('Tab');
    expect(result.current.state.isKeyboardNavigation).toBe(true);

    simulateKeyboardEvent('Tab');
    expect(result.current.state.isKeyboardNavigation).toBe(false);
  });

  it('should detect screen reader', () => {
    const { result } = renderUseAccessibility();
    
    simulateScreenReaderDetection();
    expect(result.current.state.isScreenReaderActive).toBe(true);
  });

  it('should handle keyboard navigation mode', () => {
    const { result } = renderUseAccessibility();
    
    act(() => {
      result.current.setKeyboardMode('SELECTION');
    });
    expect(result.current.state.keyboardMode).toBe('SELECTION');

    act(() => {
      result.current.setKeyboardMode('NAVIGATION');
    });
    expect(result.current.state.keyboardMode).toBe('NAVIGATION');
  });

  it('should handle panel activation', () => {
    const { result } = renderUseAccessibility();
    
    act(() => {
      result.current.setActivePanel('NODE_PALETTE');
    });
    expect(result.current.state.activePanel).toBe('NODE_PALETTE');

    act(() => {
      result.current.setActivePanel(null);
    });
    expect(result.current.state.activePanel).toBeNull();
  });

  it('should handle focus management', () => {
    const { result } = renderUseAccessibility();
    
    act(() => {
      result.current.focus.focusNode('node1');
    });
    expect(document.querySelector).toHaveBeenCalledWith('[data-node-id="node1"]');

    act(() => {
      result.current.focus.focusEdge('edge1');
    });
    expect(document.querySelector).toHaveBeenCalledWith('[data-edge-id="edge1"]');
  });

  it('should handle keyboard navigation', () => {
    const { result } = renderUseAccessibility();
    
    act(() => {
      result.current.navigation.selectNode('node1');
    });
    expect(result.current.state.currentFocus).toBe('node-node1');

    act(() => {
      result.current.navigation.selectEdge('edge1');
    });
    expect(result.current.state.currentFocus).toBe('edge-edge1');
  });

  it('should handle focus clearing', () => {
    const { result } = renderUseAccessibility();
    
    act(() => {
      result.current.focus.clearFocus();
    });
    expect(result.current.state.currentFocus).toBeNull();
    expect(result.current.state.previousFocus).toBeNull();
  });

  it('should handle focusable elements', () => {
    const { result } = renderUseAccessibility();
    
    const elements = result.current.focus.getFocusableElements();
    expect(elements).toHaveLength(0); // No elements in mock document
  });
});
