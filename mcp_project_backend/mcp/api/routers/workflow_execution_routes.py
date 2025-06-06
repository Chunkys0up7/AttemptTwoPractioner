"""
API Endpoints for Workflow Execution.
"""
# import uuid # Unused
# from typing import Dict, Any, Optional # All unused

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from mcp.db.session import get_db
from mcp.core.config import settings  # Import settings
from mcp.core.services.workflow_engine_service import WorkflowEngineService
from mcp.schemas.workflow import WorkflowRunRead, WorkflowRunCreate

# Placeholder for actor_id until authentication is implemented
DUMMY_ACTOR_ID = "system_actor_placeholder_uuid"

router = APIRouter(
    # Updated prefix based on main.py
    prefix=f"{settings.API_V1_STR}/workflow-runs",
    tags=["Workflow Runs"],  # Updated tag
)

# Dependency for WorkflowEngineService


def get_workflow_engine_service(db: Session = Depends(get_db)) -> WorkflowEngineService:
    return WorkflowEngineService(db)


@router.post("/", response_model=WorkflowRunRead, status_code=status.HTTP_202_ACCEPTED)
async def start_workflow_run(
    run_create: WorkflowRunCreate,  # Use WorkflowRunCreate schema for the body
    service: WorkflowEngineService = Depends(get_workflow_engine_service)
):
    """
    Start a new workflow run based on a Workflow Definition ID and optional input parameters.
    The `workflow_definition_id` is part of the `run_create` request body.

    The response indicates acceptance, and the workflow execution starts asynchronously.
    """
    try:
        workflow_run = await service.start_workflow_run(
            workflow_definition_id=run_create.workflow_definition_id,
            run_create_data=run_create,  # Pass the full Pydantic model
            actor_id=DUMMY_ACTOR_ID
        )
        return workflow_run
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error starting workflow run: {str(e)}")

# GET endpoints for runs (e.g., get by ID, list runs) would go here
# These are read operations and typically don't involve actor_id for auditing creation/modification.
# Example:
# @router.get("/{run_id}", response_model=WorkflowRunRead)
# async def get_workflow_run_details(
#     run_id: uuid.UUID,
#     service: WorkflowEngineService = Depends(get_workflow_engine_service)
# ):
#     run = service.get_workflow_run(run_id)
#     if not run:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow Run not found")
#     return run
