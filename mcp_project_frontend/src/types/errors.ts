/**
 * Error types for the workflow system
 */

export interface WorkflowError {
  id: string;
  type: WorkflowErrorType;
  message: string;
  details?: any;
  timestamp: Date;
  componentId?: string;
  nodeId?: string;
  edgeId?: string;
  retryCount?: number;
  isFatal?: boolean;
  stack?: string;
}

export enum WorkflowErrorType {
  VALIDATION = 'VALIDATION',
  EXECUTION = 'EXECUTION',
  TRANSFORMATION = 'TRANSFORMATION',
  NETWORK = 'NETWORK',
  AUTH = 'AUTH',
  CONFIG = 'CONFIG',
  UNKNOWN = 'UNKNOWN',
}

export interface ErrorBoundaryProps {
  fallback?: React.ReactNode | ((props: { error: Error }) => React.ReactNode);
  onReset?: () => void;
  onError?: (error: Error) => void;
  maxRetries?: number;
  retryDelay?: number;
  children: React.ReactNode;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  retryCount: number;
  lastErrorTime?: Date;
}

export interface ErrorLoggerProps {
  error: Error;
  metadata?: any;
  isFatal?: boolean;
  context?: string;
}

export interface ErrorHandlerProps {
  error: Error;
  type: WorkflowErrorType;
  componentId?: string;
  nodeId?: string;
  edgeId?: string;
  metadata?: any;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export interface ErrorReport {
  id: string;
  error: Error;
  type: WorkflowErrorType;
  metadata: any;
  timestamp: Date;
  handled: boolean;
  retryCount: number;
  isFatal: boolean;
}

export interface ErrorContextType {
  error: Error | null;
  setError: (error: Error) => void;
  clearError: () => void;
  hasError: boolean;
  errorType: WorkflowErrorType | null;
  errorMetadata: any;
}

export interface ErrorBoundaryConfig {
  maxRetries: number;
  retryDelay: number;
  fallbackUI: React.ReactNode | ((props: { error: Error }) => React.ReactNode);
  onMaxRetries?: () => void;
  onError?: (error: Error) => void;
}
