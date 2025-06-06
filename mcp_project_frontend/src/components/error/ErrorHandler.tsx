import React from 'react';
import { ErrorHandlerProps, WorkflowErrorType } from '../../types/errors';

/**
 * Error handler component
 * @param props - ErrorHandlerProps
 * @returns Error handler component
 */
export const ErrorHandler: React.FC<ErrorHandlerProps> = (props) => {
  const {
    error,
    type,
    componentId,
    nodeId,
    edgeId,
    metadata,
    onRetry,
    onDismiss,
  } = props;

  const getErrorMessage = () => {
    switch (type) {
      case WorkflowErrorType.VALIDATION:
        return 'Workflow validation failed';
      case WorkflowErrorType.EXECUTION:
        return 'Workflow execution failed';
      case WorkflowErrorType.TRANSFORMATION:
        return 'Workflow transformation failed';
      case WorkflowErrorType.NETWORK:
        return 'Network error';
      case WorkflowErrorType.AUTH:
        return 'Authentication error';
      case WorkflowErrorType.CONFIG:
        return 'Configuration error';
      default:
        return error.message || 'An unexpected error occurred';
    }
  };

  const getErrorDetails = () => {
    const details = [];

    if (componentId) {
      details.push(`Component: ${componentId}`);
    }
    if (nodeId) {
      details.push(`Node: ${nodeId}`);
    }
    if (edgeId) {
      details.push(`Edge: ${edgeId}`);
    }

    if (metadata) {
      Object.entries(metadata).forEach(([key, value]) => {
        details.push(`${key}: ${value}`);
      });
    }

    return details.join(', ');
  };

  return (
    <div className="error-handler">
      <div className="error-header">
        <h3>{getErrorMessage()}</h3>
        <button onClick={onDismiss} className="close-button">
          ×
        </button>
      </div>
      <div className="error-details">
        {getErrorDetails()}
      </div>
      {onRetry && (
        <button onClick={onRetry} className="retry-button">
          Retry
        </button>
      )}
      <pre className="error-stack">
        {error.stack}
      </pre>
    </div>
  );
};
