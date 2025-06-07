import logging
import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from structlog import configure, get_logger, make_filtering_bound_logger
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level

from mcp.core.config import settings
from mcp.core.exceptions import MCPException

# Configure structlog
configure(
    processors=[
        add_log_level,
        TimeStamper(fmt="iso"),
        JSONRenderer(sort_keys=True)
    ],
    context_class=dict,
    logger_factory=get_logger,
    wrapper_class=make_filtering_bound_logger(logging.INFO),
    cache_logger_on_first_use=True,
)

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp.log')
    ]
)

# Get structlog logger
logger = get_logger("mcp")

# Add custom logging middleware for FastAPI
class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Log request
            start_time = datetime.utcnow()
            request_id = request.headers.get('X-Request-ID', 'unknown')
            
            logger.info(
                "http.request",
                method=request.method,
                path=request.url.path,
                client_ip=request.client.host if request.client else None,
                request_id=request_id,
                timestamp=start_time.isoformat()
            )
            
            # Process request
            response = await call_next(request)
            
            # Log response
            process_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                "http.response",
                status_code=response.status_code,
                process_time=process_time,
                request_id=request_id,
                timestamp=datetime.utcnow().isoformat()
            )
            
            return response
            
        except MCPException as e:
            logger.error(
                "http.error",
                error_type=type(e).__name__,
                message=str(e),
                status_code=e.status_code,
                timestamp=datetime.utcnow().isoformat()
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    'message': e.message,
                    'details': e.details
                }
            )
            
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