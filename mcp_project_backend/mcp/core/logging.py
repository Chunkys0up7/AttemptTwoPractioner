import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from mcp.core.errors import MCPError, handle_mcp_error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp.log')
    ]
)

logger = logging.getLogger('mcp')

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = datetime.utcnow()
        request_id = request.headers.get('X-Request-ID', 'unknown')
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'client_ip': request.client.host if request.client else None
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log response
            process_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'process_time': process_time
                }
            )
            
            return response
            
        except Exception as e:
            # Log error
            process_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    'request_id': request_id,
                    'error': str(e),
                    'process_time': process_time
                },
                exc_info=True
            )
            
            # Handle MCPError
            if isinstance(e, MCPError):
                return JSONResponse(
                    status_code=e.status_code,
                    content={
                        'message': e.message,
                        'details': e.details
                    }
                )
            
            # Handle other exceptions
            return JSONResponse(
                status_code=500,
                content={
                    'message': 'Internal server error',
                    'details': {'error': str(e)}
                }
            )

def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    level: int = logging.ERROR
) -> None:
    """Log an error with optional context."""
    extra = {'error': str(error)}
    if context:
        extra.update(context)
    
    logger.log(level, str(error), extra=extra, exc_info=True)

def log_info(
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Log an info message with optional context."""
    extra = context or {}
    logger.info(message, extra=extra)

def log_warning(
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Log a warning message with optional context."""
    extra = context or {}
    logger.warning(message, extra=extra)

def log_debug(
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """Log a debug message with optional context."""
    extra = context or {}
    logger.debug(message, extra=extra) 