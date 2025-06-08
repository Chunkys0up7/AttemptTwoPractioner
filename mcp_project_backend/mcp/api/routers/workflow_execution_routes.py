"""
API Endpoints for Workflow Execution with enhanced error handling and monitoring.
"""
from typing import Optional, List
from uuid import UUID
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from mcp.db.session import get_db
from mcp.core.settings import settings
from mcp.core.services.workflow_engine_service import WorkflowEngineService
from mcp.schemas.workflow import WorkflowRunRead, WorkflowRunCreate, WorkflowRunList
from mcp.monitoring.performance import performance_monitor

# Placeholder for actor_id until authentication is implemented
DUMMY_ACTOR_ID = "system_actor_placeholder_uuid"

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/workflow-runs",
    tags=["Workflow Runs"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        422: {"description": "Unprocessable Entity"},
        500: {"description": "Internal Server Error"}
    }
)

logger = logging.getLogger(__name__)

def get_workflow_engine_service(db: Session = Depends(get_db)) -> WorkflowEngineService:
    """
    Dependency for WorkflowEngineService with error handling.
    """
    try:
        return WorkflowEngineService(db)
    except Exception as e:
        logger.error(f"Failed to initialize WorkflowEngineService: {e}")
        performance_monitor.increment_error("workflow_engine_init", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize workflow engine"
        )

@router.post("/", response_model=WorkflowRunRead, status_code=status.HTTP_202_ACCEPTED)
async def start_workflow_run(
    request: Request,
    run_create: WorkflowRunCreate,
    service: WorkflowEngineService = Depends(get_workflow_engine_service)
):
    """
    Start a new workflow run based on a Workflow Definition ID and optional input parameters.

    The response indicates acceptance, and the workflow execution starts asynchronously.

    Security:
    - Requires authentication (TODO)
    - Rate limited to 100 requests per minute
    - Input validation
    - Database transaction isolation

    Returns:
    - 202: Workflow run accepted
    - 400: Invalid input
    - 401: Unauthorized
    - 403: Forbidden
    - 404: Workflow definition not found
    - 422: Validation error
    - 500: Internal server error
    """
    try:
        # Validate workflow definition ID
        if not run_create.workflow_definition_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow definition ID is required"
            )

        # Monitor workflow start
        with performance_monitor.monitor_workflow_execution(run_create.workflow_definition_id):
            workflow_run = await service.start_workflow_run(
                workflow_definition_id=run_create.workflow_definition_id,
                run_create_data=run_create,
                actor_id=DUMMY_ACTOR_ID
            )

        logger.info(
            f"[Request {request.state.request_id}] Started workflow run {workflow_run.id} "
            f"for definition {run_create.workflow_definition_id}"
        )
        
        return workflow_run

    except ValidationError as e:
        logger.error(f"[Request {request.state.request_id}] Validation error: {e}")
        performance_monitor.increment_error("workflow_validation", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ValueError as e:
        logger.error(f"[Request {request.state.request_id}] Workflow error: {e}")
        performance_monitor.increment_error("workflow_error", str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        logger.error(f"[Request {request.state.request_id}] Database error: {e}")
        performance_monitor.increment_error("workflow_db_error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Unexpected error: {e}")
        performance_monitor.increment_error("workflow_unexpected_error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/", response_model=WorkflowRunList)
async def list_workflow_runs(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    workflow_definition_id: Optional[UUID] = None,
    service: WorkflowEngineService = Depends(get_workflow_engine_service)
):
    """
    List workflow runs with optional filtering.

    Security:
    - Requires authentication (TODO)
    - Rate limited to 100 requests per minute
    - Input validation

    Returns:
    - 200: List of workflow runs
    - 400: Invalid input
    - 401: Unauthorized
    - 403: Forbidden
    - 422: Validation error
    """
    try:
        runs, total = await service.list_workflow_runs(
            skip=skip,
            limit=limit,
            status=status,
            workflow_definition_id=workflow_definition_id
        )
        
        logger.info(
            f"[Request {request.state.request_id}] Listed {len(runs)} workflow runs (total: {total})"
        )
        
        return WorkflowRunList(items=runs, total=total)
        
    except ValueError as e:
        logger.error(f"[Request {request.state.request_id}] Filter error: {e}")
        performance_monitor.increment_error("workflow_filter_error", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        logger.error(f"[Request {request.state.request_id}] Database error: {e}")
        performance_monitor.increment_error("workflow_db_error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Unexpected error: {e}")
        performance_monitor.increment_error("workflow_unexpected_error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/{run_id}", response_model=WorkflowRunRead)
async def get_workflow_run(
    request: Request,
    run_id: UUID,
    service: WorkflowEngineService = Depends(get_workflow_engine_service)
):
    """
    Get details of a specific workflow run.

    Security:
    - Requires authentication (TODO)
    - Rate limited to 100 requests per minute

    Returns:
    - 200: Workflow run details
    - 401: Unauthorized
    - 403: Forbidden
    - 404: Workflow run not found
    """
    try:
        run = await service.get_workflow_run(run_id)
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow run not found"
            )
            
        logger.info(
            f"[Request {request.state.request_id}] Retrieved workflow run {run_id}"
        )
        
        return run
        
    except SQLAlchemyError as e:
        logger.error(f"[Request {request.state.request_id}] Database error: {e}")
        performance_monitor.increment_error("workflow_db_error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"[Request {request.state.request_id}] Unexpected error: {e}")
        performance_monitor.increment_error("workflow_unexpected_error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
#     service: WorkflowEngineService = Depends(get_workflow_engine_service)
# ):
#     run = service.get_workflow_run(run_id)
#     if not run:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow Run not found")
#     return run
