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
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

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
from mcp.core.config import settings  # Import after .env is loaded

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

# CORS middleware
if not os.getenv('TESTING'):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if os.getenv('TESTING'):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error (test mode)"}
        )
    
    logger.error(f"An error occurred: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

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
    # Example: Log a loaded setting
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Redis URL: {settings.REDIS_URL}")


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
