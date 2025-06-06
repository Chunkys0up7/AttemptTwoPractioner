import React, { Component } from 'react';
import { ErrorBoundaryProps, ErrorBoundaryState } from '../../types/error';

/**
 * Error boundary for workflow components
 * @param props - ErrorBoundaryProps
 * @returns Error boundary component
 */
class WorkflowErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  static defaultProps = {
    retryDelay: 3000,
    maxRetries: 3,
  };

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, retryCount: 0 };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error, retryCount: 0 };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Workflow error:', error, errorInfo);
    // Log error to error tracking service
    if (this.props.onError) {
      this.props.onError(error);
    }
  }

  retry = () => {
    const { retryCount } = this.state;
    const { maxRetries } = this.props;

    if (retryCount < maxRetries) {
      this.setState({ hasError: false, retryCount: retryCount + 1 });
    } else {
      // Handle max retries reached
      if (this.props.onMaxRetries) {
        this.props.onMaxRetries();
      }
    }
  };

  render() {
    const { hasError, error, retryCount } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      return (
        <div className="error-boundary">
          <div className="error-content">
            <h2>Something went wrong</h2>
            <p>{error?.message || 'An unexpected error occurred'}</p>
            <p>Retry attempt: {retryCount + 1}</p>
            <button onClick={this.retry} className="retry-button">
              Retry
            </button>
            {fallback && fallback(error)}
          </div>
        </div>
      );
    }

    return children;
  }
}

export default WorkflowErrorBoundary;
