import { createLogger, format, transports } from 'winston';
import { format as logFormat } from 'logform';
import { API_BASE_URL } from '../config';

// Define log levels
const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4
};

// Define log format
const formatLog = format.combine(
  format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  format.errors({ stack: true }),
  format.splat(),
  format.json()
);

// Create logger instance
const logger = createLogger({
  levels,
  format: formatLog,
  defaultMeta: { service: 'mcp-frontend' },
  transports: [
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.simple()
      )
    }),
    new transports.File({
      filename: 'error.log',
      level: 'error'
    }),
    new transports.File({ filename: 'combined.log' })
  ]
});

// Add custom error handler
const handleError = (error: Error, context: Record<string, any> = {}) => {
  logger.error(error.message, {
    ...context,
    stack: error.stack,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    apiBaseUrl: API_BASE_URL
  });
};

// Add custom info handler
const handleInfo = (message: string, context: Record<string, any> = {}) => {
  logger.info(message, {
    ...context,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
};

// Add custom warn handler
const handleWarn = (message: string, context: Record<string, any> = {}) => {
  logger.warn(message, {
    ...context,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
};

// Add custom debug handler
const handleDebug = (message: string, context: Record<string, any> = {}) => {
  logger.debug(message, {
    ...context,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
};

// Add custom http handler
const handleHttp = (
  method: string,
  url: string,
  status: number,
  context: Record<string, any> = {}
) => {
  logger.http(`${method} ${url} ${status}`, {
    ...context,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
};

export const Logger = {
  error: handleError,
  info: handleInfo,
  warn: handleWarn,
  debug: handleDebug,
  http: handleHttp,
  logger: logger
};
