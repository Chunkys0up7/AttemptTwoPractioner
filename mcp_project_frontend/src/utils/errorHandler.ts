import { Logger } from './logger';
import { AxiosError } from 'axios';

export class FrontendError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status?: number,
    public readonly details?: Record<string, any>
  ) {
    super(message);
    this.name = 'FrontendError';
  }
}

export class APIError extends FrontendError {
  constructor(
    message: string,
    status: number,
    details?: Record<string, any>
  ) {
    super(message, 'API_ERROR', status, details);
    this.name = 'APIError';
  }
}

export class ValidationError extends FrontendError {
  constructor(
    message: string,
    details?: Record<string, any>
  ) {
    super(message, 'VALIDATION_ERROR', undefined, details);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends FrontendError {
  constructor(
    message: string = 'Authentication failed',
    details?: Record<string, any>
  ) {
    super(message, 'AUTHENTICATION_ERROR', 401, details);
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends FrontendError {
  constructor(
    message: string = 'Not authorized',
    details?: Record<string, any>
  ) {
    super(message, 'AUTHORIZATION_ERROR', 403, details);
    this.name = 'AuthorizationError';
  }
}

export class NotFoundError extends FrontendError {
  constructor(
    message: string,
    details?: Record<string, any>
  ) {
    super(message, 'NOT_FOUND', 404, details);
    this.name = 'NotFoundError';
  }
}

export const handleError = (error: Error | AxiosError, context?: Record<string, any>) => {
  if (error instanceof AxiosError) {
    const { response } = error;
    if (response) {
      // Handle API errors with response
      const apiError = new APIError(
        response.data?.message || 'API error occurred',
        response.status,
        response.data?.details
      );
      Logger.error(apiError, context);
      return apiError;
    } else {
      // Handle network errors
      const networkError = new APIError(
        'Network error occurred',
        500,
        { error: error.message }
      );
      Logger.error(networkError, context);
      return networkError;
    }
  } else if (error instanceof FrontendError) {
    // Handle custom frontend errors
    Logger.error(error, context);
    return error;
  } else {
    // Handle generic errors
    const genericError = new FrontendError(
      error.message || 'An unexpected error occurred',
      'GENERIC_ERROR',
      undefined,
      { error: error.message }
    );
    Logger.error(genericError, context);
    return genericError;
  }
};

export const handleAPIError = (error: AxiosError) => {
  return handleError(error);
};

export const handleValidationError = (error: Error) => {
  return handleError(error);
};

export const handleAuthError = (error: Error) => {
  return handleError(error);
};
