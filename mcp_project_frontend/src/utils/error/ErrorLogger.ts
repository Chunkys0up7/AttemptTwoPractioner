import { ErrorLoggerProps, WorkflowErrorType } from '../../types/errors';
import { v4 as uuidv4 } from 'uuid';

/**
 * Error logging utility
 */
export class ErrorLogger {
  private static instance: ErrorLogger;
  private errorReports: WorkflowError[] = [];
  private maxReports: number = 100;

  private constructor() {}

  public static getInstance(): ErrorLogger {
    if (!ErrorLogger.instance) {
      ErrorLogger.instance = new ErrorLogger();
    }
    return ErrorLogger.instance;
  }

  /**
   * Log an error
   * @param props - ErrorLoggerProps
   * @returns Error report ID
   */
  public static logError(props: ErrorLoggerProps): string {
    const instance = ErrorLogger.getInstance();
    const errorId = uuidv4();

    const errorReport: WorkflowError = {
      id: errorId,
      type: props.type || WorkflowErrorType.UNKNOWN,
      message: props.error.message,
      details: props.error,
      timestamp: new Date(),
      componentId: props.metadata?.componentId,
      nodeId: props.metadata?.nodeId,
      edgeId: props.metadata?.edgeId,
      retryCount: props.metadata?.retryCount,
      isFatal: props.isFatal || false,
      stack: props.error.stack,
    };

    instance.errorReports.push(errorReport);
    instance.errorReports = instance.errorReports.slice(-instance.maxReports);

    // Log to console
    console.error(`[${errorReport.type}] ${errorReport.message}`, {
      error: errorReport.details,
      metadata: props.metadata,
      context: props.context,
    });

    // Send to error tracking service
    instance.sendToTrackingService(errorReport);

    return errorId;
  }

  /**
   * Get error reports
   * @param filter - Optional filter object
   * @returns Array of error reports
   */
  public static getErrorReports(filter?: {
    type?: WorkflowErrorType;
    componentId?: string;
    nodeId?: string;
    edgeId?: string;
    isFatal?: boolean;
  }): WorkflowError[] {
    const instance = ErrorLogger.getInstance();
    return instance.errorReports.filter(report => {
      if (filter?.type && report.type !== filter.type) return false;
      if (filter?.componentId && report.componentId !== filter.componentId) return false;
      if (filter?.nodeId && report.nodeId !== filter.nodeId) return false;
      if (filter?.edgeId && report.edgeId !== filter.edgeId) return false;
      if (filter?.isFatal !== undefined && report.isFatal !== filter.isFatal) return false;
      return true;
    });
  }

  /**
   * Clear error reports
   */
  public static clearErrorReports(): void {
    const instance = ErrorLogger.getInstance();
    instance.errorReports = [];
  }

  /**
   * Send error report to tracking service
   * @param report - Error report
   */
  private sendToTrackingService(report: WorkflowError): void {
    // TODO: Implement actual error tracking service integration
    // This is a placeholder for error tracking integration
    // Could be Sentry, New Relic, or custom error tracking service
    console.log('Sending error to tracking service:', report);
  }

  /**
   * Get error statistics
   * @returns Error statistics
   */
  public static getErrorStatistics(): {
    total: number;
    byType: Record<WorkflowErrorType, number>;
    byComponent: Record<string, number>;
    byNode: Record<string, number>;
    byEdge: Record<string, number>;
    fatal: number;
  } {
    const instance = ErrorLogger.getInstance();
    const stats = {
      total: instance.errorReports.length,
      byType: {} as Record<WorkflowErrorType, number>,
      byComponent: {} as Record<string, number>,
      byNode: {} as Record<string, number>,
      byEdge: {} as Record<string, number>,
      fatal: 0,
    };

    instance.errorReports.forEach(report => {
      stats.byType[report.type] = (stats.byType[report.type] || 0) + 1;
      if (report.componentId) {
        stats.byComponent[report.componentId] = (stats.byComponent[report.componentId] || 0) + 1;
      }
      if (report.nodeId) {
        stats.byNode[report.nodeId] = (stats.byNode[report.nodeId] || 0) + 1;
      }
      if (report.edgeId) {
        stats.byEdge[report.edgeId] = (stats.byEdge[report.edgeId] || 0) + 1;
      }
      if (report.isFatal) {
        stats.fatal++;
      }
    });

    return stats;
  }
}
