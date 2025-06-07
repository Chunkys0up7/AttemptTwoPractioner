from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from mcp.core.exceptions import (
    WorkflowDefinitionError,
    WorkflowStepError,
    AuthenticationError,
    RateLimitExceededError,
    CircuitBreakerOpenError
)
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ExceptionHandler:
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions.
        
        Args:
            request: Incoming request
            exc: HTTP exception
            
        Returns:
            JSON response with error details
        """
        logger.error(
            f"HTTP Exception - {exc.status_code}: {exc.detail}",
            extra={
                "request_id": request.state.request_id,
                "correlation_id": request.state.correlation_id,
                "status_code": exc.status_code,
                "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": request.state.request_id,
                "timestamp": datetime.now().isoformat()
            }
        )

    @staticmethod
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """
        Handle Pydantic validation errors.
        
        Args:
            request: Incoming request
            exc: Validation error
            
        Returns:
            JSON response with validation errors
        """
        logger.error(
            f"Validation Error: {str(exc)}",
            extra={
                "request_id": request.state.request_id,
                "correlation_id": request.state.correlation_id,
                "error_type": "validation",
                "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
            }
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "request_id": request.state.request_id,
                "timestamp": datetime.now().isoformat()
            }
        )

    @staticmethod
    async def workflow_definition_error_handler(request: Request, exc: WorkflowDefinitionError) -> JSONResponse:
        """
        Handle workflow definition errors.
        
        Args:
            request: Incoming request
            exc: Workflow definition error
            
        Returns:
            JSON response with error details
        """
        logger.error(
            f"Workflow Definition Error: {str(exc)}",
            extra={
                "request_id": request.state.request_id,
                "correlation_id": request.state.correlation_id,
                "error_type": "workflow_definition",
                "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
            }
        )
        
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "request_id": request.state.request_id,
                "timestamp": datetime.now().isoformat()
            }
        )

    @staticmethod
    async def workflow_step_error_handler(request: Request, exc: WorkflowStepError) -> JSONResponse:
        """
        Handle workflow step errors.
        
        Args:
            request: Incoming request
            exc: Workflow step error
            
        Returns:
            JSON response with error details
        """
        logger.error(
            f"Workflow Step Error: {str(exc)}",
            extra={
                "request_id": request.state.request_id,
                "correlation_id": request.state.correlation_id,
                "error_type": "workflow_step",
                "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
            }
        )
        
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc),
                "request_id": request.state.request_id,
                "timestamp": datetime.now().isoformat()
            }
        )

    @staticmethod
    async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        """
        Handle authentication errors.
        
        Args:
            request: Incoming request
            exc: Authentication error
            
        Returns:
            JSON response with error details
        """
        logger.error(
            f"Authentication Error: {str(exc)}",
            extra={
                "request_id": request.state.request_id,
                "correlation_id": request.state.correlation_id,
                "error_type": "authentication",
                "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
            }
        )
        
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Unauthorized",
                "request_id": request.state.request_id,
                "timestamp": datetime.now().isoformat()
            }
        )

    @staticmethod
    async def rate_limit_error_handler(request: Request, exc: RateLimitExceededError) -> JSONResponse:
        """
        Handle rate limit errors.
        
        Args:
            request: Incoming request
            exc: Rate limit error
            
        Returns:
            JSON response with error details
        """
        logger.warning(
            f"Rate Limit Exceeded: {str(exc)}",
            extra={
                "request_id": request.state.request_id,
                "correlation_id": request.state.correlation_id,
                "error_type": "rate_limit",
                "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
            }
        )
        
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "request_id": request.state.request_id,
                "timestamp": datetime.now().isoformat()
            }
        )

    @staticmethod
    async def circuit_breaker_error_handler(request: Request, exc: CircuitBreakerOpenError) -> JSONResponse:
        """
        Handle circuit breaker errors.
        
        Args:
            request: Incoming request
            exc: Circuit breaker error
            
        Returns:
            JSON response with error details
        """
        logger.error(
            f"Circuit Breaker Open: {str(exc)}",
            extra={
                "request_id": request.state.request_id,
                "correlation_id": request.state.correlation_id,
                "error_type": "circuit_breaker",
                "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
            }
        )
        
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Service temporarily unavailable due to high error rate",
                "request_id": request.state.request_id,
                "timestamp": datetime.now().isoformat()
            }
        )
