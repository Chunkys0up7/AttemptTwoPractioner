import { 
  WorkflowError,
  WorkflowErrorType,
  ErrorBoundaryProps,
  ErrorBoundaryState,
  ErrorLoggerProps,
  ErrorHandlerProps,
  ErrorReport,
  ErrorContextType,
} from '../../types/errors';

export const mockError: Error = new Error('Test error message');

export const mockWorkflowError: WorkflowError = {
  id: 'error1',
  type: WorkflowErrorType.VALIDATION,
  message: 'Validation failed',
  details: mockError,
  timestamp: new Date(),
  componentId: 'component1',
  nodeId: 'node1',
  edgeId: 'edge1',
  retryCount: 0,
  isFatal: false,
  stack: mockError.stack,
};

export const mockErrorReport: ErrorReport = {
  id: 'report1',
  error: mockError,
  type: WorkflowErrorType.VALIDATION,
  metadata: {
    componentId: 'component1',
    nodeId: 'node1',
    edgeId: 'edge1',
  },
  timestamp: new Date(),
  handled: false,
  retryCount: 0,
  isFatal: false,
};

export const mockErrorBoundaryProps: ErrorBoundaryProps = {
  fallback: <div>Error occurred</div>,
  onReset: jest.fn(),
  onError: jest.fn(),
  maxRetries: 3,
  retryDelay: 3000,
  children: <div>Content</div>,
};

export const mockErrorHandlerProps: ErrorHandlerProps = {
  error: mockError,
  type: WorkflowErrorType.VALIDATION,
  componentId: 'component1',
  nodeId: 'node1',
  edgeId: 'edge1',
  metadata: {},
  onRetry: jest.fn(),
  onDismiss: jest.fn(),
};

export const mockErrorLoggerProps: ErrorLoggerProps = {
  error: mockError,
  metadata: {
    componentId: 'component1',
    nodeId: 'node1',
    edgeId: 'edge1',
  },
  isFatal: false,
  context: 'Test context',
};

export const mockErrorContext: ErrorContextType = {
  error: null,
  setError: jest.fn(),
  clearError: jest.fn(),
  hasError: false,
  errorType: null,
  errorMetadata: {},
};

export const renderErrorBoundary = (props: Partial<ErrorBoundaryProps> = {}) => {
  return render(
    <ErrorBoundary {...mockErrorBoundaryProps} {...props} />
  );
};

export const simulateError = (error: Error) => {
  throw error;
};

export const simulateRetry = (count: number) => {
  for (let i = 0; i < count; i++) {
    setTimeout(() => {}, 100);
  }
};
