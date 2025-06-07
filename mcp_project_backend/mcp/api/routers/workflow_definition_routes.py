"""
API Endpoints for managing Workflow Definitions and their Workflow Steps.

This router provides CRUD operations for WorkflowDefinitions and for managing WorkflowSteps within a workflow (adding, removing, reordering MCP versions as steps).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import ValidationError
from mcp.db.session import get_db
from mcp.core.config import settings
from mcp.api.schemas.workflow_definition_schemas import (
    WorkflowDefinitionCreate, WorkflowDefinitionRead, WorkflowDefinitionUpdate,
    WorkflowStepCreate, WorkflowStepRead
)
from mcp.db.crud.crud_workflow_definition import crud_workflow_definition, crud_workflow_step
from mcp.core.exceptions import WorkflowDefinitionError, WorkflowStepError
from mcp.core.logging import logger
from fastapi.responses import JSONResponse

# Custom exception handlers
async def handle_validation_error(request: Any, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

async def handle_workflow_error(request: Any, exc: WorkflowDefinitionError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Workflow error",
            "message": str(exc)
        }
    )

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/workflow-definitions",
    tags=["Workflow Definitions"],
)

@router.post("/", response_model=WorkflowDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_workflow_definition(
    db: Session = Depends(get_db),
    wf_def_in: WorkflowDefinitionCreate
):
    """
    Create a new Workflow Definition, optionally with steps.

    Args:
        wf_def_in: Workflow definition data
        db: Database session

    Returns:
        Created workflow definition

    Raises:
        HTTPException: If validation fails or creation fails
    """
    try:
        # Validate input
        if not wf_def_in.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow name is required"
            )

        if len(wf_def_in.steps or []) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 steps allowed per workflow"
            )

        # Create workflow
        wf_def = crud_workflow_definition.create_with_steps(db=db, obj_in=wf_def_in)
        
        # Log creation
        logger.info(f"Workflow created: {wf_def.name} (ID: {wf_def.id})")
        
        return wf_def

    except ValidationError as e:
        logger.error(f"Validation error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except WorkflowDefinitionError as e:
        logger.error(f"Workflow creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the workflow"
        )

@router.get("/", response_model=List[WorkflowDefinitionRead])
def list_workflow_definitions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search term to filter workflows by name or description"),
    mcp_type: Optional[str] = Query(None, description="Filter workflows containing steps of this MCP type"),
    include_archived: bool = Query(False, description="Include archived workflows")
):
    """
    List all Workflow Definitions with optional filtering.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        search: Search term to filter workflows by name or description
        mcp_type: Filter workflows containing steps of this MCP type
        include_archived: Include archived workflows in results

    Returns:
        List of workflow definitions matching filters

    Raises:
        HTTPException: If database error occurs
    """
    try:
        # Apply filters
        if search or mcp_type or include_archived:
            defs = crud_workflow_definition.get_filtered(
                db,
                skip=skip,
                limit=limit,
                search_term=search,
                mcp_type=mcp_type,
                include_archived=include_archived
            )
        else:
            # No filters, get all
            defs = crud_workflow_definition.get_multi(db, skip=skip, limit=limit)
        
        logger.info(f"Retrieved {len(defs)} workflows")
        return defs

    except Exception as e:
        logger.error(f"Error fetching workflow definitions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching workflows"
        )

@router.get("/{wf_def_id}", response_model=WorkflowDefinitionRead)
def get_workflow_definition(
    db: Session = Depends(get_db),
    wf_def_id: int = Path(..., description="Workflow Definition ID")
):
    """
    Get a Workflow Definition by ID, including its steps.

    Args:
        wf_def_id: Workflow Definition ID
        db: Database session

    Returns:
        Workflow definition with steps

    Raises:
        HTTPException: If workflow not found
    """
    wf_def = crud_workflow_definition.get_with_steps(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    return wf_def

@router.put("/{wf_def_id}", response_model=WorkflowDefinitionRead)
def update_workflow_definition(
    db: Session = Depends(get_db),
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    wf_def_update: WorkflowDefinitionUpdate
):
    """
    Update a Workflow Definition.

    Args:
        wf_def_id: Workflow Definition ID
        wf_def_update: Update data
        db: Database session

    Returns:
        Updated workflow definition

    Raises:
        HTTPException: If workflow not found or update fails
    """
    try:
        wf_def = crud_workflow_definition.get(db, id=wf_def_id)
        if not wf_def:
            raise HTTPException(status_code=404, detail="Workflow Definition not found")

        updated_wf_def = crud_workflow_definition.update(
            db=db,
            db_obj=wf_def,
            obj_in=wf_def_update
        )
        return updated_wf_def

    except Exception as e:
        logger.error(f"Error updating workflow definition {wf_def_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the workflow"
        )

@router.delete("/{wf_def_id}", response_model=WorkflowDefinitionRead)
@router.delete("/{wf_def_id}", response_model=WorkflowDefinitionRead)
def delete_workflow_definition(
    db: Session = Depends(get_db),
    wf_def_id: int = Path(..., description="Workflow Definition ID")
):
    """
    Delete a Workflow Definition and all its steps.

    Args:
        wf_def_id: Workflow Definition ID
        db: Database session

    Returns:
        Deleted workflow definition

    Raises:
        HTTPException: If workflow not found or deletion fails
    """
    try:
        wf_def = crud_workflow_definition.get(db, id=wf_def_id)
        if not wf_def:
            raise HTTPException(status_code=404, detail="Workflow Definition not found")

        deleted_wf_def = crud_workflow_definition.remove(db=db, id=wf_def_id)
        logger.info(f"Workflow deleted: {deleted_wf_def.name} (ID: {deleted_wf_def.id})")
        return deleted_wf_def

    except Exception as e:
        logger.error(f"Error deleting workflow definition {wf_def_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the workflow"
        )

# --- Workflow Step Endpoints ---

@router.post("/{wf_def_id}/steps/", response_model=WorkflowStepRead, status_code=status.HTTP_201_CREATED)
def add_workflow_step(
    db: Session = Depends(get_db),
    wf_def_id: int = Path(..., description="Workflow Definition ID"),
    step_in: WorkflowStepCreate
):
    """
    Add a new step to a Workflow Definition.

    Args:
        wf_def_id: Workflow Definition ID
        step_in: Step creation data
        db: Database session

    Returns:
        Created workflow step

    Raises:
        HTTPException: If workflow or step creation fails
    """
    # Ensure parent exists
    wf_def = crud_workflow_definition.get(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")

    try:
        step = crud_workflow_step.create(
            db=db,
            obj_in={**step_in.model_dump(), "workflow_definition_id": wf_def_id}
        )
        logger.info(f"Step added to workflow {wf_def_id}: {step.id}")
        return step

    except Exception as e:
        logger.error(f"Error adding step to workflow {wf_def_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the step"
        )

@router.delete("/{wf_def_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow_step(
    db: Session = Depends(get_db),
    wf_def_id: int,
    step_id: int
):
    """
    Delete a step from a Workflow Definition.
    """
    step = crud_workflow_step.get(db, id=step_id)
    if not step or step.workflow_definition_id != wf_def_id:
        raise HTTPException(status_code=404, detail="Workflow Step not found for this Workflow Definition")
    crud_workflow_step.remove(db, id=step_id)
    return

@router.put("/{wf_def_id}/steps/{step_id}", response_model=WorkflowStepRead)
def update_workflow_step(
    db: Session = Depends(get_db),
    wf_def_id: int,
    step_id: int,
    step_update: WorkflowStepCreate
):
    """
    Update a step in a Workflow Definition.
    """
    step = crud_workflow_step.get(db, id=step_id)
    if not step or step.workflow_definition_id != wf_def_id:
        raise HTTPException(status_code=404, detail="Workflow Step not found for this Workflow Definition")
    updated = crud_workflow_step.update(db, db_obj=step, obj_in=step_update)
    return updated

@router.get("/{wf_def_id}/steps/", response_model=List[WorkflowStepRead])
def list_workflow_steps(
    db: Session = Depends(get_db),
    wf_def_id: int
):
    """
    List all steps for a Workflow Definition.
    """
    wf_def = crud_workflow_definition.get_with_steps(db, id=wf_def_id)
    if not wf_def:
        raise HTTPException(status_code=404, detail="Workflow Definition not found")
    return wf_def.steps
