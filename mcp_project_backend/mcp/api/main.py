"""
Main FastAPI application for the MCP Backend.

This module initializes the FastAPI application, sets up logging, loads environment
variables, and defines global application event handlers and basic health check endpoints.
"""
# --- Start: Environment Variable Loading from .env ---
# This section MUST be at the very top of the file
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import time
from typing import Callable, Optional
import logging
from datetime import datetime
import uuid
from mcp.monitoring.performance import performance_monitor
from mcp.monitoring.security import security_monitor
from mcp.monitoring.health import health_monitor
from mcp.monitoring.metrics import metrics_monitor
from mcp.core.config import settings
from mcp.core.auth import get_current_user
from mcp.core.cache import cache_manager
from mcp.core.rate_limiter import rate_limiter
from mcp.core.security import security_manager
from mcp.core.logging import setup_logging
from mcp.core.exceptions import APIException
from mcp.core.schemas import ErrorResponse
from mcp.core.utils import generate_request_id, get_remote_ip
from mcp.core.cache import cache_manager
from mcp.core.rate_limiter import rate_limiter
from mcp.core.security import security_manager
from mcp.core.logging import setup_logging
from mcp.core.exceptions import APIException
from mcp.core.schemas import ErrorResponse
from mcp.core.utils import generate_request_id, get_remote_ip

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mcp.core.pubsub.redis_pubsub_manager import redis_pubsub_manager
from mcp.api.routers import (
    mcp_crud_routes,
    workflow_execution_routes,
    external_db_config_routes,
    streaming_routes,
    dashboard_routes,
    entity_routes,    # Add entity_routes
)
from mcp.core.settings import settings  # Import after .env is loaded

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Assuming mcp/api/main.py is the location of this file
    # Project root is three levels up from mcp/api/main.py (main.py -> api -> mcp -> mcp -> project_root)
    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parent.parent.parent.parent
    env_file_path = project_root / '.env'

    if env_file_path.exists():
        logger.info(
            f"MCP Backend: Loading environment variables from: {env_file_path}")
        load_dotenv(dotenv_path=str(env_file_path), override=True)
    else:
        logger.info("No .env file found, using environment variables directly.")
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    raise

# Initialize FastAPI app
if os.getenv('TESTING'):
    app = FastAPI(
        title="MCP Backend API (Test)",
        description="API for managing MCP workflows and executions (Test Mode).",
        version="1.0.0",
        docs_url=None,  # Disable docs in test mode
        redoc_url=None,
        openapi_url=None
    )
else:
    app = FastAPI(
        title="MCP Backend API",
        description="API for managing MCP workflows and executions.",
        version="1.0.0",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

# Security middleware
if settings.ENABLE_SECURITY:
    # Trusted Hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # HTTPS Redirect
    if settings.FORCE_HTTPS:
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Session Management
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET,
        max_age=settings.SESSION_MAX_AGE
    )
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Length", "Content-Type", "X-Request-ID"],
        max_age=3600
    )
    
    # GZIP Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Rate Limiting
    app.add_middleware(rate_limiter)
    
    # Security Headers
    app.add_middleware(
        security_manager,
        x_content_type_options="nosniff",
        x_frame_options="DENY",
        x_xss_protection="1; mode=block",
        strict_transport_security="max-age=31536000; includeSubDomains",
        referrer_policy="strict-origin-when-cross-origin"
    )

