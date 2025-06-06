import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary } from '../ErrorBoundary';
import { 
  mockError,
  mockErrorBoundaryProps,
  mockWorkflowError,
} from '../../../test/utils/error.testUtils';

// Mock window.sr for screen reader detection
window.sr = undefined;

describe('ErrorBoundary', () => {
  let originalConsoleError: typeof console.error;

  beforeEach(() => {
    originalConsoleError = console.error;
    console.error = jest.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  it('should render children when no error', () => {
    const { getByText } = render(
      <ErrorBoundary {...mockErrorBoundaryProps}>
        <div>Test Content</div>
      </ErrorBoundary>
    );
    expect(getByText('Test Content')).toBeInTheDocument();
  });

  it('should catch and render error', () => {
    const TestComponent = () => {
      throw mockError;
      return <div>Should not render</div>;
    };

    const { getByText } = render(
      <ErrorBoundary {...mockErrorBoundaryProps}>
        <TestComponent />
      </ErrorBoundary>
    );

    expect(getByText('Something went wrong')).toBeInTheDocument();
    expect(getByText('Please try again later.')).toBeInTheDocument();
  });

  it('should handle retry', () => {
    const TestComponent = () => {
      throw mockError;
      return <div>Should not render</div>;
    };

    const { getByText } = render(
      <ErrorBoundary {...mockErrorBoundaryProps}>
        <TestComponent />
      </ErrorBoundary>
    );

    const retryButton = screen.getByText(/Retry/);
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(mockErrorBoundaryProps.onReset).toHaveBeenCalled();
  });

  it('should handle max retries', () => {
    const TestComponent = () => {
      throw mockError;
      return <div>Should not render</div>;
    };

    const { getByText } = render(
      <ErrorBoundary {...mockErrorBoundaryProps}>
        <TestComponent />
      </ErrorBoundary>
    );

    const retryButton = screen.getByText(/Retry/);
    fireEvent.click(retryButton);
    fireEvent.click(retryButton);
    fireEvent.click(retryButton);

    expect(mockErrorBoundaryProps.onMaxRetries).toHaveBeenCalled();
  });

  it('should call onError', () => {
    const TestComponent = () => {
      throw mockError;
      return <div>Should not render</div>;
    };

    render(
      <ErrorBoundary {...mockErrorBoundaryProps}>
        <TestComponent />
      </ErrorBoundary>
    );

    expect(mockErrorBoundaryProps.onError).toHaveBeenCalledWith(mockError);
  });

  it('should handle custom fallback', () => {
    const customFallback = (props: { error: Error }) => (
      <div>Error: {props.error.message}</div>
    );

    const TestComponent = () => {
      throw mockError;
      return <div>Should not render</div>;
    };

    const { getByText } = render(
      <ErrorBoundary {...mockErrorBoundaryProps} fallback={customFallback}>
        <TestComponent />
      </ErrorBoundary>
    );

    expect(getByText(`Error: ${mockError.message}`)).toBeInTheDocument();
  });
});
