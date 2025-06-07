import uuid
from fastapi import Request, Response, HTTPException
from datetime import datetime
import logging
from mcp.core.logging import setup_request_logging

logger = logging.getLogger(__name__)

class RequestContextMiddleware:
    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Process incoming request and add request context.
        
        Args:
            request: Incoming request
            call_next: Next middleware in the chain
            
        Returns:
            Response with request context
        """
        try:
            # Generate request ID
            request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
            
            # Get correlation ID from headers or generate new one
            correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
            
            # Add request context to state
            request.state.request_id = request_id
            request.state.correlation_id = correlation_id
            request.state.start_time = datetime.now()
            
            # Setup request logging
            setup_request_logging(request)
            
            # Log request start
            logger.info(
                f"Request started - {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
                }
            )

            # Call next middleware
            response = await call_next(request)

            # Calculate request duration
            duration = (datetime.now() - request.state.start_time).total_seconds()
            
            # Log request completion
            logger.info(
                f"Request completed - {request.method} {request.url.path} {response.status_code}",
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "duration_ms": duration * 1000,
                    "status_code": response.status_code,
                    "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
                }
            )

            return response

        except HTTPException as e:
            logger.error(
                f"Request failed - {request.method} {request.url.path} {e.status_code}",
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "error": str(e.detail),
                    "status_code": e.status_code,
                    "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
                }
            )
            raise

        except Exception as e:
            logger.error(
                f"Request failed - {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "error": str(e),
                    "user_id": request.state.user_id if hasattr(request.state, "user_id") else "-"
                }
            )
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error"
            )