# Custom exception handler
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """
    Handle custom API exceptions with proper error responses.
    """
    logger.error(
        f"API Error [{request.state.request_id}]: {exc.detail}",
        extra={"error_type": type(exc).__name__, "status_code": exc.status_code}
    )
    
    security_monitor.increment_error("api_error", str(exc))
    metrics_monitor.increment("api_errors", 1, tags=["error_type:api"])
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.detail,
            details=exc.details
        ).model_dump()
    )

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors with detailed error responses.
    """
    logger.error(
        f"Validation Error [{request.state.request_id}]: {exc.errors()}",
        extra={"errors": exc.errors(), "body": exc.body}
    )
    
    security_monitor.increment_error("validation_error", str(exc))
    metrics_monitor.increment("validation_errors", 1, tags=["error_type:validation"])
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details=exc.errors()
        ).model_dump()
    )

# Request ID middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and track request IDs.
    """
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = generate_request_id()
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log request metrics
            duration = time.time() - start_time
            metrics_monitor.observe("request_duration", duration, 
                                 tags=["endpoint:", f"{request.url.path}"])
            
            return response
            
        except Exception as e:
            logger.error(
                f"Request Error [{request_id}]: {str(e)}",
                extra={"path": request.url.path, "method": request.method}
            )
            raise e

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if os.getenv('TESTING'):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error (test mode)"}
        )
    
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mcp.db.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("MCP Backend starting up...")
    # Create database tables (if not using Alembic for all DDL management initially)
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

    # Connect Redis Pub/Sub publisher
    if settings.REDIS_URL:
        try:
            await redis_pubsub_manager.connect_publisher()
        except ConnectionError as e:
            logger.error(
                f"Failed to connect to Redis for Pub/Sub: {e}. Real-time features may be impacted.")
            # Depending on requirements, you might prevent app startup if Redis is critical.
    else:
        logger.warning(
            "REDIS_URL not configured. Real-time Pub/Sub features will be disabled.")

    yield
    # Shutdown
    logger.info("MCP Backend shutting down...")
    # Disconnect Redis Pub/Sub publisher
    if redis_pubsub_manager._publisher_client:  # Check if client was initialized
        await redis_pubsub_manager.disconnect_publisher()
    
    # Clean up database
    try:
        engine.dispose()
    except Exception as e:
        logger.error(f"Error cleaning up database: {e}")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="0.1.0",  # Example version
    description="Backend API for the Model Context Protocol (MCP) AI Ops Console.",
    # Add other FastAPI configurations as needed, like contact, license_info
    lifespan=lifespan  # Use the lifespan context manager
)

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/")
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Custom RequestValidationError handler


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # You can customize the error response format here
    # For example, log the error details
    logger.error(f"Request validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body if hasattr(
            exc, 'body') else None}
    )


@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup."""
    logger.info("Application startup...")
    
    # Initialize logging
    setup_logging()
    
    # Initialize monitoring
    performance_monitor.start()
    security_monitor.start()
    health_monitor.start()
    metrics_monitor.start()
    
    # Initialize cache
    await cache_manager.initialize()
    
    # Initialize rate limiter
    await rate_limiter.initialize()
    
    # Initialize security
    await security_manager.initialize()
    
    # Log configuration
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Redis URL: {settings.REDIS_URL}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")
    logger.info(f"Security Enabled: {settings.ENABLE_SECURITY}")
    logger.info(f"Force HTTPS: {settings.FORCE_HTTPS}")
    logger.info(f"Rate Limiting: {settings.RATE_LIMIT_ENABLED}")
    logger.info(f"Cache Enabled: {settings.CACHE_ENABLED}")
    logger.info(f"Monitoring Enabled: {settings.MONITORING_ENABLED}")
    
    # Health check
    health_status = await health_monitor.check_health()
    if not health_status.get("healthy", False):
        logger.error("Health check failed during startup:", extra={"health": health_status})
        raise Exception("Health check failed during startup")
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown."""
    logger.info("Application shutdown...")
    
    # Cleanup monitoring
    await performance_monitor.stop()
    await security_monitor.stop()
    await health_monitor.stop()
    await metrics_monitor.stop()
    
    # Cleanup cache
    await cache_manager.cleanup()
    
    # Cleanup rate limiter
    await rate_limiter.cleanup()
    
    # Cleanup security
    await security_manager.cleanup()
    
    logger.info("Application shutdown complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown."""
    logger.info("Application shutdown...")


# Include routers with their own prefixes
app.include_router(mcp_crud_routes.router)
app.include_router(workflow_execution_routes.router)
app.include_router(external_db_config_routes.router)
app.include_router(streaming_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(entity_routes.router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint to verify the application is running."""
    return {"status": "ok", "app_name": settings.APP_NAME}

# To run the app (example from project root):
# Ensure .env file is in mcp_project_backend/ directory or project root if path adjusted
# Option 1: (If mcp_project_backend is in PYTHONPATH or you are in that directory)
# uvicorn mcp.api.main:app --reload
# Option 2: Specify app-dir (uvicorn will add this to sys.path)
# uvicorn mcp.api.main:app --reload --app-dir ./mcp_project_backend

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # pragma: no cover
