import { ErrorLogger } from '../ErrorLogger';
import { 
  mockError,
  mockWorkflowError,
  mockErrorReport,
  mockErrorLoggerProps,
} from '../../../test/utils/error.testUtils';

// Mock console.error
describe('ErrorLogger', () => {
  let instance: ErrorLogger;
  let originalConsoleError: typeof console.error;

  beforeEach(() => {
    originalConsoleError = console.error;
    console.error = jest.fn();
    instance = ErrorLogger.getInstance();
  });

  afterEach(() => {
    console.error = originalConsoleError;
    ErrorLogger.clearErrorReports();
  });

  it('should be a singleton', () => {
    const instance1 = ErrorLogger.getInstance();
    const instance2 = ErrorLogger.getInstance();
    expect(instance1).toBe(instance2);
  });

  it('should log error', () => {
    const errorId = ErrorLogger.logError(mockErrorLoggerProps);
    expect(typeof errorId).toBe('string');
    expect(errorId.length).toBeGreaterThan(0);
  });

  it('should get error reports', () => {
    ErrorLogger.logError(mockErrorLoggerProps);
    const reports = ErrorLogger.getErrorReports();
    expect(reports).toHaveLength(1);
  });

  it('should filter error reports', () => {
    ErrorLogger.logError(mockErrorLoggerProps);
    const reports = ErrorLogger.getErrorReports({
      type: WorkflowErrorType.VALIDATION,
      componentId: 'component1',
    });
    expect(reports).toHaveLength(1);
  });

  it('should clear error reports', () => {
    ErrorLogger.logError(mockErrorLoggerProps);
    ErrorLogger.clearErrorReports();
    const reports = ErrorLogger.getErrorReports();
    expect(reports).toHaveLength(0);
  });

  it('should get error statistics', () => {
    ErrorLogger.logError(mockErrorLoggerProps);
    const stats = ErrorLogger.getErrorStatistics();
    expect(stats.total).toBe(1);
    expect(stats.byType[WorkflowErrorType.VALIDATION]).toBe(1);
    expect(stats.byComponent['component1']).toBe(1);
  });

  it('should handle error tracking', () => {
    jest.spyOn(console, 'log');
    ErrorLogger.logError(mockErrorLoggerProps);
    expect(console.log).toHaveBeenCalledWith(
      expect.stringContaining('Sending error to tracking service')
    );
  });
});
