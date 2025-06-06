import React, { Component } from 'react';
import { ErrorBoundaryProps, ErrorBoundaryState, WorkflowErrorType } from '../../types/errors';
import { ErrorLogger } from './ErrorLogger';

/**
 * Error boundary component for workflow components
 * @param props - ErrorBoundaryProps
 * @returns Error boundary component
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  static defaultProps = {
    maxRetries: 3,
    retryDelay: 3000,
    fallback: (
      <div className="error-boundary">
        <h2>Something went wrong</h2>
        <p>Please try again later.</p>
      </div>
    ),
  };

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error, retryCount: 0 };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to error tracking service
    ErrorLogger.logError({
      error,
      metadata: {
        component: this.props.children?.type?.name,
        errorInfo,
      },
      isFatal: true,
      context: 'ErrorBoundary',
    });

    if (this.props.onError) {
      this.props.onError(error);
    }
  }

  retry = () => {
    const { retryCount } = this.state;
    const { maxRetries, onReset } = this.props;

    if (retryCount < maxRetries) {
      this.setState({ hasError: false, retryCount: retryCount + 1 });
      if (onReset) {
        onReset();
      }
    } else {
      if (this.props.onMaxRetries) {
        this.props.onMaxRetries();
      }
    }
  };

  render() {
    const { hasError, error, retryCount } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      const fallbackUI = typeof fallback === 'function' ? fallback({ error }) : fallback;
      return (
        <div className="error-boundary">
          {fallbackUI}
          <div className="retry-container">
            <button onClick={this.retry} className="retry-button">
              Retry ({retryCount + 1}/{this.props.maxRetries})
            </button>
          </div>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;
