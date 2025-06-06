import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AccessibilityProvider } from '../AccessibilityProvider';
import { mockAccessibilityState } from '../../../test/utils/accessibility.testUtils';
import { AccessibilityContext } from '../AccessibilityProvider';

// Mock window.sr for screen reader detection
window.sr = undefined;

describe('AccessibilityProvider', () => {
  it('should render children', () => {
    const { getByText } = render(
      <AccessibilityProvider>
        <div>Test Content</div>
      </AccessibilityProvider>
    );
    expect(getByText('Test Content')).toBeInTheDocument();
  });

  it('should provide default context value', () => {
    const TestComponent = () => {
      const context = React.useContext(AccessibilityContext);
      return <div>{JSON.stringify(context.state)}</div>;
    };

    const { getByText } = render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>
    );

    expect(getByText(JSON.stringify(mockAccessibilityState))).toBeInTheDocument();
  });

  it('should detect screen reader', () => {
    const TestComponent = () => {
      const context = React.useContext(AccessibilityContext);
      return <div>{context.state.isScreenReaderActive ? 'Active' : 'Inactive'}</div>;
    };

    const { getByText } = render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>
    );

    expect(getByText('Inactive')).toBeInTheDocument();

    // Simulate screen reader detection
    window.sr = true;
    fireEvent.change(screen.getByText('Inactive'));
    expect(getByText('Active')).toBeInTheDocument();
  });

  it('should handle keyboard navigation', () => {
    const TestComponent = () => {
      const context = React.useContext(AccessibilityContext);
      const handleKeyDown = (event: React.KeyboardEvent) => {
        if (event.key === 'Tab') {
          context.navigation.toggleKeyboardMode();
        }
      };

      return (
        <div onKeyDown={handleKeyDown}>
          {context.state.keyboardMode}
        </div>
      );
    };

    const { getByText } = render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>
    );

    const element = getByText('NAVIGATION');
    fireEvent.keyDown(element, { key: 'Tab' });
    expect(getByText('SELECTION')).toBeInTheDocument();

    fireEvent.keyDown(element, { key: 'Tab' });
    expect(getByText('NAVIGATION')).toBeInTheDocument();
  });

  it('should handle panel activation', () => {
    const TestComponent = () => {
      const context = React.useContext(AccessibilityContext);
      const activatePanel = () => {
        context.navigation.activatePanel('NODE_PALETTE');
      };

      return (
        <div>
          <button onClick={activatePanel}>Activate Panel</button>
          {context.state.activePanel}
        </div>
      );
    };

    const { getByText } = render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>
    );

    const button = getByText('Activate Panel');
    fireEvent.click(button);
    expect(getByText('NODE_PALETTE')).toBeInTheDocument();
  });

  it('should handle focus management', () => {
    const TestComponent = () => {
      const context = React.useContext(AccessibilityContext);
      const focusNode = () => {
        context.focus.focusNode('node1');
      };

      return (
        <div>
          <button onClick={focusNode}>Focus Node</button>
          {context.state.currentFocus}
        </div>
      );
    };

    const { getByText } = render(
      <AccessibilityProvider>
        <TestComponent />
      </AccessibilityProvider>
    );

    const button = getByText('Focus Node');
    fireEvent.click(button);
    expect(getByText('node-node1')).toBeInTheDocument();
  });
});
