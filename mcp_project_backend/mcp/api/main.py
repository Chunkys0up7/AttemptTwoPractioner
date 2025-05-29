"""
Main FastAPI application for the MCP Backend.

This module initializes the FastAPI application, sets up logging, loads environment
variables, and defines global application event handlers and basic health check endpoints.
"""
# --- Start: Environment Variable Loading from .env ---
# This section MUST be at the very top of the file
from mcp.core.pubsub.redis_pubsub import RedisPubSubManager
# from mcp.db import base_class # For creating tables if needed, or use Alembic
# Assuming SessionLocal and engine are setup
# from mcp.db.session import get_db # SessionLocal, engine are unused, get_db also unused
from mcp.api.routers import (
    mcp_crud_routes,
    workflow_execution_routes,
    external_db_config_routes,
    streaming_routes,
    dashboard_routes,
    entity_routes,    # Add entity_routes
)
from mcp.core.config import settings  # Import after .env is loaded
# import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
# from fastapi.staticfiles import StaticFiles # Unused
import uvicorn
# import asyncio # Unused

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Assuming mcp/api/main.py is the location of this file
    # Project root is three levels up from mcp/api/main.py (main.py -> api -> mcp -> project_root)
    current_file_path = Path(__file__).resolve()
    project_root = current_file_path.parent.parent.parent
    env_file_path = project_root / '.env'

    if env_file_path.exists():
        logger.info(
            f"MCP Backend: Loading environment variables from: {env_file_path}")
        load_dotenv(dotenv_path=str(env_file_path), override=True)
    else:
        logger.info(
            f"MCP Backend: No .env file found at {env_file_path}. Relying on system environment variables.")
except Exception as e:
    logger.error(f"MCP Backend: Error loading .env file: {e}")
# --- End: Environment Variable Loading from .env ---


# Import RedisPubSubManager

# Create an instance of RedisPubSubManager
# This requires REDIS_URL to be available in settings when main.py is loaded.
redis_pubsub_manager = RedisPubSubManager(settings.REDIS_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("MCP Backend starting up...")
    # Create database tables (if not using Alembic for all DDL management initially)
    # try:
    #     base_class.Base.metadata.create_all(bind=engine)
    #     logger.info("Database tables checked/created.")
    # except Exception as e:
    #     logger.error(f"Error creating database tables: {e}")

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


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint to verify the application is running."""
    return {"status": "ok", "app_name": settings.APP_NAME}

# Include the MCP CRUD router
app.include_router(mcp_crud_routes.router, prefix=settings.API_V1_STR)

# Include the Workflow Execution router
app.include_router(workflow_execution_routes.router,
                   prefix=settings.API_V1_STR)

# Include the External DB Config router
app.include_router(external_db_config_routes.router,
                   prefix=settings.API_V1_STR)

# Include the Streaming routes router
app.include_router(streaming_routes.router, prefix=settings.API_V1_STR)

# Include the Dashboard routes router
app.include_router(dashboard_routes.router, prefix=settings.API_V1_STR)

# Include the Entity routes router
app.include_router(entity_routes.router, prefix=settings.API_V1_STR)

# To run the app (example from project root):
# Ensure .env file is in mcp_project_backend/ directory or project root if path adjusted
# Option 1: (If mcp_project_backend is in PYTHONPATH or you are in that directory)
# uvicorn mcp.api.main:app --reload
# Option 2: Specify app-dir (uvicorn will add this to sys.path)
# uvicorn mcp.api.main:app --reload --app-dir ./mcp_project_backend

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # pragma: no cover
